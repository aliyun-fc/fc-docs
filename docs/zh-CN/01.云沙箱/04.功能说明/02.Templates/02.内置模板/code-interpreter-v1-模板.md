# code-interpreter-v1 模板

code-interpreter-v1 模板提供安全隔离的代码执行沙箱环境，支持在云端安全地执行 Python、JavaScript 等语言代码，并提供文件管理、终端命令执行、上下文管理等完整的数据面 API。

code-interpreter-v1 模板对齐 E2B Code Interpreter 的代码上下文、代码执行、文件访问和命令能力。

## 功能特性

| **特性** | **说明** |
| --- | --- |
| 多语言代码执行 | 支持 Python、JavaScript 等语言代码的安全执行，基于 Jupyter Kernel 实现上下文保持 |
| 文件系统操作 | 完整的文件 CRUD 能力：上传、下载、读取、写入、创建目录、移动、删除，支持文本和二进制文件 |
| 终端命令执行 | 支持同步命令执行和 WebSocket 交互式终端（TTY），支持颜色、光标控制、终端调整大小 |
| 上下文管理 | 独立的代码执行环境，支持创建多个上下文（Kernel），每个上下文保持独立的变量状态 |
| 进程管理 | 列出、查询、停止沙箱内运行的进程 |
| 安全隔离 | 基于函数实例独占隔离，每个沙箱实例拥有独立的文件系统和进程空间 |

## 适用场景

| **场景** | **说明** |
| --- | --- |
| AI Agent 代码沙箱 | 为 AI Agent 提供安全的代码执行环境，防止不可信代码访问或篡改宿主系统资源 |
| 数据分析 | 在沙箱中运行 Python 数据分析脚本，配合 pandas、numpy 等库处理数据 |
| 文件处理 | 上传文件到沙箱，执行格式转换、数据清洗等操作后下载结果 |
| 脚本执行与自动化 | 执行 Shell 命令、安装依赖、运行自动化脚本 |

## 默认配置

code-interpreter-v1 模板的默认配置如下：

| **配置项** | **默认值** | **说明** |
| --- | --- | --- |
| 容器镜像 | `sandbox-code-interpreter:v0.9.30` | 预置代码解释器沙箱镜像 |
| 默认端口 | 5000 | 沙箱服务监听端口 |
| CPU | 2 vCPU | 最低要求 |
| 内存 | 2048 MB | 最低要求 |
| 磁盘大小 | 512 MB | 可选 512 MB 或 10240 MB |

## 架构说明

Code Interpreter API 分为控制面和数据面两个层面：

| **层面** | **说明** |
| --- | --- |
| 控制面 OpenAPI | 负责沙箱模板和沙箱实例资源的创建和生命周期管理 |
| 数据面 OpenAPI | 负责具体的代码执行、文件操作、终端命令、进程管理等功能调用 |

数据面 Base URL 格式：`https://{阿里云主账号ID}.e2b-data.cn-hangzhou.aliyuncs.com/`

## SDK 使用方式

使用 code-interpreter-v1 模板时，是否需要显式指定 `template` 取决于 SDK：

| **SDK** | **template 参数** | **说明** |
| --- | --- | --- |
| `e2b_code_interpreter` SDK | 不需要指定 | 专用 SDK 默认创建 `code-interpreter-v1` 沙箱 |
| `e2b` SDK | 需要指定 `code-interpreter-v1` | 通用 SDK 默认创建 base 沙箱，需要显式选择 code-interpreter-v1 模板 |

**使用 `e2b_code_interpreter` SDK：**

```python
import os
from e2b_code_interpreter import Sandbox

sbx = Sandbox.create(
    api_key=os.environ["E2B_API_KEY"],
    api_url=os.environ["E2B_API_URL"],
    domain=os.environ["E2B_DOMAIN"],
)
execution = sbx.run_code("print('hello from code interpreter')")
print(execution.logs.stdout)
sbx.kill()
```

