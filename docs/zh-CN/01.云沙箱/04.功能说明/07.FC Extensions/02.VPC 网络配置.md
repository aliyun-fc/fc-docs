# VPC 网络配置

VPC 网络配置用于让 Sandbox 访问专有网络中的资源，例如 RDS、Redis、内网 API、ACR EE 镜像仓库或自建服务。

该功能需要先在函数计算控制台或控制面完成 VPC、交换机、安全组等配置。应用侧仍然使用 E2B SDK 创建 Sandbox。

## 验证内网访问

```typescript
import { Sandbox } from "e2b";

const sandbox = await Sandbox.create("code-interpreter-v1", {
  apiKey: process.env.E2B_API_KEY,
  apiUrl: process.env.E2B_API_URL,
  domain: process.env.E2B_DOMAIN,
});

try {
  const endpoint = process.env.INTERNAL_API_ENDPOINT;
  if (!endpoint) {
    throw new Error("INTERNAL_API_ENDPOINT is required");
  }

  const result = await sandbox.commands.run(
    `python3 - <<'PY'
import os
import urllib.request

url = os.environ["INTERNAL_API_ENDPOINT"]
with urllib.request.urlopen(url, timeout=5) as response:
    print(response.status)
PY`,
    {
      envs: {
        INTERNAL_API_ENDPOINT: endpoint,
      },
      timeoutMs: 10_000,
    }
  );

  console.log(result.stdout.trim());
} finally {
  await sandbox.kill();
}
```

## 常见配置项

- VPC：Sandbox 需要访问的专有网络。
- vSwitch：Sandbox 使用的交换机。
- 安全组：控制 Sandbox 与目标资源之间的访问范围。
- 目标服务白名单：RDS、Redis、内网 API 等服务侧的访问控制。

## 注意事项

- VPC、vSwitch、云沙箱和目标资源应位于可访问的地域和网络范围内。
- 只开放 Sandbox 访问目标资源所需的端口和地址范围。
- 网络可达不等于具备业务权限，数据库、API、对象存储等资源仍需要服务侧鉴权。

配置方式参见官方文档：[VPC 网络配置](https://help.aliyun.com/zh/functioncompute/vpc-network-configuration)。
