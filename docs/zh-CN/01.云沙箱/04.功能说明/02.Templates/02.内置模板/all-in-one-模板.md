# All-In-One 模板

All-In-One 模板将 browser 模板与 code-interpreter-v1 模板能力合并，提供一个统一的云端隔离执行环境。All-In-One 沙箱既能通过 CDP/VNC 驱动云端浏览器，也能在同一沙箱内执行 Python/JavaScript 代码、处理文件和运行终端命令，适合需要“浏览器自动化 + 代码执行”协同的 AI Agent 场景。

All-In-One 模板对齐 E2B 中浏览器自动化与 Code Interpreter 协同使用的体验。

## 功能特性

| **特性** | **说明** |
| --- | --- |
| 浏览器自动化 | 内置 Chromium/Chrome 浏览器，支持 CDP over WebSocket，兼容 Puppeteer、Playwright、BrowserUse 等自动化框架 |
| VNC 实时可视化 | 内置 VNC 服务，支持通过 noVNC 客户端实时查看浏览器桌面环境，方便调试和监控 |
| 代码执行 | 集成 Code Interpreter 能力，支持 Python/JavaScript 代码执行、上下文保持和结果返回 |
| 文件系统操作 | 支持上传、下载、读取、写入、目录管理等文件 API，可将浏览器采集结果交给代码继续处理 |
| 终端命令 | 支持同步命令执行和 WebSocket 交互式终端（TTY） |
| 协同执行 | 在同一沙箱会话中完成“浏览器访问动态页面 -> 代码解析/分析 -> 文件导出”的端到端工作流 |
| 安全隔离 | 每个 All-In-One 沙箱实例拥有独立的文件系统、浏览器实例和进程空间 |

## 适用场景

| **场景** | **说明** |
| --- | --- |
| AI Agent 复合任务 | 在同一会话中驱动浏览器完成页面交互，同时运行代码进行数据分析、推理辅助或文件处理 |
| 数据采集与处理 | 先用浏览器抓取动态页面、截图或下载文件，再用 Python 脚本解析、清洗、汇总和导出 |
| 自动化测试 | 将浏览器 E2E 测试与后台脚本、日志分析、报告生成放在同一个隔离容器中完成 |
| 内容生成与归档 | 生成截图、PDF、视频录制或结构化数据，并通过文件 API 下载结果 |

## 默认配置

All-In-One 模板的默认配置如下：

| **配置项** | **默认值** | **说明** |
| --- | --- | --- |
| 容器镜像 | `fc-e2b-registry.ap-southeast-1.cr.aliyuncs.com/runtime/all-in-one:v0.0.36` | 预置一体化沙箱镜像 |
| 浏览器端口 | 3000 | browser 服务监听端口，用于 `/health`、CDP 和 VNC |
| 代码执行端口 | 5000 | Code Interpreter/envd 服务监听端口 |
| CPU | 4 vCPU | 推荐规格，需同时支撑浏览器和代码执行 |
| 内存 | 8192 MB | 推荐规格 |
| 磁盘大小 | 10240 MB | 建议 10 GB 以存储浏览器缓存、截图、下载文件和代码执行结果 |

> **说明**
>
> All-In-One 模板的默认 CPU 和内存规格高于 code-interpreter-v1 模板和 browser 模板，因为需要同时支撑浏览器运行时和代码执行环境。示例镜像位于新加坡地域（`ap-southeast-1`），构建和运行模板时建议使用同地域的 API URL 与域名。

## 与 browser 模板的区别

browser 模板提供浏览器运行时，默认通过 3000 端口暴露 CDP 和 VNC 能力，适合网页访问、页面交互、截图、数据采集和 UI 测试等浏览器自动化任务。它包含 E2B envd 兼容基础能力，但不提供 Code Interpreter 服务，因此不能通过 Code Interpreter 上下文直接执行 Python。

All-In-One 模板在浏览器能力之上叠加 Code Interpreter 服务，默认同时使用 3000 端口作为浏览器入口、5000 端口作为代码执行和文件管理入口。它可以在同一个沙箱会话中直接执行 Python，用于完成“浏览器抓取动态页面 -> Python 解析/清洗/分析 -> 文件导出”的复合流程。

