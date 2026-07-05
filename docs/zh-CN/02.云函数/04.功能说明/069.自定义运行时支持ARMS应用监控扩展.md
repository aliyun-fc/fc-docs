# 自定义运行时支持ARMS应用监控扩展

函数计算内置的Java 8运行时支持接入ARMS（Application Real-Time Monitoring Service）应用监控。自定义运行时中的Java 8、Java 11和Java 17也支持接入ARMS应用监控。本文介绍如何使用自定义运行时接入ARMS应用监控。

## 背景信息

函数计算无缝对接ARMS应用监控平台后，您可以通过ARMS应用监控平台对目标函数进行监控追踪，获取相关信息，例如实例级别的可观测性、链路追踪信息、Java虚拟机指标、代码级别的剖析（Profiling）信息和应用安全信息等。更多信息，请参见[什么是应用实时监控服务ARMS？](https://help.aliyun.com/zh/arms/product-overview/what-is-arms#concept-42781-zh)。

| **功能** | **描述** |
| --- | --- |
| 实例级别的可观测性 | 以函数实例为维度，聚合丰富的主机监控指标，例如CPU、内存及请求等。 |
| 链路追踪 | ARMS探针自动获取函数与上下游组件的拓扑关系及相关指标，您可以在ARMS监控平台查看相关信息，例如数据库、Redis及MQ等。 |
| Java虚拟机指标 | ARMS探针自动获取Java虚拟机应用，您可以在ARMS监控平台中查看Java虚拟机应用的相关监控数据，例如GC次数、堆信息及线程栈信息等。 |
| 代码级别的剖析 | 您可以查看函数执行过程中代码级别的剖析（Profiling）信息，例如每个方法的耗时、异常等。 |
| [应用安全](https://help.aliyun.com/zh/arms/application-security/product-overview/what-is-application-security#task-2118339) | 基于RASP（Runtime Application Self-Protection）技术，应用安全可以为应用在运行时提供强大的安全防护能力，并抵御绝大部分未知漏洞所利用的攻击手法。 |

## 自定义运行时接入ARMS

ARMS应用监控是一种内部扩展。自定义运行时接入ARMS应用监控时，主要包括以下三部分。

### 使用公共层获取ARMS Agent程序

函数计算平台以公共层的形式，提供了支持Java 8、Java 11和Java 17三种Java版本的ARMS Agent。

| **Java版本** | **兼容运行时** | **公共层ARN** |
| --- | --- | --- |
| Java 11/Java 8 | 自定义运行时 | acs:fc:{region}:official:layers/ArmsAgent273x/versions/1 |
| Java 17 | 自定义运行时 | acs:fc:{region}:official:layers/ArmsAgent273x_JDK17/versions/1 |

### 使用Bootstrap脚本作为启动命令

使用ARMS需要添加3个启动参数，考虑到启动命令比较复杂，建议通过脚本来启动。可以在函数代码页面使用WebIDE创建文件bootstrap，并设置文件权限为可执行权限（终端窗口执行命令`chmod +x bootstrap`）。示例代码如下所示。

```
#!/bin/bash set -eo pipefail # 1. 设置ARMS应用名称 appName="FC:Custom_Java_Arms_Demo" if [ -n "${FC_FUNCTION_NAME}" ]; then appName="FC:${FC_FUNCTION_NAME}" fi echo "appName: ${appName}" params=" " # 2. 添加ARMS参数 if [[ -n "${FC_EXTENSIONS_ARMS_LICENSE_KEY}" ]]; then echo "FC_EXTENSIONS_ARMS_LICENSE_KEY: ${FC_EXTENSIONS_ARMS_LICENSE_KEY}" params+="-Dfc.instanceId=$HOSTNAME@`hostname -i` " # 使用公共层的ARMS程序路径 params+="-javaagent:/opt/ArmsAgent/arms-bootstrap-1.7.0-SNAPSHOT.jar " params+="-Darms.licenseKey=${FC_EXTENSIONS_ARMS_LICENSE_KEY} " params+="-Darms.appName=${appName} " else echo "The environment FC_EXTENSIONS_ARMS_LICENSE_KEY does not exist, please set the FC_EXTENSIONS_ARMS_LICENSE_KEY environment!" exit 1 fi # 3. 启动应用程序 echo "params: ${params}" exec java $params \ -Dserver.port=9000 \ -jar /code/target/demo-0.0.1-SNAPSHOT.jar
```

示例代码解析如下。

1. 设置ARMS应用名称。默认为`FC:{FunctionName}`。
2. 添加ARMS参数。
  
  - `javaagent`：ARMS程序路径。如果使用ARMS Agent的公共层，该路径为`/opt/ArmsAgent/arms-bootstrap-1.7.0-SNAPSHOT.jar`。
  - `Darms.licenseKey`：License key信息。本文示例展示从环境变量中获取License key。更多关于获取License Key的信息，请参见[获取License Key](https://help.aliyun.com/zh/arms/application-monitoring/user-guide/install-the-arms-agent-for-a-java-application-in-function-compute#section-k8t-icc-d2g)。
  - `Darms.appName`：ARMS应用程序名称。按照实际情况填写。

### 设置环境变量

- 设置环境变量`FC_EXTENSIONS_ARMS_LICENSE_KEY=xxxx`，值为License Key。获取License Key信息的具体步骤，请参见[获取License Key](https://help.aliyun.com/zh/arms/application-monitoring/user-guide/install-the-arms-agent-for-a-java-application-in-function-compute#section-k8t-icc-d2g)。
- 设置环境变量`FC_EXTENSION_ARMS=true`。
  
  添加该环境变量后，在一次函数调用结束时，不会立刻冻结函数实例，会等待10s再冻结函数实例，以确保ARMS Agent扩展成功上报日志。
  
  **
  
  **重要**
  
  函数计算在调用结束至冻结前的等待时长会产生费用，收费策略与实例调用阶段的计费逻辑相同。具体信息，请参见[产品计费](https://help.aliyun.com/zh/functioncompute/fc/product-overview/billing-fc/)。

## 前提条件

- 已创建自定义运行时函数，具体运行环境为Java 8、Java 11或Java 17。具体操作，请参见[创建函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/creating-a-web-function#section-b9y-zn1-5wr)。
- 已开通ARMS服务。具体操作，请参见[开通ARMS](https://help.aliyun.com/zh/arms/getting-started/activate-arms#concept-65257-zh)。

## 操作步骤

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com)，在左侧导航栏，选择**函数管理**>**函数列表**。
2. 在顶部菜单栏，选择地域，然后在**函数列表**页面，单击目标函数。
3. 在函数配置页面，选择**配置**页签。
4. 找到**高级配置**单击其右侧**编辑**，在高级配置面板找到层区域进行编辑，选择**+添加层**>**添加官方公共层**，添加与所选Java语言兼容的ArmsAgent层。
5. 在高级配置面板找到**环境变量**区域进行编辑，添加环境变量`FC_EXTENSION_ARMS=true`和`FC_EXTENSIONS_ARMS_LICENSE_KEY=xxxx`。
  
  具体操作，请参见[设置环境变量](#p-im4-1v0-gjx)。
6. 在函数代码页面的WebIDE中，创建Bootstrap文件，然后单击**部署代码**。
  
  具体操作，请参见[使用Bootstrap脚本作为启动命令](#p-rrt-a2v-ww0)。
  
  成功更新配置并部署代码后，您的函数将被添加到ARMS应用监控进行高性能管理。同时，ARMS监控将对您的服务进行计费。更多信息，请参见[计费概述](https://help.aliyun.com/zh/arms/application-monitoring/product-overview/billing-overview-1#concept-2121380)。

**

**重要**

- 当您的函数成功接入ARMS监控平台后，如果您需要查看对应监控信息，请确保ARMS监控平台和函数所属地域相同。
- 为了函数能够正常执行，请确保您的函数配置中，内存规格大于512 MB（ARMS大概占用300 MB内存）。

## 结果验证

当您成功将函数接入ARMS应用监控平台后，您可以在ARMS控制台查看接入的函数。

您也可以登录[ARMS控制台](https://arms.console.aliyun.com/#/home)，在左侧导航栏，选择**应用监控**>**应用列表**，然后单击目标应用名称，查看详细监控信息。更多信息，请参见[应用总览](https://help.aliyun.com/zh/arms/application-monitoring/user-guide/application-overview#concept-87109-zh)。

**

**说明**

目标应用的名称为Bootstrap脚本中的`appName`，默认值为`FC:{FunctionName}`。
