# CDN事件触发器概述

阿里云内容分发网络CDN（Content Delivery Network）和函数计算无缝集成，您可以编写函数对CDN事件进行自定义处理。当CDN系统捕获到指定类型的、满足过滤条件的事件后，通过CDN事件触发器触发函数执行。

## 背景信息

阿里云CDN是建立并覆盖在承载网之上、由分布在不同区域的边缘节点服务器群组成的分布式网络。阿里云CDN可以替代传统以Web Server为中心的数据传输模式，将源站资源缓存到阿里云全国各地的边缘服务器，供您就近快速获取，提升用户体验，降低源站压力。在函数计算中通过配置内容分发网络事件触发器（以下简称“CDN事件触发器”）集成CDN服务可以实现您对CDN的各类事件进行自定义处理。例如，您可以设置函数和对应的CDN触发器来处理www.taobao.com域名下的资源刷新事件，当该域名下有资源刷新事件时，CDN事件触发器会自动触发函数执行。

## 使用场景

CDN事件触发器可以实现函数计算与CDN服务的集成，集成的使用场景如下：

- CDN在预热（CachedObjectsPushed）和刷新（CachedObjectsRefreshed）用户数据后，通过触发器执行函数。用户可以及时得知资源预热刷新的状态并进行下一步处理，避免不断轮询列表查询最新状态。
- 日志文件生成后（LogFileCreated），通过触发器执行函数处理日志。您不需要长时间等待日志，可以及时转存或处理日志。
- 当某加速域名被停用（CdnDomainStopped）或者被启用（CdnDomainStarted），通过触发器执行函数及时作出相应的处理。

## CDN事件定义

当CDN系统捕获到相关事件后，会将事件信息编码为JSON字符串，传递给函数进行处理。CDN事件触发器当前支持的事件及版本如下表所示。

| **事件名称** | **事件版本** | **过滤参数** | **参考文档** |
| --- | --- | --- | --- |
| CachedObjectsRefreshed | 1.0.0 | domain | [RefreshObjectCaches - 刷新缓存](https://help.aliyun.com/zh/cdn/developer-reference/api-cdn-2018-05-10-refreshobjectcaches) |
| CachedObjectsBlocked | 1.0.0 | domain | 封装CDN节点上指定URL<br>**<br>**说明**<br>如果需要使用该接口，请[提交工单](https://selfservice.console.aliyun.com/ticket/createIndex)联系CDN产品开通接口白名单。 |
| CachedObjectsPushed | 1.0.0 | domain | [PushObjectCache - 预热URL](https://help.aliyun.com/zh/cdn/developer-reference/api-cdn-2018-05-10-pushobjectcache) |
| LogFileCreated | 1.0.0 | domain | [DescribeCdnDomainLogs - 查询离线日志下载地址](https://help.aliyun.com/zh/cdn/developer-reference/api-cdn-2018-05-10-describecdndomainlogs) |
| CdnDomainStarted | 1.0.0 | domain | [StartCdnDomain - 启用域名](https://help.aliyun.com/zh/cdn/developer-reference/api-cdn-2018-05-10-startcdndomain) |
| CdnDomainStopped | 1.0.0 | domain | [StopCdnDomain - 停用域名](https://help.aliyun.com/zh/cdn/developer-reference/api-cdn-2018-05-10-stopcdndomain) |
| CdnDomainAdded | 1.0.0 | domain | [AddCdnDomain - 添加域名](https://help.aliyun.com/zh/cdn/developer-reference/api-cdn-2018-05-10-addcdndomain) |
| CdnDomainDeleted | 1.0.0 | domain | [DeleteCdnDomain - 删除域名](https://help.aliyun.com/zh/cdn/developer-reference/api-cdn-2018-05-10-deletecdndomain) |
