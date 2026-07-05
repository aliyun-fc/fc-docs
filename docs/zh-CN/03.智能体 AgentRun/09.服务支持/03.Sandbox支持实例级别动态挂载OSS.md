# Sandbox支持实例级别动态挂载OSS

对象存储 OSS是一款海量、安全、低成本、高可靠的云存储服务。当您在 Sandbox 实例中需要持久化存储数据、共享文件或处理大量文件时，可以通过配置 OSS 挂载，让 Sandbox 实例像访问本地文件系统一样访问 OSS 中的文件，从而简化资源访问和数据处理流程。

**

**重要**

- 在同一地域下的同一个Sandbox实例最多支持配置5个OSS挂载点。
- NAS挂载点和OSS挂载点设置的函数运行环境中的本地目录不能冲突。

## **使用限制**

| **限制项** | **说明** |
| --- | --- |
| 挂载点数量 | 在同一地域下的同一个 Sandbox 实例最多支持配置 5 个 OSS 挂载点 |
| 目录冲突 | NAS 挂载点和 OSS 挂载点设置的函数运行环境中的本地目录不能冲突 |
| 本地目录限制 | 挂载目录必须为`/home`<br>、`/mnt`<br>或`/data`<br>的子目录 |
| 存储类型 | 仅支持标准存储类型的 OSS Bucket，不支持归档存储和冷归档存储 |
| 内存规格 | 建议 Sandbox 实例内存规格不低于 512 MB，避免因内存不足导致挂载功能不可用 |
| 执行角色 | 需选择有权限访问 OSS 的执行角色（executionRoleArn） |

## 前提条件

### 对象存储OSS

已开通OSS服务并创建存储空间（Bucket）。具体操作，请参见：

