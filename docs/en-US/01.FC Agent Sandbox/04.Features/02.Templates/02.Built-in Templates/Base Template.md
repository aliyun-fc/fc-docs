# Base Template

The base template provides a minimal cloud sandbox runtime environment, containing only the E2B envd-compatible base service. It is suitable for scenarios that require managing sandbox lifecycle, running basic commands, accessing the file system via E2B-compatible SDKs, or serving as a baseline for custom capabilities.

The base template aligns with E2B's Commands, Filesystem, and Sandbox lifecycle capabilities, and serves as the common foundation for the code-interpreter-v1 template, browser template, and All-in-One template.

## Features

| **Feature** | **Description** |
| --- | --- |
| envd Base Service | Built-in E2B envd-compatible service for sandbox creation, connection, basic commands, and file access |
| Lightweight Runtime | No pre-installed Code Interpreter service or browser automation service |
| Secure Isolation | Each sandbox instance has an independent file system and process space |
| Extensible Baseline | Suitable as a foundation for custom toolchains, business runtimes, or higher-level capabilities |

## Use Cases

| **Use Case** | **Description** |
| --- | --- |
| Basic Command Execution | Run simple Shell commands via envd for environment checks, file preparation, and other tasks |
| Custom Runtime Baseline | Install or wrap your own dependencies and tools on top of a minimal sandbox environment |
| SDK Connectivity Verification | Validate API Key, region, template creation, sandbox creation, and teardown workflows |
| Lightweight Tasks | Tasks that do not require a Python code interpreter service or browser automation capabilities |

## Default Configuration

The default configuration for the base template is as follows:

| **Configuration** | **Default Value** | **Description** |
| --- | --- | --- |
| Default Port | No business port | Provides envd base service |
| CPU | 2 vCPU | Minimum requirement |
| Memory | 2048 MB | Minimum requirement |
| Disk Size | 512 MB | Suitable for lightweight commands and temporary files |

## Quick Start

If you need code interpreter, browser automation, or a combination of both, please choose the [Code Interpreter v1 Template](Code Interpreter v1 Template.md), [Browser Template](Browser Template.md), or [All-in-One Template](All-in-One Template.md) respectively.

When `template` is not explicitly specified, a base sandbox is created by default.

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

TypeScript example:

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

## Related Documentation

- [Sandbox Template Overview](../02.Built-in Templates.md)
- [Build Templates](../03.Build Custom Image Templates.md)
- [Lifecycle](../../01.Sandbox/01.Lifecycle.md)
- [Code Interpreter v1 Template](Code Interpreter v1 Template.md)
- [Browser Template](Browser Template.md)
- [All-in-One Template](All-in-One Template.md)
