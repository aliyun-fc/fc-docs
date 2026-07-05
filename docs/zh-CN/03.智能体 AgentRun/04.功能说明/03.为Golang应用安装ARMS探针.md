# 为Golang应用安装ARMS探针

通过[Instgo](https://help.aliyun.com/zh/arms/application-monitoring/developer-reference/instgo-tool-introduction)编译 Golang 应用后，ARMS 可自动监控应用性能，并支持采集 LLM 调用次数、Token 消耗、Trace 链路及会话等 AI 业务指标。本文将介绍如何在 AgentRun 为自定义镜像部署的 Golang Agent 安装阿里云 ARMS 应用探针。

## **环境约束**

- 探针支持的 Golang 版本：1.18及以上版本
- 编译过程需要下载安装探针包，需要确保和公网或阿里云内网连通，且编译环境所在安全组已开放8080、8848、9990、80、443 的TCP出方向权限。

## 安装步骤

### 1、下载instgo工具

在`Dockerfile`构建阶段下载并安装instgo：

```
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories RUN apk add --no-cache wget RUN wget "http://arms-apm-cn-hangzhou.oss-cn-hangzhou.aliyuncs.com/instgo/instgo-linux-amd64" -O /usr/local/bin/instgo && \ chmod +x /usr/local/bin/instgo
```

### **2、处理依赖**

若项目使用`-mod=vendor`，请确保：

- `go.mod`包含`google.golang.org/protobuf`（直接或间接）；
- 在`main.go`中添加空导入以避免编译剔除：
  
  ```
  _ "google.golang.org/protobuf/proto" _ "google.golang.org/protobuf/runtime/protoimpl"
  ```
- 执行`go mod tidy && go mod vendor`同步依赖。

### 3、使用instgo编译

替换原生`go build`为`instgo go build`：

```
ENV GOPROXY=https://mirrors.aliyun.com/goproxy/,direct COPY go.mod go.sum ./ RUN go mod download COPY . . RUN instgo go build -ldflags="-w -s" -o /app/app main.go
```

提示：若使用较旧 Go 版本，建议在编译前通过`instgo set --licenseKey=xxx`或设置`ARMS_LICENSE_KEY`环境变量指定 LicenseKey，以确保下载匹配的探针版本。

### 4、配置运行时环境变量

必须设置以下四个变量：

- `ARMS_ENABLE=true`：启用探针；
- `ARMS_APP_NAME`：应用名称；
- `ARMS_REGION_ID`：地域 ID（如`cn-hangzhou`）；
- `ARMS_LICENSE_KEY`：从 ARMS 控制台获取的接入凭证。

AgentRun 控制台支持在部署 Agent 阶段定义环境变量，可不在此处 Dockerfile 中配置。

## 完整Dockerfile示例

**Dockerfile**

```
# 第一阶段：构建阶段 FROM mirrors-ssl.aliyuncs.com/golang:1.22-alpine AS builder # 设置工作目录 WORKDIR /app RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories # 安装必要的构建工具 RUN apk add --no-cache git ca-certificates tzdata wget # ╔═══════════════════════════════════════════════════════════════════════════╗ # ║ ARMS 探针配置 - 步骤 1: 下载工具 ║ # ╠═══════════════════════════════════════════════════════════════════════════╣ # ║ 下载并安装阿里云 ARMS Go 应用监控探针工具 instgo ║ # ║ instgo 是编译时插桩工具，会在编译阶段将监控代码注入到应用中 ║ # ╚═══════════════════════════════════════════════════════════════════════════╝ RUN wget "http://arms-apm-cn-hangzhou.oss-cn-hangzhou.aliyuncs.com/instgo/instgo-linux-amd64" -O /usr/local/bin/instgo && \ chmod +x /usr/local/bin/instgo ENV GOPROXY=https://mirrors.aliyun.com/goproxy/,direct # 复制 go.mod 和 go.sum 文件 COPY go.mod go.sum ./ # 下载依赖 RUN go mod download # 复制源代码 COPY . . # ╔═══════════════════════════════════════════════════════════════════════════╗ # ║ ARMS 探针配置 - 步骤 2: 使用 instgo 编译应用 ║ # ╠═══════════════════════════════════════════════════════════════════════════╣ # ║ 关键步骤：使用 instgo 替代原生 go build 命令进行编译 ║ # ║ ║ # ║ 与普通编译的区别： ║ # ║ 普通编译: go build -o app main.go ║ # ║ 探针编译: instgo go build -o app main.go ← 添加 instgo 前缀即可 ║ # ║ ║ # ║ 编译后的二进制文件已包含 ARMS 监控能力，运行时会自动上报监控数据 ║ # ╚═══════════════════════════════════════════════════════════════════════════╝ RUN instgo go build -ldflags="-w -s" -o /app/openai-demo-go-buildnoenv main.go # 第二阶段：运行阶段 FROM mirrors-ssl.aliyuncs.com/alpine:latest RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories # 设置时区为上海 RUN apk add --no-cache ca-certificates tzdata && \ cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \ echo "Asia/Shanghai" > /etc/timezone && \ apk del tzdata # 创建非root用户 RUN addgroup -g 1000 appuser && \ adduser -D -u 1000 -G appuser appuser # 设置工作目录 WORKDIR /app # 从构建阶段复制可执行文件 COPY --from=builder /app/openai-demo-go-buildnoenv . # 更改文件所有者 RUN chown -R appuser:appuser /app # 切换到非root用户 USER appuser # 暴露端口 EXPOSE 8000 # 健康检查 HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \ CMD wget --no-verbose --tries=1 --spider http://localhost:8000/ || exit 1 # 启动应用 CMD ["./openai-demo-go-buildnoenv"]
```

**main.go**

```
package main import ( "context" "fmt" "log" "net/http" "github.com/gin-gonic/gin" "github.com/sashabaranov/go-openai" ) var client *openai.Client // 在应用启动时初始化一次客户端 func initOpenAIClient() { config := openai.DefaultConfig("sk-ed8d03d6e**************") config.BaseURL = "https://dashscope.aliyuncs.com/compatible-mode/v1" client = openai.NewClientWithConfig(config) } // 单次调用大模型的原始接口 func callOpenAISingle(c *gin.Context) { ctx := context.Background() resp, err := client.CreateChatCompletion(ctx, openai.ChatCompletionRequest{ Model: "qwen-max", Messages: []openai.ChatCompletionMessage{ { Role: openai.ChatMessageRoleUser, Content: "Write a haiku about the girl who is looking at the sea.", }, }, }) if err != nil { log.Printf("Error calling OpenAI API: %v", err) c.JSON(http.StatusInternalServerError, gin.H{ "error": err.Error(), }) return } content := resp.Choices[0].Message.Content c.JSON(http.StatusOK, gin.H{ "data": content, }) } // ProcessLog 用于记录每一步的处理日志 type ProcessLog struct { Step int `json:"step"` Prompt string `json:"prompt"` Result string `json:"result"` } // MultiStepPoemResponse 用于返回最终结果 type MultiStepPoemResponse struct { FinalResult struct { Title string `json:"title"` Poem string `json:"poem"` } `json:"final_result"` ProcessLog []ProcessLog `json:"process_log"` } // 多步骤调用接口：一次外部请求，内部多次调用 func callOpenAIMultipleSteps(c *gin.Context) { ctx := context.Background() var processLog []ProcessLog // 封装调用函数 callLLM := func(prompt string) (string, error) { resp, err := client.CreateChatCompletion(ctx, openai.ChatCompletionRequest{ Model: "qwen-max", Messages: []openai.ChatCompletionMessage{ { Role: openai.ChatMessageRoleUser, Content: prompt, }, }, }) if err != nil { return "", err } return resp.Choices[0].Message.Content, nil } // --- 第 1 步：让大模型想一个关于"孤独的灯塔"的具体创意 --- log.Println("Step 1: Generating a creative idea...") prompt1 := "Give me a creative idea for a poem about a lonely lighthouse." creativeIdea, err := callLLM(prompt1) if err != nil { log.Printf("Error in Step 1: %v", err) c.JSON(http.StatusInternalServerError, gin.H{ "error": err.Error(), "process_log": processLog, }) return } processLog = append(processLog, ProcessLog{ Step: 1, Prompt: prompt1, Result: creativeIdea, }) log.Printf("Step 1 Result: %s\n", creativeIdea) // --- 第 2 步：基于上一步的创意，让大模型写一首短诗 --- log.Println("\nStep 2: Writing a poem based on the idea...") prompt2 := fmt.Sprintf("Based on this idea: '%s', write a short, four-stanza poem. And do not set the title for the poem.", creativeIdea) poem, err := callLLM(prompt2) if err != nil { log.Printf("Error in Step 2: %v", err) c.JSON(http.StatusInternalServerError, gin.H{ "error": err.Error(), "process_log": processLog, }) return } processLog = append(processLog, ProcessLog{ Step: 2, Prompt: prompt2, Result: poem, }) log.Printf("Step 2 Result:\n%s\n", poem) // --- 第 3 步：让大模型为生成的诗歌起一个标题 --- log.Println("\nStep 3: Creating a title for the poem...") prompt3 := fmt.Sprintf("Based on the following poem, suggest a compelling title:\n\n---\n%s\n---", poem) title, err := callLLM(prompt3) if err != nil { log.Printf("Error in Step 3: %v", err) c.JSON(http.StatusInternalServerError, gin.H{ "error": err.Error(), "process_log": processLog, }) return } processLog = append(processLog, ProcessLog{ Step: 3, Prompt: prompt3, Result: title, }) log.Printf("Step 3 Result: %s\n", title) // --- 最后，将所有结果结构化地返回给前端 --- var result MultiStepPoemResponse result.FinalResult.Title = title result.FinalResult.Poem = poem result.ProcessLog = processLog c.JSON(http.StatusOK, result) } func main() { // 初始化OpenAI客户端 initOpenAIClient() // 创建Gin路由器 r := gin.Default() // 定义路由 r.GET("/", callOpenAISingle) r.GET("/multi_step_poem", callOpenAIMultipleSteps) // 启动服务器 log.Println("Starting server on :8000...") if err := r.Run(":8000"); err != nil { log.Fatalf("Failed to start server: %v", err) } }
```

**go.mod**

```
module agentrun_o11b_demo/ArmsTraceGolangOpenAIDemo go 1.22 toolchain go1.22.0 require ( github.com/gin-gonic/gin v1.10.0 github.com/sashabaranov/go-openai v1.41.2 ) require ( github.com/bytedance/sonic v1.11.6 // indirect github.com/bytedance/sonic/loader v0.1.1 // indirect github.com/cloudwego/base64x v0.1.4 // indirect github.com/cloudwego/iasm v0.2.0 // indirect github.com/gabriel-vasile/mimetype v1.4.3 // indirect github.com/gin-contrib/sse v0.1.0 // indirect github.com/go-playground/locales v0.14.1 // indirect github.com/go-playground/universal-translator v0.18.1 // indirect github.com/go-playground/validator/v10 v10.20.0 // indirect github.com/goccy/go-json v0.10.2 // indirect github.com/json-iterator/go v1.1.12 // indirect github.com/klauspost/cpuid/v2 v2.2.7 // indirect github.com/leodido/go-urn v1.4.0 // indirect github.com/mattn/go-isatty v0.0.20 // indirect github.com/modern-go/concurrent v0.0.0-20180306012644-bacd9c7ef1dd // indirect github.com/modern-go/reflect2 v1.0.2 // indirect github.com/pelletier/go-toml/v2 v2.2.2 // indirect github.com/twitchyliquid64/golang-asm v0.15.1 // indirect github.com/ugorji/go/codec v1.2.12 // indirect golang.org/x/arch v0.8.0 // indirect golang.org/x/crypto v0.32.0 // indirect golang.org/x/net v0.34.0 // indirect golang.org/x/sys v0.29.0 // indirect golang.org/x/text v0.21.0 // indirect google.golang.org/protobuf v1.34.1 // indirect gopkg.in/yaml.v3 v3.0.1 // indirect )
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
  - **容器镜像实例****、****ACR 镜像仓库**：选择您刚刚上传的镜像。
4. **启动命令**：若已在 Dockerfile 中通过`CMD`配置，此处可留空。
5. **启动端口**：填入您应用实际监听的端口，例如`8000`。
6. **资源配置**：根据需要为 Agent 分配CPU和内存。
7. **配置探针环境变量（推荐）：**参考[步骤4](#a7d995a727d9u)配置ARMS探针所需环境变量。
8. **开启链路追踪**
  
  在高级配置中，找到并务必启用链路追踪开关。如果此开关关闭，所有探针配置将不会生效，应用无法上报任何监控数据。
9. 点击**开始部署**。

### 验证探针状态

部署成功 1–2 分钟后，进入Agent**详情**页 →**可观测性**页面，检查：

- “概览”中是否出现请求数、LLM 调用次数、Token 使用量；
- “Trace 列表”中是否包含`openai`或`dashscope`的调用链。

## 参考资料

- 探针安装运行的常见问题参考：[Go Agent 常见问题说明](https://help.aliyun.com/zh/arms/application-monitoring/user-guide/go-agent-faq)
- 探针性能开销数据可以参考：[Golang探针性能压测报告](https://help.aliyun.com/zh/arms/application-monitoring/developer-reference/golang-probe-performance-pressure-test-report)
- 探针支持的组件和框架可以参考：[ARMS应用监控支持的Go组件和框架](https://help.aliyun.com/zh/arms/application-monitoring/developer-reference/go-components-and-frameworks-supported-by-arms-application-monitoring)
