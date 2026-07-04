# 使用 Computer Use Sandbox

Computer Use Sandbox 面向“让 Agent 像人一样操作计算机”的场景，通常需要桌面环境、浏览器或应用窗口、屏幕观察、点击、输入和结果判定。如果已准备包含桌面环境、浏览器、截图和输入控制能力的 `desktop` 模板，开发者可以参考 E2B Computer Use 的模式：创建桌面沙箱，获取屏幕截图，把截图交给视觉模型决策，再把点击、输入、滚动、按键等动作发送回沙箱执行。

这个实践适合桌面软件自动化、复杂后台操作、UI 问题复现、浏览器与终端组合任务、Computer Use Agent 评测。相比 Browser Use Sandbox，Computer Use Sandbox 不只操作网页，还可以操作窗口、终端、文件管理器和多应用流程，因此必须更严格地控制权限、动作边界和人工确认。

## 业务场景

- 自动操作企业后台，完成跨页面录入、截图、导出文件。
- 复现用户提交的 UI 问题，并生成操作轨迹。
- 让 Agent 在隔离环境中完成浏览器、终端和文件处理的组合任务。
- 对桌面操作 Agent 做评测，记录每一步观察、动作和结果。

## 推荐架构

Computer Use 不建议从“给模型一个无限制桌面”开始。更稳的架构是：

1. 业务系统定义任务、允许访问的应用和操作边界。
2. 使用已准备好的 `desktop` 模板创建云沙箱。
3. Agent Harness 获取屏幕截图，将观察结果交给视觉模型。
4. 模型输出受限动作，例如 click、type、scroll、keypress。
5. 高风险动作进入人工确认，例如提交表单、付款、删除文件、发送消息。
6. 任务结束后导出轨迹、截图和产物，并销毁环境。

## 示例代码

以下示例参考 E2B Computer Use 的开发体验，适用于已确认兼容 `@e2b/desktop` 的桌面模板：创建 `desktop` 沙箱，打开页面，截图，然后执行一次点击和输入。实际接入视觉模型时，把 `screenshot` 传给模型，由模型返回下一步动作即可。

```javascript
import { Sandbox } from "@e2b/desktop";

const desktop = await Sandbox.create({
  template: "desktop",
  apiKey: process.env.E2B_API_KEY,
  apiUrl: process.env.E2B_API_URL,
  domain: process.env.E2B_DOMAIN,
  resolution: [1024, 768],
  dpi: 96,
  timeoutMs: 300_000,
  metadata: { scenario: "computer-use" },
});

try {
  await desktop.launch("firefox", "https://example.com");

  const screenshot = await desktop.screenshot();
  // 将 screenshot 发送给视觉模型，模型返回下一步动作。
  // 这里用固定动作演示 Computer Use 的控制闭环。

  await desktop.mouse.click(320, 240);
  await desktop.keyboard.type("hello from sandbox");
  await desktop.keyboard.press("ENTER");

  const after = await desktop.screenshot();
  console.log({
    beforeBytes: screenshot.length,
    afterBytes: after.length,
  });
} finally {
  await desktop.kill();
}
```

如果需要让用户或开发者实时观察桌面，可以在模板中启动远程桌面或 VNC/streaming 服务，并通过 `getHost(port)` 获取访问地址。生产环境必须为该访问地址增加认证，不要暴露未授权桌面。

```javascript
import { Sandbox } from "e2b";

const sandbox = await Sandbox.create("desktop", {
  apiKey: process.env.E2B_API_KEY,
  apiUrl: process.env.E2B_API_URL,
  domain: process.env.E2B_DOMAIN,
  metadata: { scenario: "desktop-preview" },
});

const vnc = await sandbox.commands.run("start-vnc --host 0.0.0.0 --port 6080", {
  background: true,
  timeoutMs: 30_000,
});

console.log(`Desktop preview: https://${sandbox.getHost(6080)}`);
console.log(`VNC process id: ${vnc.pid}`);
```

其中 `start-vnc` 是 `desktop` 模板内的启动脚本示例，具体命令以实际模板提供的脚本为准。只要服务监听在沙箱端口上，就可以通过 `getHost(port)` 获取访问地址。

## 上线建议

- 将动作空间限制为明确的 click、type、scroll、keypress，不接受模型生成的任意系统命令。
- 截图可能包含敏感信息，传给模型前应做脱敏或访问控制。
- 登录、支付、删除、发送消息、修改配置等动作必须进入人工确认。
- 记录每一步观察、动作、截图、窗口状态和模型输出，便于复盘和审计。
- 桌面任务通常资源成本更高，应设置超时、最大步数和自动清理策略。

## 相关功能

- [安全执行 Agent 工具调用](./安全执行%20Agent%20工具调用.md)
- [构建 Agent Harness](./构建%20Agent%20Harness.md)
- [Browser Use Sandbox](./使用%20Browser%20Use%20Sandbox.md)
- [AIO Sandbox](./使用%20AIO%20Sandbox.md)
