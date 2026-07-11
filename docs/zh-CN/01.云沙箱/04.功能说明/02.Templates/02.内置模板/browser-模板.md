# browser 模板

browser 模板提供云原生浏览器运行环境，支持通过标准的 Chrome DevTools Protocol（CDP）over WebSocket 远程控制运行在云端隔离容器中的浏览器实例，原生兼容 Puppeteer、Playwright 等主流自动化框架。

browser 模板对齐 E2B 浏览器自动化相关体验，提供 CDP、VNC、截图、页面交互等能力。

## 功能特性

| **特性** | **说明** |
| --- | --- |
| 浏览器自动化 | 内置 Chromium/Chrome 浏览器，支持完整 Web 标准，原生兼容 Puppeteer、Playwright 等自动化框架 |
| CDP 远程控制 | 通过标准 CDP 协议 over WebSocket 精准操控动态渲染页面（SPA），稳定维持登录态与 Session |
| VNC 实时可视化 | 内置 VNC 服务，支持通过 noVNC 客户端实时查看浏览器桌面环境，方便调试和监控 |
| 操作录制 | 支持 VNC 录制功能，可将浏览器操作过程录制为 MKV 视频文件，便于回放和审计 |
| 安全隔离 | 每个 browser 沙箱实例拥有独立的文件系统和进程空间 |
| 传输加密 | 所有数据面端点（CDP 和 VNC）均使用 WSS（WebSocket Secure）协议，全程加密 |

## 适用场景

| **场景** | **说明** |
| --- | --- |
| AI Agent 赋能 | 作为大模型的"眼睛"和"手"，赋予其执行网页浏览、信息提取、在线操作等复杂任务的能力 |
| 数据采集 | 稳定、高效地进行网页抓取，应对动态加载和反爬虫挑战 |
| 自动化测试 | 在云端按需运行端到端（E2E）测试和视觉回归测试，无需维护本地测试环境 |
| 内容生成 | 将动态网页或数据看板自动化生成为 PDF 或截图，用于制作报告和归档 |

## 默认配置

browser 模板的默认配置如下：

| **配置项** | **默认值** | **说明** |
| --- | --- | --- |
| 容器镜像 | `fc-e2b-registry.cn-beijing.cr.aliyuncs.com/runtime/browser:v0.0.36` | 预置 browser 镜像 |
| 默认端口 | 3000 | 沙箱服务监听端口 |
| CPU | 4 vCPU | 最低要求 |
| 内存 | 8192 MB | 最低要求 |
| 磁盘大小 | 10240 MB | 建议 10 GB 以获得充足的临时存储空间，函数计算将默认提供 |

## 快速入门

### 第一步：创建 browser 沙箱

