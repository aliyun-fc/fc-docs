# 使用 Browser Use Sandbox

Browser Use Sandbox 面向需要访问网页、点击按钮、填写表单、截图归档或抓取动态页面的 Agent。如果已准备包含浏览器、字体和 Playwright/Puppeteer 依赖的 `browser` 模板，开发者可以直接用 E2B SDK 创建浏览器沙箱，把网页操作放进隔离、可回收、可审计的环境中执行。

这个实践适合网页数据采集、运营后台自动化、网页截图归档、页面巡检、轻量 E2E 测试和浏览器工具型 Agent。Agent 负责决定访问哪个页面、执行什么动作、如何解释结果；Browser Use Sandbox 负责运行浏览器、保存截图和下载文件、限制生命周期。

## 业务场景

- 从动态网页抓取数据，再交给代码执行器清洗和汇总。
- 自动填写网页表单、点击按钮、下载文件、生成截图或 PDF。
- 为营销、客服、运营 Agent 提供网页观察和操作能力。
- 在隔离环境中运行浏览器 E2E 测试，避免污染 CI Worker 或业务服务。

## 推荐流程

1. 使用已准备好的 `browser` 模板创建云沙箱。
2. 将任务 URL、动作参数和必要的短期凭证写入沙箱。
3. 在沙箱内运行 Playwright/Puppeteer 脚本。
4. 输出结构化结果，并将截图、HTML、PDF 或下载文件保存到任务目录。
5. 读取结果后释放沙箱。

## 示例代码

以下示例假设 `browser` 模板已预装 Playwright 和浏览器依赖，用于访问网页、提取标题和正文摘要，并保存截图。

```javascript
import { Sandbox } from "e2b";

const sandbox = await Sandbox.create("browser", {
  apiKey: process.env.E2B_API_KEY,
  apiUrl: process.env.E2B_API_URL,
  domain: process.env.E2B_DOMAIN,
  envs: { TASK_TYPE: "browser-use" },
  metadata: { scenario: "browser-use" },
  timeoutMs: 300_000,
});

try {
  await sandbox.files.makeDir("/tmp/browser-task");
  await sandbox.files.write(
    "/tmp/browser-task/task.json",
    JSON.stringify({
      url: "https://example.com",
      screenshotPath: "/tmp/browser-task/page.png",
    }),
  );

  await sandbox.files.write(
    "/tmp/browser-task/run-browser-task.mjs",
    `import fs from "node:fs/promises";
import { chromium } from "playwright";

const task = JSON.parse(await fs.readFile("task.json", "utf8"));
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1365, height: 768 } });

await page.goto(task.url, { waitUntil: "networkidle", timeout: 60_000 });
await page.screenshot({ path: task.screenshotPath, fullPage: true });

const result = await page.evaluate(() => ({
  title: document.title,
  text: document.body.innerText.replace(/\\s+/g, " ").slice(0, 500),
}));

await browser.close();
console.log(JSON.stringify(result));
`,
  );

  const result = await sandbox.commands.run("node run-browser-task.mjs", {
    cwd: "/tmp/browser-task",
    timeoutMs: 120_000,
  });

  if (result.exitCode !== 0) {
    throw new Error(result.stderr || result.stdout);
  }

  console.log(JSON.parse(result.stdout));
} finally {
  await sandbox.kill();
}
```

## 连接云端浏览器

Browser Sandbox 暴露标准 CDP 端点，可被 Playwright、Puppeteer、BrowserUse 等框架连接。常用端点如下：

| 端点 | 用途 |
| --- | --- |
| `/ws/automation` | 通过 CDP 控制云端浏览器 |
| `/ws/livestream` | 通过 VNC/livestream 观察浏览器画面 |

Python SDK 中可以通过 `sandbox.get_host(3000)` 获取 Browser Sandbox 的主机地址：

```python
import os
from e2b import Sandbox
from playwright.sync_api import sync_playwright

BROWSER_PORT = 3000

sandbox = Sandbox.create(
    template=os.getenv("BROWSER_TEMPLATE_NAME"),
    timeout=300,
    api_key=os.getenv("E2B_API_KEY"),
)

try:
    host = sandbox.get_host(BROWSER_PORT)
    cdp_url = f"wss://{host}/ws/automation"
    headers = {"X-Access-Token": sandbox._envd_access_token}

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(cdp_url, headers=headers)
        page = browser.contexts[0].pages[0]
        page.goto("https://example.com")
        page.screenshot(path="screenshot.png")
        browser.close()
finally:
    sandbox.kill()
```

## 集成 BrowserUse

BrowserUse 适合让多模态模型基于页面截图和 DOM 信息自主完成网页任务。BrowserUse 不需要在本地启动浏览器，只需要连接 Browser Sandbox 的 CDP 端点。

安装依赖：

```bash
pip install browser-use python-dotenv "e2b>=2.20.0"
```

示例：

