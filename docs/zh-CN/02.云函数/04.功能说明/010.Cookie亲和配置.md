# Cookie亲和配置

在分布式函数计算场景中，不同请求可能被路由到不同实例，导致会话状态无法保持。Cookie亲和功能通过服务端自动植入Cookie，将携带相同Cookie值的请求路由到同一个函数实例，确保会话状态一致性。

## 核心配置

在函数配置页面的**高级配置 > 隔离性、亲和性**中，开启**会话亲和**开关，选择**Cookie 亲和**，配置**单实例并发 Session 数、会话生命周期**，点击**部署**即可启用。

首次请求时系统会自动在响应头中植入Cookie，客户端后续请求携带此Cookie即可路由到同一实例。

## 适用范围

- **通用限制**：使用前建议先阅读[会话亲和通用限制及原理说明](https://help.aliyun.com/zh/functioncompute/fc/user-guide/cookie-affinity-feature)；
- **仅支持服务端植入 Cookie 模式**：客户端首次访问时，函数计算自动在响应中通过`Set-Cookie`Header 植入 Cookie。客户端需解析并保存该 Cookie，并在后续请求中携带。
- **请求限制：**
  
  - 单实例可同时处理多个Session（默认20个，最大200个），当单实例下绑定的Session数达到上限时，系统自动创建新实例
  - 多个Session共享实例的200并发度配额
- **支持 SessionAPI 管理**：可通过 SessionAPI 对会话进行生命周期管理（如创建、更新、查询、终止等）。

## 配置Cookie亲和

### 流程概述

配置Cookie亲和包括三个步骤：开启会话亲和、选择Cookie类型、配置参数并部署。可在创建函数时配置，也可为已有函数更新配置。

### 开启会话亲和

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com)
2. 进入函数列表，选择目标函数或[创建函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/function-instance-1/)
  
  创建函数时，可以直接在**高级配置**区域，找到**隔离性、亲和性**配置项，进行后续配置后创建
3. 在函数详情页面，点击**配置**标签页
4. 在**高级配置**区域，找到**隔离性、亲和性**配置项
5. 点击**隔离性、亲和性**，展开配置面板
6. 开启**会话亲和**开关

### 选择Cookie亲和类型

1. 在**会话亲和**配置区域，选择**Cookie 亲和**单选按钮
2. 系统自动显示Cookie亲和的配置选项

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
4. 点击**部署**按钮保存配置。

**重要提示**：

- 开启会话亲和后，系统会自动将**单实例并发度**调整为200（系统默认值，不可手动调整）
- 在创建函数时配置会话亲和，配置会随函数一起创建；如果为已有函数配置会话亲和，需要单独部署配置
- Cookie名称由系统自动生成，格式为`x-fc-cookie-session-id`，Cookie值由系统自动生成全局唯一ID
- Cookie的`Max-Age`默认为21600秒（6小时），与Session生命周期一致

## 验证Cookie亲和功能

**目的**：验证相同Cookie值的请求路由到同一实例，以及实例自动扩容机制。

- 相同Cookie值的请求路由到同一实例
- 当实例Session数达到上限时，系统自动创建新实例
- 所有请求都成功返回（状态码200）

可以通过在控制台函数详情页，查看实例扩容变化。

**操作步骤**：

1. **准备测试环境**
  
  - 确保函数已部署并配置了Cookie亲和（单实例并发 Session 数建议设置为2以便测试）
  - 获取函数的HTTP触发器地址
  - 测试时可以将HTTP触发器使用签名认证，修改为匿名访问以便测试：
    
    - 进入函数详情页面的**触发器**标签页
    - 点击触发器的**编辑**按钮
    - 将**认证方式**修改为**匿名访问**
    - 保存配置
2. **第一次请求：不带Cookie，系统会自动植入Cookie**
  
  - 发起第一个请求：`curl -i http://your-function-url/`
    
    在函数详情页，点击HTTP触发器，可以获取临时验证的url。
    
    **示例：**
    
    ```
    curl -i https://test-cookies-b*******v.cn-hangzhou.fcapp.run
    ```
  - **预期结果：**
    
    ```
    Content-Length: 13 Content-Type: text/html; charset=utf-8 Set-Cookie: x-fc-cookie-session-id=3******a-c**5-4**0-a**4-e**********4; Max-Age=21600 X-Fc-Request-Id: 1-******e8-******c9-e**********8 Date: Tue, 30 Dec 2025 11:47:53 GMT Hello, World!%
    ```
  - 从响应头中提取`Set-Cookie`中的Cookie值（`x-fc-cookie-session-id`）
  - 记录响应中的`X-Fc-Request-Id`（可用于分析请求路由情况）
