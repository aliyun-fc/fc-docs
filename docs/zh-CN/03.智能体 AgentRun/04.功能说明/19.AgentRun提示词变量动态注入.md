# AgentRun提示词变量动态注入

同一个 AgentRuntime 需要服务不同用户、业务线或场景时，为每个场景复制 Agent 会导致维护成本迅速增长。提示词变量动态注入通过将提示词写成模板、在每次调用时传入不同变量值，让同一个 AgentRuntime 在请求级别展现不同角色和行为，无需复制 Agent 配置。

## 前提条件

使用提示词变量动态注入功能前，确保满足以下条件：

- 已创建一个可调用的 AgentRuntime，并完成 Endpoint 发布。如果还没有，参考[快速创建Agent（无代码）](https://help.aliyun.com/zh/functioncompute/fc/quickly-create-agent-no-code)完成创建。
- AgentRuntime 的系统提示词中已包含`{变量名}`格式的占位符。

## 变量来源与优先级

提示词变量动态注入的核心做法是：把稳定的提示词写成模板，把会变化的部分作为变量在每次调用时传入。AgentRuntime 在收到请求后自动将占位符替换为实际值，生成最终的系统提示词。

例如，系统提示词模板可以写成：

```
你是{role}，擅长{expertise}。请用{tone}的语气回答用户问题。
```

调用时只需传入不同的变量值（如`role=企业知识库助手`），AgentRuntime 会自动将占位符替换为实际值。

AgentRuntime 按照以下顺序处理提示词变量：

```
提示词模板（包含 {变量名} 占位符） ↓ 默认变量（运行时配置，例如 PROMPT_VARIABLES 环境变量） ↓ 请求级变量（forwardedProps.system_prompt_vars，优先级更高） ↓ 展开后的系统提示词
```

默认变量负责兜底，确保即使调用方未传入变量，AgentRuntime 也能得到一条完整的提示词。请求级变量随每次 API 调用传入，覆盖默认变量的同名字段。

### 默认变量

通过 AgentRuntime 运行时配置的`PROMPT_VARIABLES`环境变量，为提示词占位符提供默认值。推荐使用 JSON 对象格式：

```
PROMPT='你是{role}，擅长{expertise}。请用{tone}的语气回答用户问题。' PROMPT_VARIABLES='{"role":"智能助手","expertise":"通用问答","tone":"清晰、礼貌"}'
```

`PROMPT_VARIABLES`也支持数组格式，适合从控制台表单配置转换：

```
[ {"variable_key": "role", "variable_value": "智能助手"}, {"variable_key": "expertise", "variable_value": "通用问答"}, {"variable_key": "tone", "variable_value": "清晰、礼貌"} ]
```

### 请求级变量

调用 AgentRuntime 时，通过请求体顶层的`forwardedProps`传入`system_prompt_vars`。它是一个 JSON 对象，键名对应提示词里的`{变量名}`。

```
{ "forwardedProps": { "system_prompt_vars": { "role": "企业知识库助手", "expertise": "检索和总结内部知识库", "tone": "简洁、专业" } } }
```

如果默认变量和请求级变量包含同名字段，请求级变量会覆盖默认值；没有被覆盖的字段继续使用默认值。

## 调用 AgentRuntime 注入变量

AgentRuntime 支持通过 OpenAI 兼容协议和 AG-UI 协议两种方式调用，两者均支持`forwardedProps.system_prompt_vars`传入请求级变量，变量合并规则一致。根据集成场景选择协议：

| **协议** | **适用场景** |
| --- | --- |
| OpenAI 兼容协议 | 已有 OpenAI SDK 集成，或希望复用 Chat Completions 接口的标准请求/响应结构 |
| AG-UI 协议 | 需要 AG-UI 事件流能力，或使用 AG-UI 客户端框架 |

### 通过 OpenAI 兼容协议调用

使用 OpenAI Chat Completions 协议调用 AgentRuntime 时，请求体直接携带`forwardedProps`：

```
curl "https://{account-id}.agentrun-data.{region}.aliyuncs.com/agent-runtimes/{agent-name}/endpoints/{endpoint-name}/invocations/openai/v1/chat/completions" \ -X POST \ -H "Content-Type: application/json" \ -H "x-agentrun-session-id: {your-session-id}" \ -d '{ "messages": [ {"role": "user", "content": "请介绍一下你的能力"} ], "stream": true, "forwardedProps": { "system_prompt_vars": { "role": "企业知识库助手", "expertise": "检索和总结内部知识库", "tone": "简洁、专业" } } }'
```

上述请求会将提示词模板中的占位符替换为实际值：

| **占位符** | **本次请求的值** |
| --- | --- |
| `{role}` | `企业知识库助手` |
| `{expertise}` | `检索和总结内部知识库` |
| `{tone}` | `简洁、专业` |

如果不传`forwardedProps.system_prompt_vars`，AgentRuntime 会使用默认变量展开提示词。

请求 URL 中的参数说明如下：

| **参数** | **说明** |
| --- | --- |
| `{account-id}` | 阿里云账号 ID |
| `{region}` | AgentRuntime 所在地域，例如`cn-hangzhou` |
| `{agent-name}` | AgentRuntime 名称 |
| `{endpoint-name}` | Endpoint 名称 |
| `{your-session-id}` | 会话 ID，用于多轮对话的上下文关联 |

### 通过 AG-UI 协议调用

AG-UI 协议同样支持通过`forwardedProps.system_prompt_vars`传入请求级变量。AG-UI 的响应为 SSE（Server-Sent Events）事件流，客户端需要按事件流方式处理返回数据：

```
curl "https://{account-id}.agentrun-data.{region}.aliyuncs.com/agent-runtimes/{agent-name}/endpoints/{endpoint-name}/invocations/ag-ui/agent" \ -X POST \ -H "Content-Type: application/json" \ -H "Accept: text/event-stream" \ -H "x-agentrun-session-id: {your-session-id}" \ -d '{ "threadId": "{thread-id}", "runId": "{run-id}", "messages": [ {"role": "user", "content": "请介绍一下你的能力"} ], "forwardedProps": { "system_prompt_vars": { "role": "企业知识库助手", "expertise": "检索和总结内部知识库", "tone": "简洁、专业" } } }'
```

与 OpenAI 兼容协议相比，AG-UI 协议的请求额外包含以下参数：

| **参数** | **说明** |
| --- | --- |
| `threadId` | 会话线程 ID |
| `runId` | 本次执行的唯一标识 |

### 验证变量注入结果

发送请求后，Agent 的回复内容应体现注入的角色和风格。以上述示例为例，Agent 应以"企业知识库助手"的身份、使用"简洁、专业"的语气回应。如果回复内容包含原始占位符文本（如`{role}`），说明变量未正确替换，排查方法见常见问题章节。

## 展开规则

| **规则** | **说明** |
| --- | --- |
| 占位符格式 | 使用`{变量名}`，例如`{role}` |
| 匹配方式 | 变量名必须完全一致，大小写敏感 |
| 覆盖顺序 | `forwardedProps.system_prompt_vars`覆盖默认变量中的同名字段 |
| 缺失变量 | 没有提供值的占位符会保留原样（不会报错） |
| 变量值类型 | 非字符串值会自动转为字符串后写入提示词 |

建议为所有占位符都配置默认值。这样即使调用方漏传变量，AgentRuntime 也能得到一条完整的提示词，避免占位符原样暴露给模型。

## 安全建议

- 不要将 API Key、AccessKey、手机号、身份证号、客户编号等敏感信息写入提示词变量。
- 示例代码、日志、截图或工单不得暴露完整的调用域名、鉴权头、账号 ID 或真实会话 ID。
- 如果变量值来自外部用户输入，应先按业务白名单或枚举值进行校验，再传递给 AgentRuntime。
- 对于角色定义、权限边界、合规规则等关键变量，优先由服务端生成，不要完全信任前端传入的值。

## 常见问题

**Q：**`**system_prompt_vars**`**应该放在哪里？**

放在请求体顶层的`forwardedProps`里：

```
{ "forwardedProps": { "system_prompt_vars": { "role": "企业知识库助手" } } }
```

不要将它放进`messages`、`metadata`或请求头中。

**Q：请求级变量会不会覆盖全部默认变量？**

不会。请求级变量只覆盖同名字段。例如，默认变量中包含`role`、`expertise`、`tone`三个字段，请求中只传入`tone`，最终提示词会使用默认的`role`和`expertise`，以及请求传入的`tone`。

**Q：能不能把用户输入直接作为变量值？**

可以，但需要先进行必要的业务校验。变量展开后会进入系统提示词，属于影响 Agent 行为的高优先级上下文。不要让未经校验的用户输入直接控制角色定义、权限边界、工具使用规则等关键字段。

**Q：为什么提示词没有按预期替换？**

按以下顺序排查：

1. 提示词模板里的占位符是否使用`{变量名}`格式（注意是花括号`{}`，不是双花括号）。
2. `system_prompt_vars`中的键名是否和占位符中的变量名完全一致（大小写敏感）。
3. `forwardedProps`是否位于请求体顶层（与`messages`同级），而非嵌套到其他字段里。
4. `PROMPT_VARIABLES`环境变量的值是否是合法的 JSON 格式。
5. 查看日志中是否出现变量解析失败或占位符缺失的提示信息。

## 相关链接

- **AgentRun 控制台**：[https://functionai.console.aliyun.com/](https://functionai.console.aliyun.com/)
- **AgentRun Python SDK**：[https://github.com/Serverless-Devs/agentrun-sdk-python](https://github.com/Serverless-Devs/agentrun-sdk-python)
- **Agent 集成与发布**：[https://help.aliyun.com/zh/document_detail/2998775.html](https://help.aliyun.com/zh/functioncompute/fc/agent-integration)
