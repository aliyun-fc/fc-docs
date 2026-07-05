# 在VPC中的函数如何访问公网？

函数计算在VPC功能中提供了启用或禁用您的函数访问公网的功能。一旦启用公网访问，函数计算将具有公网访问能力。您可以通过在[函数计算控制台](https://fcnext.console.aliyun.com)设置**允许函数访问公网**配置项，来启用或禁用公网访问。具体操作，请参见[配置网络](https://help.aliyun.com/zh/functioncompute/fc/user-guide/configure-network-settings)。

您也可以在您的VPC中搭建公网NAT，然后设置**允许函数访问公网**为**否**，这样函数就会通过VPC的公网NAT访问公网。
