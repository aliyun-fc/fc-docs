# MCP Tool Hook

当智能体调用 MCP 工具时，工具返回的原始数据可能包含敏感信息，或需要格式化、审计标记等后处理。MCP Tool Hook 在 MCP 客户端和服务端之间插入代理层，在工具调用前后执行自定义逻辑，无需修改原始 MCP 服务代码。

## 工作原理

MCP Tool Hook 基于 AgentRun MCP 代理层运行。代理层位于 MCP 客户端（智能体）和 MCP 服务端之间，作为透明中间层转发所有 MCP 协议请求。启用代理后，工具调用请求不再直接到达 MCP 服务，而是经过代理层中转。代理层在执行`tools/list`和`tools/call`操作的前后，触发已配置的 Hook 事件，将请求或响应转发至外部 Hook 服务（HTTP Webhook）进行处理。

**

**说明**

MCP 协议标准本身不定义 Hook 或中间件机制。MCP Tool Hook 是 AgentRun 在协议层之上的扩展能力，对 MCP 服务端完全透明。

以 POST_CALL_TOOL 事件为例，数据流转过程如下：

1. 智能体发起工具调用请求。
2. AgentRun MCP 代理层接收请求，调用 MCP 服务执行工具操作。
3. MCP 服务返回原始结果。
4. 代理层根据 Hook 配置，将结果通过 HTTP POST 转发至 Hook 服务。
5. Hook 服务对结果进行处理（如脱敏、审计标记），返回修改后的结果。
6. 代理层将最终结果返回给智能体。

其他事件的流转方式类似：PRE_CALL_TOOL 在工具调用前触发，可修改请求参数或拦截调用；PRE_LIST_TOOLS 和 POST_LIST_TOOLS 分别在获取工具列表前后触发，可对工具列表进行预处理或过滤修改。

### Hook 事件类型

支持以下 Hook 事件：

| 事件类型 | 触发时机 | 说明 |
| --- | --- | --- |
| PRE_CALL_TOOL | 工具调用之前 | MCP 服务执行工具调用前触发。Hook 服务接收请求参数，可修改参数或拦截调用。 |
| POST_CALL_TOOL | 工具调用完成后 | MCP 服务返回工具调用结果后触发。Hook 服务接收原始结果，可修改后返回。 |
| PRE_LIST_TOOLS | 获取工具列表之前 | MCP 服务执行`tools/list`之前触发。Hook 服务可对请求进行预处理。 |
| POST_LIST_TOOLS | 获取工具列表之后 | MCP 服务返回工具列表后触发。Hook 服务可对工具列表进行过滤或修改。 |

### 适用场景

- **数据脱敏**：对工具返回结果中的手机号、邮箱、地址等敏感信息进行掩码处理。
- **审计标记**：在工具调用结果中注入请求 ID、时间戳等审计标识，便于追踪和审计。
- **结果增强**：对工具返回的原始数据进行格式化、补充或过滤。
- **访问控制**：在工具调用前后添加权限校验逻辑，限制特定工具的使用范围。

## 部署模式

AgentRun 支持两种 MCP Tool Hook 部署模式：

| 部署模式 | 架构 | 适用场景 |
| --- | --- | --- |
| mcp_remote | 远程 MCP + 代理 + Hook。MCP 服务和 Hook 服务分别独立部署为 HTTP 服务。 | MCP 服务已独立部署。 |
| mcp_code | 代码打包 MCP + 代理 + Hook。MCP 服务代码直接打包到 AgentRun 运行时。 | 希望简化部署流程，将 MCP 服务代码直接打包到运行时。 |

两种模式使用相同的 Hook 配置方式，区别在于 MCP 服务的部署和引用方式。

## 准备工作

