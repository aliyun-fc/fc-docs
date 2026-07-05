# HTTP触发器概述

通过 HTTP 请求触发函数执行，适用于快速搭建 Web 服务等场景。使用前需了解：触发器与 HTTP/HTTPS的使用限制；同步/异步调用方式；认证鉴权与跨域（CORS）的配置方式。本文介绍上述内容及常见问题。

## 注意事项

- **匿名触发器的安全风险**：若 HTTP 触发器在配置中将**认证方式**选为**无需认证**，则不会验证身份，任何人均可通过 HTTP 请求调用函数，存在 URL 泄露风险。可在业务中校验请求头`Authorization`是否合法以自行鉴权。详见[为HTTP触发器配置签名认证](https://help.aliyun.com/zh/functioncompute/fc/user-guide/configure-signature-authentication-for-http-triggers)。
- **监管抽检**：根据国家网络安全监管要求，阿里云会对备案域名进行随机抽检，匿名 HTTP 域名可能被请求并产生调用记录。
- **APK 下载限制**：根据国家网络安全监管要求，自 2024 年 6 月 10 日起，新创建的 HTTP 触发器禁止通过公网地址下载 APK 文件（MIME 类型为`application/vnd.android.package-archive`），访问将返回 400。详见[如何确保HTTP触发器公网访问地址正常返回.apk文件](https://help.aliyun.com/zh/functioncompute/fc/how-to-ensure-that-the-public-network-access-address-of-the-http-trigger-returns-the-apk-file-normally)。
- **VIP 轮换**：函数计算为提升系统韧性与服务稳定性实施 VIP（虚拟 IP）轮换，HTTP 触发器提供的公网/内网访问地址对应的 VIP 会不定期轮换。直接硬编码 VIP 可能导致服务中断，建议通过自定义域名访问以保证业务稳定。因不当使用 VIP 导致的故障不在函数计算赔付范围内。
  
  可通过自定义域名搭配 CNAME 访问，详见[配置自定义域名](https://help.aliyun.com/zh/functioncompute/fc/configure-custom-domain-names)。

## 使用限制

### 触发器限制

- 每个版本或别名下最多创建一个 HTTP 类型触发器。详细信息，请参见[版本管理](https://help.aliyun.com/zh/functioncompute/fc/user-guide/manage-versions)和[别名管理](https://help.aliyun.com/zh/functioncompute/fc/user-guide/manage-aliases)。
- 内置域名仅用于测试，请勿用于线上对外服务，以免受内置域名稳定性影响。
  
  **
  
  **说明**
  
  对外提供网站类服务需使用已备案的自定义域名，将域名与函数绑定后对外提供服务。更多信息，请参见[配置自定义域名](https://help.aliyun.com/zh/functioncompute/fc/configure-custom-domain-names)。

### HTTP/HTTPS协议使用限制

**

**说明**

支持GET、POST、PUT、DELETE、HEAD、PATCH和OPTIONS方式触发函数，适用于简单的请求-响应场景。更多信息，请参见[配置HTTP触发器](https://help.aliyun.com/zh/functioncompute/fc/configure-an-http-trigger-for-a-function-and-invoke-the-function-by-using-http-requests)。

- HTTP Request限制
  
  - Request Headers不支持以x-fc-开头的自定义字段和以下自定义字段。
    
    - connection
    - keep-alive
  - 如果Request超过以下限制，会返回`400`状态码和`InvalidArgument`错误码。
    
    - Headers大小：Headers中的所有Key和Value的总大小不得超过8 KB。
    - Path大小：包括所有的Query Params，Path的总大小不得超过4 KB。
    - Body大小：同步调用请求的Body的总大小不得超过32 MB，关于异步调用请求的Body的大小，请以[函数运行资源限制](https://help.aliyun.com/zh/functioncompute/fc/product-overview/limits-of-usage#section-zxo-z1j-3w8)为准。
- HTTP Response限制
  
  - Response Headers不支持以x-fc-开头的自定义字段和以下自定义字段。
    
    - connection
    - content-length
    - date
    - keep-alive
    - server
    - upgrade
    - content-disposition:attachment
      
      **
      
      **说明**
      
      从安全角度考虑，使用函数计算默认的aliyuncs.com域名，服务端会在Response Headers中强制添加content-disposition: attachment字段，此字段会使得返回结果在浏览器中以附件的方式下载。如果要解除该限制，需设置自定义域名。更多信息，请参见[配置自定义域名](https://help.aliyun.com/zh/functioncompute/fc/configure-custom-domain-names)。
  - 如果Response超过以下限制，会返回`502`状态码和`BadResponse`错误码。
    
    - Headers大小：Headers中的所有Key和Value的总大小不得超过8 KB。

## 与API网关的对比与优势

HTTP触发器与API网关触发器均可应用于Web应用的创建。使用方式如下：

- HTTP触发器：您可以通过绑定自定义域名，为HTTP函数映射不同的HTTP访问路径。详细信息，请参见[配置自定义域名](https://help.aliyun.com/zh/functioncompute/fc/configure-custom-domain-names)。
- API网关触发器：您还可以使用API网关，后端服务类型选择函数计算，实现类似功能。详细信息，请参见[使用函数计算作为API后端服务](https://help.aliyun.com/zh/api-gateway/traditional-api-gateway/user-guide/function-compute#bebf3fe06fvfg)。

相较于API网关触发器，HTTP触发器有以下优势。

- 降低开发人员的学习成本和简化开发人员的调试过程，帮助开发人员快速使用函数计算搭建Web应用和API。
- 减少请求处理环节，HTTP触发器支持更高效的请求、响应格式，不需要编码或解码成JSON格式，性能更优。
- 支持选择熟悉的HTTP测试工具验证函数计算侧的功能和性能。
- 方便对接其他支持Webhook回调的服务，例如CDN回源、轻量消息队列（原 MNS）等。

## 调用方式

### 同步调用

同步调用指事件被函数处理后直接返回结果。HTTP触发器默认的函数调用方式为同步调用。更多信息，请参见[同步调用](https://help.aliyun.com/zh/functioncompute/fc/user-guide/synchronous-invocations)。

### 异步调用

异步调用指函数计算收到请求后，将请求持久化保存，然后立即返回响应，而不是等待请求执行完成后，再返回执行结果。

- [异步调用](https://help.aliyun.com/zh/functioncompute/fc/user-guide/asynchronous-invocation)：使用HTTP触发器调用函数时，您可以通过增加请求头`"X-Fc-Invocation-Type":"Async"`的方式实现请求级别的异步调用。
- [异步任务](https://help.aliyun.com/zh/functioncompute/fc/user-guide/asynchronous-task)：HTTP函数配置了异步任务后，您可以通过增加请求头`"X-Fc-Async-Task-Id":"g6u*****iyvhd3jk8s6bhj0hh"`完成异步任务调用Invocation ID的配置。

关于请求头的更多信息，请参见[调用函数](https://help.aliyun.com/zh/functioncompute/fc/developer-reference/api-fc-2023-03-30-invokefunction)。

异步调用成功后，函数计算会返回状态码`202`，表示请求接收成功。同时会通过请求头返回Request ID，格式如`"X-Fc-Request-Id": "80bf7****281713e1"`。

**

**说明**

如果函数计算返回的状态码是`202`以外的状态码，则表示调用失败。关于调用失败后错误原因，请参见[重试机制](https://help.aliyun.com/zh/functioncompute/fc/user-guide/error-handling-1-2)。

相关文档：

- 关于异步调用的更多信息，请参见[异步调用](https://help.aliyun.com/zh/functioncompute/fc/user-guide/asynchronous-invocation)。
- 关于异步任务的更多信息，请参见[异步任务](https://help.aliyun.com/zh/functioncompute/fc/user-guide/asynchronous-task)。

## 认证鉴权

函数计算支持对HTTP触发器配置认证鉴权。外部用户通过HTTP触发器访问函数时，必须经过函数计算的认证鉴权之后，才能访问到函数。HTTP触发器支持的鉴权方式如下：

- [为HTTP触发器配置签名认证](https://help.aliyun.com/zh/functioncompute/fc/user-guide/configure-signature-authentication-for-http-triggers)
- [为HTTP触发器配置Basic认证鉴权](https://help.aliyun.com/zh/functioncompute/fc/user-guide/configure-basic-authentication-for-an-http-trigger)
- [为HTTP触发器配置JWT认证鉴权](https://help.aliyun.com/zh/functioncompute/fc/user-guide/configure-jwt-authentication-for-an-http-trigger)
- [为HTTP触发器开启Bearer认证鉴权](https://help.aliyun.com/zh/functioncompute/fc/user-guide/enable-bearer-authentication-for-an-http-trigger)

## CORS请求处理

函数计算系统默认允许函数的调用请求跨域访问，同时也支持用户在函数代码中自定义函数对跨域（即CORS）请求的处理行为。

### **简单请求**

简单请求不会发送预检请求，您可以直接在函数代码中设置`Access-Control-Allow-*`开头的Header，完成简单的访问控制。对于简单请求，函数计算支持自定义的Headers包括：`Access-Control-Allow-Origin`、`Access-Control-Allow-Headers`、和`Access-Control-Max-Age`。

如果您没有自定义Headers，函数计算的Response Headers会默认设置为Request请求中相应的字段：

- `Access-Control-Allow-Origin`：Request请求的Origin Header。
- `Access-Control-Allow-Credentials`：默认取值为`true`。
- `Access-Control-Expose-Headers`：函数计算自定义的一些Header。

### 非简单请求

非简单请求在发送正式请求前会发送预检请求，即一次非简单请求包含一次OPTIONS方法的函数调用请求和一次实际的函数调用请求。正式请求的规则与上文的简单请求相同。如果您需要自定义预检请求的返回，则需要为HTTP触发器添加OPTIONS方法，然后在函数代码中处理OPTIONS请求，即设置`Access-Control-Allow-*`开头的Header以控制函数的跨域行为。

对于预检请求，函数计算支持用户自定义的Headers包括`Access-Control-Allow-Origin`、`Access-Control-Allow-Headers`、`Access-Control-Allow-Methods`和`Access-Control-Max-Age`。

以Node.js内置运行时为例，函数代码中处理预检请求的示例如下所示：

```
exports.handler = (event, context,callback) => { console.log('hello world'); const method = JSON.parse(event).requestContext.http.method; if (method === 'OPTIONS') { // 设置响应头以处理预检请求 const fcResponse = { 'statusCode': 204, 'headers': { 'Access-Control-Allow-Origin': 'http://www.fc.com', 'Access-Control-Allow-Methods': 'POST', 'Access-Control-Allow-Headers': 'Content-Type, Authorization', 'Access-Control-Max-Age':'3600' }, 'body': 'hello world' }; callback(null, fcResponse); } else { callback(null, { 'statusCode': 500, 'body': 'hello world' }); } };
```

### **API Configured CORS**

API Configured CORS 当前为邀测功能。如需开通，请[联系我们](https://help.aliyun.com/zh/functioncompute/fc/support/contact-us-1)并提供阿里云账号 ID（UID）。

#### **功能说明**

API Configured CORS 是函数计算（FC）在网关层提供的能力。可在 HTTP 触发器或自定义域名上直接配置 CORS 策略，无需在函数代码中编写跨域逻辑。

##### **核心优势**

- **代码更简单**：跨域逻辑与业务解耦，只需关注业务实现。
- **成本更低**：OPTIONS 预检由网关直接响应，不触发函数实例，节省执行时长费用。
- **统一管理**：在触发器或域名维度配置策略，便于多服务治理。
- **响应更快**：预检结果由网关直接返回，时延更低。

#### **适用范围**

- **API 版本**：仅适用于 FC 3.0 函数（API 版本：2023-03-30）。
- **访问方式**：HTTP 触发器（含内置测试域名）或已绑定的自定义域名。

#### **配置方式**

通过接口[更新触发器](https://help.aliyun.com/zh/functioncompute/fc/developer-reference/api-fc-2023-03-30-updatetrigger)或[更新自定义域名](https://help.aliyun.com/zh/functioncompute/fc/developer-reference/api-fc-2023-03-30-updatecustomdomain)进行配置。

##### **CORS 配置参数**

| **参数名称** | **类型** | **说明** | **默认值** | **限制/约束** |
| --- | --- | --- | --- | --- |
| allowOrigins | Array | 允许访问资源的来源列表（Origin）。 | - | 最多 100 个，单个长度不超过 256 字符。支持`*`或`https://*`。 |
| allowMethods | Array | 允许的 HTTP 方法列表。 | 触发器 methods | 不支持手动配置`OPTIONS`（由网关自动处理）。 |
| allowHeaders | Array | 允许浏览器发送的自定义请求头。 | - | 最多 50 个。支持使用`*`。 |
| exposeHeaders | Array | 允许浏览器获取的响应头字段。 | 系统默认值 | 最多 50 个。 |
| allowCredentials | Boolean | 是否允许跨域请求携带凭证（如 Cookie）。 | false | 为`true`时，`allowOrigins`不能配置为`*`。 |
| maxAge | Integer | 预检请求（OPTIONS）结果的缓存时长（秒）。 | 3600 | 取值范围：0 ~ 86400。 |

**allowOrigins取值**：

- 通配符`*`：允许所有来源（仅当`allowCredentials`为`false`时）。
- 通配符`https://*`：允许所有以`https://`开头的来源。
- 特定域名：如`https://example.com`。
- 多个域名：数组形式，如`["https://example.com", "https://app.example.com"]`。
- 不支持子域名通配符（如`https://*.example.com`）。

**allowMethods取值**：

- 标准 HTTP 方法：`GET`、`POST`、`PUT`、`DELETE`、`PATCH`、`HEAD`。
- 通配符`*`：表示允许所有 HTTP 方法。
- **不支持**`OPTIONS`：OPTIONS 方法由系统自动处理，用于预检请求。

#### **请求处理逻辑**

配置 API Configured CORS 后，网关按请求类型处理：

##### **1. 预检请求（OPTIONS）**

浏览器发起非简单请求的预检时，网关校验`Origin`、`Access-Control-Request-Method`、`Access-Control-Request-Headers`：

- **校验通过**：返回`204 No Content`并注入配置的 CORS 响应头，不触发函数。
- **校验失败**：
  
  - Origin 匹配但其他头不匹配：网关设置基础 CORS Header。
  - Origin 不匹配：不设置 CORS Header。
  - 请求会继续转发到函数实例。

##### **2. 简单请求（GET/POST/HEAD 等）**

网关仅校验`Origin`：

- **校验通过**：在响应中注入`Access-Control-Allow-Origin`等 Header，请求转发到函数执行。
- **校验失败**：不注入 CORS Header，请求仍转发到函数执行。

#### **兼容性与优先级**

同一路径可能同时存在多种 CORS 处理方式，优先级从高到低：

1. **API Configured CORS**：一旦配置，网关优先按此逻辑处理。
2. **默认 CORS**：未开启 API Configured 时，使用内置默认跨域回显。
3. **函数内 CORS**：函数返回的 Header 会与上述结果合并（追加），保证兼容。

##### **方案对比**

| **特性** | **API Configured CORS（推荐）** | **默认 CORS** | **用户自定义 CORS（代码）** |
| --- | --- | --- | --- |
| 预检请求是否计费 | 不计费（网关拦截） | 可能计费 | 计费（触发函数） |
| 代码入侵性 | 无 | 无 | 高 |
| 适用 API 版本 | 仅 FC 3.0 | 所有版本 | 所有版本 |
| 配置复杂度 | 低（一次性配置） | 无需配置 | 高（需处理 OPTIONS 方法） |

#### **常见问题 (FAQ)**

##### **Q1：为什么我配置了 allowMethods 包含 OPTIONS，但 API 调用报错？**

A：根据设计，`OPTIONS`方法由函数计算网关自动管理。您无需在`corsConfig`的`allowMethods`中手动添加`OPTIONS`，系统会自动处理所有预检请求。

##### **Q2：配置成功后，为什么我的 OPTIONS 请求依然返回 200 而不是 240？**

A：请确认您的账号是否已由值班同学开启“邀测权限”。若未完全激活拦截插件，网关会降级到“默认 CORS”逻辑（返回 200 并透传至函数）。

##### **Q3：allowOrigins 可以配置通配符子域名（如**`***.example.com**`**）吗？**

A：目前不支持子域名模糊匹配。建议在`allowOrigins`数组中枚举所有二级域名，或使用`https://*`进行大范围匹配。

##### **Q4：如果我的函数代码里也写了 CORS Header，会发生冲突吗？**

A：不会冲突。网关生成的 Header 与函数返回的 Header 会合并输出。如果存在重复，浏览器通常会以第一个或符合规范的值为准，但这有助于确保旧有业务在平滑迁移时不中断。

## **常见问题**

**在哪里可以设置监听端口？**

在创建函数时，选择创建**Web 函数**的方式创建函数时，才需要设置监听端口。

**函数调用时间太长，要怎么处理？**

- 函数使用频率较低，在首次发起调用时需要等待实例冷启动。
  
  具体原因可参见[为什么使用频率较低的函数调用时间比较长？](https://help.aliyun.com/zh/functioncompute/fc/why-infrequently-used-functions-take-a-longer-period-of-time-to-invoke-1)。如果您希望消除冷启动延时的影响，请参见[如何让实例一直存活不销毁，消除冷启动延时的影响？](https://help.aliyun.com/zh/functioncompute/fc/how-to-keep-instances-alive-to-eliminate-the-impact-of-cold-starts-1)。
- 如果函数调用偶然出现超时现象，您可以调整执行超时时间，并通过日志查找超时原因，具体解决方案可以参见[函数执行超时，报错Function time out after怎么办？](https://help.aliyun.com/zh/functioncompute/fc/function-time-out-after)。
- 如果您的函数请求量很大，建议设置实例并发度减少执行时长，具体请参见[设置实例并发度](https://help.aliyun.com/zh/functioncompute/user-guide/configure-instance-concurrency)。

**函数出现499错误，客户端主动取消请求要如何处理？**

- 出现客户端499错误后函数实例会重启，您可以通过配置健康检查避免实例重启，具体原因及操作请参见[为什么函数出现客户端499错误后函数实例会重启？](https://help.aliyun.com/zh/functioncompute/fc/why-does-a-function-instance-restart-after-a-client-499)。
- 如果客户端调用出现超时情况，您可以将耗时的逻辑放在新的函数中，使用函数的异步调用功能调用新的函数，或者在客户端调用时使用异步调用。

**函数处于运行中，如何更新函数配置？**

- 函数执行完成后才会更新函数配置。更新函数配置后，已经在执行中的请求仍然使用原来的配置运行直到执行结束。新发起的调用请求将使用新的函数配置。
- 删除当前函数，创建新的函数重新配置。
