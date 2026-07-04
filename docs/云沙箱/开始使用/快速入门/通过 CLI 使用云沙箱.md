# 通过 CLI 使用云沙箱

本文引导你通过 E2B CLI 查看模板、创建 Sandbox、进入终端并清理资源。

## 前置条件

- 已拥有阿里云账号，并具备函数计算相关操作权限。
- 已在函数计算控制台创建云沙箱 API Key。
- 已确认目标地域支持云沙箱，并且本机网络可访问该地域的云沙箱服务。
- 已安装满足版本要求的 E2B CLI。版本要求参见[使用约束](../使用约束.md)。

## 1. 安装 CLI

macOS 可以使用 Homebrew：

```bash
brew install e2b
```

也可以使用 npm：

```bash
npm i -g @e2b/cli
```

## 2. 配置环境变量

配置 API Key、API URL 和域名：

```bash
export E2B_API_KEY="<your-api-key>"
export E2B_API_URL="https://api.<region>.e2b.fc.aliyuncs.com"
export E2B_DOMAIN="<region>.e2b.fc.aliyuncs.com"
```

其中 `<region>` 为云沙箱服务所在地域。支持地域和 Endpoint 规则参见[使用约束](../使用约束.md)。

E2B CLI 还需要读取 `E2B_ACCESS_TOKEN`。接入 云沙箱时，其值与 `E2B_API_KEY` 相同：

```bash
export E2B_ACCESS_TOKEN=$E2B_API_KEY
```

## 3. 查看模板

```bash
e2b template list
```

输出中可以看到当前账号可用的模板。以下只展示输出格式，模板 ID、规格、创建时间和状态会随账号、地域和模板配置变化：

```text
Access  Template ID    Template Name         vCPUs  RAM MiB  Created at    Disk size MiB  names                buildStatus
Public  <template-id>  code-interpreter-v1       2     2048  <created-at>          10240  code-interpreter-v1  ready
```

## 4. 创建并连接 Sandbox

```bash
e2b sandbox create code-interpreter-v1
```

进入 Sandbox 终端后，可以执行：

```bash
python3 -c 'print("hello from sandbox")'
exit
```

## 5. 查看和终止 Sandbox

查看 Sandbox 列表：

```bash
e2b sandbox list
```

终止不再使用的 Sandbox：

```bash
e2b sandbox kill <sandbox-id>
```

任务完成后建议主动终止 Sandbox，避免资源持续占用。

## 下一步

- 使用 SDK 在应用中创建和管理 Sandbox，参见[通过 SDK 使用云沙箱](./通过%20SDK%20使用云沙箱.md)。