- 已开通 AgentRun 服务。可通过[AgentRun 控制台](https://functionai.console.aliyun.com)确认。
- 已开通函数计算（FC）服务，用于部署 MCP 服务和 Hook 服务。
- 已安装 Golang 1.23 及以上开发环境。
- 已获取阿里云账号的 UID、AccessKey ID 和 AccessKey Secret。获取方式请参见[获取 AccessKey](https://help.aliyun.com/zh/ram/user-guide/create-an-accesskey-pair)。
- 已准备 MCP 服务代码和 Hook 服务代码。完整示例可从[start-agentrun](https://github.com/devsapp/start-agentrun)仓库获取：
  
  ```
  git clone https://github.com/devsapp/start-agentrun.git cd start-agentrun
  ```
  
  项目中包含两个示例目录：`mcp_remote`（远程 MCP 模式）和`mcp_code`（代码打包模式），分别对应两种部署模式的完整示例。以下操作步骤中的相对路径均基于项目根目录`start-agentrun/`。

部署函数计算服务时，默认使用中国地域（如`cn-hangzhou`）。请根据实际业务需求选择合适的地域。

## 配置 MCP Tool Hook（mcp_remote 模式）

以下以订单查询服务（`orderdesk`）和数据脱敏 Hook 服务（`userhook`）为例，演示 mcp_remote 模式的完整配置流程。

### 步骤一：配置环境变量

进入`mcp_remote`示例目录，配置阿里云凭证信息。

1. 进入示例目录：
  
  ```
  cd mcp_remote
  ```
2. 复制环境变量模板并填写凭证信息：
  
  ```
  cp .env.example .env
  ```
  
  编辑`.env`文件，填入您的阿里云账号信息。其中`AGENTRUN_DATA_ENDPOINT`需将`<ALIBABA_CLOUD_UID>`替换为实际 UID：
  
  ```
  ALIBABA_CLOUD_UID=<您的阿里云账号 UID> ALIBABA_CLOUD_ACCESS_KEY_ID=<您的 AccessKey ID> ALIBABA_CLOUD_ACCESS_KEY_SECRET=<您的 AccessKey Secret>
  ```

### 步骤二：一键部署

运行示例程序，自动完成 MCP 服务（`orderdesk`）和 Hook 服务（`userhook`）的部署，以及 AgentRun 上的工具创建、代理启用和 Hook 配置。

```
go run .
```

程序将自动执行以下操作：

1. 将 MCP 服务和 Hook 服务部署到函数计算。
2. 在 AgentRun 中创建 MCP 工具，并启用代理。
3. 配置 Hook（`POST_CALL_TOOL`事件），将 Hook 服务地址关联到工具配置中。
4. 发起测试调用并输出验证结果。

**

**说明**

示例程序在验证完成后不会自动清理所部署的资源。保留的函数计算函数不产生额外费用。如需清理，请手动删除函数计算中对应的函数和 AgentRun 中对应的 MCP 工具。

### 步骤三：验证结果

程序执行完成后，查看输出的验证结果，确认 Hook 已生效。

未启用 Hook 时返回的原始订单数据（以查询 ORDER-1001 为例）：

```
{ "order_id": "ORDER-1001", "customer_name": "张三", "phone": "138****5678", "email": "zhangsan@example.com", "shipping_address": "浙江省杭州市西湖区文三路 100 号", "status": "PAID", "amount": 259.8, "items": [ {"sku": "SKU-AX100", "name": "人体工学鼠标", "quantity": 1, "price": 129.9}, {"sku": "SKU-KB200", "name": "机械键盘键帽", "quantity": 1, "price": 129.9} ] }
```

启用 Hook 后，返回的脱敏数据：

```
{ "order_id": "ORDER-1001", "customer_name": "张*", "phone": "138****5678", "email": "zh***@example.com", "shipping_address": "浙江省杭州市****", "status": "PAID", "amount": 259.8, "items": [ {"sku": "SKU-AX100", "name": "人体工学鼠标", "quantity": 1, "price": 129.9}, {"sku": "SKU-KB200", "name": "机械键盘键帽", "quantity": 1, "price": 129.9} ], "audit_id": "audit_xxxxxxxxxxxxxxxx" }
```

### 配置参数参考

示例程序自动生成的`mcpProxyConfiguration`配置如下：

```
{ "proxyEnabled": true, "hooks": [ { "event": "POST_CALL_TOOL", "endpoint": "<Hook 服务的 Endpoint 地址>" } ] }
```

配置参数说明：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| proxyEnabled | Boolean | 是 | 是否启用 MCP 代理。设置为`true`时，工具调用通过代理层中转。 |
| hooks | Array | 否 | Hook 配置列表。每个元素包含事件类型和 Hook 服务地址。 |
| hooks[].event | String | 是 | Hook 事件类型。支持`PRE_CALL_TOOL`、`POST_CALL_TOOL`、`PRE_LIST_TOOLS`、`POST_LIST_TOOLS`。 |
| hooks[].endpoint | String | 是 | Hook 服务的 HTTP 地址。代理层在事件触发时，向该地址发送 HTTP POST 请求。 |
| hooks[].enabled | Boolean | 否 | 是否启用该 Hook，默认`true`。 |
| hooks[].timeout | Integer | 否 | Hook 请求超时时间（秒）。 |
| hooks[].description | String | 否 | Hook 描述信息。 |
| hooks[].headers | Object | 否 | 自定义请求头，键值对格式。 |

## 配置 MCP Tool Hook（mcp_code 模式）

`mcp_code`模式将 MCP 服务代码打包到 AgentRun 运行时中，无需单独部署 MCP 服务，简化部署流程。以下同样以`orderdesk`（MCP 服务）和`userhook`（Hook 服务）为例。

### 步骤一：配置环境变量

进入`mcp_code`示例目录，配置阿里云凭证信息。

1. 进入示例目录：
  
  ```
  cd mcp_code
  ```
2. 复制环境变量模板并填写凭证信息：
  
  ```
  cp .env.example .env
  ```
  
  编辑`.env`文件，填入您的阿里云账号信息（格式与 mcp_remote 模式相同）。

### 步骤二：一键部署

运行示例程序，自动完成 MCP 服务代码打包、Hook 服务部署，以及 AgentRun 上的工具创建、代理启用和 Hook 配置。

```
go run .
```

与 mcp_remote 模式不同，mcp_code 模式下 MCP 服务代码直接打包到 AgentRun 运行时，无需部署独立的 MCP 服务。

### 步骤三：验证结果

验证方式与 mcp_remote 模式相同，参考[步骤三：验证结果](#sec-step-remote-3)。

## 示例：订单数据脱敏 Hook 服务

示例程序中的 Hook 服务（`userhook`）使用 Go 实现，处理`POST_CALL_TOOL`事件。以下是核心脱敏函数，完整代码参见[start-agentrun](https://github.com/devsapp/start-agentrun)仓库。

```
// maskPhone 对手机号进行掩码处理，保留前 3 位和后 4 位。 func maskPhone(phone string) string { runes := []rune(strings.TrimSpace(phone)) if len(runes) <= 7 { return "***" } return string(runes[:3]) + "****" + string(runes[len(runes)-4:]) } // maskEmail 对邮箱进行掩码处理，保留前 2 位用户名。 func maskEmail(email string) string { parts := strings.SplitN(email, "@", 2) if len(parts) != 2 { return "***" } name := []rune(parts[0]) keep := 1 if len(name) > 2 { keep = 2 } return string(name[:keep]) + "***@" + parts[1] } // maskAddress 对地址进行掩码处理，保留前 6 个字符。 func maskAddress(address string) string { runes := []rune(strings.TrimSpace(address)) if len(runes) <= 6 { return "***" } return string(runes[:6]) + "****" } // maskName 对姓名进行掩码处理，保留姓氏。 func maskName(name string) string { runes := []rune(strings.TrimSpace(name)) if len(runes) == 0 { return "***" } return string(runes[:1]) + "*" } // auditIDFromBytes 根据原始响应生成审计编号（SHA256 哈希前缀）。 func auditIDFromBytes(body []byte) string { sum := sha256.Sum256(body) return "audit_" + hex.EncodeToString(sum[:])[:16] }
```

Hook 服务接收代理层通过 HTTP POST 转发的事件负载，负载中的请求和响应 Body 采用 Base64 编码。Hook 服务解码后对敏感字段进行掩码处理，注入审计标识，再将修改后的结果 Base64 编码返回。

## 错误处理

Hook 服务异常时，代理层将中断本次 MCP 请求：

| 异常场景 | 代理层行为 |
| --- | --- |
| Hook 服务超时 | MCP 请求失败，向调用方返回错误。 |
| Hook 服务不可用（连接失败） | MCP 请求失败，向调用方返回错误。 |
| Hook 服务返回非 200 状态码 | MCP 请求失败，向调用方返回错误。 |

**

**重要**

Hook 服务异常（超时、不可用或返回非 200 状态码）时，代理层不会降级处理，而是直接将本次 MCP请求标记为失败。PRE_CALL_TOOL 阶段失败时，工具不会被执行。POST_CALL_TOOL 阶段失败时，工具的原始结果不会返回给调用方。请确保 Hook 服务的高可用性。

## 常见问题

### Hook 服务配置后不生效

按以下步骤排查：

1. 确认`proxyEnabled`已设置为`true`。
2. 确认`hooks[].endpoint`地址正确且 Hook 服务正常运行。
3. 确认`hooks[].event`值为支持的事件类型（`PRE_CALL_TOOL`、`POST_CALL_TOOL`、`PRE_LIST_TOOLS`或`POST_LIST_TOOLS`，注意大小写）。
4. 检查 Hook 服务日志，确认是否收到代理层的 HTTP POST 请求。

### 如何选择部署模式

| 条件 | 推荐模式 |
| --- | --- |
| MCP 服务已独立部署 | mcp_remote |
| 希望简化部署，将 MCP 服务代码打包到运行时 | mcp_code |
