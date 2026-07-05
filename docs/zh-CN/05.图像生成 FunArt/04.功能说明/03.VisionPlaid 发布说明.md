# VisionPlaid 发布说明

VisionPlaid 是阿里云基础软件团队推出的、面向视觉扩散模型（Diffusion Model）的高性能推理加速框架。本文介绍其首版发布内容、核心特性与性能表现，便于在 ComfyUI 与 FunArt 等场景中选型与使用。

## **版本动态**

- **2026-03-12**：首个正式版本发布。深度整合量化、并行与通信优化及多种注意力后端，提供对 ComfyUI 的原生支持，深度兼容 ComfyUI 节点式工作流；为**Qwen-Image**、**Qwen-Image-Edit**及**Wan2.1/2.2**系列提供推理加速，支持硬件包括 L20、RTX 4090、RTX 5090。

## **为什么选择 VisionPlaid？**

在现有推理方案中，VisionPlaid 主要提供以下四方面能力，便于在显存与速度之间取得更好平衡。

### **1. ComfyUI 序列并行加速（SP）**

- **不止于显存节省**：相较仅通过分布式 Offload 节省显存的方案（如 comfyui-multigpu），VisionPlaid 实现**序列并行（Sequence Parallelism, SP）**，在多卡协同下既能跑起大模型，也能明显缩短单图/单视频的生成时间。
- **端到端速度**：在并行模式下可同时开启 Async Offload，并与 4-bit 量化结合，单张大图或长视频的端到端（E2E）生成速度可接近硬件上限。

### **2. 原生 ComfyUI 兼容**

- **直接使用社区权重**：无需通过独立后端服务接管，即可复用现有 ComfyUI 生态与权重。
- **组件兼容**：作为 ComfyUI 内嵌方案，可继续使用各类自定义节点与插件，与 xDiT 等独立框架的迁移成本不同。

### **3. 智能内存与异步 Offload**

- 在 ComfyUI 既有内存管理之上，提供**异步加载/卸载（Async Load/Unload）**能力。推理进行的同时在后台准备下一阶段权重，从而支持在显存容量有限的情况下运行更大规模模型。

### **4. 架构易用性**

- **节点级接入**：在工作流中启用并行时，仅需**替换 KSampler 节点**即可接入加速。
- **Worker 管理**：切换 GPU 数量时，由系统自动销毁并重建 Worker，**无需重启 ComfyUI**即可生效。

## **核心特性**

VisionPlaid 通过软硬件协同优化，在尽量保持精度的前提下提升推理性能。

### **并行与通信**

- **SP 计算与通信重叠**：通过序列并行隐藏通信延迟，实现计算与通信的并发。
- **量化通信**：采用低位宽通信，减轻多卡/多节点带宽压力。

### **精度与量化**

- **Int4 / NVFP4**：原生支持低精度量化，在压缩显存占用的同时兼顾生成质量。
- **4-Step 蒸馏**：适配少步数蒸馏模型，支持秒级图像/视频生成。

### **架构与算子**

- **ComfyUI 原生集成**：在工作流中支持节点级并行推理。
- **多 Attention 后端**：支持 SageAttention、FlashAttention 与 SDPA，可在不重启的情况下切换。
- **异步 Offload**：按需加载/卸载权重，用计算流水掩盖 IO，支持超出单机显存的大模型推理。
- **算子与编译优化**：结合`torch.compile`与自定义融合算子，提升硬件利用率。

## **横向评测（Benchmarks）**

在相同测试设定下，VisionPlaid 在 Transformer 单步时间与端到端延迟上相对当前主流方案具备优势，以下数据供选型参考。

### **视频生成**

| 框架名称 | GPUs | Step Time | End-To-End Time | Speedup |
| --- | --- | --- | --- | --- |
| Diffusers | 1 | 24.03 s/it | 499.47 s | 1x |
| LightX2V | 1 | 20.41 s/it | 465.00 s | 1.07x |
| xDiT | 1 | 32.80 s/it | 670.23 s | - |
| FastVideo | 1 | 22.75 s/it | 466.43 s | 1.07x |
| SGL Diffusion | 1 | 15.41 s/it | 324.10 s | 1.5x |
| VisionPlaid | 1 | 14.98 s/it | 308.11 s | 1.6x |
| LightX2V | 2 | 13.01 s/it | 268.81 s | 1.8x |
| xDiT | 2 | OOM | - | - |
| FastVideo | 2 | 14.73 s/it | 306.28 s | 1.6x |
| SGL Diffusion | 2 | 12.57 s/it | 285.21 s | 1.8x |
| VisionPlaid | 2 | 8.74 s/it | 200.60 s | 2.5x |

