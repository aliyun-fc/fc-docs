# 在Google ADK中使用会话状态

将 Google ADK Agent 的会话数据持久化到云端，实现多轮对话管理和断点续接。本文介绍如何使用`OTSSessionService`将 ADK 的会话、事件流和三级 State 持久化到阿里云表格存储（Tablestore），无需修改 Agent 业务逻辑。

## 前提条件

- 已创建表格存储（OTS）类型的记忆存储实例，且已开启**会话状态**功能。如尚未创建，请参见[创建和管理记忆存储](https://help.aliyun.com/zh/functioncompute/fc/create-and-manage-memory-storage)。
- 已安装 AgentRun SDK 和 Google ADK。
  
  ```
  pip install agentrun google-adk
  ```
- 已配置环境变量`MEMORY_COLLECTION_NAME`为已创建的记忆存储名称。
- 已配置环境变量`DASHSCOPE_API_KEY`（用于 LLM 模型服务）。

**

**重要**

会话状态功能开启后不可关闭，请确认后再开启。

## 快速开始

以下示例用 5 步将 Google ADK Agent 的会话持久化到 OTS。运行前需设置环境变量`DASHSCOPE_API_KEY`和`MEMORY_COLLECTION_NAME`。

各步骤说明：

- **初始化 SessionStore**：通过记忆存储（MemoryCollection）名称创建存储入口，并自动创建所需的 OTS 表和索引。
- **创建 OTSSessionService**：实例化 ADK 的会话持久化适配器。
- **定义 Agent**：配置模型和指令，创建 ADK Agent。
- **创建 Runner**：将 Agent 和 OTSSessionService 绑定。
- **运行对话**：创建 Session 并发起首轮对话，验证持久化效果。

```
import asyncio import os from google.adk.agents import Agent from google.adk.models.lite_llm import LiteLlm from google.adk.runners import Runner from google.genai import types from agentrun.conversation_service import SessionStore from agentrun.conversation_service.adapters import OTSSessionService # 步骤 1：初始化 SessionStore store = SessionStore.from_memory_collection( os.environ["MEMORY_COLLECTION_NAME"]) store.init_adk_tables() # 步骤 2：创建 OTSSessionService session_service = OTSSessionService(session_store=store) # 步骤 3：定义 Agent model = LiteLlm( model="openai/qwen-max", api_key=os.environ["DASHSCOPE_API_KEY"], api_base="https://dashscope.aliyuncs.com/compatible-mode/v1", ) agent = Agent( name="assistant", model=model, instruction="你是一个友好的中文智能助手。", ) # 步骤 4：创建 Runner runner = Runner( agent=agent, app_name="my_app", session_service=session_service, ) # 步骤 5：运行对话 async def main(): try: session = await session_service.create_session( app_name="my_app", user_id="user_1") content = types.Content( role="user", parts=[types.Part(text="你好，今天北京天气怎么样？")], ) async for event in runner.run_async( user_id="user_1", session_id=session.id, new_message=content, ): if event.is_final_response() and event.content and event.content.parts: for part in event.content.parts: if part.text: print(f"Agent: {part.text}") # 验证持久化 loaded = await session_service.get_session( app_name="my_app", user_id="user_1", session_id=session.id) print(f"持久化事件数: {len(loaded.events)}") except Exception as e: print(f"运行失败: {e}") raise asyncio.run(main())
```

运行后输出 Agent 的回复和持久化的事件数量。程序重启后，通过`get_session`加载同一个`session_id`，历史对话仍然存在。

## 集成指南

### 初始化 SessionStore

`SessionStore`是 Conversation Service 的核心入口。通过记忆存储名称初始化，SDK 会自动完成以下工作：

1. 调用 AgentRun API 获取记忆存储（MemoryCollection）配置。
2. 从中提取 Tablestore 的`endpoint`和`instance_name`。
3. 构建 OTS 客户端。

```
from agentrun.conversation_service import SessionStore # 记忆存储名称，需替换为实际值 store = SessionStore.from_memory_collection("your-memory-collection-name")
```

初始化后，需调用`init_adk_tables()`创建所需的数据库表和索引。该方法幂等，表或索引已存在时自动跳过，可在每次启动时调用。

```
store.init_adk_tables()
```

#### 异步初始化

`SessionStore`的所有方法均提供异步版本（方法名加`_async`后缀）：

```
store = await SessionStore.from_memory_collection_async( "your-memory-collection-name") await store.init_adk_tables_async()
```

### 创建 OTSSessionService

`OTSSessionService`是 Google ADK`BaseSessionService`的 OTS 实现。将其传入 ADK 的`Runner`，即可让 ADK 的会话自动持久化到 OTS。

```
from agentrun.conversation_service.adapters import OTSSessionService # 传入已初始化的 SessionStore session_service = OTSSessionService(session_store=store)
```

将`session_service`传入`Runner`：

```
from google.adk.runners import Runner runner = Runner( agent=agent, app_name="my_app", # 应用名称，对应 OTS 中的 agent_id session_service=session_service, # 传入 OTS 会话服务 )
```

`runner.run_async()`的所有对话会自动持久化到 OTS，包括：

- 用户消息
- Agent 回复
- 工具调用（`function_call`）和工具返回（`function_response`）
- State 变更（`state_delta`）

### Session 管理

#### 创建 Session

```
session = await session_service.create_session( app_name="my_app", user_id="user_1", session_id="custom-session-id", # 可选，不传则自动生成 UUID state={ # 可选，初始状态 "app:model_name": "qwen-max", # App 级状态（app: 前缀） "user:language": "zh-CN", # User 级状态（user: 前缀） "turn_count": 0, # Session 级状态（无前缀） }, ) print(f"Session ID: {session.id}")
```

参数说明：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| app_name | str | 是 | 应用名称，对应 OTS 中的`agent_id` |
| user_id | str | 是 | 用户 ID |
| session_id | str | 否 | 会话 ID，不传则自动生成 UUID |
| state | dict | 否 | 初始状态，会根据 key 前缀自动拆分到三级 State |

**

**说明**

在 Server 场景中，通常由客户端通过 HTTP Header 传入`session_id`，以便同一用户的多轮对话关联到同一个会话。如果不传，每次请求会创建一个新的独立会话。

#### 获取 Session

```
session = await session_service.get_session( app_name="my_app", user_id="user_1", session_id="your-session-id", ) if session is None: print("会话不存在") else: print(f"事件数: {len(session.events)}") print(f"当前状态: {session.state}")
```

返回的`session`对象包含：

| 属性 | 类型 | 说明 |
| --- | --- | --- |
| id | str | 会话 ID |
| app_name | str | 应用名称 |
| user_id | str | 用户 ID |
| events | list[Event] | 完整的 ADK Event 列表（按时间正序） |
| state | dict | 合并后的三级状态（详见三级 State 机制） |
| last_update_time | float | 最后更新时间（Unix 秒级时间戳） |

#### 控制返回的事件数量

通过`GetSessionConfig`控制只返回最近 N 条事件，避免一次性加载过多数据：

```
from google.adk.sessions.base_session_service import GetSessionConfig session = await session_service.get_session( app_name="my_app", user_id="user_1", session_id="your-session-id", config=GetSessionConfig(num_recent_events=20), # 仅返回最近 20 条事件 ) # session.events 只包含最近 20 条事件
```

通过`after_timestamp`只返回指定时间之后的事件：

```
import time one_hour_ago = time.time() - 3600 # 1 小时前的时间戳 session = await session_service.get_session( app_name="my_app", user_id="user_1", session_id="your-session-id", config=GetSessionConfig(after_timestamp=one_hour_ago), )
```

#### 列出 Session

列出指定用户的所有会话，按最后更新时间倒序排列：

```
response = await session_service.list_sessions( app_name="my_app", user_id="user_1", ) for s in response.sessions: print(f"Session: {s.id}, 最后更新: {s.last_update_time}")
```

不传`user_id`时，列出该应用下所有用户的会话：

```
response = await session_service.list_sessions( app_name="my_app", user_id=None, )
```

**

**说明**

`list_sessions`返回的 Session 对象不包含`events`和`state`（出于性能考虑），仅包含元信息。如需完整数据，请对感兴趣的 Session 调用`get_session`。

#### 删除 Session

删除会话时级联删除该会话下的所有事件和 Session 级状态（删除顺序：Event -> State -> Session 元数据）。操作幂等，中间步骤失败后重试可继续清理。

```
await session_service.delete_session( app_name="my_app", user_id="user_1", session_id="your-session-id", )
```

**

**说明**

删除 Session 不会影响 App 级和 User 级的状态。这两个级别的状态生命周期独立于单个 Session。

#### 同步方法

`OTSSessionService`的所有方法都提供同步版本，方法名加`_sync`后缀：

```
session = session_service.create_session_sync( app_name="my_app", user_id="user_1") session = session_service.get_session_sync( app_name="my_app", user_id="user_1", session_id="xxx") response = session_service.list_sessions_sync( app_name="my_app", user_id="user_1") session_service.delete_session_sync( app_name="my_app", user_id="user_1", session_id="xxx")
```

### 三级 State 机制

Google ADK 定义了三级 State 作用域，Conversation Service 将它们分别持久化到不同的 OTS 表中。

#### Key 前缀约定

ADK 通过 key 的前缀来区分 State 的作用域：

| 前缀 | 作用域 | 存储位置 | 示例 |
| --- | --- | --- | --- |
| `app:` | App 级 | app_state 表 | `app:model_name`、`app:total_queries` |
| `user:` | User 级 | user_state 表 | `user:language`、`user:preferences` |
| 无前缀 | Session 级 | state 表 | `turn_count`、`last_reply` |
| `temp:` | 临时状态 | 仅内存，不持久化 | `temp:processing` |

#### State 合并规则

通过`get_session`加载会话时，三级 State 按 App -> User -> Session 的顺序浅合并（后者覆盖前者）。返回的`session.state`是合并后的完整字典。

```
# 合并后 session.state 示例 { "turn_count": 3, "last_reply": "北京今天晴朗", "user:language": "zh-CN", "app:model_name": "qwen-max", "app:version": "1.0", }
```

#### 通过 state_delta 更新 State

在 ADK 中，Agent 可通过事件的`actions.state_delta`自动更新 State。`OTSSessionService`会自动将 delta 按前缀拆分并持久化到对应的 State 表：

```
from google.adk.events.event import Event from google.adk.events.event_actions import EventActions event = Event( invocation_id="inv-001", author="my_agent", content=..., actions=EventActions( state_delta={ "turn_count": 1, # 无前缀 -> state 表（Session 级） "app:total_queries": 42, # app: 前缀 -> app_state 表（App 级） "user:last_query_city": "北京", # user: 前缀 -> user_state 表（User 级） }, ), )
```

#### output_key 自动写入

ADK Agent 支持`output_key`参数，会自动将 Agent 的最终回复写入`session.state[output_key]`。搭配`OTSSessionService`，该值会自动持久化到 OTS 的 Session State 中。

```
agent = Agent( name="assistant", model=model, instruction="你是一个智能助手。", output_key="last_reply", # Agent 回复自动写入 state["last_reply"] )
```

后续通过`get_session`加载会话时，从`session.state["last_reply"]`读取上一轮的 Agent 回复。

#### 手动更新 State

除`state_delta`自动更新外，也可通过`SessionStore`手动更新指定级别的 State。常用于 Server 的`invoke_agent`回调。

```
# 更新 Session 级状态 await store.update_session_state_async( "my_app", "user_1", "session_id", {"turn_count": 5, "last_user_input": "今天天气如何"}, ) # 更新 User 级状态 await store.update_user_state_async( "my_app", "user_1", {"language": "en-US"}, ) # 更新 App 级状态 await store.update_app_state_async( "my_app", {"model_name": "qwen-turbo"}, )
```

State 更新采用浅合并语义：只覆盖提供的 key，未提供的 key 保持不变。将值设为`None`可以删除对应的 key。

### 工具定义与 ToolContext

ADK 支持在工具函数中通过`ToolContext`访问和操作当前 Session 的状态。`OTSSessionService`完整支持这一机制。

```
from google.adk.tools import ToolContext def get_session_state(tool_context: ToolContext) -> dict: """获取当前会话的状态信息。""" return tool_context.state.to_dict() def update_preference(city: str, tool_context: ToolContext) -> str: """更新用户偏好的城市。""" tool_context.state["user:preferred_city"] = city return f"已更新偏好城市为: {city}" agent = Agent( name="assistant", model=model, instruction="你是一个智能助手。", tools=[get_session_state, update_preference], )
```

通过`ToolContext`修改的 State 会通过`state_delta`自动持久化到 OTS。

### 结合 AgentRunServer 部署

将 ADK Agent 部署为 HTTP 服务的完整示例。请将以下代码保存为`conversation_service_adk_server.py`，后续部署章节将引用该文件。

```
import os import uuid from typing import Any from google.adk.agents import Agent from google.adk.models.lite_llm import LiteLlm from google.adk.runners import Runner from google.genai import types from agentrun import AgentRequest from agentrun.conversation_service import SessionStore from agentrun.conversation_service.adapters import OTSSessionService from agentrun.server import AgentRunServer APP_NAME = "my_chat_server" # ── 初始化 ──────────────────────────────────────────────────── store = SessionStore.from_memory_collection( os.environ["MEMORY_COLLECTION_NAME"]) store.init_adk_tables() session_service = OTSSessionService(session_store=store) model = LiteLlm( model="openai/qwen3-max", api_key=os.environ["DASHSCOPE_API_KEY"], api_base="https://dashscope.aliyuncs.com/compatible-mode/v1", ) agent = Agent( name="assistant", model=model, instruction="你是一个友好的中文智能助手。", output_key="last_reply", ) runner = Runner( agent=agent, app_name=APP_NAME, session_service=session_service, ) # ── 辅助函数 ────────────────────────────────────────────────── async def get_or_create_session(user_id: str, session_id: str) -> Any: """获取已有 session，不存在则自动创建。""" existing = await session_service.get_session( app_name=APP_NAME, user_id=user_id, session_id=session_id, ) if existing is not None: return existing return await session_service.create_session( app_name=APP_NAME, user_id=user_id, session_id=session_id, ) # ── 核心处理函数 ────────────────────────────────────────────── async def invoke_agent(req: AgentRequest): # 从 HTTP Header 获取 session_id 和 user_id headers = dict(req.raw_request.headers) if req.raw_request else {} session_id = ( headers.get("x-agentrun-session-id") or f"chat_{uuid.uuid4().hex[:8]}" ) user_id = headers.get("x-agentrun-user-id") or "default_user" # 获取或创建 Session session = await get_or_create_session(user_id, session_id) # 提取用户消息 last_user_text = "" for msg in reversed(req.messages): if msg.role == "user": last_user_text = msg.content or "" break if not last_user_text: yield "请输入问题。" return # 转换为 ADK Content 格式并调用 Runner content = types.Content( role="user", parts=[types.Part(text=last_user_text)], ) async for event in runner.run_async( user_id=user_id, session_id=session.id, new_message=content, ): if ( event.is_final_response() and event.content and event.content.parts ): for part in event.content.parts: if part.text: yield part.text # ── 启动服务 ────────────────────────────────────────────────── if __name__ == "__main__": server = AgentRunServer( invoke_agent=invoke_agent, memory_collection_name=os.environ["MEMORY_COLLECTION_NAME"], ) server.start(port=9000)
```

客户端请求时的 Header 约定：

| Header | 说明 | 必填 |
| --- | --- | --- |
| X-AgentRun-Session-ID | 会话 ID，用于关联多轮对话 | 否（不传则自动生成新会话） |
| X-AgentRun-User-ID | 用户 ID | 否（默认`default_user`） |

本地测试：

```
curl -X POST http://localhost:9000/openai/v1/chat/completions \ -H "Content-Type: application/json" \ -H "X-AgentRun-Session-ID: my-session-1" \ -H "X-AgentRun-User-ID: user-1" \ -d '{"model":"qwen-max","stream":true,"messages":[{"role":"user","content":"你好"}]}'
```

## 部署到 AgentRun 云平台

通过 Serverless Devs 工具将 Agent 部署到 AgentRun 云平台。

### 安装部署工具

#### 安装 Serverless Devs

Serverless Devs（`s`命令）用于将代码部署到 AgentRun，通过 npm 安装：

```
npm install -g @serverless-devs/s
```

安装完成后验证：

```
s --version
```

#### 配置阿里云凭证

运行以下命令配置阿里云密钥，按引导输入 AccessKey ID 和 AccessKey Secret。记住密钥对名称（如`default`），该名称用于`s.yaml`中的`access`字段：

```
s config add
```

#### 安装 Docker

`s build`命令需要 Docker 来构建 Linux x64 兼容的依赖包。请安装 Docker Desktop 或其他兼容环境（如 Podman、Lima）。

### 准备配置文件

**requirements.txt**：确保项目根目录下有`requirements.txt`文件：

```
agentrun-sdk[server,google-adk]==0.0.31 python-dotenv>=1.0.0
```

**.fcignore**：创建`.fcignore`文件，排除敏感文件和本地环境：

```
.env .venv
```

**s.yaml**：在项目根目录创建`s.yaml`配置文件：

```
edition: 3.0.0 name: my-conversation-service access: 'default' # 修改为通过 s config add 配置的密钥对名称 vars: region: 'cn-hangzhou' agent_name: 'my-adk-agent' # Agent 名称 role: 'acs:ram::${config("AccountID")}:role/AliyunAgentRunDefaultRole' memory_collection_name: 'your-memory-collection-name' # 替换为记忆存储名称 api_key: 'your-dashscope-api-key' # 替换为 DashScope API Key resources: agent: component: agentrun props: region: ${vars.region} agent: name: ${vars.agent_name} description: 'Google ADK Conversation Service' role: ${vars.role} code: src: ./ language: python3.12 command: - python3 - conversation_service_adk_server.py cpu: 1.0 memory: 2048 port: 9000 instanceConcurrency: 200 internetAccess: true environmentVariables: PYTHONPATH: /code/python:/opt/python:/code:/code/python MEMORY_COLLECTION_NAME: '${vars.memory_collection_name}' DASHSCOPE_API_KEY: '${vars.api_key}' logConfig: auto endpoints: - name: prod version: LATEST description: '生产环境端点'
```

配置说明：

| 字段 | 说明 |
| --- | --- |
| `access` | `s config add`时设置的密钥对名称 |
| `vars.role` | Agent 运行时的 RAM 角色。`AliyunAgentRunDefaultRole`是默认角色，创建和授权步骤参见「配置 RAM 角色授权」 |
| `code.command` | 启动命令，此处指向`conversation_service_adk_server.py`（即上文「结合 AgentRunServer 部署」中的完整代码示例）。如果使用其他文件名，需同步修改此处 |
| `environmentVariables` | 云上环境变量，替代本地的`.env`文件 |

### 构建依赖

云上为 Linux x64 环境，通过`s build`在 Docker 中安装兼容的依赖（拉取函数计算运行镜像，执行`pip install`，输出到`python/`目录）：

```
s build --use-docker
```

### 部署

执行部署命令：

```
s deploy
```

部署成功后，输出中会包含 Agent 的访问 URL：

```
endpoints: - name: prod url: https://<account-id>.agentrun-data.cn-hangzhou.aliyuncs.com/agent-runtimes/<agent-name>/endpoints/prod/invocations status: READY
```

### 测试

使用部署输出的 URL 发起请求。将`<your-endpoint-url>`替换为`s deploy`输出的实际 URL：

```
curl -X POST https://<your-endpoint-url>/openai/v1/chat/completions \ -H "Content-Type: application/json" \ -H "X-AgentRun-Session-ID: my-session-1" \ -H "X-AgentRun-User-ID: user-1" \ -d '{"model":"qwen-max","stream":true,"messages":[{"role":"user","content":"你好"}]}'
```

## 常见问题

### init_adk_tables() 需要每次启动都调用吗？

`init_adk_tables()`是幂等操作，表或索引已存在时自动跳过。建议在应用启动时调用，确保资源就绪。

### Session 删除后 App 级和 User 级状态还在吗？

`delete_session`只删除 Session 本身及其关联的事件和 Session 级状态。App 级状态和 User 级状态的生命周期独立于单个 Session，不会被级联删除。

### 如何处理并发写入冲突？

State 更新使用乐观锁机制（version 字段）。如果两个请求同时更新同一行，后到的请求会因 version 不匹配而失败。在高并发场景下，建议在业务层实现重试逻辑。

### ADK 和 LangChain / LangGraph 的区别

详见上文「选型建议：何时选用 ADK 方案」中的对比表。核心结论：如果你的 Agent 涉及多工具调用、需要维护多层级状态（如应用级配置、用户偏好、会话上下文），ADK 配合 OTSSessionService 是更合适的选择。

### 支持哪些模型？

Conversation Service 不限制模型选择。示例中使用的是通义千问（通过 DashScope API 调用），可以替换为任何 ADK 支持的模型（如 Gemini、OpenAI 等）。模型选择由 ADK 的 Agent 配置决定，与 Conversation Service 无关。

### 常见错误及排查

| **错误场景** | **排查方法** |
| --- | --- |
| 认证失败（AccessKey 无效或过期） | 检查环境变量`ALIBABA_CLOUD_ACCESS_KEY_ID`和`ALIBABA_CLOUD_ACCESS_KEY_SECRET`是否正确配置。确认 AccessKey 未被禁用，且对应的 RAM 用户有 Tablestore 访问权限。 |
| 网络超时（OTS 连接失败） | 确认记忆存储中配置的`endpoint`可达。如果在 VPC 内运行，检查是否使用了 VPC 内网 endpoint。网络不稳定时可在业务层增加重试逻辑。 |
| 环境变量缺失 | 运行时报`KeyError: MEMORY_COLLECTION_NAME`等错误，说明必需的环境变量未设置。使用`.env`文件配合`python-dotenv`加载，或在部署环境的`s.yaml`中配置 environmentVariables。 |
| 记忆存储不存在 | 确认`MEMORY_COLLECTION_NAME`的值与 AgentRun 平台上创建的资源名称完全一致（区分大小写）。 |
