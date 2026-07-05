# 函数实例生命周期回调方法

本文介绍C#运行时实现函数实例生命周期回调的方法。

## 背景信息

当您实现并配置函数实例生命周期回调后，函数计算将在相关实例生命周期事件发生时调用对应的回调程序。C#运行时支持Initializer和PreStop回调。更多信息，请参见[配置实例生命周期](https://help.aliyun.com/zh/functioncompute/fc/function-instance-lifecycle)。

函数实例生命周期回调程序与正常调用请求计费规则一致，但其执行日志只能在**实时日志**、**函数日志**或**高级日志**中查询，**调用请求列表**不会展示回调程序日志。具体操作，请参见[查看实例生命周期回调函数日志](#b1b155704229n)。

## 回调方法签名

- 初始化回调程序（Initializer回调）
  
  在函数实例启动成功之后，运行请求处理程序（Handler）之前执行。函数计算保证在一个实例生命周期内，成功且只成功执行一次Initializer回调。如果您的Initializer回调第一次执行失败，那么此次函数调用直接返回失败，下次调用时，会再新建一个函数实例执行initializer回调。
  
  **
  
  **说明**
  
  当Initializer回调程序执行超时或失败时，服务端始终返回HTTP 200状态码，必须通过响应头`X-Fc-Error-Type:InitializationError`或响应体中的errorMessage字段判断是否因初始化失败导致错误。
- 预停止回调程序（PreStop回调）
  
  在函数实例销毁前执行。

C#的Initializer回调和PreStop回调方法签名相同，均只有一个Context输入参数，没有返回参数。定义如下。

```
public void FunctionName(IFcContext context);
```

您也可以将回调方法设置为静态方法，定义如下。

```
public static void FunctionName(IFcContext context);
```

## 简单示例：流式事件请求处理程序

以下示例代码展示一个简单的包含Initializer回调和PreStop回调的程序。

```
using System; using System.IO; using System.Threading.Tasks; using Aliyun.Serverless.Core; using Microsoft.Extensions.Logging; namespace Example { public class Hello { public void Initialize(IFcContext context) { IFcLogger logger = context.Logger; logger.LogInformation("Initialize start"); logger.LogInformation("Handle initializer: {0}", context.RequestId); logger.LogInformation("Initialize end"); } public void PreStop(IFcContext context) { IFcLogger logger = context.Logger; logger.LogInformation("PreStop start"); logger.LogInformation("Handle PreStop: {0}", context.RequestId); logger.LogInformation("PreStop end"); } public async Task<Stream> StreamHandler(Stream input, IFcContext context) { IFcLogger logger = context.Logger; logger.LogInformation("Handle request: {0}", context.RequestId); MemoryStream copy = new MemoryStream(); await input.CopyToAsync(copy); copy.Seek(0, SeekOrigin.Begin); return copy; } static void Main(string[] args){} } }
```

## 配置生命周期回调函数

### 通过控制台配置

在[函数计算控制台](https://fcnext.console.aliyun.com)的函数**配置**>**实例配置**中设置生命周期回调，具体操作，请参见[配置实例生命周期](https://help.aliyun.com/zh/functioncompute/fc/function-instance-lifecycle)。回调方法的格式和请求处理程序的格式相同，为`程序集名称::命名空间.类名::方法名`。更多信息，请参见[请求处理程序（Handler）](https://help.aliyun.com/zh/functioncompute/fc/user-guide/handlers-in-a-c-runtime)。

示例如下。

- Initializer回调程序：`HelloFcApp::Example.Hello::Initialize`
- PreStop回调程序：`HelloFcApp::Example.Hello::PreStop`

### 通过Serverless Devs配置

如果使用Serverless Devs工具，需要在s.yaml配置文件中添加Initializer回调程序和PreStop回调程序。

- Initializer回调配置
  
  在function配置下添加instanceLifecycleConfig.initializer字段，包括handler和timeout两个字段。
- PreStop回调配置
  
  在function配置下添加instanceLifecycleConfig.preStop字段，包括handler和timeout两个字段。

具体示例如下所示。

```
# ------------------------------------ # 官方手册: https://manual.serverless-devs.com/user-guide/aliyun/#fc3 # 常见小贴士: https://manual.serverless-devs.com/user-guide/tips/ # 有问题快来钉钉群问一下吧：33947367 # ------------------------------------ edition: 3.0.0 name: hello-world-app access: "default" vars: # 全局变量 region: "cn-hangzhou" resources: hello_world: component: fc3 actions: pre-${regex('deploy|local')}: - run: dotnet publish -c Release -o ./target path: ./HelloWorldApp props: region: ${vars.region} functionName: "start-dotnetcore-p6jp" description: 'hello world by serverless devs' runtime: "dotnetcore3.1" code: ./HelloWorldApp/target/ handler: HelloWorldApp::Example.Hello::StreamHandler memorySize: 128 timeout: 10 instanceLifecycleConfig: # 扩展函数 initializer: # initializer函数 handler: HelloFcApp::Example.Hello::Initialize timeout: 60 preStop: # PreStop函数 handler: HelloFcApp::Example.Hello::PreStop # 函数入口 timeout: 60 # 超时时间 # triggers: # - triggerName: httpTrigger # 触发器名称 # triggerType: http # 触发器类型 # description: 'xxxx' # qualifier: LATEST # 触发服务的版本 # triggerConfig: # authType: anonymous # 鉴权类型，可选值：anonymous、function # disableURLInternet: false # 是否禁用公网访问 URL # methods: # HTTP 触发器支持的访问方法，可选值：GET、POST、PUT、DELETE、HEAD # - GET # - POST
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
