# PTY

PTY 会为命令分配伪终端，适合需要终端行为的工具，例如彩色输出、Shell 脚本、交互式命令或依赖 TTY 判断的 CLI。

## 运行 PTY 命令

TypeScript 示例：

```typescript
import { Sandbox } from "e2b";

const sandbox = await Sandbox.create("code-interpreter-v1", {
  apiKey: process.env.E2B_API_KEY,
  apiUrl: process.env.E2B_API_URL,
  domain: process.env.E2B_DOMAIN,
});

try {
  const result = await sandbox.commands.run("python3 - <<'PY'\nimport sys\nprint(sys.stdout.isatty())\nPY", {
    pty: true,
  });

  console.log(result.stdout.trim());
} finally {
  await sandbox.kill();
}
```

Python 示例：

```python
result = sandbox.commands.run(
    "python3 - <<'PY'\nimport sys\nprint(sys.stdout.isatty())\nPY",
    pty=True,
)
print(result.stdout.strip())
```

## 何时使用 PTY

适合使用 PTY 的场景：

- 需要模拟真实终端行为的命令。
- 工具在非 TTY 环境下会关闭颜色、进度或交互能力。
- 需要给交互式进程发送标准输入。

不建议使用 PTY 的场景：

- 只需要稳定解析 stdout/stderr 的批处理命令。
- 需要严格区分 stdout 和 stderr 的任务。
- 大量结构化日志输出场景。PTY 可能改变输出格式，增加解析成本。

默认情况下，优先使用普通 `commands.run()`。只有命令明确依赖终端行为时，再开启 PTY。
