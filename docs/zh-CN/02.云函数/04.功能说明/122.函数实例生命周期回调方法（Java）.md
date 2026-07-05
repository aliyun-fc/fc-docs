# 函数实例生命周期回调方法

本文介绍Java运行时实现函数实例生命周期回调的方法。

## 背景信息

当您实现并配置函数实例生命周期回调后，函数计算系统将在相关实例生命周期事件发生时调用对应的回调程序。当前Java运行时支持Initializer和PreStop两种函数实例生命周期回调函数。更多信息，请参见[配置实例生命周期](https://help.aliyun.com/zh/functioncompute/fc/function-instance-lifecycle)。

函数实例生命周期回调程序与正常调用请求计费规则一致，但其执行日志只能在**实时日志**、**函数日志**或**高级日志**中查询，**调用请求列表**不会展示回调程序日志。具体操作，请参见[查看实例生命周期回调函数日志](#6e3db7e142lqu)。

## 回调方法签名

### **Initializer回调签名**

初始化回调程序（Initializer回调）是在函数实例启动成功之后，运行请求处理程序（Handler）之前执行。函数计算保证在一个实例生命周期内，成功且只成功执行一次Initializer回调。如果您的Initializer回调第一次执行失败，那么此次函数调用直接返回失败，下次调用时，会再新建一个函数实例执行initializer回调。

**

**说明**

当Initializer回调程序执行超时或失败时，服务端始终返回HTTP 200状态码，必须通过响应头`X-Fc-Error-Type:InitializationError`或响应体中的errorMessage字段判断是否因初始化失败导致错误。

Initializer回调只有一个context输入参数，使用方法同[请求处理程序（Handler）](https://help.aliyun.com/zh/functioncompute/fc/handlers-in-a-java-runtime)。

使用Initializer回调需要继承[FunctionInitializer接口](https://github.com/aliyun/fc-java-libs/blob/master/fc-java-core/src/main/java/com/aliyun/fc/runtime/FunctionInitializer.java)，并实现该接口的`initialize`方法，接口定义如下。

```
package com.aliyun.fc.runtime; import java.io.IOException; /** * This is the interface for the initialization operation */ public interface FunctionInitializer { /** * The interface to handle a function compute initialize request * * @param context The function compute initialize environment context object. * @throws IOException IOException during I/O handling */ void initialize(Context context) throws IOException; }
```

### **PreStop回调签名**

预停止回调程序（PreStop回调）在函数实例销毁前执行，使用PreStop回调需要继承[PreStopHandler接口](https://github.com/aliyun/fc-java-libs/blob/master/fc-java-core/src/main/java/com/aliyun/fc/runtime/PreStopHandler.java)，并实现该接口的`preStop`方法，接口定义如下。

```
package com.aliyun.fc.runtime; import java.io.IOException; /** * This is the interface for the preStop operation */ public interface PreStopHandler { /** * The interface to handle a function compute preStop request * * @param context The function compute preStop environment context object. * @throws IOException IOException during I/O handling */ void preStop(Context context) throws IOException; }
```

## 简单示例：流式事件请求处理程序

```
package example; import java.io.IOException; import java.io.InputStream; import java.io.OutputStream; import com.aliyun.fc.runtime.Context; import com.aliyun.fc.runtime.StreamRequestHandler; import com.aliyun.fc.runtime.FunctionInitializer; import com.aliyun.fc.runtime.PreStopHandler; public class App implements StreamRequestHandler, FunctionInitializer, PreStopHandler { @Override public void initialize(Context context) throws IOException { context.getLogger().info("initialize start ..."); } @Override public void handleRequest( InputStream inputStream, OutputStream outputStream, Context context) throws IOException { context.getLogger().info("handlerRequest ..."); outputStream.write(new String("hello world\n").getBytes()); } @Override public void preStop(Context context) throws IOException { context.getLogger().info("preStop start ..."); } }
```

**

**说明**

InputStream是流式的，OutputStream不支持流式返回数据。

## 配置生命周期回调函数

### **通过控制台配置**

在[函数计算控制台](https://fcnext.console.aliyun.com)的FC函数**配置**>**实例配置**中设置生命周期回调，回调格式为`[包名].[类名]::[方法名]`。

- **Initializer回调程序**：设置为`example.App::initialize`，表示实现`example`包中App.java文件里的`initialize`方法。
- **PreStop回调程序**：设置为`example.App::preStop`，表示实现`example`包中App.java文件里的`preStop`方法。

### **通过Serverless Devs配置**

如果使用Serverless Devs工具，需要在`s.yaml`配置文件中添加**Initializer 回调程序**和**PreStop 回调程序**。

- Initializer回调配置
  
  在function配置下添加instanceLifecycleConfig.initializer字段，包括handler和timeout两个字段。
- PreStop回调配置
  
  在function配置下添加instanceLifecycleConfig.preStop字段，包括handler和timeout两个字段。

具体的示例如下所示。

```
# ------------------------------------ # 官方手册: https://manual.serverless-devs.com/user-guide/aliyun/#fc3 # 常见小贴士: https://manual.serverless-devs.com/user-guide/tips/ # 有问题快来钉钉群问一下吧：33947367 # ------------------------------------ edition: 3.0.0 name: hello-world-app access: "default" vars: # 全局变量 region: "cn-hangzhou" resources: hello_world: component: fc3 actions: pre-${regex('deploy|local')}: - run: mvn package -DskipTests path: ./ props: region: ${vars.region} functionName: "start-java-1xqf" description: 'hello world by serverless devs' runtime: "java8" code: ./target/HelloFCJava-1.0-SNAPSHOT-jar-with-dependencies.jar handler: example.App::handleRequest memorySize: 128 timeout: 10 instanceLifecycleConfig: # 扩展函数 initializer: # initializer函数 handler: example.App::initialize timeout: 60 preStop: # PreStop函数 handler: example.App::preStop # 函数入口 timeout: 60 # 超时时间
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

- [java11-mysql](https://github.com/awesome-fc/code-example/tree/master/java/java11-mysql)：函数计算提供的Initializer回调和PreStop回调的示例程序。
  
  该示例为您展示了如何使用Java运行时的Initializer回调从环境变量中获取数据库配置并创建MySQL连接，以及如何使用PreStop回调负责关闭MySQL连接。
