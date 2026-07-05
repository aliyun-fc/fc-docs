# All-in-One 模板

All-in-One（AIO）模板将 Browser Tool（无头浏览器沙箱）与 Code Interpreter（代码执行沙箱）能力合并，提供一个统一的云端隔离执行环境。AIO 沙箱既能做浏览器级自动化（CDP / VNC / 录制），也能做代码执行、文件管理与交互式终端，是 AI Agent 的"眼睛 + 大脑 + 手"。

## 功能特性

| **特性** | **说明** |
| --- | --- |
| 浏览器自动化 | 集成 Browser Tool 全部能力，支持 CDP 协议、Puppeteer/Playwright 兼容、VNC 实时查看和操作录制 |
| 代码执行 | 集成 Code Interpreter 全部能力，支持 Python/JavaScript 代码执行、上下文管理、文件系统操作 |
| 终端命令 | 支持同步命令执行和 WebSocket 交互式终端（TTY） |
| 进程管理 | 列出、查询、停止沙箱内运行的进程 |
| 协同执行 | 在同一会话中同时使用浏览器和代码解释器，实现"浏览器抓取 → 代码处理"的端到端工作流 |
| 安全隔离 | 基于 MicroVM 级别隔离，每个沙箱实例拥有独立的文件系统、浏览器实例和进程空间 |

## 适用场景

| **场景** | **说明** |
| --- | --- |
| AI Agent 复合任务 | 在同一会话中既能驱动浏览器完成页面交互，也能运行代码处理和分析数据 |
| 数据采集与处理 | 先用浏览器抓取动态页面，再在沙箱内运行脚本解析、清洗、导出结果 |
| 自动化测试 | 支持浏览器 E2E 与后台脚本协同执行，便于在受控容器环境中回放与问题定位 |
| 内容生成与归档 | 生成截图/PDF/录制，并把处理结果持久化或下载 |

## 默认配置

All-in-One 模板的默认配置如下：

| **配置项** | **默认值** | **说明** |
| --- | --- | --- |
| 容器镜像 | `sandbox-all-in-one:v0.9.30` | 预置一体化沙箱镜像 |
| 默认端口 | 5000 | 沙箱服务监听端口 |
| CPU | 4 vCPU | 默认规格，因需同时支撑浏览器和代码执行 |
| 内存 | 8192 MB（8 GB） | 默认规格 |
| 磁盘大小 | 10240 MB（10 GB） | 建议 10 GB 以存储浏览器数据和执行结果 |

**说明**

All-in-One 模板的默认 CPU 和内存规格高于 Code Interpreter 和 Browser Tool 模板，因为需要同时支撑浏览器运行时和代码执行环境。

## 快速入门

### 第一步：创建 AIO 沙箱

1. 登录 [函数计算控制台](https://fcnext.console.aliyun.com/)。
2. 创建并获取 API Key
3. 然后通过SDK的方式获取 API 端点

### 第二步：获取端点

AIO 沙箱提供以下端点：

| **端点** | **格式** | **用途** |
| --- | --- | --- |
| CDP 自动化端点 | `wss://{sbx.get_host(3000)}/ws/automation` | 浏览器自动化（Puppeteer/Playwright） |
| VNC 实时流端点 | `wss://{sbx.get_host(3000)}/ws/livestream` | 实时查看浏览器界面 |
| 数据面 REST API | `https://{accountID}.e2b-data.cn-hangzhou.aliyuncs.com/` | 代码执行、文件管理、终端命令 |

> **说明**：CDP 和 VNC 端点通过 SDK 的 `sbx.get_host(3000)` 获取 host 地址，连接时需要在请求头中携带 `X-Access-Token` 进行身份验证。

### 第三步：使用浏览器自动化

```javascript
const puppeteer = require('puppeteer-core');
const { Sandbox } = require('e2b');

const BROWSERTOOL_PORT = 3000;

async function main() {
  const sbx = await Sandbox.create({ template: 'all-in-one-template', apiKey: E2B_API_KEY, timeout: 600 });
  const host = sbx.getHost(BROWSERTOOL_PORT);
  const cdpEndpoint = `wss://${host}/ws/automation`;

  const browser = await puppeteer.connect({
    browserWSEndpoint: cdpEndpoint,
    headers: { 'X-Access-Token': sbx.envdAccessToken },
  });
  const page = await browser.newPage();
  await page.goto('https://example.com');
  await page.screenshot({ path: 'example.png' });
  await browser.close();
}
main();
```

### 第四步：使用代码执行

通过数据面 API 创建上下文并执行代码：

```json
POST ${BASEURL}/sandboxes/{sandboxId}/contexts

{
  "language": "python",
  "cwd": "/home/user"
}
```

```json
POST ${BASEURL}/sandboxes/{sandboxId}/contexts/execute

{
  "contextId": "{contextId}",
  "code": "import json\nprint(json.dumps({'status': 'ok'}))",
  "timeout": 30
}
```

### 在同一会话中协同使用

AIO 模板的核心优势是在同一沙箱会话中同时使用浏览器和代码执行能力。典型工作流：浏览器抓取数据 → Python 代码处理分析 → 文件 API 导出结果。

```python
import asyncio
from e2b import Sandbox
from browser_use import BrowserSession, BrowserProfile

BROWSERTOOL_PORT = 3000

async def run_aio_task():
    # 1. 创建沙箱并获取 CDP 端点
    sbx = Sandbox.create(template="all-in-one-template", api_key=E2B_API_KEY, timeout=600)
    host = sbx.get_host(BROWSERTOOL_PORT)
    cdp_url = f"wss://{host}/ws/automation"

    browser = BrowserSession(
        cdp_url=cdp_url,
        browser_profile=BrowserProfile(headless=True),
        extra_headers={"X-Access-Token": sbx._envd_access_token},
    )

    # 2. 通过数据面 API 创建 Python 上下文并执行数据处理代码
    #    POST ${BASEURL}/sandboxes/{sandboxId}/contexts
    #    POST ${BASEURL}/sandboxes/{sandboxId}/contexts/execute

    # 3. 用浏览器抓取数据，再用代码处理分析
    #    ...

asyncio.run(run_aio_task())
```