**测试环境**：Wan 2.1 T2V 14B，4090，20 steps，81 frames，480P（480×848），SageAttention，BF16。
**说明**：xDiT 未接入 SageAttention，故未列出 Speedup；2 卡时 xDiT 因 CPU offload 与 parallel 冲突出现 OOM。

### **图片生成（BF16/FP8）**

| 框架名称 | 权重 | GPUs | Step Time | End-To-End Time | Speedup |
| --- | --- | --- | --- | --- | --- |
| Diffusers | bf16 | 1 | - | OOM | - |
| LightX2V | bf16 | 1 | 3.23 s/it | 65.63 s | 1x |
| LightX2V | fp8 | 1 | 1.62 s/it | 33.83 s | 1x |
| LightX2V | 4steps+fp8 | 1 | 0.81 s/it | 4.10 s | 1x |
| xDiT | bf16 | 1 | - | OOM | - |
| SGL Diffusion | bf16 | 1 | - | OOM | - |
| VisionPlaid | bf16 | 1 | 2.97 s/it | 60.95 s | 1.08x vs LightX2V |
| VisionPlaid | fp8 | 1 | 1.51 s/it | 30.73 s | 1.10x vs LightX2V |
| VisionPlaid | 4steps+fp8 | 1 | 0.71 s/it | 3.51 s | 1.17x vs LightX2V |

**测试环境**：Qwen-Image-2512，4090，20 steps 或 4 steps，1024×1024，SageAttention。
**说明**：4-step 使用 CFG=1.0；xDiT、SGL Diffusion 未支持 FP8。

### **图片生成（Int4 / 4steps+Int4）**

| 框架名称 | 权重 | GPUs | Step Time | End-To-End Time | Speedup* |
| --- | --- | --- | --- | --- | --- |
| ComfyUI | bf16 | 1 | 9.04 s/it | 188.39 s | 0.69x |
| ComfyUI | 4steps+bf16 | 1 | 4.38 s/it | 24.40 s | 0.56x |
| Nunchaku | int4 | 1 | 6.42 s/it | 129.46 s | 1x |
| Nunchaku | 4steps+int4 | 1 | 3.19 s/it | 13.73 s | 1x |
| VisionPlaid + default attention | int4 | 1 | 5.96 s/it | 121.65 s | 1.06x |
| VisionPlaid + default attention | 4steps+int4 | 1 | 2.84 s/it | 12.97 s | 1.06x |
| VisionPlaid + sage attention | int4 | 1 | 3.16 s/it | 64.92 s | 2.0x |
| VisionPlaid + sage attention | 4steps+int4 | 1 | 1.49 s/it | 7.24 s | 1.9x |
| VisionPlaid + default attention | int4 | 2 | 3.77 s/it | 77.07 s | 1.7x |
| VisionPlaid + default attention | 4steps+int4 | 2 | 1.97 s/it | 9.23 s | 1.5x |
| VisionPlaid + sage attention | int4 | 2 | 2.29 s/it | 47.17 s | 2.7x |
| VisionPlaid + sage attention | 4steps+int4 | 2 | 1.24 s/it | 6.04 s | 2.3x |

**测试环境**：Qwen-Image-Edit-2509，4090，20 steps 或 4 steps，1440×1920，ComfyUI 默认启动参数。
**说明**：4-step 使用 CFG=1.0；Speedup 以 Nunchaku 的 int4 与 4steps+int4 分别为基准；VisionPlaid 支持无重启切换 SageAttention，适合 GPU 数量或 workload 不固定的长时间运行场景（如阿里云 FC）。

## **操作入门**

- 在**FunArt**中直接使用 VisionPlaid 进行推理加速与多卡并行，可前往：[在FunArt中使用VisionPlaid](https://help.aliyun.com/zh/functioncompute/fc/use-visionplaid-in-funart)。
