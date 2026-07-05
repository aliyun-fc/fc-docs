# 错误处理

本文介绍C#运行环境发生错误信息时，函数计算如何处理 。

## 函数抛出异常

如果您的函数在执行过程中抛出异常，函数计算会捕获并返回异常信息。

示例代码如下。

```
using System; using System.IO; using System.Threading.Tasks; using Aliyun.Serverless.Core; using Microsoft.Extensions.Logging; namespace Example { public class Hello { public async void StreamHandler(Stream input, IFcContext context) { throw new Exception("oops"); } static void Main(string[] args){} } }
```

调用函数时收到的响应如下所示。

```
{ "errorMessage": "oops", "errorType": "System.Exception", "stackTrace": [...] }
```

发生异常时，函数调用相应的HTTP Header中会包含X-Fc-Error-Type`UnhandledInvocationError`。关于函数计算错误类型的更多信息，请参见[基础信息](https://help.aliyun.com/zh/functioncompute/fc/basics#section-cgk-2tl-g4v)。

## 函数主动退出

通过主动退出运行中的函数获取错误信息时，无法获取退出时的报错信息和堆栈信息。不推荐使用该方法。

示例代码如下。

```
using System; using System.IO; using System.Threading.Tasks; using Aliyun.Serverless.Core; using Microsoft.Extensions.Logging; namespace Example { public class Hello { public async void StreamHandler(Stream input, IFcContext context) { System.Environment.Exit(1); } static void Main(string[] args){} } }
```

调用函数时收到的响应如下所示。

```
{ "errorMessage": "Process exited unexpectedly before completing request (duration: 45ms, maxMemoryUsage: 49MB)" }
```
