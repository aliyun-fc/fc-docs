# Claude Code 自定义镜像

[Claude Code](https://docs.anthropic.com/en/docs/claude-code) 是 Anthropic 的终端 AI 编程 Agent，可在沙箱内读代码、改文件、执行命令。我们已在各地域 ACR 预置 Claude Code 镜像，您无需自行推送镜像或配置 ACREE，选取下方 VPC 镜像地址，通过 `from_image` + `Template.build` 构建模板后即可使用。

首次使用请先完成 [通过 SDK 创建第一个云沙箱](https://help.aliyun.com/zh/functioncompute/create-your-first-cloud-sandbox-via-the-sdk) 中的 SLR 授权、API Key 与 SDK 配置。

---

## 前置条件

- 已完成 [SDK 接入](https://help.aliyun.com/zh/functioncompute/create-your-first-cloud-sandbox-via-the-sdk)（E2B API Key、`api_url`、`domain`）
- 已安装依赖：`pip install e2b e2b-code-interpreter`
- 已准备模型 API Key，创建沙箱时通过 `envs` 注入 — 镜像内不预置
  - 海外：[Anthropic Console](https://console.anthropic.com/) 获取 `ANTHROPIC_API_KEY`
  - 国内：[百炼控制台](https://bailian.console.aliyun.com/) 获取 API Key（`sk-` 开头）

---

## 镜像地址

按地域选取 `FROM_IMAGE`，须使用 **VPC 内网地址**（域名含 `-vpc`）：

| Region | 镜像（VPC） |
|--------|-------------|
| cn-beijing | `fc-e2b-registry-vpc.cn-beijing.cr.aliyuncs.com/runtime/claude-code:v0.0.32` |
| cn-shenzhen | `fc-e2b-registry-vpc.cn-shenzhen.cr.aliyuncs.com/runtime/claude-code:v0.0.32` |
| ap-southeast-1 | `fc-e2b-registry-vpc.ap-southeast-1.cr.aliyuncs.com/runtime/claude-code:v0.0.32` |
| cn-hongkong | `fc-e2b-registry-vpc.cn-hongkong.cr.aliyuncs.com/runtime/claude-code:v0.0.32` |
| cn-shanghai | `fc-e2b-registry-vpc.cn-shanghai.cr.aliyuncs.com/runtime/claude-code:v0.0.32` |
| cn-hangzhou | `fc-e2b-registry-vpc.cn-hangzhou.cr.aliyuncs.com/runtime/claude-code:v0.0.32` |

推荐构建规格：`cpu_count=2`，`memory_mb=8192`。

---

## 快速开始

以下以北京地域为例，分四步：**构建 Template → 创建 Sandbox → 运行 Claude Code → 销毁沙箱**。

### 构建 Template

```python
import time

from e2b import Template, default_build_logger

FROM_IMAGE = "fc-e2b-registry-vpc.cn-beijing.cr.aliyuncs.com/runtime/claude-code:v0.0.25"

OPTS = {
    "api_key": "<你的 E2B API Key>",
    "api_url": "https://api.cn-beijing.e2b.fc.aliyuncs.com",
    "domain": "cn-beijing.e2b.fc.aliyuncs.com",
}

build = Template.build(
    Template().from_image(FROM_IMAGE),
    alias=f"claude-code-{int(time.time())}",
    cpu_count=2,
    memory_mb=8192,
    on_build_logs=default_build_logger(),
    **OPTS,
)

print(f"template_id: {build.template_id}")   # 保存，后续可复用
```

构建完成后控制台模板状态应为 `ready`。同一 `template_id` 可多次创建 Sandbox，无需每次重新构建。

### 创建 Sandbox

国内用户推荐使用百炼 DashScope，海外用户可使用 Anthropic 直连，以下 Sandbox.create 步骤二选一即可。

```python
from e2b_code_interpreter import Sandbox

# 国内：推荐使用百炼 DashScope
sandbox = Sandbox.create(
    template=build.template_id,
    envs={
        "ANTHROPIC_AUTH_TOKEN": "<your-bailian-api-key>",
        "ANTHROPIC_BASE_URL": "https://dashscope.aliyuncs.com/apps/anthropic",
        "ANTHROPIC_MODEL": "qwen3.6-flash",
        "ANTHROPIC_DEFAULT_HAIKU_MODEL": "qwen3.6-flash",
        "ANTHROPIC_DEFAULT_SONNET_MODEL": "qwen3.6-flash",
        "ANTHROPIC_DEFAULT_OPUS_MODEL": "qwen3.6-flash",
    },
    timeout=600,
    **OPTS,
)

# 海外：Anthropic 直连
sandbox = Sandbox.create(
    template=build.template_id,
    envs={"ANTHROPIC_API_KEY": "<your-anthropic-api-key>"},
    timeout=600,
    **OPTS,
)

# 首次运行前须初始化 `~/.claude.json`，否则可能报配置损坏。
sandbox.commands.run("echo '{}' > /home/user/.claude.json")
```

### 运行 Claude Code

非交互模式使用 `-p`；在沙箱内可加 `--dangerously-skip-permissions` 跳过权限确认。建议加 `< /dev/null` 避免 stdin 等待警告：

```python
result = sandbox.commands.run(
    'claude --dangerously-skip-permissions < /dev/null '
    '-p "Create a hello world HTTP server in Go"',
    timeout=0,
)
print(result.stdout)
```

### 销毁沙箱

任务完成后释放资源：

```python
sandbox.kill()
```

---

## 环境概览

| 项目 | 规格 |
|------|------|
| 操作系统 | Ubuntu 25.04 |
| Claude Code 路径 | `/home/user/.local/bin/claude` |
| 默认用户 / 工作目录 | `user` / `/home/user` |
| MCP Gateway | **不支持** |

---

## 使用场景

以下示例假设已完成 Template 构建，`sandbox` 已创建且已初始化 `~/.claude.json`。

### 克隆仓库并执行任务

```python
sandbox.git.clone(
    "https://github.com/your-org/your-repo.git",
    path="/home/user/repo",
    username="x-access-token",
    password="<your-github-token>",
    depth=1,
)

result = sandbox.commands.run(
    'cd /home/user/repo && claude --dangerously-skip-permissions < /dev/null '
    '-p "Add error handling to all API endpoints"',
    on_stdout=lambda data: print(data, end=""),
    timeout=0,
)

diff = sandbox.commands.run("cd /home/user/repo && git diff")
print(diff.stdout)
```

### 获取结构化 JSON 输出

```python
import json

result = sandbox.commands.run(
    'claude --dangerously-skip-permissions --output-format json < /dev/null '
    '-p "List all files and describe each" 2>&1',
    timeout=0,
)

for line in reversed(result.stdout.strip().split("\n")):
    if line.startswith("{"):
        response = json.loads(line)
        break
else:
    raise RuntimeError("no JSON in output")

print(response.get("result") or response)
```

### 流式 JSONL 输出

```python
import json

def handle_event(data):
    for line in data.strip().split("\n"):
        if line.startswith("{"):
            event = json.loads(line)
            if event["type"] == "assistant":
                usage = event.get("message", {}).get("usage", {})
                print(f"[assistant] tokens: {usage.get('output_tokens')}")
            elif event["type"] == "result":
                print(f"[done] {event['subtype']} in {event['duration_ms']}ms")

sandbox.commands.run(
    'claude --dangerously-skip-permissions --verbose --output-format stream-json < /dev/null '
    '-p "Find and fix all TODO comments" 2>&1',
    on_stdout=handle_event,
    timeout=0,
)
```

### 恢复会话

```python
import json

initial = sandbox.commands.run(
    'claude --dangerously-skip-permissions --output-format json < /dev/null '
    '-p "Analyze the codebase and create a refactoring plan" 2>&1',
    timeout=0,
)

for line in reversed(initial.stdout.strip().split("\n")):
    if line.startswith("{"):
        session_id = json.loads(line)["session_id"]
        break

sandbox.commands.run(
    f'claude --dangerously-skip-permissions --resume {session_id} < /dev/null '
    f'-p "Now implement step 1 of the plan"',
    on_stdout=lambda data: print(data, end=""),
    timeout=0,
)
```

### 自定义系统提示词

```python
sandbox.files.write("/home/user/repo/CLAUDE.md", """
You are working on a Go microservice.
Always use structured logging with slog.
Follow the project's error handling conventions in pkg/errors.
""")

sandbox.commands.run(
    'cd /home/user/repo && claude --dangerously-skip-permissions < /dev/null '
    '-p "Add a /healthz endpoint"',
    timeout=0,
)
```

### 连接 MCP 工具

Claude Code 原生支持 [MCP](https://modelcontextprotocol.io/)。可通过 `claude mcp add` 手动注册 MCP Server，沙箱具备出站网络。

**stdio 本地进程（推荐）：**

```python
sandbox.commands.run(
    "claude mcp add --transport stdio fs -- "
    "npx -y @modelcontextprotocol/server-filesystem /home/user",
    timeout=180,
)

result = sandbox.commands.run(
    'claude --dangerously-skip-permissions < /dev/null '
    '-p "Use the fs MCP tool to list /home/user and summarize top-level entries."',
    timeout=0,
)
```

**HTTP 远程 Server：**

```python
sandbox.commands.run(
    "claude mcp add --transport http deepwiki https://mcp.deepwiki.com/mcp",
)

result = sandbox.commands.run(
    'claude --dangerously-skip-permissions < /dev/null '
    '-p "Use deepwiki MCP: what tools are available?"',
    timeout=0,
)
```

| 能力 | 支持情况 |
|------|----------|
| `claude mcp add`（stdio / HTTP） | **支持** |
| SDK `mcp` 创建参数 | **不支持** |
| `getMcpUrl()` / `getMcpToken()` | **不支持** |

---

## 计费说明

Sandbox 按 CPU、内存规格与运行时长计费；模型 API 调用费用由 Anthropic、百炼等模型服务单独结算。详见 [计费概述](../../产品计费/计费概述.md)。

---

## 常见问题

| 现象 | 处理 |
|------|------|
| 报配置损坏 | `echo '{}' > /home/user/.claude.json` |
| Agent 无响应 | 确认 `envs` 已注入模型 Key；国内用百炼 `envs` 配置 |
| 构建失败 | 确认 `FROM_IMAGE` 为 VPC 地址且与地域匹配 |
| 其他 SDK / 构建问题 | 见[自定义模板 — 问题排查](https://help.aliyun.com/zh/functioncompute/custom-template#d21d3cbd8b8xo) |

---
