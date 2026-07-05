# 如何配置IP黑名单和白名单？

函数计算FC的HTTP触发器和自定义域名不支持配置IP黑白名单的功能。您需要使用API网关或Web应用防火墙WAF来实现此功能。如果您不想使用API网关或WAF来实现此功能，您可以在FC的业务代码中获取请求头，请求头中可以获取到客户端IP，并自行添加判断逻辑来实现IP黑白名单的功能。

相关文档详见：[为自定义域名开启Web应用防火墙](https://help.aliyun.com/zh/functioncompute/fc/user-guide/enable-waf-protection)，[Web应用防火墙的防护规则](https://help.aliyun.com/zh/waf/web-application-firewall-3-0/user-guide/protection-rules/)，[API网关插件](https://help.aliyun.com/zh/api-gateway/traditional-api-gateway/user-guide/plug-ins-of-the-ip-access-control-type)。
