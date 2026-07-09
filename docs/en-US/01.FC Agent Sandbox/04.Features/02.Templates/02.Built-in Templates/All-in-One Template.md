# All-In-One Template

The All-In-One template combines the browser template and the code-interpreter-v1 template in one isolated cloud execution environment. An All-In-One sandbox can drive a cloud browser over CDP/VNC and, in the same sandbox, execute Python/JavaScript code, process files, and run terminal commands. It is suitable for AI Agent scenarios that need browser automation and code execution to work together.

The All-In-One template aligns with the E2B experience of using browser automation and Code Interpreter together.

## Features

| **Feature** | **Description** |
| --- | --- |
| Browser automation | Ships with Chromium/Chrome, supports CDP over WebSocket, and is compatible with Puppeteer, Playwright, BrowserUse, and other automation frameworks |
| Real-time VNC | Built-in VNC service lets you view the browser desktop in real time through a noVNC client, making debugging and monitoring easy |
| Code execution | Integrates Code Interpreter capabilities, including Python/JavaScript execution, persistent contexts, and result output |
| File system operations | Supports file APIs such as upload, download, read, write, and directory management, so browser-collected data can be processed by code |
| Terminal commands | Supports synchronous command execution and an interactive WebSocket terminal (TTY) |
| Coordinated execution | Complete workflows such as "browser visits a dynamic page -> code parses/analyzes data -> files are exported" in one sandbox session |
| Secure isolation | Each All-In-One sandbox instance has its own file system, browser instance, and process space |

## Use cases

| **Scenario** | **Description** |
| --- | --- |
| AI Agent composite tasks | Drive the browser for page interaction and run code for data analysis, reasoning support, or file processing in the same session |
| Data collection and processing | Use the browser to scrape dynamic pages, take screenshots, or download files, then use Python scripts to parse, clean, summarize, and export the results |
| Automated testing | Run browser E2E tests, backend scripts, log analysis, and report generation in one isolated container |
| Content generation and archiving | Generate screenshots, PDFs, recordings, or structured data, then download the results through the file APIs |

## Default configuration

The default configuration of the All-In-One template is as follows:

| **Item** | **Default** | **Description** |
| --- | --- | --- |
| Container image | `fc-e2b-registry.ap-southeast-1.cr.aliyuncs.com/runtime/all-in-one:v0.0.36` | Prebuilt All-In-One sandbox image |
| Browser port | 3000 | Port for the browser service, including `/health`, CDP, and VNC |
| Code execution port | 5000 | Port for the Code Interpreter/envd service |
| CPU | 4 vCPU | Recommended spec because the sandbox runs both the browser and code execution environment |
| Memory | 8192 MB | Recommended spec |
| Disk size | 10240 MB | 10 GB is recommended for browser cache, screenshots, downloaded files, and code execution results |

> **Note**
>
> The All-In-One template uses higher CPU and memory specs than the code-interpreter-v1 template and the browser template because it must run both the browser runtime and the code execution environment. The example image is in the Singapore region (`ap-southeast-1`), so build and run the template with an API URL and domain from the same region.

## Difference from the browser template

The browser template provides a browser runtime and exposes CDP and VNC through port 3000 by default. It suits browser automation tasks such as web access, page interaction, screenshots, data collection, and UI testing. It includes E2B envd-compatible base capabilities but does not provide the Code Interpreter service, so you cannot execute Python directly through a Code Interpreter context.

The All-In-One template layers the Code Interpreter service on top of the browser capabilities. It uses port 3000 as the browser entry and port 5000 as the code execution and file management entry by default. It can execute Python directly in the same sandbox session, enabling composite flows such as "browser scrapes a dynamic page -> Python parses/cleans/analyzes -> files are exported."

| **Comparison** | **Browser template** | **All-In-One template** |
| --- | --- | --- |
| Core positioning | Lightweight browser automation environment | Integrated browser automation + code execution environment |
| Browser capabilities | Supports CDP, VNC, screenshots, and page interaction | Supports CDP, VNC, screenshots, and page interaction |
| Code Interpreter service | Not supported | Supported |
| Code execution | Cannot execute Python through Code Interpreter | Supports Python/JavaScript code execution |
| File processing | Supports basic file access, no Code Interpreter file API | Supports file APIs plus in-context read/write and processing |
| Typical entries | 3000 (browser entry) | 3000 (browser entry) / 5000 (code entry) |
| Recommended spec | 4 vCPU / 8192 MB / 10240 MB disk | 4 vCPU / 8192 MB / 10240 MB disk |
| Recommended for | Only browser automation is needed | Browser automation and code execution need to work together |

## Quickstart

