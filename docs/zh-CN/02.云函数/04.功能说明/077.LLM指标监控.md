# LLM指标监控

函数计算支持对 GPU 函数中的 LLM 推理服务进行指标监控，可在控制台查看请求状态、Token 吞吐量、首 Token 延迟等数据，帮助您监控服务运行情况并优化性能。

## **前提条件**

- 已创建 GPU 函数，且使用 vLLM 或 SGLang 推理框架。
- 已开启日志服务（日志监控）。

## **使用限制**

- LLM 指标监控仅适用于 GPU 函数。
- 日志监控的**配置方式**需选择**自定义配置**，自动配置模式下无法开启 LLM 指标。
- SGLang 需在启动命令中显式添加`--enable-metrics`参数；vLLM 默认开启指标能力。

## **开启 LLM 指标**

### **新建函数时开启**

新建函数时，可按以下方式开启 LLM 指标监控：

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com/)，在页面顶部选择**地域**。
2. 在左侧菜单选择**函数管理**>**函数**，在右侧单击**创建函数**。
3. 在打开的**选择最适合你的函数类型**页面，选择**GPU 函数**，单击**创建{title}**。
4. 在**创建{title}**页面，找到**高级配置**下的**日志监控、链路追踪**部分，将**配置方式**选择为**自定义配置**，将**LLM 指标**选择为**打开**。
5. 其他配置与[创建 GPU 函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/creating-a-gpu-function/)中的说明相同，按需配置后单击**创建**。

**

**说明**

指标需在实例启动运行后才开始采集；若使用 SGLang，需在启动命令中添加`--enable-metrics`。

完成上述配置后，函数的 LLM 指标监控即已开启。

### **已有函数开启**

在已有函数的场景，可以通过以下方式开启 LLM 指标配置：

1. 在函数**配置**页面，找到**高级配置**部分，单击右上角**编辑**，打开高级配置编辑页面。
2. 在**日志**区域，将**LLM 指标**选择为打开，单击**部署**。
3. 等实例轮转完毕、新实例创建出来之后，即可在函数的**监控指标**页面看到 LLM 指标。

**

**说明**

由于推理框架实现上的差异，vLLM 默认开启 LLM 指标能力，SGLang 需要通过配置启动参数`--enable-metrics`显式开启。

## **查看 LLM 指标**

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com/)，在页面顶部选择**地域**。
2. 在左侧导航栏选择**函数管理**>**函数**，单击目标函数名称。
3. 在函数详情页，单击**监控指标**页签。
4. 单击**LLM 指标**子页签，查看各项指标数据。图表支持悬停查看详细数值。

**

**说明**

如果 LLM 指标未开启，页面会显示提示信息并提供快捷链接引导您到配置页面开启。

## **指标说明**

### **vLLM 指标**

vLLM 支持如下指标：

| 指标名称 | 说明 |
| --- | --- |
| **Requests Status** | 请求状态（Running 运行中、Waiting 等待中、Swapped 已换出） |
| **Token Throughput (tokens/sec)** | Token 吞吐量（tokens/秒） |
| **Request Completion Status** | 请求完成状态 |
| **Time to First Token (seconds)** | 首 Token 延迟（秒），从请求开始到首个 Token 输出的耗时 |
| **E2E Request Latency (seconds)** | 端到端请求延迟（秒） |
| **Queue Time (seconds)** | 队列时间（秒） |
| **Inference Time (seconds)** | 推理时间（秒） |
| **Prefill Time (seconds)** | 预填充时间（秒） |
| **Decode Time (seconds)** | 解码时间（秒） |
| **Processed Prefill Tokens** | 已处理的预填充 Token 数 |
| **Processed Generation Tokens** | 已处理的生成 Token 数 |
| **Request Parameters** | 请求参数 |

### **SGLang 指标**

SGLang 支持如下指标：

| 指标名称 | 说明 |
| --- | --- |
| **Requests Num** | 请求数量 |
| **Token Throughput (tokens/sec)** | Token 吞吐量（tokens/秒） |
| **Time to First Token (seconds)** | 首 Token 延迟（秒），从请求开始到首个 Token 输出的耗时 |
| **E2E Request Latency** | 端到端请求延迟 |
| **Cache Hit Rate (%)** | KV Cache 命中率（%） |
| **Used Tokens Num** | 已使用 Token 数 |
| **Token Usage (%)** | Token 使用率（%） |

部分指标支持分位统计：

例如，vLLM 的 Time to First Token (seconds)、E2E Request Latency (seconds)、Queue Time (seconds)、Inference Time (seconds)、Prefill Time (seconds)、Decode Time (seconds)、Processed Prefill Tokens、Processed Generation Tokens 等指标，以及 SGLang 的 Time to First Token (seconds)、E2E Request Latency 等指标。

## **相关文档**

- [创建 GPU 函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/creating-a-gpu-function/)：使用容器镜像方式创建 GPU 函数的完整步骤。
- [LLM 推理模型服务指标监控集成方案](https://help.aliyun.com/zh/functioncompute/fc/user-guide/integrating-prometheus-metric-monitoring-for-llm-inference-service-in-function-compute)：将 LLM 指标对接到 ARMS Prometheus，实现自定义可视化与告警。
