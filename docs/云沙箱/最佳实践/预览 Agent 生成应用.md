# 预览 Agent 生成应用

App Builder、Coding Agent 和自动化测试系统经常需要启动一个临时 Web 服务，让用户或上层系统检查生成结果。预览能力的价值不只是“拿到一个 URL”，而是把代码生成、服务启动、健康检查和结果确认放进同一个隔离环境。

云沙箱适合作为临时预览环境。Agent 可以把生成的前端页面、后端服务或静态文件写入沙箱，使用后台命令启动服务，再通过本地健康检查确认服务已经可用。需要对外暴露时，可以结合 `getHost(port)` 获取访问地址，并按当前访问控制策略验证可访问性。

## 业务场景

- App Builder 生成页面后，立即启动预览服务供用户确认。
- Coding Agent 修改前端代码后，返回临时访问地址和构建日志。
- 自动化测试在沙箱中启动 Web 服务，再运行接口检查或页面冒烟。
- 多个用户并发生成应用时，每个任务使用独立预览环境。

## 方案设计

建议把预览链路拆成四步：

1. 写入生成物，例如 `index.html`、应用代码或构建产物。
2. 使用后台命令启动服务，并记录进程 ID。
3. 在沙箱内做健康检查，确认服务已经监听并返回预期内容。
4. 返回预览地址或检查结果，任务结束后终止后台进程并释放沙箱。

如果要把预览地址直接给最终用户，需要额外评估访问控制、敏感文件暴露、服务生命周期和调试接口风险。

## 示例代码

以下示例在沙箱中启动静态页面服务，并先用沙箱内本地请求完成健康检查。

```javascript
import { Sandbox } from "e2b";

const sandbox = await Sandbox.create("code-interpreter-v1", {
  apiKey: process.env.E2B_API_KEY,
  apiUrl: process.env.E2B_API_URL,
  domain: process.env.E2B_DOMAIN,
  envs: { TASK_TYPE: "web-preview" },
});

let server;

try {
  await sandbox.files.makeDir("/tmp/web-preview");
  await sandbox.files.write(
    "/tmp/web-preview/index.html",
    `<!doctype html>
<html>
  <head><title>Agent Preview</title></head>
  <body><h1>Agent generated preview</h1></body>
</html>
`,
  );

  server = await sandbox.commands.run("python3 -m http.server 8000 --bind 127.0.0.1", {
    cwd: "/tmp/web-preview",
    background: true,
  });

  const check = await sandbox.commands.run(
    `python3 - <<'PY'
import time
import urllib.request

last_error = None
for _ in range(30):
    try:
        body = urllib.request.urlopen("http://127.0.0.1:8000", timeout=2).read().decode()
        assert "Agent generated preview" in body
        print("preview_ok")
        break
    except Exception as exc:
        last_error = exc
        time.sleep(1)
else:
    raise RuntimeError(last_error)
PY`,
    { timeoutMs: 30_000 },
  );
  if (check.exitCode !== 0) {
    throw new Error(check.stderr || check.stdout);
  }

  console.log({
    localCheck: check.stdout.trim(),
    previewHost: sandbox.getHost(8000),
  });
} finally {
  if (server?.pid) {
    await sandbox.commands.kill(server.pid);
  }
  await sandbox.kill();
}
```

## 上线建议

- 服务启动后先做沙箱内健康检查，再把预览地址交给用户。
- 对外预览前确认目录中没有凭证、日志、环境变量文件或调试接口。
- 预览服务应设置任务级生命周期，不建议作为长期生产服务使用。
- 如果公网访问返回权限错误，应按当前云沙箱访问控制策略排查，不要在业务系统中绕过鉴权。
- 前端构建、依赖安装和浏览器测试建议放到自定义模板中预装依赖。

## 可运行示例

本实践对应示例项目中的 `npm run web-preview`。该脚本会在云沙箱中启动本地预览服务，完成健康检查，并输出 `getHost(port)` 返回的访问地址。

## 相关功能

- [后台命令](../功能说明/Commands/后台命令.md)
- [终止命令](../功能说明/Commands/终止命令.md)
- [Sandbox 公网 URL](../功能说明/Network/Sandbox%20公网%20URL.md)
- [访问地址](../功能说明/Network/访问地址.md)
