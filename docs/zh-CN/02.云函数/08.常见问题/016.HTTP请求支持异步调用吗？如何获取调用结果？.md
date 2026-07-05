# HTTP请求支持异步调用吗？如何获取调用结果？

支持。您可以通过增加请求头`"X-Fc-Invocation-Type":"Async"`的方式实现HTTP请求的异步调用。具体信息，请参见[HTTP触发器概述](https://help.aliyun.com/zh/functioncompute/fc/user-guide/http-triggers-overview)。

如您想获取调用结果，只能通过配置异步目标服务实现结果回调功能。具体操作，请参见[结果回调](https://help.aliyun.com/zh/functioncompute/result-callback)。
