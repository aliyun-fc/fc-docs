# 在LangGraph中使用会话状态

在 LangGraph 中构建多轮对话智能体时，服务重启、扩容或网络中断会导致对话上下文丢失。通过 AgentRun 的 OTSCheckpointSaver，将 LangGraph checkpoint 自动持久化到表格存储（Tablestore），实现跨请求恢复和断点续接，无需修改 Graph 逻辑。本文介绍 OTSCheckpointSaver 的集成方法、checkpoint 管理操作以及生产环境部署方案。

## 前提条件

- 已创建表格存储（OTS）类型的记忆存储实例，且已开启**会话状态**功能。如尚未创建，请参见[创建和管理记忆存储](https://help.aliyun.com/zh/functioncompute/fc/create-and-manage-memory-storage)。
- 已安装 AgentRun SDK 和 LangGraph。
  
  ```
  pip install agentrun langgraph
  ```
- 已配置环境变量`MEMORY_COLLECTION_NAME`为已创建的记忆存储名称。

**

**重要**

会话状态功能开启后不可关闭，请确认后再开启。

## 快速开始

完成前提条件后，使用以下示例验证 LangGraph checkpoint 持久化到 OTS 的多轮对话能力。

安装依赖：

```
pip install "agentrun-sdk[server,langgraph]==0.0.31" langgraph langchain-core langchain-openai
```

完整示例代码：

```
import os from typing import Annotated, Any, TypedDict from langchain_core.messages import AIMessage, BaseMessage, HumanMessage from langchain_openai import ChatOpenAI from langgraph.graph import END, START, StateGraph from langgraph.graph.message import add_messages from agentrun.conversation_service import SessionStore from agentrun.conversation_service.adapters import OTSCheckpointSaver # Step 1：初始化 SessionStore 并创建数据表 store = SessionStore.from_memory_collection("your-memory-collection-name") store.init_langgraph_tables() # Step 2：创建 OTSCheckpointSaver checkpointer = OTSCheckpointSaver(store) # Step 3：定义 Graph class ChatState(TypedDict): messages: Annotated[list[BaseMessage], add_messages] llm = ChatOpenAI( model="qwen-max", api_key=os.environ.get("DASHSCOPE_API_KEY"), base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", ) def chat_node(state: ChatState) -> dict[str, Any]: response = llm.invoke(state["messages"]) return {"messages": [response]} graph = StateGraph(ChatState) graph.add_node("chat", chat_node) graph.add_edge(START, "chat") graph.add_edge("chat", END) app = graph.compile(checkpointer=checkpointer) # Step 4：多轮对话 config = {"configurable": {"thread_id": "my-thread-1"}} result1 = app.invoke( {"messages": [HumanMessage(content="你好，我叫小明")]}, config=config, ) print(f"第一轮消息数: {len(result1['messages'])}") result2 = app.invoke( {"messages": [HumanMessage(content="我叫什么名字？")]}, config=config, ) print(f"第二轮消息数: {len(result2['messages'])}") # Step 5：验证输出 # 预期输出： # 第一轮消息数: 2 # 第二轮消息数: 4
```

运行后，第二轮对话自动恢复了第一轮的状态（消息数累加）。即使程序重启，用同一个`thread_id`再次调用，历史状态仍然存在。

## 集成指南

Agent 的本质是对无状态 LLM 进行有状态的精细化 Context 管理。无论使用哪种 Agent 框架，持久化会话状态都是构建生产级 Agent 的关键一步。

LangGraph 在 Graph 每完成一步执行后，通过`checkpointer.put()`保存当前状态快照（checkpoint）。`OTSCheckpointSaver`是 LangGraph`BaseCheckpointSaver`的 OTS 实现，传给`StateGraph.compile(checkpointer=...)`即可让 checkpoint 自动持久化到 OTS，无需修改任何 Graph 逻辑。

Checkpoint 数据分三部分存储在 OTS 中：

| **数据** | **OTS 表** | **说明** |
| --- | --- | --- |
| Checkpoint 元数据 | checkpoint | 包含 checkpoint ID、parent ID、metadata 等 |
| Channel Values | checkpoint_blobs | Graph 状态中每个 channel 的值（如 messages 列表），base64 编码存储 |
| Pending Writes | checkpoint_writes | 中间写入记录，用于 Graph 执行恢复 |

OTSCheckpointSaver 支持以下功能：

- **Checkpoint 持久化**：自动将 Graph 的完整执行状态（消息、自定义字段等）持久化到 OTS。
- **状态恢复**：同一 thread_id 的后续调用自动从 OTS 恢复上次状态，实现跨请求的多轮对话。
- **会话同步**：设置 agent_id 后，每次 checkpoint 写入时自动在 conversation 表中同步会话记录，支持 list_sessions 查询。
- **Thread 删除**：一次调用删除 thread 下所有 checkpoint 数据及关联的会话记录。

### 初始化 SessionStore

`SessionStore`是 Conversation Service 的核心入口。通过记忆存储名称初始化时，SDK 自动完成以下工作：

1. 调用 AgentRun API 获取记忆存储配置。
2. 从中提取 Tablestore 的 endpoint 和 instance_name。
3. 构建 OTS 客户端。

```
from agentrun.conversation_service import SessionStore store = SessionStore.from_memory_collection("your-memory-collection-name")
```

初始化后，调用`init_langgraph_tables()`创建所需的数据库表和索引。该方法是幂等的，表或索引已存在时自动跳过，可以在每次启动时调用。

```
store.init_langgraph_tables()
```

#### 异步初始化

`SessionStore`的所有方法均提供异步版本（方法名加`_async`后缀）：

```
store = await SessionStore.from_memory_collection_async( "your-memory-collection-name") await store.init_langgraph_tables_async()
```

### 创建 OTSCheckpointSaver

`OTSCheckpointSaver`是 LangGraph`BaseCheckpointSaver`的 OTS 实现。创建后传给`StateGraph.compile()`即可。

```
from agentrun.conversation_service.adapters import OTSCheckpointSaver checkpointer = OTSCheckpointSaver(store)
```

参数说明：

| **参数** | **类型** | **必填** | **说明** |
| --- | --- | --- | --- |
| session_store | SessionStore | 是 | SessionStore 实例 |
| agent_id | str | 否 | 智能体 ID。设置后 checkpoint 写入时自动同步 conversation 表记录 |
| user_id | str | 否 | 默认用户 ID。可通过 config["metadata"]["user_id"] 在每次调用时覆盖 |

指定`agent_id`和`user_id`：

```
checkpointer = OTSCheckpointSaver( store, agent_id="my_agent", user_id="default_user", ) # 后续 put 操作会自动同步 conversation 记录 # 可通过 list_sessions 查询 sessions = store.list_sessions("my_agent", "default_user")
```

#### 会话同步机制

当设置了`agent_id`时，`OTSCheckpointSaver`在每次`put`时自动在 conversation 表中创建或更新会话记录（`session_id`=`thread_id`，framework = "langgraph"）。外部服务可以通过`list_sessions`或`search_sessions`查询 LangGraph 会话列表。

#### user_id 优先级

`user_id`按以下优先级解析：

1. `config["metadata"]["user_id"]`（每次调用时动态传入，优先级最高）
2. 构造器参数`user_id`
3. 默认值`"default"`

在 Server 场景中，通常从 HTTP Header 获取`user_id`并通过 config metadata 传入。

### 构建 Graph 并使用 checkpointer

将`OTSCheckpointSaver`传给`StateGraph.compile()`的`checkpointer`参数：

```
config = { "configurable": {"thread_id": thread_id}, "metadata": {"user_id": user_id}, } await app.ainvoke({"messages": [...]}, config=config)
```

编译后，通过`thread_id`区分不同对话线程。同一`thread_id`的调用自动恢复之前的状态：

```
config = {"configurable": {"thread_id": "my-thread-1"}} # 第一轮：新线程 result1 = await app.ainvoke( {"messages": [HumanMessage(content="你好")]}, config=config, ) # 第二轮：自动恢复第一轮状态 result2 = await app.ainvoke( {"messages": [HumanMessage(content="继续聊")]}, config=config, ) # result2["messages"] 包含第一轮 + 第二轮的所有消息
```

### Checkpoint 管理

#### 查询 checkpoint

通过`get_tuple`/`aget_tuple`查询指定 thread 的最新 checkpoint：

```
config = {"configurable": {"thread_id": "my-thread-1"}} checkpoint_tuple = await checkpointer.aget_tuple(config) if checkpoint_tuple: cp = checkpoint_tuple.checkpoint print(f"checkpoint_id: {cp['id']}") messages = cp["channel_values"].get("messages", []) print(f"消息数: {len(messages)}") print(f"metadata: {checkpoint_tuple.metadata}")
```

也可以指定`checkpoint_id`查询特定版本：

```
config = { "configurable": { "thread_id": "my-thread-1", "checkpoint_id": "specific-checkpoint-id", } } checkpoint_tuple = await checkpointer.aget_tuple(config)
```

#### 列出 checkpoint 历史

通过`list`/`alist`列出 thread 的 checkpoint 历史（按`checkpoint_id`倒序）：

```
config = {"configurable": {"thread_id": "my-thread-1"}} async for cp_tuple in checkpointer.alist(config, limit=10): print(f" checkpoint_id={cp_tuple.checkpoint['id']}")
```

支持`filter`参数按 metadata 过滤，以及`before`参数分页：

```
async for cp_tuple in checkpointer.alist( config, filter={"source": "loop"}, limit=5, ): print(cp_tuple.metadata)
```

#### 删除 thread

删除 thread 会清理所有关联的 checkpoint 数据。如果设置了`agent_id`，还会级联删除 conversation 表中的会话记录：

```
await checkpointer.adelete_thread("my-thread-1")
```

#### 回滚到历史 checkpoint

通过指定`checkpoint_id`恢复到历史状态：

```
# 列出历史 checkpoint config = {"configurable": {"thread_id": "my-thread-1"}} async for cp_tuple in checkpointer.alist(config, limit=5): print(f"checkpoint_id={cp_tuple.checkpoint['id']}") # 从指定 checkpoint 恢复 config_with_cp = { "configurable": { "thread_id": "my-thread-1", "checkpoint_id": "target-checkpoint-id", } } result = await app.ainvoke( {"messages": [HumanMessage(content="继续")]}, config=config_with_cp, )
```

### 结合 AgentRunServer 部署

生产环境中，通常将 LangGraph Agent 部署为 HTTP 服务。将以下服务端代码保存为`conversation_service_langgraph_server.py`：

```
import os import uuid from typing import Annotated, Any, TypedDict from langchain_core.messages import AIMessage, BaseMessage, HumanMessage from langchain_openai import ChatOpenAI from langgraph.graph import END, START, StateGraph from langgraph.graph.message import add_messages from agentrun import AgentRequest from agentrun.conversation_service import SessionStore from agentrun.conversation_service.adapters import OTSCheckpointSaver from agentrun.server import AgentRunServer AGENT_ID = "langgraph_chat_server" class ChatState(TypedDict): messages: Annotated[list[BaseMessage], add_messages] llm = ChatOpenAI( model="qwen-max", api_key=os.environ["DASHSCOPE_API_KEY"], base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", ) def chat_node(state: ChatState) -> dict[str, Any]: response = llm.invoke(state["messages"]) return {"messages": [response]} # 初始化 store = SessionStore.from_memory_collection( os.environ["MEMORY_COLLECTION_NAME"]) store.init_langgraph_tables() checkpointer = OTSCheckpointSaver(store, agent_id=AGENT_ID) graph = StateGraph(ChatState) graph.add_node("chat", chat_node) graph.add_edge(START, "chat") graph.add_edge("chat", END) app = graph.compile(checkpointer=checkpointer) # 核心处理函数 async def invoke_agent(req: AgentRequest): # 从 HTTP Header 获取 thread_id 和 user_id headers = dict(req.raw_request.headers) if req.raw_request else {} thread_id = ( headers.get("x-agentrun-session-id") or f"thread_{uuid.uuid4().hex[:8]}" ) user_id = headers.get("x-agentrun-user-id") or "default_user" config = { "configurable": {"thread_id": thread_id}, "metadata": {"user_id": user_id}, } # 提取用户消息 last_user_text = "" for msg in reversed(req.messages): if msg.role == "user": last_user_text = msg.content or "" break if not last_user_text: yield "请输入问题。" return # 调用 LangGraph 流式输出 async for event in app.astream( {"messages": [HumanMessage(content=last_user_text)]}, config=config, stream_mode="values", ): messages = event.get("messages", []) if messages: last_msg = messages[-1] if isinstance(last_msg, AIMessage) and last_msg.content: yield last_msg.content # 启动服务 if __name__ == "__main__": server = AgentRunServer( invoke_agent=invoke_agent, memory_collection_name=os.environ["MEMORY_COLLECTION_NAME"], ) server.start(port=9000)
```

客户端请求时的 Header 约定：

| **Header** | **说明** | **必填** |
| --- | --- | --- |
| X-AgentRun-Session-ID | 对应 LangGraph 的 thread_id，用于关联多轮对话 | 否（不传则自动生成新 thread） |
| X-AgentRun-User-ID | 用户 ID，写入 config["metadata"]["user_id"] | 否（默认 default_user） |

本地测试（确保端口与 s.yaml 中的 port 配置一致）：

```
curl -X POST http://localhost:9000/openai/v1/chat/completions \ -H "Content-Type: application/json" \ -H "X-AgentRun-Session-ID: my-thread-1" \ -H "X-AgentRun-User-ID: user-1" \ -d '{"model":"qwen-max","stream":true,"messages":[{"role":"user","content":"你好"}]}'
```

## 部署到 AgentRun 云平台

### 安装部署工具

通过 npm 安装 Serverless Devs（`s`命令）：

```
npm install -g @serverless-devs/s
```

安装完成后验证：

```
s --version
```

配置阿里云凭证。运行以下命令，按照引导输入 AccessKey ID 和 AccessKey Secret：

```
s config add
```

**

**说明**

记住配置时设置的密钥对名称（如 default），该名称将用于 s.yaml 中的 access 字段。

`s build`命令需要 Docker 构建 Linux x64 兼容的依赖包，需提前安装 Docker Desktop 或兼容环境（如 Podman、Lima）。

### 准备配置文件

确保项目根目录下有`requirements.txt`文件：

```
agentrun-sdk[server,langgraph]==0.0.31 python-dotenv>=1.0.0
```

创建`.fcignore`文件，排除敏感文件和本地环境：

```
.env .venv
```

在项目根目录创建`s.yaml`配置文件：

```
edition: 3.0.0 name: my-conversation-service access: 'default' # 修改为通过 s config add 配置的密钥对名称 vars: region: 'cn-hangzhou' agent_name: 'my-langgraph-agent' # Agent 名称 role: 'acs:ram::${config("AccountID")}:role/AliyunAgentRunDefaultRole' memory_collection_name: 'your-memory-collection-name' # 替换为记忆存储名称 api_key: 'your-dashscope-api-key' # 替换为 DashScope API Key resources: agent: component: agentrun props: region: ${vars.region} agent: name: ${vars.agent_name} description: 'LangGraph Conversation Service' role: ${vars.role} code: src: ./ language: python3.12 command: - python3 - conversation_service_langgraph_server.py cpu: 1.0 memory: 2048 port: 9000 instanceConcurrency: 200 internetAccess: true environmentVariables: PYTHONPATH: /code/python:/opt/python:/code:/code/python MEMORY_COLLECTION_NAME: '${vars.memory_collection_name}' DASHSCOPE_API_KEY: '${vars.api_key}' logConfig: auto endpoints: - name: prod version: LATEST description: '生产环境端点'
```

关键配置说明：

| **字段** | **说明** |
| --- | --- |
| access | s config add 时设置的密钥对名称 |
| vars.role | Agent 运行时的 RAM 角色。可前往[RAM 角色管理页面](https://ram.console.aliyun.com/roles/AliyunAgentRunDefaultRole)查看或创建 |
| code.command | 启动命令，根据使用的框架修改对应的 server 文件名。本文示例为`conversation_service_langgraph_server.py`。 |
| environmentVariables | 云上环境变量，替代本地的 .env 文件 |

### 构建与部署

云上为 Linux x64 环境，需要通过`s build`在 Docker 中安装兼容的依赖：

```
s build --use-docker
```

该命令拉取函数计算的运行镜像，在其中执行 pip install，将依赖安装到`python/`目录。

构建完成后部署：

```
s deploy
```

部署成功后，输出中包含 Agent 的访问 URL：

```
endpoints: - name: prod url: https://<agent-id>.agentrun-data.cn-hangzhou.aliyuncs.com/agent-runtimes/<runtime-id>/endpoints/prod/invocations status: READY
```

### 测试

使用部署输出的 URL 发起请求。将`<your-endpoint-url>`替换为`s deploy`输出的实际 URL：

```
curl -X POST https://<your-endpoint-url>/openai/v1/chat/completions \ -H "Content-Type: application/json" \ -H "X-AgentRun-Session-ID: my-thread-1" \ -H "X-AgentRun-User-ID: user-1" \ -d '{"model":"qwen-max","stream":true,"messages":[{"role":"user","content":"你好"}]}'
```

## 常见问题

### init_langgraph_tables() 是否需要每次启动都调用

可以。`init_langgraph_tables()`是幂等操作，表或索引已存在时自动跳过。建议在应用启动时调用，确保所需资源就绪。

### thread_id 和 session_id 的关系

在 LangGraph 场景中，`thread_id`用于区分不同的对话线程。当启用会话同步（设置`agent_id`）时，`OTSCheckpointSaver`将`thread_id`映射为 conversation 表中的`session_id`，两者是同一个值。

### 是否需要设置 agent_id

取决于使用场景：

- **不设置**：checkpoint 数据正常持久化和恢复，但无法通过 list_sessions / search_sessions 查询会话列表。适合简单场景或不需要会话管理的应用。
- **设置（推荐）**：每次 checkpoint 写入时自动同步 conversation 表记录。适合需要展示会话列表、搜索会话的生产应用。

### LangGraph 和 LangChain 的区别

| **维度** | **LangGraph (OTSCheckpointSaver)** | **LangChain (OTSChatMessageHistory)** |
| --- | --- | --- |
| 持久化粒度 | Graph 完整状态快照（包含所有 channel 值） | 单条消息（每条 Message 一个 Event） |
| 状态恢复 | 自动恢复所有 State 字段（messages + 自定义字段） | 只恢复消息列表 |
| 适用场景 | 复杂 Agent Graph（多节点、条件分支、工具调用） | 简单对话链（Prompt + LLM） |
| 初始化方法 | init_langgraph_tables() | init_langchain_tables() |

### 支持哪些模型

Conversation Service 不限制模型选择。示例中使用的是通义千问（通过 DashScope API 调用），可以替换为任何 LangChain 支持的 Chat Model（如 OpenAI GPT、Anthropic Claude、Google Gemini 等）。模型选择由 LangGraph 节点中的 LLM 配置决定，与 Conversation Service 无关。

### 异常处理与常见问题排查

集成过程中可能遇到以下常见问题：

| **错误场景** | **错误信息** | **解决方法** |
| --- | --- | --- |
| 认证失败 | `InvalidAccessKeyId`或`SignatureDoesNotMatch` | 运行`echo $ALIBABA_CLOUD_ACCESS_KEY_ID`检查环境变量是否已设置。确认 AccessKey 未被禁用，且对应 RAM 用户有 Tablestore 权限。 |
| 网络超时 | `ConnectionTimeout`或`OTSClientError` | 在 AgentRun 控制台查看记忆存储中的 endpoint 配置，确认网络可达。VPC 内运行时使用内网 endpoint。可在业务层增加重试逻辑。 |
| 环境变量缺失 | `KeyError: 'MEMORY_COLLECTION_NAME'` | 运行`echo $MEMORY_COLLECTION_NAME`检查变量是否已设置。本地开发使用`.env`文件配合`python-dotenv`加载。 |
| 记忆存储不存在 | `MemoryCollectionNotFound` | 前往 AgentRun 控制台核对记忆存储名称（区分大小写），确保与`$MEMORY_COLLECTION_NAME`环境变量值一致。 |
| Checkpoint 恢复失败 | 多轮对话无法恢复历史状态 | 确认多次调用使用了相同的`thread_id`。运行`echo $MEMORY_COLLECTION_NAME`确认连接的目标实例正确。检查`init_langgraph_tables()`在首次运行时是否成功创建了所需表和索引。 |

建议在生产环境中对关键操作添加异常处理：

```
from langgraph.graph import StateGraph try: result = await app.ainvoke( {"messages": [HumanMessage(content="你好")]}, config=config, ) except Exception as e: print(f"Graph 执行失败: {e}") # 检查 checkpoint 状态 cp = await checkpointer.aget_tuple(config) if cp: print(f"最后一次成功的 checkpoint: {cp.checkpoint['id']}") raise
```