1. 登录 [函数计算控制台](https://fcnext.console.aliyun.com/)。
2. 在**云沙箱**页签下选择**API Keys**, 生成API key。
3. 创建成功后，在服务详情页的**VNC 调试**标签页下**新建沙箱**，获取 CDP 连接端点。

您也可以通过 OpenAPI 或 SDK 进行创建。

browser 模板的完整用法分为两个阶段：先**构建模板**（从 browser 镜像固化出一个带名称的模板），再**运行模板**（创建沙箱、等待健康检查、通过 CDP 自动化并截图、校验 VNC）。下面分别给出 Python 与 Node.js 两种实现。

> **说明**：示例中的 `API_KEY` 需替换为您在控制台生成的 API Key，`API_URL` / `DOMAIN` 需替换为对应地域的接入地址。连接 CDP/VNC 端点时需在请求头中携带 `X-Access-Token` 进行身份验证：Python SDK 可通过内部属性 `sbx._envd_access_token` 获取（后续版本可能重命名或移除），JS SDK 可使用公开字段 `sbx.envdAccessToken`。

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
  "name": "browser-template-demo",
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

### 第三步：构建 browser 模板

从 browser 镜像构建一个带名称的模板，构建时指定 CPU 与内存规格（推荐 4 vCPU / 8192 MB）。

**Python**：

```python
"""browser 模板构建示例。"""

from e2b import Template, default_build_logger

API_KEY = "e2b_xxx"  # 替换为您的 API Key
API_URL = "https://api.cn-beijing.e2b.fc.aliyuncs.com"
DOMAIN = "cn-beijing.e2b.fc.aliyuncs.com"
FROM_IMAGE = "fc-e2b-registry.cn-beijing.cr.aliyuncs.com/runtime/browser:v0.0.36"
OPTS = {"api_key": API_KEY, "api_url": API_URL, "domain": DOMAIN}

TEMPLATE_NAME = "my-browser-template"

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
// browser 模板构建示例。
import { Template, defaultBuildLogger } from 'e2b';

const API_KEY = 'e2b_xxx'; // 替换为您的 API Key
const API_URL = 'https://api.cn-beijing.e2b.fc.aliyuncs.com';
const DOMAIN = 'cn-beijing.e2b.fc.aliyuncs.com';
const FROM_IMAGE =
  'fc-e2b-registry.cn-beijing.cr.aliyuncs.com/runtime/browser:v0.0.36';
const OPTS = { apiKey: API_KEY, apiUrl: API_URL, domain: DOMAIN };

const TPL_NAME = 'my-browser-template';

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

### 第四步：运行模板并执行自动化脚本

创建沙箱后，先轮询 `/health` 等待 browser 服务就绪，再通过 CDP 端点连接 Playwright 打开目标页并截图，最后校验 VNC（livestream）端点握手。

**Python**：

```python
"""browser 模板运行示例：创建沙箱 -> 等待健康检查 -> CDP 自动化 -> 截图 -> VNC 校验。"""

import time

from e2b_code_interpreter import Sandbox

API_KEY = "e2b_xxx"  # 替换为您的 API Key
API_URL = "https://api.cn-beijing.e2b.fc.aliyuncs.com"
DOMAIN = "cn-beijing.e2b.fc.aliyuncs.com"
OPTS = {"api_key": API_KEY, "api_url": API_URL, "domain": DOMAIN}

TEMPLATE_NAME = "my-browser-template"

BROWSERTOOL_PORT = 3000
TARGET_URL = "https://example.com"
SCREENSHOT_PATH = "browser-example.png"


def wait_until_healthy(sbx: Sandbox, host: str, token: str, timeout: int = 60) -> None:
    """轮询公网网关 /health 端点，直到 browser 服务就绪或超时。"""
    # 走公网网关 host（3000-<sandboxId>.<domain>），需带 X-Access-Token 头。
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
            print(f"  ✓ /health 就绪 (HTTP {code})")
            return
        print(f"  ...等待 browser 服务就绪 (HTTP {code!r})")
        time.sleep(2)
    raise TimeoutError(f"browser 服务在 {timeout}s 内未就绪")


def verify_vnc_handshake(sbx: Sandbox, host: str, token: str) -> None:
    """探测公网网关 /ws/livestream 的 WebSocket 握手，返回 101 即视为 VNC 就绪。"""
    # 升级成功后连接会保持为 WebSocket，curl 会一直读到 -m 超时（退出码 28），
    # 这属于预期行为，用 `|| true` 吞掉退出码，只解析已收到的响应头。
    # 走公网网关 host（3000-<sandboxId>.<domain>），需带 X-Access-Token 头。
    token_header = f"-H 'X-Access-Token: {token}' " if token else ""
    cmd = (
        "curl -sS -i -m 4 "
        "-H 'Connection: Upgrade' "
        "-H 'Upgrade: websocket' "
        "-H 'Sec-WebSocket-Version: 13' "
        "-H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' "
        "{token_header}"
        "https://{host}/ws/livestream || true"
    ).format(token_header=token_header, host=host)
    result = sbx.commands.run(cmd, timeout=15)
    out = "".join(result.stdout or [])
    status_line = out.splitlines()[0].strip() if out.strip() else "<无响应>"
    print(f"  /ws/livestream 响应: {status_line!r}")
    assert "101" in out and "Switching Protocols" in out, (
        f"VNC 端点未能升级为 WebSocket: {out[:200]!r}"
    )
    print("  ✓ VNC (livestream) 端点握手通过")


def verify_with_playwright(cdp_ws_url: str, headers: dict) -> None:
    """通过 CDP 连接 browsertool，打开目标页并校验 title，同时截图。"""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(cdp_ws_url, headers=headers)
        # 复用 browsertool 已 launch 的默认 context
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.new_page()
        try:
            page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)
            title = page.title()
            print(f"  page.title() = {title!r}")
            assert "Example" in title, f"unexpected title: {title!r}"

            page.screenshot(path=SCREENSHOT_PATH, full_page=True)
            print(f"  ✓ 截图已保存: {SCREENSHOT_PATH}")
            print("  ✓ Playwright over CDP 验证通过")
        finally:
            page.close()
            browser.close()


