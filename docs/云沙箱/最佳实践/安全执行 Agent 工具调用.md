# 安全执行 Agent 工具调用

Agent 工具调用是把模型能力接入业务系统的关键路径。模型可以决定调用 `run_tests`、`analyze_csv`、`convert_file` 或内部诊断工具，但真正的风险发生在执行阶段：参数可能不可信，输入文件可能异常，工具脚本可能阻塞，执行结果也需要审计。

云沙箱适合作为工具调用的隔离执行层。业务系统负责模型调用、工具选择、参数校验和权限判断；云沙箱负责运行工具、限制时间、保存临时文件并返回结构化结果。这样可以把“模型会调用工具”变成可控的工程流程。

## 业务场景

- 代码助手调用测试、构建、静态检查工具。
- 数据 Agent 调用 CSV 分析、数据质量检查、报表生成工具。
- 办公 Agent 调用文档转换、表格处理、文件解析工具。
- 运维 Agent 调用只读诊断脚本，返回结构化排查结果。

## 方案设计

工具调用不应等同于任意命令执行。推荐的设计是：

1. 模型只输出工具名和参数。
2. 业务编排器根据白名单找到固定工具入口。
3. 编排器校验参数、租户权限、输入文件和超时时间。
4. 云沙箱执行工具，并返回 JSON 结果、退出码和日志摘要。

这种模式把模型的不确定性限制在“选择哪个工具、给出什么参数”上，避免模型直接控制运行环境。

## 示例代码

以下示例把订单分析作为一个受控工具执行。模型只请求 `summarize_orders`，实际命令由业务侧白名单决定。

```javascript
import { Sandbox } from "e2b";

const sandbox = await Sandbox.create("code-interpreter-v1", {
  apiKey: process.env.E2B_API_KEY,
  apiUrl: process.env.E2B_API_URL,
  domain: process.env.E2B_DOMAIN,
  envs: { TASK_TYPE: "agent-tool-call" },
});

const tools = {
  summarize_orders: {
    command: "python3 tools/summarize_orders.py data/orders.csv",
    cwd: "/tmp/agent-tool-call",
    timeoutMs: 30_000,
  },
};

function validateToolCall(call) {
  if (!tools[call.name]) {
    throw new Error(`Tool is not allowed: ${call.name}`);
  }
  if (call.arguments && Object.keys(call.arguments).length > 0) {
    throw new Error("Unexpected tool arguments");
  }
}

try {
  await sandbox.files.makeDir("/tmp/agent-tool-call");
  await sandbox.files.makeDir("/tmp/agent-tool-call/data");
  await sandbox.files.makeDir("/tmp/agent-tool-call/tools");
  await sandbox.files.write(
    "/tmp/agent-tool-call/data/orders.csv",
    "order_id,customer,amount,status\n1001,Acme,1200,paid\n1002,Acme,900,paid\n1003,Globex,300,refunded\n",
  );
  await sandbox.files.write(
    "/tmp/agent-tool-call/tools/summarize_orders.py",
    `import csv, json
paid_total = 0
with open("data/orders.csv", newline="") as f:
    for row in csv.DictReader(f):
        if row["status"] == "paid":
            paid_total += int(row["amount"])
print(json.dumps({"paid_total": paid_total, "business_summary": f"Paid revenue is {paid_total}."}))
`,
  );

  const call = { name: "summarize_orders", arguments: {} };
  validateToolCall(call);

  const result = await sandbox.commands.run(tools[call.name].command, {
    cwd: tools[call.name].cwd,
    timeoutMs: tools[call.name].timeoutMs,
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

- 工具入口固定，参数显式校验，不把模型输出拼接成 Shell 命令。
- 每个工具设置独立超时、输入大小限制和输出大小限制。
- 工具结果优先返回 JSON，完整日志进入审计系统。
- 凭证按任务注入，使用短有效期和最小权限，不写入模板。
- 对高风险工具增加人工审批或策略引擎，例如文件删除、外部网络访问、写入型云资源操作。

## 可运行示例

本实践对应示例项目中的 `npm run tool-call`。该脚本会在云沙箱中执行受控订单分析工具，并返回结构化业务结果。

## 相关功能

- [运行命令](../功能说明/Commands/运行命令.md)
- [读写文件](../功能说明/Filesystem/读写文件.md)
- [环境变量](../功能说明/Sandbox/环境变量.md)
- [凭证安全](../安全合规/凭证安全.md)
