# Code Interpreter v1 Template

The code-interpreter-v1 template provides a securely isolated code execution sandbox environment, supporting secure execution of Python, JavaScript, and other language code in the cloud, with comprehensive data plane APIs for file management, terminal command execution, and context management.

The code-interpreter-v1 template aligns with E2B Code Interpreter's code context, code execution, file access, and command capabilities.

## Features

| **Feature** | **Description** |
| --- | --- |
| Multi-language Code Execution | Supports secure execution of Python, JavaScript, and other languages, with context persistence based on Jupyter Kernel |
| File System Operations | Complete file CRUD capabilities: upload, download, read, write, create directories, move, delete; supports text and binary files |
| Terminal Command Execution | Supports synchronous command execution and WebSocket interactive terminal (TTY), with color, cursor control, and terminal resize |
| Context Management | Independent code execution environments; supports creating multiple contexts (Kernels), each maintaining its own variable state |
| Process Management | List, query, and stop processes running inside the sandbox |
| Secure Isolation | Function instance-level isolation; each sandbox instance has an independent file system and process space |

## Use Cases

| **Use Case** | **Description** |
| --- | --- |
| AI Agent Code Sandbox | Provides a secure code execution environment for AI Agents, preventing untrusted code from accessing or modifying host system resources |
| Data Analysis | Run Python data analysis scripts in the sandbox, processing data with libraries such as pandas and numpy |
| File Processing | Upload files to the sandbox, perform format conversion, data cleaning, and other operations, then download the results |
| Script Execution & Automation | Execute Shell commands, install dependencies, and run automation scripts |

## Default Configuration

The default configuration for the code-interpreter-v1 template is as follows:

| **Configuration** | **Default Value** | **Description** |
| --- | --- | --- |
| Container Image | `sandbox-code-interpreter:v0.9.30` | Pre-built code interpreter sandbox image |
| Default Port | 5000 | Sandbox service listening port |
| CPU | 2 vCPU | Minimum requirement |
| Memory | 2048 MB | Minimum requirement |
| Disk Size | 512 MB | Options: 512 MB or 10240 MB |

## Architecture

The Code Interpreter API is divided into two layers: control plane and data plane:

| **Layer** | **Description** |
| --- | --- |
| Control Plane OpenAPI | Responsible for creating sandbox templates and sandbox instance resources, and managing their lifecycle |
| Data Plane OpenAPI | Responsible for specific function calls such as code execution, file operations, terminal commands, and process management |

Data plane Base URL format: `https://{Alibaba Cloud main account ID}.e2b-data.cn-hangzhou.aliyuncs.com/`

## SDK Usage

When using the code-interpreter-v1 template, whether you need to explicitly specify `template` depends on the SDK:

| **SDK** | **template Parameter** | **Description** |
| --- | --- | --- |
| `e2b_code_interpreter` SDK | Not required | The dedicated SDK creates `code-interpreter-v1` sandboxes by default |
| `e2b` SDK | Specify `code-interpreter-v1` | The general SDK creates base sandboxes by default; you need to explicitly select the code-interpreter-v1 template |

**Using the `e2b_code_interpreter` SDK:**

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

TypeScript example:

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

**Using the `e2b` SDK:**

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

## Usage Workflow

1. **Create a code-interpreter-v1 sandbox template**: Create a template via the console or OpenAPI.
2. **Start a sandbox instance**: Create a sandbox instance based on the template and obtain the sandbox ID.
3. **Create an execution context**: Create a code execution context inside the sandbox (specify the language type).
4. **Execute code**: Execute Python or JavaScript code through the context.

## Core API Overview

### Sandbox Instance Management

| **Operation** | **Method** | **Path** |
| --- | --- | --- |
| Create sandbox instance | POST | `/sandboxes` |
| Stop sandbox instance | POST | `/sandboxes/{sandboxId}/stop` |
| Delete sandbox instance | DELETE | `/sandboxes/{sandboxId}` |
| Health check | GET | `/sandboxes/{sandboxId}/health` |

Create sandbox instance request example:

```json
POST ${BASEURL}/sandboxes

{
  "templateName": "my-code-interpreter",
  "sandboxId": "optional-custom-id"
}
```

Response example:

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

### Context Management

