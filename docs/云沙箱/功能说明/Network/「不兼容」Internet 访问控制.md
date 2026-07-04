# 「不兼容」Internet 访问控制

E2B 支持通过 `allowInternetAccess` 或网络配置控制沙箱出站访问。云沙箱当前未将该能力作为 E2B 兼容功能对外提供。

不建议在云沙箱接入路径中依赖以下配置：

- `allowInternetAccess`
- `network.denyOut`
- `network.allowOut`

如需限制外部访问，应在业务系统、VPC、代理或企业网络治理层实现。

