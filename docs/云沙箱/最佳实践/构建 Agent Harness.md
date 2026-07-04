# 构建 Agent Harness

Agent Harness 是把模型变成可执行系统的中间层。它负责工具路由、上下文管理、权限审批、轨迹记录、失败重试和结果汇总。没有 Harness，Agent 调用工具很容易变成零散脚本；没有隔离执行层，Harness 又会把不可信代码、用户文件、第三方依赖和长时间任务压到业务服务里。

云沙箱适合作为 Agent Harness 的执行层。Harness 决定“做什么、能不能做、如何记录”；云沙箱负责“在哪里执行、如何隔离、如何回收”。这个分工能让 Agent 系统同时具备业务可控性和工程可复现性。

## 业务场景

- 企业内部 Agent 需要调用多个工具，但每次执行都要隔离、审计和回收。
- Coding Agent 需要在仓库中运行测试、生成 diff、执行修复。
- 数据 Agent 需要处理用户上传文件，并返回结构化结果。
- 多租户 Agent 平台需要按任务隔离文件、进程、日志和临时凭证。

## 方案设计

一个面向生产的 Harness 通常包含五个模块：

1. 任务入口：接收用户请求、租户身份、任务上下文和策略配置。
2. 工具注册表：维护可调用工具、参数 schema、超时和权限要求。
3. 沙箱执行器：创建云沙箱，写入输入文件和工具脚本，执行命令。
4. 轨迹记录器：记录 tool call、Sandbox ID、stdout/stderr、exitCode、产物路径。
5. 决策层：根据执行结果决定继续调用、交给人工确认或结束任务。

## 示例代码

以下示例模拟一个 Harness：它先分析订单数据，再执行一条业务规则校验，最终根据校验结果决定是否允许自动导入。

```javascript
import { Sandbox } from "e2b";

const sandbox = await Sandbox.create("code-interpreter-v1", {
  apiKey: process.env.E2B_API_KEY,
  apiUrl: process.env.E2B_API_URL,
  domain: process.env.E2B_DOMAIN,
  metadata: { taskId: "task-harness-001" },
});

const tools = {
  profile_dataset: {
    command: "python3 tools/profile_dataset.py input/orders.csv",
    cwd: "/tmp/agent-harness",
    timeoutMs: 30_000,
  },
  validate_business_rule: {
    command: "python3 tools/validate_business_rule.py input/orders.csv",
    cwd: "/tmp/agent-harness",
    timeoutMs: 30_000,
  },
};

try {
  await sandbox.files.makeDir("/tmp/agent-harness");
  await sandbox.files.makeDir("/tmp/agent-harness/input");
  await sandbox.files.makeDir("/tmp/agent-harness/tools");
  await sandbox.files.write(
    "/tmp/agent-harness/input/orders.csv",
    "order_id,customer,amount,status\n1001,Acme,1200,paid\n1002,Acme,900,paid\n1003,Globex,300,refunded\n1004,Initech,0,paid\n",
  );
  await sandbox.files.write(
    "/tmp/agent-harness/tools/profile_dataset.py",
    `import csv, json, sys
rows = list(csv.DictReader(open(sys.argv[1], newline="")))
print(json.dumps({
    "row_count": len(rows),
    "columns": list(rows[0].keys()) if rows else [],
    "paid_rows": sum(1 for row in rows if row["status"] == "paid")
}, ensure_ascii=False))
`,
  );
  await sandbox.files.write(
    "/tmp/agent-harness/tools/validate_business_rule.py",
    `import csv, json, sys
violations = []
for row in csv.DictReader(open(sys.argv[1], newline="")):
    if row["status"] == "paid" and int(row["amount"]) <= 0:
        violations.append({"order_id": row["order_id"], "reason": "paid order amount must be positive"})
print(json.dumps({
    "passed": len(violations) == 0,
    "violations": violations,
    "recommendation": "block_auto_import" if violations else "ready_for_import"
}, ensure_ascii=False))
`,
  );

  const trace = [];
  for (const name of ["profile_dataset", "validate_business_rule"]) {
    const tool = tools[name];
    const result = await sandbox.commands.run(tool.command, {
      cwd: tool.cwd,
      timeoutMs: tool.timeoutMs,
    });
    if (result.exitCode !== 0) {
      throw new Error(result.stderr || result.stdout);
    }
    trace.push({ tool: name, result: JSON.parse(result.stdout) });
  }

  console.log({ sandboxId: sandbox.sandboxId, trace });
} finally {
  await sandbox.kill();
}
```

## 上线建议

- 工具注册表必须由业务系统维护，不让模型直接生成任意命令。
- 每个工具设置独立超时、输入大小、输出大小和权限等级。
- Harness 需要记录完整执行轨迹，但对用户只展示摘要、关键日志和产物链接。
- 高风险动作必须进入人工确认，例如写入外部系统、发送消息、删除文件、访问敏感数据。
- 沙箱内文件系统是任务级临时状态，长期状态应写入外部数据库、对象存储或业务系统。

## 可运行示例

本实践对应示例项目中的 `npm run agent-harness`。该脚本会在云沙箱中执行两个工具调用，记录 trace，并输出最终业务决策。

## 相关功能

- [安全执行 Agent 工具调用](./安全执行%20Agent%20工具调用.md)
- [运行 Agent Skills](./运行%20Agent%20Skills.md)
- [运行命令](../功能说明/Commands/运行命令.md)
- [元数据](../功能说明/Sandbox/元数据.md)
