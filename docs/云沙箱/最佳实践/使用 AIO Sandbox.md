# 使用 AIO Sandbox

AIO Sandbox 面向“浏览器操作 + 代码执行 + 文件处理”连续发生的 Agent 任务。如果已准备同时包含浏览器、Playwright/Puppeteer、Python/Node.js 和常用数据处理依赖的 `aio` 模板，开发者可以在同一个沙箱中完成网页访问、截图、下载、数据清洗、代码计算和报告生成，减少浏览器环境与代码执行环境之间的数据搬运。

这个实践适合网页数据采集后分析、自动化测试后生成报告、内容生产 Agent、运营后台巡检和多工具 Agent。相比只使用 Browser Use Sandbox，AIO Sandbox 更适合需要把浏览器产物立即交给 Python/Node 脚本继续处理的任务。

## 业务场景

- 从动态网页采集数据，立即运行 Python 脚本清洗、汇总并导出文件。
- 在浏览器中完成操作后，对下载文件做解析、转码或报表生成。
- 自动化测试中同时运行浏览器 E2E 和后端脚本。
- 为内容生产 Agent 生成截图、PDF、表格和归档文件。

## 核心能力

AIO Sandbox 的关键价值是把浏览器、Shell、代码运行时和文件系统放在同一个沙箱实例中。浏览器下载的文件、Python 生成的结果、Node.js 自动化脚本和 Shell 命令都访问同一份任务目录，避免在多个沙箱之间通过 OSS、NAS 或业务服务搬运中间文件。

常见能力如下：

| 能力 | 用途 | 典型接口 |
| --- | --- | --- |
| 浏览器自动化 | 访问网页、截图、下载文件、表单操作 | Playwright / Puppeteer / CDP |
| 代码执行 | 清洗网页结果、解析文件、生成报告 | `sandbox.commands.run()` |
| 文件处理 | 保存 Cookie、截图、HTML、JSON、CSV、PDF | `sandbox.files.write()` / `sandbox.files.read()` |
| 人工介入 | 登录、验证码、任务观察和调试 | VNC / Livestream |

如果 Agent 会在一个任务里连续使用浏览器和代码解释器，优先使用 AIO Sandbox；如果任务只需要浏览器观察和操作，可以使用 [Browser Use Sandbox](./使用%20Browser%20Use%20Sandbox.md)。

## 推荐流程

1. 使用已准备好的 `aio` 模板创建云沙箱。
2. 浏览器阶段访问网页、交互、截图或下载文件。
3. 代码阶段读取浏览器产物，完成解析、清洗、计算和报告生成。
4. 审计阶段保存 URL、动作摘要、截图路径、脚本版本和输出结果。
5. 清理阶段释放沙箱，删除任务级凭证和临时文件。

## 示例代码

以下示例假设 `aio` 模板已预装 Playwright、浏览器和 Python，用于先采集网页信息，再生成分析结果。

```javascript
import { Sandbox } from "e2b";

const sandbox = await Sandbox.create("aio", {
  apiKey: process.env.E2B_API_KEY,
  apiUrl: process.env.E2B_API_URL,
  domain: process.env.E2B_DOMAIN,
  envs: { TASK_TYPE: "aio-browser-code" },
  metadata: { scenario: "aio-browser-code" },
  timeoutMs: 300_000,
});

try {
  await sandbox.files.makeDir("/tmp/aio-task");
  await sandbox.files.write(
    "/tmp/aio-task/collect.mjs",
    `import fs from "node:fs/promises";
import { chromium } from "playwright";

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1365, height: 768 } });
await page.goto("https://example.com", { waitUntil: "networkidle" });
await page.screenshot({ path: "page.png", fullPage: true });

const rows = await page.evaluate(() => [{
  url: location.href,
  title: document.title,
  textLength: document.body.innerText.length,
}]);

await fs.writeFile("browser-result.json", JSON.stringify(rows, null, 2));
await browser.close();
`,
  );
  await sandbox.files.write(
    "/tmp/aio-task/analyze.py",
    `import json
from pathlib import Path

