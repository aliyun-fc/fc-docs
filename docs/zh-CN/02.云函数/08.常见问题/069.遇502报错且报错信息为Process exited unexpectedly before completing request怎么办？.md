# 遇502报错且报错信息为Process exited unexpectedly before completing request怎么办？

## 可能原因

HTTP Server连接主动关闭，主动关闭的可能原因如下：

- 连接未设置Keep-Alive。
- 空闲一段时间后，主动关闭。
- 读写超时或错误时关闭。

## 解决方案

当前的函数计算使用Keep-Alive连续访问Custom Container内的HTTP Server，对于幂等请求例如GET、HEAD、OPTIONS或TRACE等，在连接失败时例如`EOF`和`connection reset by peer`等，会主动重试。但对于非幂等请求例如POST、PATCH等，在连接失败时会直接返回502报错。为避免502报错，Custom Container的服务端需要设置以下两类参数：

- 将连接模式Connection设置为Keep-Alive。
- 关闭IDLE超时时间或将IDLE超时时间设置为15分钟以上。

对于不同的HTTP Server框架以上两种参数的配置方式可能会不一样，例如GoFrame框架，不仅需要将`SetIdletimeout`设置为0，还需要设置`ReadTimeout`和`python uvicorn`参数，`python uvicorn`还需要在命令行中设置`--timeout-keep-alive`等参数。建议您自行验证，对于Keep-Alive模式的HTTP客户端在进行稀疏性调用时，是否会触发HTTP server主动关闭连接。

## 可能原因

函数本身原因导致进程退出，可能原因如下：

- 主动调用`exit`等接口退出。
- 运行过程中出现的`exception`未被捕获。

## 解决方案

您可以按照以下方式检查您的代码：

- 检查您的代码中是否存在主动退出的逻辑。
- 在运行环境进程顶层增加异常捕获或覆盖，避免发生`exception`时进程退出。
