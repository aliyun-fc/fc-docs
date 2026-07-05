# 上下文

本文介绍在函数计算中使用Python运行时开发代码时，所涉及的Context（上下文）的相关概念和使用示例。

## 什么是上下文

当函数计算运行您的函数时，会将上下文对象传递到执行方法中。该对象包含有关调用、服务、函数和执行环境等信息。

### **Python 3.12**

Python 3.12运行时上下文对象主要提供了以下参数。

| **字段** | **类型** | **说明** |
| --- | --- | --- |
| request_id | String | 本次调用请求的唯一ID。您可以记录该ID，当函数调用出现问题时方便查询。 |
| function | FunctionMeta结构，包含以下字段：<br>- name<br>- handler<br>- memory<br>- timeout<br>- version_id<br>- qualifier | 当前调用的函数的一些基本信息，例如函数名、函数入口、函数内存、超时时间以及版本和别名信息。 |
| region | String | 当前调用的函数所在地域ID，例如在华东2（上海）地域调用，则地域ID为cn-shanghai。详细信息，请参见[服务接入地址](https://help.aliyun.com/zh/functioncompute/fc/developer-reference/fc-endpoints)。 |
| logger | String | 函数执行过程中记录日志信息。 |
| account_id | String | 函数所属的阿里云账号ID（主账号ID）。 |
| log_project、log_store | string | 接入的日志服务SLS的Project和。Logstore信息 |

Python 3.12移除了上下文字段`credentials`，您可以使用环境变量ALIBABA_CLOUD_ACCESS_KEY_ID、ALIBABA_CLOUD_ACCESS_KEY_SECRET和ALIBABA_CLOUD_SECURITY_TOKEN替代`credentials`访问其他资源，详见[配置环境变量](https://help.aliyun.com/zh/functioncompute/fc/user-guide/environment-variables)。

关于Python 3.12上下文的具体信息，请参见如下格式。

```
# -*- coding: utf-8 -*- import json class FunctionMeta: def __init__(self, name, handler, memory, timeout, version_id, qualifier): self.name = name self.handler = handler self.memory = memory self.timeout = timeout self.version_id = version_id self.qualifier = qualifier class FCContext: def __init__(self, account_id, request_id, function_meta, logger, log_project, log_store, region): self.account_id = account_id self.request_id = request_id self.function = function_meta self.logger = logger self.log_project = log_project self.log_store = log_store self.region = region
```

### **Python 3.10、Python 3.9和Python 3.6**

Python 3.10、Python 3.9和Python 3.6上下文对象主要提供了以下参数。

| **字段** | **类型** | **说明** |
| --- | --- | --- |
| request_id | String | 本次调用请求的唯一ID。您可以记录该ID，当函数调用出现问题时方便查询。 |
| credentials | Credentials结构，包含以下字段：<br>- access_key_id<br>- access_key_secret<br>- security_token | 为函数配置角色后，函数计算通过[AssumeRole](https://help.aliyun.com/zh/ram/developer-reference/api-sts-2015-04-01-assumerole#main-107864)API获取的一组临时密钥，其有效时间是36小时。您可以在代码中使用`Credentials`去访问相应的服务例如OSS，这就避免了您把自己的AccessKey信息编码在函数代码里。详细信息，请参见[使用函数角色授予函数计算访问其他云服务的权限](https://help.aliyun.com/zh/functioncompute/fc/grant-function-compute-permissions-to-access-other-alibaba-cloud-services)。 |
| function | FunctionMeta结构，包含以下字段：<br>- name<br>- handler<br>- memory<br>- timeout | 当前调用的函数的一些基本信息，例如函数名、函数入口、函数内存和超时时间。 |
| service | ServiceMeta结构，包含以下字段：<br>- log_project<br>- log_store<br>- qualifier<br>- version_id | 当前调用的函数所在的服务信息，包含接入的日志服务SLS的Project和Logstore信息，以及版本和别名信息。其中`qualifier`表示调用函数时指定的服务版本或别名，`versionId`表示实际调用的服务版本。 |
| region | String | 当前调用的函数所在地域ID，例如在华东2（上海）地域调用，则地域ID为cn-shanghai。详细信息，请参见[服务接入地址](https://help.aliyun.com/zh/functioncompute/fc/developer-reference/fc-endpoints)。 |
| account_id | String | 函数所属的阿里云账号ID（主账号ID）。 |

关于上下文的具体信息，请参见如下格式。

```
# -*- coding: utf-8 -*- import json class Credentials: def __init__(self, access_key_id, access_key_secret, security_token): self.access_key_id = access_key_id self.access_key_secret = access_key_secret self.security_token = security_token class Tracing: def __init__(self, span_context, base64_baggages, jaeger_endpoint): self.span_context = span_context self.jaeger_endpoint = jaeger_endpoint self.span_baggages = self.parseOpenTracingBaggages(base64_baggages) def parseOpenTracingBaggages(self, base64_baggages): span_baggages = {} # None || '' returns false if base64_baggages: try: import base64 str_baggages = base64.b64decode(base64_baggages) span_baggages = json.loads(str_baggages) except Exception as e: import logging fc_sys_logger = logging.getLogger('fc_sys_logger') fc_sys_logger.error('Failed to parse base64 opentracing baggages:[{}], err: {}'.format(base64_baggages, e)) return span_baggages class FunctionMeta: def __init__(self, name, handler, memory, timeout): self.name = name self.handler = handler self.memory = memory self.timeout = timeout class FCContext: def __init__(self, account_id, request_id, credentials, function_meta, service_meta, region, tracing): self.credentials = credentials self.function = function_meta self.request_id = request_id self.service = service_meta self.region = region self.account_id = account_id # self.tracing = tracing
```

## 使用示例

关于上下文的使用示例，请参见[示例二：通过临时密钥安全读写OSS的资源](https://help.aliyun.com/zh/functioncompute/fc/user-guide/event-handlers-1-1#section-46i-2fd-2um)。