| **对比项** | **browser 模板** | **All-In-One 模板** |
| --- | --- | --- |
| 核心定位 | 轻量浏览器自动化环境 | 浏览器自动化 + 代码执行的一体化环境 |
| 浏览器能力 | 支持 CDP、VNC、截图、页面交互 | 支持 CDP、VNC、截图、页面交互 |
| Code Interpreter 服务 | 不支持 | 支持 |
| 代码执行 | 不支持通过 Code Interpreter 执行 Python | 支持 Python/JavaScript 代码执行 |
| 文件处理 | 支持基础文件访问，不提供 Code Interpreter 文件 API | 支持文件 API、上下文内读写和处理 |
| 典型入口 | 3000（浏览器入口） | 3000（浏览器入口）/ 5000（代码入口） |
| 推荐规格 | 4 vCPU / 8192 MB / 10240 MB 磁盘 | 4 vCPU / 8192 MB / 10240 MB 磁盘 |
| 推荐场景 | 只需要浏览器自动化 | 需要浏览器和代码执行协同 |

## 快速入门

All-In-One 模板的完整用法分为两个阶段：先**构建模板**（从 All-In-One 镜像固化出一个带名称的模板），再**运行模板**（创建沙箱、等待 browser 服务健康检查、通过 CDP 自动化并截图、通过 Code Interpreter 执行代码）。下面分别给出 Python 与 Node.js 两种实现。

> **说明**：示例中的 `API_KEY` 需替换为您在控制台生成的 API Key，`API_URL` / `DOMAIN` 需替换为对应地域的接入地址。连接 CDP/VNC 端点时需在请求头中携带 `X-Access-Token` 进行身份验证：Python SDK 可通过内部属性 `sbx._envd_access_token` 获取（后续版本可能重命名或移除），JS SDK 可使用公开字段 `sbx.envdAccessToken`。

### 第一步：创建 API Key

