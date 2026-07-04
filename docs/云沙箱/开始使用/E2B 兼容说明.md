# E2B 兼容说明

本文集中说明云沙箱对 E2B SDK 和 E2B CLI 的兼容范围。其它开始使用文档只保留最小接入步骤，接口边界集中在本文维护。

接入参数配置参见[使用约束](./使用约束.md)。

## 兼容范围总览

| 能力模块 | 兼容状态 | 说明 |
| --- | --- | --- |
| Sandbox | 兼容 | 支持创建、连接、查询、超时、暂停、终止、上传下载地址和端口访问地址。 |
| Commands | 兼容 | 支持命令执行、运行中进程管理、标准输入和 PTY。 |
| Filesystem | 兼容 | 支持文件读写、目录管理、重命名、删除和存在性检查。 |
| Code Interpreter | 兼容 | 支持代码执行、上下文管理、执行输出和多次执行之间的状态保持。 |
| Template | 兼容 | 支持模板管理、模板构建、标签和别名。 |
| CLI | 部分兼容 | 支持常用 Sandbox 和 Template 命令。 |
| Metrics / Logs / Network Config Update | 受限 | 接口可调用，但返回结果或实际效果存在限制。 |
| Snapshots / Volume / Team / Access Token | 暂不兼容 | 不建议作为云沙箱接入路径使用。 |

## 兼容 API

### Sandbox

支持以下 Sandbox 生命周期和访问能力：

- `Sandbox.create()`
- `Sandbox.connect(sandboxId)`
- `Sandbox.list()`
- `Sandbox.getInfo(sandboxId)`
- `Sandbox.kill(sandboxId)`
- `Sandbox.setTimeout(sandboxId, ms)`
- `sandbox.getInfo()`
- `sandbox.isRunning()`
- `sandbox.setTimeout(ms)`
- `sandbox.pause()`
- `sandbox.kill()`
- `sandbox.downloadUrl(path)`
- `sandbox.uploadUrl(path)`
- `sandbox.getHost(port)`

`Sandbox.connect(sandboxId)` 可连接已有 Sandbox。如果目标 Sandbox 已暂停，连接时会自动恢复。

### Commands

支持以下命令执行和进程管理能力：

- `sandbox.commands.run()`
- `sandbox.commands.list()`
- `sandbox.commands.connect()`
- `sandbox.commands.sendStdin()`
- `sandbox.commands.kill()`

`sandbox.commands.run()` 支持 PTY 模式，适合运行需要伪终端行为的命令。

### Filesystem

支持以下文件系统能力：

- `sandbox.files.list()`
- `sandbox.files.exists()`
- `sandbox.files.getInfo()` / `sandbox.files.get_info()`
- `sandbox.files.read()`
- `sandbox.files.write()`
- `sandbox.files.makeDir()`
- `sandbox.files.remove()`
- `sandbox.files.rename()`
### Code Interpreter

支持代码解释器核心能力：

- `CodeInterpreter.create()`
- `sandbox.runCode()` / `sandbox.run_code()`
- `sandbox.createContext()` / `sandbox.create_context()`
- Context 创建、查询和删除。
- 执行结果输出，包括 stdout、stderr、execution count 和裸表达式结果。
- 多次代码执行之间的变量和上下文状态保持。

### Template

支持以下模板能力：

- Template CRUD。
- Template Build。
- Template Tags。
- Template Alias。

当前模板构建支持从镜像创建模板。具体使用方式参见[自定义模板](../功能说明/Templates/自定义模板.md)。

### CLI

支持 E2B CLI 的常用命令：

- `sandbox create`
- `sandbox list`
- `sandbox kill`
- `template list`

CLI 接入时需要设置 `E2B_ACCESS_TOKEN`。配置方式参见[通过 CLI 使用云沙箱](./快速入门/通过%20CLI%20使用云沙箱.md)。

## 受限能力

- Sandbox Metrics：当前为 Stub 实现，返回模拟数据或空数组。
- Sandbox Logs：当前返回空数组。
- Network Config Update：当前返回成功，但不进行实际网络变更。

这些接口可以用于保持 SDK 调用兼容，但不适合作为生产监控、日志采集或网络变更的控制面依赖。

## 暂不兼容能力

以下能力当前不属于云沙箱 E2B 兼容主路径：

- Snapshots。
- Volume API。
- Team 管理。
- API Key / Access Token 管理。

需要持久化存储或云上数据访问时，请先使用 NAS、OSS 等云存储方案。API Key 请在函数计算控制台创建和管理，不通过 E2B SDK 管理。

VPC、OSS、日志采集、监控告警等能力属于云沙箱的 FC Extensions（云上扩展），不属于 E2B SDK 原生兼容接口。相关说明参见[FC Extensions](../功能说明/FC%20Extensions/概览.md)。

## 迁移建议

- 已有 E2B 应用优先保持 SDK 调用方式不变，只替换 API Key、API URL 和域名。
- 先用 `code-interpreter-v1` 和最小 Sandbox 示例验证创建、命令执行、文件读写和释放资源。
- 对依赖 Metrics、Logs、Network Config Update、Snapshots 或 Volume 的应用，需要先调整设计，不要按 E2B 原路径直接迁移。
- 生产代码应显式调用 `sandbox.kill()`，避免 Sandbox 长时间占用资源。

## 后续阅读

- [通过 SDK 使用云沙箱](./快速入门/通过%20SDK%20使用云沙箱.md)
- [通过 CLI 使用云沙箱](./快速入门/通过%20CLI%20使用云沙箱.md)
- [自定义模板](../功能说明/Templates/自定义模板.md)
