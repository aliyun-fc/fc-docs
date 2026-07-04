# Git 集成

云沙箱可以在沙箱内运行 Git 命令，也可以使用 E2B SDK 暴露的 Git 模块完成常见仓库操作。适合 Agent 拉取代码、创建临时分支、运行测试和生成补丁。

## 使用命令运行 Git

```typescript
const result = await sandbox.commands.run(
  "git clone --depth=1 https://github.com/e2b-dev/e2b.git /tmp/repo && git -C /tmp/repo status --short",
  { timeoutMs: 120_000 },
);

console.log(result.stdout);
```

## 使用 SDK Git 模块

```typescript
await sandbox.git.clone("https://github.com/e2b-dev/e2b.git", "/tmp/repo");
const status = await sandbox.git.status("/tmp/repo");
console.log(status);
```

## 使用建议

- 访问私有仓库时，凭证应由业务侧注入，并控制最小权限。
- 拉取大型仓库建议使用浅克隆或只拉取必要目录。
- 运行不可信仓库代码前，应先完成依赖源、脚本和执行命令的安全校验。

