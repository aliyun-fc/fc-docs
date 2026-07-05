# 上下文及日志格式

在自定义镜像函数中，如需获取上下文或者查看执行日志，可以参考自定义镜像的公共请求头以及日志格式。您可以根据这些信息打造属于您的自定义运行环境。

## 函数计算公共请求头

自定义镜像从函数计算中接收到的公共请求头如下表所示。如果您需要访问阿里云其他服务，您可能需要用到临时AccessKey的Headers。如果您需要迁移已有的应用，可忽略下文的内容。

**

**说明**

- 事件函数和HTTP函数均包含Common Headers。
- 公共请求头是函数计算自动生成的，主要包含权限信息和函数的基本信息等。

| **Header** | **描述** |
| --- | --- |
| x-fc-request-id | Request ID。 |
| x-fc-access-key-id | 临时AccessKey ID。您为函数配置角色后，函数计算通过[AssumeRole](https://help.aliyun.com/zh/ram/developer-reference/api-sts-2015-04-01-assumerole#main-107864)API获取的密钥ID。 |
| x-fc-access-key-secret | 临时AccessKey Secret。您为函数配置角色后，函数计算通过[AssumeRole](https://help.aliyun.com/zh/ram/developer-reference/api-sts-2015-04-01-assumerole#main-107864)API获取的临时密钥。 |
| x-fc-security-token | 临时Security Token。您为函数配置角色后，函数计算通过[AssumeRole](https://help.aliyun.com/zh/ram/developer-reference/api-sts-2015-04-01-assumerole#main-107864)API获取的临时密钥Token。 |
| x-fc-function-handler | 函数的Handler，如果运行时本身就是函数（例如自定义运行时或者自定义镜像函数），则该值无意义，设置为一个随机字符串即可。 |
| x-fc-function-memory | 函数最大能使用的内存。 |
| x-fc-region | 函数所在的地域。 |
| x-fc-account-id | 函数所有者的UID。 |
| x-fc-qualifier | 函数调用时指定的服务版本或别名。更多信息，请参见[使用版本和别名实现灰度发布](https://help.aliyun.com/zh/functioncompute/fc/user-guide/use-versions-and-aliases-to-implement-canary-release)。 |
| x-fc-version-id | 函数调用时指定的服务版本。 |
| x-fc-function-name | 函数名称。 |
| x-fc-service-logproject | 函数所在服务配置的日志项目。 |
| x-fc-service-logstore | 函数所在服务配置的日志库。 |
| x-fc-control-path | 函数的请求类型。<br>对于自定义运行时或自定义镜像，您可以根据Headers中的参数来判断函数调用是HTTP函数调用还是事件函数调用。参数信息如下：<br>- /invoke：该请求为事件函数调用。/invoke表示是Invoke函数调用请求。<br>- /http-invoke：该请求为HTTP函数调用。/http-invoke表示是HTTP invoke函数调用请求，函数计算会将您的请求（包括Path、Body和Headers）加上Common Headers后转发给自定义运行时或自定义镜像，自定义运行时或自定义镜像返回的响应头和响应体则会被返回给客户端。<br>- /initialize：/initialize表示第一次创建执行环境时，函数计算自动发起的Initialize函数调用请求。在容器的生命周期内，有且仅成功调用一次，类似于Class构造函数。 |

## 函数日志格式

建议您在创建服务时启用日志功能，自定义镜像中所有打印到标准输出（Stdout）的日志会自动收集到您指定的日志服务中。具体步骤，请参见[配置日志](https://help.aliyun.com/zh/functioncompute/fc/configure-the-logging-feature)。

函数计算在其他运行环境，即除自定义运行时和自定义镜像以外的运行环境中调用函数时，如果请求头中包含`x-fc-log-type" = "Tail"`，那么返回的响应头包含`x-fc-log-result`的内容就是函数执行时打印的日志，日志上限为4 KB。您可以在[函数计算控制台](https://fcnext.console.aliyun.com)函数执行结果中查看该日志。

**

**说明**

不同语言下指定日志级别的接口不同，请您根据实际运行环境设置。更多信息，请参见[基础信息](https://help.aliyun.com/zh/functioncompute/fc/basics)。

## 相关文档

- 使用自定义镜像函数，容器镜像依赖的基础环境会带来额外的数据下载和解压的时间，为了降低冷启动时间，请参见[冷启动优化最佳实践](https://help.aliyun.com/zh/functioncompute/fc-3-0/user-guide/overview-of-customcontainer#section-e70-asi-3lz)。
- 创建自定义镜像函数的方法和步骤，请参见[创建自定义镜像函数](https://help.aliyun.com/zh/functioncompute/fc/create-a-custom-container-function-in-a-container-runtime)。
- 自定义镜像实现函数实例生命周期回调的方法，请参见[函数实例生命周期回调](https://help.aliyun.com/zh/functioncompute/fc/lifecycle-hooks-for-gpu-function)。