sbx = None
try:
    sbx = Sandbox.create(template=TEMPLATE_NAME, timeout=900, **OPTS)
    print(f"sandbox_id: {sbx.sandbox_id}")

    host = sbx.get_host(BROWSERTOOL_PORT)
    cdp_ws_url = f"wss://{host}/ws/automation"
    vnc_ws_url = f"wss://{host}/ws/livestream"
    # e2b 公网网关要求 X-Access-Token 头，否则请求/WS 升级 403
    token = sbx._envd_access_token
    print("\n--- WebSocket 端点 ---")
    print(f"  host: {host}")
    print(f"  CDP : {cdp_ws_url}")
    print(f"  VNC : {vnc_ws_url}")

    print("\n--- 等待健康检查 ---")
    wait_until_healthy(sbx, host, token)

    print("\n--- Playwright CDP 用例 ---")
    headers = {}
    if token:
        headers["X-Access-Token"] = token
    verify_with_playwright(cdp_ws_url, headers)

    print("\n--- VNC livestream 用例 ---")
    verify_vnc_handshake(sbx, host, token)
finally:
    if sbx is not None:
        sbx.kill()
        print("\n沙箱已销毁")
```

**Node.js**：

```javascript
// browser 模板运行示例：创建沙箱 -> 等待健康检查 -> CDP 自动化 -> 截图 -> VNC 校验。
import { Sandbox } from '@e2b/code-interpreter';
import { chromium } from 'playwright-core';

const API_KEY = 'e2b_xxx'; // 替换为您的 API Key
const API_URL = 'https://api.cn-beijing.e2b.fc.aliyuncs.com';
const DOMAIN = 'cn-beijing.e2b.fc.aliyuncs.com';
const OPTS = { apiKey: API_KEY, apiUrl: API_URL, domain: DOMAIN };

const TPL_NAME = 'my-browser-template';

const BROWSERTOOL_PORT = 3000;
const TARGET_URL = 'https://example.com';
const SCREENSHOT_PATH = 'browser-example.png';

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

/** 轮询公网网关 /health 端点，直到 browser 服务就绪或超时。 */
async function waitUntilHealthy(sbx, host, token, timeout = 60) {
  // 走公网网关 host（3000-<sandboxId>.<domain>），需带 X-Access-Token 头。
  const tokenHeader = token ? `-H 'X-Access-Token: ${token}' ` : '';
  const deadline = Date.now() + timeout * 1000;
  while (Date.now() < deadline) {
    // 服务未起时 curl 会以非 0 退出（连接失败），e2b 会抛 CommandExitError，
    // 该异常同样携带 stdout，捕获后按未就绪处理继续轮询。
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
      console.log(`  ✓ /health 就绪 (HTTP ${code})`);
      return;
    }
    console.log(`  ...等待 browser 服务就绪 (HTTP ${JSON.stringify(code)})`);
    await sleep(2000);
  }
  throw new Error(`browser 服务在 ${timeout}s 内未就绪`);
}

