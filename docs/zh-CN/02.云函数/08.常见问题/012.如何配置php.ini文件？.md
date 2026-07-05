# 如何配置php.ini文件？

`php.ini`文件是PHP的配置文件，它包含了PHP运行环境的各种设置选项和参数。当您需要自定义或调整环境信息时，可以通过修改`php.ini`来实现。在函数计算中，使用不同方式创建函数时，配置`php.ini`文件的方法不同。

- 如果您使用容器镜像的方式创建函数，按照正常的配置方式进行配置即可，即将`php.ini`文件放置在`/usr/local/etc/php`目录。此方式适用于对Docker比较熟悉的用户。
- 如果您使用函数计算的内置运行时或自定义运行时创建函数，则只能将`php.ini`文件放置在`/code`目录下。此时，您可以通过配置环境变量的方式给出读取该配置文件的路径，系统将根据此路径获取配置文件，如下图所示。具体操作，请参见[配置环境变量](https://help.aliyun.com/zh/functioncompute/fc/user-guide/environment-variables)。
  
  更多信息，请参见[PHP: The configuration file](https://www.php.net/manual/en/configuration.file.php)。
  
  将环境变量名设置为`PHP_INI_SCAN_DIR`，值设置为`/code/etc/php/7.4/cli/conf.d`。
