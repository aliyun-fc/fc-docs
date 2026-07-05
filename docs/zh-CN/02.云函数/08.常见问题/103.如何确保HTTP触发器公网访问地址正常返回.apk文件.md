# 如何确保HTTP触发器公网访问地址正常返回.apk文件

本文介绍**HTTP触发器公网访问地址**无法正常返回apk文件的原因和解决方法。

## **问题现象**

通过**HTTP触发器公网访问地址**（https://[subdomain-prefix].[region].fcapp.run）访问服务，当以直接返回文件形式访问apk文件时，服务器返回400错误，错误码为ApkDownloadForbidden。

## **问题原因**

出于安全考虑，自2024年06月10日起，通过**HTTP触发器公网访问地址**访问该日期之后创建的函数时，请求将被阻断。

## **解决办法**

通过**HTTP触发器内网访问地址**或**自定义域名**返回apk文件。

| **访问方式** | **具体步骤** |
| --- | --- |
| **HTTP触发器内网访问地址**（https://[subdomain-prefix].[region]-vpc.fcapp.run） | 1. 登录[函数计算控制台](https://fcnext.console.aliyun.com/)，在左侧导航栏，单击**函数**。<br>2. 在顶部菜单栏，选择地域，然后在**函数**页面，单击目标函数。<br>3. 在函数详情页面，选择**配置**页签，然后在左侧选择**触发器**。<br>4. 在**触发器**页面**配置信息**中复制**内网访问地址**链接进行访问。 |
| **自定义域名** | 请参见[配置自定义域名](https://help.aliyun.com/zh/functioncompute/fc/configure-custom-domain-names)。 |
