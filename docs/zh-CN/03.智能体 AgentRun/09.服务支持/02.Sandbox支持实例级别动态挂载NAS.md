# Sandbox支持实例级别动态挂载NAS

## **背景说明**

在Sandbox的应用场景中，存在需要访问隔离的共享文件系统的需求。例如，浏览器沙箱场景中，您可能希望将用户的登录数据存储在共享文件目录中，以便后续二次使用，以便持久化保存Sandbox操作期间生成的文件、项目代码、数据集等关键资产。

在过去的方案中，开发者常将所有Sandbox挂载到同一个共享的NAS根目录下。然而，这种做法存在严重的数据越权访问风险：一个恶意或异常会话可能通过路径遍历、权限提升等方式访问甚至篡改其他租户的数据，无法满足企业级安全与合规要求。

为应对这一挑战，Agentrun Sandbox进一步将隔离能力延伸至持久化存储层，推出"动态挂载文件存储NAS"功能。该功能允许每个AI Sandbox会话在启动时，自动、安全地挂载到专属的NAS子目录，实现从计算到存储的端到端多租户隔离，并实现文件共享，简化数据管理流程，同时解决本地磁盘空间限制问题。为Sandbox实例配置NAS文件系统后，您的Sandbox可以像操作本地文件系统一样，轻松执行读取和写入NAS文件的操作。

**

**重要**

- 目前仅支持挂载通用版NAS。
- 在同一地域下的同一个Sandbox实例最多支持配置5个NAS文件系统。

## **前提条件**

### AgentRun

需创建Sandbox模板并为模板配置VPC网络访问能力和有权访问NAS的执行角色：

