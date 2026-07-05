# 请求处理程序（Handler）

您可以使用Go请求处理程序响应接收到的事件并执行相应的业务逻辑。本文介绍Go请求处理程序的相关概念、结构特点和使用示例。

**

**说明**

如您需要通过HTTP触发器或自定义域名访问函数，请先获取请求结构体再自定义HTTP响应。更多信息，请参见[HTTP触发器调用函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/http-trigger-invoking-function)。

## 什么是请求处理程序

FC函数的请求处理程序，是函数代码中处理请求的方法。当您的FC函数被调用时，函数计算会运行您提供的Handler方法处理请求。您可以通过[函数计算控制台](https://fcnext.console.aliyun.com)的**函数入口**配置Handler。

对Go语言的FC函数而言，您的请求处理程序被编译为一个可执行的二进制文件。您只需要将FC函数的请求处理程序配置项设置为该可执行文件的文件名即可。

关于FC函数的具体定义和相关操作，请参见[创建事件函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/creating-an-event-function#45e9ee65bd8n7)。

请求处理程序的具体配置均需符合函数计算平台的配置规范。配置规范因请求处理程序类型而异。

## 使用示例

在Go语言的代码中，您需要引入官方的SDK库`aliyun/serverless/fc-runtime-go-sdk/fc`，并实现`handler`函数和`main`函数。示例如下。

```
package main import ( "fmt" "context" "github.com/aliyun/fc-runtime-go-sdk/fc" ) type StructEvent struct { Key string `json:"key"` } func HandleRequest(ctx context.Context, event StructEvent) (string, error) { return fmt.Sprintf("hello, %s!", event.Key), nil } func main() { fc.Start(HandleRequest) }
```

传入的`event`参数是一个包含`key`属性的JSON字符串，示例如下。

```
{ "key": "value" }
```

具体的示例解析如下：

- `package main`：在Go语言中，Go应用程序都包含一个名为`main`的包。
- `import`：需要引用函数计算依赖的包，主要包括以下包：
  
  - `github.com/aliyun/fc-runtime-go-sdk/fc`：函数计算Go语言的核心库。
  - `context`：函数计算Go语言的Context对象。
- `func HandleRequest(ctx context.Context, event StructEvent) (string, error)`：处理请求的方法（即Handler），需包含将要执行的代码，参数含义如下：
  
  - `ctx context.Context`：为您的FC函数调用提供在调用时的运行上下文信息。更多信息，请参见[上下文](https://help.aliyun.com/zh/functioncompute/fc/user-guide/context-5)。
  - `event StructEvent`：调用函数时传入的数据，可以支持多种类型。
  - `string, error`：返回两个值，字符串和错误信息。更多信息，请参见[错误处理](https://help.aliyun.com/zh/functioncompute/fc/user-guide/error-handling-4-1)。
  - `return fmt.Sprintf("Hi，%s !", event.Key), nil`：简单地返回`hello`信息，其中包含传入的`event`。`nil`表示没有报错。
- `func main()`：运行FC函数代码的入口点，Go程序必须包含`main`函数。通过添加代码`fc.Start(HandleRequest)`，您的程序即可运行在阿里云函数计算平台。

## Event Handler签名

下面列举出了有效的Event Handler签名，其中`InputType`和`OutputType`与`encoding/json`标准库兼容。

函数计算会使用`json.Unmarshal`方法对传入的`InputType`进行反序列化，以及使用`json.Marshal`方法对返回的`OutputType`进行序列化。关于如何反序列化函数的返回数据，请参考[JSON Unmarshal](https://pkg.go.dev/encoding/json#Unmarshal)。

- `func ()`
- `func () error`
- `func (InputType) error`
- `func () (OutputType, error)`
- `func (InputType) (OutputType, error)`
- `func (context.Context) error`
- `func (context.Context, InputType) error`
- `func (context.Context) (OutputType, error)`
- `func (context.Context, InputType) (OutputType, error)`

Handler的使用需遵循以下规则：

- Handler必须是一个函数。
- Handler支持0～2个输入参数。如果有2个参数，则第一个参数必须是`context.Context`。
- Handler支持0～2个返回值。如果有1个返回值，则必须是`error`类型；如果有2个返回值，则第2个返回值必须是`error`。

函数的Handler示例代码：

- [event-struct.go](https://github.com/aliyun/fc-runtime-go-sdk/blob/master/examples/event-struct.go)：`event`为Struct类型的示例代码。
- [event-string.go](https://github.com/aliyun/fc-runtime-go-sdk/blob/master/examples/event-string.go)：`event`为String类型的示例代码。
- [event-map.go](https://github.com/aliyun/fc-runtime-go-sdk/blob/master/examples/event-map.go)：`event`为`map[string]interface{}`类型的示例代码。

更多Handler示例，请参见[examples](https://github.com/aliyun/fc-runtime-go-sdk/tree/master/examples)。

## Context

Context的详细使用方法，请参见[上下文](https://help.aliyun.com/zh/functioncompute/fc/user-guide/context-5)。

## **使用HTTP触发器调用函数**

### **示例代码**

```
package main import ( "encoding/base64" "encoding/json" "fmt" "net/http" "github.com/aliyun/fc-runtime-go-sdk/events" "github.com/aliyun/fc-runtime-go-sdk/fc" ) type HTTPTriggerEvent events.HTTPTriggerEvent type HTTPTriggerResponse events.HTTPTriggerResponse func (h HTTPTriggerEvent) String() string { jsonBytes, err := json.MarshalIndent(h, "", " ") if err != nil { return "" } return string(jsonBytes) } func NewHTTPTriggerResponse(statusCode int) *HTTPTriggerResponse { return &HTTPTriggerResponse{StatusCode: statusCode} } func (h *HTTPTriggerResponse) String() string { jsonBytes, err := json.MarshalIndent(h, "", " ") if err != nil { return "" } return string(jsonBytes) } func (h *HTTPTriggerResponse) WithStatusCode(statusCode int) *HTTPTriggerResponse { h.StatusCode = statusCode return h } func (h *HTTPTriggerResponse) WithHeaders(headers map[string]string) *HTTPTriggerResponse { h.Headers = headers return h } func (h *HTTPTriggerResponse) WithIsBase64Encoded(isBase64Encoded bool) *HTTPTriggerResponse { h.IsBase64Encoded = isBase64Encoded return h } func (h *HTTPTriggerResponse) WithBody(body string) *HTTPTriggerResponse { h.Body = body return h } func HandleRequest(event HTTPTriggerEvent) (*HTTPTriggerResponse, error) { fmt.Printf("event: %v\n", event) if event.Body == nil { return NewHTTPTriggerResponse(http.StatusBadRequest). WithBody(fmt.Sprintf("the request did not come from an HTTP Trigger, event: %v", event)), nil } reqBody := *event.Body if event.IsBase64Encoded != nil && *event.IsBase64Encoded { decodedByte, err := base64.StdEncoding.DecodeString(*event.Body) if err != nil { return NewHTTPTriggerResponse(http.StatusBadRequest). WithBody(fmt.Sprintf("HTTP Trigger body is not base64 encoded, err: %v", err)), nil } reqBody = string(decodedByte) } return NewHTTPTriggerResponse(http.StatusOK).WithBody(reqBody), nil } func main() { fc.Start(HandleRequest) }
```

上述示例从SDK中引入了HTTP触发器的请求结构HTTPTriggerEvent，以及响应结构HTTPTriggerResponse。关于HTTP触发调用的请求负载格式和响应负载格式，请参见[HTTP触发器调用函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/http-trigger-invoking-function)。

### **前提条件**

已使用上述示例创建运行环境为Go的函数，并创建HTTP触发器。具体操作，请参见[创建事件函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/creating-an-event-function#45e9ee65bd8n7)和[配置HTTP触发器](https://help.aliyun.com/zh/functioncompute/fc/configure-an-http-trigger-for-a-function-and-invoke-the-function-by-using-http-requests#title-w29-ied-xjp)。

### **操作步骤**

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com)，在左侧导航栏，选择**函数管理**>**函数列表**。
2. 在顶部菜单栏，选择地域，然后在**函数列表**页面，单击目标函数。
3. 在函数详情页面，单击**触发器**页签，在触发器页面获取HTTP触发器的公网访问地址。
4. 执行以下命令调用函数。
  
  ```
  curl -i "https://http-trigger-demo.cn-shanghai.fcapp.run" -d "Hello FC!"
  ```
  
  **
  
  **重要**
  
  - 如果HTTP触发器的**认证方式**为**无需认证**，您可以直接使用Postman或Curl工具来调用函数。具体操作，请参见本文[操作步骤](#240398e78ahwd)。
  - 如果HTTP触发器的认证方式为**签名认证**、**JWT认证**或**Bearer认证**，请使用签名方式、JWT认证或Bearer认证方式来调用函数。具体操作，请参见[认证鉴权](https://help.aliyun.com/zh/functioncompute/fc/user-guide/http-triggers-overview#section-h0d-vmz-zpn)。

### **错误处理**

本示例代码支持使用HTTP Trigger触发器或者自定义域名调用，如果使用API调用，但配置的测试参数不符合HTTP Trigger请求格式规范，会出现报错。

例如，在控制台上调用，配置请求参数为`"Hello, FC!"`，点击**测试函数**按钮，会出现报错如下所示。

```
{ "statusCode": 400, "body": "the request did not come from an HTTP Trigger, event: {\n \"version\": null,\n \"rawPath\": null,\n \"headers\": null,\n \"queryParameters\": null,\n \"body\": null,\n \"isBase64Encoded\": null,\n \"requestContext\": null\n}" }
```

如果想获取原始的请求事件负载，可以使用下面示例中的Handler。

```
// GetRawRequestEvent: obtain the raw request event func GetRawRequestEvent(event []byte) (*HTTPTriggerResponse, error) { fmt.Printf("raw event: %s\n", string(event)) return NewHTTPTriggerResponse(http.StatusOK).WithBody(string(event)), nil } func main() { fc.Start(GetRawRequestEvent) }
```
