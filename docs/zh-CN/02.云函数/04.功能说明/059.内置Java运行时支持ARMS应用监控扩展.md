# 内置Java运行时支持ARMS应用监控扩展

本文主要介绍使用内置Java运行时如何接入ARMS应用监控。

目前支持Java运行时中的Java8、Java11两种版本，如果使用自定义运行时，请参见[自定义运行时支持ARMS应用监控扩展](https://help.aliyun.com/zh/functioncompute/fc/user-guide/arms-extensions-for-custom-runtimes)。

## 背景信息

函数计算无缝对接ARMS应用监控平台后，您可以通过ARMS应用监控平台对目标函数进行监控追踪，获取相关信息，例如实例级别的可观测性、链路追踪信息、Java虚拟机指标、代码级别的剖析（Profiling）信息和应用安全信息等。更多信息，请参见[什么是应用实时监控服务ARMS？](https://help.aliyun.com/zh/arms/product-overview/what-is-arms#concept-42781-zh)。

| **功能** | **描述** |
| --- | --- |
| 实例级别的可观测性 | 以函数实例为维度，聚合丰富的主机监控指标，例如CPU、内存及请求等。 |
| 链路追踪 | ARMS探针自动获取函数与上下游组件的拓扑关系及相关指标，您可以在ARMS监控平台查看相关信息，例如数据库、Redis及MQ等。 |
| Java虚拟机指标 | ARMS探针自动获取Java虚拟机应用，您可以在ARMS监控平台中查看Java虚拟机应用的相关监控数据，例如GC次数、堆信息及线程栈信息等。 |
| 代码级别的剖析 | 您可以查看函数执行过程中代码级别的剖析（Profiling）信息，例如每个方法的耗时、异常等。 |
| [应用安全](https://help.aliyun.com/zh/arms/application-security/product-overview/what-is-application-security#task-2118339) | 基于RASP（Runtime Application Self-Protection）技术，应用安全可以为应用在运行时提供强大的安全防护能力，并抵御绝大部分未知漏洞所利用的攻击手法。 |

## **内置Java运行时接入ARMS**

ARMS 应用监控是一种内部扩展，内置Java运行时要接入ARMS应用监控主要包括以下两部分内容。

### 使用公共层获取ARMS Agent程序

函数计算平台提供了支持Java8、Java11两种Java版本的ARMS Agent。

| **运行时** | **公共层ARN** |
| --- | --- |
| java8 | `acs:fc:{region}:official:layers/ArmsAgent4x/versions/1` |
| java11 | `acs:fc:{region}:official:layers/ArmsAgent4x/versions/1` |

### 设置环境变量

```
{ "FC_EXTENSIONS_ARMS_LICENSE_KEY": "xxx", "JAVA_TOOL_OPTIONS": "-javaagent:/opt/ArmsAgent/arms-bootstrap-1.7.0-SNAPSHOT.jar" }
```

- 设置环境变量`FC_EXTENSIONS_ARMS_LICENSE_KEY`，值为License Key 信息。关于License Key信息的获取方式，请参见[获取License Key信息](https://help.aliyun.com/zh/arms/application-monitoring/user-guide/install-the-arms-agent-for-a-java-application-in-function-compute#arms-cs-k8s-java)。
- 设置环境变量 JAVA_TOOL_OPTIONS， 官方公共层的 arms 程序均在目录`/opt/ArmsAgent/arms-bootstrap-1.7.0-SNAPSHOT.jar`。

**

**重要**

函数计算在调用结束至冻结前的等待时长会产生费用，收费策略与实例调用阶段的计费逻辑相同。具体信息，请参见[产品计费](https://help.aliyun.com/zh/functioncompute/fc/product-overview/billing-fc/)。

## 前提条件

- 已创建内置运行时的事件函数，具体的运行环境为Java 8或Java 11。具体操作，请参加[创建事件函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/creating-an-event-function)。
- 已开通ARMS服务。具体操作，请参见[开通ARMS](https://help.aliyun.com/zh/arms/getting-started/activate-arms#concept-65257-zh)。

## 操作步骤

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com)，在左侧导航栏，选择**函数管理**>**函数列表**。
2. 在顶部菜单栏，选择地域，然后在**函数列表**页面，单击目标函数。
3. 在函数配置页面，选择**配置**页签。
4. 找到**高级配置**单击其右侧**编辑**，在高级配置面板找到层区域进行编辑，选择**+添加层**>**通过ARN添加层**，添加与所选Java语言兼容的ArmsAgent层。修改ARN中的`{region}`的值，点击**部署**。
5. 在高级配置面板找到**环境变量**区域进行编辑，添加环境变量`JAVA_TOOL_OPTIONS=-javaagent:/opt/ArmsAgent/arms-bootstrap-1.7.0-SNAPSHOT.jar`和`FC_EXTENSIONS_ARMS_LICENSE_KEY=yourLicensekey`。具体操作，请参见[设置环境变量](https://help.aliyun.com/zh/functioncompute/fc-2-0/user-guide/arms-extensions-for-custom-runtimes#p-im4-1v0-gjx)。
6. 成功更新配置并部署代码后，您的函数将被添加到ARMS应用监控进行高性能管理。同时，ARMS监控将对您的服务进行计费。更多信息，请参见[计费概述](https://help.aliyun.com/zh/arms/application-monitoring/product-overview/billing-overview-1#concept-2121380)。

**

**重要**

- 当您的函数成功接入ARMS监控平台后，如果您需要查看对应监控信息，请确保ARMS监控平台和函数所属地域相同。
- 为了函数能够正常执行，请确保您的函数配置中，内存规格大于512 MB（ARMS大概占用300 MB内存）。

## 结果验证

当您成功将函数接入ARMS应用监控平台后，您可以在ARMS控制台查看接入的函数。

您也可以登录[ARMS控制台](https://arms.console.aliyun.com/#/home)，在左侧导航栏，选择**应用监控**>**应用列表**，然后单击目标应用名称，查看详细监控信息。更多信息，请参见[应用总览](https://help.aliyun.com/zh/arms/application-monitoring/user-guide/application-overview#concept-87109-zh)。
