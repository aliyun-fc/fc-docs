# 请求处理程序（Handler）

您可以使用Java请求处理程序响应接收到的事件并执行相应的业务逻辑。本文介绍Java请求处理程序的相关概念、结构特点和示例。

**

**说明**

如您需要通过HTTP触发器或自定义域名访问函数，请先获取请求结构体再自定义HTTP响应。更多信息，请参见[HTTP触发器调用函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/http-trigger-invoking-function)。

## 什么是请求处理程序

FC函数的请求处理程序，是函数代码中处理请求的方法。当您的函数被调用时，函数计算会运行您提供的Handler方法处理请求。

您可以通过[函数计算控制台](https://fcnext.console.aliyun.com)配置**请求处理程序**，对于Java语言的函数，您的请求处理程序需配置为`[包名].[类名]::[方法名]`。例如，您的包名为example，类名为HelloFC，方法名为handleRequest，则请求处理程序可配置为`example.HelloFC::handleRequest`。

请求处理程序的具体配置均需符合函数计算平台的配置规范。配置规范因请求处理程序类型而异。

## 处理程序接口

您在使用Java编程时，必须要实现函数计算提供的接口类，[fc-java-core](https://github.com/aliyun/fc-java-libs/tree/master/fc-java-core)库为请求处理程序定义了以下两个接口。

- [StreamRequestHandler](#section-f71-r3j-0vu)
  
  以流的方式接收输入的`event`事件并返回执行结果。您需要从输入流中读取调用函数时的输入，处理完成后把函数执行结果写到输出流中来返回。
- [PojoRequestHandler](#section-llu-srm-3k2)
  
  以泛型的方式接收输入的`event`事件并返回执行结果。您可以自定义输入和输出的类型，但是输入和输出的类型必须是POJO类型。

## StreamRequestHandler

一个最简单的StreamRequestHandler示例如下所示。

```
package example; import com.aliyun.fc.runtime.Context; import com.aliyun.fc.runtime.StreamRequestHandler; import java.io.IOException; import java.io.InputStream; import java.io.OutputStream; public class HelloFC implements StreamRequestHandler { @Override public void handleRequest(InputStream inputStream, OutputStream outputStream, Context context) throws IOException { outputStream.write(new String("hello world").getBytes()); } }
```

- 包名和类名
  
  由于Java有包的概念，因此执行方法和其他语言有所不同，需要包含包的信息。代码示例中请求处理程序（handler）为`example.HelloFC::handleRequest`，其中`example`标识为包名，`HelloFC`标识为类名，`handleRequest`标识为类方法。
  
  **
  
  **说明**
  
  包名和类名可以是任意的，但是需要与函数配置信息中的**请求处理程序**字段相对应。关于**请求处理程序**的设置，请参见[创建事件函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/creating-an-event-function#45e9ee65bd8n7)。
- 实现的接口
  
  您的代码中必须要实现函数计算预定义的接口。上述的代码示例中实现了`StreamRequestHandler`，其中的inputStream参数为调用函数时传入的数据，outputStream参数用于返回函数的执行结果。
- Context参数
  
  Context参数中包含一些函数的运行时信息（例如RequestId、临时AccessKey等），其类型是`com.aliyun.fc.runtime.Context`。具体信息，请参见[上下文](https://help.aliyun.com/zh/functioncompute/fc/user-guide/context-3-1)。
- 返回值
  
  实现`StreamRequestHandler`接口的函数通过`outputStream`参数返回执行结果。
- 引入接口库
  
  其中用到的`com.aliyun.fc.runtime`包的依赖可以通过下文的`pom.xml`引用。
  
  ```
  <dependency> <groupId>com.aliyun.fc.runtime</groupId> <artifactId>fc-java-core</artifactId> <version>1.4.1</version> </dependency>
  ```
  
  您可以通过[Maven仓库](https://mvnrepository.com/artifact/com.aliyun.fc.runtime/fc-java-core)获取`fc-java-core`最新的版本号。

在创建函数之前，您需要将代码和其依赖的`fc-java-core`打包为JAR格式的压缩包。打包方式，请参见[编译部署代码包](https://help.aliyun.com/zh/functioncompute/fc/user-guide/compile-and-deploy-code-packages)。

## PojoRequestHandler

一个最简单的PojoRequestHandler示例如下所示。SimpleRequest的对象需要支持JSON序列化，例如POJO。

```
// HelloFC.java package example; import com.aliyun.fc.runtime.Context; import com.aliyun.fc.runtime.PojoRequestHandler; public class HelloFC implements PojoRequestHandler<SimpleRequest, SimpleResponse> { @Override public SimpleResponse handleRequest(SimpleRequest request, Context context) { String message = "Hello, " + request.getFirstName() + " " + request.getLastName(); return new SimpleResponse(message); } }
```

```
// SimpleRequest.java package example; public class SimpleRequest { String firstName; String lastName; public String getFirstName() { return firstName; } public void setFirstName(String firstName) { this.firstName = firstName; } public String getLastName() { return lastName; } public void setLastName(String lastName) { this.lastName = lastName; } public SimpleRequest() {} public SimpleRequest(String firstName, String lastName) { this.firstName = firstName; this.lastName = lastName; } }
```

```
// SimpleResponse.java package example; public class SimpleResponse { String message; public String getMessage() { return message; } public void setMessage(String message) { this.message = message; } public SimpleResponse() {} public SimpleResponse(String message) { this.message = message; } }
```

传入的event参数示例如下。

```
{ "firstName": "FC", "lastName": "aliyun" }
```

## **示例：使用HTTP触发器调用函数**

### **示例代码**

以上示例代码中，HTTPTriggerEvent.java声明了HTTP触发器的请求格式，HTTPTriggerResponse.java声明了HTTP触发器的响应格式，关于HTTP触发器的请求结构体和响应结构体的详细格式，请参见[HTTP触发器调用函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/http-trigger-invoking-function)。

HTTPTriggerEvent.java

```
package example; import lombok.AllArgsConstructor; import lombok.Builder; import lombok.Data; import lombok.NoArgsConstructor; import com.fasterxml.jackson.annotation.JsonProperty; import java.util.Map; @Data @NoArgsConstructor @AllArgsConstructor @Builder(setterPrefix = "with") public class HTTPTriggerEvent { private String version; private String rawPath; private Map<String, String> headers; private Map<String, String> queryParameters; private RequestContext requestContext; @JsonProperty("isBase64Encoded") private boolean IsBase64Encoded; private String body; @Data @NoArgsConstructor @AllArgsConstructor @Builder(setterPrefix = "with") public static class RequestContext { private String accountId; private String domainName; private String domainPrefix; private HttpInfo http; private String requestId; private String time; private String timeEpoch; @Data @NoArgsConstructor @AllArgsConstructor @Builder(setterPrefix = "with") public static class HttpInfo { private String method; private String path; private String protocol; private String sourceIp; private String userAgent; } } }
```

HTTPTriggerResponse.java

```
package example; import lombok.AllArgsConstructor; import lombok.Builder; import lombok.Data; import lombok.NoArgsConstructor; import java.util.Map; import com.fasterxml.jackson.annotation.JsonProperty; @Data @NoArgsConstructor @AllArgsConstructor @Builder(setterPrefix = "with") public class HTTPTriggerResponse { private int statusCode; private Map<String, String> headers; @JsonProperty("isBase64Encoded") private boolean IsBase64Encoded; private String body; }
```

App.java定义了函数入口类。

App.java

```
package example; import java.nio.charset.StandardCharsets; import java.util.HashMap; import java.util.Map; import com.aliyun.fc.runtime.Context; import com.aliyun.fc.runtime.PojoRequestHandler; /** * HTTP Trigger demo * */ public class App implements PojoRequestHandler<HTTPTriggerEvent, HTTPTriggerResponse> { @Override public HTTPTriggerResponse handleRequest(HTTPTriggerEvent request, Context context) { context.getLogger().info("Receive HTTP Trigger request: " + request.toString()); String requestBody = request.getBody(); if (request.isIsBase64Encoded()) { requestBody = new String(java.util.Base64.getDecoder().decode(request.getBody()), StandardCharsets.UTF_8); } String message = "HTTP Trigger request body: " + requestBody; context.getLogger().info(message); Map<String, String> headers = new HashMap<>(); headers.put("Content-Type", "text/plain"); return HTTPTriggerResponse.builder().withStatusCode(200).withHeaders(headers).withBody(request.getBody()) .withIsBase64Encoded(request.isIsBase64Encoded()).build(); } }
```

本示例程序除了引入[fc-java-core](https://github.com/aliyun/fc-java-libs/tree/master/fc-java-core)库外，还需要引入jackson和lombok两个库，可以在Maven的配置文件`pom.xml`中添加此依赖。

```
<dependency> <groupId>com.fasterxml.jackson.core</groupId> <artifactId>jackson-databind</artifactId> <version>2.16.1</version> </dependency> <dependency> <groupId>org.projectlombok</groupId> <artifactId>lombok</artifactId> <version>1.18.30</version> </dependency>
```

### **前提条件**

已使用上述示例创建运行环境为Java的函数，并创建HTTP触发器。具体操作，请参见[创建事件函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/creating-an-event-function#45e9ee65bd8n7)和[配置HTTP触发器](https://help.aliyun.com/zh/functioncompute/fc/configure-an-http-trigger-for-a-function-and-invoke-the-function-by-using-http-requests#title-w29-ied-xjp)。

### **操作步骤**

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com)，在左侧导航栏，选择**函数管理**>**函数列表**。
2. 在顶部菜单栏，选择地域，然后在**函数列表**页面，单击目标函数。
3. 在函数详情页面，单击**触发器**页签，在触发器页面获取HTTP触发器的公网访问地址。
4. 在Curl工具执行以下命令，调用函数。
  
  ```
  curl -i "https://dev-jav-test-fc-luiqas****.cn-shanghai.fcapp.run" -d 'hello fc3.0'
  ```
  
  以上命令中，`https://dev-jav-test-fc-luiqas****.cn-shanghai.fcapp.run`为获取到的HTTP触发器公网访问地址。
  
  响应结果如下。
  
  ```
  HTTP/1.1 200 OK Content-Disposition: attachment Content-Length: 11 Content-Type: application/json X-Fc-Request-Id: 1-652503f2-afbfd2b1dc4dd0fcb0230959 Date: Tue, 10 Oct 2023 07:57:38 GMT hello fc3.0%
  ```
  
  **
  
  **重要**
  
  - 如果HTTP触发器的**认证方式**为**无需认证**，您可以直接使用Postman或Curl工具来调用函数。具体操作，请参见本文[操作步骤](#3d0f4d2067xye)。
  - 如果HTTP触发器的**认证方式**为**签名认证**、**JWT认证**或**Bearer认证**，请使用签名方式、JWT认证或Bearer认证方式或来调用函数。具体操作，请参见[认证鉴权](https://help.aliyun.com/zh/functioncompute/fc/user-guide/http-triggers-overview#section-h0d-vmz-zpn)。

### **错误分析**

本示例代码支持使用HTTP触发器或者自定义域名调用。如果使用API调用，但配置的测试参数不符合HTTP触发器请求格式规范时，会出现报错。

例如，在控制台上调用函数，配置请求参数为`"Hello, FC!"`，单击**测试函数**，收到的响应如下所示。

```
{ "errorType": "com.fasterxml.jackson.databind.exc.MismatchedInputException", "errorMessage": "Cannot construct instance of `example.HTTPTriggerEvent` (although at least one Creator exists): no String-argument constructor/factory method to deserialize from String value ('Hello, FC!')\n at [Source: (byte[])\"\"Hello, FC!\"\"; line: 1, column: 1]", "stackTrace": [ "com.fasterxml.jackson.databind.exc.MismatchedInputException.from(MismatchedInputException.java:63)", "com.fasterxml.jackson.databind.DeserializationContext.reportInputMismatch(DeserializationContext.java:1588)", "com.fasterxml.jackson.databind.DeserializationContext.handleMissingInstantiator(DeserializationContext.java:1213)", "com.fasterxml.jackson.databind.deser.std.StdDeserializer._deserializeFromString(StdDeserializer.java:311)", "com.fasterxml.jackson.databind.deser.BeanDeserializerBase.deserializeFromString(BeanDeserializerBase.java:1495)", "com.fasterxml.jackson.databind.deser.BeanDeserializer._deserializeOther(BeanDeserializer.java:207)", "com.fasterxml.jackson.databind.deser.BeanDeserializer.deserialize(BeanDeserializer.java:197)", "com.fasterxml.jackson.databind.deser.DefaultDeserializationContext.readRootValue(DefaultDeserializationContext.java:322)", "com.fasterxml.jackson.databind.ObjectMapper._readMapAndClose(ObjectMapper.java:4593)", "com.fasterxml.jackson.databind.ObjectMapper.readValue(ObjectMapper.java:3643)" ] }
```

## 示例程序

函数计算官方库包含了使用各种处理程序类型和接口的示例应用程序。每个示例应用程序都包含用于轻松编译部署的方法。例如：

- [java11-blank-stream-event](https://github.com/awesome-fc/code-example/tree/master/java/java11-blank-stream-event)：使用Stream格式的事件回调处理程序。
- [java11-blank-pojo-event](https://github.com/awesome-fc/code-example/tree/master/java/java11-blank-pojo-event)：使用POJO格式的事件回调处理程序。
