# 错误处理

本文介绍Go运行环境的错误处理相关内容。

发生异常时，函数调用响应的HTTP Header中会包含`X-Fc-Error-Type`，例如`X-Fc-Error-Type: UnhandledInvocationError`。函数计算的错误类型的更多信息，请参见[基础信息](https://help.aliyun.com/zh/functioncompute/fc/basics#section-cgk-2tl-g4v)。

函数计算返回错误信息的方式如下。

- 在入口函数直接返回错误信息，示例如下。
  
  ```
  package main import ( "errors" "fmt" "github.com/aliyun/fc-runtime-go-sdk/fc" ) func HandleRequest() error { fmt.Println("hello world") return errors.New("something is wrong") } func main() { fc.Start(HandleRequest) }
  ```
  
  调用函数时收到的响应如下所示。
  
  ```
  { "errorMessage": "something is wrong!", "errorType": "errorString" }
  ```
- 使用panic抛出错误信息，示例如下。
  
  ```
  package main import ( "fmt" "github.com/aliyun/fc-runtime-go-sdk/fc" ) func HandleRequest() error { fmt.Println("hello world") panic("Error: something is wrong") return nil } func main() { fc.Start(HandleRequest) }
  ```
  
  调用函数时收到的响应如下所示（示例中省略了部分堆栈信息）。
  
  ```
  { errorMessage: 'Error: something is wrong', errorType: 'string', stackTrace: [ { path: 'github.com/aliyun/fc-runtime-go-sdk/fc/errors.go', line: 39, label: 'fcPanicResponse' }, { path: 'github.com/aliyun/fc-runtime-go-sdk/fc/function.go', line: 84, label: '(*Function).Invoke.func1' }, ... ... ... { path: 'code/main.go', line: 22, label: 'main' }, { path: 'runtime/proc.go', line: 255, label: 'main' }, { path: 'runtime/asm_amd64.s', line: 1581, label: 'goexit' } ] }
  ```
- 建议不要使用包含`os.Exit(1)`代码的错误处理代码，例如`log.Fatal`。
  
  **
  
  **重要**
  
  使用该方法无法获取退出时的报错信息和堆栈信息。
  
  ```
  package main import ( "fmt" "log" "github.com/aliyun/fc-runtime-go-sdk/fc" ) func HandleRequest() error { fmt.Println("hello world") log.Fatal("something is wrong") return nil } func main() { fc.Start(HandleRequest) }
  ```
  
  调用函数时收到的响应如下所示。
  
  ```
  { errorMessage: 'Process exited unexpectedly before completing request (duration: 0ms, maxMemoryUsage: 8MB)' }
  ```
