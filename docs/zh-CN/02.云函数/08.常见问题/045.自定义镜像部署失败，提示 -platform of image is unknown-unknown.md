# 自定义镜像部署失败，提示 "platform of image is unknown/unknown"

#### 问题现象

在函数计算（FC）控制台部署或更新自定义镜像时，任务失败并报错：

`镜像资源更新失败：invalid image, platform of image is unknown/unknown`

#### 问题原因

该问题通常是因为使用较新版本的 Docker（尤其是启用 Buildx 插件后）构建镜像时，默认开启了 Provenance Attestations 特性。这会导致生成的镜像清单（Manifest List）中包含一个平台类型为`unknown/unknown`的层（用于存储构建元数据），而部分运行环境无法识别此类多架构清单，导致校验失败。

#### 排查步骤

在本地终端执行以下操作，检查镜像的 Manifest 信息：

```
docker manifest inspect <您的镜像名称:标签>
```

如果在返回的 JSON 结果中，`platform`字段出现了`unknown/unknown`（如下图所示），即可确认是此原因。

```
{ "platform": { "architecture": "unknown", "os": "unknown" }}
```

#### 解决方案

在构建镜像时，显式关闭生成 provenance 信息。

**方法 A：在**`**docker build**`**命令中添加参数（推荐）**
在执行构建命令时增加`--provenance=false`参数：

```
docker build --platform=linux/amd64 --provenance=false -t <镜像名称:标签> .
```

**方法 B：使用 Buildx 时的完整命令**
如果您使用的是`docker buildx build`，请确保指定平台并关闭 provenance：

```
docker buildx build --platform linux/amd64 --provenance=false -t <镜像名称:标签> --push .
```

**方法 C：环境变量方式（全局生效）**
如果您在 CI/CD 环境中不便修改命令，可以尝试设置环境变量：
`export BUILDX_NO_DEFAULT_ATTESTATIONS=1`
