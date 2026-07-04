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

## 上线建议

- 浏览器任务默认处理不可信网页，必须限制可访问域名、下载文件类型和输出大小。
- 页面内容可能包含 prompt injection，不要让 Agent 未经校验地执行网页中的指令。
- 登录态、Cookie、账号凭证应按任务隔离，通过运行时注入，不写入模板。
- 对外部网页操作要记录 URL、截图、关键 DOM 摘要、工具调用轨迹和结果文件。
- 如果任务需要在浏览器操作后继续运行 Python/Node 脚本处理数据，优先使用 [AIO Sandbox](./使用%20AIO%20Sandbox.md)。

## 相关功能

- [构建模板](../功能说明/Templates/构建模板.md)
- [后台命令](../功能说明/Commands/后台命令.md)
- [上传和下载文件](../功能说明/Filesystem/上传和下载文件.md)
- [预装 Agent 环境](./预装%20Agent%20环境.md)
