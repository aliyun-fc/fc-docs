# 触发器event格式

函数计算每个类型的触发器，其event内容和结构都会根据触发事件的具体情况有所不同，函数在被调用时可以根据event中的信息来执行相应的业务逻辑处理。

## 使用说明

触发器触发事件，传递到函数的event参数需要您自行在代码中解析才能使用。关于解析event参数的代码示例，请参见[示例一：解析JSON格式参数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/event-handlers-1-1#section-qv4-7ev-s0q)。

## HTTP触发器

通过HTTP触发器URL访问的请求或者通过自定义域名访问的请求，函数计算会将其转换为event，再将event传递给请求处理程序Handler。函数执行结束后，将函数返回的响应映射为HTTP响应。详情请参见[HTTP请求映射逻辑](https://help.aliyun.com/zh/functioncompute/fc/user-guide/http-trigger-invoking-function#a9f64be4a808d)和[响应解析逻辑](https://help.aliyun.com/zh/functioncompute/fc/user-guide/http-trigger-invoking-function#e34ba3bc38i9i)。

## 定时触发器

```
{ "triggerTime":"2023-12-26T07:49:00Z", "triggerName":"timer-trigger", "payload":"awesome-fc" }
```

| **参数** | **类型** | **示例值** | **描述** |
| --- | --- | --- | --- |
| triggerTime | String | 2023-12-26T07:49:00Z | 函数被触发的时间。 |
| triggerName | String | timer-trigger | 定时触发器的名称。 |
| payload | String | awesome-fc | 您在触发器配置里输入的自定义参数，即**触发消息**的值。 |

## OSS触发器

```
{ "events": [ { "eventName": "ObjectCreated:PutObject", "eventSource": "acs:oss", "eventTime": "2022-08-13T06:45:43.000Z", "eventVersion": "1.0", "oss": { "bucket": { "arn": "acs:oss:cn-hangzhou:123456789:testbucket", "name": "testbucket", "ownerIdentity": "164901546557****" }, "object": { "deltaSize": 122539, "eTag": "688A7BF4F233DC9C88A80BF985AB****", "key": "source/a.png", "objectMeta": { "mimeType": "application/zip", "userMeta": { "x-oss-meta-last-modified":"20250213" } }, "size": 122539 }, "ossSchemaVersion": "1.0", "ruleId": "9adac8e253828f4f7c0466d941fa3db81161****" }, "region": "cn-hangzhou", "requestParameters": { "sourceIPAddress": "140.205.XX.XX" }, "responseElements": { "requestId": "58F9FF2D3DF792092E12044C" }, "userIdentity": { "principalId": "164901546557****" } } ] }
```

event参数中不同属性字段的解释如下表所示。

| **参数** | **类型** | **示例值** | **描述** |
| --- | --- | --- | --- |
| eventName | String | ObjectCreated:PutObject | 事件类型。 |
| eventSource | String | acs:oss | 事件源，固定为`acs:oss`。 |
| eventTime | String | 2022-08-13T06:45:43.000Z | 事件产生的时间。使用ISO-8601标准时间格式。 |
| eventVersion | String | 1.0 | 事件协议的版本。 |
| oss | Map |  | OSS事件内容。 |
| bucket | Map |  | bucket参数内容。 |
| name | String | testbucket | Bucket的名称。 |
| arn | String | acs:oss:cn-hangzhou:123456789:testbucket | Bucket的唯一标识符。 |
| ownerIdentity | String | 164901546557**** | 创建Bucket的用户ID。 |
| object | Map |  | object参数内容。 |
| size | Int | 122539 | object的大小。单位：Byte。 |
| deltaSize | Int | 122539 | object的大小变化量。单位：Byte。<br>- 如果新增一个文件，此参数的值表示文件大小。<br>- 如果同名覆盖一个文件，此参数的值表示新文件与旧文件的大小差值。 |
| eTag | String | 688A7BF4F233DC9C88A80BF985AB**** | Object的标签。 |
| key | String | source/a.png | Object的名称。 |
| objectMeta | Map |  | objectMeta参数内容。 |
| mimeType | String | application/zip | Object的文件类型，更多请参见[mimeType](https://help.aliyun.com/zh/oss/user-guide/configure-the-content-type-header#concept-5041)。 |
| userMeta | Map |  | 用户自定义元数据，用于标识Object的用途或属性等。 |
| x-oss-meta-last-modified | String | 20250213 | 自定义元数据是一组键值对，元数据名称必须以`x-oss-meta-`开头。本示例值例如`"x-oss-meta-last-modified":"20250213"`含义为可用于记录本地文件最后修改时间为2025年2月13日。更多请参见[用户自定义元数据](https://help.aliyun.com/zh/oss/user-guide/manage-object-metadata-10/#section-3sr-lnh-ojh)。 |
| ossSchemaVersion | String | 1.0 | OSS模式的版本号。 |
| ruleId | String | 9adac8e253828f4f7c0466d941fa3db81161**** | 事件匹配的规则ID。 |
| region | String | cn-hangzhou | Bucket所在的地域。 |
| requestParameters | Map |  | 请求参数。 |
| sourceIPAddress | String | 140.205.XX.XX | 请求的源IP地址。 |
| responseElements | Map |  | 响应元素。 |
| requestId | String | 58F9FF2D3DF792092E12044C | 请求对应的Request ID。 |
| userIdentity | Map |  | 用户属性。 |
| principalId | String | 164901546557**** | 请求发起者的阿里云账号ID。 |

## SLS触发器

```
{ "parameter": {}, "source": { "endpoint": "http://cn-hangzhou-intranet.log.aliyuncs.com", "projectName": "fc-test-project", "logstoreName": "fc-test-logstore", "shardId": 0, "beginCursor": "MTUyOTQ4MDIwOTY1NTk3ODQ2Mw==", "endCursor": "MTUyOTQ4MDIwOTY1NTk3ODQ2NA==" }, "jobName": "1f7043ced683de1a4e3d8d70b5a412843d81****", "taskId": "c2691505-38da-4d1b-998a-f1d4bb8c****", "cursorTime": 1529486425 }
```

| **参数** | **说明** |
| --- | --- |
| parameter | 您配置触发器时填写的调用参数的值。 |
| source | 设置函数读取的日志块信息。<br>- endpoint：日志服务Project所属的阿里云地域。<br>- projectName：日志服务Project名称。<br>- logstoreName：函数计算要消费的Logstore名称，当前触发器会定时从该日志库中订阅数据到函数服务进行自定义加工。<br>- shardId：Logstore中一个确定的Shard。<br>- beginCursor：开始消费数据的位置。<br>- endCursor：停止消费数据的位置。<br>**<br>**说明**<br>在函数调试的时候，您可以调用[通过时间查询Cursor](https://help.aliyun.com/zh/sls/developer-reference/api-sls-2020-12-30-getcursor)接口获取beginCursor和endCursor，并按上述示例构建一个函数Event用于测试。 |
| jobName | 日志服务ETL Job名字，函数配置的SLS触发器对应一个日志服务的ETL Job。<br>此参数由函数计算自动生成，用户无需配置。 |
| taskId | 对于ETL Job而言，taskId是一个确定性的函数调用标识。<br>此参数由函数计算自动生成，用户无需配置。 |
| cursorTime | 最后一条日志到达日志服务端的Unix时间戳，单位：秒。 |

## CDN触发器

- LogFileCreated事件的event示例。
  
  替换`filePath`为您CDN日志的路径，或任何测试文件。
  
  ```
  { "events": [ { "eventName": "LogFileCreated", "eventSource": "cdn", "region": "cn-hangzhou", "eventVersion": "1.0.0", "eventTime": "2018-06-14T15:31:49+08:00", "traceId": "c6459282-6a4d-4413-894c-e4ea3968****", "userIdentity": { "aliUid": "164901546557****" }, "resource": { "domain": "example.com" }, "eventParameter": { "domain": "example.com", "endTime": 1528959900, "fileSize": 1788115, "filePath": "http://cdnlog.cn-hangzhou.oss.aliyun-inc.com/www.aliyun.com/2017_12_27/www.aliyun.com_2017_12_27_0800_0900.gz?OSSAccessKeyId=xxxx&Expires=xxxx&Signature=xxxx", "startTime": 1528959600 } } ] }
  ```
  
  event参数中不同属性字段的解释如下表所示。
  
  | **参数** | **类型** | **示例值** | **描述** |
  | --- | --- | --- | --- |
  | eventName | String | LogFileCreated | 事件类型。 |
  | eventSource | String | cdn | 事件源名称。 |
  | region | String | cn-hangzhou | CDN所在地域。 |
  | eventVersion | String | 1.0.0 | 事件触发版本。 |
  | eventTime | String | 2018-06-14T15:31:49+08:00 | 事件发生时间。 |
  | traceId | String | c6459282-6a4d-4413-894c-e4ea3968**** | 事件源传递的ID，用于排查问题。 |
  | userIdentity | Map |  | 用户属性。 |
  | aliUid | String | 164901546557**** | 阿里云账号ID。 |
  | resource | Map |  | 资源信息。 |
  | domain | String | example.com | 域名。 |
  | eventParameter | Map |  | 事件参数。 |
  | domain | String | example.com | 域名。 |
  | endTime | String | 1528959900 | 日志文件的结束时间。 |
  | fileSize | String | 1788115 | 日志文件大小。 |
  | filePath | String | http://cdnlog.cn-hangzhou.oss.aliyun-inc.com/www.aliyun.com/2017_12_27/www.aliyun.com_2017_12_27_0800_0900.gz?OSSAccessKeyId=xxxx&Expires=xxxx&Signature=xxxx | 日志文件地址。 |
  | startTime | String | 1528959600 | 日志文件的起始时间。 |
- CachedObjectsRefreshed和CachedObjectsPushed事件的event示例。
  
  ```
  { "events": [ { "eventName": "CachedObjectsRefreshed", "eventVersion": "1.0.0", "eventSource": "cdn", "region": "cn-hangzhou", "eventTime": "2018-03-16T14:19:55+08:00", "traceId": "cf89e5a8-7d59-4bb5-a33e-4c3d08e2****", "resource": { "domain": "example.com" }, "eventParameter": { "objectPath": [ "/2018/03/16/13/33b430c57e7.mp4", "/2018/03/16/14/4ff6b9bd54d.mp4" ], "createTime": 1521180769, "domain": "example.com", "completeTime": 1521180777, "objectType": "File", "taskId": 2089687230 }, "userIdentity": { "aliUid": "164901546557****" } } ] }
  ```
  
  event参数中不同属性字段的解释如下表所示。
  
  | **参数** | **类型** | **示例值** | **描述** |
  | --- | --- | --- | --- |
  | eventName | String | CachedObjectsRefreshed | 事件类型。 |
  | eventSource | String | cdn | 事件源名称。 |
  | region | String | cn-hangzhou | CDN所在地域。 |
  | eventVersion | String | 1.0.0 | 事件触发版本。 |
  | eventTime | String | 2018-06-14T15:31:49+08:00 | 事件发生时间。 |
  | traceId | String | c6459282-6a4d-4413-894c-e4ea3968**** | 事件源传递的ID，用于排查问题。 |
  | resource | Map |  | 资源信息。 |
  | domain | String | example.com | 域名。 |
  | eventParameter | Map |  | 事件参数。 |
  | objectPath | String | /2018/03/16/13/33b430c57e7.mp4 | 资源标识。 |
  | createTime | String | 1521180769 | 刷新开始时间。 |
  | domain | String | example.com | 域名。 |
  | completeTime | String | 1521180777 | 刷新结束时间。 |
  | objectType | String | File | 刷新类型，取值说明如下：<br>- File：文件。<br>- Directory：文件夹。 |
  | taskId | String | 2089687230 | 资源刷新任务ID。 |
  | userIdentity | Map |  | 用户属性。 |
  | aliUid | String | 164901546557**** | 阿里云账号ID。 |
- CdnDomainStarted和CdnDomainStopped事件的event示例。
  
  ```
  { "events": [ { "eventName": "CdnDomainStarted", "eventVersion": "1.0.0", "eventSource": "cdn", "region": "cn-hangzhou", "eventTime": "2018-03-16T14:19:55+08:00", "traceId": "cf89e5a8-7d59-4bb5-a33e-4c3d08e2****", "resource": { "domain": "example.com" }, "eventParameter": { "domain": "example.com", "status": "online" }, "userIdentity": { "aliUid": "164901546557****" } } ] }
  ```
  
  event参数中不同属性字段的解释如下表所示。
  
  | **参数** | **类型** | **示例值** | **描述** |
  | --- | --- | --- | --- |
  | eventName | String | CdnDomainStarted | 事件类型。 |
  | eventSource | String | cdn | 事件源名称。 |
  | region | String | cn-hangzhou | CDN所在地域。 |
  | eventVersion | String | 1.0.0 | 事件触发版本。 |
  | eventTime | String | 2018-06-14T15:31:49+08:00 | 事件发生时间。 |
  | traceId | String | c6459282-6a4d-4413-894c-e4ea3968**** | 事件源传递的ID，用于排查问题。 |
  | resource | Map |  | 资源信息。 |
  | domain | String | example.com | 域名。 |
  | eventParameter | Map |  | 事件参数。 |
  | domain | String | example.com | 域名。 |
  | status | String | online | 域名状态。 |
  | userIdentity | Map |  | 用户属性。 |
  | aliUid | String | 164901546557**** | 阿里云账号ID。 |
- CdnDomainAdded和CdnDomainDeleted事件的event示例。
  
  ```
  { "events": [ { "eventName": "CdnDomainAdded", "eventVersion": "1.0.0", "eventSource": "cdn", "region": "cn-hangzhou", "eventTime": "2018-03-16T14:19:55+08:00", "traceId": "cf89e5a8-7d59-4bb5-a33e-4c3d08e2****", "resource": { "domain": "example.com" }, "eventParameter": { "domain": "example.com" }, "userIdentity": { "aliUid": "164901546557****" } } ] }
  ```
  
  event参数中不同属性字段的解释如下表所示。
  
  | **参数** | **类型** | **示例值** | **描述** |
  | --- | --- | --- | --- |
  | eventName | String | CdnDomainAdded | 事件类型。 |
  | eventSource | String | cdn | 事件源名称。 |
  | region | String | cn-hangzhou | CDN所在地域。 |
  | eventVersion | String | 1.0.0 | 事件触发版本。 |
  | eventTime | String | 2018-06-14T15:31:49+08:00 | 事件发生时间。 |
  | traceId | String | c6459282-6a4d-4413-894c-e4ea3968**** | 事件源传递的ID，用于排查问题。 |
  | resource | Map |  | 资源信息。 |
  | domain | String | example.com | 域名。 |
  | eventParameter | Map |  | 事件参数。 |
  | domain | String | example.com | 域名。 |
  | userIdentity | Map |  | 用户属性。 |
  | aliUid | String | 164901546557**** | 阿里云账号ID。 |

## Tablestore触发器

```
{ "Version": "Sync-v1", "Records": [ { "Type": "PutRow", "Info": { "Timestamp": 1506416585740836 }, "PrimaryKey": [ { "ColumnName": "pk_0", "Value": 1506416585881590900 }, { "ColumnName": "pk_1", "Value": "2017-09-26 17:03:05.8815909 +0800 CST" }, { "ColumnName": "pk_2", "Value": 1506416585741000 } ], "Columns": [ { "Type": "Put", "ColumnName": "attr_0", "Value": "hello_table_store", "Timestamp": 1506416585741 }, { "Type": "Put", "ColumnName": "attr_1", "Value": 1506416585881590900, "Timestamp": 1506416585741 } ] } ] }
```

| **参数** | **描述** |
| --- | --- |
| Version | Payload版本号。示例如Sync-v1。类型为String。 |
| Records | 数据表中的增量数据行数组。包含如下内部成员：<br>- Type：数据行类型，包含PutRow、UpdateRow和DeleteRow。类型为String。<br>- Info：包含Timestamp内部成员。Timestamp表示该行的最后修改UTC时间。类型为Int64。 |
| PrimaryKey | 主键列数组。包含如下内部成员：<br>- ColumnName：主键列名称。类型为String。<br>- Value：主键列内容。类型为formated_value，支持Integer、String和Blob。 |
| Columns | 属性列数组。包括如下内部成员：<br>- Type：属性列类型，包含Put、DeleteOneVersion和DeleteAllVersions。类型为String。<br>- ColumnName：属性列名称。类型为String。<br>- Value：属性列内容。类型为formated_value，支持Integer、Boolean、Double、String和Blob。<br>- Timestamp：属性列最后修改UTC时间。类型为Int64。 |

## MNS主题触发器

- 创建触发器时，若**Event格式**设置为**STREAM**。
  
  - 当消息中不含消息属性（MessageAttributes）时，event格式如下。
    
    **
    
    **说明**
    
    当消息中不含消息属性（MessageAttributes）时，event的内容格式为JSON字符串。
    
    ```
    # 消息正文。 'hello topic'
    ```
  - 当消息中含有消息属性（MessageAttributes）时，event格式如下。
    
    **
    
    **说明**
    
    event的内容中包含MessageAttributes相关的键值对。更多信息，请参见[PublishMessage](https://help.aliyun.com/zh/mns/publishmessage-1#concept-2028955)。
    
    ```
    { "body": "hello topic", "attrs": { "Extend": "{\\"key\\":\\"value\\"}" } }
    ```
- 创建触发器时，若**Event格式**设置为**JSON**。
  
  - 当消息中不含消息属性（MessageAttributes）时，event格式如下。
    
    ```
    { "TopicOwner": "118620210433****", "Message": "hello topic", "Subscriber": "118620210433****", "PublishTime": 1550216480040, "SubscriptionName": "test-fc-subscribe", "MessageMD5": "BA4BA9B48AC81F0F9C66F6C909C3****", "TopicName": "Mytopic", "MessageId": "2F5B3C082B923D4EAC694B76D928****" }
    ```
  - 当消息中含有消息属性（MessageAttributes）时，event格式如下。
    
    **
    
    **说明**
    
    event的内容中包含MessageAttributes相关的键值对。更多信息，请参见[PublishMessage](https://help.aliyun.com/zh/mns/publishmessage-1#concept-2028955)。
    
    ```
    { "key": "value", "TopicOwner": "118620210433****", "Message": "hello topic", "Subscriber": "118620210433****", "PublishTime": 1550216302888, "SubscriptionName": "test-fc-subscribe", "MessageMD5": "BA4BA9B48AC81F0F9C66F6C909C3****", "TopicName": "Mytopic", "MessageId": "2F5B3C281B283D4EAC694B742528****" }
    ```

event参数中不同属性字段的解释如下表所示。

| **参数** | **类型** | **示例值** | **描述** |
| --- | --- | --- | --- |
| key | String | value | 消息属性相关的键值对。 |
| TopicOwner | String | 118620210433**** | 订阅Topic的AccountId。 |
| Message | String | hello topic | 消息内容。 |
| Subscriber | String | 118620210433**** | 用户的AccountId。 |
| PublishTime | Int | 1550216302888 | 消息发布时间。 |
| SubscriptionName | String | test-fc-subscribe | 订阅的名称。 |
| MessageMD5 | String | BA4BA9B48AC81F0F9C66F6C909C3**** | 消息正文的MD5值。 |
| TopicName | String | Mytopic | Topic名称。 |
| MessageId | String | 2F5B3C281B283D4EAC694B742528**** | 消息的编号。 |

## **MNS队列触发器**

`event`格式如下所示。

```
[ { "id":"c2g71017-6f65-fhcf-a814-a396fc8d****", "source":"MNS-Function-mnstrigger", "specversion":"1.0", "type":"mns:Queue:SendMessage", "datacontenttype":"application/json; charset=utf-8", "subject":"acs:mns:cn-hangzhou:164901546557****:queues/zeus", "time":"2021-04-08T06:28:17.093Z", "aliyunaccountid":"164901546557****", "aliyunpublishtime":"2021-10-15T07:06:34.028Z", "aliyunoriginalaccountid":"164901546557****", "aliyuneventbusname":"MNS-Function-mnstrigger", "aliyunregionid":"cn-chengdu", "aliyunpublishaddr":"42.120.XX.XX", "data":{ "requestId":"606EA3074344430D4C81****", "messageId":"C6DB60D1574661357FA227277445****", "messageBody":"TEST" } }, { "id":"d2g71017-6f65-fhcf-a814-a396fc8d****", "source":"MNS-Function-mnstrigger", "specversion":"1.0", "type":"mns:Queue:SendMessage", "datacontenttype":"application/json; charset=utf-8", "subject":"acs:mns:cn-hangzhou:164901546557****:queues/zeus", "time":"2021-04-08T06:28:17.093Z", "aliyunaccountid":"164901546557****", "aliyunpublishtime":"2021-10-15T07:06:34.028Z", "aliyunoriginalaccountid":"164901546557****", "aliyuneventbusname":"MNS-Function-mnstrigger", "aliyunregionid":"cn-chengdu", "aliyunpublishaddr":"42.120.XX.XX", "data":{ "requestId":"606EA3074344430D4C81****", "messageId":"C6DB60D1574661357FA227277445****", "messageBody":"TEST" } } ]
```

data字段包含的参数解释如下表所示。关于CloudEvents规范中定义的参数解释，请参见[事件概述](https://help.aliyun.com/zh/eventbridge/user-guide/event-overview#concept-1938024)。

| **参数** | **类型** | **示例值** | **描述** |
| --- | --- | --- | --- |
| requestId | String | 606EA3074344430D4C81**** | 请求ID。每个请求的ID取值唯一。 |
| messageId | String | C6DB60D1574661357FA227277445**** | 消息ID。每条消息的ID取值唯一。 |
| messageBody | String | TEST | 消息内容。 |

## RocketMQ触发器

`event`格式如下所示。

```
[ { "id":"94ebc15f-f0db-4bbe-acce-56fb72fb****", "source":"RocketMQ-Function-rocketmq-trigger", "specversion":"1.0", "type":"mq:Topic:SendMessage", "datacontenttype":"application/json; charset=utf-8", "subject":"acs:mq:cn-hangzhou:164901546557****:MQ_INST_164901546557****_BXhFHryi%TopicName", "time":"2021-04-08T06:01:20.766Z", "aliyunaccountid":"164901546557****", "aliyunpublishtime":"2021-10-15T02:05:16.791Z", "aliyunoriginalaccountid":"164901546557****", "aliyuneventbusname":"RocketMQ-Function-rocketmq-trigger", "aliyunregionid":"cn-chengdu", "aliyunpublishaddr":"42.120.XX.XX", "data":{ "topic":"TopicName", "systemProperties":{ "MIN_OFFSET":"0", "TRACE_ON":"true", "MAX_OFFSET":"8", "MSG_REGION":"cn-hangzhou", "KEYS":"systemProperties.KEYS", "CONSUME_START_TIME":1628577790396, "TAGS":"systemProperties.TAGS", "INSTANCE_ID":"MQ_INST_164901546557****_BXhFHryi" }, "userProperties":{ }, "body":"TEST" } }, { "id":"94ebc15f-f0db-4bbe-acce-56fb72fb****", "source":"RocketMQ-Function-rocketmq-trigger", "specversion":"1.0", "type":"mq:Topic:SendMessage", "datacontenttype":"application/json; charset=utf-8", "subject":"acs:mq:cn-hangzhou:164901546557****:MQ_INST_164901546557****_BXhFHryi%TopicName", "time":"2021-04-08T06:01:20.766Z", "aliyunaccountid":"164901546557****", "aliyunpublishtime":"2021-10-15T02:05:16.791Z", "aliyunoriginalaccountid":"164901546557****", "aliyuneventbusname":"RocketMQ-Function-rocketmq-trigger", "aliyunregionid":"cn-chengdu", "aliyunpublishaddr":"42.120.XX.XX", "data":{ "topic":"TopicName", "systemProperties":{ "MIN_OFFSET":"0", "TRACE_ON":"true", "MAX_OFFSET":"8", "MSG_REGION":"cn-hangzhou", "KEYS":"systemProperties.KEYS", "CONSUME_START_TIME":1628577790396, "TAGS":"systemProperties.TAGS", "INSTANCE_ID":"MQ_INST_164901546557****_BXhFHryi" }, "userProperties":{ }, "body":"TEST" } } ]
```

data字段包含的参数解释如下表所示。关于CloudEvents规范中定义的参数解释，请参见[事件概述](https://help.aliyun.com/zh/eventbridge/user-guide/event-overview#concept-1938024)。

| **参数** | **类型** | **示例值** | **描述** |
| --- | --- | --- | --- |
| topic | String | TopicName | Topic名称。 |
| systemProperties | Map |  | 系统属性。 |
| MIN_OFFSET | Int | 0 | 最低位点。 |
| TRACE_ON | Boolean | true | 是否有消息轨迹。取值说明如下：<br>- true：有消息轨迹。<br>- false：无消息轨迹。 |
| MAX_OFFSET | Int | 8 | 最高位点。 |
| MSG_REGION | String | cn-hangzhou | 发送消息的地域。 |
| KEYS | String | systemProperties.KEYS | 过滤属性。 |
| CONSUME_START_TIME | Long | 1628577790396 | 开始消费时间。单位：毫秒。 |
| UNIQ_KEY | String | AC14C305069E1B28CDFA3181CDA2**** | 消息唯一键。 |
| TAGS | String | systemProperties.TAGS | 过滤属性。 |
| INSTANCE_ID | String | MQ_INST_123456789098****_BXhFHryi | 实例ID。 |
| userProperties | Map | 无 | 用户属性。 |
| body | String | TEST | 消息内容。 |

## RabbitMQ触发器

`event`格式如下所示。

```
[ { "id":"bj694332-4cj1-389e-9d8c-b137h30b****", "source":"RabbitMQ-Function-rabbitmq-trigger", "specversion":"1.0", "type":"amqp:Queue:SendMessage", "datacontenttype":"application/json;charset=utf-8", "subject":"acs:amqp:cn-hangzhou:164901546557****:/instances/amqp-cn-tl32e756****/vhosts/eb-connect/queues/housekeeping", "time":"2021-08-12T06:56:40.709Z", "aliyunaccountid":"164901546557****", "aliyunpublishtime":"2021-10-15T08:58:55.140Z", "aliyunoriginalaccountid":"164901546557****", "aliyuneventbusname":"RabbitMQ-Function-rabbitmq-trigger", "aliyunregionid":"cn-chengdu", "aliyunpublishaddr":"42.120.XX.XX", "data":{ "envelope":{ "deliveryTag":98, "exchange":"", "redeliver":false, "routingKey":"housekeeping" }, "body":{ "Hello":"RabbitMQ" }, "props":{ "contentEncoding":"UTF-8", "messageId":"f7622d51-e198-41de-a072-77c1ead7****" } } }, { "id":"bj694332-4cj1-389e-9d8c-b137h30b****", "source":"RabbitMQ-Function-rabbitmq-trigger", "specversion":"1.0", "type":"amqp:Queue:SendMessage", "datacontenttype":"application/json;charset=utf-8", "subject":"acs:amqp:cn-hangzhou:164901546557****:/instances/amqp-cn-tl32e756****/vhosts/eb-connect/queues/housekeeping", "time":"2021-08-12T06:56:40.709Z", "aliyunaccountid":"164901546557****", "aliyunpublishtime":"2021-10-15T08:58:55.140Z", "aliyunoriginalaccountid":"164901546557****", "aliyuneventbusname":"RabbitMQ-Function-rabbitmq-trigger", "aliyunregionid":"cn-chengdu", "aliyunpublishaddr":"42.120.XX.XX", "data":{ "envelope":{ "deliveryTag":98, "exchange":"", "redeliver":false, "routingKey":"housekeeping" }, "body":{ "Hello":"RabbitMQ" }, "props":{ "contentEncoding":"UTF-8", "messageId":"f7622d51-e198-41de-a072-77c1ead7****" } } } ]
```

data字段包含的参数解释如下表所示。关于CloudEvents规范中定义的参数解释，请参见[事件概述](https://help.aliyun.com/zh/eventbridge/user-guide/event-overview#concept-1938024)。

| **参数** | **类型** | **示例值** | **描述** |
| --- | --- | --- | --- |
| body | Map |  | 消息内容。 |
| Hello | String | EventBridge | 用户数据。 |
| props | Map |  | 消息属性。 |
| contentEncoding | String | utf-8 | 消息内容编码。 |
| messageId | String | f7622d51-e198-41de-a072-77c1ead7**** | 消息ID。每条消息的ID取值唯一。 |
| envelope | Map |  | 消息的envelope信息。 |
| deliveryTag | Int | 98 | 消息的Tag。 |
| exchange | String | 无 | 消息的Exchange。 |
| redeliver | Boolean | false | 是否支持重发消息。取值说明如下：<br>- true：支持<br>- false：不支持 |
| routingKey | String | housekeeping | 消息的路由规则。 |

## Kafka触发器

`event`格式如下所示：

```
[ { "specversion":"1.0", "id":"8e215af8-ca18-4249-8645-f96c1026****", "source":"acs:alikafka", "type":"alikafka:Topic:Message", "subject":"acs:alikafka_pre-cn-i7m2t7t1****:topic:mytopic", "datacontenttype":"application/json; charset=utf-8", "time":"2022-06-23T02:49:51.589Z", "aliyunaccountid":"164901546557****", "data":{ "topic":"****", "partition":7, "offset":25, "timestamp":1655952591589, "headers":{ "headers":[ ], "isReadOnly":false }, "key":"keytest", "value":"hello kafka msg" } }, { "specversion":"1.0", "id":"8e215af8-ca18-4249-8645-f96c1026****", "source":"acs:alikafka", "type":"alikafka:Topic:Message", "subject":"acs:alikafka_pre-cn-i7m2t7t1****:topic:mytopic", "datacontenttype":"application/json; charset=utf-8", "time":"2022-06-23T02:49:51.589Z", "aliyunaccountid":"164901546557****", "data":{ "topic":"****", "partition":7, "offset":25, "timestamp":1655952591589, "headers":{ "headers":[ ], "isReadOnly":false }, "key":"keytest", "value":"hello kafka msg" } } ]
```

CloudEvents规范中定义的参数解释，请参见[事件概述](https://help.aliyun.com/zh/eventbridge/user-guide/event-overview#concept-1938024)。

data字段包含的参数解释如下表所示。

| **参数** | **类型** | **示例值** | **描述** |
| --- | --- | --- | --- |
| topic | String | TopicName | Topic的名称。 |
| partition | Int | 1 | 云消息队列 Kafka 版的消费分区信息。 |
| offset | Int | 0 | 云消息队列 Kafka 版的消息位点。 |
| timestamp | String | 1655952591589 | 开始消费时间戳。 |
| headers.headers | List | [header1, header2] | 消息 header |
| headers.isReadOnly | Boolean | false | 此字段仅保留，无实际意义 |
| key | String | dataKey | 消息 key |
| value | String | dataValue | 消息 value。具体内容格式和任务配置的数据格式相关。<br>- Json：消息内容解析为 Json 结构<br>- Text：消息内容解析为字符串<br>- Binary：消息内容经 base64 编码后的字符串 |

## **DTS触发器**

`event`格式如下所示：

```
[ { "data": { "id": 321****, "topicPartition": { "hash": 0, "partition": 0, "topic": "cn_hangzhou_rm_1234****_test_version2" }, "offset": 3218099, "sourceTimestamp": 1654847757, "operationType": "UPDATE", "schema": { "recordFields": [ { "fieldName": "id", "rawDataTypeNum": 8, "isPrimaryKey": true, "isUniqueKey": false, "fieldPosition": 0 }, { "fieldName": "topic", "rawDataTypeNum": 253, "isPrimaryKey": false, "isUniqueKey": false, "fieldPosition": 1 } ], "nameIndex": { "id": { "fieldName": "id", "rawDataTypeNum": 8, "isPrimaryKey": true, "isUniqueKey": false, "fieldPosition": 0 }, "topic": { "fieldName": "topic", "rawDataTypeNum": 253, "isPrimaryKey": false, "isUniqueKey": false, "fieldPosition": 1 } }, "schemaId": "(hangzhou-test-db,hangzhou-test-db,message_info)", "databaseName": "hangzhou--test-db", "tableName": "message_info", "primaryIndexInfo": { "indexType": "PrimaryKey", "indexFields": [ { "fieldName": "id", "rawDataTypeNum": 8, "isPrimaryKey": true, "isUniqueKey": false, "fieldPosition": 0 } ], "cardinality": 0, "nullable": true, "isFirstUniqueIndex": false }, "uniqueIndexInfo": [], "foreignIndexInfo": [], "normalIndexInfo": [], "databaseInfo": { "databaseType": "MySQL", "version": "5.7.35-log" }, "totalRows": 0 }, "beforeImage": { "recordSchema": { "recordFields": [ { "fieldName": "id", "rawDataTypeNum": 8, "isPrimaryKey": true, "isUniqueKey": false, "fieldPosition": 0 }, { "fieldName": "topic", "rawDataTypeNum": 253, "isPrimaryKey": false, "isUniqueKey": false, "fieldPosition": 1 } ], "nameIndex": { "id": { "fieldName": "id", "rawDataTypeNum": 8, "isPrimaryKey": true, "isUniqueKey": false, "fieldPosition": 0 }, "topic": { "fieldName": "topic", "rawDataTypeNum": 253, "isPrimaryKey": false, "isUniqueKey": false, "fieldPosition": 1 } }, "schemaId": "(hangzhou-test-db,hangzhou-test-db,message_info)", "databaseName": "hangzhou-test-db", "tableName": "message_info", "primaryIndexInfo": { "indexType": "PrimaryKey", "indexFields": [ { "fieldName": "id", "rawDataTypeNum": 8, "isPrimaryKey": true, "isUniqueKey": false, "fieldPosition": 0 } ], "cardinality": 0, "nullable": true, "isFirstUniqueIndex": false }, "uniqueIndexInfo": [], "foreignIndexInfo": [], "normalIndexInfo": [], "databaseInfo": { "databaseType": "MySQL", "version": "5.7.35-log" }, "totalRows": 0 }, "values": [ { "data": 115 }, { "data": { "hb": [ 104, 101, 108, 108, 111 ], "offset": 0, "isReadOnly": false, "bigEndian": true, "nativeByteOrder": false, "mark": -1, "position": 0, "limit": 9, "capacity": 9, "address": 0 }, "charset": "utf8mb4" } ], "size": 45 }, "afterImage": { "recordSchema": { "recordFields": [ { "fieldName": "id", "rawDataTypeNum": 8, "isPrimaryKey": true, "isUniqueKey": false, "fieldPosition": 0 }, { "fieldName": "topic", "rawDataTypeNum": 253, "isPrimaryKey": false, "isUniqueKey": false, "fieldPosition": 1 } ], "nameIndex": { "id": { "fieldName": "id", "rawDataTypeNum": 8, "isPrimaryKey": true, "isUniqueKey": false, "fieldPosition": 0 }, "topic": { "fieldName": "topic", "rawDataTypeNum": 253, "isPrimaryKey": false, "isUniqueKey": false, "fieldPosition": 1 } }, "schemaId": "(hangzhou-test-db,hangzhou-test-db,message_info)", "databaseName": "hangzhou-test-db", "tableName": "message_info", "primaryIndexInfo": { "indexType": "PrimaryKey", "indexFields": [ { "fieldName": "id", "rawDataTypeNum": 8, "isPrimaryKey": true, "isUniqueKey": false, "fieldPosition": 0 } ], "cardinality": 0, "nullable": true, "isFirstUniqueIndex": false }, "uniqueIndexInfo": [], "foreignIndexInfo": [], "normalIndexInfo": [], "databaseInfo": { "databaseType": "MySQL", "version": "5.7.35-log" }, "totalRows": 0 }, "values": [ { "data": 115 }, { "data": { "hb": [ 98, 121, 101 ], "offset": 0, "isReadOnly": false, "bigEndian": true, "nativeByteOrder": false, "mark": -1, "position": 0, "limit": 11, "capacity": 11, "address": 0 }, "charset": "utf8mb4" } ], "size": 47 } }, "id": "12f701a43741d404fa9a7be89d9acae0-321****", "source": "DTSstreamDemo", "specversion": "1.0", "type": "dts:ConsumeMessage", "datacontenttype": "application/json; charset=utf-8", "time": "2022-06-10T07:55:57Z", "subject": "acs:dts:cn-hangzhou:12345****:kk123abc60g782/dtsabcdet1ro" } ]
```

CloudEvents规范中定义的参数解释，请参见[事件概述](https://help.aliyun.com/zh/eventbridge/user-guide/event-overview#concept-1938024)。

data字段包含的参数解释如下表所示。

| **参数** | **类型** | **说明** |
| --- | --- | --- |
| id | String | DTS数据ID。 |
| topicPartition | Array | Topic的分区信息。 |
| hash | String | DTS底层存储参数。 |
| partition | String | Topic的分区。 |
| topic | String | Topic的名称。 |
| offset | Int | DTS数据对应的消息存储位点。 |
| sourceTimestamp | Int | DTS数据生成时间戳。 |
| operationType | String | DTS数据的操作类型。 |
| schema | Array | 数据库表结构信息。 |
| recordFields | Array | 字段详情记录。 |
| fieldName | String | 字段名称。 |
| rawDataTypeNum | Int | 字段类型映射值。<br>该值对应从数据订阅通道中获取的增量数据反序列化后的dataTypeNumber字段值，详情请参见[使用Kafka客户端消费订阅数据](https://help.aliyun.com/zh/dts/user-guide/use-a-kafka-client-to-consume-tracked-data-2)。 |
| isPrimaryKey | Boolean | 字段是否是主键。 |
| isUniqueKey | Boolean | 字段是否是唯一值。 |
| fieldPosition | String | 字段位置。 |
| nameIndex | Array | 命名索引。 |
| schemaId | String | 数据库表结构信息的ID。 |
| databaseName | String | 数据库名称。 |
| tableName | String | 数据表名称。 |
| primaryIndexInfo | String | 主键索引。 |
| indexType | String | 主键索引类型。 |
| indexFields | Array | 主键索引字段内容。 |
| cardinality | String | 主键基数。 |
| nullable | Boolean | 主键是否可为null。 |
| isFirstUniqueIndex | Boolean | 是否是第一个唯一索引。 |
| uniqueIndexInfo | String | 唯一索引。 |
| foreignIndexInfo | String | 外键索引。 |
| normalIndexInfo | String | 普通索引。 |
| databaseInfo | Array | 数据库信息。 |
| databaseType | String | 数据库类型。 |
| version | String | 数据库版本。 |
| totalRows | Int | 数据表的总行数。 |
| beforeImage | String | 操作前记录字段内容镜像。 |
| values | String | 记录字段的值。 |
| size | Int | 记录字段大小。 |
| afterImage | String | 操作后记录字段内容镜像。 |

## MQTT触发器

```
[ { "props": { "firstTopic": "testTopic", "secondTopic": "/testMq4****", "clientId": "consumerGroupID@@@xxx" }, "body": "hello mq4Iot pub sub msg" } ]
```

**event**字段包含的参数解释如下表所示。

| **参数** | **类型** | **示例值** | **描述** |
| --- | --- | --- | --- |
| **props** | Map |  | 消息属性。 |
| **firstTopic** | String | testTopic | 用于收发消息的父级Topic。 |
| **secondTopic** | String | /testMq4**** | 子级Topic。 |
| **clientId** | String | consumerGroupID@@@xx | 客户端ID。 |
| **body** | String | hello mq4Iot pub sub msg | 消息内容。 |

## **自建Apache RocketMQ触发器**

```
[ { "msgId": "7F0000010BDD2A84AEE70DA49B57****", "topic": "testTopic", "systemProperties": { "UNIQ_KEY": "7F0000010BDD2A84AEE70DA49B57****", "CLUSTER": "DefaultCluster", "MIN_OFFSET": "0", "TAGS": "TagA", "MAX_OFFSET": "128" }, "userProperties": {}, "body": "Hello RocketMQ" } ]
```

**event**字段包含的参数解释如下表所示。

| **参数** | **类型** | **示例值** | **描述** |
| --- | --- | --- | --- |
| **msgId** | String | 7F0000010BDD2A84AEE70DA49B57**** | Apache RocketMQ消息 ID。 |
| **topic** | String | testTopic | Topic名称。 |
| **systemProperties** | Map |  | 系统属性。 |
| **UNIQ_KEY** | String | 7F0000010BDD2A84AEE70DA49B57**** | 消息唯一键。 |
| **CLUSTER** | String | DefaultCluster | Apache RocketMQ集群名称。 |
| **MIN_OFFSET** | Int | 0 | 最低位点。 |
| **MAX_OFFSET** | Int | 128 | 最高位点。 |
| **TAGS** | String | TagA | 过滤属性。 |
| **userProperties** | Map | 无 | 用户属性。 |
| **body** | String | Hello RocketMQ | 消息内容。 |

## **API网关触发器（仅事件函数）**

```
{ "path":"api request path", "httpMethod":"request method name", "headers":{all headers,including system headers}, "queryParameters":{query parameters}, "pathParameters":{path parameters}, "body":"string of request payload", "isBase64Encoded":"true|false, indicate if the body is Base64-encode" }
```

**event**字段包含的参数解释如下表所示。

| **参数** | **类型** | **描述** |
| --- | --- | --- |
| **path** | String | API请求路径。 |
| **httpMethod** | String | 请求的方法名称，例如GET、POST、PUT和DELETE等。 |
| **headers** | Object | 包含所有请求头信息，包括系统头和自定义头。 |
| **queryParameters** | Object | 查询参数，通常在 URL 的问号后面以键值对的形式出现。 |
| **pathParameters** | Object | 路径参数，通常是 URL 中的一部分，用于标识特定资源。 |
| **body** | String | 请求体。 |
| **isBase64Encoded** | Boolean | 是否对请求体body进行了Base64编码。<br>**<br>**说明**<br>- 如果`isBase64Encoded`的值为`true`，表示API网关传给函数计算的body内容已进行Base64编码。函数计算需要先对body内容进行Base64解码后再处理。<br>- 如果`isBase64Encoded`的值为`false`，表示API网关没有对body内容进行Base64编码，在函数中可以直接获取body内容。 |
