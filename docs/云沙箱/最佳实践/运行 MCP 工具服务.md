# 运行 MCP 工具服务

MCP 的价值在于把工具发现、参数描述、调用入口和结果格式统一起来。对企业 Agent 来说，这能降低工具接入成本，也便于把内部能力按协议暴露给 Agent。但需要明确边界：本文介绍的是在云沙箱中运行自定义 MCP 风格工具服务，不是云沙箱兼容 E2B MCP Gateway。

更稳妥的落地方式，是把 Agent Runner 和工具服务放在同一个云沙箱中，通过 `localhost` 调用。这样既能采用 MCP 风格的工具抽象，又不需要把工具服务直接暴露到公网。任务结束后销毁沙箱，工具服务和临时状态一起释放。

## 业务场景

- 为单次 Agent 任务启动项目专属工具服务，任务结束后销毁。
- 把企业内部工具封装成 MCP 风格接口，但运行环境与主业务服务隔离。
- 在沙箱中同时运行 Agent Runner、工具服务和临时文件处理逻辑。
- 对不完全可信的工具参数和输入文件做隔离执行。

## 方案设计

推荐流程如下：

1. 业务系统创建云沙箱，写入工具服务和 Agent Runner。
2. 使用后台命令启动工具服务，监听 `127.0.0.1`。
3. Agent Runner 在同一个沙箱内通过 `localhost` 调用工具服务。
4. 工具服务返回结构化结果，Runner 汇总后输出。
5. 业务系统读取结果，终止后台进程并释放沙箱。

这种模式适合任务级工具服务，不适合作为长期在线 API 网关。如果需要沙箱外部 MCP Client 直接访问，应把公网访问、鉴权、会话管理和访问控制作为独立设计项。

## 示例代码

以下示例在沙箱内启动一个 JSON-RPC 工具服务，提供 `score_lead` 工具，并在同一沙箱内用客户端调用。

```javascript
import { Sandbox } from "e2b";

const sandbox = await Sandbox.create("code-interpreter-v1", {
  apiKey: process.env.E2B_API_KEY,
  apiUrl: process.env.E2B_API_URL,
  domain: process.env.E2B_DOMAIN,
  envs: { TASK_TYPE: "mcp-tool-service" },
});

const server = `from http.server import BaseHTTPRequestHandler, HTTPServer
import json

def score_lead(arguments):
    employees = int(arguments.get("employees", 0))
    intent = arguments.get("intent", "low")
    score = min(100, employees // 10 + (40 if intent == "high" else 10))
    return {"content": [{"type": "text", "text": json.dumps({
        "score": score,
        "tier": "enterprise" if score >= 70 else "growth",
        "next_action": "route_to_sales" if score >= 70 else "nurture"
    })}]}

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("content-length", "0"))
        request = json.loads(self.rfile.read(length))
        method = request.get("method")
        params = request.get("params") or {}
        if method == "tools/call":
            result = score_lead(params.get("arguments") or {})
        else:
            result = {"ok": True}
        body = json.dumps({"jsonrpc": "2.0", "id": request.get("id"), "result": result}).encode()
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return

HTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
`;

const client = `import json, urllib.request
body = json.dumps({
    "jsonrpc": "2.0",
    "id": "tools/call",
    "method": "tools/call",
    "params": {"name": "score_lead", "arguments": {"employees": 820, "intent": "high"}}
}).encode()
request = urllib.request.Request("http://127.0.0.1:8765", data=body, headers={"content-type": "application/json"})
print(urllib.request.urlopen(request, timeout=5).read().decode())
`;

let serverCommand;

try {
  await sandbox.files.makeDir("/tmp/mcp-tool-server");
  await sandbox.files.write("/tmp/mcp-tool-server/server.py", server);
  await sandbox.files.write("/tmp/mcp-tool-server/client.py", client);

  serverCommand = await sandbox.commands.run("python3 server.py", {
    cwd: "/tmp/mcp-tool-server",
    background: true,
  });

  const result = await sandbox.commands.run("python3 client.py", {
    cwd: "/tmp/mcp-tool-server",
    timeoutMs: 30_000,
  });
  if (result.exitCode !== 0) {
    throw new Error(result.stderr || result.stdout);
  }

  console.log(JSON.parse(result.stdout));
} finally {
  if (serverCommand?.pid) {
    await sandbox.commands.kill(serverCommand.pid);
  }
  await sandbox.kill();
}
```

## 上线建议

- 优先让 Agent Runner 和工具服务在同一个沙箱内本地调用，减少公网暴露面。
- 只注册本次任务需要的工具，不要把内部能力一次性暴露给模型。
- `inputSchema` 只能描述参数，业务侧仍需要做强校验。
- 后台工具服务必须在任务结束时终止，避免进程残留。
- 不要把该模式描述为托管 MCP Gateway。服务目录、统一鉴权、跨服务路由需要独立产品能力支持。

## 可运行示例

本实践对应示例项目中的 `npm run mcp`。该脚本会在云沙箱内启动工具服务，并通过沙箱内客户端完成调用。

## 相关功能

- [后台命令](../功能说明/Commands/后台命令.md)
- [连接命令](../功能说明/Commands/连接命令.md)
- [运行命令](../功能说明/Commands/运行命令.md)
- [「不兼容」MCP gateway 概览](../功能说明/MCP%20gateway/「不兼容」概览.md)