1. 登录[AgentRun控制台](https://functionai.console.aliyun.com)，在顶部菜单栏选择地域。
2. 在左侧导航栏，选择。
3. 创建需要使用实例级别NAS挂载的Sandbox模板。
  
  NAS挂载需要配置模板的VPC。创建模板时，请开启**允许访问VPC**，并配置专有网络、交换机和安全组。
4. 选择有权访问NAS的**执行角色**（executionRoleArn）。
  
  执行角色用于授予函数计算访问其他阿里云服务的权限，需要包含访问NAS的相关策略。

### 文件存储NAS

已创建NAS文件系统，并添加挂载点。具体操作，请参见[创建文件系统](https://help.aliyun.com/zh/nas/user-guide/create-a-file-system)和[添加挂载点](https://help.aliyun.com/zh/nas/user-guide/manage-mount-targets#section-6xi-a3u-zkq)。

目前只支持在私有的VPC环境内添加NAS挂载点，因此，在配置网络时需设置允许函数访问VPC内资源，并配置正确的VPC，才能访问指定的NAS文件系统。

## 使用限制

- 函数计算在同一地域下的一个函数最多支持配置5个NAS挂载点。
- NAS挂载点的函数运行环境中的本地目录不能冲突。

## 配置NAS文件系统

Sandbox支持在创建实例时配置NAS动态挂载，提供两种配置方式：

- **控制台配置**：通过AgentRun控制台的在线调试功能，在创建沙箱实例时配置NAS挂载。
- **API配置**：通过数据面API在创建沙箱实例时配置NAS挂载（推荐）。

**

**说明**

- NAS挂载需要配置模板的VPC，确保与通用型NAS文件系统使用相同的专有网络、交换机和安全组。
- Sandbox的默认用户和用户组都是1000/1000，如果您没有特别需求，可以不设置该参数，或设置为默认值。
- 上传至NAS的文件权限与本地文件权限完全相同。
- 挂载点的VPC需要与Sandbox模板配置的VPC相同，否则无法选择该挂载点。

关于费用详情，请参见[VPC产品计费](https://help.aliyun.com/zh/vpc/what-is-vpc#7844a18956h07)和[通用型NAS计费](https://help.aliyun.com/zh/nas/product-overview/billing-of-general-purpose-nas-file-systems#task-2567548)。

### 通过控制台配置

1. 登录[AgentRun控制台](https://functionai.console.aliyun.com)，在顶部菜单栏选择地域。
2. 在左侧导航栏，选择。
3. 点击目标Sandbox模板，进入模板详情页面。
4. 点击左侧导航栏的**在线调试**。
5. 点击**创建沙箱**按钮，弹出创建沙箱实例对话框。
6. 在NAS挂载配置区域：
  
  - **启用NAS挂载**：开启开关。
  - **文件系统**：选择已创建的通用型NAS文件系统。
  - **挂载点**：选择与Sandbox模板VPC相同的挂载点。
  - **远端目录**：填写NAS中的远端目录，例如`/`。
  - **函数挂载目录**：填写Sandbox实例中的挂载目录，例如`/mnt/nas`。
7. 点击**确认并创建**。

**说明**：

- 系统会自动过滤并显示与Sandbox模板VPC匹配的挂载点。
- 创建流程包括**创建沙箱实例**和**健康检查**两个步骤，通常需要几秒钟完成。

### 通过API配置（推荐）

您可以通过数据面API在创建沙箱实例时配置NAS挂载。更多详情，请参见[Code Interpreter代码解释器](https://help.aliyun.com/zh/functioncompute/fc/sandbox-sandbox-code-interepreter)。

### API请求说明

**请求路径**

```
POST ${BASEURL}/sandboxes
```

**BASEURL 格式**：`https://${主账号ID}.agentrun-data.cn-hangzhou.aliyuncs.com`

**请求头**

| **参数** | **说明** |
| --- | --- |
| X-Acs-Parent-Id | 阿里云主账号ID |
| Content-Type | application/json |
| X-API-Key | ${API Key}（如果沙箱模板配置了访问凭证，则必须添加此请求头） |

**认证说明**：

- **如果沙箱模板配置了访问凭证**：通过 API 创建沙箱实例时，必须在请求头中添加`X-API-Key: ${API Key}`，其中`${API Key}`为模板配置的访问凭证对应的 API Key。
- **如果沙箱模板配置了匿名访问**：需要在控制台勾选`**允许数据面接口匿名调用沙箱实例创建、查询、删除接口**`选项，否则会返回 403 错误（`template does not allow anonymous manage via data plane`）。

**请求体**

```
{ "templateName": "string", "sandboxId": "string", "nasConfig": { "groupId": 1000, "userId": 1000, "mountPoints": [ { "serverAddr": "string", "mountDir": "string" } ] } }
```

**参数说明**

| **参数** | **是否必填** | **说明** |
| --- | --- | --- |
| templateName | 是 | 模板名称。系统内部通过templateName查询template_id。 |
| sandboxId | 否 | 自定义沙箱ID，用于端到端tracing。如果不指定，系统会自动生成ULID格式的ID。 |
| nasConfig.groupId | 否 | 用户组ID。默认值为1000。 |
| nasConfig.userId | 否 | 用户ID。默认值为1000。 |
| nasConfig.mountPoints | 是 | 挂载点配置列表。 |
| nasConfig.mountPoints[].serverAddr | 是 | NAS服务器地址。格式为`挂载点:/`，例如：`a1234567-cvx53.cn-hangzhou.nas.aliyuncs.com:/` |
| nasConfig.mountPoints[].mountDir | 是 | 挂载目录。格式为本地目录路径，例如：`/home/user/yournasdir` |

**请求示例**

```
curl -X POST "${BASEURL}/sandboxes" \ -H "X-Acs-Parent-Id: ${阿里云主账号ID}" \ -H "Content-Type: application/json" \ -d '{ "templateName": "your-template-name", "nasConfig": { "groupId": 1000, "userId": 1000, "mountPoints": [ { "serverAddr": "a1234567-cvx53.cn-hangzhou.nas.aliyuncs.com:/", "mountDir": "/home/user/nasdir" } ] } }'
```

## 验证NAS是否挂载成功

Sandbox实例创建成功后，可以通过终端工具验证NAS是否挂载成功。

```
# 查看NAS挂载目录，假设目录为/home/user/nasfsdir ls -la /home/user/nasfsdir # 写入数据 echo "hello" > /home/user/nasfsdir/hello.txt # 读取数据验证 cat /home/user/nasfsdir/hello.txt
```

您也可以使用NAS可视化浏览器应用直接通过浏览器管理已挂载NAS文件系统中的文件。具体操作，请参见[使用函数计算快速搭建可视化NAS浏览器应用](https://help.aliyun.com/zh/functioncompute/fc/use-cases/use-function-compute-to-quickly-build-a-visual-nas-browser-application)。

针对华东1（杭州）和华东2（上海）地域，您无需搭建上述函数计算的可视化NAS浏览器应用，直接在[NAS控制台](https://nasnext.console.aliyun.com/overview)，找到目标文件系统，在操作列选择**浏览器**，即可进行可视化管理文件。

## 相关概念

### NAS用户和用户组

UserID（用户ID）和GroupID（用户组ID）取值范围为[0, 65534]，如果不填写，默认值均为1000，即分别表示user用户ID和user用户组ID。

您需要根据需求设置文件的拥有者和相应的组权限，确保文件读写权限一致。例如，如果您希望不同函数可以共享NAS文件资源，您需要在为这些函数配置NAS文件系统时，使用同一个用户和用户组。

### 远端目录和Sandbox本地目录

每个NAS挂载点的地址由**远端目录**和**Sandbox本地目录**组成。挂载NAS的过程本质上是创建了一个从Sandbox实例的本地目录到NAS远端目录的映射关系。

#### **远端目录**

远端NAS中的目录是指位于NAS文件系统中的目录，由挂载点和绝对目录两部分组成。挂载点可以通过NAS控制台来添加。将挂载点和绝对目录拼接得到远端目录。

例如，NAS文件系统的挂载点是`xxxx-nas.aliyuncs.com`，您希望被访问的绝对目录是`/workspace/document`，对应完整的远端目录就是`xxxx-nas.aliyuncs.com:/workspace/document`。

您可以登录[NAS控制台](https://nasnext.console.aliyun.com/)，在文件系统列表中，单击目标文件系统，然后单击**挂载使用**，以获取挂载点。

#### **Sandbox本地目录**

函数运行环境中的本地目录是指本地文件系统的挂载点。建议使用`/home`、`/mnt`、`/tmp`或`/data`的子目录。

不能使用通用的Linux和Unix系统目录及其子目录挂载NAS，例如`/bin`、`/opt`、`/var`或`/dev`等。

## 相关文档

- 函数计算支持的存储类型包括文件存储NAS、对象存储OSS、临时硬盘和层，如果您希望了解这些存储类型的适用场景及差异，请参见[函数存储选型](https://help.aliyun.com/zh/functioncompute/fc/user-guide/selection-of-function-storage)。
- 如果您需要存储大量图片、视频和文档等非结构化数据，建议您挂载OSS对象存储系统来实现。更多信息，请参见[配置OSS对象存储](https://help.aliyun.com/zh/functioncompute/fc/user-guide/configure-an-oss-file-system-1)。
