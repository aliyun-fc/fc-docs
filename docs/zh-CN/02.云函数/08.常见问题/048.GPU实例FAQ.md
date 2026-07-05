# GPU实例FAQ

本文介绍使用GPU实例过程中可能遇到的问题，并提供对应的解决方案。

- [函数计算GPU实例的驱动和CUDA版本是什么?](#21629a1067n25)
- [执行时遇到CUFFT_INTERNAL_ERROR怎么办？](#0d10b2c08444q)
- [构建镜像时报错CUDA GPG Error如何解决？](#section-xgn-zw1-dy2)
- [为什么我的GPU实例规格显示的是g1？](#section-o4w-bn1-vzw)
- [为什么实例启动失败？](#section-q42-n0h-8if)
- [无法正常弹出GPU弹性实例，提示"ResourceExhausted"、"ResourceThrottled"如何处理？](#2c2f43bf62fvt)
- [GPU镜像大小限制是多少？](#section-wzb-j8z-3cp)
- [GPU镜像加速转换失败怎么办？](#section-td4-gx3-pan)
- [模型应该打在镜像里，还是与镜像分离？](#section-cnl-yuk-r5q)
- [如何做模型预热，有没有最佳实践？](#section-53u-u0a-azy)
- [GPU镜像启动报错“FunctionNotStarted”Function Instance health check failed on port xxx in 120 seconds怎么办？](#section-us6-1jq-7gi)
- [我的函数端到端延迟较大，并且波动很大，需要怎么处理？](#eceaf8b02106i)
- [无法找到NVIDIA驱动程序怎么办？](#e5a3beb783y5u)

## 函数计算GPU实例的驱动和CUDA版本是什么?

GPU实例涉及的组件版本主要分为以下两个部分：

- **驱动版本**：包含内核态驱动`nvidia.ko`、CUDA用户态驱动`libcuda.so`等。函数计算GPU实例所使用的驱动由NVIDIA提供，由函数计算平台负责部署。随着功能迭代、新卡型推出、BUG修复、驱动生命周期到期等原因，GPU实例所使用的驱动版本未来可能变化，请避免在容器镜像中添加驱动特定相关内容，更多内容，请参见[无法找到NVIDIA驱动程序怎么办？](#e5a3beb783y5u)。
- **CUDA Toolkit版本**：包含CUDA Runtime、cuDNN、cuFFT等。CUDA Toolkit版本由您在构建容器镜像时决定。

GPU驱动和CUDA Toolkit由NVIDIA发布，两者有一定的对应关系，细节信息请参见对应版本的[CUDA Toolkit Release Notes](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html)。

函数计算GPU目前使用的驱动版本为**580.95.05**，其对应的CUDA用户态驱动版本为**13.0**。为了最佳的兼容性支持，建议您使用的CUDA Toolkit最低版本为**11.8**，最高不超过平台提供的CUDA用户态驱动版本。

## 执行时遇到CUFFT_INTERNAL_ERROR怎么办？

目前已知CUDA 11.7中的cuFFT库存在前向兼容性问题，在较新的卡型中可能遇到上述错误，建议至少升级至CUDA 11.8版本。关于GPU卡型介绍，请参见[实例类型和规格](https://help.aliyun.com/zh/functioncompute/fc/product-overview/instance-types-and-specifications#section-mfv-5fb-ehw)。

以PyTorch为例，升级后，可以用以下代码片段来验证，无报错说明升级有效。

```
import torch out = torch.fft.rfft(torch.randn(1000).cuda())
```

## 构建镜像时报错CUDA GPG Error如何解决？

构建镜像时报错GPG error，具体信息如下。

```
W: GPG error: https://developer.download.nvidia.cn/compute/cuda/repos/ubuntu2004/x86_64 InRelease: The following signatures couldn't be verified because the public key is not available: NO_PUBKEY A4B469963BF863CC E: The repository 'https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64 InRelease' is not signed.
```

此时，您可以在Dockerfile文件的`RUN rm`命令行后面增加如下脚本，然后重新构建镜像。

```
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys A4B469963BF863CC
```

## 为什么我的GPU实例规格显示的是g1？

实例规格设置为g1等同于设置为fc.gpu.tesla.1。更多信息，请参见[实例规格](https://help.aliyun.com/zh/functioncompute/fc/product-overview/instance-types-and-specifications#section-mfv-5fb-ehw)。

## 为什么实例启动失败？

实例启动异常可能存在以下原因：

- 启动超时
  
  - 错误码："FunctionNotStarted"
  - 错误信息："Function instance health check failed on port XXX in 120 seconds"
  - 解决方案：检查应用启动逻辑，是否存在公网模型下载、10 GB以上大模型加载逻辑。建议优先完成Web Server启动，再执行模型加载逻辑。
- 已达到函数或地域级别的实例数量上限
  
  - 错误码："ResourceThrottled"
  - 错误信息："Reserve resource exceeded limit"
  - 解决方案：单个阿里云账号地域级别的GPU物理卡默认上限为30卡，实际数值以[配额中心](https://quotas.console.aliyun.com/products/fc/quotas)为准，如您有更高的物理卡需求，请前往[配额中心](https://quotas.console.aliyun.com/products/fc/quotas)申请。

## **无法正常弹出GPU弹性实例，提示"**ResourceExhausted**"、"**ResourceThrottled**"如何处理？**

由于GPU资源供应相对稀缺，受资源池水位波动的影响，可能导致无法及时弹出GPU弹性实例满足调用请求。如果需要可预期的资源交付，建议为函数配置最小实例数，提前锁定资源，详见[配置最小实例数弹性策略](https://help.aliyun.com/zh/functioncompute/fc/configure-launch-snapshot-and-auto-scaling-rules)。

## GPU镜像大小限制是多少？

镜像大小限制是针对压缩后的镜像，非压缩前的镜像。您可以在阿里云[容器镜像服务控制台](https://cr.console.aliyun.com/)查看压缩后镜像尺寸，也可以在本地执行命令`docker images`查询压缩前镜像尺寸。

通常情况下，压缩前尺寸小于20 GB的镜像可以正常部署到函数计算并使用。

## GPU镜像加速转换失败怎么办？

随着您的镜像尺寸增长，镜像加速转换耗时会同步的增长，可能会因为超时导致镜像加速转换失败。您可以通过在[函数计算控制台](https://fcnext.console.aliyun.com)编辑和保存函数配置的方式（无需实际调整参数），重新触发加速镜像的转换。

## 模型应该打在镜像里，还是与镜像分离？

如果您的模型文件较大、迭代频繁或随镜像发布时超过平台镜像大小限制，建议模型与镜像分离。如果选择模型与镜像分离的部署方式，可以将模型存储在NAS文件系统或OSS文件系统中，详情请参见[GPU实例模型存储最佳实践](https://help.aliyun.com/zh/functioncompute/fc/user-guide/gpu-instance-model-storage-best-practices/)。

## 如何做模型预热，有没有最佳实践？

建议在`/initialize`方法中进行模型预热，仅当`/initialize`方法完成后，模型才会真正接入生产流量。更多信息，请参见以下文档：

- [配置实例生命周期](https://help.aliyun.com/zh/functioncompute/fc/function-instance-lifecycle)
- [模型预热代码示例](https://github.com/devsapp/start-fc-gpu/blob/main/fc-http-gpu-inference-paddlehub-cv-ppocr/src/code/app.py#L23)

## GPU镜像启动报错“FunctionNotStarted”Function Instance health check failed on port xxx in 120 seconds怎么办？

- 问题原因：AI/GPU应用启动耗时过长，导致函数计算FC平台健康检查失败。其中导致AI/GPU应用启动耗时过长的常见原因是加载模型耗时过长，导致WebServer启动超时。
- 解决方案：
  
  - 不要在应用启动时从公网动态加载模型，建议将模型放置在镜像中，或者文件存储NAS中，就近加载模型。
  - 将模型初始化放置在`/initialize`方法中，优先完成应用启动。即WebServer启动后，再加载模型。
    
    **
    
    **说明**
    
    关于函数实例生命周期的详细信息，请参见[配置实例生命周期](https://help.aliyun.com/zh/functioncompute/fc/function-instance-lifecycle)。

## **我的函数端到端延迟较大，并且波动很大，需要怎么处理？**

1. 首先需要确认环境信息中镜像加速准备状态为可用。
2. 确认NAS文件系统的类型。如果您的函数需要从NAS文件系统中读取数据，如读取模型，为了保证性能，强烈建议使用通用型NAS的性能型，不推荐使用容量型。更多信息，请参见[通用型NAS](https://help.aliyun.com/zh/nas/product-overview/general-purpose-nas-file-systems#concept-61136-zh)。

## **无法找到**NVIDIA**驱动程序怎么办？**

通过`docker run --gpus all`命令指定容器，并使用`docker commit`方式构建应用镜像时，构建的镜像会携带本地NVIDIA驱动程序信息，这将导致镜像部署到函数计算后驱动程序无法正常挂载。此时，系统无法找到NVIDIA驱动程序。

为了解决以上问题，函数计算建议您使用Dockerfile的方式构建应用镜像。更多信息，请参见[dockerfile](https://docs.docker.com/build/building/packaging/#dockerfile)。

另外，请勿在镜像中添加驱动相关的组件，同时请您避免应用对特定的驱动版本产生依赖。例如，不要将提供CUDA Driver API的`libcuda.so`放入镜像中，此动态库与设备内核驱动版本强相关。镜像中的此类动态库不匹配可能导致应用因兼容性问题出现行为异常。

创建函数实例时，函数计算平台会预先将驱动相关的用户态组件注入到容器中，这些组件与平台提供的驱动版本相匹配。这也是NVIDIA Container Runtime等GPU容器虚拟化技术的行为，将驱动特定的任务交予平台资源提供方，从而最大化GPU容器镜像的环境适应能力。函数计算GPU实例所使用的驱动由NVIDIA提供。随着功能迭代、新卡型推出、BUG修复、驱动生命周期到期等原因，GPU实例所使用的驱动版本未来可能变化。

若您已经在使用NVIDIA Container Runtime等GPU容器虚拟化技术，请您避免使用`docker commit`命令创建镜像，此类镜像中会包含已注入的驱动相关组件。当您在函数计算平台使用此类镜像时，可能因组件版本与平台不匹配而产生未定义行为，如应用异常等。
