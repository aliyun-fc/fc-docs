# 如何安装我需要的FFmpeg版本？

函数计算运行环境内置了FFmpeg，如果此FFmpeg不能满足您的需求，您可以通过如下方式安装您需要的FFmpeg版本：

- 使用Web函数自定义容器镜像方式创建函数，您可以完全定制您的运行环境。
- 如果您使用内置运行时或自定义运行时创建函数，需先通过[FFmpeg](https://johnvansickle.com/ffmpeg/)下载amd64版本的FFmpeg，然后将其打包到代码包或层中。关于打包层的说明，请参见[构建层的ZIP包](https://help.aliyun.com/zh/functioncompute/fc/user-guide/create-a-custom-layer-1#section-jos-h78-3xb)。
  
  **
  
  **说明**
  
  压缩代码包前，请先执行`chmod +x ffmpeg`等命令，使FFmpeg具有可执行权限。
