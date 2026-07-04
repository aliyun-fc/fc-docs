# E2B 兼容与迁移

## 已有 E2B 应用如何接入云沙箱？

优先保持 E2B SDK 调用方式不变，只替换 API Key、API URL 和域名。

```bash
export E2B_API_KEY="<your-api-key>"
export E2B_API_URL="https://api.<region>.e2b.fc.aliyuncs.com"
export E2B_DOMAIN="<region>.e2b.fc.aliyuncs.com"
```

替换后先验证四件事：创建 Sandbox、执行命令、读写文件、释放资源。不要一开始就迁移复杂模板、网络和存储逻辑。

## 为什么官方 E2B 示例不需要配置 Endpoint？

E2B 官方示例默认访问 E2B 服务。云沙箱是 FC 侧 E2B 兼容端点，因此必须显式配置 `E2B_API_URL` 和 `E2B_DOMAIN`。

`E2B_API_URL`、`E2B_DOMAIN`、模板和 Sandbox 需要属于同一地域。地域不一致时，常见现象是创建失败、连接失败或模板找不到。

## E2B CLI 为什么还要配置 `E2B_ACCESS_TOKEN`？

E2B CLI 读取 `E2B_ACCESS_TOKEN`。接入云沙箱时，它与 `E2B_API_KEY` 使用同一个值。

```bash
export E2B_ACCESS_TOKEN=$E2B_API_KEY
```

如果 SDK 可用但 CLI 不可用，优先检查这个变量。

## 云沙箱是否完全等同于 E2B？

不是。云沙箱首先提供 E2B SDK 友好的开发体验，让已有 E2B 应用可以用较低改造成本迁移到 云沙箱；在此基础上，云沙箱会结合阿里云基础设施继续扩展企业级能力。

从产品定位看，云沙箱不是简单复制 E2B，而是在兼容 E2B 开发者体验的同时，增强云上运行能力，例如 VPC 接入、企业级精细化权限控制、NAS/OSS/RDS 等云上资源连接，以及面向企业生产环境的治理和集成能力。长期看，云沙箱会更接近“E2B 友好体验 + 云上企业级增强”的能力超集。

迁移时仍要按当前已开放能力判断。涉及 Snapshot、Volume、Team、Access Token 管理、Metrics/Logs、Network Config Update 或云上增强能力时，应先查[E2B 兼容说明](../开始使用/E2B%20兼容说明.md)，或联系产品/销售确认当前支持范围、开通方式和使用边界。

## API Key 能通过 E2B SDK 管理吗？

不能。云沙箱 API Key 由函数计算控制台创建和管理，不通过 E2B SDK 管理。

生产环境应按应用、环境或工作空间隔离 API Key。不要把完整 API Key 写入代码、模板、日志、命令输出、下载文件或前端页面。

## Python 和 TypeScript 示例为什么参数名不同？

这是 SDK 语言风格差异。Python 常见参数是 `api_key`、`api_url`，TypeScript 常见参数是 `apiKey`、`apiUrl`。

排查时以当前语言 SDK 的类型定义和示例为准，不要把另一个语言的字段名直接复制过来。

## 迁移后创建成功，但 `run_code` 或端口访问失败怎么办？

这类问题通常不是鉴权问题，而是模板、启动命令、服务就绪或端口监听问题。

先用内置模板验证 `run_code`、命令执行和文件读写。如果内置模板正常，自定义模板需要重点检查 Code Interpreter 依赖、启动命令、监听端口和就绪条件。

## E2B 的 Volume、Storage、Snapshot 能直接迁移吗？

不要默认直接迁移。云沙箱当前应以已兼容能力为准。

如果原应用依赖 Volume 或 Snapshot 保存状态，需要先确认云沙箱当前是否支持对应接口；如果依赖 Storage、Archil、Cloud buckets 或 FUSE 挂载，也应先确认是否属于正式兼容路径。不能确认时，不应写入 FAQ 作为推荐方案。
