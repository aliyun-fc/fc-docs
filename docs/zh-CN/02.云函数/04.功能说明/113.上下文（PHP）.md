# 上下文

本文介绍在函数计算中使用PHP运行时开发代码时，所涉及的Context（上下文）的相关概念。

## 什么是上下文

当函数计算运行您的函数时，会将上下文对象传递到执行方法中。该对象包含有关调用、服务、函数和执行环境等信息。

在PHP运行时中，$context参数的数据类型是数组Array类型，定义如下所示。

```
[ 'requestId' => 'b1c5100f-819d-c421-3a5e-7782a27d8a33', 'credentials' => [ 'accessKeyId' => 'STS.access_key_id', 'accessKeySecret' => 'access_key_secret', 'securityToken' => 'security_token', ], 'function' => [ 'name' => 'my-func', 'handler' => 'index.handler', 'memory' => 128, 'timeout' => 10, 'initializer' => 'index.initializer', 'initializationTimeout' => 10, ], 'service' =>[ 'logProject' => 'my-log-project', 'logStore' => 'my-log-store', 'qualifier' => 'qualifier', 'versionId' => '1' ], 'region' => 'cn-shanghai', 'accountId' => '123456', 'tracing': { 'openTracingSpanContext': 'xxxxxxxxxxxx', 'jaegerEndpoint': 'xxxxxxxx', 'openTracingSpanBaggages': [] } ]
```

$context中包含了以下信息。

| **字段** | **类型** | **说明** |
| --- | --- | --- |
| requestId | String | 本次调用请求的唯一ID。您可以记录该ID，当函数调用出现问题时方便查询。 |
| credentials | Array类型，包含以下字段：<br>- accessKeyId<br>- accessKeySecret<br>- securityToken | 为函数配置角色后，函数计算通过[AssumeRole](https://help.aliyun.com/zh/ram/developer-reference/api-sts-2015-04-01-assumerole#main-107864)API获取的一组临时密钥，其有效时间是36小时。您可以在代码中使用`Credentials`去访问相应的服务例如OSS，这就避免了您把自己的AccessKey信息编码在函数代码里。详细信息，请参见[授予函数计算访问其他云服务的权限](https://help.aliyun.com/zh/functioncompute/fc/grant-function-compute-permissions-to-access-other-alibaba-cloud-services)。 |
| function | Array类型，包含以下字段：<br>- name<br>- handler<br>- memory<br>- timeout<br>- initializer<br>- initializationTimeout | 当前调用的函数的一些基本信息，例如函数名、函数入口、函数内存和超时时间。 |
| service | Array类型，包含以下字段：<br>- logProject<br>- logStore<br>- qualifier<br>- versionId | 当前调用的函数所在的服务信息，包含接入的日志服务SLS的Project和Logstore信息，以及版本和别名信息。其中`qualifier`表示调用函数时指定的服务版本或别名，`versionId`表示实际调用的服务版本。 |
| region | String | 当前调用的函数所在地域ID，例如在华东2（上海）地域调用，则地域ID为cn-shanghai。详细信息，请参见[服务接入地址](https://help.aliyun.com/zh/functioncompute/fc/developer-reference/fc-endpoints)。 |
| accountId | String | 函数所属的阿里云账号ID（主账号ID）。 |
