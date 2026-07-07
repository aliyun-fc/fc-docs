# Browser Template

The browser template provides a cloud-native browser runtime. It lets you remotely control a browser instance running in an isolated cloud container over the standard Chrome DevTools Protocol (CDP) over WebSocket, with native compatibility for mainstream automation frameworks such as Puppeteer and Playwright.

The browser template aligns with the E2B browser automation experience and offers CDP, VNC, screenshots, page interaction, and more.

## Features

| **Feature** | **Description** |
| --- | --- |
| Browser automation | Ships with Chromium/Chrome, supports full web standards, natively compatible with Puppeteer, Playwright, and other automation frameworks |
| CDP remote control | Precisely drive dynamically rendered pages (SPAs) over the standard CDP protocol over WebSocket, while reliably maintaining login state and sessions |
| Real-time VNC | Built-in VNC service lets you view the browser desktop in real time through a noVNC client, making debugging and monitoring easy |
| Session recording | Supports VNC recording to capture the browser session as an MKV video file for playback and auditing |
| Secure isolation | Each browser sandbox instance has its own file system and process space |
| Encrypted transport | All data-plane endpoints (CDP and VNC) use the WSS (WebSocket Secure) protocol, encrypted end to end |

## Use cases

| **Scenario** | **Description** |
| --- | --- |
| AI Agent enablement | Acts as the "eyes" and "hands" of an LLM, giving it the ability to browse the web, extract information, perform online actions, and other complex tasks |
| Data collection | Stable, efficient web scraping that copes with dynamic loading and anti-bot challenges |
| Automated testing | Run end-to-end (E2E) and visual regression tests on demand in the cloud, without maintaining a local test environment |
| Content generation | Automatically turn dynamic web pages or dashboards into PDFs or screenshots for reports and archiving |

## Default configuration

The default configuration of the browser template is as follows:

| **Item** | **Default** | **Description** |
| --- | --- | --- |
| Container image | `fc-e2b-registry.cn-beijing.cr.aliyuncs.com/runtime/browser:v0.0.36` | Prebuilt browser image |
| Default port | 3000 | Port the sandbox service listens on |
| CPU | 4 vCPU | Minimum requirement |
| Memory | 8192 MB | Minimum requirement |
| Disk size | 10240 MB | 10 GB is recommended for sufficient temporary storage; Function Compute provides it by default |

## Quickstart

### Step 1: Create a browser sandbox

