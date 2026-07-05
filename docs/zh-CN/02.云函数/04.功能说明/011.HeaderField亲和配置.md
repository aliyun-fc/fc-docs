# HeaderField亲和配置

HeaderField亲和功能允许通过HTTP请求头中的指定字段实现会话亲和，支持客户端传入或服务端生成两种模式，将携带相同HeaderField值的请求路由到同一个函数实例。

## 核心配置

在函数配置页面的**高级配置 > 隔离性、亲和性**中，开启**会话亲和**开关，选择**HeaderField 亲和**，配置**Header Name**（如`mySessionId`）、**单实例并发 Session 数、会话生命周期配置**，点击**部署**即可启用。

客户端可在请求头中携带自定义Session ID，或由服务端自动生成并在响应头中返回。

## 适用范围

- **通用限制：**使用前请先阅读[会话亲和通用限制及原理说明](https://help.aliyun.com/zh/functioncompute/fc/user-guide/cookie-affinity-feature)。
- **会话 ID 来源**：
  
  - 若客户端在预定义 Header 中传入会话 ID，则以该值作为会话标识。
    
    1. 长度限制为 [1,64]
    2. 以字母、数字或下划线开头，后面可跟字母、数字、下划线或连字符（-）的字符串
  - 若未传入，服务端将生成全局唯一会话 ID，通过CreateFunction预定义的Header字段，通过响应 Header 返回。
- **Header 字段定义**：在创建函数时，于`SessionAffinityConfig`中指定用于传输会话 ID 的 Header 字段名。
- **请求限制**
  
  - 单实例可同时处理多个Session（默认20个，最大200个），当单实例下绑定的Session数达到上限时，系统自动创建新实例
  - 多个Session共享实例的200并发度配额
- **支持 SessionAPI 管理：**可通过 SessionAPI 对会话进行生命周期管理（如创建、更新、查询、终止等）。

## 配置HeaderField亲和

### 流程概述

配置HeaderField亲和包括四个步骤：开启会话亲和、选择HeaderField类型、配置Header Name、配置参数并部署。可在创建函数时配置，也可为已有函数补充配置。

### 开启会话亲和

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com)
2. 进入函数列表，选择目标函数或[创建函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/function-instance-1/)
  
  创建函数时，可以直接在**高级配置**区域，找到**隔离性、亲和性**配置项，进行后续配置后创建
3. 在函数详情页面，点击**配置**标签页
4. 在**高级配置**区域，找到**隔离性、亲和性**配置项
5. 点击**隔离性、亲和性**，展开配置面板
6. 开启**会话亲和**开关

### 选择HeaderField亲和类型

1. 在会话亲和配置区域，选择**HeaderField 亲和**单选按钮
2. 系统自动显示HeaderField亲和的配置选项

### 配置Header Name

**目的**：设置用于传递Session ID的HTTP请求头名称。

**操作步骤**：

在**Header Name**输入框中，输入自定义的Header名称

- 命名规范：
  
  - 不能以`x-fc-`前缀开头
  - 以字母开头
  - 非首字符可包含数字、中划线、下划线、字母
  - 长度5-40个字符
- 示例：`mySessionId`、`session-id`、`customSessionId`
- 建议：使用有意义的名称，便于识别和维护

### 配置会话参数

**目的**：设置Session数量、生命周期和空闲时长，控制会话绑定和资源使用。

**操作步骤**：

1. **单实例并发 Session 数**：设置单实例可同时处理的最大Session数
  
  - 默认值：20
  - 取值范围：1-200
  - 建议：测试场景可设置为较小值（如10），生产环境根据业务需求调整
2. **单个 Session 生命周期**：设置Session从创建到销毁的最长时长
  
  - 默认值：21600秒（6小时）
  - 说明：超过此时间后，系统自动销毁Session，不再保证亲和性
3. **Session Idle时长**：设置Session空闲多长时间后自动销毁
  
  - 默认值：1800秒（30分钟）
  - 说明：实例无请求超过此时长，Session进入空闲状态并自动销毁
4. 点击**部署**按钮保存配置

**重要提示**：

- 开启会话亲和后，系统会自动将**单实例并发度**调整为200（系统默认值，不可手动调整）
- **Header Name**配置后不可随意修改，修改后需要客户端同步更新

## 验证HeaderField亲和功能

**目的**：验证相同HeaderField值的请求路由到同一实例，以及实例自动扩容机制。

可以通过在控制台函数详情页，查看实例扩容变化。

**操作步骤**：

1. **准备测试环境**
  
  - 确保函数已部署并配置了HeaderField亲和（Header Name =`mySessionId`，单实例并发 Session 数建议设置为2）
  - 在函数详情页，点击触发器，获取函数的HTTP触发器地址
  - 如果HTTP触发器使用签名认证，建议修改为匿名访问以便测试
2. **测试服务端生成模式**

```
# 第一次请求，不携带Header，服务端会自动生成Session ID curl -v http://your-function-url/your-path
```

- 从响应头中提取配置的Header Name的值（服务端生成的Session ID）
- 记录响应中的实例ID

1. **验证同一Session路由到同一实例**

```
# 使用提取的Session ID发起后续请求 curl -v -H "mySessionId: <从响应中提取的Session ID>" http://your-function-url/your-path
```

- **验证点**：多次请求应该路由到同一个实例，在函数详情页可以找到实例按钮，是否有新实例产生

1. **测试客户端传入模式**

```
# 客户端主动传入Session ID curl -v -H "mySessionId: session-2" http://your-function-url/your-path
```

- **验证点**：如果单实例并发Session数为2，新Session应该绑定到同一实例

1. **验证实例自动扩容**

```
# 客户端传入新的Session ID curl -v -H "mySessionId: session-3" http://your-function-url/your-path
```

- **验证点**：当实例Session数达到上限时，新Session应该绑定到新创建的实例

**预期结果**：

- 相同HeaderField值的请求路由到同一实例
- 客户端传入和服务端生成两种模式均正常工作
- 当实例Session数达到上限时，系统自动创建新实例

## 常见问题

### 客户端传入和服务端生成模式有什么区别？

**区别**：

- **客户端传入模式**：客户端主动控制Session ID，适用于需要自定义Session ID的场景
- **服务端生成模式**：服务端自动生成Session ID，客户端只需提取response字段，并在后续请求中携带此ID，适用于简化客户端实现的场景。

**选择建议**：

- 需要自定义Session ID或与现有系统集成时，使用客户端传入模式
- 需要简化客户端实现时，使用服务端生成模式
