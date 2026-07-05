# 错误处理

本文介绍Python运行环境的错误处理相关内容。

如果函数在执行过程中抛出异常，那么函数计算会捕获并返回异常信息，示例如下所示。

```
def my_handler(event, context): raise Exception('something is wrong')
```

发送异常时，函数调用响应的HTTP Header中会包含`X-Fc-Error-Type: UnhandledInvocationError`，HTTP请求体（Body）包含如下信息。函数计算的错误类型的更多信息，请参见[错误处理](https://help.aliyun.com/zh/functioncompute/fc-2-0/user-guide/error-handling#task-2134831)。

```
{ "errorMessage": "something is wrong", "errorType": "Exception", "stackTrace": [ [ "File \"/code/index.py\"", "line 2", "in my_handler", "raise Exception('something is wrong')" ] ] }
```

异常信息包含如下三个字段：

| **字段** | **类型** | **解释说明** |
| --- | --- | --- |
| errorMessage | String | 异常信息。 |
| errorType | String | 异常类型。 |
| stackTrace | List | 异常堆栈。 |
