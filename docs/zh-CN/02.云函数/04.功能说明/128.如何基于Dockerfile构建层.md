# 如何基于Dockerfile构建层

函数计算提供多种构建层的方式，对于不包含动态链接库的依赖（例如纯Python库），可直接使用控制台在线安装依赖的方式或使用本地构建的方式构建层。对于依赖中包含动态链接库，或者本地环境与函数计算的运行时环境不兼容的情况，不支持通过控制台或本地构建的方式构建层，只能基于Dockerfile构建层。本文以Node.js安装Puppeteer依赖为例，介绍如何基于Dockerfile构建层。

## 注意事项

构建层时，各个语言的依赖库建议按照页面[创建自定义层](https://help.aliyun.com/zh/functioncompute/fc/user-guide/create-a-custom-layer-1)的说明打包到层ZIP包的指定目录下。例如，Python库打包到层ZIP包的`/python`目录下。如果依赖库中包含动态链接库，建议将动态链接库放到层ZIP包的`/lib`目录下，上传到函数计算运行时环境后，会自动解压到`/opt/lib`目录。使用内置运行时，会默认将目录`/opt/lib`添加到路径LD_LIBRARY_PATH，而使用自定义运行时，需要手动添加。

## 构建Puppeteer层

### 步骤一：准备Dockerfile文件

示例如下。

```
# 指定构建镜像的基础镜像，推荐使用build-latest的镜像进行构建。 # 在本地构建层时，使用的基础镜像的运行时版本需要和函数的运行时版本保持一致。 # 中国内地用户建议使用registry.cn-beijing.aliyuncs.com仓库的基础镜像。 FROM aliyunfc/runtime-nodejs14:build-latest # 声明环境变量，并指定工作目录/tmp。 ENV PATH /opt/bin:$PATH ENV LD_LIBRARY_PATH /opt/lib ENV NODE_PATH /opt/nodejs/node_modules WORKDIR /tmp # 安装Puppeteer库到/opt/nodejs目录。 COPY ./package.json /opt/nodejs/ RUN cd /opt/nodejs \ && npm --registry https://registry.npmmirror.com i # 将需要安装到系统依赖库的.deb文件下载到/tmp/install/archives目录。 RUN mkdir -p /opt/lib /tmp/install RUN apt-get update && apt-get install -y -d -o=dir::cache=/tmp/install \ libblas3 fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \ libgtk-3-0 libnspr4 libnss3 libpangocairo-1.0-0 libxcb-dri3-0 \ libx11-xcb1 libxcb1 libxss1 libxtst6 lsb-release \ xdg-utils libatspi2.0-0 libatk1.0-0 libxkbcommon0 libepoxy0 \ libglapi-mesa libnspr4 libgbm-dev \ --reinstall --no-install-recommends RUN for f in $(ls /tmp/install/archives/*.deb); do \ echo "Preparing to unpack ${f##*/}"; \ cd /tmp/install/archives; \ dpkg-deb -x ${f##*/} /tmp/install; \ done; # 拷贝安装的.so文件到/opt/lib目录。 RUN cp -r /tmp/install/usr/bin /opt/; \ cp -r /tmp/install/usr/lib/x86_64-linux-gnu/* /opt/lib/ # 将/opt/lib目录下的文件打包成ZIP格式的压缩包。注意添加-y参数保留软链接。 # .[^.]* 表示包含隐藏文件并排除父目录。 RUN cd /opt \ && zip -ry layer.zip * .[^.]* CMD ["bash"]
```

### 步骤二：构建层ZIP包

1. 执行以下命令，使用Dockerfile文件打包镜像。
  
  ```
  sudo docker build -t ${layer-image-name} -f Dockerfile .
  ```
2. 执行以下命令，将层ZIP包从镜像中拷贝出来。
  
  ```
  sudo docker run --rm -v $(pwd):/tmp ${layer-image-name} sh -c "cp /opt/layer.zip /tmp/"
  ```

### 步骤三：创建自定义层

层ZIP包构建完成后，您可以通过[函数计算控制台](https://fcnext.console.aliyun.com)或者Serverless Devs创建层。层上传方式选择通过ZIP包上传，具体操作，请参见[创建自定义层](https://help.aliyun.com/zh/functioncompute/fc/user-guide/create-a-custom-layer-1#836cebee4fsua)。

## 函数计算的基本镜像

以下列举函数计算针对不同的语言及开发环境预置的基本镜像。实际使用时，您可以从对应镜像仓库路径直接拉取，拉取脚本如`docker pull registry.cn-beijing.aliyuncs.com/aliyunfc/runtime-python3.10:latest`。

| **镜像名称** | **镜像仓库路径** |
| --- | --- |
| python3.10 | registry.cn-beijing.aliyuncs.com/aliyunfc/runtime-python3.10 |
| python3.9 | registry.cn-beijing.aliyuncs.com/aliyunfc/runtime-python3.9 |
| python3.6 | registry.cn-beijing.aliyuncs.com/aliyunfc/runtime-python3.6 |
| nodejs16 | registry.cn-beijing.aliyuncs.com/aliyunfc/runtime-nodejs16 |
| nodejs14 | registry.cn-beijing.aliyuncs.com/aliyunfc/runtime-nodejs14 |
| nodejs12 | registry.cn-beijing.aliyuncs.com/aliyunfc/runtime-nodejs12 |
| java11 | registry.cn-beijing.aliyuncs.com/aliyunfc/runtime-java11 |
| java8 | registry.cn-beijing.aliyuncs.com/aliyunfc/runtime-java8 |
| dotnetcore2.1 | registry.cn-beijing.aliyuncs.com/aliyunfc/runtime-dotnetcore2.1 |
| go1 | registry.cn-beijing.aliyuncs.com/aliyunfc/runtime-go1 |
| custom | registry.cn-beijing.aliyuncs.com/aliyunfc/runtime-custom |
| custom.debian10 | registry.cn-beijing.aliyuncs.com/aliyunfc/runtime-custom.debian10 |

更多信息，请参见[函数计算基本镜像](https://github.com/aliyun/fc-docker/blob/master/README.md)。

## **后续操作**

层创建完成后，您可以通过[函数计算控制台](https://fcnext.console.aliyun.com)或Serverless Devs将其绑定到函数，以便函数访问层中提供的资源。具体操作，请参见[配置自定义层](https://help.aliyun.com/zh/functioncompute/fc/user-guide/configure-custom-layers-for-a-function-1)。