/** 探测公网网关 /ws/livestream 的 WebSocket 握手，返回 101 即视为 VNC 就绪。 */
async function verifyVncHandshake(sbx, host, token) {
  // 升级成功后连接会保持为 WebSocket，curl 会一直读到 -m 超时（退出码 28），
  // 这属于预期行为，用 `|| true` 吞掉退出码，只解析已收到的响应头。
  // 走公网网关 host（3000-<sandboxId>.<domain>），需带 X-Access-Token 头。
  const tokenHeader = token ? `-H 'X-Access-Token: ${token}' ` : '';
  const cmd =
    `curl -sS -i -m 4 ` +
    `-H 'Connection: Upgrade' ` +
    `-H 'Upgrade: websocket' ` +
    `-H 'Sec-WebSocket-Version: 13' ` +
    `-H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' ` +
    tokenHeader +
    `https://${host}/ws/livestream || true`;
  const result = await sbx.commands.run(cmd, { timeoutMs: 15_000 });
  const out = result.stdout || '';
  const statusLine = out.trim() ? out.split('\n')[0].trim() : '<无响应>';
  console.log(`  /ws/livestream 响应: ${JSON.stringify(statusLine)}`);
  if (!(out.includes('101') && out.includes('Switching Protocols'))) {
    throw new Error(`VNC 端点未能升级为 WebSocket: ${JSON.stringify(out.slice(0, 200))}`);
  }
  console.log('  ✓ VNC (livestream) 端点握手通过');
}

