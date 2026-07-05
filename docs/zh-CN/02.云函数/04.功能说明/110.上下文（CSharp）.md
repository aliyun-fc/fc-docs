# 上下文

本文介绍在函数计算中使用C#运行时开发代码时，所涉及的Context（上下文）的相关概念和使用示例。

## 什么是上下文

当函数计算运行您的函数时，会将上下文对象传递到执行方法中。该对象包含有关调用、服务、函数和执行环境等信息。上下文对象主要提供了以下字段。

| **字段** | **说明** |
| --- | --- |
| RequestId | 本次调用请求的ID。您可以记录该ID，出现问题时方便查询。 |
| Function | 当前调用函数的基本信息，例如函数名、请求处理程序、函数内存和超时时间等。 |
| Credentials | 为函数配置角色后，函数计算通过[AssumeRole](https://help.aliyun.com/zh/ram/developer-reference/api-sts-2015-04-01-assumerole#main-107864)API获取的一组临时密钥，其有效时间是36小时。您可以在代码中使用`Credentials`去访问相应的服务例如OSS，这就避免了您把自己的AccessKey信息编码在函数代码里。详细信息，请参见[授予函数计算访问其他云服务的权限](https://help.aliyun.com/zh/functioncompute/fc/grant-function-compute-permissions-to-access-other-alibaba-cloud-services)。 |
| Logger | 函数计算封装过的Logger。 |
| Service | 当前调用的服务的一些基本信息。 |

您可以通过接口获取上下文信息，接口定义如下。更多信息，请参见[IFcContext](https://github.com/aliyun/fc-dotnet-libs/blob/master/Aliyun.Serverless.Core/IFcContext.cs)。

```
public interface IFcContext { /// <summary> /// The AliFc request ID associated with the request. /// This is the same ID returned to the client that called invoke(). /// This ID is reused for retries on the same request. /// </summary> string RequestId { get; } /// <summary> /// Gets the function parameter interface. /// </summary> /// <value>The function parameter interface.</value> IFunctionParameter FunctionParam {get;} /// <summary> /// AliFc logger associated with the Context object. /// </summary> IFcLogger Logger { get; } /// <summary> /// Gets the credentials interface. /// </summary> /// <value>The credentials interface.</value> ICredentials Credentials {get;} /// <summary> /// Gets the account identifier. /// </summary> /// <value>The account identifier.</value> string AccountId { get; } /// <summary> /// Gets the region. /// </summary> /// <value>The region.</value> string Region { get; } /// <summary> /// Gets the service meta. /// </summary> /// <value>The service meta.</value> IServiceMeta ServiceMeta { get; } }
```

## 示例程序：使用临时密钥访问OSS

该示例演示如何使用上下文中的临时密钥向OSS上传一个文件。更多信息，请参见[dotnet3-oss](https://github.com/awesome-fc/code-example/tree/master/java/java11-oss?spm=a2c4g.11186623.0.0.39f364d5tuA78m)。

```
using System; using System.IO; using Aliyun.OSS; using Aliyun.Serverless.Core; using Microsoft.Extensions.Logging; namespace Example { public class OssExample { public Stream HandleRequest(Stream stream, IFcContext context) { context.Logger.LogInformation("Handle request: {0}", context.RequestId); // Bucket名称, 需要预先创建。 string bucketName = "my-****"; // Object路径。 string objectName = "exampledir/exampleobject.txt"; // Endpoint必须填写Bucket所在地域对应的Endpoint，推荐使用内网访问地址。以华东1（杭州）为例，内网访问Endpoint为https://oss-cn-hangzhou-internal.aliyuncs.com。 string endpoint = "https://oss-cn-hangzhou-internal.aliyuncs.com"; // 获取密钥信息，执行前，确保函数所在的服务已配置角色信息，且为该角色授予AliyunOSSFullAccess权限。 // 建议直接使用AliyunFCDefaultRole角色。 ICredentials creds = context.Credentials; // 创建OSSClient实例。 /* 阿里云账号AccessKey拥有所有API的访问权限，建议您使用RAM用户进行API访问或日常运维。 建议不要把AccessKey ID和AccessKey Secret保存到工程代码里，否则可能导致AccessKey泄露，威胁您账号下所有资源的安全。 本示例以从上下文中获取AccessKey/AccessSecretKey为例。 */ OssClient ossClient = new OssClient(endpoint, creds.AccessKeyId, creds.AccessKeySecret, creds.SecurityToken); // 依次填写Bucket名称（例如examplebucket）和Object完整路径（例如exampledir/exampleobject.txt）。 ossClient .PutObject(bucketName, objectName, stream); OssObject obj = ossClient.GetObject(bucketName,objectName); context.Logger.LogInformation("Put object to oss success: {0}", obj.ToString()); return obj.Content; } } class Program { static void Main(string[] args) { Console.WriteLine("Hello World!"); } } }
```
