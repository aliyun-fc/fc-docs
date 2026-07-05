# 部署代码包

本文以第三方依赖Nette\Utils为例，介绍如何为您的PHP代码安装依赖、打包代码并部署至函数计算。

## 准备工作

1. 创建一个用于测试的代码目录，如`mycode`。
  
  - Linux或macOS系统
    
    您可以执行`mkdir -p /tmp/mycode`创建。
  - Windows系统
    
    在任意位置新建文件夹，并将其命名为`mycode`即可。
2. 在`mycode`目录下，建立`index.php`文件。
  
  文件内容如下。
  
  ```
  <?php require_once __DIR__ . '/vendor/autoload.php'; use Nette\Utils\Arrays; function handler($event, $context) { return Arrays::contains([1, 2, 3], 1); }
  ```

## 使用Composer安装依赖并部署

### **前提条件**

- 您本机已安装PHP和Composer，且具有执行Composer命令的权限。关于Composer更多信息，请参见[Composer](https://getcomposer.org/)。
- **可选：**您已在[函数计算控制台](https://fcnext.console.aliyun.com)创建PHP函数。具体操作，请参见[创建事件函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/creating-an-event-function#45e9ee65bd8n7)。

### **操作步骤**

1. 在`mycode`目录下创建文件composer.json。
  
  内容如下：
  
  ```
  { "require": { "nette/utils": "v3.2.5" } }
  ```
2. 在`mycode`目录下执行命令`composer install`下载依赖。
  
  执行完成后，在该目录下自动生成文件composer.lock和目录vendor，vendor目录下包括已下载的依赖。
3. 打包`mycode`目录下所有文件。
  
  - Linux或macOS系统
    
    进入`mycode`目录，执行`zip code.zip -r ./*`。
    
    **
    
    **说明**
    
    请确保您具有该目录的读写权限。
  - Windows系统
    
    进入`mycode`目录，选中所有文件，单击鼠标右键，选择打包为ZIP包。
  
  **
  
  **说明**
  
  请确保您创建的`index.php`文件位于包的根目录。
4. 在[函数计算控制台](https://fcnext.console.aliyun.com)找到目标函数，然后在函数详情页面的**代码**页签，单击右上角**上传代码**上传您上一步打包的ZIP包。
  
  您也可以选择在[函数计算控制台](https://fcnext.console.aliyun.com)创建新的函数的同时上传ZIP包。具体操作步骤，请参见[创建事件函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/creating-an-event-function#45e9ee65bd8n7)。
5. 在函数详情的**代码**页签，单击**测试函数**。

## 使用Serverless devs工具安装依赖并部署

### **前提条件**

- [安装Serverless Devs和Docker](https://help.aliyun.com/zh/functioncompute/fc/developer-reference/install-serverless-devs-and-docker)
- [配置Serverless Devs](https://help.aliyun.com/zh/functioncompute/fc-3-0/developer-reference/configure-serverless-devs-1)

### **操作步骤**

1. 在`mycode`目录下编写`s.yaml`文件。
  
  文件内容示例如下。
  
  ```
  edition: 3.0.0 name: fcDeployApp access: "default" vars: # 全局变量 region: "cn-hangzhou" resources: hello_world: component: fc3 # 组件名称 props: region: ${vars.region} # 关于变量的使用方法，可以参考：https://docs.serverless-devs.com/serverless-devs/yaml#%E5%8F%98%E9%87%8F%E8%B5%8B%E5%80%BC functionName: "testphp" description: 'this is a test' runtime: "php7.2" code: ./ handler: index.handler memorySize: 128 timeout: 30
  ```
2. 在`mycode`目录下，新增`composer.json`文件。
  
  编写文件内容如下。
  
  ```
  { "require": { "nette/utils": "^3.0" } }
  ```
3. 执行`sudo s build --use-docker`安装依赖。
  
  执行完成后，会将依赖和相关代码部署到./vendor目录。
4. 执行`sudo s deploy`部署项目。
  
  执行完成后，即可部署函数到函数计算。

## 更多信息

您也可以使用函数计算的层功能安装依赖。具体操作，请参见[创建自定义层](https://help.aliyun.com/zh/functioncompute/fc/user-guide/create-a-custom-layer-1)。