/** 通过 CDP 连接 browsertool，打开目标页并校验 title，同时截图。 */
async function verifyWithPlaywright(cdpWsUrl, headers) {
  const browser = await chromium.connectOverCDP(cdpWsUrl, { headers });
  // 复用 browsertool 已 launch 的默认 context
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
    console.log(`  ✓ 截图已保存: ${SCREENSHOT_PATH}`);
    console.log('  ✓ Playwright over CDP 验证通过');
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
    const vncWsUrl = `wss://${host}/ws/livestream`;
    // e2b 公网网关要求 X-Access-Token 头，否则请求/WS 升级 403
    const token = sbx.envdAccessToken;
    console.log('\n--- WebSocket 端点 ---');
    console.log(`  host: ${host}`);
    console.log(`  CDP : ${cdpWsUrl}`);
    console.log(`  VNC : ${vncWsUrl}`);

    console.log('\n--- 等待健康检查 ---');
    await waitUntilHealthy(sbx, host, token);

    console.log('\n--- Playwright CDP 用例 ---');
    const headers = {};
    if (token) {
      headers['X-Access-Token'] = token;
    }
    await verifyWithPlaywright(cdpWsUrl, headers);

    console.log('\n--- VNC livestream 用例 ---');
    await verifyVncHandshake(sbx, host, token);
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

browser 模板提供两个 WebSocket 端点，用于不同的自动化场景：

| **端点** | **路径** | **用途** |
| --- | --- | --- |
| 健康检查端点 | `https://<sandbox-host>/health` | 判断 browser 服务是否启动完成 |
| CDP 自动化端点 | `wss://<sandbox-host>/ws/automation` | 浏览器自动化，与 Puppeteer 和 Playwright 兼容 |
| VNC 实时流端点 | `wss://<sandbox-host>/ws/livestream` | 实时查看浏览器桌面环境，支持通过 noVNC 客户端查看 |

> **说明**：`<sandbox-host>` 通过 SDK 的 `sbx.get_host(3000)` 获取。所有端点均需在请求头中携带 `X-Access-Token` 进行身份验证。

在沙箱内部可以先探测 CDP WebSocket 握手是否正常。如果返回 `101 Switching Protocols`，说明 CDP 端点已经可升级为 WebSocket 连接：

```bash
curl -sS -m 4 -i \
  -H 'Connection: Upgrade' \
  -H 'Upgrade: websocket' \
  -H 'Sec-WebSocket-Version: 13' \
  -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' \
  http://localhost:3000/ws/automation
```

您可以使用 `wscat` 工具直接与 CDP 端点交互，发送原始 CDP 命令进行调试：

```bash
# 安装 wscat
npm install -g wscat

# 连接到 CDP 代理（host 通过 sbx.get_host(3000) 获取）
wscat -c "wss://<sandbox-host>/ws/automation" -H "X-Access-Token:<access-token>"

# 发送 CDP 命令
{"id":1,"method":"Runtime.evaluate","params":{"expression":"navigator.userAgent"}}
```

## VNC 实时查看

browser 模板支持通过 VNC 实时查看远程浏览器的桌面环境，方便在开发和调试阶段监控自动化任务的执行情况。

### 使用在线 noVNC 客户端

1. 访问 noVNC 官方提供的在线客户端：[https://novnc.com/noVNC/vnc.html](https://novnc.com/noVNC/vnc.html)
2. 在连接设置中，**高级** > **WebSocket** 中填入以下连接信息：
   - **主机**：通过 `sbx.get_host(3000)` 获取的 host 地址
   - **端口**：`443`
   - **路径**：`ws/livestream`
3. 点击**连接**，即可看到浏览器界面。

> **说明**：noVNC 连接同样需要通过 `X-Access-Token` 进行身份验证。

> **说明**
>
> 连接成功后，初始界面可能为黑屏或灰屏。这是正常现象，因为浏览器正在等待指令。当您的自动化脚本执行 `page.goto()` 等操作后，界面才会显示相应内容。

## 框架集成

以下示例聚焦框架接入方式。实际运行前，请先按快速入门中的流程创建 browser 沙箱，并获取 `cdp_url` 和 `X-Access-Token`。

### BrowserUse 集成

BrowserUse 是专门为 AI Agent 设计的浏览器自动化框架，通过 browser 模板可以在云端运行：

```python
import asyncio
from e2b import Sandbox
from browser_use import Agent, BrowserSession
from browser_use.llm import ChatDeepSeek
from browser_use.browser import BrowserProfile

BROWSER_SANDBOX_PORT = 3000

async def main():
    sbx = Sandbox.create(template="my-browser-template", api_key=E2B_API_KEY, timeout=600)
    host = sbx.get_host(BROWSER_SANDBOX_PORT)
    cdp_url = f"wss://{host}/ws/automation"

    browser_session = BrowserSession(
        cdp_url=cdp_url,
        browser_profile=BrowserProfile(
            headless=False,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            timeout=3000000,
            keep_alive=True,
        ),
        extra_headers={"X-Access-Token": sbx._envd_access_token},
    )

    llm = ChatDeepSeek(api_key="sk-your-deepseek-sk")

    agent = Agent(
        task="请访问 https://www.aliyun.com/product/list 并分析阿里云提供的产品分类",
        llm=llm,
        browser_session=browser_session,
        use_vision=True
    )
    result = await agent.run()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### LangChain 集成

通过 E2B SDK 可以将 browser 模板轻松集成到 LangChain Agent 中：

```python
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from e2b import Sandbox
from playwright.async_api import async_playwright

BROWSER_SANDBOX_PORT = 3000

# 创建沙箱并获取 CDP 端点
sbx = Sandbox.create(template="my-browser-template", api_key=E2B_API_KEY, timeout=600)
host = sbx.get_host(BROWSER_SANDBOX_PORT)
cdp_url = f"wss://{host}/ws/automation"
headers = {"X-Access-Token": sbx._envd_access_token}

@tool
def navigate_and_extract(url: str) -> str:
    """导航到指定 URL 并提取页面文本内容"""
    import asyncio
    async def _run():
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(cdp_url, headers=headers)
            page = browser.contexts[0].pages[0] if browser.contexts[0].pages else await browser.contexts[0].new_page()
            await page.goto(url, wait_until="networkidle")
            content = await page.content()
            return content[:5000]
    return asyncio.run(_run())

llm = ChatOpenAI(model="qwen-max", api_key="sk-your-key", base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

agent = create_react_agent(
    model=llm,
    tools=[navigate_and_extract],
)

async def run_agent():
    result = await agent.ainvoke({
        "messages": [
            HumanMessage(content="请访问新浪财经，查询腾讯控股今日的股价")
        ]
    })
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_agent())
```

## 使用限制

| **限制项** | **约束** |
| --- | --- |
| 浏览器支持 | 目前内置 Chromium/Chrome 浏览器 |

## 相关文档

- [沙箱模板概述](../02.内置模板.md)
- [创建沙箱](../../01.Sandbox/02.创建沙箱.md)
- [生命周期](../../01.Sandbox/01.生命周期.md)
- [base 模板](base-模板.md)（仅需 envd 基础能力时选择）
- [code-interpreter-v1 模板](code-interpreter-v1-模板.md)（仅需代码执行能力时选择）
- [All-In-One 模板](all-in-one-模板.md)（需要同时使用浏览器和代码执行能力时选择）
