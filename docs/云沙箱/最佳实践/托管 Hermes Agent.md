# 托管 Hermes Agent

Hermes Agent 是 Nous Research 开源的自进化 Agent。它支持 CLI/TUI、消息网关、持久记忆、Skills、MCP、浏览器自动化、终端工具、子 Agent 和定时任务。Hermes 官方文档中，Linux/macOS/WSL2 可以通过安装脚本部署 CLI；首次使用可通过 `hermes setup` 或 `hermes setup --portal` 配置模型和工具；日常交互可以使用 `hermes`、`hermes --tui` 或 `hermes chat -q`。

云沙箱（FC Agent Sandbox）适合把 Hermes 作为完整 Agent 应用托管到云上隔离环境中：把 Hermes CLI、Python/Node 依赖、浏览器依赖和常用工具预装进模板；创建沙箱后通过 `commands.run()` 启动 CLI、TUI、消息 Gateway 或自定义服务；如果模板中启用了 HTTP 控制台、消息网关回调服务或调试服务，可以通过 `getHost(port)` 获取访问地址。

## 适用场景

- 团队希望把 Hermes Agent 运行在云上，而不是开发者本地机器。
- 企业要评测 Hermes 的 Skills、MCP、浏览器自动化和终端工具，要求隔离执行环境。
- 业务需要为每个客户、项目或评测任务启动独立 Agent 环境，任务结束后释放。
- Agent 需要执行命令、处理文件、访问浏览器或调用外部工具，希望通过沙箱限制影响范围。

## 推荐架构

建议使用“Hermes 模板 + 沙箱实例 + 外部状态”的架构：

- **自定义模板**：预装 Hermes CLI、Python、Node.js、Playwright/浏览器依赖、`ripgrep`、`ffmpeg` 等运行组件。
- **云沙箱（FC Agent Sandbox）**：按任务、用户或项目创建 Hermes 运行环境，执行 CLI/TUI、Gateway、Skills 和工具调用。
- **外部系统**：保存用户身份、长期记忆、审计日志、模型凭证和业务数据。

Hermes 有自己的安全机制，例如命令审批、YOLO 模式提示和危险命令阻断。云沙箱提供的是更外层的运行隔离和生命周期管理，两者应叠加使用。

## 构建 Hermes 模板

Hermes 官方安装脚本会处理 Python、Node.js、`ripgrep`、`ffmpeg`、虚拟环境和全局 `hermes` 命令。用于云沙箱模板时，建议先做专用镜像，并在镜像构建阶段完成安装。

```dockerfile
FROM debian:bookworm

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    ca-certificates curl git xz-utils build-essential \
  && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-browser

ENV PATH="/root/.local/bin:/root/.hermes/hermes-agent/venv/bin:${PATH}"
WORKDIR /workspace
```

如果需要浏览器自动化，不要使用 `--skip-browser`，并按 Hermes 官方建议补齐 Playwright/Chromium 的系统依赖。浏览器能力对镜像体积、内存和启动耗时更敏感，建议单独做模板验证。

构建并推送镜像后，通过 E2B SDK 创建云沙箱模板：

```python
import os
import time
from e2b import Template, default_build_logger

image = os.environ["HERMES_IMAGE"]

build = Template.build(
    Template().from_image(image),
    name=f"hermes-agent-{int(time.time())}",
    cpu_count=2,
    memory_mb=4096,
    api_key=os.environ["E2B_API_KEY"],
    api_url=os.environ["E2B_API_URL"],
    domain=os.environ["E2B_DOMAIN"],
    on_build_logs=default_build_logger(),
)

print("template_id:", build.template_id)
```

## 启动并验证 Hermes

创建沙箱后，先用 CLI 验证 Hermes 是否可用。首次配置可以通过 `hermes setup`、`hermes model`、`hermes tools` 或 `hermes gateway setup` 完成；生产环境建议把配置整理成初始化脚本，并通过运行时环境变量注入模型和工具凭证。