1. 登录 [函数计算控制台](https://fcnext.console.aliyun.com/)。
2. 在**云沙箱**页签下选择 **API Keys**，生成 API Key。
3. 通过 SDK 使用 API Key 与 API 端点构建模板并创建沙箱。

### 第二步：准备本地环境

**Python**：

```bash
uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install e2b e2b-code-interpreter 'playwright>=1.49.0'
playwright install chromium
```

**Node.js**：使用如下 `package.json`，然后执行 `npm install`。

```json
{
  "name": "all-in-one-template-demo",
  "version": "1.0.0",
  "type": "module",
  "dependencies": {
    "@e2b/code-interpreter": "^2.6.1",
    "e2b": "^2.31.0",
    "playwright-core": "^1.49.0"
  },
  "devDependencies": {
    "@types/node": "^26.1.0",
    "tsx": "^4.23.0",
    "typescript": "^6.0.3"
  }
}
```

### 第三步：构建 All-In-One 模板

从 All-In-One 镜像构建一个带名称的模板，构建时指定 CPU 与内存规格（推荐 4 vCPU / 8192 MB）。

**Python**：

```python
"""All-In-One 模板构建示例。"""

from e2b import Template, default_build_logger

API_KEY = "e2b_xxx"  # 替换为您的 API Key
API_URL = "https://api.ap-southeast-1.e2b.fc.aliyuncs.com"
DOMAIN = "ap-southeast-1.e2b.fc.aliyuncs.com"
FROM_IMAGE = "fc-e2b-registry.ap-southeast-1.cr.aliyuncs.com/runtime/all-in-one:v0.0.36"
OPTS = {"api_key": API_KEY, "api_url": API_URL, "domain": DOMAIN}

TEMPLATE_NAME = "my-all-in-one-template"

build = Template.build(
    Template().from_image(FROM_IMAGE),
    name=TEMPLATE_NAME,
    cpu_count=4,
    memory_mb=8192,
    skip_cache=False,
    on_build_logs=default_build_logger(),
    **OPTS,
)

print(f"template_id: {build.template_id}")
print(f"build_id: {build.build_id}")
```

**Node.js**：

```javascript
// All-In-One 模板构建示例。
import { Template, defaultBuildLogger } from 'e2b';

const API_KEY = 'e2b_xxx'; // 替换为您的 API Key
const API_URL = 'https://api.ap-southeast-1.e2b.fc.aliyuncs.com';
const DOMAIN = 'ap-southeast-1.e2b.fc.aliyuncs.com';
const FROM_IMAGE =
  'fc-e2b-registry.ap-southeast-1.cr.aliyuncs.com/runtime/all-in-one:v0.0.36';
const OPTS = { apiKey: API_KEY, apiUrl: API_URL, domain: DOMAIN };

const TPL_NAME = 'my-all-in-one-template';

async function main() {
  const build = await Template.build(Template().fromImage(FROM_IMAGE), TPL_NAME, {
    ...OPTS,
    cpuCount: 4,
    memoryMB: 8192,
    skipCache: false,
    onBuildLogs: defaultBuildLogger(),
  });

  console.log(`template_id: ${build.templateId}`);
  console.log(`build_id: ${build.buildId}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
```

### 第四步：运行模板并验证组合能力

创建沙箱后，先轮询 `/health` 等待 browser 服务就绪，再通过 CDP 端点连接 Playwright 打开目标页并截图，最后通过 Code Interpreter 执行一段 Python 代码验证代码执行能力。

**Python**：

```python
"""All-In-One 模板运行示例：创建沙箱 -> CDP 自动化 -> Code Interpreter 执行代码。"""

import time

from e2b_code_interpreter import Sandbox

API_KEY = "e2b_xxx"  # 替换为您的 API Key
API_URL = "https://api.ap-southeast-1.e2b.fc.aliyuncs.com"
DOMAIN = "ap-southeast-1.e2b.fc.aliyuncs.com"
OPTS = {"api_key": API_KEY, "api_url": API_URL, "domain": DOMAIN}

TEMPLATE_NAME = "my-all-in-one-template"

BROWSERTOOL_PORT = 3000
TARGET_URL = "https://example.com"
SCREENSHOT_PATH = "all-in-one-example.png"


def wait_until_healthy(sbx: Sandbox, host: str, token: str, timeout: int = 60) -> None:
    """轮询公网网关 /health 端点，直到 browser 服务就绪或超时。"""
    token_header = f"-H 'X-Access-Token: {token}' " if token else ""
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = sbx.commands.run(
            f"curl -sS -o /dev/null -w '%{{http_code}}' -m 4 "
            f"{token_header}"
            f"https://{host}/health",
            timeout=10,
        )
        code = "".join(result.stdout or []).strip()
        if code == "200":
            print(f"  /health 就绪 (HTTP {code})")
            return
        print(f"  ...等待 browser 服务就绪 (HTTP {code!r})")
        time.sleep(2)
    raise TimeoutError(f"browser 服务在 {timeout}s 内未就绪")


def verify_with_playwright(cdp_ws_url: str, headers: dict) -> None:
    """通过 CDP 连接 browsertool，打开目标页并截图。"""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(cdp_ws_url, headers=headers)
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.new_page()
        try:
            page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)
            title = page.title()
            print(f"  page.title() = {title!r}")
            assert "Example" in title, f"unexpected title: {title!r}"

            page.screenshot(path=SCREENSHOT_PATH, full_page=True)
            print(f"  截图已保存: {SCREENSHOT_PATH}")
        finally:
            page.close()
            browser.close()


sbx = None
try:
    sbx = Sandbox.create(template=TEMPLATE_NAME, timeout=900, **OPTS)
    print(f"sandbox_id: {sbx.sandbox_id}")

    host = sbx.get_host(BROWSERTOOL_PORT)
    cdp_ws_url = f"wss://{host}/ws/automation"
    token = sbx._envd_access_token
    headers = {"X-Access-Token": token} if token else {}

    print("\n--- 等待 browser 健康检查 ---")
    wait_until_healthy(sbx, host, token)

    print("\n--- Playwright CDP 用例 ---")
    verify_with_playwright(cdp_ws_url, headers)

    print("\n--- Code Interpreter 用例 ---")
    execution = sbx.run_code(
        "import json\n"
        "result = {'status': 'ok', 'source': 'all-in-one'}\n"
        "print(json.dumps(result, ensure_ascii=False))"
    )
    print(execution.logs.stdout)