| **Operation** | **Method** | **Path** |
| --- | --- | --- |
| List all contexts | GET | `/sandboxes/{sandboxId}/contexts` |
| Create new context | POST | `/sandboxes/{sandboxId}/contexts` |
| Get context details | GET | `/sandboxes/{sandboxId}/contexts/{contextId}` |
| Delete context | DELETE | `/sandboxes/{sandboxId}/contexts/{contextId}` |

Create context request example:

```json
POST ${BASEURL}/sandboxes/{sandboxId}/contexts

{
  "language": "python",
  "cwd": "/home/user"
}
```

### Code Execution

Execute code synchronously through a context:

```json
POST ${BASEURL}/sandboxes/{sandboxId}/contexts/execute

{
  "contextId": "kernel-12345-67890",
  "code": "print('hello from sandbox')",
  "timeout": 30
}
```

Response example:

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

### File System Operations

| **Operation** | **Method** | **Path** |
| --- | --- | --- |
| Read file | GET | `/sandboxes/{sandboxId}/files?path={path}` |
| Write file | POST | `/sandboxes/{sandboxId}/files` |
| List directory | GET | `/sandboxes/{sandboxId}/filesystem?path={path}` |
| Get file info | GET | `/sandboxes/{sandboxId}/filesystem/stat?path={path}` |
| Download file | GET | `/sandboxes/{sandboxId}/filesystem/download?path={path}` |
| Upload file | POST | `/sandboxes/{sandboxId}/filesystem/upload` (multipart/form-data, max 100 MB) |
| Create directory | POST | `/sandboxes/{sandboxId}/filesystem/mkdir` |
| Move/Rename | POST | `/sandboxes/{sandboxId}/filesystem/move` |
| Delete file/directory | POST | `/sandboxes/{sandboxId}/filesystem/remove` |

Text files return the `content` field in UTF-8 encoding, while binary files return it in base64 encoding. File uploads use `multipart/form-data` format, with a maximum size of 100 MB.

### Terminal and Process Management

| **Operation** | **Method** | **Path** |
| --- | --- | --- |
| Synchronous command execution | POST | `/sandboxes/{sandboxId}/processes/cmd` (30-second timeout) |
| Interactive terminal | GET | `/sandboxes/{sandboxId}/processes/tty?protocol=json` (WebSocket) |
| List all processes | GET | `/sandboxes/{sandboxId}/processes` |
| Get process details | GET | `/sandboxes/{sandboxId}/processes/{pid}` |
| Stop process | DELETE | `/sandboxes/{sandboxId}/processes/{pid}` |

Synchronous command execution example:

```json
POST ${BASEURL}/sandboxes/{sandboxId}/processes/cmd

{
  "command": "ls -la /home/user",
  "cwd": "/home/user"
}
```

Response example:

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

The interactive terminal supports `json` (structured messages) and `text` (xterm.js compatible) protocol modes. The client must send a heartbeat every 30 seconds; the connection is closed after 2 minutes without a heartbeat.

## Sandbox Instance States

A sandbox instance goes through the following states during its lifecycle:

| **State** | **Description** |
| --- | --- |
| `CREATING` | Being created |
| `READY` | Ready to use |
| `TERMINATED` | Stopped |

## Usage Limits

| **Limit** | **Constraint** |
| --- | --- |
| Sandbox lifecycle | Maximum lifecycle of 6 hours per sandbox instance |
| Idle timeout | Configurable via the `sandboxIdleTimeoutSeconds` parameter |
| File upload size | Maximum 100 MB per upload |
| Code execution timeout | Maximum 30 seconds per synchronous execution |
| Hidden files | Creating hidden files starting with `.` is not allowed |

## Best Practices

**Clean up resources promptly**: Delete unnecessary files, contexts, and sandbox instances after completing tasks, and monitor storage usage.

**Configure timeouts appropriately**: Use shorter timeouts (5–10 minutes) for short-term tasks, and extend as appropriate (30 minutes to 6 hours) for long-term tasks.

**Error handling**: Implement exponential backoff retries for 5xx server errors, and wait before retrying on 429 rate-limiting errors.

## Related Documentation

- [Sandbox Template Overview](../02.Built-in Templates.md)
- [Build Templates](../03.Build Custom Image Templates.md)
- [Lifecycle](../../01.Sandbox/01.Lifecycle.md)
- [Base Template](Base Template.md) (choose when you only need envd basic capabilities)
- [Browser Template](Browser Template.md) (choose when you only need browser automation capabilities)
- [All-in-One Template](All-in-One Template.md) (choose when you need both browser and code execution capabilities)