TypeScript 示例：

```typescript
import { Sandbox } from "@e2b/code-interpreter";

const sbx = await Sandbox.create("code-interpreter-v1", {
  apiKey: process.env.E2B_API_KEY,
  apiUrl: process.env.E2B_API_URL,
  domain: process.env.E2B_DOMAIN,
});

try {
  const execution = await sbx.runCode("print('hello from code interpreter')");
  console.log(execution.logs.stdout);
} finally {
  await sbx.kill();
}
```

**使用 `e2b` SDK：**

```python
import os
from e2b import Sandbox

sbx = Sandbox.create(
    template="code-interpreter-v1",
    api_key=os.environ["E2B_API_KEY"],
    api_url=os.environ["E2B_API_URL"],
    domain=os.environ["E2B_DOMAIN"],
)
result = sbx.commands.run("python --version")
print(result.stdout)
sbx.kill()
```

## 使用流程

1. **创建 code-interpreter-v1 沙箱模板**：通过控制台或 OpenAPI 创建模板。
2. **启动沙箱实例**：基于模板创建沙箱实例，获取沙箱 ID。
3. **创建执行上下文**：在沙箱内创建代码执行上下文（指定语言类型）。
4. **执行代码**：通过上下文执行 Python 或 JavaScript 代码。

## 核心 API 概览

### 沙箱实例管理

| **操作** | **方法** | **路径** |
| --- | --- | --- |
| 创建沙箱实例 | POST | `/sandboxes` |
| 停止沙箱实例 | POST | `/sandboxes/{sandboxId}/stop` |
| 删除沙箱实例 | DELETE | `/sandboxes/{sandboxId}` |
| 健康检查 | GET | `/sandboxes/{sandboxId}/health` |

创建沙箱实例请求示例：

```json
POST ${BASEURL}/sandboxes

{
  "templateName": "my-code-interpreter",
  "sandboxId": "optional-custom-id"
}
```

响应示例：

```json
{
  "sandboxId": "01JCED8Z9Y6XQVK8M2NRST5WXY",
  "templateId": "01JCED8Z9Y6XQVK8M2NRST5ABC",
  "templateName": "my-code-interpreter",
  "templateType": "CodeInterpreter",
  "status": "READY",
  "sandboxIdleTimeoutInSeconds": 3600,
  "createdAt": "2024-12-02T10:30:00Z"
}
```

### 上下文管理

| **操作** | **方法** | **路径** |
| --- | --- | --- |
| 列出所有上下文 | GET | `/sandboxes/{sandboxId}/contexts` |
| 创建新上下文 | POST | `/sandboxes/{sandboxId}/contexts` |
| 获取上下文详情 | GET | `/sandboxes/{sandboxId}/contexts/{contextId}` |
| 删除上下文 | DELETE | `/sandboxes/{sandboxId}/contexts/{contextId}` |

创建上下文请求示例：

```json
POST ${BASEURL}/sandboxes/{sandboxId}/contexts

{
  "language": "python",
  "cwd": "/home/user"
}
```

### 代码执行

通过上下文同步执行代码：

```json
POST ${BASEURL}/sandboxes/{sandboxId}/contexts/execute

{
  "contextId": "kernel-12345-67890",
  "code": "print('hello from sandbox')",
  "timeout": 30
}
```

响应示例：

```json
{
  "results": [
    { "type": "stdout", "text": "hello from sandbox" },
    { "type": "result", "text": "None" },
    { "type": "endOfExecution", "status": "ok" }
  ],
  "contextId": "kernel-12345-67890"
}
```

### 文件系统操作

