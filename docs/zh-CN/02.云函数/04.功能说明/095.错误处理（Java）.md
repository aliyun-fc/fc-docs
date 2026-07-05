# 错误处理

本文介绍Java运行环境的错误处理，包括错误类型和异常信息。

## 错误类型

- 您的函数如果在执行过程中抛出异常，函数计算会捕获并返回异常信息。
  
  示例代码如下：
  
  ```
  package example; import com.aliyun.fc.runtime.Context; import com.aliyun.fc.runtime.StreamRequestHandler; import java.io.IOException; import java.io.InputStream; import java.io.OutputStream; public class HelloFC implements StreamRequestHandler { @Override public void handleRequest(InputStream inputStream, OutputStream outputStream, Context context) throws IOException { throw new IOException("oops"); } }
  ```
  
  调用函数时收到的响应如下所示。
  
  ```
  { "errorMessage" : "oops", "errorType" : "java.io.IOException", "errorCause" : "oops", "stackTrace" : [ "example.HelloFC.handleRequest(HelloFC.java:15)" ] }
  ```
- 如果您的函数在运行过程中主动退出，系统会返回一个通用的错误信息。
  
  示例代码如下：
  
  ```
  package example; import java.io.IOException; import java.io.InputStream; import java.io.OutputStream; import com.aliyun.fc.runtime.Context; import com.aliyun.fc.runtime.StreamRequestHandler; public class App implements StreamRequestHandler { @Override public void handleRequest(InputStream inputStream, OutputStream outputStream, Context context) throws IOException { System.exit(-1); } }
  ```
  
  调用函数时收到的响应如下所示。
  
  ```
  { errorMessage: 'Process exited unexpectedly before completing request (duration: 43ms, maxMemoryUsage: 65MB)' }
  ```

## 异常信息

异常信息包含如下三个字段：

| **字段** | **类型** | **说明** |
| --- | --- | --- |
| errorMessage | String | 异常信息。 |
| errorType | String | 异常类型。 |
| stackTrace | List | 异常堆栈。 |

更多错误类型，请参见[基础信息](https://help.aliyun.com/zh/functioncompute/fc/basics#section-cgk-2tl-g4v)。
