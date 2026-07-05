# 在LangChain中使用会话状态

使用 LangChain 构建多轮对话应用时，对话消息默认存储在内存中，进程重启即丢失。本文介绍如何通过 AgentRun 的`OTSChatMessageHistory`适配器，将对话消息自动持久化到表格存储 Tablestore（OTS），实现跨请求、跨进程重启的会话记忆。

## 前提条件

- 已创建表格存储（OTS）类型的记忆存储实例，且已开启**会话状态**功能。如尚未创建，请参见[创建和管理记忆存储](https://help.aliyun.com/zh/functioncompute/fc/create-and-manage-memory-storage)。
- 已安装 AgentRun SDK。
  
  ```
  pip install agentrun
  ```
- 已配置环境变量`MEMORY_COLLECTION_NAME`为已创建的记忆存储名称。

**

**重要**

会话状态功能开启后不可关闭，请确认后再开启。

## 快速开始

开始前，完成以下准备工作：

- 设置环境变量`MEMORY_COLLECTION_NAME`为已创建的记忆存储名称。
- Python 3.10 及以上版本。
- 安装依赖：`pip install agentrun-sdk langchain-core langchain-openai`

以下示例展示如何将 LangChain 的对话消息持久化到 OTS。

代码示例中的占位符说明：

- `your-memory-collection-name`：替换为在 AgentRun 控制台创建的记忆存储名称。登录[AgentRun 控制台](https://functionai.console.aliyun.com/cn-hangzhou/agent/runtime/agent-list)→ 在左侧导航栏，选择**记忆**即可查看。
- `your-api-key`：替换为 DashScope API Key。登录[百炼控制台](https://bailian.console.aliyun.com/cn-beijing?tab=globalset#/efm/api_key)，在**API-KEY管理**页面获取。

示例使用 DashScope 的 OpenAI 兼容接口，需要设置环境变量`DASHSCOPE_API_KEY`。

```
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder from langchain_core.runnables.history import RunnableWithMessageHistory from langchain_openai import ChatOpenAI from agentrun.conversation_service import SessionStore from agentrun.conversation_service.adapters import OTSChatMessageHistory # 初始化 store = SessionStore.from_memory_collection("your-memory-collection-name") store.init_langchain_tables() llm = ChatOpenAI( model="qwen-max", api_key="your-api-key", base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", ) # 构建 Prompt + Chain prompt = ChatPromptTemplate.from_messages([ ("system", "你是一个友好的中文智能助手。"), MessagesPlaceholder(variable_name="history"), ("human", "{input}"), ]) chain = prompt | llm # 通过工厂函数创建 History-RunnableWithMessageHistory 会根据 # session_id 自动调用此函数获取对应的消息历史 chain_with_history = RunnableWithMessageHistory( chain, lambda session_id: OTSChatMessageHistory( session_store=store, agent_id="my_agent", user_id="user_1", session_id=session_id, ), input_messages_key="input", history_messages_key="history", ) # 使用：指定 session_id 即可自动管理历史 config = {"configurable": {"session_id": "session_1"}} response1 = chain_with_history.invoke( {"input": "我叫小明"}, config=config, ) print(f"回复1: {response1.content}") response2 = chain_with_history.invoke( {"input": "我叫什么名字？"}, config=config, ) print(f"回复2: {response2.content}") # Agent 能记住用户叫小明，因为历史消息已自动从 OTS 加载
```

运行后，Agent 能记住用户名字，因为历史消息已自动从 OTS 加载并注入到 Prompt 中。即使程序重启，再次以相同的`session_id`创建`OTSChatMessageHistory`，历史消息仍然存在。

预期输出示例：

```
回复1: 你好，小明！很高兴认识你。 回复2: 你叫小明。
```

如果第二次回复中包含"小明"字样，说明消息持久化已生效；否则请检查记忆存储名称和环境变量配置是否正确。

## 集成指南

以下步骤介绍如何将 OTSChatMessageHistory 集成到 LangChain 应用中，实现会话消息的持久化管理。

### 初始化 SessionStore

`SessionStore`是 Conversation Service 的核心入口。通过`记忆存储`名称初始化时，SDK 自动完成以下工作：

1. 调用 AgentRun API 获取`记忆存储`配置。
2. 从中提取 Tablestore 的 endpoint 和 instance_name。
3. 构建 OTS 客户端。

```
from agentrun.conversation_service import SessionStore store = SessionStore.from_memory_collection("your-memory-collection-name")
```

初始化后，调用`init_langchain_tables()`创建所需的数据库表和索引。该方法是幂等的，表或索引已存在时自动跳过，可以在每次启动时安全调用。

```
store.init_langchain_tables()
```

#### 异步初始化

`SessionStore`的所有方法均提供异步版本（方法名加`_async`后缀）。

```
store = await SessionStore.from_memory_collection_async( "your-memory-collection-name") await store.init_langchain_tables_async()
```

### 创建 OTSChatMessageHistory

`OTSChatMessageHistory`是 LangChain`BaseChatMessageHistory`的 OTS 实现。每个实例绑定一个具体的会话（由`agent_id`+`user_id`+`session_id`唯一标识）。

```
from agentrun.conversation_service.adapters import OTSChatMessageHistory history = OTSChatMessageHistory( session_store=store, agent_id="my_agent", user_id="user_1", session_id="session_1", )
```

参数说明：

| **参数** | **类型** | **必填** | **说明** |
| --- | --- | --- | --- |
| session_store | SessionStore | 是 | 提供 Tablestore 连接信息的 SessionStore 对象 |
| agent_id | str | 是 | 智能体 ID，用于区分不同的 Agent 应用 |
| user_id | str | 是 | 用户 ID |
| session_id | str | 是 | 会话 ID，同一`session_id`共享消息历史 |
| auto_create_session | bool | 否 | Session 不存在时是否自动创建，默认 True。设为 False 时需手动创建 Session（如先校验权限再创建） |

### 消息管理

#### 写入消息

使用`add_message`写入单条消息，或`add_messages`批量写入。

```
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage # 写入单条消息 history.add_message(HumanMessage(content="今天天气怎么样？")) history.add_message(AIMessage(content="今天北京晴朗，气温 15~25°C。")) # 批量写入 history.add_messages([ HumanMessage(content="上海呢？"), AIMessage(content="上海多云，气温 12~20°C。"), ])
```

每条 LangChain`BaseMessage`会被序列化为一条 OTS Event，包含以下信息：

| **字段** | **说明** |
| --- | --- |
| lc_type | 消息类型（human、ai、system、tool） |
| content | 消息内容 |
| additional_kwargs | 额外参数（如有） |
| response_metadata | 响应元数据（如有） |
| tool_calls | 工具调用列表（`AIMessage`特有） |
| tool_call_id | 工具调用 ID（`ToolMessage`特有） |

#### 读取消息

通过`messages`属性读取完整的消息历史，按写入顺序（`seq_id`正序）返回。返回标准的 LangChain`BaseMessage`列表，可直接传给 LLM。

```
for msg in history.messages: print(f"{msg.type}: {msg.content}")
```

```
response = llm.invoke( [SystemMessage(content="你是一个助手。")] + history.messages)
```

#### 清空消息

清空当前 Session 的所有消息，但保留 Session 元数据。

```
history.clear()
```

### 配合 RunnableWithMessageHistory 自动管理消息

LangChain 的`RunnableWithMessageHistory`可以自动将消息历史注入到 Chain 中。配合`OTSChatMessageHistory`，可以实现完全自动化的消息管理。

`RunnableWithMessageHistory`的工作流程：

- **调用前**：从 OTS 加载历史消息，注入到 Prompt 中。
- **调用后**：将新的用户消息和 AI 回复写入 OTS。

#### 流式输出

`RunnableWithMessageHistory`也支持流式输出：

```
config = {"configurable": {"session_id": "session_1"}} for chunk in chain_with_history.stream({"input": "讲个笑话"}, config=config): print(chunk.content, end="", flush=True)
```

#### 动态 user_id

在 Server 场景中，`user_id`通常从请求中动态获取。通过扩展工厂函数实现：

```
from langchain_core.runnables import ConfigurableFieldSpec chain_with_history = RunnableWithMessageHistory( chain, lambda session_id, *, user_id="default_user", **kwargs: OTSChatMessageHistory( session_store=store, agent_id="my_agent", user_id=user_id, session_id=session_id, ), input_messages_key="input", history_messages_key="history", history_factory_config=[ ConfigurableFieldSpec( id="session_id", annotation=str, name="Session ID", default="", ), ConfigurableFieldSpec( id="user_id", annotation=str, name="User ID", default="default_user", ), ], ) config = {"configurable": {"session_id": "s1", "user_id": "user_1"}} response = chain_with_history.invoke({"input": "你好"}, config=config)
```

### 结合 AgentRunServer 部署为 HTTP 服务

在生产环境中，通常将 LangChain Agent 部署为 HTTP 服务。以下示例展示在`AgentRunServer`的`invoke_agent`函数中手动管理消息历史：

```
import os import uuid from langchain_core.messages import AIMessage, HumanMessage, SystemMessage from langchain_openai import ChatOpenAI from agentrun import AgentRequest from agentrun.conversation_service import SessionStore from agentrun.conversation_service.adapters import OTSChatMessageHistory from agentrun.server import AgentRunServer AGENT_ID = "langchain_chat_server" SYSTEM_PROMPT = "你是一个友好的中文智能助手。" store = SessionStore.from_memory_collection( os.environ["MEMORY_COLLECTION_NAME"]) store.init_langchain_tables() llm = ChatOpenAI( model="qwen-max", api_key=os.environ["DASHSCOPE_API_KEY"], base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", ) async def invoke_agent(req: AgentRequest): headers = dict(req.raw_request.headers) if req.raw_request else {} session_id = ( headers.get("x-agentrun-session-id") or f"session_{uuid.uuid4().hex[:8]}" ) user_id = headers.get("x-agentrun-user-id") or "default_user" history = OTSChatMessageHistory( session_store=store, agent_id=AGENT_ID, user_id=user_id, session_id=session_id, ) # 提取用户消息 last_user_text = "" for msg in reversed(req.messages): if msg.role == "user": last_user_text = msg.content or "" break if not last_user_text: yield "请输入问题。" return # 写入用户消息 history.add_message(HumanMessage(content=last_user_text)) # 拼接完整消息列表并流式调用 LLM full_messages = [SystemMessage(content=SYSTEM_PROMPT)] + history.messages full_response = "" async for chunk in llm.astream(full_messages): text = chunk.content if isinstance(text, str) and text: full_response += text yield text # 写入 AI 回复（持久化到 OTS） if full_response: history.add_message(AIMessage(content=full_response)) if __name__ == "__main__": server = AgentRunServer( invoke_agent=invoke_agent, memory_collection_name=os.environ["MEMORY_COLLECTION_NAME"], ) server.start(port=9002)
```

客户端请求时的 Header 约定：

| **Header** | **说明** | **必填** |
| --- | --- | --- |
| X-AgentRun-Session-ID | 会话 ID，用于关联多轮对话 | 否（不传则自动生成新会话） |
| X-AgentRun-User-ID | 用户 ID | 否（默认 default_user） |

本地测试：

```
curl -X POST http://localhost:9002/openai/v1/chat/completions \ -H "Content-Type: application/json" \ -H "X-AgentRun-Session-ID: my-session-1" \ -H "X-AgentRun-User-ID: user-1" \ -d '{"model":"qwen-max","stream":true,"messages":[{"role":"user","content":"你好"}]}'
```

## 部署到 AgentRun 云平台

完成本地开发和测试后，通过 Serverless Devs 工具将 Agent 部署到 AgentRun 云平台。部署后，Agent 作为 Serverless 服务运行，自动获得弹性伸缩、日志监控等能力，无需手动管理服务器。

### 安装部署工具

Serverless Devs（`s`命令）用于将代码部署到 AgentRun。如果环境已安装 Node.js，通过 npm 安装：

```
npm install -g @serverless-devs/s
```

安装完成后验证：

```
s --version
```

部署前需要配置阿里云凭证。运行以下命令，按照引导输入 AccessKey ID 和 AccessKey Secret，并记住密钥对名称（如 default），该名称将用于 s.yaml 中的`access`字段。

```
s config add
```

此外，`s build`命令需要 Docker 来构建 Linux x64 兼容的依赖包。请安装 Docker Desktop 或其他兼容环境（如 Podman、Lima）。

### 准备配置文件

确保项目根目录下有`requirements.txt`文件：

```
agentrun-sdk[server,langchain]==0.0.31 python-dotenv>=1.0.0
```

创建`.fcignore`文件，排除敏感文件和本地环境：

```
.env .venv
```

在项目根目录创建`s.yaml`配置文件：

```
edition: 3.0.0 access: 'default' # 修改为通过 s config add 配置的密钥对名称 vars: region: 'cn-hangzhou' agent_name: 'my-langchain-agent' # Agent 名称 role: 'acs:ram::${config("AccountID")}:role/AliyunAgentRunDefaultRole' memory_collection_name: 'your-memory-collection-name' # 替换为记忆存储名称 api_key: 'your-dashscope-api-key' # 替换为 DashScope API Key resources: agent: component: agentrun props: region: ${vars.region} agent: name: ${vars.agent_name} description: 'LangChain Conversation Service' role: ${vars.role} code: src: ./ language: python3.12 command: - python3 - conversation_service_langchain_server.py cpu: 1.0 memory: 2048 port: 9000 instanceConcurrency: 200 internetAccess: true environmentVariables: PYTHONPATH: /code/python:/opt/python:/code:/code/python MEMORY_COLLECTION_NAME: '${vars.memory_collection_name}' DASHSCOPE_API_KEY: '${vars.api_key}' logConfig: auto endpoints: - name: prod version: LATEST description: '生产环境端点'
```

关键配置说明：

| **字段** | **说明** |
| --- | --- |
| access | `s config add`时设置的密钥对名称 |
| vars.role | Agent 运行时的 RAM 角色。AliyunAgentRunDefaultRole 是默认角色，可通过快速授权链接创建 |
| code.command | 启动命令，根据使用的框架修改对应的 server 文件名 |
| environmentVariables | 云上环境变量，替代本地的 .env 文件 |

### 构建和部署

云上为 Linux x64 环境，通过`s build`在 Docker 中安装兼容的依赖。该命令会拉取函数计算的运行镜像，在其中执行 pip install，将依赖安装到 python/ 目录。

```
s build --use-docker
```

构建完成后执行部署：

```
s deploy
```

部署成功后，输出中包含 Agent 的访问 URL。示例输出：

```
endpoints: - name: prod url: https://<account-id>.agentrun-data.cn-hangzhou.aliyuncs.com/agent-runtimes/<agent-name>/endpoints/prod/invocations status: READY
```

### 验证部署

使用部署输出的 URL 发起请求。将`<your-endpoint-url>`替换为`s deploy`输出的实际 URL：

```
curl -X POST https://<your-endpoint-url>/openai/v1/chat/completions \ -H "Content-Type: application/json" \ -H "X-AgentRun-Session-ID: my-session-1" \ -H "X-AgentRun-User-ID: user-1" \ -d '{"model":"qwen-max","stream":true,"messages":[{"role":"user","content":"你好"}]}'
```

## 常见问题

### init_langchain_tables() 需要每次启动都调用吗？

可以。`init_langchain_tables()`是幂等操作，表或索引已存在时自动跳过。建议在应用启动时调用，确保所需资源就绪。

### 手动管理和自动管理消息历史如何选择？

- **手动管理**（直接使用`OTSChatMessageHistory`）：适合需要完全控制消息流的场景，如在`AgentRunServer`的`invoke_agent`中手动读写消息。
- **自动管理**（使用`RunnableWithMessageHistory`）：适合标准的 Chain 调用场景，消息的读取和写入由框架自动完成，代码更简洁。

### 支持哪些消息类型？

支持 LangChain 的四种核心消息类型：

| **类型** | **LangChain 类** | **说明** |
| --- | --- | --- |
| human | `HumanMessage` | 用户消息 |
| ai | `AIMessage` | Agent 回复（含 tool_calls） |
| system | `SystemMessage` | 系统提示 |
| tool | `ToolMessage` | 工具执行结果 |

`AIMessage`的`tool_calls`、`invalid_tool_calls`和`ToolMessage`的`tool_call_id`等字段均会完整序列化和反序列化。

### 支持哪些模型？

Conversation Service 不限制模型选择。示例中使用的是通义千问（通过 DashScope API 调用），可以替换为任何 LangChain 支持的 Chat Model（如 OpenAI GPT、Anthropic Claude、Google Gemini 等）。模型选择由 LangChain 的 ChatModel 配置决定，与 Conversation Service 无关。

### 如何处理并发写入冲突？

消息写入是追加（append）操作，使用自增序列号（`seq_id`）保证顺序，不会产生写入冲突。会话元数据的更新使用乐观锁机制（`version`字段），如果两个请求同时更新同一行，后到的请求会因`version`不匹配而失败。

### 使用限制

使用会话状态功能时，需注意以下限制：

- 单条消息大小受 Tablestore 单行数据大小限制，建议单条消息不超过 400 KB。
- 单个会话的消息数量无硬性上限，但建议控制在合理范围内以避免加载延迟。如需存储大量历史数据，建议使用 长期记忆 方案。
- 记忆存储的地域需与 Agent 部署地域一致，跨地域访问可能产生延迟。

### 异常处理

在生产环境中，建议对 Conversation Service 的关键操作添加异常处理。以下是推荐的错误处理模式：

```
import logging from agentrun.conversation_service import SessionStore from agentrun.conversation_service.adapters import OTSChatMessageHistory logger = logging.getLogger(__name__) # 初始化时的异常处理 try: store = SessionStore.from_memory_collection("your-memory-collection-name") store.init_langchain_tables() except ValueError as e: # 记忆存储名称无效或不存在 logger.error(f"记忆存储初始化失败: {e}") raise except Exception as e: # 网络超时或认证失败 logger.error(f"连接 AgentRun 服务失败: {e}") raise # 消息读写时的异常处理 try: history = OTSChatMessageHistory( session_store=store, agent_id="my_agent", user_id="user_1", session_id="session_1", ) history.add_message(HumanMessage(content="你好")) messages = history.messages except ConnectionError as e: logger.error(f"OTS 连接失败，请检查网络: {e}") except TimeoutError as e: logger.error(f"OTS 请求超时: {e}") except Exception as e: logger.error(f"消息读写异常: {e}")
```

常见错误场景及解决方案：

| **错误场景** | **可能原因** | **解决方案** |
| --- | --- | --- |
| `MemoryCollection not found` | 记忆存储名称拼写错误或资源未创建 | 登录[AgentRun 控制台](https://functionai.console.aliyun.com/cn-hangzhou/agent/runtime/agent-list)→ 在左侧导航栏，选择 记忆，确认记忆存储已创建，名称与代码中的一致 |
| 认证失败（`401 Unauthorized`） | AccessKey 无效或 RAM 角色权限不足 | 检查环境变量中的 AccessKey ID 和 AccessKey Secret 是否正确，确认 RAM 角色已授予 AgentRun 和 Tablestore 访问权限 |
| 网络超时（`ConnectionTimeout`） | 网络不稳定或 endpoint 配置错误 | 检查网络连通性，确认记忆存储中的 Tablestore endpoint 可访问 |
| 版本冲突（`OTSConditionCheckFail`） | 多个客户端同时更新同一会话元数据 | 添加重试机制，乐观锁冲突通常在重试后自动解决 |
