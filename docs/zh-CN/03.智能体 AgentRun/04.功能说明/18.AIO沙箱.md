# AIO沙箱

AIO Sandbox (All-In-One Sandbox) 是集成 BrowserTool（无头浏览器） 与 Code Interpreter（代码执行） 能力的统一云端隔离环境。它旨在作为 AI Agent 的“眼睛、大脑与手”，提供一站式的网页自动化、复杂计算、文件处理与交互式终端能力。

**主要用途：**

- **AI Agent 集成**：在同一会话中驱动浏览器交互，并立即运行代码处理抓取到的数据。
- **自动化测试**：在受控容器中协同执行浏览器 E2E 测试与后台脚本。
- **数据采集与处理**：通过浏览器抓取动态渲染页面，随后在沙箱内进行解析、转换并导出。
- **内容生成与归档**：自动化生成截图/PDF/录屏，并实现结果的持久化存储或下载。

**核心价值：**

- **免运维**：无需管理浏览器集群或复杂的代码运行依赖。
- **Serverless架构**：按需计费，支持根据任务负载自动伸缩。
- **原生兼容**：支持 Puppeteer、Playwright 等主流框架，提供安全的RESTful API。

## **准备工作**

### 1. 权限配置

首次使用，请登录[AgentRun控制台](https://functionai.console.aliyun.com/cn-hangzhou/agent/runtime/agent-list)，根据界面提示创建服务关联角色`AliyunServiceRoleForAgentRun`。

### 2. 获取关键信息

- 阿里云主账号 ID：在控制台右上角头像处获取。
- 凭证 Secret (API-KEY)：在控制台凭证管理页面获取。
- 数据面 Base URL：`https://${阿里云主账号 ID}.agentrun-data.cn-hangzhou.aliyuncs.com`。

## **快速入门**

### **1. 核心概念**

- 沙箱模板：定义实例的基础配置（如资源规格）。
- 沙箱实例：执行任务的具体环境。
  
  - 生命周期：默认最长 6 小时。
  - 闲置超时：通过`sandboxIdleTimeoutInSeconds`设置，若闲置超过该值将提前释放资源。

### **2. 基本使用流程**

1. 创建模板：在控制台**Sandbox沙箱**页签下，选择创建。
2. 启动实例：基于模板调用 API 开启沙箱。
3. 执行代码/控制浏览器：通过 API 提交代码或连接 CDP 端口。

## **控制面OpenAPI**

### **准备工作**

1. 进入[OpenAPI Explorer](https://next.api.aliyun.com/api/)。
2. 在顶部菜单栏，单击**选择云产品**，在搜索框搜索并选择**AgentRun**。
3. 在左侧导航栏，找到对应的API接口开始使用。

### **模板管理**

以上述OpenAPI门户链接中的API文档为准。

## **数据面API参考**

数据面API用于管理和操作沙箱实例。通常，需要先通过控制面API（或在控制台）创建好沙箱模板，然后才能调用以下数据面API来创建和使用实例。

### 沙箱实例管理

数据面的沙箱实例管理通常情况下需要配合凭证进行调用，如果没有携带凭证将会调用失败。如果您确实需要匿名调用沙箱实例管理接口，请在创建模板的时候确认不绑定凭证（不推荐）。

**

**说明**

该部分接口暂未上线OpenAPI Explorer，可先通过SDK或直接调用API端点使用。

#### 创建沙箱实例

- **请求路径：**`POST ${BASEURL}/sandboxes`
- **请求头：**
  
  `X-Acs-Parent-Id: ${阿里云主账号ID}`
  
  `X-API-KEY: 凭证 Secret`
  
  `Content-Type: application/json`
- **请求体：**
  
  ```
  { "templateName": "string", // 必需：模板名称，系统内部通过 templateName 查询 template_id "sandboxId": "string", // 可选：自定义沙箱 ID，用于端到端 tracing。如果不指定，系统会自动生成 ULID 格式的 ID }
  ```
- **响应示例：**
  
  ```
  { "sandboxId": "01JCED8Z9Y6XQVK8M2NRST5WXY", "templateId": "01JCED8Z9Y6XQVK8M2NRST5ABC", "templateName": "aio-sandbox", "templateType": "AllInOne", "status": "READY", "sandboxIdleTimeoutInSeconds": 3600, "createdAt": "2024-12-02T10:30:00Z", "lastUpdatedAt": "2024-12-02T10:30:15Z", "metadata": { "fcSessionDetails": { "sessionId": "1234567890abcdef", "sessionStatus": "Active", "sessionIdleTimeoutInSeconds": 3600, "functionName": "sandbox-function", "qualifier": "LATEST", "containerId": "container-123", "createdTime": "2024-12-02T10:30:00Z", "lastModifiedTime": "2024-12-02T10:30:15Z", "sessionAffinityType": "HEADER_FIELD" } } }
  ```

#### 停止Sandbox实例

**请求路径：**POST`${BASEURL}/sandboxes/{sandboxId}/stop`

**请求头：**

`X-Acs-Parent-Id: ${阿里云主账号ID}`

`X-API-KEY: 凭证 Secret`

**路径参数：**

- `sandboxId`（string, 必需）： 沙箱 ID

**请求体：**无

**响应示例：**

```
{ "sandboxId": "01JCED8Z9Y6XQVK8M2NRST5WXY", "templateId": "01JCED8Z9Y6XQVK8M2NRST5ABC", "templateName": "aio-sandbox", "templateType": "AllInOne", "status": "TERMINATED", "sandboxIdleTimeoutInSeconds": 3600, "createdAt": "2024-12-02T10:30:00Z", "lastUpdatedAt": "2024-12-02T11:00:00Z", "endedAt": "2024-12-02T11:00:00Z" }
```

**说明：**

- 停止 Sandbox 会删除 FC Session 并将数据库状态更新为`TERMINATED`
- 操作具有幂等性，如果 Sandbox 已经是`TERMINATED`状态，直接返回
- 会设置`endedAt`时间戳

#### **删除Sandbox实例**

**请求路径：**`DELETE ${BASEURL}/sandboxes/{sandboxId}`

**请求头：**

`X-Acs-Parent-Id: ${阿里云主账号ID}`

`X-API-KEY: 凭证 Secret`

**路径参数：**

- `sandboxId`（string，必需）：沙箱 ID

**请求体：**无

**响应示例：**

```
{ "sandboxId": "01JCED8Z9Y6XQVK8M2NRST5WXY", "templateId": "01JCED8Z9Y6XQVK8M2NRST5ABC", "templateName": "aio-sandbox", "templateType": "AllInOne", "status": "TERMINATED", "sandboxIdleTimeoutInSeconds": 3600, "createdAt": "2024-12-02T10:30:00Z", "lastUpdatedAt": "2024-12-02T11:30:00Z", "endedAt": "2024-12-02T11:00:00Z" }
```

删除 Sandbox 会执行以下操作：

- 检查 Sandbox 是否存在
- 如果 Sandbox 是`READY`状态，先调用 StopSandbox 删除 FC Session
- 会返回删除前 Sandbox 的状态

#### 状态说明

- `CREATING`: 创建中
- `READY`: 就绪，可以使用
- `TERMINATED`: 已停止（通过 StopSandbox 接口）

### **健康检查**

#### **检查服务健康状态**

**请求语法**：`GET ${BASEURL}/sandboxes/{sandboxId}/health`

**请求头**：`X-Acs-Parent-Id：${阿里云主账号ID}`

**查询参数**：无

**响应示例**：

```
{ "status": "ok", }
```

## 重要端点与协议

### **BrowserTool协议端点**

从AIO沙箱**详情**页进入**调试与VNC**，在右上方点击**CDP**/**VNC**复制端点地址。示例如下：

#### CDP 自动化端点（用于 Puppeteer / Playwright）

- 格式（示例）：`wss://{accountID}.agentrun-data.cn-hangzhou.aliyuncs.com/sandboxes/{sandboxId}/ws/automation?tenantId={accountID}&Authorization={accessToken}`
- 用途：连接 Chromium 的 Chrome DevTools Protocol（CDP），支持 Puppeteer/Playwright 的`connect`/`connectOverCDP`。

#### VNC 实时流端点（/ws/livestream）

- 格式（示例）:wss://{accountID}.agentrun-data.cn-hangzhou.aliyuncs.com/sandboxes/{sandboxID}/ws/livestream?tenantId={accountID}&Authorization={accessToken}
- 用途：通过 noVNC 等客户端实时查看浏览器桌面画面，便于调试与可视化监控。

#### 录制管理

- VNC 录制管理：`GET /recordings/`、`GET /recordings/{filename}`、`DELETE /recordings/{filename}`
- 列表：`GET /recordings/?page=&page_size=`返回录制文件列表与 metadata。
- 下载：`GET /recordings/{filename}`（仅支持 .mkv，Content-Type: video/x-matroska，支持流式传输，录制中也可下载）。
- 删除：`DELETE /recordings/{filename}`（慎重，操作不可恢复）。

更多细节请参考[BrowserTool浏览器](https://help.aliyun.com/zh/functioncompute/fc/sandbox-browsertool)。

### Code Interpreter

数据面 REST API（代码执行、文件系统、进程管理等）

- Base URL:`https://${阿里云主账号ID}.agentrun-data.cn-hangzhou.aliyuncs.com/`
- 关键资源：
  
  - 创建执行上下文（language: python/javascript）：`POST /sandboxes/{sandboxId}/contexts`
  - 同步执行代码：`POST /sandboxes/{sandboxId}/contexts/execute`
  - 文件管理：`GET /sandboxes/{sandboxId}/filesystem`、`/filesystem/download`、`/filesystem/upload`
  - 同步命令执行：`POST /sandboxes/{sandboxId}/processes/cmd`
  - WebSocket 交互式终端：`GET /sandboxes/{sandboxId}/processes/tty?protocol=text`

更多细节请参考[Code Interpreter代码解释器](https://help.aliyun.com/zh/functioncompute/fc/sandbox-sandbox-code-interepreter)。

## **快速示例**

在 AIO 沙箱中，您可以使用 Code Interpreter 和 Browser 两类 sandbox 的功能，您可以在 Sandbox 中直接操作浏览器，我们已经为您预装了`puppeteer-code`(nodejs) 和`playwright`(python)，您可以在代码解释器中执行如下的代码，操作内置的浏览器。

```
const puppeteer = require('puppeteer-core'); async function controlBrowser() { // 如希望启用录制请使用 'ws://localhost:5000/ws/automation?recording=true' const browserWSEndpoint = 'ws://localhost:5000/ws/automation'; console.log('正在连接到浏览器:', browserWSEndpoint); let browser; try { browser = await puppeteer.connect({ browserWSEndpoint: browserWSEndpoint, timeout: 5000 }); console.log('连接成功!'); const page = await browser.newPage(); await page.setViewport({ width: 1920, height: 1080 }); console.log('正在打开 https://www.bing.com ...'); await page.goto('https://www.bing.com', { waitUntil: 'networkidle2', timeout: 10000 }); const title = await page.title(); console.log('页面标题:', title); console.log('已断开连接'); } catch (error) { console.error('发生错误:', error.message); } finally { if (browser) await browser.disconnect(); } } (async () => { try { await controlBrowser(); console.log("脚本执行完毕"); } catch (err) { console.error("未捕获的顶层错误:", err); } })();
```

```
from playwright.sync_api import sync_playwright def run(): with sync_playwright() as playwright: chromium = playwright.chromium browser = chromium.connect_over_cdp("ws://localhost:5000/ws/automation") context = browser.contexts[0] page = context.pages[0] page.goto("https://www.example.com") print(page.title()) browser.close() run()
```

您可以通过 Code Interpreter 提供的`/contexts/execute`提交上述代码进行运行，内部将自动处理与浏览器的交互过程。

## **使用限制与计费**

- 生命周期：单个实例最长存活 6 小时。
- 计费模式：Serverless 按需计费，详细计费规则请参考[函数计算计费概述](https://help.aliyun.com/zh/functioncompute/fc/product-overview/billing-overview-of-fc)。
- 最佳实践：
  
  - 及时释放：任务结束后务必调用`stop`接口或设置合理的`sandboxIdleTimeoutInSeconds`。
  - 资源清理：定期删除不必要的`/recordings/`录制文件。
  - 健康检查：通过`GET /sandboxes/{sandboxId}/health`监控实例可用性。