- [开通OSS服务](https://oss.console.aliyun.com/overview?spm=a2c4g.11186623.0.0.6f04230eTrPQ9h)
- [创建OSS Bucket](https://help.aliyun.com/zh/oss/user-guide/console-quick-start#task-u3p-3n4-tdb)（存储类型选择标准存储）

**重要：**OSS Bucket 必须与 Sandbox 实例在同一地域，否则在配置时无法选择该 Bucket**。**

### AgentRun Sandbox

已创建Sandbox模板并配置执行角色：

1. 登录[AgentRun控制台](https://functionai.console.aliyun.com/cn-hangzhou/agent/runtime/agent-list)，在顶部菜单栏选择地域。
2. 在左侧导航栏，选择。
3. 创建或编辑Sandbox模板，并配置对应的执行角色和VPC（若需）参数。

### 执行角色权限

为函数角色配置访问OSS的权限。启用OSS挂载功能时，需要为AgentRun Sandbox配置访问OSS的角色。具体操作，请参见[使用函数角色授予函数计算访问其他云服务的权限](https://help.aliyun.com/zh/functioncompute/fc/grant-function-compute-permissions-to-access-other-alibaba-cloud-services)。

权限要求：

- **只读权限**：包括`oss:ListObjects`和`oss:GetObject`策略。
- **读写权限**：包括`oss:ListObjects`、`oss:GetObject`、`oss:PutObject`、`oss:DeleteObject`、`oss:ListParts`和`oss:AbortMultipartUpload`策略。

**说明**：`oss:ListObjects`为Bucket级别操作。因此，当您为特定的Bucket开启访问时，权限策略中需要包含Bucket级别的资源指示，例如`acs:oss:*:*:bucketName`。更多信息，请参见[基于RAM Policy控制OSS的访问权限](https://help.aliyun.com/zh/oss/user-guide/access-control-base-on-ram-policy)。

## 通过API配置OSS挂载

您可以通过数据面API在创建Sandbox实例时配置OSS动态挂载。

### 请求信息

**请求路径：**

```
POST ${BASEURL}/sandboxes
```

**请求头：**

| **参数** | **说明** |
| --- | --- |
| X-Acs-Parent-Id | 阿里云主账号ID |
| Content-Type | application/json |
| X-API-Key | ${API Key}（如果沙箱模板配置了访问凭证，则必须添加此请求头） |

**BASEURL 格式**：`https://${主账号ID}.agentrun-data.cn-hangzhou.aliyuncs.com`

**认证说明**：

- **如果沙箱模板配置了访问凭证**：通过 API 创建沙箱实例时，必须在请求头中添加`X-API-Key: ${API Key}`，其中`${API Key}`为模板配置的访问凭证对应的 API Key。
- **如果沙箱模板配置了匿名访问**：需要在控制台勾选`**允许数据面接口匿名调用沙箱实例创建、查询、删除接口**`选项，否则会返回 403 错误（`template does not allow anonymous manage via data plane`）。

### **请求体**

```
{ "templateName": "string", "sandboxId": "string", "ossMountConfig": { "mountPoints": [ { "bucketName": "example-bucket", "bucketPath": "/prod", "endpoint": "http://oss-cn-hangzhou.aliyuncs.com", "mountDir": "/mnt/oss", "readOnly": false } ] } }
```

### 参数说明

| **配置项** | **说明** | **示例** |
| --- | --- | --- |
| templateName | 模板名称，系统内部通过templateName查询template_id。 | sandbox-code-interpreter-76K7ZU |
| sandboxId | 自定义沙箱ID，用于端到端tracing。如果不指定，系统会自动生成ULID格式的ID。 | test-oss-mount-001 |
| ossMountConfig.mountPoints | OSS挂载点配置列表。 | - |
| bucketName | 选择已创建的存储空间Bucket。如需创建新的OSS存储空间，可以跳转到[对象存储控制台](https://oss.console.aliyun.com/)手动创建。关于使用OSS存储涉及的费用问题，请参见[计费概述](https://help.aliyun.com/zh/oss/billing-overview#concept-n4t-mwg-tdb)。 | example-bucket |
| bucketPath | 设置Bucket中的子目录，必须为绝对路径。留空或设置为`/`表示挂载Bucket的根目录。 | /prod |
| endpoint | OSS访问地址。选择Bucket后，默认选择该Bucket对应的访问地址。可以根据需要选择自定义地址，调整访问地址的值。关于各地域OSS服务的访问地址，请参见[地域和Endpoint](https://help.aliyun.com/zh/oss/user-guide/regions-and-endpoints#concept-zt4-cvy-5db)。<br>**说明**：<br>- 如果选择与函数计算相同地域的Bucket，建议使用OSS内网Endpoint作为访问地址。<br>- 如果选择不同地域的Bucket，则必须使用OSS外网Endpoint作为访问地址，这将产生一定的外网流出流量费用。 |  |
| mountDir | 设置函数运行环境中的本地目录，必须为`/home`、`/mnt`或`/data`的子目录。 | /mnt/oss |
| readOnly | 选择Bucket挂载到函数运行环境中的本地目录后，该目录的访问权限。支持设置为只读或读写权限。 | false（读写） |

**说明**：OSS挂载功能依赖函数的网络配置。当您的网络配置只允许函数访问VPC，且**允许函数默认网卡访问公网**为**否**时，如需使用OSS外网Endpoint，要求函数能够通过指定的VPC访问公网。具体操作，请参见[配置固定公网IP地址](https://help.aliyun.com/zh/functioncompute/fc-2-0/user-guide/configure-static-public-ip-addresses#task-2174820)。

## **访问OSS挂载的目录文件**

完成 OSS 挂载配置后，您可以通过以下方式访问 OSS 挂载目录中的文件：

### **通过终端访问**

1. **连接 Sandbox 实例终端**
  
  - 在 Sandbox 模板详情页，点击**在线调试**标签
  - 在沙箱列表中选择已创建并运行中的实例
  - 点击**连接沙箱**按钮
  - 点击**终端**按钮，等待终端连接成功
2. **验证挂载点**
  
  ```
  # 检查挂载点 df -h | grep -i oss # 预期输出：ossfs 16E 0 16E 0% /mnt/oss ​ # 查看挂载目录 ls -la /mnt/oss # 预期输出：显示 OSS 中的文件列表
  ```
3. **读取文件**
  
  ```
  # 读取 OSS 中的文件 cat /mnt/oss/test_oss_upload.txt # 预期输出：文件内容
  ```
4. **写入文件**
  
  ```
  # 写入文件到 OSS echo "Hello from Sandbox" > /mnt/oss/test_from_sandbox.txt ​ # 验证写入成功 cat /mnt/oss/test_from_sandbox.txt # 预期输出：Hello from Sandbox
  ```

### **通过代码访问**

在 Sandbox 实例中，您可以使用标准的文件系统 API 访问 OSS 挂载目录，就像访问本地文件系统一样：

**Python 示例**：

```
# 读取文件 with open('/mnt/oss/test.txt', 'r') as f: content = f.read() print(content) ​ # 写入文件 with open('/mnt/oss/output.txt', 'w') as f: f.write('Hello from Sandbox')
```

**说明**：

- OSS 挂载使用 ossfs 文件系统，支持标准的文件系统操作
- 写入操作会在文件关闭或调用 Flush 时同步到 OSS
- 不同 Sandbox 实例之间相互独立，不同实例中查询到的 OSS 挂载点内容可能不同

## 常见问题

### 提示OSS挂载失败，报错信息为`bucket not found`

请确认OSS访问地址、Bucket名称是否填写准确。

### 提示OSS挂载失败，报错信息为`host resolv error`或`deadline exceeded`

请确认Endpoint地址是否填写准确。

- Endpoint地址中的域名解析失败会导致`host resolv error`报错。
- 内网Endpoint不可跨地域使用。使用其他地域的内网Endpoint作为访问地址时，会出现连接超时，导致`deadline exceeded`报错。

### 挂载失败，报错信息为`invalid credentials`

请确认您为函数配置的RAM角色是否具备访问OSS的权限，权限信息如下所示。更多信息，请参见[使用函数角色授予函数计算访问其他云服务的权限](https://help.aliyun.com/zh/functioncompute/fc/grant-function-compute-permissions-to-access-other-alibaba-cloud-services)。

- **只读**：包括`oss:ListObjects`和`oss:GetObject`策略。
- **读写**：包括`oss:ListObjects`、`oss:GetObject`、`oss:PutObject`、`oss:DeleteObject`、`oss:ListParts`和`oss:AbortMultipartUpload`策略。

**说明**：`oss:ListObjects`为Bucket级别操作。因此，当您为特定的Bucket开启访问时，权限策略中需要包含Bucket级别的资源指示，例如`acs:oss:*:*:bucketName`。更多信息，请参见[RAM Policy](https://help.aliyun.com/zh/oss/user-guide/ram-policy/#section-an0-sb1-5sh)。

### 读取挂载的文件时，报错信息为`Input/output error`

请确认您配置的OSS Bucket的存储类型，其中存储类型为归档存储和冷归档存储时，存放到该Bucket的文件都是冻结状态，这类文件要解冻后才能正常访问。建议您配置的OSS Bucket存储类型为标准存储。

### 沙箱实例内访问挂载点出现`Transport endpoint is not connected`

如果沙箱实例内存规格较低、内存用量较大等，可能导致OSS挂载功能因内存不足而不可用，产生上述错误。请根据业务情况调高函数内存规格，建议使用OSS挂载点时函数内存规格不低于512 MB。

### 函数目录下写入的数据能持久保存吗？

沙箱实例被销毁的时候，在函数目录下写入的数据也会被删除。如果您希望数据可以持久保存，建议您配置挂载。配置NAS文件系统挂载或者配置OSS挂载均可以让数据持久保存。具体操作请参见[配置NAS文件系统](https://help.aliyun.com/zh/functioncompute/fc/configure-a-nas-file-system-for-fc)和[配置OSS对象存储](https://help.aliyun.com/zh/functioncompute/fc/user-guide/configure-an-oss-file-system-1)。

### 如何通过权限策略仅允许只读访问指定Bucket？

展开查看权限策略描述示例。请将示例中`bucketName`替换为指定的Bucket名称。更多信息，请参见[RAM Policy](https://help.aliyun.com/zh/oss/user-guide/ram-policy/#concept-y5r-5rm-2gb)。

### 如何通过权限策略允许读写访问指定Bucket？

展开查看权限策略描述示例。请将示例中`bucketName`替换为指定的Bucket名称。更多信息，请参见[RAM Policy](https://help.aliyun.com/zh/oss/user-guide/ram-policy/#concept-y5r-5rm-2gb)。

### 如何通过权限策略仅允许只读访问指定Bucket的子目录？

展开查看权限策略描述示例。请将示例中`bucketName`替换为指定的Bucket名称，`bucketPath`替换为指定的Bucket子目录。更多信息，请参见[RAM Policy](https://help.aliyun.com/zh/oss/user-guide/ram-policy/#concept-y5r-5rm-2gb)。

### 如何通过权限策略允许读写访问指定Bucket的子目录？

展开查看权限策略描述示例。请将示例中`bucketName`替换为指定的Bucket名称，`bucketPath`替换为指定的Bucket子目录。更多信息，请参见[RAM Policy](https://help.aliyun.com/zh/oss/user-guide/ram-policy/#concept-y5r-5rm-2gb)。

### 通过OSS挂载点写文件的过程中，从OSS侧观察文件为空

**原因说明**：
通过 OSS 挂载点写文件时，一般情况下，系统只在用户主动调用 Flush 或者关闭文件时，才将写入内容上传至 OSS 侧。

**解决方法**：

- 确保文件已正确关闭（在代码中使用`close()`或`with`语句）
- 如需立即同步，可以主动调用`flush()`方法

### 在OSS挂载点中，执行压缩、解压或文件传输等操作时响应较慢

**原因说明**：
OSS 本身不支持文件系统 API。当您将 OSS Bucket 挂载为目录之后，函数计算会组合封装 OSS API，实现文件系统 API 的效果。例如，OSS 本身不支持随机写，当您需要使用文件系统 API 变更 OSS 挂载点上现有的文件时，函数计算会将源文件从 OSS 全量下载并改写后重新上传到 OSS。

当文件系统 API 与 OSS API 功能对应时，例如顺序的文件读写，通常操作执行的性能较好。而需要组合封装 OSS API 实现的操作，例如压缩、解压可能用到的文件随机读写操作，可能需与 OSS 进行多次交互，故性能略差于本地文件系统。

**建议**：

- 对于需要频繁随机读写的操作，建议使用 NAS 文件系统
- 对于顺序读写操作，OSS 挂载性能较好

### 不同沙箱实例之间访问OSS挂载点会互相协调同步吗？

不同沙箱实例之间相互独立，不同实例中查询到的 OSS 挂载点内容可能不同。例如，通过沙箱实例 A 在 OSS 挂载点中创建文件 F 后，在沙箱实例 B 中可能无法实时查询到该文件。

**说明**：

- OSS 挂载使用 ossfs 文件系统，不同实例之间的文件操作是独立的
- 如果需要实时同步，建议在应用层面实现同步机制
