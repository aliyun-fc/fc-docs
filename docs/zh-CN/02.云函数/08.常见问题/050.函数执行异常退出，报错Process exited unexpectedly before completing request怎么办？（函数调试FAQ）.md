# 函数执行异常退出，报错Process exited unexpectedly before completing request怎么办？

函数执行异常退出，可能存在以下问题，你可以根据不同问题采取不同的措施。

- 函数本身逻辑错误，多见于下游数据库问题，示例代码如下。您可以增加日志功能，根据日志调试解决。
  
  ```
  # -*- coding: utf-8 -*- import os def handler(event, context): logger = logging.getLogger() logger.info('hello world') os._exit(-1) return 'hello world'
  ```
- 如果您的函数是自定义运行时或者自定义镜像函数，可能创建HTTP Server时，Connection未设置为Keep-Alive，且函数的执行超时时间小于15分钟。更多信息，请参见[HTTP Server配置要求](https://help.aliyun.com/zh/functioncompute/fc/user-guide/principles-1#section-ffl-tm3-txg)。
