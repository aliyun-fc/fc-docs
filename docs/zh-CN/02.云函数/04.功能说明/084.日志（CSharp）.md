# 日志

本文介绍如何在.NET运行环境下打印日志和查看日志。

## 打印日志

函数向标准输出stdout或标准错误stderr打印的内容会被收集到创建服务时指定的Logstore中。您可以使用[fc-dotnet-lib](https://github.com/aliyun/fc-dotnet-libs)库提供的`context.Logger`方法打印日志，也可以使用其他日志库打印日志。

**

**说明**

推荐您使用`context.Logger`方法打印日志，使用该方法打印的日志自动包含RequestId，便于在出现错误的时候定位问题日志。

### 使用context.Logger打印日志

使用该方法打印的每条日志中都包含时间、RequestId和日志级别等信息。示例代码如下所示。

```
using System.IO; using System.Threading.Tasks; using Aliyun.Serverless.Core; using Microsoft.Extensions.Logging; namespace Example { public class Hello { public async Task<Stream> StreamHandler(Stream input, IFcContext context) { IFcLogger logger = context.Logger; logger.LogInformation("Handle request: {0}", context.RequestId); logger.LogInformation(string.Format("detail = {0} ", "hello world")); MemoryStream copy = new MemoryStream(); await input.CopyToAsync(copy); copy.Seek(0, SeekOrigin.Begin); return copy; } static void Main(string[] args){} } }
```

执行上面的示例代码，输出的日志内容如下。

```
2022-10-09T07:20:31.024Z 9666a77e-65e7-42a9-b011-************ [INFO] detail = hello world
```

### 改变日志级别

您可以通过改变Logger的Property`EnabledLogLevel`改变日志级别，日志级别从高到低排列如下。

| **日志级别** | **Level** | **接口** |
| --- | --- | --- |
| Critical | 5 | `context.Logger.LogCritical` |
| Error | 4 | `context.Logger.LogError` |
| Warning | 3 | `context.Logger.LogWarning` |
| Information | 2 | `context.Logger.LogInformation` |
| Debug | 1 | `context.Logger.LogDebug` |
| Trace | 0 | `context.Logger.LogTrace` |

关于日志级别的更多信息， 请参见[LogLevel Enum](https://docs.microsoft.com/en-us/dotnet/api/microsoft.extensions.logging.loglevel?view=aspnetcore-2.1)。

示例代码如下所示。

```
using System.IO; using System.Threading.Tasks; using Aliyun.Serverless.Core; using Microsoft.Extensions.Logging; namespace Example { public class Hello { public async Task<Stream> StreamHandler(Stream input, IFcContext context) { IFcLogger logger = context.Logger; // 打印大于Error级别的日志信息 logger.EnabledLogLevel = LogLevel.Error; logger.LogError("console error 1"); logger.LogInformation("console info 1"); logger.LogWarning("console warn 1"); logger.LogDebug("console debug 1"); // 打印大于Warning级别的日志信息 logger.EnabledLogLevel = LogLevel.Warning; logger.LogError("console error 2"); logger.LogInformation("console info 2"); logger.LogWarning("console warn 2"); logger.LogDebug("console debug 2"); // 打印大于Information级别的日志信息 logger.EnabledLogLevel = LogLevel.Information; logger.LogInformation("Handle request: {0}", context.RequestId); MemoryStream copy = new MemoryStream(); await input.CopyToAsync(copy); copy.Seek(0, SeekOrigin.Begin); return copy; } static void Main(string[] args){} } }
```

执行以上代码输出的日志内容如下所示。

```
2022-10-09T07:31:42.644Z 77b8ed17-6760-4877-8a43-b79189****** [ERROR] console error 1 2022-10-09T07:31:42.644Z 77b8ed17-6760-4877-8a43-b79189****** [ERROR] console error 2 2022-10-09T07:31:42.644Z 77b8ed17-6760-4877-8a43-b79189****** [WARNING] console warn 2 2022-10-09T07:31:42.644Z 77b8ed17-6760-4877-8a43-b79189****** [INFO] Handle request: 77b8ed17-6760-4877-8a43-b79189******
```

## 查看日志

函数执行完成后，您可以在函数详情页的**调用日志**页签查看日志信息。具体操作和说明，请参见[查看调用日志](https://help.aliyun.com/zh/functioncompute/fc/configure-the-logging-feature#section-z06-gdf-7c9)。
