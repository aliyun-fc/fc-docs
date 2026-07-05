# 自定义运行时的监听端口一定要和HTTP Server的监听端口一致吗？

是的。自定义运行时的监听端口（CAPort）默认是9000。如果自定义运行时使用默认的监听端口，那么您实现的自定义运行时的HTTP Server监听的端口也必须是9000。 如果自定义运行时使用的监听端口是8080，那么您实现的自定义运行时的HTTP Server监听的端口也必须是8080。

自定义运行时启动的HTTP Server一定要监听`0.0.0.0:CAPort`或`*:CAPort`端口。如果您使用`127.0.0.1:CAPort`端口，会导致请求超时，出现以下错误：

```
{ "ErrorCode":"FunctionNotStarted", "ErrorMessage":"TheCA'shttpservercannotbestarted:ContainerStartDuration:25000000000.PingCAfaileddueto:dialtcp21.0.5.7:9000:getsockopt:connectionrefusedLogs:2019-11-29T09:53:30.859837462ZListeningonport9000" }
```