3. **第二次请求：使用提取的Cookie值发起请求**
  
  - **验证同一Session路由到同一实例，**其中`<first-x-fc-cookie-session-id>`需替换为上一步提取的`Set-Cookie`中`x-fc-cookie-session-id`的值
    
    ```
    curl -i -b "x-fc-cookie-session-id=<first-x-fc-cookie-session-id>" https://your-function-url/
    ```
    
    **示例：**
    
    ```
    curl -i -b "x-fc-cookie-session-id=3******a-c**5-4**0-a**4-e**********4" https://test-cookies-b********v.cn-hangzhou.fcapp.run
    ```
  - **预期结果：**
    
    ```
    HTTP/1.1 200 OK Content-Length: 13 Content-Type: text/html; charset=utf-8 X-Fc-Request-Id: 1-******cb-******16-e**********2 Date: Tue, 30 Dec 2025 12:12:59 GMT Hello, World!%
    ```
  - **亲和验证**：在控制台函数详情页，点击**实例**>**实例日志**，可以观察到，两次请求由同一实例处理（根据`X-Fc-Request-Id`判断）
    
    第二次请求携带了第一次请求获取的cookie，同一实例的日志输出如下所示。
    
    ```
    2025-12-30 20:19:41 FC Invoke Start RequestId: 1-695xxx08d1309db 2025-12-30 20:19:41 FC Invoke End RequestId: 1-69xxx1309db 2025-12-30 20:19:42 * Serving Flask app 'app' * Debug mode: off WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead. * Running on all addresses (0.0.0.0) * Running on hxxx * Running on hxxx Press CTRL+C to quit Path: Data: b'' 21.0.0.1 - - [30/Dec/2025 12:19:41] "GET / HTTP/1.1" 200 - 2025-12-30 20:22:18 FC Invoke Start RequestId: 1-695xxxa15fef9d 2025-12-30 20:22:18 FC Invoke End RequestId: 1-695xxxa15fef9d 2025-12-30 20:22:19 Path: Data: b'' xxx - - [30/Dec/2025 12:22:18] "GET / HTTP/1.1" 200 -
    ```
4. **第三次请求：不带Cookie，系统会生成新的Cookie**
  
  - 发起新请求`curl -i https://your-function-url/`
    
    **示例：**
    
    ```
    curl -i http://test-cookies-o********j.cn-hangzhou.fcapp.run/
    ```
  - **预期结果：**系统为新的Session生成不同的Cookie值
    
    ```
    Access-Control-Expose-Headers: Date,x-fc-request-id Content-Disposition: attachment Content-Length: 13 Content-Type: text/html; charset=utf-8 Set-Cookie: x-fc-cookie-session-id=d******e-***3-4**5-a**2-3**********d; Max-Age=21600 X-Fc-Request-Id: 1-******cb-******16-1**********a Date: Tue, 30 Dec 2025 12:31:00 GMT Hello, World!%
    ```
  - **亲和验证：**如果单实例并发Session数为2，新Session应该绑定到同一实例。在控制台函数详情页，点击**实例**>**实例日志**查看（根据`X-Fc-Request-Id`判断）
    
    实例日志验证结果（实例规格: vCPU 0.35 vCPU / 内存 512 MB，函数: test-cookies，自定义运行时 Debian10）：前两次请求使用同一个 cookie 值，第三次请求使用新 cookie 值，说明会话亲和生效。
    
    ```
    2025-12-30 20:26:41 * Serving Flask app 'app' * Debug mode: off WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead. * Running on all addresses (0.0.0.0) * Running on xxx * Running on xxx Press CTRL+C to quit 2025-12-30 20:31:00 FC Invoke Start RequestId: 1-6xxx60a # 同一个cookie值 2025-12-30 20:31:00 FC Invoke End RequestId: 1-6xxx1760a 2025-12-30 20:31:01 Path: Data: b'' 2xxx -- [30/Dec/2025 12:31:00] "GET / HTTP/1.1" 200 – 2025-12-30 20:33:03 FC Invoke Start RequestId: 1-6xxxe69 # 同一个cookie值 2025-12-30 20:33:03 FC Invoke End RequestId: 1-6xxxe69 2025-12-30 20:33:04 Path: Data: b'' 2xxx -- [30/Dec/2025 12:33:03] "GET / HTTP/1.1" 200 – 2025-12-30 20:33:48 FC Invoke Start RequestId: 1-6xxx385d # 新cookie值 2025-12-30 20:33:48 FC Invoke End RequestId: 1-6xxx385d 2025-12-30 20:33:49 Path: Data: b'' 2xxx -- [30/Dec/2025 12:33:48] "GET / HTTP/1.1" 200 –
    ```
5. **发起第四次请求，不带Cookie，验证实例自动扩容**
  
  - **不带Cookie，发起请求，生成新的Cookie值，**实例Session数达到上限，新Session绑定到新创建的实例`curl -i http://your-function-url/`
    
    **示例：**
    
    ```
    curl -i http://test-cookies-o********j.cn-hangzhou.fcapp.run/
    ```
  - **预期结果：**
    
    ```
    HTTP/1.1 200 OK Access-Control-Expose-Headers: Date,x-fc-request-id Content-Disposition: attachment Content-Length: 13 Content-Type: text/html; charset=utf-8 X-Fc-Request-Id: 1-6******c-1******2-**********5d Date: Tue, 30 Dec 2025 12:33:48 GMT Hello, World!%
    ```
  - **亲和验证：**在控制台函数详情页，点击**实例**，可以看到新增实例
    
    实例列表中显示两个状态为**运行中**的实例，版本均为**LATEST**，表明已成功创建多个实例可用于亲和验证。

## 常见问题

### 为什么Cookie亲和不生效？

**可能原因**：

1. 客户端未正确解析首请求的Set-Cookie中的会话ID信息，并未正确在后续的请求中携带此ID
2. Session已超过生命周期或Idle时长被销毁
3. 函数未正确部署会话亲和配置

**排查步骤**：

1. 检差首请求响应头中是否包含`Set-Cookie`字段，且包含会话ID值信息。
2. 检查后续请求是否携带Cookie Header
3. 检查函数配置中会话亲和是否已开启并部署