```typescript
import { Sandbox } from "e2b";

const template = process.env.HERMES_TEMPLATE_ID;
if (!template) {
  throw new Error("HERMES_TEMPLATE_ID is required");
}

const sandbox = await Sandbox.create(template, {
  apiKey: process.env.E2B_API_KEY,
  apiUrl: process.env.E2B_API_URL,
  domain: process.env.E2B_DOMAIN,
  envs: {
    HERMES_HOME: "/workspace/.hermes",
    // 按 Hermes 的 provider 配置要求注入模型或 Nous Portal 相关凭证。
    // 不要把真实凭证写入模板或代码仓库。
  },
  metadata: {
    app: "hermes",
    purpose: "agent-demo",
  },
});

try {
  await sandbox.commands.run("mkdir -p /workspace/.hermes");

  const doctor = await sandbox.commands.run("hermes doctor", {
    cwd: "/workspace",
    timeoutMs: 60_000,
  });
  console.log(doctor.stdout);

  const reply = await sandbox.commands.run(
    `hermes chat -q "检查当前目录，说明这个运行环境是否已经准备好执行 Agent 任务"`,
    {
      cwd: "/workspace",
      timeoutMs: 180_000,
    },
  );
  console.log(reply.stdout);
} finally {
  // 演示环境可以保留沙箱给用户继续交互；自动化测试结束后应释放沙箱。
  // await sandbox.kill();
}
```

如果要使用交互式终端，可以通过 PTY 运行 `hermes` 或 `hermes --tui`；如果要做自动化任务，优先使用 `hermes chat -q`、`hermes model`、`hermes tools`、`hermes skills` 等非交互命令。

## 访问 Gateway 或自定义 Web 服务

Hermes 官方 CLI 是 TUI，不是 Web UI。云沙箱文档不应把 Hermes 写成必然存在 Web 控制台的产品。更稳妥的写法是：Hermes 本体通过 CLI/TUI 和消息平台使用；如果你的模板额外启动了 Hermes Gateway、回调服务、自定义管理台或调试服务，则像访问其他沙箱内 HTTP 服务一样使用 `getHost(port)`。

```typescript
const process = await sandbox.commands.run(
  "start-hermes-gateway --host 0.0.0.0 --port 8080",
  {
    cwd: "/workspace",
    background: true,
    timeoutMs: 30_000,
  },
);

const url = `https://${sandbox.getHost(8080)}`;
console.log(url);
console.log(process.pid);
```

其中 `start-hermes-gateway` 是模板内的启动脚本示例，不是 Hermes 官方固定命令。脚本可以封装当前 Hermes 版本的 Gateway、消息平台回调服务或团队自定义控制台。正式写入模板前，先在沙箱中用 `hermes gateway setup`、`hermes --help` 和对应服务的 `--help` 确认当前版本的命令形态。只要服务最终监听在沙箱内某个端口，就可以通过 `getHost(port)` 获取访问地址。

## 连接已有 Hermes 沙箱

对于需要跨请求继续管理的 Hermes 实例，保存 `sandbox.sandboxId`，后续通过 `Sandbox.connect()` 连接：

```typescript
const sandboxId = process.env.HERMES_SANDBOX_ID;
if (!sandboxId) {
  throw new Error("HERMES_SANDBOX_ID is required");
}

const sandbox = await Sandbox.connect(sandboxId, {
  apiKey: process.env.E2B_API_KEY,
  apiUrl: process.env.E2B_API_URL,
  domain: process.env.E2B_DOMAIN,
});

const sessions = await sandbox.commands.run("hermes --continue --help", {
  cwd: "/workspace",
});

console.log(sessions.stdout);
```

如果沙箱只是一次性执行任务，任务完成后应主动 `kill()`；如果需要保留会话现场，可以结合暂停与恢复能力管理生命周期。

## 最佳实践

- **先跑通 CLI 基线**：先验证 `hermes doctor`、`hermes chat -q`，再启用 Gateway、Skills、MCP、浏览器和定时任务。
- **模板固定运行环境**：Hermes、Python、Node.js、浏览器依赖和常用工具放入模板，避免每次创建沙箱后重复安装。
- **状态外置**：Hermes 的长期记忆、配置、审计日志和业务数据应外置。沙箱本地文件系统适合保存任务级临时状态，不适合作为唯一持久化来源。
- **谨慎使用 YOLO 模式**：Hermes 支持关闭审批的 YOLO 模式。只有在一次性、可回收、低风险的沙箱任务中才考虑使用，并配合外层权限控制。
- **逐步启用工具能力**：先启用文件和终端工具，再按需启用浏览器、MCP、消息平台和定时任务。每启用一类工具，都应补充权限边界和日志采集。

## 相关功能

- [构建模板](../功能说明/Templates/构建模板.md)
- [运行命令](../功能说明/Commands/运行命令.md)
- [PTY](../功能说明/Commands/PTY.md)
- [Sandbox 公网 URL](../功能说明/Network/Sandbox%20公网%20URL.md)
- [连接沙箱](../功能说明/Sandbox/连接沙箱.md)
- [凭证安全](../安全合规/凭证安全.md)
