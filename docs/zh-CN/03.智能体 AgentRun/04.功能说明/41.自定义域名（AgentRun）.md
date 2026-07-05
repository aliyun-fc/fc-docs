# 自定义域名（AgentRun）

如需通过自有域名访问 AgentRun 上部署的 Agent、LLM 代理、工具或沙箱实例，可以使用自定义域名功能将品牌域名（如 api.example.com）绑定到对应服务，替代默认的平台地址。AgentRun 支持标准域名和沙箱域名两种类型，分别适用于不同的资源绑定场景。

| **域名类型** | **适用场景** |
| --- | --- |
| **标准域名** | 绑定 Agent、LLM、工具等资源，通过路由规则将不同路径映射到不同服务 |
| **Sandbox 域名** | 绑定沙箱实例，支持泛域名和单域名两种模式 |

## 准备工作

配置自定义域名前，需要完成以下准备工作：

- **域名准备**：已拥有一个经过 ICP 备案的域名（中国站要求）。
- **RAM 权限**：账号已被授予 AgentRun、OSS、CDN、SSL 证书服务（yundun-cert）相关的写权限。具体权限配置参见[授权RAM用户使用 AgentRun](https://help.aliyun.com/zh/functioncompute/fc/authorize-ram-users-to-use-agentrun)。
- **DNS 服务**：能够在域名的 DNS 服务商处添加 CNAME 记录。
- **SSL 证书**（如需 HTTPS）：已在阿里云证书服务申请证书，或已准备好 PEM 格式的证书文件和 RSA 私钥文件。

## 域名类型说明

### 标准域名

**标准域名**用于绑定 Agent、LLM 代理、工具等资源。一个标准域名支持配置多条路由规则，将不同的 URL 路径映射到不同的后端服务。例如，将`api.example.com/agent/*`路由到某个 Agent 实例，将`api.example.com/llm/*`路由到 LLM 代理服务。

### 沙箱域名

**Sandbox 域名**专门用于绑定沙箱实例，支持以下两种模式：

| **模式** | **域名格式** | **说明** |
| --- | --- | --- |
| **泛域名模式** | `*.sandbox.example.com` | 每个实例通过独立子域名访问，适合需要域名级别隔离的场景 |
| **单域名模式** | `sandbox.example.com` | 所有实例共用一个域名入口，通过 Header 或 Query 参数指定目标实例和端口，适合需要统一入口的场景 |

## 创建标准域名

1. 登录[AgentRun 控制台](https://functionai.console.aliyun.com/)。
2. 从左侧导航栏选择**自定义域名**。
3. 单击**添加域名**。
4. **域名类型**选择**标准域名**。
5. **域名**输入框输入域名，例如`api.example.com`。
  
  **
  
  **说明**
  
  标准域名不能以`*.`开头。
6. （可选）**描述**填写域名的用途描述。
7. （可选）配置 HTTPS。具体操作参见[配置 HTTPS](#h2-https-01)。
8. 单击**保存修改**完成创建。
9. 根据页面提示的**域名CNAME配置**信息，在 DNS 服务商处添加 CNAME 记录，将域名指向系统提供的网关地址。
  
  **
  
  **说明**
  
  域名解析生效通常需要 10 分钟到 24 小时。如果是阿里云托管的域名，可以直接进入**阿里云DNS管理**完成配置。
10. 验证域名生效：**自定义域名**列表，单击目标域名的**详情**，确认 DNS 状态显示为正常。

## 创建沙箱域名

1. 登录[AgentRun 控制台](https://functionai.console.aliyun.com/)。
2. 从左侧导航栏选择**自定义域名**。
3. 单击**添加域名**。
4. **域名类型**选择**Sandbox 域名**。
5. 选择**Sandbox 域名类型**：
  
  - **泛域名模式**：输入以`*.`开头的域名，例如`*.sandbox.agentrun.cn`。支持通过子域名访问不同的 Sandbox 实例。
  - **单域名模式**：输入具体的域名，例如`sandbox.example.com`。通过 Header 参数指定 Sandbox 实例和端口。
6. （可选）配置 HTTPS 证书。
7. 单击**保存修改**完成创建。
8. 在 DNS 服务商处添加 CNAME 记录，将域名指向系统提供的网关地址。
9. 验证域名生效：**自定义域名**列表，单击目标域名的**详情**，确认 DNS 状态显示为正常。

## 配置 HTTPS

创建或编辑域名时，可以配置 SSL 证书以启用 HTTPS 访问。

1. 在域名创建或编辑页面，找到**HTTPS配置**区域。
2. 选择证书配置方式：
  
  | **方式** | **说明** |
  | --- | --- |
  | 手动证书 | 手动填写证书名称、PEM 格式证书内容和 RSA 私钥内容 |
  | 阿里云证书 | 从阿里云证书服务中选择已有证书 |
3. 单击**保存HTTPS配置**。
4. 保存后，在域名详情页确认 SSL 证书状态为正常，并通过浏览器访问`https://{域名}`确认无证书警告。

**

**重要**

未配置 SSL 证书的域名仅支持 HTTP 访问，存在数据传输安全风险。建议配置 SSL 证书以启用 HTTPS 加密传输。

## 绑定资源

### 为标准域名配置路由

标准域名通过路由规则将不同的请求路径映射到不同的后端资源。

1. 在域名详情页面，选择**路由配置**。
2. 单击**新增路由**。
3. 配置路由参数：
  
  | **参数** | **说明** |
  | --- | --- |
  | **路由路径** | 请求路径，必须以`/`开头。例如`/`、`/*`、`/agent/*` |
  | **请求方法** | 支持的 HTTP 方法，可多选 |
  | **目标类型** | 选择要绑定的资源类型（目前仅支持Agent） |
  | **目标服务** | 选择具体的资源实例 |
  | **选择Endpoint** | 选择资源的 Endpoint |
4. 单击**保存修改**。

也可以在资源详情页面通过**绑定自定义域名**快速为资源绑定域名。绑定时可以选择已有域名，也可以新建域名。

### 沙箱域名的资源绑定

沙箱域名创建后即可直接用于访问 Sandbox 实例，无需额外配置路由。访问时通过子域名（泛域名模式）或 Header/Query 参数（单域名模式）指定目标实例。

## 通过域名访问

### 通过标准域名访问

标准域名配置路由后，可以通过域名 + 路由路径访问对应的后端服务。例如：

```
https://api.example.com/agent/chat https://api.example.com/llm/v1/chat/completions https://api.example.com/tools/search
```

请求会根据路由规则转发到对应的 Agent、LLM 代理或工具服务。

### 通过沙箱域名访问

#### 泛域名模式

泛域名模式下，通过子域名中的端口号和实例 ID 指定访问目标。

访问地址格式：

- 指定端口：`{port}-{sandboxId}.sandbox.example.com`
- 默认端口：`{sandboxId}.sandbox.example.com`

示例：

- 访问 Sandbox 实例`XXXXXXXX`的`8080`端口，地址为`8080-XXXXXXXX.sandbox.example.com`。
- 访问 Sandbox 实例`XXXXXXXX`的默认端口，地址为`XXXXXXXX.sandbox.example.com`。

#### 单域名模式

单域名模式下，通过 Header 参数或 Query 参数指定要访问的 Sandbox 实例和端口。

**方式一：通过 Header 传递参数（推荐）**

必需的 Header 参数：

| **Header** | **说明** |
| --- | --- |
| `X-Sandbox-ID` | Sandbox 实例的唯一标识符 |
| `X-Sandbox-Port` | Sandbox 实例的端口号 |

**

**说明**

两个 Header 参数都是必需的，缺少任何一个都会导致请求失败。

cURL 请求示例：

```
curl -H "X-Sandbox-ID: your-sandbox-id" \ -H "X-Sandbox-Port: 8080" \ https://sandbox.example.com/your-path
```

**方式二：通过 Query 参数传递**

Query 参数格式：`?sandboxPort=8080&sandboxId=sb-prod-001`

示例：

```
https://sandbox.example.com/your-path?sandbox_id=your-sandbox-id&sandbox_port=8080
```

**

**说明**

Header 参数优先级高于 Query 参数。如果同时提供两种参数，系统将优先使用 Header 中的值。

## 管理域名

### 查看域名详情

**自定义域名**列表，单击目标域名的**详情**可查看域名的基本信息、CNAME 地址、DNS 状态、SSL 证书状态和绑定资源。

### 编辑域名

单击目标域名的**编辑**可修改域名的 HTTPS 配置和描述。

### 删除域名

单击目标域名的**删除**，确认后域名及其所有相关配置将被永久删除，无法恢复。

**

**警告**

删除域名前，确保没有业务流量指向该域名。

## 相关 API

通过 API 也可以管理自定义域名。AgentRun 提供以下 API：

| **API** | **说明** |
| --- | --- |
| CreateCustomDomain | [创建自定义域名](https://help.aliyun.com/zh/functioncompute/fc/developer-reference/api-agentrun-2025-09-10-createcustomdomain) |
| ListCustomDomains | [列出自定义域名](https://help.aliyun.com/zh/functioncompute/fc/developer-reference/api-agentrun-2025-09-10-listcustomdomains) |
| GetCustomDomain | [获取自定义域名](https://help.aliyun.com/zh/functioncompute/fc/developer-reference/api-agentrun-2025-09-10-getcustomdomain) |
| UpdateCustomDomain | [更新自定义域名](https://help.aliyun.com/zh/functioncompute/fc/developer-reference/api-agentrun-2025-09-10-updatecustomdomain) |
| DeleteCustomDomain | [删除自定义域名](https://help.aliyun.com/zh/functioncompute/fc/developer-reference/api-agentrun-2025-09-10-deletecustomdomain) |

## 相关文档

- [什么是AgentRun](https://help.aliyun.com/zh/functioncompute/fc/what-is-agentrun)
- [授权RAM用户使用 AgentRun](https://help.aliyun.com/zh/functioncompute/fc/authorize-ram-users-to-use-agentrun)
- [通过PrivateLink内网访问AgentRun资源](https://help.aliyun.com/zh/functioncompute/fc/access-agenrun-resources-through-privatelink-intranet)
