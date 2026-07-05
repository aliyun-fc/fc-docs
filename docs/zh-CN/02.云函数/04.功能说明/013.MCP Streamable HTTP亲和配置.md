# MCP Streamable HTTP亲和配置

在MCP（Model Context Protocol）Streamable HTTP场景中，需要确保同一MCP会话的请求路由到同一个函数实例以保持上下文一致性。MCP Streamable HTTP亲和功能基于MCP 2025-03-26和2025-06-18版本协议，系统解析HTTP响应头中的`Mcp-Session-Id`字段建立会话绑定，将携带相同`Mcp-Session-Id`的请求路由到初始化会话的实例，适用于使用MCP Streamable HTTP传输的场景。

## 核心配置

在函数配置页面的**高级配置 > 隔离性、亲和性**中，开启**会话亲和**开关，选择**MCP Streamable HTTP 亲和**，配置**单实例并发 Session 数**，确保HTTP触发器支持GET、POST和DELETE方法，点击**部署**即可启用。

客户端通过POST请求初始化Session，从响应头获取`Mcp-Session-Id`，后续请求携带此ID即可路由到同一实例。

## 适用范围

- **通用限制**：请先阅读[会话亲和通用限制及原理说明](https://help.aliyun.com/zh/functioncompute/fc/user-guide/cookie-affinity-feature)
- **协议版本要求：**支持 MCP 协议版本`2025-03-26`和`2025-06-18`。客户端与函数必须遵循对应版本的 Transport 层规范。
- **兼容性说明：**若函数启用了 MCP Streamable HTTP 亲和，则 禁止使用 MCP HTTP with SSE 调用，因会话管理机制不兼容，导致调用失败。
- **访问方式限制：**仅支持通过 HTTP 触发器 或 自定义域名 访问。
- **HTTP 触发器配置要求：**必须至少支持`GET`、`POST`和`DELETE`方法。
  
  DELETE 方法必要性：
  客户端可通过`DELETE`请求主动结束会话。函数计算将回收该 Session 的资源（包括实例并发配额）。若未启用 DELETE 方法，系统将拒绝请求，导致 Session 无法正常释放。
- **请求限制：**
  
  - 单实例可同时处理多个Session（默认20个，最大200个），当单实例下绑定的Session数达到上限时，系统自动创建新实例
  - 多个Session共享实例的200并发度配额（SSE长连接和POST请求共享）
- **不支持 SessionAPI 管理。**

## 配置MCP Streamable HTTP亲和

### 流程概述

配置MCP Streamable HTTP亲和包括四个步骤：开启会话亲和、选择MCP Streamable HTTP类型、配置HTTP触发器、配置参数并部署。需要确保函数代码实现MCP协议规范。

### 开启会话亲和

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com)
2. 进入函数列表，选择目标函数或[创建函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/function-instance-1/)
  
  创建函数时，可以直接在**高级配置**区域，找到**隔离性、亲和性**配置项，进行后续配置后创建
3. 在函数详情页面，点击**配置**标签页
4. 在**高级配置**区域，找到**隔离性、亲和性**配置项
5. 点击**隔离性、亲和性**，展开配置面板
6. 开启**会话亲和**开关

### 选择MCP Streamable HTTP亲和类型

1. 在会话亲和配置区域，选择**MCP Streamable HTTP 亲和**单选按钮
2. 系统自动显示MCP Streamable HTTP亲和的配置选项

### 配置HTTP触发器

**目的**：确保HTTP触发器支持MCP Streamable HTTP协议所需的请求方法。

**操作步骤**：

1. 在函数详情页面，点击**触发器**标签页
2. 检查或创建HTTP触发器
3. 确保触发器支持以下请求方法：
  
  - **GET**：用于SSE长连接（可选）
  - **POST**：用于MCP请求和Session初始化（必需）
  - **DELETE**：用于终止Session（必需）

### 配置会话参数

**目的**：设置Session数量、生命周期和空闲时长，控制会话绑定和资源使用。

**操作步骤**：

1. **单实例并发 Session 数**：设置单实例可同时处理的最大Session数
  
  - 默认值：20
  - 取值范围：1-200
  - 建议：测试场景可设置为较小值（如10），生产环境根据业务需求调整；
2. **单个 Session 生命周期**：设置Session从创建到销毁的最长时长
  
  - 默认值：21600秒（6小时）
  - 说明：超过此时间后，系统自动销毁Session，不再保证亲和性
3. **Session Idle时长**：设置Session空闲多长时间后自动销毁
  
  - 默认值：1800秒（30分钟）
  - 说明：实例无请求超过此时长，Session进入空闲状态并自动销毁
4. 点击**部署**按钮保存配置

**重要提示**：

- 开启会话亲和后，系统会自动将**单实例并发度**调整为200（系统默认值，不可手动调整）
- 确保HTTP触发器支持GET、POST和DELETE方法，DELETE方法用于终止Session

## **验证MCP Streamable HTTP亲和配置**

请参考 MCP官方文档[Build an MCP client](https://modelcontextprotocol.io/docs/develop/build-client)，可使用函数计算提供的默认 http 触发器域名或自定义域名，通过标准的 MCP Client向函数发起请求，验证亲和配置。

## 常见问题

### 为什么MCP Streamable HTTP亲和不生效？

**可能原因**：

1. HTTP触发器未支持GET、POST和DELETE方法
2. 未通过MCP标准协议发送请求

**排查步骤**：

1. 检查HTTP触发器是否支持GET、POST和DELETE方法
2. 请使用标准 MCP Streamable协议请求

### 如何终止Session？

**方法**：

- 客户端通过DELETE请求终止Session
- 请求头中需要携带`Mcp-Session-Id`字段
- 系统清除平台侧会话并释放资源
