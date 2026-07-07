# code-interpreter-v1 Template

The code-interpreter-v1 template provides a securely isolated code execution sandbox. It lets you safely execute code in languages such as Python and JavaScript in the cloud, and offers a complete data-plane API for file management, terminal command execution, context management, and more.

The code-interpreter-v1 template aligns with E2B Code Interpreter's code context, code execution, file access, and command capabilities.

## Features

| **Feature** | **Description** |
| --- | --- |
| Multi-language code execution | Securely executes Python, JavaScript, and other code, with context preserved through a Jupyter kernel |
| File system operations | Full file CRUD: upload, download, read, write, create directories, move, delete; supports text and binary files |
| Terminal command execution | Supports synchronous command execution and an interactive WebSocket terminal (TTY) with color, cursor control, and terminal resizing |
| Context management | Independent code execution environments; supports creating multiple contexts (kernels), each keeping its own variable state |
| Process management | List, query, and stop processes running inside the sandbox |
| Secure isolation | Dedicated isolation based on function instances; each sandbox instance has its own file system and process space |

## Use cases

| **Scenario** | **Description** |
| --- | --- |
| AI Agent code sandbox | Provides a safe code execution environment for AI Agents, preventing untrusted code from accessing or tampering with host system resources |
| Data analysis | Run Python data-analysis scripts in the sandbox, using libraries such as pandas and numpy to process data |
| File processing | Upload files to the sandbox, perform format conversion or data cleaning, and download the results |
| Script execution and automation | Run shell commands, install dependencies, and run automation scripts |

## Default configuration

The default configuration of the code-interpreter-v1 template is as follows:

| **Item** | **Default** | **Description** |
| --- | --- | --- |
| Container image | `sandbox-code-interpreter:v0.9.30` | Prebuilt code interpreter sandbox image |
| Default port | 5000 | Port the sandbox service listens on |
| CPU | 2 vCPU | Minimum requirement |
| Memory | 2048 MB | Minimum requirement |
| Disk size | 512 MB | 512 MB or 10240 MB available |

## Architecture

The Code Interpreter API is split into a control plane and a data plane:

| **Plane** | **Description** |
| --- | --- |
| Control-plane OpenAPI | Handles creation and lifecycle management of sandbox template and sandbox instance resources |
| Data-plane OpenAPI | Handles concrete calls such as code execution, file operations, terminal commands, and process management |

Data-plane base URL format: `https://{alibaba-cloud-primary-account-id}.e2b-data.cn-hangzhou.aliyuncs.com/`

## SDK usage

Whether you need to explicitly specify a `template` for the code-interpreter-v1 template depends on the SDK:

| **SDK** | **template parameter** | **Description** |
| --- | --- | --- |
| `e2b_code_interpreter` SDK | Not required | The dedicated SDK creates a `code-interpreter-v1` sandbox by default |
| `e2b` SDK | Must specify `code-interpreter-v1` | The general SDK creates a base sandbox by default, so you must explicitly select the code-interpreter-v1 template |

**Using the `e2b_code_interpreter` SDK:**

```python
import os
from e2b_code_interpreter import Sandbox

sbx = Sandbox.create(api_key=os.environ["E2B_API_KEY"])
execution = sbx.run_code("print('hello from code interpreter')")
print(execution.logs.stdout)
sbx.kill()
```

**Using the `e2b` SDK:**

```python
import os
from e2b import Sandbox

sbx = Sandbox.create(
    template="code-interpreter-v1",
    api_key=os.environ["E2B_API_KEY"],
)
result = sbx.commands.run("python --version")
print(result.stdout)
sbx.kill()
```

## Workflow

1. **Create a code-interpreter-v1 sandbox template**: create the template through the console or the OpenAPI.
2. **Start a sandbox instance**: create a sandbox instance from the template and obtain the sandbox ID.
3. **Create an execution context**: create a code execution context inside the sandbox (specify the language).
4. **Execute code**: run Python or JavaScript code through the context.

## Core API overview

### Sandbox instance management

| **Operation** | **Method** | **Path** |
| --- | --- | --- |
| Create sandbox instance | POST | `/sandboxes` |
| Stop sandbox instance | POST | `/sandboxes/{sandboxId}/stop` |
| Delete sandbox instance | DELETE | `/sandboxes/{sandboxId}` |
| Health check | GET | `/sandboxes/{sandboxId}/health` |

Example request to create a sandbox instance:

```json
POST ${BASEURL}/sandboxes

{
  "templateName": "my-code-interpreter",
  "sandboxId": "optional-custom-id"
}
```

