# 在FunArt中使用VisionPlaid

FunArt 对 VisionPlaid 做了深度集成，提供示例工作流与依赖，开箱即用。本文介绍如何创建 ComfyUI 项目并选择 VisionPlaid 加速引擎、运行示例工作流，以及 VisionPlaid ComfyUI 节点参数说明。

## 概述

FunArt 对 VisionPlaid 做了深度集成，包括集成 VisionPlaid 加速引擎、提供 VisionPlaid 示例工作流、示例工作流所需模型数据及依赖包，用户可开箱即用。VisionPlaid 在Qwen-Image-Edit-*、Qwen-Image-*和Wan2.2系列模型下具备SOTA的端到端推理性能。本文介绍从创建项目、运行示例工作流到节点参数说明的完整流程。性能数据与对比图详见[VisionPlaid 发布说明](https://help.aliyun.com/zh/functioncompute/fc/visionplaid-release-notes)。

## 前提条件

开始前，请确保满足以下条件：

- 已登录[FunArt 控制台](https://functionai.console.aliyun.com/funart/cn-hangzhou/explore)。
- **RAM 授权**：已开通函数计算及相关服务，并完成账号授权。详细步骤请参考[授权 RAM 用户使用图像生成项目](https://help.aliyun.com/zh/functioncompute/fc/authorize-ram-users-to-use-images-to-generate-projects)。
- **账户余额**：建议账户余额大于等于 100 元以获得更好体验。新用户可使用[试用套餐](https://help.aliyun.com/zh/functioncompute/fc/product-overview/trial-quota-1)以节省成本。

## 创建并配置使用 VisionPlaid 的 ComfyUI 项目

在 FunArt 中通过创建 ComfyUI 项目，并在创建流程的第三步将**加速引擎**选为**VisionPlaid**，即可使用 VisionPlaid 加速。步骤如下。

### 步骤 1：选择项目类型

在 FunArt 控制台页面导航栏，单击**项目**，单击**创建新项目**。在第一步「选择项目类型」中选择**ComfyUI**。

### 步骤 2：选择 GPU 卡型和规格

在第二步「选择 GPU 卡型和规格」中，按业务需求选择 GPU 卡型。使用 VisionPlaid 时建议选择**Ada-*系统**或**Blackwell 系列**，并配置 GPU 显存、vCPU、内存、磁盘等规格，单击**下一步**。

### 步骤 3：配置其他项目属性并选择 VisionPlaid

在第三步「配置其他项目属性」中配置以下内容：

- **项目名称**：必填，输入项目名称。
- **地域**：选择项目部署地域（如华东 1（杭州））。
- **加速引擎**：在**加速引擎**下拉框中选择**VisionPlaid**。该选项用于为 ComfyUI 配置加速工具，选择 VisionPlaid 后即可在项目中使用 VisionPlaid 进行推理加速。
- **存储配置**：按需选择（如「自动配置」表示使用 NAS 存储模型和插件等资源）。

配置完成后，单击**下一步**。

### 步骤 4：确认并完成创建

在第四步「确认并完成创建」页面，查看配置信息（项目名称、项目类型、地域、GPU 规格等）及部署资源（函数计算 FC、文件存储 NAS、日志服务 SLS 等）的计费说明，确认无误后单击**确认部署**。系统将开始部署，页面提示「正在准备项目（3～5 分钟），部署阶段不会产生 GPU 费用」。部署完成后即可进入项目开发阶段，使用工作站进行出图与调试。

**

**重要**

GPU 采用按量计费，界面预估费用仅供参考，以实际使用为准。使用完毕后请及时关闭工作空间以停止计费。

## 项目开发与使用

项目创建并部署完成后，可进入项目详情页进行开发与出图。可参考[创建 ComfyUI 项目快速入门](https://help.aliyun.com/zh/functioncompute/fc/quick-start-comfyui)中的工作站与出图流程。

### 运行示例工作流

在打开的项目页面中，选择**项目开发**>**工作站**>**Workflows**，可看到 FunArt 已内置的 VisionPlaid 示例工作流。

选择要运行的工作流，单击右上角**Run**按钮即可开始推理。

### VisionPlaid ComfyUI 节点介绍

以下为 VisionPlaid 在 ComfyUI 工作流中的主要节点及参数说明。

#### VisionPlaid Load Diffusion Model

- **unet_name**：要加载的模型权重，与 ComfyUI 的 Load Diffusion Model 一致。若使用 W4A4 量化，需在此指定对应权重；若开启 4-step 优化，可下载 4-step 优化专用权重。
- **weight_dtype**（量化类型）：**default**与 ComfyUI 的 Load Diffusion Model 一致；**int4**为 W4A4 的 int4 量化；**nvfp4**为 W4A4 的 nvfp4 量化；**其他**与 ComfyUI 的 Load Diffusion Model 一致。

#### Diffusion Boost V1

Diffusion Boost V1 是控制和配置推理加速的统一入口。

- **enable_compile**：开启或关闭编译，使用 torch.compile 编译 transformer 可优化算子以提升性能。
- **attn_type**（Attention 类型）：当前支持`default`、`sage`、`flash`。default 跟随 ComfyUI 所用 Attention；flash 需自行安装 FlashAttention；sage 使用 SageAttention（bitforge 版本已内置，无需单独安装）。
- **enable_fbcache**、**residual_diff_threshold**、**cache_start**：当前版本尚未支持。
- **enable_offload**：开启自动 offload transformer 权重，可缓解大图时 VAE decode 占用内存过高的问题，避免因 transformer unload 带来的性能损失。
- **num_blocks_on_gpu**：开启自动 offload 时，控制常驻 GPU 的 transformer block 数量。减小该值可降低与 VAE 抢占内存的概率；增大该值有时可提升性能，可根据图片大小调试。

**

**重要**

第一次运行可能需要编译，耗时较长，多跑几次后性能可达最佳。

#### Parallel KSampler

除与 ComfyUI 一致的**model**、**seed**、**steps**、**cfg**、**sampler_name**、**scheduler**、**positive**、**negative**、**latent_image**、**denoise**等参数外，VisionPlaid 提供：

- **num_gpus**：多卡并行的卡数。num_gpus=1 时为单卡推理；num_gpus>1 时开启多卡序列并行，并启用通信掩盖（overlap）以降低通信开销。

- **进入项目**：在项目列表中单击已创建且已配置 VisionPlaid 加速引擎的 ComfyUI 项目，进入项目详情。
- **使用工作站**：在**项目开发**页签下，使用**工作站**配置模型、工作流及参数，设置提示词并执行工作流完成出图。
- **文件管理**：在**文件管理**页签中可查看输入输出文件及模型等资源。

## 发布线上服务（可选）

若需将已配置 VisionPlaid 的 ComfyUI 项目发布为线上 API 供外部调用，可在**线上服务**中完成发布与配置管理。操作步骤详见：[为 ComfyUI 项目发布线上服务](https://help.aliyun.com/zh/functioncompute/fc/publish-online-service-for-comfyui-project)。

**

**重要**

请勿在函数计算控制台直接修改由 FunArt 创建的函数配置，避免被下次发布覆盖。

## 相关文档

- [VisionPlaid 发布说明](https://help.aliyun.com/zh/functioncompute/fc/visionplaid-release-notes)
- [创建 ComfyUI 项目快速入门](https://help.aliyun.com/zh/functioncompute/fc/quick-start-comfyui)（可参考 FunArt 控制台通用操作）
- [为 ComfyUI 项目发布线上服务](https://help.aliyun.com/zh/functioncompute/fc/publish-online-service-for-comfyui-project)
