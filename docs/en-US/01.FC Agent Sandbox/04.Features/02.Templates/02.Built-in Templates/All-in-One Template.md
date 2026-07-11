# All-In-One Template

The All-In-One template combines the capabilities of the browser template and the code-interpreter-v1 template into a single, unified cloud-based isolated execution environment. An All-In-One sandbox can drive a cloud browser via CDP/VNC and, within the same sandbox, execute Python/JavaScript code, process files, and run terminal commands. It is ideal for AI Agent scenarios that require coordinated "browser automation + code execution."

The All-In-One template aligns with the E2B experience of using browser automation and Code Interpreter together.

## Features

| **Feature** | **Description** |
| --- | --- |
| Browser automation | Built-in Chromium/Chrome browser with CDP over WebSocket support, compatible with Puppeteer, Playwright, BrowserUse, and other automation frameworks |
| Real-time VNC visualization | Built-in VNC service for real-time viewing of the browser desktop environment via a noVNC client, convenient for debugging and monitoring |
| Code execution | Integrated Code Interpreter capabilities supporting Python/JavaScript execution, context persistence, and result output |
| File system operations | Supports file APIs including upload, download, read, write, and directory management, enabling browser-collected results to be handed off to code for further processing |
| Terminal commands | Supports synchronous command execution and WebSocket-based interactive terminal (TTY) |
| Coordinated execution | Complete end-to-end workflows such as "browser visits a dynamic page → code parses/analyzes → file export" within a single sandbox session |
| Secure isolation | Each All-In-One sandbox instance has its own independent file system, browser instance, and process space |

## Use Cases

| **Scenario** | **Description** |
| --- | --- |
| AI Agent composite tasks | Drive the browser for page interaction while running code for data analysis, reasoning assistance, or file processing in the same session |
| Data collection and processing | Use the browser to scrape dynamic pages, take screenshots, or download files, then use Python scripts to parse, clean, summarize, and export the results |
| Automated testing | Combine browser E2E tests with backend scripts, log analysis, and report generation in a single isolated container |
| Content generation and archiving | Generate screenshots, PDFs, video recordings, or structured data, and download the results via the file APIs |

## Default Configuration

The default configuration of the All-In-One template is as follows:

| **Configuration** | **Default** | **Description** |
| --- | --- | --- |
| Container image | `fc-e2b-registry.ap-southeast-1.cr.aliyuncs.com/runtime/all-in-one:v0.0.36` | Prebuilt All-In-One sandbox image |
| Browser port | 3000 | Browser service listening port for `/health`, CDP, and VNC |
| Code execution port | 5000 | Code Interpreter/envd service listening port |
| CPU | 4 vCPU | Recommended spec to support both browser and code execution |
| Memory | 8192 MB | Recommended spec |
| Disk size | 10240 MB | 10 GB recommended for browser cache, screenshots, downloaded files, and code execution results |

> **Note**
>
> The All-In-One template's default CPU and memory specs are higher than those of the code-interpreter-v1 template and the browser template because it must support both the browser runtime and the code execution environment. The example image is hosted in the Singapore region (`ap-southeast-1`); when building and running the template, it is recommended to use the API URL and domain from the same region.

## Differences from the Browser Template

The browser template provides a browser runtime and exposes CDP and VNC capabilities through port 3000 by default. It is suited for browser automation tasks such as web access, page interaction, screenshots, data collection, and UI testing. It includes E2B envd-compatible base capabilities but does not provide the Code Interpreter service, so Python cannot be executed directly through a Code Interpreter context.

The All-In-One template layers the Code Interpreter service on top of the browser capabilities. It uses port 3000 as the browser entry and port 5000 as the code execution and file management entry by default. It can execute Python directly in the same sandbox session, enabling composite flows such as "browser scrapes a dynamic page → Python parses/cleans/analyzes → files are exported."

