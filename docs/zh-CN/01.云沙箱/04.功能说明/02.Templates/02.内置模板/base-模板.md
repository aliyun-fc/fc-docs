# base 模板

base 模板提供最小化的云沙箱运行环境，只包含 E2B envd 兼容基础服务。它适合需要通过 E2B 兼容 SDK 管理沙箱生命周期、运行基础命令、访问文件系统或作为自定义能力基线的场景。

base 模板提供与 E2B Commands、Filesystem、Sandbox 生命周期相关的基础体验对齐能力，是 code-interpreter-v1 模板、browser 模板和 All-In-One 模板的共同能力基础。

## 功能特性

| **特性** | **说明** |
| --- | --- |
| envd 基础服务 | 内置 E2B envd 兼容服务，用于支持沙箱创建、连接、基础命令和文件访问 |
| 轻量运行环境 | 不预置 Code Interpreter 服务，也不预置浏览器自动化服务 |
| 安全隔离 | 每个沙箱实例拥有独立的文件系统和进程空间 |
| 可扩展基线 | 适合作为自定义工具链、业务运行时或更上层能力的基础模板 |

## 适用场景

| **场景** | **说明** |
| --- | --- |
| 基础命令执行 | 通过 envd 运行简单 Shell 命令，完成环境检查、文件准备等任务 |
| 自定义运行时基线 | 在最小沙箱环境上安装或封装自有依赖和工具 |
| SDK 连通性验证 | 验证 API Key、地域、模板创建、沙箱创建和销毁流程 |
| 轻量任务 | 不需要 Python 代码解释器服务，也不需要浏览器自动化能力的任务 |

## 默认配置

base 模板的默认配置如下：

| **配置项** | **默认值** | **说明** |
| --- | --- | --- |
| 默认端口 | 无业务端口 | 提供 envd 基础服务 |
| CPU | 2 vCPU | 最低要求 |
| 内存 | 2048 MB | 最低要求 |
| 磁盘大小 | 512 MB | 适合轻量命令和临时文件 |

## 快速入门

如果需要代码解释器、浏览器自动化或二者组合能力，请分别选择 [code-interpreter-v1 模板](code-interpreter-v1-模板.md)、[browser 模板](browser-模板.md) 或 [All-In-One 模板](all-in-one-模板.md)。

未显式指定 `template` 时，默认创建 base 沙箱。

```python
import os

from e2b import Sandbox

sbx = Sandbox.create(
    api_key=os.environ["E2B_API_KEY"],
    api_url=os.environ["E2B_API_URL"],
    domain=os.environ["E2B_DOMAIN"],
    timeout=600,
)

result = sbx.commands.run("echo hello from base template")
print(result.stdout)

sbx.kill()
```

TypeScript 示例：

```typescript
import { Sandbox } from "e2b";

const sbx = await Sandbox.create({
  apiKey: process.env.E2B_API_KEY,
  apiUrl: process.env.E2B_API_URL,
  domain: process.env.E2B_DOMAIN,
  timeoutMs: 600_000,
});

try {
  const result = await sbx.commands.run("echo hello from base template");
  console.log(result.stdout);
} finally {
  await sbx.kill();
}
```

## 相关文档

- [沙箱模板概述](../02.内置模板.md)
- [构建模板](../03.构建自定义镜像模板.md)
- [生命周期](../../01.Sandbox/01.生命周期.md)
- [code-interpreter-v1 模板](code-interpreter-v1-模板.md)
- [browser 模板](browser-模板.md)
- [All-In-One 模板](all-in-one-模板.md)
