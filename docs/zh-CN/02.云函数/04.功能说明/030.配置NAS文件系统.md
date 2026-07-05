# 配置NAS文件系统

在函数计算的应用场景中，面对多个应用或函数需共享访问同一组数据的需求，例如，机器学习应用中，训练好的模型需要被多个推理函数共享，您可以为函数配置NAS文件系统来存储这些数据，实现文件共享，简化数据管理流程，同时解决本地磁盘空间限制问题。为函数配置NAS文件系统后，您的FC函数可以像操作本地文件系统一样，轻松执行读取和写入NAS文件的操作。

## 前提条件

- 函数计算
  
  已创建函数并为函数配置VPC网络访问能力。具体操作，请参见[创建函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/function-instance-1/)和[配置网络](https://help.aliyun.com/zh/functioncompute/fc/user-guide/configure-network-settings)。
  
  **
  
  **说明**
  
  目前只支持在私有的VPC环境内添加NAS挂载点，因此，在配置网络时需设置允许函数访问VPC内资源，并配置正确的VPC，才能访问指定的NAS文件系统。
- 文件存储NAS
  
  已创建NAS文件系统，并添加挂载点。具体操作，请参见[创建文件系统](https://help.aliyun.com/zh/nas/user-guide/create-a-file-system)和[添加挂载点](https://help.aliyun.com/zh/nas/user-guide/manage-mount-targets#section-6xi-a3u-zkq)。

## **使用限制**

- 函数计算在同一地域下的一个函数最多支持配置5个NAS挂载点和5个OSS挂载点。
- NAS挂载点和OSS挂载点设置的函数运行环境中的本地目录不能冲突。

## **配置NAS文件系统**

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com)，在左侧导航栏，选择**函数管理**>**函数列表**。
2. 在顶部菜单栏，选择地域，然后在**函数列表**页面，单击目标函数。
3. 在函数详情页面，选择**配置**页签，单击**高级配置**右侧的**编辑**，在**高级配置**面板，找到**存储**选项，开启**挂载NAS文件系统**开关，按照以下操作配置完成后单击**部署**。
  
  您可以选择**自动配置**或**自定义配置**两种方式来配置NAS文件系统。
  
  ## 自动配置
  
  系统自动为您创建一个名称为`Alibaba-Fc-V3-Component-Generated`的通用型NAS文件系统以及同名的专有网络、交换机和安全组。
  
  当您再次选择**自动配置**时，系统查询到当前地域下已存在该NAS文件系统，则会复用该文件系统和相关VPC配置，不会重复创建。关于费用详情，请参见[VPC产品计费](https://help.aliyun.com/zh/vpc/product-overview/product-billing#concept-1357436)和[通用型NAS计费](https://help.aliyun.com/zh/nas/product-overview/billing-of-general-purpose-nas-file-systems#task-2567548)。
  
  ## 自定义配置
  
  您需要手动选择NAS文件系统，设置用户、用户组以及NAS挂载点等NAS相关参数才能完成配置NAS文件系统。
  
  重点配置项介绍如下：
  
  | **配置项** | **说明** | **示例** |
  | --- | --- | --- |
  | **NAS 文件系统** | 选择已创建的NAS文件系统。<br>如需创建新的NAS文件系统，单击下方的**创建新的 NAS 文件系统**，跳转到[文件存储控制台](https://nasnext.console.aliyun.com/)手动创建。<br>**<br>**重要**<br>仅支持NFS协议类型的NAS文件系统，不支持SMB协议类型。 | 01d394**** |
  | **用户**、**用户组** | 需填写自定义的用户ID和用户组ID。如您不输入任何值，系统将使用root用户，即`UID=0`和`GID=0`。更多信息，请参见[NAS用户和用户组](#2892f4e436yas)。 | 1 |
  | **远端目录** | - 通用型NAS的该目录必须以/开头。<br>- 极速型NAS的该目录必须以/share开头。<br>若您配置的目录在远端NAS中不存在，函数计算将会为您自动创建该目录。目录所有者为上述配置的用户和用户组，权限等级为`777`。<br>更多信息，请参见[远端目录](#uicontrol-3vs-d3j-tgu)。 | / |
  | **函数本地目录** | 建议使用/home、/mnt、/tmp或/data的子目录。<br>**<br>**说明**<br>不能使用通用的Linux和Unix系统目录及其子目录，例如/bin、/opt、/var或/dev等，以免挂载失败。<br>更多信息，请参见[函数本地目录](#uicontrol-mi2-kjm-5qv)。 | /mnt/nas |
  
  **
  
  **说明**
  
  - 如果您希望不同函数可以共享NAS文件资源，您需要在为这些函数配置NAS文件系统时，使用同一个用户和用户组。
  - 上传至NAS的文件权限与本地文件权限完全相同。

## **验证NAS是否挂载成功**

### **准备访问NAS的函数代码**

完成NAS文件系统的配置后，您可以在您的函数代码中，通过挂载时指定的路径来访问NAS文件系统。

1. 在函数详情页面，单击**代码**页签，在代码编辑器中编写代码，然后单击**部署代码**。
  
  本文以Python事件函数代码为例，在代码中完成将内容写入NAS文件系统和读取NAS文件内容。
  
  ```
  #!/usr/bin/env python # -*- coding: utf-8 -*- import random import subprocess import string import os def handler(event, context): # report file system disk space usage and check NAS mount target out, err=subprocess.Popen(['df', '-h'], stdout=subprocess.PIPE).communicate() print('disk: ' + str(out)) lines = [ l.decode() for l in out.splitlines() if str(l).find(':') != -1 ] nas_dirs = [ x.split()[-1] for x in lines ] print('uid : ' + str(os.geteuid())) print('gid : ' + str(os.getgid())) for nas_dir in nas_dirs: sub_dir = randomString(16) file_name = randomString(6)+'.txt' new_dir = nas_dir + '/' + sub_dir + '/' print('test file: ' + new_dir + file_name) # 写入NAS文件 content = "NAS here I come" os.mkdir(new_dir) fw = open(new_dir + file_name, "w+") fw.write(content) fw.close() # Showing the folder tree in NAS for home, dirs, files in os.walk(nas_dir): level = home.replace(nas_dir, '').count(os.sep) indent = ' ' * 2 * (level) print('{}{}/'.format(indent, os.path.basename(home))) subindent = ' ' * 2 * (level + 1) for f in files: print('{}{}'.format(subindent, f)) # 读取NAS文件 f = open(new_dir + file_name, "r") print(f.readline()) f.close() return 'success' def randomString(n): return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n))
  ```

### **验证结果**

1. 代码部署成功后，单击**代码**页签的**测试函数**。
  
  执行完成后，您可以在**代码**页签的下方查看执行结果。在**日志输出**页签下可以看到函数已经成功写入NAS文件并读取NAS文件。
  
  ```
  C9JFL0.txt DCFIC887M7R74WYH/ 5CXI5H.txt H0630SH2QHPL9MHZ/ EUV7ZA.txt H4UNM032L2TDLPPQ/ YXDBPM.txt HYMF79FH11AYW66D/ LU3WNG.txt Z3QNEH0MY0K3VM6G/ 9D3FM2.txt fc-1/ modelscope-60c13a-model-download-func/ NAS here I come FC Invoke End RequestId: 1-66878b18-16cd285c-27f5980efe23
  ```
2. （可选）完成文件的写入和读取之后，您可以登录实例查看函数本地目录下的文件情况，确认查询到的NAS文件与上一步函数执行成功后日志输出内容是否一致。
  
  1. 您可以在函数详情页面，单击**实例**页签，单击目标实例**操作**列的**登录实例**。
    
    如果当前没有运行中的实例，可以在**代码**页签单击**测试函数**重新执行一次函数，创建实例。
  2. 成功登录实例后，您就可以通过命令查看配置的函数本地目录下的文件信息。
    
    ```
    root@c-668b4cff-xxx:/code# cd /mnt/nas root@c-668b4cff-xxx:/mnt/nas# ls 0Q0V5ZYWMW7SLUYV BVT5FA0OV9ZLIZMU DCFIC887M7R74WYH F8I2CGH79QQGPZKC HO63OSH2QHPL9MHZ H4UNM032L2TDLPPQ HYMF79FH11AYW66D KEDRGMD67X64A6FD Z3QNEH0MY0K3VM6G fc-1 modelscope-60c13a-model-download-func root@c-668b4cff-xxx:/mnt/nas# cd ../ root@c-668b4cff-xxx:/mnt# cd nas/Z3QNEH0MY0K3VM6G root@c-668b4cff-xxx:/mnt/nas/Z3QNEH0MY0K3VM6G# ls 9D3FM2.txt root@c-668b4cff-xxx:/mnt/nas/Z3QNEH0MY0K3VM6G#
    ```
3. （可选）您还可以使用NAS可视化浏览器应用，直接通过浏览器管理已挂载NAS文件系统中的文件。具体操作，请参见[使用函数计算快速搭建可视化NAS浏览器应用](https://help.aliyun.com/zh/functioncompute/fc/use-cases/use-function-compute-to-quickly-build-a-visual-nas-browser-application)。
  
  针对华东1（杭州）和华东2（上海）地域，您无需搭建上述函数计算的可视化NAS浏览器应用，直接在[NAS控制台](https://nasnext.console.aliyun.com/overview)，找到目标文件系统，在操作列，选择，即可进行可视化管理文件。
  
  成功访问**NAS 浏览器**后，**文件管理**页面的根目录下将显示已挂载 NAS 文件系统中的文件夹，表示挂载配置正确。

## **相关概念**

### **NAS用户和用户组**

UserID（用户ID）和GroupID（用户组ID）取值范围为[0, 65534]，如果不填写，默认值均为0，即分别表示root用户ID和root用户组ID。您需要根据需求设置文件的拥有者和相应的组权限，确保文件读写权限一致。例如，如果您希望不同函数可以共享NAS文件资源，您需要在为这些函数配置NAS文件系统时，使用同一个用户和用户组。

### **远端目录和函数本地目录**

每个NAS挂载点的地址由**远端目录**和**函数本地目录**组成。挂载NAS的过程本质上是创建了一个从函数计算实例的本地目录到NAS远端目录的映射关系。

- **远端目录**
  
  远端NAS中的目录是指位于NAS文件系统中的目录，由挂载点和绝对目录两部分组成。挂载点可以通过NAS控制台来添加。将挂载点和绝对目录拼接得到远端目录。例如，NAS文件系统的挂载点是xxxx-nas.aliyuncs.com，您希望被访问的绝对目录是/workspace/document，对应完整的远端目录就是xxxx-nas.aliyuncs.com:/workspace/document。
  
  您可以登录[NAS控制台](https://nasnext.console.aliyun.com/)，在文件系统列表中，单击目标文件系统，然后单击**挂载使用**，以获取挂载点。
- **函数本地目录**
  
  函数运行环境中的本地目录是指本地文件系统的挂载点。建议使用/home、/mnt、/tmp或/data的子目录。不能使用通用的Linux和Unix系统目录及其子目录挂载NAS，例如/bin、/opt、/var或/dev等。

## **相关文档**

- 函数计算支持的存储类型包括文件存储NAS、对象存储OSS、临时硬盘和层，如果您希望了解这些存储类型的适用场景及差异，请参见[函数存储选型](https://help.aliyun.com/zh/functioncompute/fc/user-guide/selection-of-function-storage)。
- 如果您需要存储大量图片、视频和文档等非结构化数据，建议您挂载OSS对象存储系统来实现。更多信息，请参见[配置OSS对象存储](https://help.aliyun.com/zh/functioncompute/fc/user-guide/configure-an-oss-file-system-1)。
- 您还可以使用Serverless Devs为函数挂载NAS系统。具体操作，请参见[Serverless Devs常用命令](https://help.aliyun.com/zh/functioncompute/fc/developer-reference/serverless-devs-commands-1)。
- 如果您需要可视化管理为函数配置的NAS文件管理系统，可以通过函数计算应用中心创建NAS可视化浏览器应用。具体操作，请参见[快速入门（FC）](https://help.aliyun.com/zh/nas/getting-started/quick-start-fc-nas-browser)。
