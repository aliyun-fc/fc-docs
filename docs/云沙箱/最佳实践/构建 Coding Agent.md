# 构建 Coding Agent

Coding Agent 的业务价值不在于“能生成代码”，而在于能把代码改完、跑完验证，并把可审查的结果交还给开发者。没有隔离执行环境时，Agent 只能停留在建议层；一旦需要安装依赖、运行测试、启动服务或生成补丁，就会碰到安全、资源和环境一致性问题。

云沙箱适合作为 Coding Agent 的远程执行层。主业务系统负责模型调用、任务编排、权限控制和结果展示；云沙箱负责承载仓库、运行命令、保存临时文件、输出日志和补丁。任务完成后销毁沙箱，避免依赖、进程和中间文件污染主系统。

## 业务场景

- 代码助手在隔离环境中复现问题、修改文件、运行测试，并返回 diff。
- 代码审查系统在合并前验证 AI 生成的修复是否真的通过测试。
- App Builder 生成项目后，在沙箱中执行构建和预览，不占用业务服务资源。
- 企业内部 Agent 支持多语言仓库，通过模板固定 Python、Node.js、Go 等工具链。

## 方案设计

一次可验证 Coding Agent 任务建议拆成五步：

1. 创建沙箱，写入任务 ID、仓库地址、最小必要环境变量。
2. 准备工作区，克隆仓库或写入待处理文件。
3. 执行基线验证，确认问题可复现。
4. 写入 Agent 生成的修改，重新运行测试或构建。
5. 返回测试结果、日志摘要和 diff，随后释放沙箱。

这里的关键是“先失败、再修复、再通过”。只有验证链路闭合，Agent 输出才适合进入代码审查或自动化合并流程。

## 示例代码

以下示例模拟一个 Coding Agent 修复 Python 函数：先运行测试得到失败结果，再写入修复后的代码，最后返回 diff。

```javascript
import { Sandbox } from "e2b";

const sandbox = await Sandbox.create("code-interpreter-v1", {
  apiKey: process.env.E2B_API_KEY,
  apiUrl: process.env.E2B_API_URL,
  domain: process.env.E2B_DOMAIN,
  envs: { TASK_TYPE: "coding-agent" },
});

try {
  await sandbox.files.makeDir("/tmp/coding-agent");
  await sandbox.files.write("/tmp/coding-agent/calculator.py", "def add(a, b):\n    return a - b\n");
  await sandbox.files.write(
    "/tmp/coding-agent/test_calculator.py",
    `import unittest
from calculator import add

class CalculatorTest(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)

if __name__ == "__main__":
    unittest.main()
`,
  );

  await sandbox.commands.run("git init && git add .", { cwd: "/tmp/coding-agent" });

  await sandbox.commands.run("python3 -m unittest -v > before.out 2>before.err; echo $? > before.exit", {
    cwd: "/tmp/coding-agent",
    timeoutMs: 30_000,
  });
  const beforeExit = await sandbox.files.read("/tmp/coding-agent/before.exit");

  await sandbox.files.write("/tmp/coding-agent/calculator.py", "def add(a, b):\n    return a + b\n");

  const after = await sandbox.commands.run("python3 -m unittest -v", {
    cwd: "/tmp/coding-agent",
    timeoutMs: 30_000,
  });
  if (after.exitCode !== 0) {
    throw new Error(after.stderr || after.stdout);
  }

  const diff = await sandbox.commands.run("git diff -- calculator.py", {
    cwd: "/tmp/coding-agent",
  });

  console.log({
    beforeExitCode: Number(beforeExit.trim()),
    afterExitCode: after.exitCode,
    patch: diff.stdout,
  });
} finally {
  await sandbox.kill();
}
```

## 上线建议

- 不要让模型直接拼接任意 Shell 命令。建议把“安装依赖、运行测试、生成 diff”等动作封装成受控步骤。
- 每个任务设置 Sandbox 超时和命令超时。Coding Agent 常出现长时间构建、测试卡死或服务未退出的问题。
- 对输出做分层：给用户看结论、失败测试和 diff；完整日志进入审计系统。
- 私有仓库、包管理器 Token、云资源凭证都应使用最小权限，并按任务注入，不写入模板。
- 生产环境建议为常见技术栈维护自定义模板，减少每次任务的依赖安装时间。

## 可运行示例

本实践对应示例项目中的 `npm run coding-agent`。该脚本会真实创建云沙箱、复现失败测试、写入修复、重新验证并输出 diff。

## 相关功能

- [创建沙箱](../功能说明/Sandbox/创建沙箱.md)
- [运行命令](../功能说明/Commands/运行命令.md)
- [读写文件](../功能说明/Filesystem/读写文件.md)
- [Git 集成](../功能说明/Sandbox/Git%20集成.md)
