# 自定义运行时启动的服务中调用第三方服务时，出现FunctionNotStarted错误怎么办？

您需要查看该第三方服务是否有网络限制，如果存在网络限制或网络超时的情况，则会导致没有完成启动HTTP Server的逻辑，出现如下异常。

```
{ "ErrorCode":"FunctionNotStarted", "ErrorMessage":"The CA's http server cannot be started:ContainerStartDuration:25000000000. Ping CA failed due to: dial tcp 21.0.X.X:9000: getsockopt: connection refused"}
```
