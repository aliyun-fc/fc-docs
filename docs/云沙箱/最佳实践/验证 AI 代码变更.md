# 验证 AI 代码变更

AI 生成补丁后，最容易被低估的是验证成本。代码看起来合理，不代表能通过测试；本地环境通过，也不代表能在干净环境中复现。把验证放到云沙箱中，可以让每次 AI 代码变更都在隔离、可回收、可记录的环境里运行。

这个实践适合放在代码助手、代码审查机器人、自动修复系统和 CI 前置验证中。云沙箱不是替代 CI，而是提供更靠近 Agent 执行过程的第一道验证门槛：补丁生成后立即运行测试，把失败原因反馈给 Agent 或开发者。

## 业务场景

- AI 代码修复后，在提交代码审查前自动跑最小测试集。
- 代码审查机器人根据失败测试要求 Agent 继续修改。
- 多个候选补丁并行验证，只把通过验证的补丁交给开发者。
- 企业对不可信仓库或用户代码执行验证，避免污染主 CI Worker。

## 方案设计

推荐把验证链路拆成三段：

1. 准备干净工作区，写入基线代码、测试文件和候选补丁。
2. 运行测试命令，记录退出码、stdout、stderr 和关键报告文件。
3. 根据测试结果决定继续迭代、提交人工审查或丢弃补丁。

验证系统的判断标准应以命令退出码和结构化测试报告为准，不应只依赖模型对日志的解释。

## 示例代码

以下示例先验证一个错误折扣逻辑，随后写入 AI 生成的修复，再以测试结果作为合入门禁。

```javascript
import { Sandbox } from "e2b";

const sandbox = await Sandbox.create("code-interpreter-v1", {
  apiKey: process.env.E2B_API_KEY,
  apiUrl: process.env.E2B_API_URL,
  domain: process.env.E2B_DOMAIN,
  envs: { TASK_TYPE: "ai-change-validation" },
});

try {
  await sandbox.files.makeDir("/tmp/change-validation");
  await sandbox.files.write(
    "/tmp/change-validation/discount.py",
    `def final_price(amount, vip=False):
    rate = 0.8 if vip else 1.0
    return round(amount * rate, 2)
`,
  );
  await sandbox.files.write(
    "/tmp/change-validation/test_discount.py",
    `import unittest
from discount import final_price

class DiscountTest(unittest.TestCase):
    def test_vip_discount(self):
        self.assertEqual(final_price(100, vip=True), 90)

    def test_regular_price(self):
        self.assertEqual(final_price(100), 100)

if __name__ == "__main__":
    unittest.main()
`,
  );

  await sandbox.commands.run("python3 -m unittest -v > first.out 2>first.err; echo $? > first.exit", {
    cwd: "/tmp/change-validation",
    timeoutMs: 30_000,
  });
  const firstExit = await sandbox.files.read("/tmp/change-validation/first.exit");

  await sandbox.files.write(
    "/tmp/change-validation/discount.py",
    `def final_price(amount, vip=False):
    rate = 0.9 if vip else 1.0
    return round(amount * rate, 2)
`,
  );

  const secondRun = await sandbox.commands.run("rm -rf __pycache__ && python3 -m unittest -v", {
    cwd: "/tmp/change-validation",
    timeoutMs: 30_000,
  });
  if (secondRun.exitCode !== 0) {
    throw new Error(secondRun.stderr || secondRun.stdout);
  }

  console.log({
    firstRunExitCode: Number(firstExit.trim()),
    secondRunExitCode: secondRun.exitCode,
    gate: "pass",
  });
} finally {
  await sandbox.kill();
}
```

## 上线建议

- 把测试命令配置化，不同仓库可以映射到不同验证策略。
- 对大型仓库使用模板预装基础工具链，减少验证前的依赖准备时间。
- 验证结果要保存退出码、失败用例、日志摘要和补丁版本，便于后续审计。
- 对网络访问、私有依赖和环境变量使用最小权限策略。
- 不建议在沙箱中长期运行完整 CI。云沙箱更适合任务级、交互式、Agent 驱动的快速验证。

## 可运行示例

本实践对应示例项目中的 `npm run verify-change`。该脚本会在云沙箱中运行失败测试、应用修复并重新验证。

## 相关功能

- [运行命令](../功能说明/Commands/运行命令.md)
- [流式输出](../功能说明/Commands/流式输出.md)
- [读写文件](../功能说明/Filesystem/读写文件.md)
- [预装 Agent 环境](./预装%20Agent%20环境.md)
