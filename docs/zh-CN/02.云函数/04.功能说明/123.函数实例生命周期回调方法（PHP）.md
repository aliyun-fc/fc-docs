# 函数实例生命周期回调方法

本文介绍PHP如何实现并应用函数实例生命周期回调方法。

## 背景信息

当您实现并配置函数实例生命周期回调后，函数计算将在相关实例生命周期事件发生时调用对应的回调程序。当前PHP运行时支持Initializer和PreStop两种函数实例生命周期回调函数。更多信息，请参见[配置实例生命周期](https://help.aliyun.com/zh/functioncompute/fc/function-instance-lifecycle)。

函数实例生命周期回调程序与正常调用请求计费规则一致，但其执行日志只能在**实时日志**、**函数日志**或**高级日志**中查询，**调用请求列表**不会展示回调程序日志。具体操作，请参见[查看实例生命周期回调函数日志](#5d8c5ee142be6)。

## Initializer回调

### **Initializer示例**

初始化回调程序（Initializer回调）在函数实例启动成功之后，运行请求处理程序（Handler）之前执行。函数计算保证在一个实例生命周期内，成功且最多成功执行一次Initializer回调。如果您的Initializer回调第一次执行失败，那么此次函数调用直接返回失败，下次调用时，会再新建一个函数实例执行initializer回调。

**

**说明**

当Initializer回调程序执行超时或失败时，服务端始终返回HTTP 200状态码，必须通过响应头`X-Fc-Error-Type:InitializationError`或响应体中的errorMessage字段判断是否因初始化失败导致错误。

Initializer回调只有一个$context输入参数，使用方法同[请求处理程序（Handler）](https://help.aliyun.com/zh/functioncompute/fc/user-guide/handlers-in-a-php-runtime)。

一个最简单的Initializer回调如下所示。

```
<?php function my_initializer($context) { $logger = $GLOBALS['fcLogger']; $logger->info("hello world"); } ?>
```

`my_initializer`是Initializer回调方法名，需要与您在[函数计算控制台](https://fcnext.console.aliyun.com)配置的**Initializer 回调程序**相对应。例如，您为函数配置的**Initializer 回调程序**为`main.my_initializer`，那么函数计算在配置Initializer属性后会去加载`main.php`中定义的`my_initializer`方法。

### **方法签名**

- 输入参数只有`context`，包含的信息和事件请求处理程序（handler）的`context`保持一致。
- `context`中`initializer`和`initializationTimeout`两个信息是为Initializer回调设计，如果使用Initializer功能，会被分别设置为您为函数配置的**Initializer 回调程序**和**Initializer 回调超时时间**的值，否则为空，且不生效。
- 无返回值。

## PreStop回调

预停止回调程序（PreStop回调）在函数实例销毁前执行，方法签名同Initializer回调。

如下是preStop回调的具体示例。

```
<?php $counter = 0; function preStop($context) { $GLOBALS['fcLogger']->info("preStop ok"); } function handler($event, $context) { global $counter; $counter += 2; return $counter; } ?>
```

您可以在您为函数开通的LogStore中查询到PreStop函数的日志。比如使用如下格式的语句查询该函数所有日志。更多信息，请参见[查询回调函数相关日志](https://help.aliyun.com/zh/functioncompute/fc/function-instance-lifecycle#section-rbb-dwc-ifr)。

```
<funcName> AND <ServiceName> AND qualifier: <VERSION>
```

## 配置生命周期回调函数

### **通过控制台配置**

您可以在[函数计算控制台](https://fcnext.console.aliyun.com)的FC函数**配置**>**实例配置**中，配置**Initializer 回调程序**和**PreStop 回调程序**。具体操作步骤，请参见[配置实例生命周期](https://help.aliyun.com/zh/functioncompute/fc/function-instance-lifecycle)。回调格式为`[文件名.方法名]`，例如：

- **Initializer 回调程序**设置为`index.initialize`，表示`index.php`文件中的`initialize`方法。
- **PreStop 回调程序**设置为`index.preStop`，表示`index.php`文件中的`preStop`方法。

### **通过Serverless Devs工具配置**

如果使用Serverless Devs工具，需要在`s.yaml`配置文件中添加**Initializer 回调程序**和**PreStop 回调程序**。

- Initializer回调配置
  
  在function配置下添加instanceLifecycleConfig.initializer字段，包括handler和timeout两个字段。
- PreStop回调配置
  
  在function配置下添加instanceLifecycleConfig.preStop字段，包括handler和timeout两个字段。

具体的示例如下所示。

```
edition: 3.0.0 name: fcDeployApp access: "default" vars: # 全局变量 region: "cn-hangzhou" resources: hello_world: component: fc3 # 组件名称 props: region: ${vars.region} # 关于变量的使用方法，可以参考：https://docs.serverless-devs.com/serverless-devs/yaml#%E5%8F%98%E9%87%8F%E8%B5%8B%E5%80%BC functionName: "testphp" description: 'this is a test' runtime: "php7.2" code: ./ handler: index.handler memorySize: 128 timeout: 30 instanceLifecycleConfig: # 扩展函数 initializer: # initializer函数 handler: index.my_initializer timeout: 60 preStop: # PreStop函数 handler: index.preStop # 函数入口 timeout: 60 # 超时时间
```

关于Serverless Devs的YAML配置规范，请参见[Serverless Devs常用命令](https://help.aliyun.com/zh/functioncompute/fc/developer-reference/serverless-devs-commands-1)。

## 查看实例生命周期回调函数日志

您可以通过**函数日志**功能查看回调函数日志。

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com)，在左侧导航栏，选择**函数管理**>**函数列表**。
2. 在顶部菜单栏，选择地域，然后在**函数列表**页面，单击目标函数。
3. 在函数详情页面，选择**测试**页签，单击**测试函数**，然后选择**日志**>**函数日志**。
  
  在**函数日志**页签，您可以查看函数的调用日志和Initializer回调日志，示例如下。
  
  ```
  2024-03-04 17:57:28FC Initialize Start RequestId: 1-65e59b07-1520da26-bf73bbb91b69 2024-03-04 17:57:282024-03-04 09:57:28.192 1-65e59b07-1520da26-bf73bbb91b69 [info] initializer 2024-03-04 17:57:28FC Initialize End RequestId: 1-65e59b07-1520da26-bf73bbb91b69 2024-03-04 17:57:28FC Invoke Start RequestId: 1-65e59b07-1520da26-bf73bbb91b69 2024-03-04 17:57:28FC Invoke End RequestId: 1-65e59b07-1520da26-bf73bbb91b69
  ```
  
  因为每个函数实例会缓存一段时间，不会马上销毁，因此不能立即查看PreStop回调日志。如需快速触发PreStop回调，可更新函数配置或者函数代码。更新完成后，再次查看**函数日志**，您可以查看PreStop回调日志。示例如下。
  
  ```
  2024-03-04 18:33:26FC PreStop Start RequestId: 93c93603-9fbe-4576-9458-193c8b213031 2024-03-04 18:33:262024-03-04 10:33:26.077 93c93603-9fbe-4576-9458-193c8b213031 [info] preStop 2024-03-04 18:33:26FC PreStop End RequestId: 93c93603-9fbe-4576-9458-193c8b213031
  ```

## 示例程序

函数计算为您提供了使用Initializer回调和PreStop回调的MySQL示例程序。在本示例中，Initializer回调函数用于从环境变量中获取MySQL数据库配置，创建MySQL连接并测试连通性，PreStop回调函数负责关闭MySQL连接。详细信息，请参见[php72-mysql](https://github.com/awesome-fc/code-example/tree/master/php/php72-mysql)。
