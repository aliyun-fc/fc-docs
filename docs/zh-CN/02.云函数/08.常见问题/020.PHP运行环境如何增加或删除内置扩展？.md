# PHP运行环境如何增加或删除内置扩展？

函数计算的PHP运行环境中自带一些常见的内置扩展，同时支持自定义增加或删除内置扩展。本文介绍如何增加或删除PHP运行环境的内置扩展。

本文以不引入protobuf内置扩展为例，介绍如何删除PHP运行环境的内置扩展。关于函数计算PHP运行环境目前支持的内置扩展，请参见[PHP内置扩展](https://help.aliyun.com/zh/functioncompute/fc-3-0/user-guide/overview-php#section-zxz-fow-swn)。

1. 在函数入口文件的相同目录创建一个extension目录，目录结构如下。
  
  ```
  . |____extension | |____my_ext.ini |____index.php
  ```
2. 编辑my_ext.ini文件，注释protobuf扩展。
  
  您可以增加其他扩展或注释不需要的扩展，优化PHP运行环境的启动速度。示例代码如下。
  
  ```
  extension=session.so extension=ftp.so extension=shmop.so extension=bcmath.so extension=gettext.so extension=pcntl.so extension=simplexml.so extension=xmlreader.so extension=bz2.so extension=gmp.so extension=pdo.so extension=soap.so extension=xmlrpc.so extension=calendar.so extension=iconv.so extension=pdo_mysql.so extension=sockets.so extension=xmlwriter.so extension=ctype.so extension=imagick.so extension=phar.so extension=sysvmsg.so extension=dom.so extension=json.so extension=posix.so extension=sysvsem.so extension=exif.so extension=zip.so extension=memcached.so extension=mbstring.so ;extension=protobuf.so extension=sysvshm.so extension=fileinfo.so extension=mysqli.so extension=redis.so extension=tokenizer.so extension=zip.so extension=memcached.so zend_extension=/usr/local/lib/php/extensions/no-debug-non-zts-20170718/opcache.so zend_extension=/usr/local/lib/php/extensions/no-debug-non-zts-20170718/xdebug.so
  ```
3. 基于上述目录的代码包创建函数。具体操作，请参见[创建函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/creating-a-web-function#section-b9y-zn1-5wr)。
4. 设置函数的环境变量。PHP_INI_SCAN_DIR指向代码目录下面的my_ext.ini，此时PHP运行环境不会加载protobuf扩展。在函数的**环境变量**配置中，添加变量`PHP_INI_SCAN_DIR`，值设置为`/code/extention`。

## 更多信息

更多信息，请参见[PHP运行环境动态加载卸载内置扩展](https://developer.aliyun.com/article/645670)。
