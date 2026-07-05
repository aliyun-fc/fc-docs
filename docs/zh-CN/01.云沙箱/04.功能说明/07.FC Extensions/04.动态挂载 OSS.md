# 动态挂载 OSS

动态挂载 OSS 用于将 OSS 路径挂载到 Sandbox 内。挂载完成后，Sandbox 可以像访问本地文件一样读取或写入挂载目录。

该功能需要先在函数计算控制台或控制面完成 OSS 挂载配置。应用代码只需要使用约定的挂载路径。

## 读取 OSS 文件

```python
from e2b import Sandbox
import os

sandbox = Sandbox.create(
    "code-interpreter-v1",
    api_key=os.environ["E2B_API_KEY"],
    api_url=os.environ["E2B_API_URL"],
    domain=os.environ["E2B_DOMAIN"],
)

try:
    mount_path = os.environ.get("OSS_MOUNT_PATH", "/mnt/oss")
    input_file = f"{mount_path}/inputs/data.csv"

    result = sandbox.commands.run(
        f"python3 - <<'PY'\n"
        f"from pathlib import Path\n"
        f"path = Path({input_file!r})\n"
        f"print(path.exists())\n"
        f"print(path.stat().st_size if path.exists() else 0)\n"
        f"PY"
    )

    print(result.stdout.strip())
finally:
    sandbox.kill()
```

## 写入 OSS 文件

```typescript
import { Sandbox } from "e2b";

const sandbox = await Sandbox.create("code-interpreter-v1", {
  apiKey: process.env.E2B_API_KEY,
  apiUrl: process.env.E2B_API_URL,
  domain: process.env.E2B_DOMAIN,
});

try {
  const outputPath = `${process.env.OSS_MOUNT_PATH ?? "/mnt/oss"}/outputs/result.txt`;

  const result = await sandbox.commands.run(
    `python3 - <<'PY'
import os
from pathlib import Path

path = Path(os.environ["OUTPUT_PATH"])
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text("sandbox task finished\\n", encoding="utf-8")
print(path)
PY`,
    {
      envs: {
        OUTPUT_PATH: outputPath,
      },
    }
  );

  console.log(result.stdout.trim());
} finally {
  await sandbox.kill();
}
```

## 常见配置项

- OSS Bucket：需要挂载的存储空间。
- OSS 路径：挂载的目录或对象前缀。
- 挂载路径：Sandbox 内访问 OSS 的本地路径，例如 `/mnt/oss`。
- 访问权限：只读或读写。

## 注意事项

- 不要把整个 Bucket 以可写方式暴露给不可信代码。
- 多租户场景应使用独立目录前缀，例如 `tenants/<tenant-id>/tasks/<task-id>/`。
- 临时产物建议配置 OSS 生命周期清理规则。

配置方式参见官方文档：[动态挂载 OSS](https://help.aliyun.com/zh/functioncompute/mount-oss-dynamically)。
