# 请求处理程序（Handler）

您可以使用C#请求处理程序响应接收到的事件并执行相应的业务逻辑。本文介绍C#请求处理程序的相关概念、结构特点和示例。

**

**说明**

如您需要通过HTTP触发器或自定义域名访问函数，请先获取请求结构体再自定义HTTP响应。更多信息，请参见[HTTP触发器调用函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/http-trigger-invoking-function)。

## 什么是请求处理程序

FC函数的请求处理程序，是函数代码中处理请求的方法。当您的FC函数被调用时，函数计算会运行您提供的Handler方法处理请求。

您可以通过[函数计算控制台](https://fcnext.console.aliyun.com)，在创建或更新函数时为函数配置请求处理程序。具体操作，请参见[创建事件函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/creating-an-event-function#45e9ee65bd8n7)。

对于C#语言的FC函数，其请求处理程序的格式为`程序集名称::命名空间.类名::方法名`（`Assembly::Namespace.ClassName::MethodName`）。

| **参数** | **说明** |
| --- | --- |
| Assembly | 创建的程序集的名称。 |
| Namespace | 命名空间名称。 |
| ClassName | 类名。 |
| MethodName | 方法名。 |

假设程序集名称为`HelloFcApp`，则请求处理程序的配置为`HelloFcApp::Example.HelloFC::StreamHandler`。一个简单的程序示例如下。

```
using System.IO; namespace Example { public class HelloFC { public async Task<Stream> StreamHandler(Stream input) { //function logic } } }
```

请求处理程序的具体配置均需符合函数计算平台的配置规范。配置规范因请求处理程序类型而异。

## 处理程序接口

当您创建一个基于C#的函数时，需要指定一个Handler方法，该方法在函数执行时被执行。这个Handler方法可以是Static方法或Instance方法。如果您想在Handler方法中访问`IFcContext`对象，则需要将该方法中的第二个参数指定为`IFcContext`对象。事件函数支持的Handler方法定义如下所示。

```
ReturnType HandlerName(InputType input, IFcContext context); //包含IFcContext。 ReturnType HandlerName(InputType input); // 不包含IFcContext。 Async Task<ReturnType> HandlerName(InputType input, IFcContext context); Async Task<ReturnType> HandlerName(InputType input);
```

函数计算支持在使用C#编写的函数中应用Async，此时函数的执行会等待异步方法执行结束。以下是对ReturnType、InputType和IFcContext的说明。

- ReturnType：返回对象可以是`void`、`System.IO.Stream`对象或者任何可以被JSON序列化和反序列化的对象。如果返回对象是Stream，该Stream内容将直接在响应体返回，否则返回对象被JSON序列化后，在响应体返回。
- InputType：输入参数可以是System.IO.Stream或任何可以被JSON序列化和反序列化的对象。
- IFcContext：函数的Context对象。更多信息，请参见[上下文](https://help.aliyun.com/zh/functioncompute/fc/context-4)。

## 事件请求处理程序类型

函数计算使用C#编写函数，需要引入`Aliyun.Serverless.Core`依赖包，可以通过以下方式，在.csproj文件中引入该依赖包。

```
<ItemGroup> <PackageReference Include="Aliyun.Serverless.Core" Version="1.0.1" /> </ItemGroup>
```

`Aliyun.Serverless.Core`包为事件请求处理程序定义了两个参数类型。

- Stream Handler
  
  以流的方式接收输入的`event`事件并返回执行结果，您需要从输入流中读取调用函数时的输入，处理完成后把函数执行结果写入到输出流中来返回。
- POCO Handler
  
  通过POCO（Plain old CLR objects）方式，您可以自定义输入和输出的类型，但是输入和输出的类型必须是POCO类型。

### Stream Handler

一个最简单的Stream Handler示例如下所示。

```
using System.IO; using System.Threading.Tasks; using Aliyun.Serverless.Core; using Microsoft.Extensions.Logging; namespace Example { public class Hello { public async Task<Stream> StreamHandler(Stream input, IFcContext context) { IFcLogger logger = context.Logger; logger.LogInformation("Handle request: {0}", context.RequestId); MemoryStream copy = new MemoryStream(); await input.CopyToAsync(copy); copy.Seek(0, SeekOrigin.Begin); return copy; } static void Main(string[] args){} } }
```

示例解析如下。

- 命名空间和类
  
  命名空间为`Example`，类名为`Hello`，方法名为`StreamHandler`，假设程序集名称为`HelloFcApp`，则请求处理程序的配置为`HelloFcApp::Example.Hello::StreamHandler`。
- 参数Stream input
  
  处理程序的输入，该示例的输入类型为Stream。
- 参数IFcContext context（可选）
  
  上下文对象，包含函数和请求的信息。
- 返回值Task<Stream>
  
  返回值为Stream类型。

### POCO Handler

一个最简单的POCO Handler示例如下所示。

```
using Aliyun.Serverless.Core; using Microsoft.Extensions.Logging; namespace Example { public class Hello { public class Product { public string Id { get; set; } public string Description { get; set; } } // optional serializer class, if it’s not specified, the default serializer (based on JSON.Net) will be used. // [FcSerializer(typeof(MySerialization))] public Product PocoHandler(Product product, IFcContext context) { string Id = product.Id; string Description = product.Description; context.Logger.LogInformation("Id {0}, Description {1}", Id, Description); return product; } static void Main(string[] args){} } }
```

除了Stream作为输入输出参数，POCO（Plain old CLR objects）对象同样也可以作为输入和输出。如果该POCO没有指定特定的JSON序列化对象，则函数计算默认使用JSON.Net进行对象的JSON序列化和反序列化。具体解析如下。

- 命名空间和类
  
  命名空间为`Example`，类名为`Hello`，方法名为`PocoHandler`，假设程序集名称为`HelloFcApp`, 则请求处理程序的配置为`HelloFcApp::Example.Hello::PocoHandler`。
- 参数`Product product`
  
  处理程序的输入，该示例的输入类型为`Product Class`。如果该POCO没有指定特定的JSON序列化对象，则函数计算默认使用JSON.Net进行对象的JSON反序列化。
- 参数IFcContext context（可选）
  
  上下文对象，包含函数和请求的信息。
- 返回值`Product`
  
  返回值为`POCO Product`类型。如果该POCO没有指定特定的JSON序列化对象，则函数计算默认使用JSON.Net进行对象的JSON序列化。

### 自定义序列化接口（Custom Serializer）

函数计算针对POCO Handler提供了默认的基于[JSON .NET](https://www.newtonsoft.com/json)的序列化接口。如果默认的序列化接口不能满足需求，您可以基于`Aliyun.Serverless.Core`中的接口`IFcSerializer`实现自定义序列化接口。

```
public interface IFcSerializer { T Deserialize<T>(Stream requestStream); void Serialize<T>(T response, Stream responseStream); }
```

## **使用HTTP触发器调用函数**

### **示例代码**

```
using System; using System.Collections.Generic; using System.Text; using System.Text.Json; using Aliyun.Serverless.Core; using Microsoft.Extensions.Logging; namespace Example { public class Hello { public class HTTPTriggerEvent { public string Version { get; set; } public string RawPath { get; set; } public string Body { get; set; } public bool IsBase64Encoded { get; set; } public RequestContext RequestContext { get; set; } public Dictionary<string, string> Headers { get; set; } public Dictionary<string, string> QueryParameters { get; set; } public override string ToString() { return JsonSerializer.Serialize(this); } } public class RequestContext { public string AccountId { get; set; } public string DomainName { get; set; } public string DomainPrefix { get; set; } public string RequestId { get; set; } public string Time { get; set; } public string TimeEpoch { get; set; } public Dictionary<string, string> Http { get; set; } } public class HTTPTriggerResponse { public int StatusCode { get; set; } public Dictionary<string, string> Headers { get; set; } public bool IsBase64Encoded { get; set; } public string Body { get; set; } } public HTTPTriggerResponse PocoHandler(HTTPTriggerEvent input, IFcContext context) { context.Logger.LogInformation("receive event: {0}", input.ToString()); string requestBody = input.Body; if (input.IsBase64Encoded) { byte[] decodedBytes = Convert.FromBase64String(input.Body); requestBody = Encoding.UTF8.GetString(decodedBytes); } return new HTTPTriggerResponse { StatusCode = 200, IsBase64Encoded = false, Body = requestBody }; } static void Main(string[] args){} } }
```

### **前提条件**

已使用上述示例创建运行环境为C#的函数。具体操作，请参见[创建事件函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/creating-an-event-function#45e9ee65bd8n7)和[配置HTTP触发器](https://help.aliyun.com/zh/functioncompute/fc/configure-an-http-trigger-for-a-function-and-invoke-the-function-by-using-http-requests#title-w29-ied-xjp)。

### **操作步骤**

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com)，在左侧导航栏，选择**函数管理**>**函数列表**。
2. 在顶部菜单栏，选择地域，然后在**函数列表**页面，单击目标函数。
3. 在函数详情页面，单击**触发器**页签，在触发器页面获取HTTP触发器的公网访问地址。
4. 在Curl工具执行以下命令，调用函数。
  
  ```
  curl -i "https://test-python-ipgrwr****.cn-shanghai.fcapp.run" -d 'Hello fc3.0'
  ```
  
  以上命令中，`https://test-python-ipgrwr****.cn-shanghai.fcapp.run`为获取到的HTTP触发器公网访问地址。
  
  **
  
  **重要**
  
  - 如果HTTP触发器的**认证方式**为**无需认证**，您可以直接使用Postman或Curl工具来调用函数。具体操作，请参见本文[操作步骤](https://help.aliyun.com/zh/functioncompute/fc/handlers-in-a-java-runtime#3d0f4d2067xye)。
  - 如果HTTP触发器的**认证方式**为**签名认证**、**JWT认证**或**Bearer认证**，请使用签名方式、JWT认证或Bearer认证方式来调用函数。具体操作，请参见[认证鉴权](https://help.aliyun.com/zh/functioncompute/fc/user-guide/http-triggers-overview#section-h0d-vmz-zpn)。
  
  响应结果如下。
  
  ```
  HTTP/1.1 200 OK Content-Disposition: attachment Content-Length: 12 Content-Type: application/json X-Fc-Request-Id: 1-64f7449a-127fbe39cd7681596e33ebad Date: Tue, 05 Sep 2023 15:09:14 GMT Hello fc3.0
  ```

### **错误分析**

本示例代码支持使用HTTP触发器或者自定义域名调用。如果使用API调用，但配置的测试参数不符合HTTP触发器请求格式规范时，会出现报错。

例如，在控制台上调用函数，配置请求参数为`"Hello, FC!"`，单击**测试函数**，收到的响应如下所示。

```
{ "errorMessage": "Unexpected character encountered while parsing value: H. Path '', line 0, position 0.", "errorType": "Newtonsoft.Json.JsonReaderException", "stackTrace": [ " at Newtonsoft.Json.JsonTextReader.ParseValue()", " at Newtonsoft.Json.JsonReader.ReadAndMoveToContent()", " at Newtonsoft.Json.JsonReader.ReadForType(JsonContract contract, Boolean hasConverter)", " at Newtonsoft.Json.Serialization.JsonSerializerInternalReader.Deserialize(JsonReader reader, Type objectType, Boolean checkAdditionalContent)", " at Newtonsoft.Json.JsonSerializer.DeserializeInternal(JsonReader reader, Type objectType)", " at Newtonsoft.Json.JsonSerializer.Deserialize(JsonReader reader, Type objectType)", " at Newtonsoft.Json.JsonSerializer.Deserialize[T](JsonReader reader)", " at Aliyun.Serverless.Core.JsonSerializer.Deserialize[T](Stream requestStream) in /dotnetcore/Libraries/src/Aliyun.Serverless.Core.Impl/JsonSerializer.cs:line 95" ] }
```

## 示例程序

函数计算官方库包含使用各种处理程序类型和接口的示例应用程序。每个示例应用程序都包含用于轻松编译部署的方法。

- [dotnet3-blank-stream-event](https://github.com/awesome-fc/code-example/tree/master/dotnet/dotnet3-blank-stream-event)：使用Stream格式的事件回调处理程序。
- [dotnet3-blank-poco-event](https://github.com/awesome-fc/code-example/tree/master/dotnet/dotnet3-blank-poco-event)：使用POCO格式的事件回调处理程序。
