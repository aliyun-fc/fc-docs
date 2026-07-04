# 使用 Code Interpreter Sandbox

Code Interpreter Sandbox 面向需要运行 Python/Node 脚本、处理用户文件、生成结构化结果或报告产物的 Agent。数据分析类 Agent 的核心诉求，是让模型生成的分析逻辑在隔离环境中处理用户数据，并返回可解释、可下载、可审计的结果。直接在业务服务中执行用户数据和模型生成代码，风险很高：依赖冲突、文件残留、长时间计算、异常日志和数据权限都会变成工程问题。

云沙箱可以作为 Code Interpreter Sandbox 使用。业务系统负责上传数据、生成或选择分析脚本、校验输入输出；云沙箱负责运行脚本、处理临时文件、返回结构化结果。这个模式适合智能问答、运营分析、报表生成、客服数据诊断等场景。

## 业务场景

- 用户上传 CSV，Agent 自动计算指标并给出摘要。
- 运营人员用自然语言触发临时分析，不需要把数据落到主服务运行目录。
- 报表系统把中间计算放到沙箱执行，结果文件再回传给业务系统。
- 多租户场景下，每次分析使用独立沙箱，降低数据串扰风险。

## 推荐流程

建议把分析任务拆成四步：

1. 写入输入数据和分析脚本。
2. 使用固定入口执行脚本，例如 `python3 analyze.py`。
3. 要求脚本输出 JSON 摘要，必要时生成文件产物。
4. 读取结果并销毁沙箱。

如果业务需要 E2B Code Interpreter 的 `run_code` 体验，可以在兼容验证通过后接入；在最佳实践层面，固定脚本入口更容易做审计、超时和输出校验。

## 示例代码

以下示例在沙箱中分析分客群收入，并返回总收入、贡献最高客群和摘要。

```javascript
import { Sandbox } from "e2b";

const sandbox = await Sandbox.create("code-interpreter-v1", {
  apiKey: process.env.E2B_API_KEY,
  apiUrl: process.env.E2B_API_URL,
  domain: process.env.E2B_DOMAIN,
  envs: { TASK_TYPE: "data-analysis" },
});

try {
  await sandbox.files.makeDir("/tmp/data-analysis");
  await sandbox.files.write(
    "/tmp/data-analysis/revenue.csv",
    `date,segment,revenue
2026-07-01,enterprise,1200
2026-07-01,startup,320
2026-07-02,enterprise,1400
2026-07-02,startup,360
`,
  );
  await sandbox.files.write(
    "/tmp/data-analysis/analyze.py",
    `import csv
import json
from collections import defaultdict

revenue_by_segment = defaultdict(int)
with open("revenue.csv", newline="") as f:
    for row in csv.DictReader(f):
        revenue_by_segment[row["segment"]] += int(row["revenue"])

total = sum(revenue_by_segment.values())
top_segment, top_revenue = max(revenue_by_segment.items(), key=lambda item: item[1])

print(json.dumps({
    "total_revenue": total,
    "top_segment": top_segment,
    "top_segment_revenue": top_revenue,
    "summary": f"{top_segment} contributes {round(top_revenue / total * 100, 1)}% of revenue."
}, ensure_ascii=False))
`,
  );

  const result = await sandbox.commands.run("python3 analyze.py", {
    cwd: "/tmp/data-analysis",
    timeoutMs: 30_000,
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

- 输入文件要限制大小、类型和路径，避免一次任务占用过多内存或磁盘。
- 输出优先使用 JSON 摘要。图表、表格、报告文件可以写入 `/tmp` 后再下载。
- 对分析代码做版本化。生产系统不要只保存模型生成的自然语言解释。
- 常用依赖如 `pandas`、`openpyxl`、绘图库和业务 SDK 建议放到模板。
- 对用户可见结果和排障日志分开处理，避免把完整堆栈或敏感数据直接返回。

## 可运行示例

本实践对应示例项目中的 `npm run data-analysis`。该脚本会在云沙箱中写入 CSV 和分析脚本，并返回结构化业务摘要。

## 相关功能

- [读写文件](../功能说明/Filesystem/读写文件.md)
- [上传和下载文件](../功能说明/Filesystem/上传和下载文件.md)
- [运行命令](../功能说明/Commands/运行命令.md)
- [Code Interpreter 概览](../功能说明/Code%20Interpreter/概览.md)
