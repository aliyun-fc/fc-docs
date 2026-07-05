# 错误处理

本文介绍PHP运行环境的错误处理。

PHP函数在执行过程中发生异常时，函数计算捕获异常并返回异常信息。以下示例代码返回了`oops`的异常信息。

```
<?php function handler($event, $context) { throw new Exception("oops"); }
```

根据以上示例代码，您调用函数时可能会收到以下响应信息。

```
{ "errorMessage":"oops", "errorType":"Exception", "stackTrace":{ "file":"/code/index.php", "line":3, "traceString":"" } }
```

发生异常时，函数调用的响应的HTTP header中会包含X-Fc-Error-Type: UnhandledInvocationError。关于函数计算错误类型的更多信息，请参见[基础信息](https://help.aliyun.com/zh/functioncompute/fc/basics#section-cgk-2tl-g4v)。
