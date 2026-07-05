# Code Interpreter代码解释器

Code Interpreter 是一个强大的代码执行沙箱环境，支持在安全的沙箱环境中执行Python代码、管理文件系统、执行shell命令等功能。本文详细介绍Code Interpreter的API接口。

## **功能介绍**

使用Code Interpreter API可以实现以下功能：

- **代码执行**：支持 Python、JavaScript等语言代码的安全执行
- **文件管理**：上传、下载、移动、删除文件
- **文件系统操作**：目录创建、文件状态查询等
- **上下文管理**：独立的代码执行环境
- **会话管理**：支持并发会话和超时控制

Code Interpreter API分为控制面和数据面两个层面：

- [控制面OpenAPI](#d1fa286c89sfo)：负责代码解释器资源实体的创建和生命周期管理。
- [数据面OpenAPI](#888160c671l3m)：负责具体的代码执行、文件操作等功能调用。

## **使用说明**

- 首次登录[AgentRun控制台](https://functionai.console.aliyun.com/cn-hangzhou/agent/runtime/agent-list)，请先根据界面提示创建AgentRun服务关联角色AliyunServiceRoleForAgentRun，后续可以通过SDK操作使用。
- 沙箱模板定义一组沙箱实例的基础配置；沙箱实例则是具体执行代码任务的沙箱环境，一个沙箱实例最长生命周期为 6 小时。此外，通过`sandboxIdleTimeoutInSeconds`参数，可以设定一个超时时长。如果会话的浅休眠（原闲置）时间超过该值，它将被提前终止，而无需等待 6 小时的生命周期结束。

## **使用流程概览**

1. **创建代码解释器模板**
2. **启动代码解释器沙箱实例**
3. **创建执行上下文**
4. **执行代码**

## **控制面OpenAPI**

### **准备工作**

1. 进入[OpenAPI Explorer](https://next.api.aliyun.com/api/)。
2. 在顶部菜单栏，单击**选择云产品**，在搜索框搜索并选择**AgentRun**。
3. 在左侧导航栏，找到对应的API接口开始使用。

### **模板管理**

以上述OpenAPI门户链接中的API文档为准。

## **数据面OpenAPI**

### **准备工作**

准备数据面调用BASEURL：`https://${阿里云主账号 ID}.agentrun-data.cn-hangzhou.aliyuncs.com/`

在产品控制台右上角单击头像获取阿里云主账号ID。

### **沙箱实例管理**

**

**说明**

该部分接口暂未上线OpenAPI Explorer，可先通过SDK或直接调用API端点使用。

#### **创建Sandbox实例**

**请求路径：**`POST ${BASEURL}/sandboxes`

**请求头：**`X-Acs-Parent-Id: ${阿里云主账号ID}`

- Content-Type: application/json

**请求体：**application/json

```
{ "templateName": "string", // 必需：模板名称，系统内部通过 templateName 查询 template_id "sandboxId": "string", // 可选：自定义沙箱 ID，用于端到端 tracing。如果不指定，系统会自动生成 ULID 格式的 ID }
```

**响应示例：**

```
{ "sandboxId": "01JCED8Z9Y6XQVK8M2NRST5WXY", "templateId": "01JCED8Z9Y6XQVK8M2NRST5ABC", "templateName": "python-sandbox", "templateType": "CodeInterpreter", "status": "READY", "sandboxIdleTimeoutInSeconds": 3600, "createdAt": "2024-12-02T10:30:00Z", "lastUpdatedAt": "2024-12-02T10:30:15Z", "metadata": { "fcSessionDetails": { "sessionId": "1234567890abcdef", "sessionStatus": "Active", "sessionIdleTimeoutInSeconds": 3600, "functionName": "sandbox-function", "qualifier": "LATEST", "containerId": "container-123", "createdTime": "2024-12-02T10:30:00Z", "lastModifiedTime": "2024-12-02T10:30:15Z", "sessionAffinityType": "HEADER_FIELD" } } }
```

#### **停止Sandbox实例**

**请求路径：**POST ${BASEURL}/sandboxes/{sandboxId}/stop

**请求头：**`X-Acs-Parent-Id: ${阿里云主账号ID}`

**路径参数：**

- `sandboxId`（string, 必需）： 沙箱 ID

**请求体：**无

**响应示例：**

```
{ "sandboxId": "01JCED8Z9Y6XQVK8M2NRST5WXY", "templateId": "01JCED8Z9Y6XQVK8M2NRST5ABC", "templateName": "python-sandbox", "templateType": "CodeInterpreter", "status": "TERMINATED", "sandboxIdleTimeoutInSeconds": 3600, "createdAt": "2024-12-02T10:30:00Z", "lastUpdatedAt": "2024-12-02T11:00:00Z", "endedAt": "2024-12-02T11:00:00Z" }
```

**说明：**

- 停止 Sandbox 会删除 FC Session 并将数据库状态更新为`TERMINATED`
- 操作具有幂等性，如果 Sandbox 已经是`TERMINATED`状态，直接返回
- 会设置`endedAt`时间戳

#### **删除Sandbox实例**

**请求路径：**`DELETE ${BASEURL}/sandboxes/{sandboxId}`

**请求头：**`X-Acs-Parent-Id: ${阿里云主账号ID}`

**路径参数：**

- `sandboxId`(string, 必需)：沙箱 ID

**请求体：**无

**响应示例：**

```
{ "sandboxId": "01JCED8Z9Y6XQVK8M2NRST5WXY", "templateId": "01JCED8Z9Y6XQVK8M2NRST5ABC", "templateName": "python-sandbox", "templateType": "CodeInterpreter", "status": "READY|TERMINATED", "sandboxIdleTimeoutInSeconds": 3600, "createdAt": "2024-12-02T10:30:00Z", "lastUpdatedAt": "2024-12-02T11:30:00Z", "endedAt": "2024-12-02T11:00:00Z" }
```

删除 Sandbox 会执行以下操作：

- 检查 Sandbox 是否存在
- 如果 Sandbox 是`READY`状态，先调用 StopSandbox 删除 FC Session
- 会返回删除前 Sandbox 的状态

#### **状态说明**

Sandbox 的状态流转：

- `CREATING`: 创建中
- `READY`: 就绪，可以使用
- `TERMINATED`: 已停止（通过 StopSandbox 接口）

#### **错误响应**

所有接口在出现错误时返回统一的错误格式：

```
{ "error": { "code": "ERROR_CODE", "message": "错误描述信息" } }
```

常见错误码：

- `400 Bad Request`：请求参数错误
- `404 Not Found`：Sandbox 不存在
- `500 Internal Server Error`：服务器内部错误

### **健康检查**

#### **检查服务健康状态**

**请求语法**：`GET ${BASEURL}/sandboxes/{sandboxId}/health`

**请求头**：`X-Acs-Parent-Id: ${阿里云主账号ID}`

**查询参数**：无

**响应示例**：

```
{ "status": "ok", "service": "sandbox-code-interpreter", "version": "v1", "timestamp": "2025-11-15T09:45:01.068104+08:00", "uptime": 1142269582541 }
```

### **上下文管理**

**列出所有上下文**

**请求语法**：`GET ${BASEURL}/sandboxes/{sandboxId}/contexts`

**请求头**：`X-Acs-Parent-Id: ${阿里云主账号ID}`

**查询参数**：无

**响应示例：**

```
[ { "id": "kernel-12345-67890", "language": "python", "cwd": "/tmp/sandbox/home/user" } ]
```

**创建新上下文**

**请求语法**：`POST ${BASEURL}/sandboxes/{sandboxId}/contexts`

**请求头**：`X-Acs-Parent-Id: ${阿里云主账号ID}`

- `Content-Type: application/json`

**请求体**：`application/json`

```
{ "language": "python", // 必需：python 或 javascript "cwd": "/tmp/sandbox/home/user" // 可选：工作目录 }
```

**响应示例：**

```
{ "id": "271f70d5-9065-4403-8ea3-4d541f7d2bb8", "language": "python", "cwd": "/home/user" }
```

**获取上下文详情**

**请求语法**：`GET ${BASEURL}/sandboxes/{sandboxId}/contexts/{contextId}`

**路径参数**：

- `contextId`(string, 必需): 上下文的唯一标识符

**请求头**：`X-Acs-Parent-Id: ${阿里云主账号ID}`

**查询参数**：无

**响应示例**：

```
{ "id": "271f70d5-9065-4403-8ea3-4d541f7d2bb8", "language": "python", "cwd": "/home/user" }
```

**删除上下文**

**请求语法**：`DELETE ${BASEURL}/sandboxes/{sandboxId}/contexts/{contextId}`

**路径参数**：

- `contextId`(string, 必需)：上下文的唯一标识符

**请求头**：`X-Acs-Parent-Id: ${阿里云主账号ID}`

**查询参数**：无

**响应**：204 No Content（无响应体）

### **文件系统操作**

**读取文件内容**

**请求语法：**`GET ${BASEURL}/sandboxes/{sandboxId}/files`

**请求头：**`X-Acs-Parent-Id: ${阿里云主账号ID}`

**查询参数：**

- `path`(string, 必需): 文件路径（支持文本文件和二进制文件）

**响应示例**：

```
{ "name": "example.txt", "type": "file", "path": "/workspace/example.txt", "size": 1024, "mode": 420, "permissions": "-rw-r--r--", "owner": "user", "group": "group", "modifiedTime": "2025-11-15T10:30:00Z", "content": "Hello, World!\nThis is a text file.", "encoding": "utf-8" }
```

**说明**:

- 文本文件：`encoding`为`"utf-8"`，`content`为 UTF-8 文本内容
- 二进制文件：`encoding`为`"base64"`，`content`为 base64 编码的内容

**写入文件内容**

**请求语法**:`POST ${BASEURL}/sandboxes/{sandboxId}/files`

**请求头**：`X-Acs-Parent-Id: ${阿里云主账号ID}`

- `Content-Type: application/json`

**请求体**:`application/json`

```
{ "path": "example.txt", // 必需：文件路径（不支持隐藏文件） "content": "Hello, World!\nThis is a text file.", // 必需：UTF-8 文本内容 "encoding": "utf-8" // 可选：默认为 utf-8 }
```

**文件限制**:

- 只支持文本文件扩展名（.txt, .py, .json, .md 等）
- 不允许创建以`.`开头的隐藏文件
- 自动创建父目录（如果不存在）
- 默认文件权限：0644

```
{ "path": "/home/user/example.txt", "size": 25 }
```

**列出目录内容**

**请求语法**:`GET ${BASEURL}/sandboxes/{sandboxId}/filesystem`

**请求头**：`X-Acs-Parent-Id: ${阿里云主账号ID}`

**查询参数**：

- `path`(string, 可选): 目录路径（默认为当前目录）
- `depth`(integer, 可选): 遍历深度（默认为 1，最小值为 1）

**响应示例**:

```
{ "path": "/home/user", "entries": [ { "name": "example.txt", "type": "file", "path": "/tmp/code-interpreter-sandbox/home/user/example.txt", "size": 1024, "mode": 420, "permissions": "-rw-r--r--", "owner": "user", "group": "group", "modifiedTime": "2025-11-15T10:30:00Z" } ] }
```

**获取文件或目录信息**

**请求语法**：`GET ${BASEURL}/sandboxes/{sandboxId}/filesystem/stat`

**请求头**：`X-Acs-Parent-Id: ${阿里云主账号ID}`

**查询参数**：

- `path`(string, 必需): 文件或目录路径

**响应示例**：

```
{ "entry": { "name": "example.py", "type": "file", "path": "/workspace/example.py", "size": 1024, "mode": 420, "permissions": "-rw-r--r--", "owner": "user", "group": "group", "modifiedTime": "2025-11-15T10:30:00Z" } }
```

**下载文件**

**请求语法**：`GET ${BASEURL}/sandboxes/{sandboxId}/filesystem/download`

**请求头**：`X-Acs-Parent-Id: ${阿里云主账号ID}`

**查询参数**：

- `path`(string, 必需): 文件路径

**响应**：

- `Content-Type`: 文件的 MIME 类型
- `Content-Disposition`:`attachment; filename="example.txt"`
- `Content-Length`: 文件大小（字节）
- 响应体: 文件二进制流

**说明**: 只支持文件下载，不支持目录

**创建目录**

**请求语法**：`POST ${BASEURL}/sandboxes/{sandboxId}/filesystem/mkdir`

**请求头**：`X-Acs-Parent-Id: ${阿里云主账号ID}`

- `Content-Type: application/json`

**请求体**：`application/json`

```
{ "path": "/tmp/home/user/testDir" // 必需：目录路径 }
```

**说明**:

- 支持幂等操作：如果目录已存在，返回 200
- 如果父目录不存在，自动创建它们（类似 mkdir -p）
- 支持递归目录创建

**响应示例：**

```
{ "entry": { "name": "testDir", "type": "directory", "path": "/home/user/test_dir", "size": 0, "mode": 493, "permissions": "drwxr-xr-x", "owner": "user", "group": "group", "modifiedTime": "2025-11-15T10:30:00Z" } }
```

**移动或重命名文件/目录**

**请求语法**：`POST ${BASEURL}/sandboxes/{sandboxId}/filesystem/move`

**请求头**：`X-Acs-Parent-Id: ${阿里云主账号ID}`

- `Content-Type: application/json`

**请求体**：`application/json`

```
{ "source": "/workspace/old_name.txt", // 必需：源文件或目录路径 "destination": "/workspace/new_name.txt" // 必需：目标文件或目录路径 }
```

**说明**:

- 支持幂等操作：如果源文件不存在且目标已存在同名文件，返回 200
- 支持跨目录移动和同目录重命名

**响应示例：**

```
{ "entry": { "name": "new_name.txt", "type": "file", "path": "/workspace/new_name.txt", "size": 1024, "mode": 420, "permissions": "-rw-r--r--", "owner": "user", "group": "group", "modifiedTime": "2025-11-15T10:30:00Z" } }
```

**删除文件或目录**

**请求语法**：`POST ${BASEURL}/sandboxes/{sandboxId}/filesystem/remove`

**请求头**：`X-Acs-Parent-Id: ${阿里云主账号ID}`

- `Content-Type: application/json`

**请求体**：`application/json`

```
{ "path": "/home/user/test_dir" // 必需：文件或目录路径 }
```

**说明**：

- 支持幂等操作：如果文件或目录不存在，返回 200
- 支持递归删除目录

**响应示例**：

```
{ "entry": { "name": "testDir", "type": "directory", "path": "/home/user/test_dir", "size": 0, "mode": 493, "permissions": "drwxr-xr-x", "owner": "user", "group": "group", "modifiedTime": "2025-11-15T10:30:00Z" } }
```

**上传文件**

**请求语法**：`POST ${BASEURL}/sandboxes/{sandboxId}/filesystem/upload`

**请求头**：`X-Acs-Parent-Id: ${阿里云主账号ID}`

- `Content-Type: multipart/form-data`

**请求体**：`multipart/form-data`

```
file: [binary] // 必需：文件内容（最大 100MB） path: "uploads/example.txt" // 可选：目标文件路径（如果不提供则使用文件名） current_path: "." // 可选：当前目录路径（当 path 未提供时使用）
```

**文件限制**：

- 最大文件大小：100MB
- 只支持文件上传，不支持目录创建
- 自动创建父目录（如果不存在）

**响应示例：**

```
{ "path": "uploads/example.txt", "size": 1024 }
```

### **代码执行**

**同步执行代码**

**请求语法**：`POST ${BASEURL}/sandboxes/{sandboxId}/contexts/execute`

**请求头**：`X-Acs-Parent-Id: ${阿里云主账号ID}`

- `Content-Type: application/json`

**请求体**：`application/json`

```
{ "contextId": "kernel-12345-67890", // 可选：上下文 ID（如果提供，则不需要 language） "language": "python", // 可选：编程语言类型（仅在未提供 contextId 时需要） "code": "print('hello')", // 必需：要执行的代码 "timeout": 30 // 可选：执行超时时间（秒，默认 30，最大 30） }
```

**响应示例：**

```
{ "results": [ { "type": "stdout", "text": "hello" }, { "type": "result", "text": "None" }, { "type": "endOfExecution", "status": "ok" } ], "contextId": "kernel-12345-67890" }
```

### **终端执行**

**同步执行命令**

#### 同步执行命令

**请求语法**:`POST ${BASEURL}/sandboxes/{sandboxId}/processes/cmd`

**请求头**：`X-Acs-Parent-Id: ${阿里云主账号ID}`

- `Content-Type: application/json`

**请求体**:`application/json`

```
{ "command": "ls -la /home/user", // 必需：要执行的命令 "cwd": "/tmp/code-interpreter-sandbox/home/user" // 可选：工作目录 }
```

**说明**:

- 硬超时限制：数据面网关强制执行的 30 秒最大执行时间
- 直接响应：在 HTTP 响应中返回完整的命令执行结果
- 无需上下文：命令执行不需要上下文
- 使用场景：简单命令、系统检查、文件操作
- 交互式终端：请使用`/processes/tty`WebSocket 端点

**响应示例**:

```
{ "executionId": "tty_exec_001", "status": "completed", "result": { "exitCode": 0, "stdout": "total 24\ndrwxr-xr-x 3 user user 4096 Jan 15 10:30 .", "stderr": "", "cwd": "/tmp/code-interpreter-sandbox/home/user", "executionTimeMs": 150 }, "executionTimeMs": 150 }
```

**WebSocket交互式终端端点**

**请求语法**:`GET ${BASEURL}/sandboxes/{sandboxId}/processes/tty?protocol=json&tenantId={阿里云主账号ID}`

**请求头**：

- `Connection: Upgrade`(必需)
- `Upgrade: websocket`(必需)
- `Sec-WebSocket-Key: {key}`(必需)
- `Sec-WebSocket-Version: 13`(必需)

**查询参数**:

- `protocol`(string, 可选): WebSocket 通信的协议模式
  
  - `json`(默认): 结构化消息的 JSON 消息格式
  - `text`: 用于 xterm.js 兼容性的直接文本流格式

**响应**: 101 Switching Protocols

**说明**：

- **交互式终端**：完整的双向终端通信
- **实时 I/O**：带终端控制序列的实时输入/输出流
- **会话持久化**：工作目录、环境变量和命令历史
- **终端功能**：支持颜色、光标控制、终端调整大小
- **无需上下文**：TTY 执行不需要上下文
- **使用场景**：交互式 shell 会话、系统管理、调试

**心跳保活机制**:

- **心跳间隔**：客户端每 30 秒发送一次 ping
- **超时检测**：服务器在 2 分钟内无心跳后关闭连接
- **超时警告**：服务器在 90 秒时发送警告
- **会话管理**：断开连接时 TTY 进程**被销毁**，重新连接时创建新会话
- **自动重连**：客户端应实现自动重连和会话重建

**会话行为**:

- **连接丢失**：TTY 进程立即终止，所有正在运行的命令停止
- **重新连接**：客户端重新连接到新的 TTY 会话，工作目录和环境重置
- **状态丢失**：命令历史、正在运行的进程和会话状态丢失
- **缓解措施**：使用 screen/tmux 创建在断开连接后仍能保持的持久会话

**消息类型（JSON 模式）**:

- `input`: 向终端发送输入（击键、命令）
- `output`: 从终端接收输出（stdout、stderr）
- `resize`: 调整终端尺寸
- `status`: 终端状态变化
- `ping`/`pong`: 连接保活心跳
- `connectionEstablished`: 连接确认，包含会话信息
- `timeoutWarning`: 连接超时前的警告
- `connectionClosing`: 连接关闭通知

**JSON 模式消息示例**:

发送输入：

```
{ "type": "input", "data": "ls -la\n" }
```

接收输出：

```
{ "type": "output", "data": "total 24\ndrwxr-xr-x 3 user user 4096 Jan 15 10:30 .\r\n", "stream": "stdout" }
```

调整大小：

```
{ "type": "resize", "rows": 24, "cols": 80 }
```

**文本模式**(`?protocol=text`- 用于 xterm.js):

- 发送：直接文本数据（击键、命令）
- 接收：直接终端输出（带 ANSI 转义码）
- 调整大小：二进制消息（8 字节：4 字节行数 + 4 字节列数，大端序）
- 无 JSON 包装，延迟更低，性能更好

### **进程管理**

**列出所有进程**

**请求语法**:`GET ${BASEURL}/sandboxes/{sandboxId}/processes`

**请求头**：`X-Acs-Parent-Id: ${阿里云主账号ID}`

**查询参数**: 无

**响应示例**：

```
{ "items": [ { "processId": 12345, "status": "running", "command": "python script.py", "tag": "my-process", "createdAt": "2025-11-15T10:30:00Z" } ], "total": 1 }
```

**按PID获取进程详情**

**请求语法**:`GET ${BASEURL}/sandboxes/{sandboxId}/processes/{pid}`

**路径参数**:

- `pid`（integer, 必需）：进程 ID

**请求头**：`X-Acs-Parent-Id: ${阿里云主账号ID}`

**查询参数**: 无

**响应示例**：

```
{ "processId": 12345, "status": "running", "command": "python script.py", "tag": "my-process", "createdAt": "2025-11-15T10:30:00Z", "working_dir": "/tmp/sandbox/home/user", "environment": { "PATH": "/usr/bin:/bin", "HOME": "/tmp/sandbox/home/user" }, "resourceUsage": { "cpuPercent": 10.5, "memoryMb": 128.0 } }
```

**强制停止进程**

**请求语法**:`DELETE ${BASEURL}/sandboxes/{sandboxId}/processes/{pid}`

**路径参数**:

- `pid`(integer, 必需)：要停止的进程 ID

**请求头**：`X-Acs-Parent-Id: ${阿里云主账号ID}`

**查询参数**: 无

**说明**:

- 通过发送 SIGTERM 信号强制停止进程，如果失败，则发送 SIGKILL 信号
- 这是一个破坏性操作，将立即终止进程

**响应示例**：

```
{ "pid": 12345, "stopped": true, "stopped_at": "2025-11-15T10:35:00Z", "message": "Process stopped successfully" }
```

**错误响应**

所有错误格式都应遵循以下格式：

```
{ "error": { "code": "ERROR_CODE", "message": "人类可读的错误消息", "details": { // 附加错误详情（可选） } } }
```

**常见错误码**

| **状态码** | **错误说明** | **处理建议** |
| --- | --- | --- |
| 400 | 请求参数错误 | 检查请求参数格式和必需字段 |
| 401 | 未授权访问 | 检查认证信息和权限配置 |
| 404 | 资源未找到 | 确认资源ID和路径正确 |
| 409 | 资源冲突 | 文件已存在或状态冲突 |
| 413 | 文件过大 | 文件超过100 MB限制，建议分段上传或压缩 |
| 500 | 内部服务器错误 | 联系技术支持 |
| 507 | 存储空间不足 | 清理文件后重试 |

**错误响应格式**

```
{ "code": "ERROR_CODE", "requestId": "abc123-def456-****", "message": "详细错误信息" }
```

**重试策略**

对于以下错误建议实施重试：

- 5xx 服务器错误：指数退避重试
- 429 限流错误：等待后重试
- 507 存储空间不足：清理后重试

## **更多信息**

### 资源管理

1. **及时清理资源**：
  
  - 完成任务后删除不需要的文件
  - 不再使用的上下文和会话应及时删除
  - 监控存储空间使用情况
2. **合理配置超时时间**：
  
  - 短期任务：使用较短的超时时间（5-10分钟）
  - 长期任务：适当延长超时时间（30分钟-6小时）

### 代码执行

1. **错误处理**：

```
import traceback try: # 你的代码 result = some_function() print(f"执行成功: {result}") except Exception as e: print(f"执行失败: {str(e)}") traceback.print_exc()
```

1. **大数据处理**：
  
  - 使用 pandas 分块读取大文件
  - 及时释放内存中的大对象
  - 使用生成器处理大量数据
2. **文件操作**：

```
import os import pandas as pd # 检查文件是否存在 if os.path.exists('/workspace/data.csv'): df = pd.read_csv('/workspace/data.csv') print(f"读取了 {len(df)} 行数据")
```

### 安全考虑

1. **输入验证**：
  
  - 验证上传文件的类型和大小
  - 检查文件路径防止目录遍历攻击
2. **权限控制**：
  
  - 使用最小权限原则配置 executionRoleArn
  - 定期审查和更新凭证
3. **数据保护**：
  
  - 敏感数据使用后及时删除
  - 避免在代码中硬编码敏感信息
