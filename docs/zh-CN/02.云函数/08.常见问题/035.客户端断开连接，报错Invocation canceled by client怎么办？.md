# 客户端断开连接，报错Invocation canceled by client怎么办？

本文介绍报错Invocation canceled by client的原因和解决方案。

## 问题现象

在请求日志中查到报错信息如下所示。

```
FC Invoke End RequestId: 1-64263a4b-2cd7c98b677*********, Error: Invocation canceled by client (duration: 4912ms, maxMemoryUsage: 0.00MB)
```

## 可能原因

发起调用的客户端主动取消了请求，导致函数执行异常中断，函数执行报错。

## 解决方案

排查步骤如下所示。

1. 根据报错日志，确认客户端主动取消请求时，函数已执行的时间。
  
  本文示例中，`duration: 4912ms`表示函数运行接近5s。
2. 根据业务情况判断该运行时间是否符合预期。
  
  - 如果符合预期，则需要增加客户端超时时间。具体操作，请参见[函数执行时间符合预期](#p-mvh-bw1-msi)。
  - 如果不符合预期，则需要根据日志排查函数的运行链路，确认具体是哪部分逻辑导致执行时间增加。具体操作，请参见[函数执行时间不符合预期](#p-1ug-69r-leb)。

### 函数执行时间符合预期

- 如果您通过SDK/API调用函数，建议将请求的超时时间设置为大于函数配置的超时时间。
  
  例如，使用Golang语言和函数计算的API调用函数，可以通过[http.Client](https://pkg.go.dev/net/http#Client)中的Timeout属性设置请求超时时间。如果在发起请求时使用了[context.Context](https://pkg.go.dev/context#Context)，可以调整Context的截止时间或超时时间。
- 如果您通过其他服务调用函数，可以在该服务的控制台修改后端超时时间。
  
  例如，前端通过API网关调用函数，可以在API网关控制台修改API的后端超时配置。具体操作，请参见[创建 API](https://help.aliyun.com/zh/api-gateway/traditional-api-gateway/user-guide/create-an-api#ea5173804epfm)。
- 如果您通过控制台调用函数，请勿在函数未执行完成前单击**取消请求**手动取消或关闭网页。

### 函数执行时间不符合预期

程序执行的耗时一般包括以下两类。

- I/O操作
  
  I/O操作，尤其网络的I/O，是执行延时增大的主要原因。建议排查程序中所有访问外部服务的操作，可以在访问外部服务前后添加日志，确认耗时是否正常。
- 计算操作
  
  大量的计算操作也可能导致延时增加，建议调大CPU规格。
