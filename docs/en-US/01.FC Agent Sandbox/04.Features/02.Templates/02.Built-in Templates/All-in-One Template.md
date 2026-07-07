# All-in-One Template

The all-in-one template merges the capabilities of the browser template and the code-interpreter-v1 template into a single, unified cloud-isolated execution environment. An all-in-one sandbox can do both browser-level automation (CDP / VNC / recording) and code execution, file management, and interactive terminals — the "eyes + brain + hands" of an AI Agent.

The all-in-one template aligns with the experience of using browser automation and Code Interpreter together in E2B.

## Features

| **Feature** | **Description** |
| --- | --- |
| Browser automation | Integrates browser template capabilities: CDP protocol, Puppeteer/Playwright compatibility, real-time VNC viewing, and session recording |
| Code execution | Integrates code-interpreter-v1 template capabilities: Python/JavaScript code execution, context management, and file system operations |
| Terminal commands | Supports synchronous command execution and an interactive WebSocket terminal (TTY) |
| Process management | List, query, and stop processes running inside the sandbox |
| Coordinated execution | Use the browser and the code interpreter in the same session to build end-to-end "browser scrape → code processing" workflows |
| Secure isolation | Dedicated isolation based on function instances; each sandbox instance has its own file system, browser instance, and process space |

## Use cases

| **Scenario** | **Description** |
| --- | --- |
| AI Agent composite tasks | Drive the browser for page interaction and run code to process and analyze data, all in the same session |
| Data collection and processing | Scrape dynamic pages with the browser first, then run scripts in the sandbox to parse, clean, and export the results |
| Automated testing | Coordinate browser E2E with backend scripts, making replay and troubleshooting easy in a controlled container environment |
| Content generation and archiving | Generate screenshots/PDFs/recordings and persist or download the processed results |

## Default configuration

The default configuration of the all-in-one template is as follows:

| **Item** | **Default** | **Description** |
| --- | --- | --- |
| Container image | `sandbox-all-in-one:v0.9.30` | Prebuilt all-in-one sandbox image |
| Default port | 5000 | Port the sandbox service listens on |
| CPU | 4 vCPU | Default spec, since it must support both the browser and code execution |
| Memory | 8192 MB (8 GB) | Default spec |
| Disk size | 10240 MB (10 GB) | 10 GB is recommended to store browser data and execution results |

> **Note**
>
> The default CPU and memory specs of the all-in-one template are higher than those of the code-interpreter-v1 template and the browser template, because it must support both the browser runtime and the code execution environment at the same time.

## Difference from the browser template

The browser template provides a browser runtime and exposes CDP and VNC capabilities through port 3000 by default. It suits browser automation tasks such as web access, page interaction, screenshots, data collection, and UI testing. It includes E2B envd-compatible base capabilities but does not provide the Code Interpreter service, so you cannot execute Python directly through a Code Interpreter context.

The all-in-one template layers the Code Interpreter service on top of the browser capabilities, using port 3000 as the browser entry and port 5000 as the code execution and file management entry by default. It can execute Python directly within the same sandbox session, enabling composite flows such as "browser scrapes a dynamic page → Python parses/cleans/analyzes → file export."

| **Comparison** | **Browser template** | **All-in-one template** |
| --- | --- | --- |
| Core positioning | Lightweight browser automation environment | Integrated browser automation + code execution environment |
| Browser capabilities | Supports CDP, VNC, screenshots, page interaction | Supports CDP, VNC, screenshots, page interaction |
| E2B envd base capabilities | Supported | Supported |
| Code Interpreter service | Not supported | Supported |
| Code execution | Cannot execute Python through Code Interpreter | Supports Python / JavaScript code execution |
| File processing | Supports basic file access, no Code Interpreter file API | Supports the file API and in-context read/write and processing |
| Typical entries | 3000 (browser entry) | 3000 (browser entry) / 5000 (code entry) |
| Default spec | 2 vCPU / 2048 MB / 10240 MB disk | 4 vCPU / 8192 MB / 10240 MB disk |
| Recommended for | Only browser automation is needed | Browser and code execution need to work together |