1. Log in to the [Function Compute console](https://fcnext.console.aliyun.com/).
2. On the **FC Agent Sandbox** tab, choose **API Keys** and generate an API key.
3. After creation, on the service details page open the **VNC Debug** tab and choose **New Sandbox** to obtain the CDP connection endpoint.

You can also create it through the OpenAPI or an SDK.

The full workflow for the browser template has two phases: first **build the template** (materialize a named template from the browser image), then **run the template** (create a sandbox, wait for the health check, automate over CDP and take a screenshot, and verify VNC). The Python and Node.js implementations are shown below.

> **Note**: Replace `API_KEY` in the examples with the API key you generated in the console, and replace `API_URL` / `DOMAIN` with the endpoint of the corresponding region. When you connect to the CDP/VNC endpoints, you must include the `X-Access-Token` header for authentication: the Python SDK exposes it through the internal attribute `sbx._envd_access_token` (which may be renamed or removed in future versions), and the JS SDK exposes the public field `sbx.envdAccessToken`.

### Step 2: Prepare the local environment

**Python**:

```bash
uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install e2b e2b-code-interpreter 'playwright>=1.49.0'
playwright install chromium
```

**Node.js**: use the following `package.json`, then run `npm install`.

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

### Step 3: Build the browser template

Build a named template from the browser image, specifying the CPU and memory (4 vCPU / 8192 MB recommended) at build time.

**Python**:

```python
"""Browser template build example."""

from e2b import Template, default_build_logger

API_KEY = "e2b_xxx"  # Replace with your API key
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

**Node.js**:

```javascript
// Browser template build example.
import { Template, defaultBuildLogger } from 'e2b';

const API_KEY = 'e2b_xxx'; // Replace with your API key
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

### Step 4: Run the template and execute an automation script

After creating the sandbox, first poll `/health` to wait for the browser service to become ready, then connect Playwright over the CDP endpoint to open the target page and take a screenshot, and finally verify the VNC (livestream) endpoint handshake.

**Python**:

```python
"""Browser template run example: create sandbox -> wait for health check -> CDP automation -> screenshot -> VNC check."""

import time

from e2b_code_interpreter import Sandbox

API_KEY = "e2b_xxx"  # Replace with your API key
API_URL = "https://api.cn-beijing.e2b.fc.aliyuncs.com"
DOMAIN = "cn-beijing.e2b.fc.aliyuncs.com"
OPTS = {"api_key": API_KEY, "api_url": API_URL, "domain": DOMAIN}

TEMPLATE_NAME = "my-browser-template"

BROWSERTOOL_PORT = 3000
TARGET_URL = "https://example.com"
SCREENSHOT_PATH = "browser-example.png"


def wait_until_healthy(sbx: Sandbox, host: str, token: str, timeout: int = 60) -> None:
    """Poll the public gateway /health endpoint until the browser service is ready or times out."""
    # Go through the public gateway host (3000-<sandboxId>.<domain>); the X-Access-Token header is required.
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
            print(f"  ✓ /health ready (HTTP {code})")
            return
        print(f"  ...waiting for the browser service (HTTP {code!r})")
        time.sleep(2)
    raise TimeoutError(f"browser service not ready within {timeout}s")


def verify_vnc_handshake(sbx: Sandbox, host: str, token: str) -> None:
    """Probe the public gateway /ws/livestream WebSocket handshake; a 101 response means VNC is ready."""
    # After a successful upgrade the connection stays a WebSocket, so curl keeps reading until the -m
    # timeout (exit code 28). This is expected: swallow the exit code with `|| true` and only parse the
    # response headers already received.
    # Go through the public gateway host (3000-<sandboxId>.<domain>); the X-Access-Token header is required.
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
    status_line = out.splitlines()[0].strip() if out.strip() else "<no response>"
    print(f"  /ws/livestream response: {status_line!r}")
    assert "101" in out and "Switching Protocols" in out, (
        f"VNC endpoint failed to upgrade to WebSocket: {out[:200]!r}"
    )
    print("  ✓ VNC (livestream) endpoint handshake passed")


def verify_with_playwright(cdp_ws_url: str, headers: dict) -> None:
    """Connect to browsertool over CDP, open the target page and validate the title, then take a screenshot."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(cdp_ws_url, headers=headers)
        # Reuse the default context that browsertool already launched
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.new_page()
        try:
            page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)
            title = page.title()
            print(f"  page.title() = {title!r}")
            assert "Example" in title, f"unexpected title: {title!r}"

            page.screenshot(path=SCREENSHOT_PATH, full_page=True)
            print(f"  ✓ Screenshot saved: {SCREENSHOT_PATH}")
            print("  ✓ Playwright over CDP verification passed")
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
    # The e2b public gateway requires the X-Access-Token header, otherwise requests/WS upgrades return 403
    token = sbx._envd_access_token
    print("\n--- WebSocket endpoints ---")
    print(f"  host: {host}")
    print(f"  CDP : {cdp_ws_url}")
    print(f"  VNC : {vnc_ws_url}")

    print("\n--- Waiting for health check ---")
    wait_until_healthy(sbx, host, token)

    print("\n--- Playwright CDP case ---")
    headers = {}
    if token:
        headers["X-Access-Token"] = token
    verify_with_playwright(cdp_ws_url, headers)

    print("\n--- VNC livestream case ---")
    verify_vnc_handshake(sbx, host, token)
finally:
    if sbx is not None:
        sbx.kill()
        print("\nSandbox destroyed")
```

**Node.js**:

```javascript
// Browser template run example: create sandbox -> wait for health check -> CDP automation -> screenshot -> VNC check.
import { Sandbox } from '@e2b/code-interpreter';
import { chromium } from 'playwright-core';

const API_KEY = 'e2b_xxx'; // Replace with your API key
const API_URL = 'https://api.cn-beijing.e2b.fc.aliyuncs.com';
const DOMAIN = 'cn-beijing.e2b.fc.aliyuncs.com';
const OPTS = { apiKey: API_KEY, apiUrl: API_URL, domain: DOMAIN };

const TPL_NAME = 'my-browser-template';

const BROWSERTOOL_PORT = 3000;
const TARGET_URL = 'https://example.com';
const SCREENSHOT_PATH = 'browser-example.png';

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

/** Poll the public gateway /health endpoint until the browser service is ready or times out. */
async function waitUntilHealthy(sbx, host, token, timeout = 60) {
  // Go through the public gateway host (3000-<sandboxId>.<domain>); the X-Access-Token header is required.
  const tokenHeader = token ? `-H 'X-Access-Token: ${token}' ` : '';
  const deadline = Date.now() + timeout * 1000;
  while (Date.now() < deadline) {
    // While the service is down, curl exits non-zero (connection failure) and e2b throws a
    // CommandExitError. That exception also carries stdout, so catch it and treat it as not ready.
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
      console.log(`  ✓ /health ready (HTTP ${code})`);
      return;
    }
    console.log(`  ...waiting for the browser service (HTTP ${JSON.stringify(code)})`);
    await sleep(2000);
  }
  throw new Error(`browser service not ready within ${timeout}s`);
}

/** Probe the public gateway /ws/livestream WebSocket handshake; a 101 response means VNC is ready. */
async function verifyVncHandshake(sbx, host, token) {
  // After a successful upgrade the connection stays a WebSocket, so curl keeps reading until the -m
  // timeout (exit code 28). This is expected: swallow the exit code with `|| true` and only parse the
  // response headers already received.
  // Go through the public gateway host (3000-<sandboxId>.<domain>); the X-Access-Token header is required.
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
  const statusLine = out.trim() ? out.split('\n')[0].trim() : '<no response>';
  console.log(`  /ws/livestream response: ${JSON.stringify(statusLine)}`);
  if (!(out.includes('101') && out.includes('Switching Protocols'))) {
    throw new Error(`VNC endpoint failed to upgrade to WebSocket: ${JSON.stringify(out.slice(0, 200))}`);
  }
  console.log('  ✓ VNC (livestream) endpoint handshake passed');
}

/** Connect to browsertool over CDP, open the target page and validate the title, then take a screenshot. */
async function verifyWithPlaywright(cdpWsUrl, headers) {
  const browser = await chromium.connectOverCDP(cdpWsUrl, { headers });
  // Reuse the default context that browsertool already launched
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
    console.log(`  ✓ Screenshot saved: ${SCREENSHOT_PATH}`);
    console.log('  ✓ Playwright over CDP verification passed');
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
    // The e2b public gateway requires the X-Access-Token header, otherwise requests/WS upgrades return 403
    const token = sbx.envdAccessToken;
    console.log('\n--- WebSocket endpoints ---');
    console.log(`  host: ${host}`);
    console.log(`  CDP : ${cdpWsUrl}`);
    console.log(`  VNC : ${vncWsUrl}`);

    console.log('\n--- Waiting for health check ---');
    await waitUntilHealthy(sbx, host, token);

    console.log('\n--- Playwright CDP case ---');
    const headers = {};
    if (token) {
      headers['X-Access-Token'] = token;
    }
    await verifyWithPlaywright(cdpWsUrl, headers);

    console.log('\n--- VNC livestream case ---');
    await verifyVncHandshake(sbx, host, token);
  } finally {
    if (sbx !== null) {
      await sbx.kill();
      console.log('\nSandbox destroyed');
    }
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
```

## WebSocket endpoints

The browser template provides two WebSocket endpoints for different automation scenarios:

| **Endpoint** | **Path** | **Purpose** |
| --- | --- | --- |
| Health check endpoint | `https://<sandbox-host>/health` | Determine whether the browser service has finished starting |
| CDP automation endpoint | `wss://<sandbox-host>/ws/automation` | Browser automation, compatible with Puppeteer and Playwright |
| VNC livestream endpoint | `wss://<sandbox-host>/ws/livestream` | View the browser desktop in real time, viewable through a noVNC client |

> **Note**: `<sandbox-host>` is obtained through the SDK's `sbx.get_host(3000)`. All endpoints require the `X-Access-Token` header for authentication.

Inside the sandbox you can first probe whether the CDP WebSocket handshake works. A `101 Switching Protocols` response means the CDP endpoint can be upgraded to a WebSocket connection:

```bash
curl -sS -m 4 -i \
  -H 'Connection: Upgrade' \
  -H 'Upgrade: websocket' \
  -H 'Sec-WebSocket-Version: 13' \
  -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' \
  http://localhost:3000/ws/automation
```

You can use the `wscat` tool to interact with the CDP endpoint directly and send raw CDP commands for debugging:

```bash
# Install wscat
npm install -g wscat

# Connect to the CDP proxy (host is obtained through sbx.get_host(3000))
wscat -c "wss://<sandbox-host>/ws/automation" -H "X-Access-Token:<access-token>"

# Send a CDP command
{"id":1,"method":"Runtime.evaluate","params":{"expression":"navigator.userAgent"}}
```

## Real-time VNC viewing

The browser template supports viewing the remote browser desktop in real time through VNC, which makes it easy to monitor automation tasks during development and debugging.

### Use the online noVNC client

1. Open the online client provided by noVNC: [https://novnc.com/noVNC/vnc.html](https://novnc.com/noVNC/vnc.html)
2. In the connection settings, under **Advanced** > **WebSocket**, fill in the following:
   - **Host**: the host address obtained through `sbx.get_host(3000)`
   - **Port**: `443`
   - **Path**: `ws/livestream`
3. Click **Connect** to see the browser interface.

> **Note**: The noVNC connection also requires authentication through `X-Access-Token`.

> **Note**
>
> After connecting, the initial screen may be black or gray. This is normal because the browser is waiting for instructions. Once your automation script runs `page.goto()` or similar operations, the interface will display the corresponding content.

## Framework integration

The following examples focus on how to integrate frameworks. Before running them, follow the quickstart to create a browser sandbox and obtain the `cdp_url` and `X-Access-Token`.

### BrowserUse integration

BrowserUse is a browser automation framework designed specifically for AI Agents, and can run in the cloud through the browser template:

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
        task="Visit https://www.aliyun.com/product/list and analyze the product categories Alibaba Cloud offers",
        llm=llm,
        browser_session=browser_session,
        use_vision=True
    )
    result = await agent.run()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### LangChain integration

Using the E2B SDK, you can easily integrate the browser template into a LangChain Agent:

```python
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from e2b import Sandbox
from playwright.async_api import async_playwright

BROWSER_SANDBOX_PORT = 3000

# Create the sandbox and obtain the CDP endpoint
sbx = Sandbox.create(template="my-browser-template", api_key=E2B_API_KEY, timeout=600)
host = sbx.get_host(BROWSER_SANDBOX_PORT)
cdp_url = f"wss://{host}/ws/automation"
headers = {"X-Access-Token": sbx._envd_access_token}

@tool
def navigate_and_extract(url: str) -> str:
    """Navigate to the given URL and extract the page's text content"""
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
            HumanMessage(content="Visit Sina Finance and look up today's stock price of Tencent Holdings")
        ]
    })
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_agent())
```

## Limitations

| **Item** | **Constraint** |
| --- | --- |
| Session lifetime | A single sandbox session lasts at most 6 hours by default, after which it is automatically destroyed |
| Idle timeout | Configurable through the `sandboxIdleTimeoutSeconds` parameter; the sandbox terminates early after being idle for the specified time |
| Browser support | Currently ships with Chromium/Chrome |
| Code interpreter | The browser template includes E2B envd-compatible base capabilities but does not provide the Code Interpreter service; you cannot execute Python directly through a Code Interpreter context |

## Related documents

- [Built-in Templates](../02.Built-in%20Templates.md)
- [Build Custom Image Templates](../03.Build%20Custom%20Image%20Templates.md)
