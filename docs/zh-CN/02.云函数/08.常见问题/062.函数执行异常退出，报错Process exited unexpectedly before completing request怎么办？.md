# 函数执行异常退出，报错Process exited unexpectedly before completing request怎么办？

发生实例进程异常退出的错误，可能存在以下问题，您可以根据不同的问题采用不同的解决方案。

1. [HTTP Server连接主动关闭](#eed6594d79l2l)。
2. [函数本身原因导致进程退出](#cause-lat-t0y-i3f)。
3. [实例内存不足导致进程OOM](#5525e84a0emec)。
4. [启动命令缺少可执行权限、文件不存在、文件格式错误](#fba6a287073o4)。

## **HTTP Server连接主动关闭**

HTTP Server连接主动关闭，主动关闭的可能原因如下：

- 连接未设置Keep-Alive。
- 空闲一段时间后，主动关闭。
- 读写超时或出错时关闭。

## 解决方案

当前的函数计算使用Keep-Alive连续访问自定义运行时内的HTTP Server，对于幂等请求例如GET、HEAD、OPTIONS或TRACE等，在连接失败时例如`EOF`、`connection reset by peer`等，会主动重试。但对于非幂等请求例如POST、PATCH等，在连接失败时会直接返回502报错。为避免502报错，自定义运行时的服务端需要设置以下两类参数：

- 将连接模式Connection设置为Keep-Alive。
- 关闭IDLE超时时间或将IDLE超时时间设置为15分钟以上。

对于不同的HTTP Server框架以上两种参数的配置方式可能会不一样，例如GoFrame框架，不仅需要将`SetIdletimeout`设置为0，还需要设置`ReadTimeout`和`python uvicorn`参数，`python uvicorn`还需要在命令行中设置`--timeout-keep-alive`等参数。建议您自行验证，对于Keep-Alive模式的HTTP客户端在进行稀疏性调用时，是否会触发HTTP server主动关闭连接。

## **函数本身的原因导致进程退出**

函数本身的原因导致进程退出，可能原因如下：

- 主动调用`exit`等接口退出。
- 运行过程中出现的`exception`未被捕获。

示例代码如下。您可以增加日志功能，根据日志调试解决。

```
# -*- coding: utf-8 -*- import os import logging def handler(event, context): logger = logging.getLogger() logger.info('something is wrong') os._exit(-1) return 'hello world'
```

## 解决方案

您可以按照以下方式检查您的代码：

- 检查您的代码中是否存在主动退出的逻辑。
- 在运行环境进程顶层增加异常捕获或覆盖，避免发生`exception`时进程退出。

强烈建议不要在代码中直接使用os._exist(-1)等方式退出进程，该方式导致函数计算侧无法获取到退出时的堆栈信息。

建议使用抛出异常的方式，或者在退出进程前，手动打印堆栈到日志。

## **实例内存不足导致程序OOM**

实例内存不足导致程序OOM，可以分析函数计算控制台“日志”界面的请求内存用量（需要开启日志的请求级别指标）。请参见[请求级别指标日志](https://help.aliyun.com/zh/functioncompute/fc/request-level-metric-logs)。

## **解决方案**

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com/)，在左侧导航栏，单击**函数**。
2. 在顶部菜单栏，选择地域，然后在**函数**页面，单击目标函数。
3. 在函数详情页面，选择**配置**页签，然后在左侧选择**基础配置**。
4. 在**基础配置**页面点击**编辑**，增加内存规格，点击**部署**。

## **启动命令缺少可执行权限、文件不存在、文件格式错误**

启动命令问题，可能原因如下：

- 启动命令缺少可执行权限。
- 启动命令指定的文件不存在。
- 文件格式错误。

## **解决方案**

详见请参见[自定义运行时错误处理](https://help.aliyun.com/zh/functioncompute/fc/troubleshooting-2#section-4er-gi7-4rk)。
