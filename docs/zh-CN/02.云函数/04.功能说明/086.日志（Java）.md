# 日志

本文介绍如何在Java运行环境下打印和查看日志。

## 打印日志

函数往标准输出stdout或标准错误stderr打印的内容会被收集到创建服务时指定的Logstore中，您可以使用[fc-java-core](https://github.com/aliyun/fc-java-libs/tree/master/fc-java-core)库提供的`context.getLogger`方法打印日志，也可以使用常见的日志库（如logback）打印日志。

**

**说明**

推荐您使用`context.getLogger`方法打印日志，使用该方法打印的日志自动包含RequestId，方便在出现错误的时候定位问题日志。

### **使用context.getLogger打印日志**

使用该方法打印的每条日志中都包含时间、RequestId和日志级别等信息。示例代码如下所示。

```
package example; import com.aliyun.fc.runtime.Context; import com.aliyun.fc.runtime.StreamRequestHandler; import java.io.IOException; import java.io.InputStream; import java.io.OutputStream; public class HelloFC implements StreamRequestHandler { @Override public void handleRequest(InputStream inputStream, OutputStream outputStream, Context context) throws IOException { context.getLogger().info("hello world"); outputStream.write(new String("hello world").getBytes()); } }
```

执行上面的示例代码输出的日志内容如下所示。

```
message:2017-07-05T05:13:35.920Z a72df088-f738-cee3-e0fe-323ad891**** [INFO] hello world
```

您也可以在代码中使用以下代码，打印不同级别的日志信息：

- `context.getLogger().trace`：打印TRACE级别的日志信息。
- `context.getLogger().debug`：打印DEBUG级别的日志信息。
- `context.getLogger().info`：打印INFO级别的日志信息。
- `context.getLogger().warn`：打印WARN级别的日志信息。
- `context.getLogger().error`：打印ERROR级别的日志信息。
- `context.getLogger().fatal`：打印FATAL级别的日志信息。

函数计算会记录每次调用的`FC Invoke Start`和`FC Invoke End`行，以及执行摘要信息，执行摘要的参数说明如下：

| **参数** | **说明** |
| --- | --- |
| Request ID | 调用的请求ID。 |
| 代码校验码 | 调用所使用代码包的校验码。 |
| 函数执行时间 | 处理程序实际运行所花费的时间。 |
| 函数计费时间 | 针对调用计费的时间量。 |
| 函数设置内存 | 分配给函数的内存量。 |
| 实际使用内存 | 函数实际使用的最大内存量。 |

## 查看日志

函数执行完成后，您可以在函数详情页的**日志**页签查看日志信息。具体操作和说明，请参见[查看调用日志](https://help.aliyun.com/zh/functioncompute/fc/configure-the-logging-feature#section-z06-gdf-7c9)。
