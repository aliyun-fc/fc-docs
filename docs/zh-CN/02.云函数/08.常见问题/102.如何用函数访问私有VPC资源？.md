# 如何用函数访问私有VPC资源？

函数计算支持函数访问特定的VPC。您可以为函数配置VPC相关信息，包括VPC ID、交换机ID和安全组ID。详情请参见[配置网络](https://help.aliyun.com/zh/functioncompute/fc/user-guide/configure-network-settings)。一旦VPC配置被启用，您的函数就运行在特定的VPC内部。

**

**说明**

建议您配置的交换机下的IP地址数量大于您可能使用的最大实例数，避免出现因IP不足引发的容器创建失败。
