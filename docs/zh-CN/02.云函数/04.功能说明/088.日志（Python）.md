# 日志

本文介绍如何在Python运行环境下打印和查看日志。

## 打印日志

函数往标准输出stdout打印的日志内容会被收集到创建服务时指定的Logstore中，您可以使用以下方式打印日志。

### 使用logging模块打印日志

使用此方法打印的每条日志中都包含时间、RequestId和日志级别等信息，RequestId方便您在出错时定位问题日志。代码示例如下所示。

```
import logging def handler(event, context): logger = logging.getLogger() logger.info('hello world') return 'done'
```

执行以上代码，输出的日志内容如下所示。

```
2017-07-05T05:13:35.920Z a72df088-f738-cee3-e0fe-323ad****e5 [INFO] hello world
```

### 使用print打印日志

使用该方法打印日志会将内容原样输出到日志中。代码示例如下所示。

```
def handler(event, context): print ('hello world') return 'done'
```

执行以上代码，输出的日志内容如下所示。

```
hello world
```

### 使用context.getLogger打印日志

使用context.getLogger打印日志，以通过RequestId区分各并发请求的日志。代码示例如下所示。

```
def handler(event, context): context.getLogger().info("hello world") return 'done'
```

执行以上代码，输出的日志内容如下所示。

```
2022-07-13 10:26:02 6785e433-497e-4c4a-a81a-2d4096d1**** [INFO] hello world
```

## 查看日志

函数执行完成后，您可以在函数详情页的**调用日志**页签查看日志信息。具体操作和说明，请参见[查看调用日志](https://help.aliyun.com/zh/functioncompute/fc/configure-the-logging-feature#section-z06-gdf-7c9)。
