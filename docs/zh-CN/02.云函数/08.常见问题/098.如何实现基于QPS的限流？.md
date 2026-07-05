# 如何实现基于QPS的限流？

函数计算FC的不支持基于QPS的限流功能。您需要借助API网关或Web应用防火墙WAF来实现此功能。如果您不想使用API网关或WAF来实现此功能，您可以考虑使用轻量级服务器或ECS等产品部署支持QPS限流功能的软件（例如：[1panel](https://1panel.cn/)）来保护您的函数。

相关文档详见：[为自定义域名开启Web应用防火墙](https://help.aliyun.com/zh/functioncompute/fc/user-guide/enable-waf-protection)，[Web应用防火墙的防护规则](https://help.aliyun.com/zh/waf/web-application-firewall-3-0/user-guide/protection-rules/)，[API网关插件](https://help.aliyun.com/zh/api-gateway/traditional-api-gateway/user-guide/plug-ins-of-the-ip-access-control-type)。