```python
import asyncio
import os
from browser_use import Agent, BrowserSession, ChatOpenAI
from browser_use.browser import BrowserProfile
from e2b import Sandbox

BROWSER_PORT = 3000

async def main():
    sandbox = Sandbox.create(
        template=os.getenv("BROWSER_TEMPLATE_NAME"),
        timeout=3000,
        api_key=os.getenv("E2B_API_KEY"),
    )
    browser_session = None

    try:
        host = sandbox.get_host(BROWSER_PORT)
        cdp_url = f"wss://{host}/ws/automation"

        llm = ChatOpenAI(
            model="qwen-vl-max",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

        browser_session = BrowserSession(
            cdp_url=cdp_url,
            browser_profile=BrowserProfile(
                headless=False,
                timeout=300000,
                keep_alive=True,
            ),
        )

        agent = Agent(
            task="访问阿里云官网并总结主要产品分类",
            llm=llm,
            browser_session=browser_session,
            use_vision=True,
        )

        result = await agent.run()
        print(result.final_result())
    finally:
        if browser_session is not None:
            await browser_session.stop()
        sandbox.kill()

asyncio.run(main())
```

BrowserUse 集成建议：

- 对复杂页面启用 `use_vision=True`，让模型结合截图理解页面。
- 多步骤任务复用同一个 `BrowserSession`，减少连接和页面状态重建。
- 开发调试时打开 VNC/livestream 观察 Agent 行为；生产环境保留截图和关键 DOM 摘要。
- 对外部网站设置总超时、单步超时和最大循环轮数，避免 Agent 长时间停留。

## 集成 LangChain Agent

LangChain 集成时，建议把 Browser Sandbox 封装成受控工具，而不是让模型直接拼接任意脚本。工具层负责创建沙箱、导航、截图和销毁，模型只选择工具并传入经过校验的参数。

示例工具结构：

```python
import os
from typing import Any
from e2b import Sandbox
from langchain.tools import tool
from playwright.sync_api import sync_playwright

BROWSER_PORT = 3000
_sandbox: Sandbox | None = None

@tool
def create_browser_sandbox(template_name: str = "") -> str:
    """创建 Browser Sandbox，并返回可审计的沙箱 ID。"""
    global _sandbox
    if _sandbox is None:
        _sandbox = Sandbox.create(
            template=template_name or os.getenv("BROWSER_TEMPLATE_NAME"),
            timeout=1800,
            api_key=os.getenv("E2B_API_KEY"),
        )
    return f"Sandbox created: {_sandbox.sandbox_id}"

@tool
def navigate_to_url(url: str) -> str:
    """在 Browser Sandbox 中访问指定 URL，并返回页面标题。"""
    if _sandbox is None:
        raise RuntimeError("create_browser_sandbox must be called first")
    if not url.startswith(("http://", "https://")):
        raise ValueError("url must start with http:// or https://")

    host = _sandbox.get_host(BROWSER_PORT)
    cdp_url = f"wss://{host}/ws/automation"
    headers = {"X-Access-Token": _sandbox._envd_access_token}

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(cdp_url, headers=headers)
        page = browser.contexts[0].pages[0]
        page.goto(url, wait_until="load", timeout=30000)
        title = page.title()
        browser.close()
    return title

@tool
def destroy_browser_sandbox() -> str:
    """释放 Browser Sandbox。"""
    global _sandbox
    if _sandbox is not None:
        sandbox_id = _sandbox.sandbox_id
        _sandbox.kill()
        _sandbox = None
        return f"Sandbox destroyed: {sandbox_id}"
    return "No active sandbox"
```

上线时应把工具注册表、参数 schema、权限判断和审计记录放在业务编排层。对于高风险动作，例如登录后台、提交表单、下载敏感文件或写入外部系统，应增加人工确认或策略引擎。

## 生命周期策略

不同场景可以采用不同的 Browser Sandbox 管理方式：

| 管理方式 | 适用场景 | 注意事项 |
| --- | --- | --- |
| 单任务单沙箱 | 一次性抓取、测试、截图 | 隔离性最好，创建成本较高 |
| 会话级复用 | 多轮对话、需要登录态的任务 | 需要清理 Cookie、下载文件和临时凭证 |
| 连接池 | 高并发生产服务 | 需要健康检查、最大复用次数和池容量控制 |

无论采用哪种方式，都应在 `finally` 或任务收尾逻辑中释放不再使用的沙箱，并记录 Sandbox ID、URL、截图路径、工具调用轨迹和错误摘要。

## 上线建议

- 浏览器任务默认处理不可信网页，必须限制可访问域名、下载文件类型和输出大小。
- 页面内容可能包含 prompt injection，不要让 Agent 未经校验地执行网页中的指令。
- 登录态、Cookie、账号凭证应按任务隔离，通过运行时注入，不写入模板。
- 对外部网页操作要记录 URL、截图、关键 DOM 摘要、工具调用轨迹和结果文件。
- 如果任务需要在浏览器操作后继续运行 Python/Node 脚本处理数据，优先使用 [AIO Sandbox](./使用%20AIO%20Sandbox.md)。
- 生产服务应设置总任务超时、单步操作超时、重试次数和最大页面数。
- 不把模型输出直接拼接成 Shell 命令或浏览器脚本；需要动态执行时先进入审核、模板化或白名单流程。

## 相关功能

- [构建模板](../功能说明/Templates/构建模板.md)
- [后台命令](../功能说明/Commands/后台命令.md)
- [上传和下载文件](../功能说明/Filesystem/上传和下载文件.md)
- [预装 Agent 环境](./预装%20Agent%20环境.md)
