# 函数执行超时，报错Function time out after怎么办？

如果函数调用偶然出现超时现象，您可以尝试以下操作。

- 将函数的执行超时时间调大。具体操作，请参见[更新函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/creating-a-web-function#section-efu-0ch-7zr)。
- 检查函数逻辑，配置日志功能，查看是否调用其他接口返回超时，导致整个函数执行时间变长而出现超时。
- 检查是否进入耗时较多的逻辑分支，例如CPU密集型。
