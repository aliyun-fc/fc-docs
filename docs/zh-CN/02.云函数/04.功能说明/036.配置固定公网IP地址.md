# 配置固定公网IP地址

函数计算系统默认的出口IP是动态的，无固定网段。而函数计算访问数据库、微信小程序或其他第三方服务时，需通过配置白名单来访问，此时您可以使用函数计算的固定公网IP功能绑定一个固定IP公网地址，然后将其添加到白名单列表中。本文介绍如何在函数计算控制台配置函数出口方向的固定公网IP地址。

## 注意事项

- 固定IP地址功能需配合专有网络VPC的公网NAT网关来完成。通过创建一个公网NAT网关，并为其绑定一个弹性公网IP地址和添加一个SNAT条目，允许VPC内的实例通过此弹性公网IP地址访问公网。此时，在公网接收端查询到的客户端IP地址为该NAT网关绑定的弹性公网IP地址。
- NAT网关和弹性公网IP地址均只能在某个地域的固定可用区购买。如果NAT网关、弹性公网IP与函数计算的函数所在的可用区不一致，您必须通过设置交换机来实现跨可用区公网互通。更多信息，请参见[函数计算支持的可用区](https://help.aliyun.com/zh/functioncompute/fc/user-guide/configure-network-settings#section-40g-39j-s9a)。
- 弹性公网IP地址可以在同一地域下的函数之间共享。
- RAM用户使用固定IP地址功能前，需先使用阿里云主账号登录[RAM 访问控制](https://ram.console.aliyun.com/overview)，为其授予`AliyunECSFullAccess`，`AliyunVPCFullAccess`，`AliyunEIPFullAccess`，AliyunRAMFullAccess和`AliyunNATGatewayFullAccess`权限。

## 计费说明

配置固定公网IP地址可能会创建NAT网关和弹性公网IP地址，产生一定的费用。具体信息，请参见[NAT 网关计费](https://help.aliyun.com/zh/nat-gateway/nat-gateway-billing#concept-z13-hty-ydb)和[弹性公网IP地址计费](https://help.aliyun.com/zh/eip/billing-overview#concept-645525)。

## 首次配置固定公网IP地址

### **前提条件**

- 已完成函数访问VPC资源相关权限和网络的配置。具体操作，请参见[配置网络和角色](https://help.aliyun.com/zh/functioncompute/fc/user-guide/configure-network-settings#section-rjq-d08-jfe)。
- 已配置**允许访问 VPC**为**是**。具体操作，请参见[配置网络](https://help.aliyun.com/zh/functioncompute/fc/user-guide/configure-network-settings)。

### **操作步骤**

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com)，在左侧导航栏，选择**函数管理**>**函数**。
2. 在顶部菜单栏，选择地域，然后在**函数**页面，单击目标函数。
3. 在函数详情页面，选择**配置**页签，单击**高级配置**右侧的**编辑**。
4. 在**高级配置**面板，找到**网络**选项，参数**固定公网 IP**选择开启，参数**允许函数默认网卡访问公网**选择为**否**。
  
  **
  
  **说明**
  
  为保证函数正常访问外部网络，您可以先配置**允许函数默认网卡访问公网**为**是**，固定IP生效之后再配置**允许函数默认网卡访问公网**为**否**，平滑迁移流量。
5. 单击**部署**，在弹出的**固定公网 IP 配置**对话框，仔细阅读提示信息，选中复选框，然后单击**确定**。
  
  1~2分钟后，网络配置完成。您可以查看到刚才保存的网络配置信息，也可以前往[专有网络控制台](https://vpc.console.aliyun.com/)，查看刚才关联或自动创建的公网NAT网关相关资源信息。

### **结果验证**

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com)，在左侧导航栏，选择**函数管理**>**函数**。
2. 在顶部菜单栏，选择地域，然后在**函数**页面，单击目标函数。
3. 在函数详情页面，选择**代码**页签，在代码编辑器中，编写代码。
  
  本文以Python代码为例。
  
  ```
  # -*- coding: utf-8 -*- import logging import requests def handler(event, context): logger = logging.getLogger() try: r = requests.get('https://myip.ipip.net') clientIP = r.content.split()[1] logger.info('Client IP: ' + clientIP) except: r = requests.get('http://ipinfo.io') clientIP = r.json()['ip'] logger.info('Client IP: ' + clientIP) return clientIP
  ```
4. 完成函数编写后，单击**部署代码**，然后单击**测试函数**。
  
  执行成功后，查看返回的客户端IP地址，即配置的固定IP地址。

## 增加其他固定公网IP地址

如您需要增加其他的固定IP地址，操作步骤如下。

1. 在函数详情页面，选择**配置**页签，单击**高级配置**右侧的**编辑**，在**高级配置**面板，找到**网络**选项，单击**固定公网 IP**配置项下方的**创建新的弹性公网IP**。
  
  页面自动跳转到[专有网络控制台](https://vpc.console.aliyun.com/)。
2. 在[专有网络控制台](https://vpc.console.aliyun.com/)，手动创建一个弹性公网IP地址并绑定到对应的NAT网关。具体步骤，请参见[申请EIP](https://help.aliyun.com/zh/eip/apply-for-new-eips#task-bh5-dll-vdb)。
  
  绑定成功后，前往函数的网络配置页面，您可查看到刚才保存的函数配置信息。

## 相关操作

如您需要关闭固定IP地址功能或删除已配置的固定IP地址，请先配置**允许函数默认网卡访问公网**为**是**，然后单击已添加的固定公网IP地址，前往[专有网络控制台](https://vpc.console.aliyun.com/)解绑NAT并删除相关资源。
