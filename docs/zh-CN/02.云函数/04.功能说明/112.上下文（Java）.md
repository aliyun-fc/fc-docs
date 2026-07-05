# 上下文

本文介绍在函数计算中使用Java运行时开发代码时，所涉及的Context的相关概念和使用示例。

## 什么是上下文

当函数计算运行您的函数时，会将上下文对象传递到执行方法中。该对象包含有关调用、服务、函数和执行环境等信息。上下文对象主要提供了以下参数。

| **字段** | **说明** |
| --- | --- |
| RequestId | 本次调用请求的ID。您可以记录下该ID，当出现问题时方便查询。 |
| Function | 当前调用的函数的一些基本信息，例如函数名、函数入口、函数内存和超时时间。 |
| Credentials | 为函数配置角色后，函数计算通过[AssumeRole](https://help.aliyun.com/zh/ram/developer-reference/api-sts-2015-04-01-assumerole#main-107864)API获取的一组临时密钥，其有效时间是36小时。您可以在代码中使用`Credentials`去访问相应的服务例如OSS，这就避免了您把自己的AccessKey信息编码在函数代码里。详细信息，请参见[授予函数计算访问其他云服务的权限](https://help.aliyun.com/zh/functioncompute/fc/grant-function-compute-permissions-to-access-other-alibaba-cloud-services)。 |
| Logger | 函数计算封装过的logger。 |
| Service | 当前调用的服务的一些基本信息。 |

接口定义如下。

```
package com.aliyun.fc.runtime; public interface Context { public String getRequestId(); public Credentials getExecutionCredentials(); public FunctionParam getFunctionParam(); public FunctionComputeLogger getLogger(); public Service getService(); # public OpenTracing getTracing(); public int getRetryCount(); }
```

## 示例程序：使用临时密钥访问OSS

该示例演示了如何使用上下文中的临时密钥向OSS中上传一个文件，详细代码，请参见[java11-oss](https://github.com/awesome-fc/code-example/tree/master/java/java11-oss)。

```
package example; import java.io.ByteArrayInputStream; import java.io.IOException; import java.io.InputStream; import java.io.OutputStream; import com.aliyun.fc.runtime.Context; import com.aliyun.fc.runtime.Credentials; import com.aliyun.fc.runtime.StreamRequestHandler; import com.aliyun.oss.OSS; import com.aliyun.oss.OSSClientBuilder; public class App implements StreamRequestHandler { @Override public void handleRequest( InputStream inputStream, OutputStream outputStream, Context context) throws IOException { // Bucket名称, 需要预先创建。 String bucketName = "my-bucket"; // Endpoint必须填写Bucket所在地域对应的Endpoint，推荐使用内网访问地址。以华东1（杭州）为例，内网访问Endpoint为https://oss-cn-hangzhou-internal.aliyuncs.com。 String endpoint = "https://oss-cn-hangzhou-internal.aliyuncs.com"; // 获取密钥信息，执行前，确保函数所在的服务配置了角色信息，并且角色需要拥有AliyunOSSFullAccess权限。 // 建议直接使用AliyunFCDefaultRole角色。 Credentials creds = context.getExecutionCredentials(); // 创建OSSClient实例。 /* 阿里云账号AccessKey拥有所有API的访问权限，建议您使用RAM用户进行API访问或日常运维。 建议不要把AccessKey ID和AccessKey Secret保存到工程代码里，否则可能导致AccessKey泄露，威胁您账号下所有资源的安全。 本示例以从上下文中获取AccessKey/AccessSecretKey为例。 */ OSS ossClient = new OSSClientBuilder().build(endpoint, creds.getAccessKeyId(), creds.getAccessKeySecret(), creds.getSecurityToken()); // 填写Byte数组。 byte[] content = "Hello FC".getBytes(); // 依次填写Bucket名称（例如examplebucket）和Object完整路径（例如exampledir/exampleobject.txt）。Object完整路径中不能包含Bucket名称。 ossClient.putObject(bucketName, "exampledir/exampleobject.txt", new ByteArrayInputStream(content)); // 关闭OSSClient。 ossClient.shutdown(); outputStream.write(new String("done").getBytes()); } }
```
