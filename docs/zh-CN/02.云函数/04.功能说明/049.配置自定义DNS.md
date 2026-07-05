# 配置自定义DNS

自定义DNS功能适用于加速站点访问等场景，本文介绍如何在函数计算控制台为函数配置自定义DNS。

## 背景信息

resolv.conf文件为系统配置文件，您配置自定义DNS解析属性后，原有resolv.conf将被覆盖。关于resolv.conf文件的规范，您可以在Linux系统执行`man 5 resolver`查看，如果提示没有man page，请先根据您使用的发行版本进行安装。更多信息，请参见[Linux manual page](https://man7.org/linux/man-pages/man5/resolv.conf.5.html)。

## 使用限制

自定义DNS功能不支持自定义镜像。

## 前提条件

已[创建函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/function-instance-1/)，不包括[GPU函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/creating-a-gpu-function/)。

## 配置DNS

**

**说明**

如需使用函数计算默认的DNS服务器，请在Name Servers中添加默认IP地址100.100.2.136和100.100.2.138。

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com)，在左侧导航栏，选择**函数管理**>**函数**。
2. 在顶部菜单栏，选择地域，然后在**函数**页面，单击目标函数。
3. 在函数详情页面，选择**配置**页签，单击**高级配置**右侧的**编辑**，在**高级配置**面板，找到**DNS**选项，按需配置以下参数，然后单击**部署**。
  
  | **参数** | **说明** | **示例值** |
  | --- | --- | --- |
  | Name Servers | DNS服务器的IP地址。支持添加多个DNS服务器的IP地址。 | - 223.5.5.5<br>- 223.6.6.6 |
  | 搜索域 | DNS搜索域。支持添加多个搜索域。当访问的域名不能被DNS解析时，搜索域将被追加到无法被解析的域名后重新解析。 | example.com |
  | DNS 选项 | resolv.conf文件中的配置项。每一项对应一个键值对，格式为*key:value*，其中键为必填。 | attempts:1 |
4. 验证配置的DNS解析属性是否生效。
  
  1. 在函数详情页面，单击**代码**页签。
  2. 在代码编辑器中编写代码，单击**部署代码**，然后单击**测试函数**。
    
    代码示例（Python 3）如下：
    
    ```
    # -*- coding: utf-8 -*- import logging import subprocess def handler(event, context): logger = logging.getLogger() f = open('/etc/resolv.conf') logger.info("".join(f.readlines())) f.close() output = subprocess.check_output(["ping", "-c", "1", "www.aliyun.com"]) return output
    ```
  3. 在**代码**页签，查看执行结果。在**返回结果**区域，查看resolv.conf生成的对应的内容，在**日志输出**区域，查看返回的域名的IP地址。