| **Comparison** | **Browser Template** | **All-In-One Template** |
| --- | --- | --- |
| Core positioning | Lightweight browser automation environment | Integrated browser automation + code execution environment |
| Browser capabilities | Supports CDP, VNC, screenshots, and page interaction | Supports CDP, VNC, screenshots, and page interaction |
| Code Interpreter service | Not supported | Supported |
| Code execution | Cannot execute Python via Code Interpreter | Supports Python/JavaScript code execution |
| File processing | Supports basic file access; no Code Interpreter file API | Supports file APIs with in-context read/write and processing |
| Typical entry points | 3000 (browser entry) | 3000 (browser entry) / 5000 (code entry) |
| Recommended spec | 4 vCPU / 8192 MB / 10240 MB disk | 4 vCPU / 8192 MB / 10240 MB disk |
| Recommended for | Only browser automation is needed | Browser automation and code execution need to work together |

## Quickstart

The complete usage of the All-In-One template is divided into two phases: first **build the template** (materialize a named template from the All-In-One image), then **run the template** (create a sandbox, wait for the browser service health check, automate via CDP and take screenshots, and execute code through Code Interpreter). Both Python and Node.js implementations are provided below.

> **Note**: Replace `API_KEY` in the examples with the API Key you generated in the console, and replace `API_URL` / `DOMAIN` with the endpoint of the corresponding region. When connecting to CDP/VNC endpoints, you must include the `X-Access-Token` header for authentication: the Python SDK exposes it via the internal attribute `sbx._envd_access_token` (which may be renamed or removed in future versions), and the JS SDK exposes the public field `sbx.envdAccessToken`.

### Step 1: Create an API Key

