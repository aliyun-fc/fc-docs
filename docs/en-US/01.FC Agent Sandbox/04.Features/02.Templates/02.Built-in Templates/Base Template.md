# Base Template

The base template provides a minimal FC Agent Sandbox runtime that contains only the E2B envd-compatible base service. It suits scenarios where you need to manage the sandbox lifecycle through an E2B-compatible SDK, run basic commands, access the file system, or use it as a baseline for custom capabilities.

The base template aligns with the base experience around E2B Commands, Filesystem, and the Sandbox lifecycle, and is the shared capability foundation of the code-interpreter-v1 template, the browser template, and the all-in-one template.

## Features

| **Feature** | **Description** |
| --- | --- |
| envd base service | Built-in E2B envd-compatible service that supports sandbox creation, connection, basic commands, and file access |
| Lightweight runtime | Does not preinstall the Code Interpreter service or browser automation service |
| Secure isolation | Each sandbox instance has its own file system and process space |
| Extensible baseline | Suitable as a base template for custom toolchains, business runtimes, or higher-level capabilities |

## Use cases

| **Scenario** | **Description** |
| --- | --- |
| Basic command execution | Run simple shell commands through envd for tasks such as environment checks and file preparation |
| Custom runtime baseline | Install or wrap your own dependencies and tools on top of a minimal sandbox environment |
| SDK connectivity checks | Validate API keys, regions, and the template/sandbox creation and destruction flow |
| Lightweight tasks | Tasks that need neither the Python code interpreter service nor browser automation |

## Default configuration

The default configuration of the base template is as follows:

| **Item** | **Default** | **Description** |
| --- | --- | --- |
| Default port | No service port | Provides the envd base service |
| CPU | 2 vCPU | Minimum requirement |
| Memory | 2048 MB | Minimum requirement |
| Disk size | 512 MB | Suitable for lightweight commands and temporary files |

## Quickstart

If you need the code interpreter, browser automation, or both, choose the [code-interpreter-v1 template](Code%20Interpreter%20v1%20Template.md), the [browser template](Browser%20Template.md), or the [all-in-one template](All-in-One%20Template.md) respectively.

When you do not explicitly specify a `template`, a base sandbox is created by default.

```python
import os

from e2b import Sandbox

sbx = Sandbox.create(
    api_key=os.environ["E2B_API_KEY"],
    timeout=600,
)

result = sbx.commands.run("echo hello from base template")
print(result.stdout)

sbx.kill()
```

## Related documents

- [Built-in Templates](../02.Built-in%20Templates.md)
- [Build Custom Image Templates](../03.Build%20Custom%20Image%20Templates.md)
- [Lifecycle](../../01.Sandbox/01.Lifecycle.md)
- [Code Interpreter v1 Template](Code%20Interpreter%20v1%20Template.md)
- [Browser Template](Browser%20Template.md)
- [All-in-One Template](All-in-One%20Template.md)