## Quickstart

### Step 1: Prepare an API key

1. Log in to the [Function Compute console](https://fcnext.console.aliyun.com/).
2. See [Create an API Key](../../../01.Getting%20Started/02.Create%20an%20API%20Key.md) to create and obtain an API key.
3. Use the API key and API endpoint through an SDK to create a sandbox (see the examples below).

### Step 2: Obtain the endpoints

An all-in-one sandbox provides the following endpoints:

| **Endpoint** | **Format** | **Purpose** |
| --- | --- | --- |
| CDP automation endpoint | `wss://{sbx.get_host(3000)}/ws/automation` | Browser automation (Puppeteer/Playwright) |
| VNC livestream endpoint | `wss://{sbx.get_host(3000)}/ws/livestream` | View the browser interface in real time |
| Data-plane REST API | `https://{accountID}.e2b-data.cn-hangzhou.aliyuncs.com/` | Code execution, file management, terminal commands |

> **Note**: The CDP and VNC endpoints obtain the host address through the SDK's `sbx.get_host(3000)`, and the `X-Access-Token` header is required for authentication when connecting.

### Step 3: Use browser automation

```javascript
const puppeteer = require('puppeteer-core');
const { Sandbox } = require('e2b');

const BROWSER_SANDBOX_PORT = 3000;

async function main() {
  const sbx = await Sandbox.create({ template: 'all-in-one-template', apiKey: E2B_API_KEY, timeout: 600 });
  try {
    const host = sbx.getHost(BROWSER_SANDBOX_PORT);
    const cdpEndpoint = `wss://${host}/ws/automation`;

    const browser = await puppeteer.connect({
      browserWSEndpoint: cdpEndpoint,
      headers: { 'X-Access-Token': sbx.envdAccessToken },
    });
    const page = await browser.newPage();
    await page.goto('https://example.com');
    await page.screenshot({ path: 'example.png' });
    await browser.close();
  } finally {
    await sbx.kill();
  }
}
main();
```

### Step 4: Use code execution

Create a context and execute code through the data-plane API:

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

### Use both in the same session

The core advantage of the all-in-one template is using the browser and code execution capabilities in the same sandbox session. A typical workflow: the browser scrapes data → Python code processes and analyzes it → the file API exports the results.

> **Note**: The Python example below obtains the access token through `sbx._envd_access_token`, which is an internal SDK implementation detail and may change in future versions. The JS SDK exposes the public field `sbx.envdAccessToken`.

```python
import asyncio
from e2b import Sandbox
from browser_use import BrowserSession, BrowserProfile

BROWSER_SANDBOX_PORT = 3000

async def run_aio_task():
    # 1. Create the sandbox and obtain the CDP endpoint
    sbx = Sandbox.create(template="all-in-one-template", api_key=E2B_API_KEY, timeout=600)
    try:
        host = sbx.get_host(BROWSER_SANDBOX_PORT)
        cdp_url = f"wss://{host}/ws/automation"

        browser = BrowserSession(
            cdp_url=cdp_url,
            browser_profile=BrowserProfile(headless=True),
            extra_headers={"X-Access-Token": sbx._envd_access_token},
        )

        # 2. Create a Python context through the data-plane API and run data-processing code
        #    POST ${BASEURL}/sandboxes/{sandboxId}/contexts
        #    POST ${BASEURL}/sandboxes/{sandboxId}/contexts/execute

        # 3. Scrape data with the browser, then process and analyze it with code
        #    ...
    finally:
        sbx.kill()

asyncio.run(run_aio_task())
```

## Related documents

- [Built-in Templates](../02.Built-in%20Templates.md)
- [Build Custom Image Templates](../03.Build%20Custom%20Image%20Templates.md)
- [Lifecycle](../../01.Sandbox/01.Lifecycle.md)
- [Base Template](Base%20Template.md) (choose when you only need the envd base capabilities)
- [Code Interpreter v1 Template](Code%20Interpreter%20v1%20Template.md) (choose when you only need code execution)
- [Browser Template](Browser%20Template.md) (choose when you only need browser automation)