1. Log in to the [Function Compute console](https://fcnext.console.aliyun.com/).
2. Under the **FC Agent Sandbox** tab, select **API Keys** and generate an API Key.
3. Use the API Key and API endpoint through the SDK to build the template and create a sandbox.

### Step 2: Prepare the Local Environment

**Python**:

```bash
uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install e2b==2.31.0 e2b-code-interpreter==2.8.1 'playwright>=1.49.0'
playwright install chromium
```

**Node.js**: Use the following `package.json`, then run `npm install`.

```json
{
  "name": "all-in-one-template-demo",
  "version": "1.0.0",
  "type": "module",
  "dependencies": {
    "@e2b/code-interpreter": "^2.8.1",
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

### Step 3: Build the All-In-One Template

Build a named template from the All-In-One image, specifying CPU and memory specs at build time (4 vCPU / 8192 MB recommended).

**Python**:

```python
"""All-In-One template build example."""

from e2b import Template, default_build_logger

API_KEY = "e2b_xxx"  # Replace with your API Key
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

const API_KEY = 'e2b_xxx'; // Replace with your API Key
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

### Step 4: Run the Template and Verify Combined Capabilities

After creating the sandbox, first poll `/health` until the browser service is ready, then connect Playwright via the CDP endpoint to open the target page and take a screenshot, and finally execute a Python snippet through Code Interpreter to verify code execution.

**Python**:

```python
"""All-In-One template run example: create sandbox -> CDP automation -> Code Interpreter code execution."""

import time

from e2b_code_interpreter import Sandbox

API_KEY = "e2b_xxx"  # Replace with your API Key
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
        print(f"  ...waiting for browser service (HTTP {code!r})")
        time.sleep(2)
    raise TimeoutError(f"browser service not ready within {timeout}s")


def verify_with_playwright(cdp_ws_url: str, headers: dict) -> None:
    """Connect to browsertool via CDP, open the target page, and take a screenshot."""
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

    print("\n--- Playwright CDP example ---")
    verify_with_playwright(cdp_ws_url, headers)

    print("\n--- Code Interpreter example ---")
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

const API_KEY = 'e2b_xxx'; // Replace with your API Key
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
    console.log(`  ...waiting for browser service (HTTP ${JSON.stringify(code)})`);
    await sleep(2000);
  }
  throw new Error(`browser service not ready within ${timeout}s`);
}

/** Connect to browsertool via CDP, open the target page, and take a screenshot. */
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

    console.log('\n--- Playwright CDP example ---');
    await verifyWithPlaywright(cdpWsUrl, headers);

    console.log('\n--- Code Interpreter example ---');
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

## WebSocket Endpoints

The browser service in the All-In-One template provides the following endpoints:

| **Endpoint** | **Path** | **Purpose** |
| --- | --- | --- |
| Health check endpoint | `https://<sandbox-host>/health` | Determine whether the browser service has finished starting |
| CDP automation endpoint | `wss://<sandbox-host>/ws/automation` | Browser automation, compatible with Puppeteer and Playwright |
| VNC livestream endpoint | `wss://<sandbox-host>/ws/livestream` | View the browser desktop environment in real time via a noVNC client |

> **Note**: `<sandbox-host>` is obtained via `sbx.get_host(3000)` or `sbx.getHost(3000)`. All endpoints require the `X-Access-Token` header for authentication.

Inside the sandbox, you can first probe whether the CDP WebSocket handshake works properly. A `101 Switching Protocols` response indicates that the CDP endpoint can be upgraded to a WebSocket connection:

```bash
curl -sS -m 4 -i \
  -H 'Connection: Upgrade' \
  -H 'Upgrade: websocket' \
  -H 'Sec-WebSocket-Version: 13' \
  -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' \
  http://localhost:3000/ws/automation
```

## Real-Time VNC Viewing

The All-In-One template supports real-time viewing of the remote browser desktop environment via VNC, making it convenient to monitor automation task execution during development and debugging.

### Using the Online noVNC Client

1. Visit the online client provided by noVNC: [https://novnc.com/noVNC/vnc.html](https://novnc.com/noVNC/vnc.html)
2. In the connection settings, under **Advanced** > **WebSocket**, fill in the following connection information:
   - **Host**: The host address obtained via `sbx.get_host(3000)` or `sbx.getHost(3000)`
   - **Port**: `443`
   - **Path**: `ws/livestream`
3. Click **Connect** to view the browser interface.

> **Note**: The noVNC connection also requires authentication via `X-Access-Token`. After connecting, the initial screen may be blank or gray; once the automation script performs operations such as `page.goto()`, the interface will display the corresponding content.

## Combined Workflow Recommendations

| **Phase** | **Recommended Approach** |
| --- | --- |
| Page access | Use Playwright/Puppeteer to connect to the browser via `wss://<sandbox-host>/ws/automation` |
| Data persistence | Write screenshots, HTML, downloaded files, or intermediate results to the sandbox file system |
| Code processing | Use the Code Interpreter SDK's `run_code` / `runCode` to parse and analyze data within the same sandbox |
| Result export | Use the file APIs or SDK to download generated CSV, JSON, image, PDF, and other result files |

## Limitations

| **Limitation** | **Constraint** |
| --- | --- |
| Browser support | Currently ships with built-in Chromium/Chrome browser |
| Resource spec | 4 vCPU / 8192 MB or higher is recommended to avoid resource contention between browser and code execution |
| Authentication requirement | CDP, VNC, and data-plane APIs all require a valid API Key or `X-Access-Token` |

## Related Documents

- [Built-in Templates](../02.Built-in Templates.md)
- [Build Custom Image Templates](../03.Build Custom Image Templates.md)
- [Create a Sandbox](../../01.Sandbox/02.Create a Sandbox.md)
- [Lifecycle](../../01.Sandbox/01.Lifecycle.md)
- [Base Template](Base Template.md) (choose when you only need envd base capabilities)
- [Code Interpreter v1 Template](Code Interpreter v1 Template.md) (choose when you only need code execution capabilities)
- [Browser Template](Browser Template.md) (choose when you only need browser automation capabilities)
