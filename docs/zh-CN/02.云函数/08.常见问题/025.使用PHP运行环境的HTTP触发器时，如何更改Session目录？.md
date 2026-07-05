# 使用PHP运行环境的HTTP触发器时，如何更改Session目录？

本文介绍在函数计算中使用PHP运行环境的HTTP触发器时，如何更改Session目录。

由于函数计算的Serverless特性，默认会将公共的内容存放在NAS目录，例如Web应用文件、临时缓存等。使用PHP运行环境时，您如果希望Session目录改为NAS公共目录，可以使用本文介绍的方法。

1. 在函数入口文件的相同目录创建一个extension目录，目录结构如下。
  
  ```
  . |____extension | |____my_ext.ini |____index.php
  ```
2. 编辑my_ext.ini文件，设置Session的存储目录并自动启动Session。
  
  示例代码如下，最后两行代码分别用于设置Session的存储目录和自动启动Session。
  
  ```
  extension=session.so extension=ftp.so extension=shmop.so extension=bcmath.so extension=gettext.so extension=pcntl.so extension=simplexml.so extension=xmlreader.so extension=bz2.so extension=gmp.so extension=pdo.so extension=soap.so extension=xmlrpc.so extension=calendar.so extension=iconv.so extension=pdo_mysql.so extension=sockets.so extension=xmlwriter.so extension=ctype.so extension=imagick.so extension=phar.so extension=sysvmsg.so extension=dom.so extension=json.so extension=posix.so extension=sysvsem.so extension=exif.so extension=mbstring.so extension=protobuf.so extension=sysvshm.so extension=fileinfo.so extension=mysqli.so extension=redis.so extension=zip.so extension=memcached.so extension=tokenizer.so session.save_path=/mnt/www session.auto_start=1
  ```
3. 基于上述目录的代码包创建函数。具体操作，请参见[创建函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/creating-a-web-function#section-b9y-zn1-5wr)。
4. 为函数增加环境变量，PHP_INI_SCAN_DIR指向代码目录下面的my_ext.ini。具体操作，请参见[创建Web函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/creating-a-web-function#section-efu-0ch-7zr)。在函数的**环境变量**配置中，添加变量名为`PHP_INI_SCAN_DIR`，值为`/code/extention`的环境变量。