The full workflow for the All-In-One template has two phases: first **build the template** (materialize a named template from the All-In-One image), then **run the template** (create a sandbox, wait for the browser health check, automate over CDP and take a screenshot, and execute code through Code Interpreter). The Python and Node.js implementations are shown below.

> **Note**: Replace `API_KEY` in the examples with the API key you generated in the console, and replace `API_URL` / `DOMAIN` with the endpoint of the corresponding region. When you connect to the CDP/VNC endpoints, you must include the `X-Access-Token` header for authentication: the Python SDK exposes it through the internal attribute `sbx._envd_access_token` (which may be renamed or removed in future versions), and the JS SDK exposes the public field `sbx.envdAccessToken`.

### Step 1: Create an API key

1. Log in to the [Function Compute console](https://fcnext.console.aliyun.com/).
2. On the **FC Agent Sandbox** tab, choose **API Keys** and generate an API key.
3. Use the API key and API endpoint through an SDK to build the template and create a sandbox.

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

### Step 3: Build the All-In-One template

Build a named template from the All-In-One image, specifying the CPU and memory (4 vCPU / 8192 MB recommended) at build time.

**Python**:

```python
"""All-In-One template build example."""

from e2b import Template, default_build_logger

API_KEY = "e2b_xxx"  # Replace with your API key
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

**Node.js**:

```javascript
// All-In-One template build example.
import { Template, defaultBuildLogger } from 'e2b';

const API_KEY = 'e2b_xxx'; // Replace with your API key
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

### Step 4: Run the template and verify the combined capabilities

After creating the sandbox, first poll `/health` until the browser service is ready, connect Playwright over the CDP endpoint to open the target page and take a screenshot, and then execute a Python snippet through Code Interpreter to verify code execution.

**Python**:

```python
"""All-In-One template run example: create sandbox -> CDP automation -> Code Interpreter code execution."""

import time

from e2b_code_interpreter import Sandbox

API_KEY = "e2b_xxx"  # Replace with your API key
API_URL = "https://api.ap-southeast-1.e2b.fc.aliyuncs.com"
DOMAIN = "ap-southeast-1.e2b.fc.aliyuncs.com"
OPTS = {"api_key": API_KEY, "api_url": API_URL, "domain": DOMAIN}

TEMPLATE_NAME = "my-all-in-one-template"

BROWSERTOOL_PORT = 3000
TARGET_URL = "https://example.com"
SCREENSHOT_PATH = "all-in-one-example.png"


def wait_until_healthy(sbx: Sandbox, host: str, token: str, timeout: int = 60) -> None:
    """Poll the public gateway /health endpoint until the browser service is ready or times out."""
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
            print(f"  /health ready (HTTP {code})")
            return
        print(f"  ...waiting for the browser service (HTTP {code!r})")
        time.sleep(2)
    raise TimeoutError(f"browser service not ready within {timeout}s")


def verify_with_playwright(cdp_ws_url: str, headers: dict) -> None:
    """Connect to browsertool over CDP, open the target page, and take a screenshot."""
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
            print(f"  Screenshot saved: {SCREENSHOT_PATH}")
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

    print("\n--- Waiting for browser health check ---")
    wait_until_healthy(sbx, host, token)

    print("\n--- Playwright CDP case ---")
    verify_with_playwright(cdp_ws_url, headers)

    print("\n--- Code Interpreter case ---")
    execution = sbx.run_code(
        "import json\n"
        "result = {'status': 'ok', 'source': 'all-in-one'}\n"
        "print(json.dumps(result, ensure_ascii=False))"
    )
    print(execution.logs.stdout)
finally:
    if sbx is not None:
        sbx.kill()
        print("\nSandbox destroyed")
```

**Node.js**:

```javascript
// All-In-One template run example: create sandbox -> CDP automation -> Code Interpreter code execution.
import { Sandbox } from '@e2b/code-interpreter';
import { chromium } from 'playwright-core';

const API_KEY = 'e2b_xxx'; // Replace with your API key
const API_URL = 'https://api.ap-southeast-1.e2b.fc.aliyuncs.com';
const DOMAIN = 'ap-southeast-1.e2b.fc.aliyuncs.com';
const OPTS = { apiKey: API_KEY, apiUrl: API_URL, domain: DOMAIN };

const TPL_NAME = 'my-all-in-one-template';

const BROWSERTOOL_PORT = 3000;
const TARGET_URL = 'https://example.com';
const SCREENSHOT_PATH = 'all-in-one-example.png';

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

/** Poll the public gateway /health endpoint until the browser service is ready or times out. */
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
      console.log(`  /health ready (HTTP ${code})`);
      return;
    }
    console.log(`  ...waiting for the browser service (HTTP ${JSON.stringify(code)})`);
    await sleep(2000);
  }
  throw new Error(`browser service not ready within ${timeout}s`);
}

/** Connect to browsertool over CDP, open the target page, and take a screenshot. */
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
    console.log(`  Screenshot saved: ${SCREENSHOT_PATH}`);
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

    console.log('\n--- Waiting for browser health check ---');
    await waitUntilHealthy(sbx, host, token);

    console.log('\n--- Playwright CDP case ---');
    await verifyWithPlaywright(cdpWsUrl, headers);

    console.log('\n--- Code Interpreter case ---');
    const execution = await sbx.runCode(
      "import json\nresult = {'status': 'ok', 'source': 'all-in-one'}\nprint(json.dumps(result, ensure_ascii=False))",
    );
    console.log(execution.logs.stdout);
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

The browser service in the All-In-One template provides the following endpoints:

| **Endpoint** | **Path** | **Purpose** |
| --- | --- | --- |
| Health check endpoint | `https://<sandbox-host>/health` | Determine whether the browser service has finished starting |
| CDP automation endpoint | `wss://<sandbox-host>/ws/automation` | Browser automation, compatible with Puppeteer and Playwright |
| VNC livestream endpoint | `wss://<sandbox-host>/ws/livestream` | View the browser desktop in real time through a noVNC client |

> **Note**: `<sandbox-host>` is obtained through `sbx.get_host(3000)` or `sbx.getHost(3000)`. All endpoints require the `X-Access-Token` header for authentication.

Inside the sandbox you can first probe whether the CDP WebSocket handshake works. A `101 Switching Protocols` response means the CDP endpoint can be upgraded to a WebSocket connection:

```bash
curl -sS -m 4 -i \
  -H 'Connection: Upgrade' \
  -H 'Upgrade: websocket' \
  -H 'Sec-WebSocket-Version: 13' \
  -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' \
  http://localhost:3000/ws/automation
```

## Real-time VNC viewing

The All-In-One template supports viewing the remote browser desktop in real time through VNC, which makes it easy to monitor automation tasks during development and debugging.

### Use the online noVNC client

1. Open the online client provided by noVNC: [https://novnc.com/noVNC/vnc.html](https://novnc.com/noVNC/vnc.html)
2. In the connection settings, under **Advanced** > **WebSocket**, fill in the following:
   - **Host**: the host address obtained through `sbx.get_host(3000)` or `sbx.getHost(3000)`
   - **Port**: `443`
   - **Path**: `ws/livestream`
3. Click **Connect** to see the browser interface.

> **Note**: The noVNC connection also requires authentication through `X-Access-Token`. After connecting, the initial screen may be black or gray. This is normal because the browser is waiting for instructions. Once your automation script runs `page.goto()` or similar operations, the interface will display the corresponding content.

## Combined workflow recommendations

| **Phase** | **Recommendation** |
| --- | --- |
| Page access | Use Playwright/Puppeteer to connect to the browser through `wss://<sandbox-host>/ws/automation` |
| Data persistence | Write screenshots, HTML, downloaded files, or intermediate results to the sandbox file system |
| Code processing | Use the Code Interpreter SDK's `run_code` / `runCode` in the same sandbox to parse and analyze data |
| Result export | Use the file APIs or SDK to download generated CSV, JSON, image, or PDF files |

## Limitations

| **Item** | **Constraint** |
| --- | --- |
| Sandbox lifetime | A single sandbox session lasts at most 6 hours by default, after which it is automatically destroyed |
| Idle timeout | Configurable through the `sandboxIdleTimeoutSeconds` parameter; the sandbox terminates early after being idle for the specified time |
| Browser support | Currently ships with Chromium/Chrome |
| Resource spec | 4 vCPU / 8192 MB or higher is recommended to avoid resource contention between browser automation and code execution |
| Authentication | CDP, VNC, and data-plane APIs all require a valid API key or `X-Access-Token` |

## Related documents

- [Built-in Templates](../02.Built-in%20Templates.md)
- [Build Custom Image Templates](../03.Build%20Custom%20Image%20Templates.md)
- [Create a Sandbox](../../01.Sandbox/02.Create%20a%20Sandbox.md)
- [Lifecycle](../../01.Sandbox/01.Lifecycle.md)
- [Base Template](Base%20Template.md) (choose when you only need the envd base capabilities)
- [Code Interpreter v1 Template](Code%20Interpreter%20v1%20Template.md) (choose when you only need code execution)
- [Browser Template](Browser%20Template.md) (choose when you only need browser automation)
