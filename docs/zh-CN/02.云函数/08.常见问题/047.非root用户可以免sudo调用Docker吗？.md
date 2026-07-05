# 非root用户可以免sudo调用Docker吗？

可以。

由于Docker需要sudo调用，因此执行`s local`或`s build`调试函数时，默认需要添加sudo。如果您不希望使用sudo，您可以配置Docker免sudo。具体信息，请参见[免sudo调用Docker](https://askubuntu.com/questions/477551/how-can-i-use-docker-without-sudo)。
