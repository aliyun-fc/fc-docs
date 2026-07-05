# 使用 Endpoint 调用 Flow Agent

## 适用场景

在 AgentRun 控制台通过 Flow（流程画布）创建 Agent 后，需要通过 HTTP API 以多种协议调用该 Agent 的场景。适用于需要与 Dify Workflow、Dify Chatflow、OpenAI 兼容接口或原生协议集成的开发者。

## 短描述

若已通过 Flow 创建了 Agent，希望用统一 Endpoint 以 Dify Workflow / Dify Chatflow / OpenAI / 原生协议发起调用并支持流式与非流式，可使用 AgentRun Flow Endpoint。本文说明各协议的请求字段映射及流式/非流式调用方式，便于一次创建、多协议复用。

## 前置条件

- **已创建并发布 Flow Agent**：在[AgentRun控制台](https://functionai.console.aliyun.com/cn-hangzhou/agent/runtime/agent-list)通过 Flow 创建并发布 Agent。操作步骤见[低代码创建Agent快速入门](https://help.aliyun.com/zh/functioncompute/fc/quick-start-to-low-code-agent-creation)。
- **已获取调用地址**：在 Agent 详情页**集成与发布**>**代码集成**中查看 Endpoint与调用示例。下文示例中的Host与Flow名称需替换为您自己的值。

## 兼容协议列表

| **协议** | **说明** | **典型用途** |
| --- | --- | --- |
| **Dify Workflow** | 与 Dify 工作流运行接口兼容 | 从 Dify 或自建系统以工作流方式调用 |
| **Dify Chatflow** | 与 Dify 对话流接口兼容 | 对话/聊天场景，支持会话与流式输出 |
| **OpenAI** | 与 OpenAI Chat Completions 兼容 | 使用 OpenAI SDK 或兼容客户端调用 |
| **原生协议** | AgentRun 原生入参格式 | 直接映射到 Flow 开始节点声明的字段 |

## Dify Workflow

### 输入字段说明

**支持的请求字段：**

- **inputs**：工作流输入，键值对会映射到 Flow 开始节点中声明的对应字段。
- **response_mode**：响应模式，如`streaming`（流式）或`blocking`（非流式）。
- **user**：用户标识，映射到开始节点中的`sys.user_id`。
- **files**：文件列表，映射到开始节点中的`sys.files`。**注意**：当前仅支持`transfer_method`为`remote_url`的 file。

**输入字段转换规则：**

- `inputs`中所有字段按 key 一一映射为开始节点中声明的同名字段。
- `user`转换为开始节点中的`sys.user_id`。
- `files`转换为开始节点中的`sys.files`（仅支持`transfer_method`为`remote_url`的 file）。

### 流式调用

**请求示例：**

```
curl https://<your-account-id>.agentrun-data.cn-hangzhou.aliyuncs.com/flows/<FlowName>/invocations/dify-workflow/v1/workflows/Default/run -XPOST \ -H "content-type: application/json" \ -d '{ "inputs": {"sys.query": "Hello World!"}, "conversation_id": "conversation_id", "user": "user-abc", "response_mode": "streaming" }'
```

**响应示例：**

```
data: {"task_id":"11587906-a92a-4055-a428-f1e469cc4405","workflow_run_id":"11587906-a92a-4055-a428-f1e469cc4405","event":"workflow_started","data":{"id":"11587906-a92a-4055-a428-f1e469cc4405","workflow_id":"agent-flow-K9Dfu","created_at":1770089211}} data: {"task_id":"11587906-a92a-4055-a428-f1e469cc4405","workflow_run_id":"11587906-a92a-4055-a428-f1e469cc4405","event":"node_started","data":{"id":"2ce857570b86864c91ec4c2f","node_id":"LLM","node_type":"llm","title":"LLM","index":0,"predecessor_node_id":null,"inputs":{"sys.conversation_id":null,"sys.query":"Hello World!","sys.user_id":"user-abc"},"created_at":1770089211}} data: {"task_id":"11587906-a92a-4055-a428-f1e469cc4405","workflow_run_id":"11587906-a92a-4055-a428-f1e469cc4405","event":"text_chunk","data":{"text":"Hello","from_variable_selector":null}} data: {"task_id":"11587906-a92a-4055-a428-f1e469cc4405","workflow_run_id":"11587906-a92a-4055-a428-f1e469cc4405","event":"text_chunk","data":{"text":"! How can","from_variable_selector":null}} data: {"task_id":"11587906-a92a-4055-a428-f1e469cc4405","workflow_run_id":"11587906-a92a-4055-a428-f1e469cc4405","event":"text_chunk","data":{"text":" I assist you","from_variable_selector":null}} data: {"task_id":"11587906-a92a-4055-a428-f1e469cc4405","workflow_run_id":"11587906-a92a-4055-a428-f1e469cc4405","event":"text_chunk","data":{"text":" today?","from_variable_selector":null}} data: {"task_id":"11587906-a92a-4055-a428-f1e469cc4405","workflow_run_id":"11587906-a92a-4055-a428-f1e469cc4405","event":"text_chunk","data":{"text":".","from_variable_selector":null}} data: {"task_id":"11587906-a92a-4055-a428-f1e469cc4405","workflow_run_id":"11587906-a92a-4055-a428-f1e469cc4405","event":"node_finished","data":{"id":"2ce857570b86864c91ec4c2f","node_id":"LLM","index":0,"predecessor_node_id":null,"inputs":{"sys.conversation_id":null,"sys.query":"Hello World!","sys.user_id":"user-abc"},"process_data":null,"outputs":{"text":"Hello! How can I assist you today? "},"status":"succeeded","error":"","elapsed_time":0.728,"created_at":1770089211}} data: {"task_id":"11587906-a92a-4055-a428-f1e469cc4405","workflow_run_id":"11587906-a92a-4055-a428-f1e469cc4405","event":"workflow_finished","data":{"id":"11587906-a92a-4055-a428-f1e469cc4405","workflow_id":"agent-flow-K9Dfu","status":"succeeded","outputs":{"text":"Hello! How can I assist you today?"},"error":"","elapsed_time":0.731,"total_tokens":27,"total_steps":2,"created_at":1770089211,"finished_at":1770089211}} data: [DONE]
```

**响应说明：**流式响应为 Server-Sent Events（SSE），每行以`data:`开头。事件类型包括：`workflow_started`、`node_started`、`text_chunk`、`node_finished`、`workflow_finished`，以及结束标记`data: [DONE]`。其中`text_chunk`的`data.text`为增量文本内容。

### 非流式调用

**请求示例：**

```
curl https://<your-account-id>.agentrun-data.cn-hangzhou.aliyuncs.com/flows/<FlowName>/invocations/dify-workflow/v1/workflows/Default/run -XPOST \ -H "content-type: application/json" \ -d '{ "inputs": {"sys.query": "Hello World!"}, "conversation_id": "conversation_id", "user": "user-abc" }'
```

**响应示例：**

```
{ "workflow_run_id":"840c5c05-3912-4a0b-a976-8d89f42d5dcc", "task_id":"840c5c05-3912-4a0b-a976-8d89f42d5dcc", "data":{ "id":"840c5c05-3912-4a0b-a976-8d89f42d5dcc", "workflow_id":"agent-flow-K9Dfu", "status":"succeeded", "outputs":{ "text":"Hello! How can I assist you today? " }, "error":null,"elapsed_time":1.2429999999999999, "total_tokens":27, "total_steps":2, "created_at":1770089350, "finished_at":1770089351 } }
```

**响应说明：**返回 JSON，包含`workflow_run_id`、`task_id`以及`data`（含`outputs`、`status`、`elapsed_time`等）。完整结果在`data.outputs`中，例如`answer`字段为最终回复内容。

## Dify Chatflow

### 输入字段说明

**支持的请求字段：**

- **query**：用户问题，映射到开始节点中的`sys.query`。
- **inputs**：额外输入，键值对映射到开始节点中声明的对应字段。
- **response_mode**：响应模式，如`streaming`（流式）或`blocking`（非流式）。
- **user**：用户标识，映射到`sys.user_id`。
- **conversation_id**：会话 ID，映射到`sys.conversation_id`。
- **files**：文件列表，映射到`sys.files`。**注意**：当前仅支持`transfer_method`为`remote_url`的 file。
- **workflow_id**：可选，用于指定执行的工作流版本。

**输入字段转换规则：**

- `query`转换为开始节点中的`sys.query`。
- `inputs`中所有字段映射为开始节点中声明的对应字段。
- `user`转换为`sys.user_id`。
- `conversation_id`转换为`sys.conversation_id`。
- `files`转换为`sys.files`（仅支持`transfer_method`为`remote_url`的 file）。

### 流式调用

**请求示例：**

```
curl https://<your-account-id>.agentrun-data.cn-hangzhou.aliyuncs.com/flows/<FlowName>/invocations/dify-chatflow/v1/chat-messages -XPOST \ -H "content-type: application/json" \ -d '{ "inputs": {}, "query": "Hello World!", "conversation_id": "conversation_id", "user": "user-abc", "response_mode": "streaming" }'
```

**响应示例：**

```
data: {"task_id":"d154697c-420e-4d87-b642-21f112e8b1f0","workflow_run_id":"d154697c-420e-4d87-b642-21f112e8b1f0","event":"workflow_started","data":{"id":"d154697c-420e-4d87-b642-21f112e8b1f0","workflow_id":"agent-flow-K9Dfu","created_at":1770089528}} data: {"task_id":"d154697c-420e-4d87-b642-21f112e8b1f0","workflow_run_id":"d154697c-420e-4d87-b642-21f112e8b1f0","event":"node_started","data":{"id":"e26bc36509d8b91fe8df0469","node_id":"LLM","node_type":"llm","title":"LLM","index":0,"predecessor_node_id":null,"inputs":{"sys.conversation_id":"conversation_id","sys.query":"Hello World!","sys.user_id":"user-abc"},"created_at":1770089528}} data: {"task_id":"d154697c-420e-4d87-b642-21f112e8b1f0","workflow_run_id":"d154697c-420e-4d87-b642-21f112e8b1f0","event":"node_finished","data":{"id":"e26bc36509d8b91fe8df0469","node_id":"LLM","index":0,"predecessor_node_id":null,"inputs":{"sys.conversation_id":"conversation_id","sys.query":"Hello World!","sys.user_id":"user-abc"},"process_data":null,"outputs":{"text":"Hello! How can I assist you today? "},"status":"succeeded","error":"","elapsed_time":0.864,"created_at":1770089528,"execution_metadata":{"total_tokens":0}}} data: {"task_id":"d154697c-420e-4d87-b642-21f112e8b1f0","workflow_run_id":"d154697c-420e-4d87-b642-21f112e8b1f0","event":"workflow_finished","data":{"id":"d154697c-420e-4d87-b642-21f112e8b1f0","workflow_id":"agent-flow-K9Dfu","status":"succeeded","outputs":{"text":"Hello! How can I assist you today? "},"error":"","elapsed_time":0.867,"total_tokens":27,"total_steps":2,"created_at":1770089528,"finished_at":1770089529}} data: {"event":"message_end","task_id":"d154697c-420e-4d87-b642-21f112e8b1f0","message_id":"d154697c-420e-4d87-b642-21f112e8b1f0","conversation_id":"conversation_id","metadata":{"usage":{"prompt_tokens":16,"completion_tokens":11,"total_tokens":27,"latency":0.862921526}}} data: [DONE]
```

**响应说明：**流式响应为 SSE。除工作流事件外，会返回`event: "message"`的增量消息（`answer`为当前片段）；结束时返回`message_end`（含`metadata.usage`）及`data: [DONE]`。

### 非流式调用

**请求示例：**

```
curl https://<your-account-id>.agentrun-data.cn-hangzhou.aliyuncs.com/flows/<FlowName>/invocations/dify-chatflow/v1/chat-messages -XPOST \ -H "content-type: application/json" \ -d '{ "inputs": {}, "query": "Hello World!", "conversation_id": "conversation_id", "user": "user-abc" }'
```

**响应示例：**

```
{"event":"message","task_id":"5437503b-de66-43ae-8172-258aa165620b","id":"5437503b-de66-43ae-8172-258aa165620b","message_id":"5437503b-de66-43ae-8172-258aa165620b","conversation_id":"conversation_id","mode":"chat","answer":"","metadata":{"usage":{"prompt_tokens":16,"completion_tokens":11,"total_tokens":27,"latency":0.721599425}},"created_at":1770089691}
```

**响应说明：**返回单条 JSON 消息，包含`event`、`task_id`、`message_id`、`conversation_id`、`answer`（完整回复）以及`metadata.usage`（如 token 用量、latency）。

## OpenAI

### 输入字段说明

**支持的请求字段：**

- **messages**：对话消息列表，最后一条作为当前用户输入，其余作为历史。
- **user**：用户标识，映射到开始节点中的`sys.user_id`。
- **stream**：是否流式返回，如`true`为流式。
- **stream_options.include_usage**：流式时是否在最后包含 usage 信息（可选）。

**输入字段转换规则：**

- `messages`中**最后一条**message 转换为开始节点中的`sys.query`。
- `messages`中**非最后一条**的所有 message 转换为开始节点中的`sys.history_message`。
- `user`转换为开始节点中的`sys.user_id`。

### 流式调用

**请求示例：**

```
curl https://<your-account-id>.agentrun-data.cn-hangzhou.aliyuncs.com/flows/<FlowName>/endpoints/<EndpointName>/invocations/openai/v1/chat/completions -XPOST \ -H "content-type: application/json" \ -d '{ "messages": [{"role": "user", "content": "Hello World!"}], "stream": true }'
```

**响应示例：**

```
data: {"id":"chatcmpl-fc24b409-ac10-4ffe-a92f-4e8d27b3480c","object":"chat.completion.chunk","created":1769394569,"model":"demoflow2","system_fingerprint":"","choices":[{"index":0,"delta":{"content":"","role":"assistant"},"logprobs":null,"finish_reason":null}],"usage":null} data: {"id":"chatcmpl-fc24b409-ac10-4ffe-a92f-4e8d27b3480c","object":"chat.completion.chunk","created":1769394569,"model":"demoflow2","system_fingerprint":"","choices":[{"index":0,"delta":{"content":"Hello"},"logprobs":null,"finish_reason":null}],"usage":null} data: {"id":"chatcmpl-fc24b409-ac10-4ffe-a92f-4e8d27b3480c","object":"chat.completion.chunk","created":1769394569,"model":"demoflow2","system_fingerprint":"","choices":[{"index":0,"delta":{"content":"! It"},"logprobs":null,"finish_reason":null}],"usage":null} data: {"id":"chatcmpl-fc24b409-ac10-4ffe-a92f-4e8d27b3480c","object":"chat.completion.chunk","created":1769394569,"model":"demoflow2","system_fingerprint":"","choices":[{"index":0,"delta":{"content":"'s nice to"},"logprobs":null,"finish_reason":null}],"usage":null} data: {"id":"chatcmpl-fc24b409-ac10-4ffe-a92f-4e8d27b3480c","object":"chat.completion.chunk","created":1769394569,"model":"demoflow2","system_fingerprint":"","choices":[{"index":0,"delta":{"content":" meet you."},"logprobs":null,"finish_reason":null}],"usage":null} data: {"id":"chatcmpl-fc24b409-ac10-4ffe-a92f-4e8d27b3480c","object":"chat.completion.chunk","created":1769394569,"model":"demoflow2","system_fingerprint":"","choices":[{"index":0,"delta":{"content":" How can I assist you today"},"logprobs":null,"finish_reason":null}],"usage":null} data: {"id":"chatcmpl-fc24b409-ac10-4ffe-a92f-4e8d27b3480c","object":"chat.completion.chunk","created":1769394569,"model":"demoflow2","system_fingerprint":"","choices":[{"index":0,"delta":{"content":"?"},"logprobs":null,"finish_reason":null}],"usage":null} data: {"id":"chatcmpl-fc24b409-ac10-4ffe-a92f-4e8d27b3480c","object":"chat.completion.chunk","created":1769394569,"model":"demoflow2","system_fingerprint":"","choices":[{"index":0,"delta":{"content":""},"logprobs":null,"finish_reason":"stop"}],"usage":null}
```

**响应说明：**流式响应为 SSE，格式与 OpenAI Chat Completions 流式一致。每个 chunk 包含`choices[].delta.content`；最后一个 chunk 的`finish_reason`为`stop`，可选返回`usage`。

### 非流式调用

**请求示例：**

```
curl https://<your-account-id>.agentrun-data.cn-hangzhou.aliyuncs.com/flows/<FlowName>/endpoints/<EndpointName>/invocations/openai/v1/chat/completions -XPOST \ -H "content-type: application/json" \ -d '{ "messages": [{"role": "user", "content": "Hello World!"}] }'
```

**响应示例：**

```
{"id":"chatcmpl-2bcde391-3e8d-4480-936f-a839ce9e6c80","object":"chat.completion","created":1770089819,"model":"agent-flow-K9Dfu","choices":[{"index":0,"message":{"role":"assistant","content":"","refusal":null,"annotations":null},"logprobs":null,"finish_reason":"stop"}],"usage":{"prompt_tokens":16,"completion_tokens":11,"total_tokens":27,"prompt_tokens_details":{"cached_tokens":0,"audio_tokens":0},"completion_tokens_details":{"reasoning_tokens":0,"audio_tokens":0,"accepted_prediction_tokens":0,"rejected_prediction_tokens":0}},"service_tier":"default"}
```

**响应说明：**返回单条 JSON，包含`id`、`choices[0].message.content`、`usage`（prompt_tokens、completion_tokens、total_tokens）等，与 OpenAI 接口格式一致。

## 原生协议

### 输入字段说明

**支持的 input 字段：**请求 body 中的**所有字段**会按 key 映射为 Flow 开始节点中声明的对应字段，无额外转换规则。

常用字段示例（具体以您在 Flow 开始节点中声明的为准）：

- **sys.query**：用户输入。
- **sys.conversation_id**：会话 ID。
- **sys.user_id**或**sys.user**：用户标识（以开始节点声明为准）。

### 调用方式

**请求示例：**

```
curl https://<your-account-id>.agentrun-data.cn-hangzhou.aliyuncs.com/flows/<FlowName>/endpoints/<EndpointName>/invocations -XPOST \ -H "content-type: application/json" \ -d '{ "sys.query": "你好", "sys.conversation_id": "conversation_id", "sys.user": "user-abc" }'
```

**响应示例：**

```
{ "FlowName":"agent-flow-K9Dfu", "Name":"5037cfb1-6e45-463f-aeef-f1284e449c45", "SessionId":"", "Output":"{\"text\":\"你好！有什么问题我可以帮助你吗？\"}", "ErrorCode":"", "ErrorMessage":"", "Status":"Succeeded", "RequestId":"84fd9a0a-5890-d020-e4f6-74f22cb1acc9", "StartedTime":"2026-02-03T03:38:04.792Z", "StoppedTime":"2026-02-03T03:38:08.109Z", "Environment":{ "Variables":[] } }
```

**响应说明：**返回 JSON，包含`FlowName`、`Name`（执行 ID）、`SessionID`、`Output`（JSON 字符串，如`{"answer":"..."}`）、`Status`、`ErrorCode`、`ErrorMessage`、`RequestId`、`StartedTime`、`StoppedTime`等。

**更多说明：**参数约定、错误码及进阶用法请参见[调用协议说明（原生协议）](https://help.aliyun.com/zh/functioncompute/fc/call-protocol-description-native-protocol)。

## AI 网关调用

Flow Agent 可通过 AI 网关进行统一接入与治理，具体调用方式、鉴权及路由策略请参见[使用 AI 网关调用 Flow Agent](https://help.aliyun.com/zh/functioncompute/fc/call-flow-agent-using-ai-gateway)。

## 相关文档

- [低代码创建Agent快速入门](https://help.aliyun.com/zh/functioncompute/fc/quick-start-to-low-code-agent-creation)：创建 Flow Agent 及在控制台查看 API 调用示例。
- [调用协议说明（原生协议）](https://help.aliyun.com/zh/functioncompute/fc/call-protocol-description-native-protocol)：原生协议参数、错误码及详细约定。
