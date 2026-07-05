# 开启Web应用防火墙

阿里云Web应用防火墙（简称WAF 3.0）支持对函数或者应用的业务流量进行恶意特征识别，对流量进行清洗和过滤后，将正常和安全的流量回源至后端函数，避免函数被恶意侵入。本文介绍如何通过控制台为函数计算的自定义域名开启Web应用防火墙功能。

## 背景信息

函数计算与WAF 3.0深度集成后，支持自定义域名级别的防护，为您的网站或App业务提供一站式安全防护。

## 使用限制

函数计算自定义域名的Web应用防火墙功能目前仅支持华东1（杭州）、华东2（上海）、华北2（北京）、华南1（深圳）和华北3（张家口）地域。

## 计费说明

开启自定义域名的Web应用防火墙后，函数计算本身不计费，但WAF 3.0将根据使用情况计费。更多信息，请参见[WAF 3.0计费概述](https://help.aliyun.com/zh/waf/web-application-firewall-3-0/overview-7#task-2238382)。

## 前提条件

已开通WAF 3.0服务。具体操作，请参见[购买WAF 3.0包年包月实例](https://help.aliyun.com/zh/waf/web-application-firewall-3-0/user-guide/purchase-a-subscription-waf-3-0-instance#task-2152697)或[开通WAF 3.0按量付费实例](https://help.aliyun.com/zh/waf/web-application-firewall-3-0/user-guide/purchase-a-pay-as-you-go-waf-3-0-instance#task-2152697)。

## 操作步骤

您可以在创建自定义域名的同时开启Web应用防火墙，也可以为已有自定义域名开启Web应用防火墙。

### 创建自定义域名时开启Web应用防火墙

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com)，在左侧导航栏，选择**函数管理**>**域名管理**。
2. 在顶部菜单栏，选择地域，然后在**域名管理**页面，单击**添加自定义域名**。
3. 在**添加自定义域名**页面，填写**域名**，配置项**Web 应用防火墙**选择**启用**，然后单击**创建**。
  
  关于各配置项的说明，请参见[配置自定义域名](https://help.aliyun.com/zh/functioncompute/fc/configure-custom-domain-names#section-4yb-ztm-q9v)。

### 为已有自定义域名开启Web应用防火墙

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com)，在左侧导航栏，选择**函数管理**>**域名管理**。
2. 在**域名管理**页面，单击目标自定义域名右侧**操作**列的**编辑**。
3. 在**编辑自定义域名**页面，配置项**Web 应用防火墙**选择**启用**，然后单击**保存**。

## 后续操作

开启Web应用防火墙后，网站访问流量将经过WAF并受到WAF的防护。WAF包含多种防护检测模块，帮助网站防御不同类型的安全威胁。其中规则防护引擎和CC安全防护模块默认开启，分别用于防御常见的Web应用攻击（例如SQL注入、XSS跨站或WebShell上传等）和CC攻击。其他防护模块需要您手动开启并配置具体防护规则。更多信息，请参见[防护配置概述](https://help.aliyun.com/zh/waf/web-application-firewall-3-0/user-guide/protection-configuration-overview#concept-tzp-g2m-42b)。
