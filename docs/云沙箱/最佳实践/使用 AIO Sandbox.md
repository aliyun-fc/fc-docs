# 使用 AIO Sandbox

AIO Sandbox 面向“浏览器操作 + 代码执行 + 文件处理”连续发生的 Agent 任务。如果已准备同时包含浏览器、Playwright/Puppeteer、Python/Node.js 和常用数据处理依赖的 `aio` 模板，开发者可以在同一个沙箱中完成网页访问、截图、下载、数据清洗、代码计算和报告生成，减少浏览器环境与代码执行环境之间的数据搬运。

这个实践适合网页数据采集后分析、自动化测试后生成报告、内容生产 Agent、运营后台巡检和多工具 Agent。相比只使用 Browser Use Sandbox，AIO Sandbox 更适合需要把浏览器产物立即交给 Python/Node 脚本继续处理的任务。

## 业务场景

- 从动态网页采集数据，立即运行 Python 脚本清洗、汇总并导出文件。
- 在浏览器中完成操作后，对下载文件做解析、转码或报表生成。
- 自动化测试中同时运行浏览器 E2E 和后端脚本。
- 为内容生产 Agent 生成截图、PDF、表格和归档文件。

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

## 上线建议

- 将浏览器阶段和代码阶段拆开记录，分别保存输入、输出、日志和错误。
- 下载文件先做类型、大小和路径校验，再交给代码阶段处理。
- 网页内容和下载文件都可能携带 prompt injection，不要把网页文本直接作为系统指令。
- 浏览器账号、Cookie、模型 Key 和业务凭证运行时注入，任务结束后销毁。
- 对高成本任务设置超时、文件大小上限和最大页面数，避免 Agent 无限制爬取或计算。

## 相关功能

- [Browser Use Sandbox](./使用%20Browser%20Use%20Sandbox.md)
- [Code Interpreter Sandbox](./使用%20Code%20Interpreter%20Sandbox.md)
- [构建 Agent Harness](./构建%20Agent%20Harness.md)