| **操作** | **方法** | **路径** |
| --- | --- | --- |
| 读取文件 | GET | `/sandboxes/{sandboxId}/files?path={path}` |
| 写入文件 | POST | `/sandboxes/{sandboxId}/files` |
| 列出目录 | GET | `/sandboxes/{sandboxId}/filesystem?path={path}` |
| 获取文件信息 | GET | `/sandboxes/{sandboxId}/filesystem/stat?path={path}` |
| 下载文件 | GET | `/sandboxes/{sandboxId}/filesystem/download?path={path}` |
| 上传文件 | POST | `/sandboxes/{sandboxId}/filesystem/upload`（multipart/form-data，最大 100 MB） |
| 创建目录 | POST | `/sandboxes/{sandboxId}/filesystem/mkdir` |
| 移动/重命名 | POST | `/sandboxes/{sandboxId}/filesystem/move` |
| 删除文件/目录 | POST | `/sandboxes/{sandboxId}/filesystem/remove` |

文本文件以 UTF-8 编码返回 `content` 字段，二进制文件以 base64 编码返回。上传文件使用 `multipart/form-data` 格式，最大支持 100 MB。

### 终端与进程管理

| **操作** | **方法** | **路径** |
| --- | --- | --- |
| 同步执行命令 | POST | `/sandboxes/{sandboxId}/processes/cmd`（30 秒超时） |
| 交互式终端 | GET | `/sandboxes/{sandboxId}/processes/tty?protocol=json`（WebSocket） |
| 列出所有进程 | GET | `/sandboxes/{sandboxId}/processes` |
| 获取进程详情 | GET | `/sandboxes/{sandboxId}/processes/{pid}` |
| 停止进程 | DELETE | `/sandboxes/{sandboxId}/processes/{pid}` |

同步执行命令示例：

```json
POST ${BASEURL}/sandboxes/{sandboxId}/processes/cmd

{
  "command": "ls -la /home/user",
  "cwd": "/home/user"
}
```

响应示例：

```json
{
  "executionId": "tty_exec_001",
  "status": "completed",
  "result": {
    "exitCode": 0,
    "stdout": "total 24\ndrwxr-xr-x 3 user user 4096 Jan 15 10:30 .",
    "stderr": "",
    "cwd": "/home/user",
    "executionTimeMs": 150
  },
  "executionTimeMs": 150
}
```

交互式终端支持 `json`（结构化消息）和 `text`（xterm.js 兼容）两种协议模式。客户端需每 30 秒发送心跳，无心跳 2 分钟后连接关闭。

## 沙箱实例状态

沙箱实例在生命周期内经历以下状态：

| **状态** | **说明** |
| --- | --- |
| `CREATING` | 创建中 |
| `READY` | 就绪，可以使用 |
| `TERMINATED` | 已停止 |

## 使用限制

| **限制项** | **约束** |
| --- | --- |
| 沙箱生命周期 | 单个沙箱实例最长生命周期为 6 小时 |
| 浅休眠超时 | 可通过 `sandboxIdleTimeoutSeconds` 参数设置 |
| 文件上传大小 | 单次上传最大 100 MB |
| 代码执行超时 | 单次同步执行最大超时 30 秒 |
| 隐藏文件 | 不允许创建以 `.` 开头的隐藏文件 |

## 最佳实践

**及时清理资源**：完成任务后删除不需要的文件、上下文和沙箱实例，监控存储空间使用情况。

**合理配置超时时间**：短期任务使用较短的超时时间（5~10 分钟），长期任务适当延长（30 分钟~6 小时）。

**错误处理**：建议对 5xx 服务器错误实施指数退避重试，对 429 限流错误等待后重试。

## 相关文档

- [沙箱模板概述](../02.内置模板.md)
- [构建模板](../03.构建自定义镜像模板.md)
- [生命周期](../../01.Sandbox/01.生命周期.md)
- [base 模板](base-模板.md)（仅需 envd 基础能力时选择）
- [browser 模板](browser-模板.md)（仅需浏览器自动化能力时选择）
- [All-In-One 模板](all-in-one-模板.md)（需要同时使用浏览器和代码执行能力时选择）
