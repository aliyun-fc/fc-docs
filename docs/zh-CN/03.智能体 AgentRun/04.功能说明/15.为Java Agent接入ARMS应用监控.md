# 为Java Agent接入ARMS应用监控

AgentRun 自定义运行时 Agent 支持接入阿里云 ARMS 应用监控，为常见 AI 应用框架提供应用监控能力。接入 ARMS 探针后，可以查看 AI 应用的大模型调用次数、Token 使用次数、Trace 数、会话数等信息。本文介绍如何为自定义运行时 Java Agent 接入 ARMS 应用监控。

## **前提条件**

- 已开通 ARMS 服务。具体操作请参见[开通ARMS](https://help.aliyun.com/zh/arms/getting-started/activate-arms#concept-65257-zh)。
- Java 版本选择自定义运行时中的Java 8、Java 11、Java 17和Java 21。

**

**说明**

与"自定义镜像部署"方案不同，本方案无需修改 Dockerfile 或构建镜像，所有配置均通过 AgentRun 控制台完成，更适合快速迭代和轻量级部署场景。

## **配置步骤**

登录[AgentRun 控制台](https://fcnext.console.aliyun.com/agent-run/cn-hangzhou/agent/runtime/agent-list)。

### **1、设置探针环境变量**

在 Agent 运行时**详情**页面，选择**概览**页签，单击**编辑配置**，添加以下**环境变量**：

```
ARMS_APP_NAME={AgentName} ARMS_LICENSE_KEY={LicenseKey} ARMS_REGION_ID={RegionId}
```

变量含义说明：

- **ARMS_APP_NAME**：Agent 名称，用于在 ARMS 应用监控中标识当前应用。
- **ARMS_LICENSE_KEY**：ARMS 应用接入凭证，可通过 OpenAPI 获取，具体方法参见[列出LicenseKey](https://help.aliyun.com/zh/arms/application-monitoring/developer-reference/api-arms-2019-08-08-describetracelicensekey-apps)。
- **ARMS_REGION_ID**：可观测数据上报的地域。

### **2、修改启动命令**

**方式一：使用**`**JAVA_TOOL_OPTIONS**`**环境变量**

在环境变量中添加`JAVA_TOOL_OPTIONS`，该变量的值会在 JVM 启动时自动拼接到启动命令中。

```
JAVA_TOOL_OPTIONS="-javaagent:/opt/AliyunJavaAgent/aliyun-java-agent.jar -Darms.licenseKey=${ARMS_LICENSE_KEY} -Darms.appName=${ARMS_APP_NAME} -Daliyun.javaagent.profileId=${ARMS_REGION_ID}"
```

**方式二：配置启动脚本，使用数组来存储Java启动参数**

ARMS 接入需要添加 4 个启动参数，考虑到启动命令较为复杂，建议通过配置启动脚本`bootstrap`来启动。

示例代码如下：

```
#!/bin/bash set -eo pipefail # 1. 设置ARMS应用名称 # 如果ARMS_APP_NAME环境变量存在且不为空，则使用其值；否则使用默认值。 appName="${ARMS_APP_NAME:-Custom_Java_Arms_Demo}" echo "appName: ${appName}" # 使用数组来存储Java启动参数，这是处理参数的最佳实践 java_opts=() # 2. 添加ARMS参数 if [[ -n "${ARMS_LICENSE_KEY}" ]]; then echo "ARMS_LICENSE_KEY is set: ${ARMS_LICENSE_KEY}, enabling ARMS agent." # 使用公共层的ARMS程序路径 java_opts+=("-javaagent:/opt/AliyunJavaAgent/aliyun-java-agent.jar") java_opts+=("-Darms.licenseKey=${ARMS_LICENSE_KEY}") java_opts+=("-Darms.appName=${appName}") java_opts+=("-Daliyun.javaagent.profileId=${ARMS_REGION_ID}") else echo "Warning: ARMS_LICENSE_KEY not set. ARMS agent will not be enabled." fi # 3. 启动应用程序 # 添加其他固定的Java参数 java_opts+=("-Dserver.port=8000") echo "Final Java command: exec java ${java_opts[*]} -jar /code/target/OpenAI-Demo-Java.jar" exec java "${java_opts[@]}" \ -jar /code/target/OpenAI-Demo-Java.jar
```

设置文件权限为可执行权限（终端窗口执行命令`chmod +x bootstrap`）。

在 Agent 运行时**详情**页面，单击**编辑配置**，修改**启动命令**的值为启动脚本`/bootstrap`。

## **验证接入**

1. 保存配置并更新 Agent。
2. 发起几次业务调用。
3. 约 1 分钟后，前往以下任一位置查看数据：
  
  - **可观测**
  -

若能看到调用链、Token 消耗、LLM 调用次数等数据，即表示接入成功。