finally:
    if sbx is not None:
        sbx.kill()
        print("\n沙箱已销毁")
```

**Node.js**：

```javascript
// All-In-One 模板运行示例：创建沙箱 -> CDP 自动化 -> Code Interpreter 执行代码。
import { Sandbox } from '@e2b/code-interpreter';
import { chromium } from 'playwright-core';

const API_KEY = 'e2b_xxx'; // 替换为您的 API Key
const API_URL = 'https://api.ap-southeast-1.e2b.fc.aliyuncs.com';
const DOMAIN = 'ap-southeast-1.e2b.fc.aliyuncs.com';
const OPTS = { apiKey: API_KEY, apiUrl: API_URL, domain: DOMAIN };

const TPL_NAME = 'my-all-in-one-template';

const BROWSERTOOL_PORT = 3000;
const TARGET_URL = 'https://example.com';
const SCREENSHOT_PATH = 'all-in-one-example.png';

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

/** 轮询公网网关 /health 端点，直到 browser 服务就绪或超时。 */
async function waitUntilHealthy(sbx, host, token, timeout = 60) {
  const tokenHeader = token ? `-H 'X-Access-Token: ${token}' ` : '';
  const deadline = Date.now() + timeout * 1000;
  while (Date.now() < deadline) {
    let result;
    try {
      result = await sbx.commands.run(
        `curl -sS -o /dev/null -w '%{http_code}' -m 4 ` +
          tokenHeader +
          `https://${host}/health`,
        { timeoutMs: 10_000 },
      );
    } catch (e) {
      result = e;
    }
    const code = (result.stdout || '').trim();
    if (code === '200') {
      console.log(`  /health 就绪 (HTTP ${code})`);
      return;
    }
    console.log(`  ...等待 browser 服务就绪 (HTTP ${JSON.stringify(code)})`);
    await sleep(2000);
  }
  throw new Error(`browser 服务在 ${timeout}s 内未就绪`);
}

/** 通过 CDP 连接 browsertool，打开目标页并截图。 */
async function verifyWithPlaywright(cdpWsUrl, headers) {
  const browser = await chromium.connectOverCDP(cdpWsUrl, { headers });
  const contexts = browser.contexts();
  const context = contexts.length ? contexts[0] : await browser.newContext();
  const page = await context.newPage();
  try {
    await page.goto(TARGET_URL, { waitUntil: 'domcontentloaded', timeout: 30_000 });
    const title = await page.title();
    console.log(`  page.title() = ${JSON.stringify(title)}`);
    if (!title.includes('Example')) {
      throw new Error(`unexpected title: ${JSON.stringify(title)}`);
    }

    await page.screenshot({ path: SCREENSHOT_PATH, fullPage: true });
    console.log(`  截图已保存: ${SCREENSHOT_PATH}`);
  } finally {
    await page.close();
    await browser.close();
  }
}

