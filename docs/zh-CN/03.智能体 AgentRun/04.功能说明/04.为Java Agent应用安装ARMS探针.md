# 为Java Agent应用安装ARMS探针

为 Java 应用安装 ARMS 探针后，可查看应用拓扑、调用链路、异常事务、慢事务和 SQL 分析等监控数据。对于 Agent 等 LLM 应用，探针还可采集大模型调用次数、Token 使用量、Trace 数、会话数等 AI 业务指标。本文介绍如何为 Java 应用手动安装探针。

## **环境约束**

- 网络要求：构建环境需能访问公网或阿里云内网，并开放 TCP 出方向端口：80、443、8080、8848、9092、9093、9990；
- JDK 版本：支持 JDK 1.8、11、17 和 21；
- 内存要求：JVM 最大堆内存需大于 256 MB。

**

**重要**

LLM 监控功能需使用 ARMS 探针 4.6.0 及以上版本。当前 LTS 版本（如 4.4.2）不支持该能力，须手动下载指定版本探针。

## 安装步骤

### 1、下载并解压探针

从[ARMS 控制台探针下载页](https://arms.console.aliyun.com/#/tracing/agentList/cn-hangzhou?tab=java)获取`AliyunJavaAgent.zip`（≥4.6.0），置于项目根目录。

在`Dockerfile`的运行阶段解压探针：

```
COPY AliyunJavaAgent.zip /tmp/AliyunJavaAgent.zip RUN apk add --no-cache unzip && \ unzip /tmp/AliyunJavaAgent.zip -d /opt/ && \ rm -f /tmp/AliyunJavaAgent.zip
```

### 2、配置ARMS环境变量

ARMS 探针运行需要以下三个环境变量：

- `ARMS_APP_NAME`：ARMS 控制台中显示的应用名称；
- `ARMS_LICENSE_KEY`：应用接入凭证，可通过[列出LicenseKey](https://help.aliyun.com/zh/arms/application-monitoring/developer-reference/api-arms-2019-08-08-describetracelicensekey-apps)获取；
- `ARMS_REGION_ID`：可观测数据上报的地域。

如需在不同应用中复用同一 Dockerfile，可在 AgentRun 控制台部署 Agent 时配置环境变量，无需在 Dockerfile 中硬编码。

### 3、启用探针

通过`JAVA_TOOL_OPTIONS`加载 Java Agent：

```
ENV JAVA_TOOL_OPTIONS="-javaagent:/opt/AliyunJavaAgent/aliyun-java-agent.jar"
```

### 4、启动应用

在启动命令中通过系统属性传递配置：

```
ENTRYPOINT ["sh", "-c", "java -Darms.licenseKey=${ARMS_LICENSE_KEY} -Darms.appName=${ARMS_APP_NAME} -Daliyun.javaagent.profileId=${ARMS_REGION_ID} -jar app.jar"]
```

**

**说明**

若`ARMS_LICENSE_KEY`为空，探针将静默失效，不影响应用正常运行。

## 完整 Dockerfile 示例

Dockerfile

```
# 多阶段构建 Dockerfile for OpenAI Demo Java with ARMS Agent # 支持阿里云 ARMS 应用监控 # 第一阶段：构建应用 FROM maven:3.9-eclipse-temurin-17 AS builder WORKDIR /build # 复制 pom.xml 并下载依赖 COPY pom.xml . RUN mvn dependency:go-offline -B # 复制源代码并构建 COPY src ./src RUN mvn clean package -DskipTests -B # 第二阶段：运行应用并安装 ARMS 探针 FROM eclipse-temurin:17-jre-alpine WORKDIR /app # ╔═══════════════════════════════════════════════════════════════════════════╗ # ║ ARMS 探针配置 - 步骤 1: 复制探针包 ║ # ╠═══════════════════════════════════════════════════════════════════════════╣ # ║ 将预先下载的 ARMS Java Agent 探针包复制到镜像中 ║ # ║ 探针包需要手动下载并放置到项目根目录 ║ # ║ 下载地址: https://arms.console.aliyun.com/#/tracing/agentList/cn-hangzhou?tab=java ║ # ╚═══════════════════════════════════════════════════════════════════════════╝ COPY AliyunJavaAgent.zip /tmp/AliyunJavaAgent.zip # ╔═══════════════════════════════════════════════════════════════════════════╗ # ║ ARMS 探针配置 - 步骤 2: 解压探针 ║ # ╠═══════════════════════════════════════════════════════════════════════════╣ # ║ 将探针包解压到 /opt/AliyunJavaAgent/ 目录 ║ # ║ 解压后包含 aliyun-java-agent.jar 等文件 ║ # ║ 清理临时压缩包以减小镜像体积 ║ # ╚═══════════════════════════════════════════════════════════════════════════╝ RUN unzip /tmp/AliyunJavaAgent.zip -d /opt/ && \ rm -f /tmp/AliyunJavaAgent.zip # 复制构建产物 COPY --from=builder /build/target/OpenAI-Demo-Java-*.jar app.jar # 暴露端口 EXPOSE 8080 # ╔═══════════════════════════════════════════════════════════════════════════╗ # ║ ARMS 探针配置 - 步骤 3: 配置 ARMS 环境变量 ║ # ╠═══════════════════════════════════════════════════════════════════════════╣ # ║ ARMS_LICENSE_KEY: ARMS 许可证密钥，用于应用认证和数据上报 ║ # ║ ARMS_APP_NAME: 应用名称，在 ARMS 控制台中显示的应用标识 ║ # ║ ARMS_REGION_ID: 可观测数据上报的地域 ║ # ╚═══════════════════════════════════════════════════════════════════════════╝ ENV ARMS_LICENSE_KEY="hc4fs1*****@d2fb***********" ENV ARMS_APP_NAME="OpenAI-Demo-Java-1112" ENV ARMS_REGION_ID={RegionId} # ╔═══════════════════════════════════════════════════════════════════════════╗ # ║ ARMS 探针配置 - 步骤 4: 配置 JAVA_TOOL_OPTIONS启用 ARMS 探针 ║ # ╠═══════════════════════════════════════════════════════════════════════════╣ # ║ JAVA_TOOL_OPTIONS 是 JVM 的标准环境变量，会在 JVM 启动时自动读取 ║ # ║ 通过 -javaagent 参数加载 ARMS 探针，实现应用性能监控和链路追踪 ║ # ║ 探针将自动收集应用的性能指标、调用链路、异常信息等数据 ║ # ╚═══════════════════════════════════════════════════════════════════════════╝ ENV JAVA_TOOL_OPTIONS="-javaagent:/opt/AliyunJavaAgent/aliyun-java-agent.jar" # 检查环境变量配置 RUN echo "JAVA_TOOL_OPTIONS: ${JAVA_TOOL_OPTIONS}" # ╔═══════════════════════════════════════════════════════════════════════════╗ # ║ ARMS 探针配置 - 步骤 5: 启动应用 ║ # ╠═══════════════════════════════════════════════════════════════════════════╣ # ║ 通过 -D 系统属性传递 ARMS 配置到探针 ║ # ║ 探针会自动注入到应用，监控应用的运行状态和性能指标 ║ # ║ 如果 ARMS_LICENSE_KEY 为空，探针不会生效但不影响应用正常运行 ║ # ╚═══════════════════════════════════════════════════════════════════════════╝ ENTRYPOINT ["sh", "-c", "java -Darms.licenseKey=${ARMS_LICENSE_KEY} -Darms.appName=${ARMS_APP_NAME} -Daliyun.javaagent.profileId=${ARMS_REGION_ID} -jar app.jar"]
```

**pom.xml**

```
<?xml version="1.0" encoding="UTF-8"?> <project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd"> <modelVersion>4.0.0</modelVersion> <parent> <groupId>org.springframework.boot</groupId> <artifactId>spring-boot-starter-parent</artifactId> <version>3.5.7</version> <relativePath/> <!-- lookup parent from repository --> </parent> <groupId>com.example</groupId> <artifactId>OpenAI-Demo-Java</artifactId> <version>0.0.1-SNAPSHOT</version> <name>OpenAI-Demo-Java</name> <description>Demo project for Spring Boot</description> <url/> <licenses> <license/> </licenses> <developers> <developer/> </developers> <scm> <connection/> <developerConnection/> <tag/> <url/> </scm> <properties> <java.version>17</java.version> </properties> <dependencies> <dependency> <groupId>org.springframework.boot</groupId> <artifactId>spring-boot-starter-web</artifactId> </dependency> <dependency> <groupId>org.springframework.boot</groupId> <artifactId>spring-boot-starter-test</artifactId> <scope>test</scope> </dependency> <!-- OpenAI Java SDK --> <!-- <dependency> <groupId>com.openai</groupId> <artifactId>openai-java</artifactId> <version>2.6.0</version> </dependency> --> <dependency> <groupId>com.openai</groupId> <artifactId>openai-java-spring-boot-starter</artifactId> <version>4.7.1</version> </dependency> </dependencies> <build> <finalName>OpenAI-Demo-Java</finalName> <plugins> <plugin> <groupId>org.springframework.boot</groupId> <artifactId>spring-boot-maven-plugin</artifactId> </plugin> </plugins> </build> </project>
```

OpenAiDemoJavaApplication.java

```
package com.example.OpenAI_Demo_Java; import com.openai.client.OpenAIClient; import com.openai.client.okhttp.OpenAIOkHttpClient; import com.openai.models.chat.completions.ChatCompletion; import com.openai.models.chat.completions.ChatCompletionCreateParams; import org.springframework.beans.factory.annotation.Value; import org.springframework.boot.SpringApplication; import org.springframework.boot.autoconfigure.SpringBootApplication; import org.springframework.context.annotation.Bean; import org.springframework.web.bind.annotation.GetMapping; import org.springframework.web.bind.annotation.RestController; /** * OpenAI Demo - 阿里云千问调用示例 * * 使用方法: * 1. 配置 application.properties 中的 dashscope.api.key * 2. 运行应用: ./mvnw spring-boot:run * 3. 访问接口: curl http://localhost:8080/ */ @SpringBootApplication @RestController public class OpenAiDemoJavaApplication { @Value("${dashscope.api.key:sk-ed8d03d6e7*****************}") private String apiKey; private OpenAIClient client; public static void main(String[] args) { SpringApplication.run(OpenAiDemoJavaApplication.class, args); } /** * 初始化 OpenAI 客户端 */ @Bean public OpenAIClient openAIClient() { // 优先使用配置文件中的 API Key，如果没有则使用环境变量 String key = apiKey.isEmpty() ? System.getenv("DASHSCOPE_API_KEY") : apiKey; if (key == null || key.isEmpty()) { throw new IllegalStateException("API Key 未配置！请在 application.properties 中设置 dashscope.api.key"); } client = OpenAIOkHttpClient.builder() .apiKey(key) .baseUrl("https://dashscope.aliyuncs.com/compatible-mode/v1") .build(); return client; } /** * HTTP 接口: GET / * 向大模型发送问题并返回响应 */ @GetMapping("/") public String chat() { try { // 构建请求参数 ChatCompletionCreateParams params = ChatCompletionCreateParams.builder() .addUserMessage("写一首关于森林的绯句") .model("qwen-plus") .build(); // 调用 API ChatCompletion response = client.chat().completions().create(params); // 提取响应内容 String content = response.choices().get(0).message().content().orElse("无响应"); return String.format("问题: 写一首关于森林的绯句\n\n回答: %s", content); } catch (Exception e) { return "错误: " + e.getMessage(); } } }
```

## 部署与验证

### **构建并上传镜像**

将包含探针的 Dockerfile 构建成镜像，并上传至[容器镜像服务ACR](https://cr.console.aliyun.com/cn-hangzhou/instances)或其他可访问的镜像仓库。

```
# 示例：将镜像上传至阿里云 ACR # 1. 为镜像添加标签 docker tag {本地镜像TAG} registry.cn-hangzhou.aliyuncs.com/{您的ACR命名空间}/{您的ACR仓库名}:{镜像版本号} # 2. 上传镜像 docker push registry.cn-hangzhou.aliyuncs.com/{您的ACR命名空间}/{您的ACR仓库名}:{镜像版本号}
```

### **在 AgentRun中部署Agent并配置探针**

1. 登录[AgentRun控制台](https://fcnext.console.aliyun.com/agent-run/cn-hangzhou/agent/runtime/agent-list)，在**Agent 运行时**页签下，点击**创建 Agent**。
2. 选择**通过代码创建**，并填写**Agent名称**和**功能描述**。
3. 在**代码配置**部分，配置如下：
  
  - **代码来源**：选择**容器镜像**。
  - **容器镜像实例、****ACR 镜像仓库**：选择您刚刚上传的镜像。
4. **启动命令**：若已在 Dockerfile 中通过`CMD`配置，此处可留空。
5. **启动端口**：填入您应用实际监听的端口，例如`8000`。
6. **资源配置**：根据需要为 Agent 分配CPU和内存。
7. **配置探针环境变量（推荐）：**参考[步骤2](#285c2a8244s3s)配置`ARMS_APP_NAME`、`ARMS_LICENSE_KEY`、`ARMS_REGION_ID`三个环境变量。
8. **开启链路追踪**：在高级配置中启用链路追踪开关。
  
  **
  
  **警告**
  
  如果链路追踪开关未开启，所有探针配置将不生效，应用无法上报监控数据。
9. 点击**开始部署**。

### 验证探针状态

部署成功 1–2 分钟后，进入 Agent**详情**页 →**可观测性**页面，检查：

- “概览”中是否出现请求数、LLM 调用次数、Token 使用量；
- “Trace 列表”中是否包含`openai`或`dashscope`的调用链。

## **参考资料**

- 探针版本说明：[探针（Java Agent）版本说明](https://help.aliyun.com/zh/arms/application-monitoring/user-guide/java-agent-release-note)
- 探针支持的组件和框架：[ARMS应用监控支持的Java组件和框架](https://help.aliyun.com/zh/arms/application-monitoring/developer-reference/java-components-and-frameworks-supported-by-arms)
- 探针性能开销数据：[4.x版本Java探针性能压测报告](https://help.aliyun.com/zh/arms/application-monitoring/developer-reference/4-x-java-agent-performance-test-report)
