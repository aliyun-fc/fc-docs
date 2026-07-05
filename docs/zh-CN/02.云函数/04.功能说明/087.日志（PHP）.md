# 日志

本文介绍如何在PHP运行环境下打印和查看日志。

## 打印日志

函数计算内置了logger模块，在使用内置运行时创建的函数中，您可以通过`$GLOBALS['fcLogger']`使用该内置logger模块，将打印的内容收集到创建服务时指定的日志服务Logstore中。使用其他方式创建的函数，您可以使用PHP提供的方法打印日志。

### **日志级别**

您可以通过setLevel方法改变日志级别，其中日志级别从高到低如下所示。

| **日志级别** | **Level** | **接口** | **描述** |
| --- | --- | --- | --- |
| EMERGENCY | 600 | `$logger->emergency` | 紧急日志 |
| ALERT | 550 | `$logger->alert` | 警示日志 |
| CRITICAL | 500 | `$logger->critical` | 严重警告 |
| ERROR | 400 | `$logger->error` | 出错信息 |
| WARNING | 300 | `$logger->warning` | 警告信息 |
| NOTICE | 250 | `$logger->notice` | 通知及常规日志 |
| INFO（默认） | 200 | `$logger->info` | 详细输出信息 |
| DEBUG | 100 | `$logger->debug` | 调试日志 |

### **使用内置日志模块打印日志**

使用该方法打印的每条日志中都包含时间、RequestId和日志级别等信息。打印日志的示例如下：

```
<?php function handler($event, $context) { $logger = $GLOBALS['fcLogger']; $logger->info('hello world'); $logger->critical('world hello'); $logger->setLevel(500); $logger->info('hello world 2'); $logger->critical('world hello 2'); return 'hello world'; }
```

上述例子中，首先使用默认的日志级别输出了2条日志，然后修改了默认日志级别，只输出1条日志。

执行以上代码输出的日志内容如下所示：

```
FunctionCompute php7.2 runtime inited. FC Invoke Start RequestId: 1-659xxxxx-16cxxxxx-39659xxxxxx 2024-01-04 10:50:44 1-659xxxxx-16cxxxxx-39659xxxxxx [INFO] hello world 2024-01-04 10:50:44 1-659xxxxx-16cxxxxx-39659xxxxxx [CRITICAL] world hello 2024-01-04 10:50:44 1-659xxxxx-16cxxxxx-39659xxxxxx [CRITICAL] world hello 2 \nFC Invoke End RequestId: 1-659xxxxx-16cxxxxx-39659xxxxxx
```

### **使用打印函数打印日志**

使用该方法打印日志会将内容原样输出到日志中。代码示例如下所示。

```
<?php function handler($event, $context) { var_dump("abcd"); echo "abcd 2\n"; fwrite(STDERR, "error\n"); return 'hello world'; }
```

输出如下：

```
FunctionCompute php7.2 runtime inited. FC Invoke Start RequestId: 1-659xxxxx-165xxxxx-455a04xxxxxx /code/index.php:4: string(4) "abcd" abcd 2 error \nFC Invoke End RequestId: 1-659xxxxx-165xxxxx-455a04xxxxxx
```

上述例子中，打印函数也可以替换为其他输出到标准输出、标准错误的函数。

## 查看日志

函数执行完成后，您可以在函数详情页的**日志**页签查看日志信息。具体操作和说明，请参见[查看调用日志](https://help.aliyun.com/zh/functioncompute/fc/configure-the-logging-feature#section-z06-gdf-7c9)。
