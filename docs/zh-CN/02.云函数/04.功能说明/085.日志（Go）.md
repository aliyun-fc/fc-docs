# 日志

本文介绍Go运行环境的日志打印相关内容。

## 打印日志

您可以使用`context.GetLogger()`方法打印日志，也可以使用log库或fmt库中的方法打印日志，或者其他写入到stdout或stderr的日志库打印日志。

### **使用context.GetLogger()方法打印日志**

使用该方法打印的每条日志中都包含日志级别、RequestId、时间、文件名和行号等信息，代码示例如下所示。

```
package main import ( "context" "github.com/aliyun/fc-runtime-go-sdk/fc" "github.com/aliyun/fc-runtime-go-sdk/fccontext" ) func HandleRequest(ctx context.Context) (string, error) { fctx, _ := fccontext.FromContext(ctx) fctx.GetLogger().Debug("this is Debug log") fctx.GetLogger().Debugf("Hi, %s\n", "this is Debugf log") fctx.GetLogger().Info("this is Info log") fctx.GetLogger().Infof("Hi, %s\n", "this is Infof log") fctx.GetLogger().Warn("this is Warn log") fctx.GetLogger().Warnf("Hi, %s\n", "this is Warnf log") fctx.GetLogger().Error("this is Error log") fctx.GetLogger().Errorf("Hi, %s\n", "this is Errorf log") return "Hello world", nil } func main() { fc.Start(HandleRequest) }
```

输出的日志内容如下所示。

```
FC Invoke Start RequestId: 1e9a87a5-fe0f-4904-a6f4-1d2728514129 2023-09-06T04:28:41.79Z d32c01bc-4397-4f52-a9ca-e374c28f96c1 [DEBUG] main.go:16: this is Debug log 2023-09-06T04:28:41.79Z d32c01bc-4397-4f52-a9ca-e374c28f96c1 [DEBUG] main.go:17: Hi, this is Debugf log 2023-09-06T04:28:41.79Z d32c01bc-4397-4f52-a9ca-e374c28f96c1 [INFO] main.go:19: this is Info log 2023-09-06T04:28:41.79Z d32c01bc-4397-4f52-a9ca-e374c28f96c1 [INFO] main.go:20: Hi, this is Infof log 2023-09-06T04:28:41.79Z d32c01bc-4397-4f52-a9ca-e374c28f96c1 [WARN] main.go:22: this is Warn log 2023-09-06T04:28:41.79Z d32c01bc-4397-4f52-a9ca-e374c28f96c1 [WARN] main.go:23: Hi, this is Warnf log 2023-09-06T04:28:41.791Z d32c01bc-4397-4f52-a9ca-e374c28f96c1 [ERROR] main.go:25: this is Error log 2023-09-06T04:28:41.791Z d32c01bc-4397-4f52-a9ca-e374c28f96c1 [ERROR] main.go:26: Hi, this is Errorf log FC Invoke End RequestId: 1e9a87a5-fe0f-4904-a6f4-1d2728514129
```

### **使用log库打印日志**

使用该方法打印的日志库包含日期和时间信息，代码示例如下所示。

```
package main import ( "log" "github.com/aliyun/fc-runtime-go-sdk/fc" ) func HandleRequest() (string, error) { log.Println("hello world") return "hello world", nil } func main() { fc.Start(HandleRequest) }
```

输出的日志内容如下所示。

```
FC Invoke Start RequestId: a15f8f85-9ed3-47c9-a61c-75678db61831 2022/02/17 04:29:02.228870 hello world FC Invoke End RequestId: a15f8f85-9ed3-47c9-a61c-75678db61831
```

### **执行摘要**

Go运行时会记录每次调用的Start和End行，以及执行摘要信息。执行摘要的参数说明如下。

| **参数** | **说明** |
| --- | --- |
| Request ID | 调用的唯一请求ID。 |
| 代码校验码 | 调用所使用代码包的校验码。 |
| 函数执行时间 | 处理程序实际运行所花费的时间。 |
| 函数计费时间 | 针对调用计费的时间量。 |
| 函数设置内存 | 分配给函数的内存量。 |
| 实际使用内存 | 函数实际使用的最大内存量。 |
