# 上下文

本文介绍在函数计算中使用Go运行时开发代码时，所涉及的Context（上下文）的相关概念和使用示例。

## 什么是上下文

当函数计算运行您的函数时，它会将上下文对象（`context.Context`）传递到执行方法中。该对象包含有关调用、服务、函数、链路追踪和执行环境等信息。

上下文对象主要提供了以下参数。

| **字段** | **说明** |
| --- | --- |
| **变量** |  |
| RequestID | 本次调用请求的唯一ID。您可以记录该ID，当函数调用出现问题时方便查询。 |
| Credentials | 为函数配置角色后，函数计算通过[AssumeRole](https://help.aliyun.com/zh/ram/developer-reference/api-sts-2015-04-01-assumerole#main-107864)API获取的一组临时密钥，其有效时间是36小时。您可以在代码中使用`Credentials`去访问相应的服务例如OSS，这就避免了您把自己的AccessKey信息编码在函数代码里。详细信息，请参见[授予函数计算访问其他云服务的权限](https://help.aliyun.com/zh/functioncompute/fc/grant-function-compute-permissions-to-access-other-alibaba-cloud-services)。 |
| Function | 当前调用的函数的一些基本信息，例如函数名、函数入口、函数内存和超时时间。 |
| Service | 当前调用的函数所在的服务信息，包含接入的日志服务SLS的Project和Logstore信息，以及版本和别名信息。其中`qualifier`表示调用函数时指定的服务版本或别名，`versionId`表示实际调用的服务版本。 |
| Region | 当前调用的函数所在地域ID，例如在华东2（上海）地域调用，则地域ID为cn-shanghai。详细信息，请参见[服务接入地址](https://help.aliyun.com/zh/functioncompute/fc/developer-reference/fc-endpoints)。 |
| AccountId | 函数所属的阿里云账号ID（主账号ID）。 |
| **方法** |  |
| deadline | 返回函数执行的超时时间，格式为Unix时间戳，单位：毫秒。 |

完整的数据结构，请参见[context.go](https://github.com/aliyun/fc-runtime-go-sdk/blob/master/fccontext/context.go)。

## 使用示例

### 示例一：打印Context信息

首先，函数的`handler`需要包含`context`参数，函数计算会把[Context信息](#table-jd3-48n-lex)中的变量信息插入到`context`的取值中。然后，需要`import aliyun/fc-runtime-go-sdk/fccontext`，通过`fccontext.FromContext`方法获取`fccontext`。

```
package main import ( "context" "encoding/json" "log" "github.com/aliyun/fc-runtime-go-sdk/fc" "github.com/aliyun/fc-runtime-go-sdk/fccontext" ) func main() { fc.Start(echoContext) } func echoContext(ctx context.Context) (string, error) { fctx, _ := fccontext.FromContext(ctx) log.Println(fctx.AccountId) log.Printf("%#v\n", fctx) res, _ := json.Marshal(fctx) return string(res), nil }
```

### 示例二：获取函数剩余执行时间

以下示例展示了如何使用`deadline`获取函数剩余执行时间。

```
package main import ( "context" "fmt" "log" "time" "github.com/aliyun/fc-runtime-go-sdk/fc" ) func LongRunningHandler(ctx context.Context) (string, error) { deadline, _ := ctx.Deadline() fmt.Printf("now: %s\ndeadline: %s\n", time.Now().String(), deadline.String()) deadline = deadline.Add(-100 * time.Millisecond) timeoutChannel := time.After(time.Until(deadline)) for { select { case <-timeoutChannel: return "Finished before timing out.", nil default: log.Print("hello!") time.Sleep(50 * time.Millisecond) } } } func main() { fc.Start(LongRunningHandler) }
```