rows = json.loads(Path("browser-result.json").read_text())
summary = {
    "page_count": len(rows),
    "titles": [row["title"] for row in rows],
    "total_text_length": sum(row["textLength"] for row in rows),
    "artifacts": ["page.png", "browser-result.json"],
}
Path("summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
print(json.dumps(summary, ensure_ascii=False))
`,
  );

  const collect = await sandbox.commands.run("node collect.mjs", {
    cwd: "/tmp/aio-task",
    timeoutMs: 120_000,
  });
  if (collect.exitCode !== 0) {
    throw new Error(collect.stderr || collect.stdout);
  }

  const analyze = await sandbox.commands.run("python3 analyze.py", {
    cwd: "/tmp/aio-task",
    timeoutMs: 60_000,
  });
  if (analyze.exitCode !== 0) {
    throw new Error(analyze.stderr || analyze.stdout);
  }

  console.log(JSON.parse(analyze.stdout));
} finally {
  await sandbox.kill();
}
```

## 连接已运行的浏览器

AIO 模板通常已经启动浏览器服务。使用 Puppeteer 时应连接到沙箱内的浏览器端点，而不是重新启动本地浏览器进程：

```javascript
const puppeteer = require("puppeteer-core");

const browser = await puppeteer.connect({
  browserWSEndpoint: "ws://localhost:5000/ws/automation",
});

const page = (await browser.pages())[0] ?? await browser.newPage();
await page.goto("https://example.com", { waitUntil: "networkidle2" });
console.log(await page.title());

await browser.disconnect();
```

Agent 生成浏览器脚本时建议显式约束三点：

- 使用 `puppeteer.connect()` 连接已有浏览器，不使用 `puppeteer.launch()`。
- 任务结束时使用 `browser.disconnect()`，避免 `browser.close()` 关闭共享浏览器。
- 中间文件写入任务目录，例如 `/home/user/data` 或 `/tmp/aio-task`，不要散落在不确定路径。

## 多步骤任务与状态保持

AIO Sandbox 适合把登录、人工确认、数据采集和文件分析拆成多个步骤。浏览器状态、Cookie 和任务文件都留在同一个沙箱实例中，后续步骤可以继续使用。

典型流程：

1. 打开登录页，通过 VNC 完成人工登录或验证码处理。
2. 读取当前页面 Cookie，保存到沙箱文件系统。
3. 后续脚本读取 Cookie，恢复登录态并执行采集或操作。
4. Python/Node.js 读取采集结果，生成结构化报告或文件。

保存 Cookie：

```javascript
const fs = require("fs");
const puppeteer = require("puppeteer-core");

const browser = await puppeteer.connect({
  browserWSEndpoint: "ws://localhost:5000/ws/automation",
});
const page = (await browser.pages())[0];
const cookies = await page.cookies();

fs.mkdirSync("/home/user/data", { recursive: true });
fs.writeFileSync("/home/user/data/cookies.json", JSON.stringify(cookies, null, 2));

await browser.disconnect();
```

恢复 Cookie：

```javascript
const fs = require("fs");
const puppeteer = require("puppeteer-core");

const browser = await puppeteer.connect({
  browserWSEndpoint: "ws://localhost:5000/ws/automation",
});
const page = (await browser.pages())[0];
const cookies = JSON.parse(fs.readFileSync("/home/user/data/cookies.json", "utf8"));

await page.setCookie(...cookies);
await page.goto("https://example.com/protected", { waitUntil: "networkidle2" });

await browser.disconnect();
```

多步骤任务应设置足够的沙箱生命周期，开发调试可以使用较长超时；生产任务应按任务复杂度设置上限，并在 `finally` 中释放沙箱。

## 上线建议

- 将浏览器阶段和代码阶段拆开记录，分别保存输入、输出、日志和错误。
- 下载文件先做类型、大小和路径校验，再交给代码阶段处理。
- 网页内容和下载文件都可能携带 prompt injection，不要把网页文本直接作为系统指令。
- 浏览器账号、Cookie、模型 Key 和业务凭证运行时注入，任务结束后销毁。
- 对高成本任务设置超时、文件大小上限和最大页面数，避免 Agent 无限制爬取或计算。
- 需要人工介入的任务保留 VNC 观察入口，并把人工确认动作写入任务审计。
- 批量任务按隔离要求选择单沙箱顺序执行或多沙箱并发执行；有登录态和前后依赖的任务优先单沙箱顺序执行。

## 相关功能

- [Browser Use Sandbox](./使用%20Browser%20Use%20Sandbox.md)
- [Code Interpreter Sandbox](./使用%20Code%20Interpreter%20Sandbox.md)
- [构建 Agent Harness](./构建%20Agent%20Harness.md)
