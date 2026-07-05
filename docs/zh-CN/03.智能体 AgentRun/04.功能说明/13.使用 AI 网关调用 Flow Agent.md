# 使用 AI 网关调用 Flow Agent

需要将已发布的 Flow Agent 暴露为标准 HTTP API 并接入鉴权限流能力时，可使用 AI 网关。本文介绍通过 AI 网关调用 Flow Agent 的完整流程，包括实例创建、Agent 绑定、路由配置及 API 调用方法。

## 适用场景

已将 Flow Agent 发布上线，且需要通过标准 HTTP API 供前端、移动端或第三方系统调用时，可使用 AI 网关。接入 AI 网关后，可获得以下能力：

- 同步与流式响应：支持 SSE（Server-Sent Events）流式输出，适用于对话场景
- 会话保持：通过会话 ID 维持多轮对话上下文
- 鉴权与限流：保护 Agent API 免受滥用
- 日志与监控：追踪每次调用的执行状态与耗时

## 前提条件

- 已在[AgentRun 控制台](https://functionai.console.aliyun.com/cn-hangzhou/agent/runtime/agent-list)创建并发布 Flow Agent。详情请参见 。
- 已开通函数计算（FC）服务并创建资源配额。

**

**重要**

AI 网关实例创建后将分配一个访问域名作为访问入口。生产中建议将业务域名通过 DNS CNAME 至该访问域名。直接使用访问域名每天有 1000 次访问限制，请勿用于生产环境。

## 创建 AI 网关实例

1. 进入[AI 网关控制台](https://apig.console.aliyun.com/)，在左侧导航栏选择******>******。
2. 在页面顶部****下拉框中，选择与 Flow Agent 相同的地域。
3. 选择**创建实例**，进入购买页。建议参考  按需配置，本文采用满足测试要求的最低规格：
  
  1. **商品类型**：选择**Serverless（按量付费）**。
  2. ****：选择与 Flow Agent 相同的地域。
  3. **网关名称**：自定义名称，如`aistudio_wg_demo`。
  4. **网络访问类型**：选择**公网**。
    
    **
    
    **说明**
    
    通过公网访问网关时，将产生公网流量费用。公网流量基于云数据传输 CDT（Cloud Data Transfer）统一计费和出账，采用多线 BGP 模式。详情请参见 。
  5. **专有网络**：根据客户端网络选择 AI 网关实例所在的 VPC。若上一步选择私网，需确保 AI 网关与调用端在同一 VPC 内。
4. 选择****，完成购买。返回**AI 网关**>****列表，等待实例状态显示为运行中。

**

**说明**

**计费说明**：AI 网关实例采用 Serverless 按量付费模式，按实际调用次数和资源使用量计费。公网访问产生的流量费用按 CDT 标准计费。详情请参见 。

## AI 网关接入配置

### 步骤一：配置网关服务（绑定 Flow Agent）

1. 进入[AI 网关控制台](https://apig.console.aliyun.com/#/cn-shanghai/ai-gateway?region=cn-shanghai)，在页面顶部****下拉框中选择实例所在地域。
2. 在实例列表中，选择目标实例，进入实例的****页面。
3. 在左侧导航栏选择****>**创建服务**，在****页面完成以下配置：
  
  1. **服务来源**：选择**云工作流 CloudFlow**。
  2. **工作流程**：选择需要接入的 Flow Agent。
  3. 选择**确定**，完成服务创建。

### 步骤二：配置 Agent API

1. 在左侧导航栏选择**Agent API**>**创建 Agent API**。
2. 在**创建 Agent API**页面完成以下配置：
  
  1. **API 名称**：自定义名称，支持英文、数字、下划线和连字符，不超过 64 个字符，如`aistudio_api_demo`。
  2. ****：如果没有可选域名，需要先选择****参考  创建域名。也可以直接在选择****后，在****输入框中输入`*`。
    
    **
    
    **重要**
    
    - 使用`*`或 IP/接入点访问仅适用于暂无域名的测试场景，存在安全风险，请谨慎使用。
    - 网关实例的访问域名可在实例详情的****页面查看。
    - 访问域名是网关实例的访问入口。生产中需将业务域名通过 DNS CNAME 至访问域名。直接使用访问域名每天有 1000 次访问限制，请勿用于生产环境。
  3. **Base Path**：保持默认或按需配置，如`/example_base`。
  4. ****：选择****。
3. 选择****，完成 Agent API 创建。

### 步骤三：配置路由（定义调用路径）

完成  后，进入 Agent API 详情页，继续完成路由配置。

1. 在**Agent API**详情页，选择**路由列表**>**创建路由**。
2. 在**创建路由**页面完成以下配置：
  
  1. **路由名称**：自定义路由名称（创建后不可修改）。
  2. **路径（Path）**：按需配置，如`/example_path`。后续 API 调用时路径需与此处一致。
  3. **Agent 服务**：**服务类型**选择**单服务**，服务名称选择在  中创建的****。
  4. 展开更多匹配规则，**方法（Method）**选择**POST**。
3. 选择****，完成路由创建。
4. 在路由详情页，选择**发布路由**，然后选择****。
5. 路由列表显示**已发布**时，表示发布成功。

## 调用 Flow Agent

完成上述配置后，通过 HTTP POST 调用已接入 AI 网关的 Flow Agent，请求 body 将作为工作流输入参数。

### 基础调用示例

以下是最简调用示例。请将 URL 中的尖括号占位符替换为实际值：

- `<YOUR_AI_GW_ENDPOINT>`：替换为 AI 网关实例的访问域名或自定义域名
- `<base_path>`：替换为 Agent API 中配置的 Base Path
- `<route_path>`：替换为路由中配置的路径

```
curl \ -H "Content-Type: application/json" \ http://<YOUR_AI_GW_ENDPOINT>/<base_path>/<route_path> \ -d '{ "sys.query": "Hello, who are you?" }'
```

请求参数说明：

| **参数** | **说明** | **示例** |
| --- | --- | --- |
| `<YOUR_AI_GW_ENDPOINT>` | 生产环境替换为 Agent API 中配置的自定义域名；测试可使用 AI 网关接入点。 | `ai******-gw.cn-hangzhou.fcapp.run`或`api.yourcompany.com` |
| `<base_path>` | Agent API 中配置的 Base Path。 | `/example_base` |
| `<route_path>` | 路由中配置的路径。 | `/example_path` |
| `sys.query` | 通过 body 传入的内置变量（在 Flow**开始节点**可查看）；也可传入自定义变量。 | ```<br>{ "sys.query": "Hello, who are you?", "context": "your_context", "doc_md": "doc_md", "number": 123, "type": "a" }<br>``` |

### 会话亲和调用模式

AI 网关支持会话亲和（Session Affinity）调用模式，通过`x-agentrun-session-id`请求头维持多轮对话的上下文关联。同一`x-agentrun-session-id`的请求会被路由到相同的后端实例，确保对话状态连续。

调用时在请求头中添加`x-agentrun-session-id`，值为自定义的会话标识符：

```
curl \ -H "Content-Type: application/json" \ -H "x-agentrun-session-id: session-abc-12345" \ http://<YOUR_AI_GW_ENDPOINT>/<base_path>/<route_path> \ -d '{ "sys.query": "还记得我刚才说的是什么吗？" }'
```

**

**说明**

会话亲和适用于需要维持多轮对话上下文的场景，如聊天机器人、对话式 AI 助手等。每个会话应使用唯一的`x-agentrun-session-id`值，建议使用 UUID 或业务会话 ID 生成。

### 响应示例

调用成功后，返回 JSON 格式响应体：

```
{ "FlowName": "agent-flow-KRbWd", "Name": "0758c9e9-808c-****-a3b2-18c86d3453e2", "SessionId": "", "Output": "{\"answer\":\"Hello! I'm Qwen, a large language model developed by Alibaba Group. How can I assist you?\"}", "ErrorCode": "", "ErrorMessage": "", "Status": "Succeeded", "RequestId": "becb807b-****-49cc-3604-20a823a8f599", "StartedTime": "2026-02-03T09:31:56.092Z", "StoppedTime": "2026-02-03T09:32:00.531Z", "Environment": { "Variables": [] } }
```

响应参数说明：

| **名称** | **类型** | **描述** |
| --- | --- | --- |
| FlowName | string | 流程名称 |
| Name | string | 执行名称，服务端生成 |
| SessionId | string | 会话 ID，会话亲和模式下返回 |
| Output | string | 流程执行输出 |
| ErrorCode | string | 错误码，流程执行失败时返回 |
| ErrorMessage | string | 错误信息，流程执行失败时返回 |
| Status | string | 流程执行状态 |
| RequestId | string | 请求 ID |
| StartedTime | string | 流程执行开始时间 |
| StoppedTime | string | 流程执行结束时间 |
| Environment | Environment | 流程执行时使用的环境变量配置信息 |

## 兼容协议说明

通过 AI 网关调用 Flow Agent 与  兼容，支持的协议和调用方式一致。每种协议均支持流式与非流式调用，将 Endpoint 地址替换为 AI 网关 URL 即可：`http://<YOUR_AI_GW_ENDPOINT>/<base_path>/<route_path>`。

以原生非流式调用为例，AgentRun 原生调用与 AI 网关调用的对比如下：

| **AgentRun 原生调用（非流式）** | **AI 网关调用（非流式）** |
| --- | --- |
| ```<br>curl https://<your-account-id>.agentrun-data.cn-hangzhou.aliyuncs.com/flows/<FlowName>/endpoints/<EndpointName>/invocations -XPOST \ -H "content-type: application/json" \ -d '{ "sys.query": "你好", "sys.conversation_id": "conversation_id", "sys.user": "user-abc" }'<br>``` | ```<br>curl http://<YOUR_AI_GW_ENDPOINT>/<base_path>/<route_path> -XPOST \ -H "content-type: application/json" \ -d '{ "sys.query": "你好", "sys.conversation_id": "conversation_id", "sys.user": "user-abc" }'<br>``` |

支持的协议与对应请求头如下：

| **协议** | **说明** | **典型用途** | **请求头（x-fnf-flow-agent-protocol）** |
| --- | --- | --- | --- |
|  | 与 Dify 工作流运行接口兼容 | 从 Dify 或自建系统以工作流方式调用 | `dify-workflow-compatible` |
|  | 与 Dify 对话流接口兼容 | 对话/聊天场景，支持会话与流式输出 | `dify-chatflow-compatible` |
|  | 与 OpenAI Chat Completions 兼容 | 使用 OpenAI SDK 或兼容客户端调用 | `openai-chat-completion-compatible` |
|  | AgentRun 原生入参格式 | 直接映射到 Flow 开始节点声明的字段 | 不需要 |

**

**说明**

- **协议指定头**：对于 Dify Workflow、Dify Chatflow、OpenAI 三种协议，必须设置`x-fnf-flow-agent-protocol`请求头，值为上表中对应的字符串。不指定时默认为原生协议。
- **流式输出**：原生协议没有内置流式控制标志，需通过设置请求头`x-fnf-param-stream: true`启用流式输出。

## 验证调用结果

完成配置和调用后，可通过以下方式验证结果：

1. 检查调用响应：返回`"Status": "Succeeded"`表示流程执行成功。
2. 在 AI 网关控制台查看调用日志，确认请求路由和响应状态。
3. 会话亲和模式下，连续发送多条请求并使用相同`x-agentrun-session-id`，确认上下文连续。

### 常见错误排查

| **错误现象** | **可能原因** | **排查方法** |
| --- | --- | --- |
| `404 Not Found` | 路由未发布或路径配置不匹配 | 确认路由状态为「已发布」，检查调用 URL 中的 Base Path 和路由 Path 是否与配置一致。 |
| `401 Unauthorized` | 鉴权配置错误或凭证无效 | 检查 API 鉴权配置是否正确，确认请求携带的认证凭证（如 API Key、Token）有效且未过期。 |
| `504 Gateway Timeout` | Flow Agent 执行超时 | 检查 Flow Agent 的执行耗时，确认是否因复杂逻辑或外部依赖导致超时。可在 AI 网关中调大超时时间配置。 |