async function main() {
  let sbx = null;
  try {
    sbx = await Sandbox.create(TPL_NAME, { ...OPTS, timeoutMs: 900_000 });
    console.log(`sandbox_id: ${sbx.sandboxId}`);

    const host = sbx.getHost(BROWSERTOOL_PORT);
    const cdpWsUrl = `wss://${host}/ws/automation`;
    const token = sbx.envdAccessToken;
    const headers = token ? { 'X-Access-Token': token } : {};

    console.log('\n--- 等待 browser 健康检查 ---');
    await waitUntilHealthy(sbx, host, token);

    console.log('\n--- Playwright CDP 用例 ---');
    await verifyWithPlaywright(cdpWsUrl, headers);

    console.log('\n--- Code Interpreter 用例 ---');
    const execution = await sbx.runCode(
      "import json\nresult = {'status': 'ok', 'source': 'all-in-one'}\nprint(json.dumps(result, ensure_ascii=False))",
    );
    console.log(execution.logs.stdout);
  } finally {
    if (sbx !== null) {
      await sbx.kill();
      console.log('\n沙箱已销毁');
    }
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
```

## WebSocket 端点说明

All-In-One 模板中的 browser 服务提供以下端点：

| **端点** | **路径** | **用途** |
| --- | --- | --- |
| 健康检查端点 | `https://<sandbox-host>/health` | 判断 browser 服务是否启动完成 |
| CDP 自动化端点 | `wss://<sandbox-host>/ws/automation` | 浏览器自动化，与 Puppeteer 和 Playwright 兼容 |
| VNC 实时流端点 | `wss://<sandbox-host>/ws/livestream` | 实时查看浏览器桌面环境，支持通过 noVNC 客户端查看 |

> **说明**：`<sandbox-host>` 通过 SDK 的 `sbx.get_host(3000)` 或 `sbx.getHost(3000)` 获取。所有端点均需在请求头中携带 `X-Access-Token` 进行身份验证。

在沙箱内部可以先探测 CDP WebSocket 握手是否正常。如果返回 `101 Switching Protocols`，说明 CDP 端点已经可升级为 WebSocket 连接：

```bash
curl -sS -m 4 -i \
  -H 'Connection: Upgrade' \
  -H 'Upgrade: websocket' \
  -H 'Sec-WebSocket-Version: 13' \
  -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' \
  http://localhost:3000/ws/automation
```

## VNC 实时查看

All-In-One 模板支持通过 VNC 实时查看远程浏览器的桌面环境，方便在开发和调试阶段监控自动化任务的执行情况。

### 使用在线 noVNC 客户端

1. 访问 noVNC 官方提供的在线客户端：[https://novnc.com/noVNC/vnc.html](https://novnc.com/noVNC/vnc.html)
2. 在连接设置中，**高级** > **WebSocket** 中填入以下连接信息：
   - **主机**：通过 `sbx.get_host(3000)` 或 `sbx.getHost(3000)` 获取的 host 地址
   - **端口**：`443`
   - **路径**：`ws/livestream`
3. 点击**连接**，即可看到浏览器界面。

> **说明**：noVNC 连接同样需要通过 `X-Access-Token` 进行身份验证。连接成功后，初始界面可能为黑屏或灰屏；当自动化脚本执行 `page.goto()` 等操作后，界面会显示相应内容。

## 组合工作流建议

| **阶段** | **建议做法** |
| --- | --- |
| 页面访问 | 使用 Playwright/Puppeteer 通过 `wss://<sandbox-host>/ws/automation` 连接浏览器 |
| 数据落盘 | 将截图、HTML、下载文件或中间结果写入沙箱文件系统 |
| 代码处理 | 使用 Code Interpreter SDK 的 `run_code` / `runCode` 在同一沙箱内解析和分析数据 |
| 结果导出 | 使用文件 API 或 SDK 下载生成的 CSV、JSON、图片、PDF 等结果文件 |

## 使用限制

| **限制项** | **约束** |
| --- | --- |
| 浏览器支持 | 目前内置 Chromium/Chrome 浏览器 |
| 资源规格 | 建议使用 4 vCPU / 8192 MB 或更高规格，避免浏览器和代码执行互相争抢资源 |
| 认证要求 | CDP、VNC、数据面 API 均需使用有效 API Key 或 `X-Access-Token` |

## 相关文档

- [沙箱模板概述](../02.内置模板.md)
- [构建模板](../03.构建自定义镜像模板.md)
- [创建沙箱](../../01.Sandbox/02.创建沙箱.md)
- [生命周期](../../01.Sandbox/01.生命周期.md)
- [base 模板](base-模板.md)（仅需 envd 基础能力时选择）
- [code-interpreter-v1 模板](code-interpreter-v1-模板.md)（仅需代码执行能力时选择）
- [browser 模板](browser-模板.md)（仅需浏览器自动化能力时选择）