Example response:

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

### Context management

| **Operation** | **Method** | **Path** |
| --- | --- | --- |
| List all contexts | GET | `/sandboxes/{sandboxId}/contexts` |
| Create a new context | POST | `/sandboxes/{sandboxId}/contexts` |
| Get context details | GET | `/sandboxes/{sandboxId}/contexts/{contextId}` |
| Delete a context | DELETE | `/sandboxes/{sandboxId}/contexts/{contextId}` |

Example request to create a context:

```json
POST ${BASEURL}/sandboxes/{sandboxId}/contexts

{
  "language": "python",
  "cwd": "/home/user"
}
```

### Code execution

Execute code synchronously through a context:

```json
POST ${BASEURL}/sandboxes/{sandboxId}/contexts/execute

{
  "contextId": "kernel-12345-67890",
  "code": "print('hello from sandbox')",
  "timeout": 30
}
```

Example response:

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

### File system operations

| **Operation** | **Method** | **Path** |
| --- | --- | --- |
| Read a file | GET | `/sandboxes/{sandboxId}/files?path={path}` |
| Write a file | POST | `/sandboxes/{sandboxId}/files` |
| List a directory | GET | `/sandboxes/{sandboxId}/filesystem?path={path}` |
| Get file info | GET | `/sandboxes/{sandboxId}/filesystem/stat?path={path}` |
| Download a file | GET | `/sandboxes/{sandboxId}/filesystem/download?path={path}` |
| Upload a file | POST | `/sandboxes/{sandboxId}/filesystem/upload` (multipart/form-data, max 100 MB) |
| Create a directory | POST | `/sandboxes/{sandboxId}/filesystem/mkdir` |
| Move/rename | POST | `/sandboxes/{sandboxId}/filesystem/move` |
| Delete file/directory | POST | `/sandboxes/{sandboxId}/filesystem/remove` |

Text files return the `content` field as UTF-8; binary files are returned base64-encoded. File uploads use `multipart/form-data` and support up to 100 MB.

### Terminal and process management

| **Operation** | **Method** | **Path** |
| --- | --- | --- |
| Execute command synchronously | POST | `/sandboxes/{sandboxId}/processes/cmd` (30-second timeout) |
| Interactive terminal | GET | `/sandboxes/{sandboxId}/processes/tty?protocol=json` (WebSocket) |
| List all processes | GET | `/sandboxes/{sandboxId}/processes` |
| Get process details | GET | `/sandboxes/{sandboxId}/processes/{pid}` |
| Stop a process | DELETE | `/sandboxes/{sandboxId}/processes/{pid}` |

Example of synchronous command execution:

```json
POST ${BASEURL}/sandboxes/{sandboxId}/processes/cmd

{
  "command": "ls -la /home/user",
  "cwd": "/home/user"
}
```

Example response:

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

The interactive terminal supports two protocol modes: `json` (structured messages) and `text` (xterm.js compatible). The client must send a heartbeat every 30 seconds; the connection closes after 2 minutes without a heartbeat.

## Sandbox instance states

A sandbox instance goes through the following states during its lifecycle:

| **State** | **Description** |
| --- | --- |
| `CREATING` | Being created |
| `READY` | Ready to use |
| `TERMINATED` | Stopped |

## Limitations

| **Item** | **Constraint** |
| --- | --- |
| Sandbox lifetime | A single sandbox instance lasts at most 6 hours |
| Idle timeout | Configurable through the `sandboxIdleTimeoutSeconds` parameter |
| File upload size | Up to 100 MB per upload |
| Code execution timeout | Up to 30 seconds per synchronous execution |
| Hidden files | Creating hidden files that start with `.` is not allowed |

## Best practices

**Clean up resources promptly**: after a task finishes, delete files, contexts, and sandbox instances you no longer need, and monitor storage usage.

**Configure timeouts sensibly**: use shorter timeouts for short-lived tasks (5–10 minutes) and extend them for long-running tasks (30 minutes–6 hours).

**Error handling**: use exponential backoff to retry 5xx server errors, and wait before retrying 429 rate-limit errors.

## Related documents

- [Built-in Templates](../02.Built-in%20Templates.md)
- [Build Custom Image Templates](../03.Build%20Custom%20Image%20Templates.md)
- [Lifecycle](../../01.Sandbox/01.Lifecycle.md)
- [Base Template](Base%20Template.md) (choose when you only need the envd base capabilities)
- [Browser Template](Browser%20Template.md) (choose when you only need browser automation)
- [All-in-One Template](All-in-One%20Template.md) (choose when you need both browser and code execution)
