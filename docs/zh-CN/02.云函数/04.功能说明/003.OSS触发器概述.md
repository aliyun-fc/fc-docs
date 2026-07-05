# OSS触发器概述

OSS与函数计算集成后，OSS事件能触发相关函数执行，实现对OSS中的数据的自定义处理。本文介绍函数计算支持的OSS触发器的使用限制、事件类型及触发规则。

## 背景信息

OSS和函数计算通过OSS触发器实现无缝集成，您可以编写函数对OSS事件进行自定义处理，当OSS捕获到指定类型的事件后，OSS事件触发相应的函数执行。例如，您可以设置函数来处理PutObject事件，当您调用OSS的[PutObject](https://help.aliyun.com/zh/oss/developer-reference/putobject#reference-l5p-ftw-tdb)接口上传图片到OSS后，相关联的函数会自动被触发来处理该图片。

OSS和函数计算集成后，您可以自由地调用各种函数处理图像或音频数据，再把结果写回到多种存储服务中。整个架构中，您只需要专注于函数逻辑的编写，系统将以实时的、可靠的、大规模并行的方式处理海量的数据。

## **OSS触发器使用限制**

- 仅[EventBridge类别的OSS触发器](https://help.aliyun.com/zh/functioncompute/fc/user-guide/configure-an-eventbridge-based-oss-trigger)支持配置多个文件前缀和文件后缀。
- [原生OSS触发器](https://help.aliyun.com/zh/functioncompute/fc/user-guide/configure-a-native-oss-trigger-1)和[EventBridge类别的OSS触发器](https://help.aliyun.com/zh/functioncompute/fc/user-guide/configure-an-eventbridge-based-oss-trigger)配置的文件前缀和文件后缀都不支持正则匹配。
- 仅[EventBridge类别的OSS触发器](https://help.aliyun.com/zh/functioncompute/fc/user-guide/configure-an-eventbridge-based-oss-trigger)支持在一个Bucket内关联超过10个以上的OSS触发器。
  
  一般情况下，不推荐一个Bucket下关联10个以上的触发器，建议您创建新的Bucket，并基于新的Bucket创建触发器。

## OSS事件定义

当OSS系统捕获到相关事件后，会将事件信息编码为JSON字符串，传递给事件处理函数。OSS事件通知格式的详细信息，请参见[消息通知](https://help.aliyun.com/zh/oss/user-guide/real-time-processing-file-changes-oss-event-notifications#section-b01-shv-in3)。

已支持的OSS事件定义如下表所示。一种事件类型对应一个ObjectCreated、ObjectRemoved或ObjectModified类型的API，调用某个API并执行成功后会触发函数执行一次。

| **事件类型** | **事件名称** | **说明** |
| --- | --- | --- |
| ObjectCreated | oss:ObjectCreated:PutObject | 调用PutObject接口上传文件。更多信息，请参见[PutObject](https://help.aliyun.com/zh/oss/developer-reference/putobject#reference-l5p-ftw-tdb)。 |
| oss:ObjectCreated:PutSymlink | 调用PutSymlink接口针对OSS上的TargetObject创建软链接，您可以通过该软链接访问TargetObject。更多信息，请参见[PutSymlink](https://help.aliyun.com/zh/oss/developer-reference/putsymlink#reference-qzz-qzw-wdb)。 |  |
| oss:ObjectCreated:PostObject | 调用PostObject接口使用HTML表单上传文件到指定的Bucket。更多信息，请参见[PostObject](https://help.aliyun.com/zh/oss/developer-reference/postobject#reference-smp-nsw-wdb)。 |  |
| oss:ObjectCreated:CopyObject | 调用CopyObject接口拷贝一个在OSS上已经存在的对象。更多信息，请参见[CopyObject](https://help.aliyun.com/zh/oss/developer-reference/copyobject#reference-mvx-xxc-5db)。 |  |
| oss:ObjectCreated:InitiateMultipartUpload | 使用MultipartUpload模式传输数据前，必须先调用InitiateMultipartUpload接口来通知OSS初始化一个MultipartUpload事件。更多信息，请参见[InitiateMultipartUpload](https://help.aliyun.com/zh/oss/developer-reference/initiatemultipartupload#reference-zgh-cnx-wdb)。 |  |
| oss:ObjectCreated:UploadPart | 初始化一个MultipartUpload事件之后，可以根据指定的对象名和Upload ID来分块（Part）上传数据。更多信息，请参见[UploadPart](https://help.aliyun.com/zh/oss/developer-reference/uploadpart#reference-pnq-2px-wdb)。 |  |
| oss:ObjectCreated:UploadPartCopy | UploadPartCopy通过从一个已存在的Object中拷贝数据来上传一个Part。更多信息，请参见[UploadPartCopy](https://help.aliyun.com/zh/oss/developer-reference/uploadpartcopy#reference-t4b-vpx-wdb)。 |  |
| oss:ObjectCreated:CompleteMultipartUpload | 在将所有数据Part都上传完成后，必须调用CompleteMultipartUpload接口来完成整个文件的MultipartUpload。更多信息，请参见[CompleteMultipartUpload](https://help.aliyun.com/zh/oss/developer-reference/completemultipartupload#reference-lq1-dtx-wdb)。 |  |
| oss:ObjectCreated:AppendObject | 调用AppendObject接口以追加写的方式上传文件。更多信息，请参见[AppendObject](https://help.aliyun.com/zh/oss/developer-reference/appendobject#reference-fvf-xld-5db)。 |  |
| oss:ObjectCreated:* | 调用任何上述ObjectCreated类型的API执行成功后都会触发函数。 |  |
| ObjectRemoved | oss:ObjectRemoved:DeleteObject | 调用DeleteObject接口删除某个对象。更多信息，请参见[DeleteObject](https://help.aliyun.com/zh/oss/developer-reference/deleteobject#reference-iqc-mqv-wdb)。 |
| oss:ObjectRemoved:DeleteObjects | 调用DeleteMultipleObjects接口批量删除文件。更多信息，请参见[DeleteMultipleObjects](https://help.aliyun.com/zh/oss/developer-reference/deletemultipleobjects#reference-ydg-25v-wdb)。 |  |
| oss:ObjectRemoved:AbortMultipartUpload | 调用AbortMultipartUpload接口可以根据用户提供的Upload ID终止其对应的MultipartUpload事件。更多信息，请参见[AbortMultipartUpload](https://help.aliyun.com/zh/oss/developer-reference/abortmultipartupload#reference-txp-bvx-wdb)。 |  |
| ObjectModified | oss:ObjectModified:UpdateObjectMeta | 调用UpdateObjectMeta接口修改某个对象的属性。<br>**<br>**说明**<br>目前，支持该事件的地域包括：华东1（杭州）、华东2（上海）、华北1（青岛）、华北2（北京）、华北3（张家口）、华北5（呼和浩特）、华南1（深圳）和西南1（成都）。 |
| ObjectReplication | oss:ObjectReplication:ObjectCreated | 数据复制过程涉及的写入操作。 |
| oss:ObjectReplication:ObjectModified | 数据复制过程涉及的覆盖操作。 |  |
| oss:ObjectReplication:ObjectRemoved | 数据复制过程涉及的删除操作。 |  |

## OSS触发器触发规则

### 避免循环触发

**

**警告**

使用OSS触发器时，请注意避免循环触发。例如，一个典型的循环触发场景是OSS的某个Bucket上传文件事件触发函数执行，此函数执行完成后又生成了一个或多个文件再写回到OSS的Bucket里，这个写入动作又触发了函数执行，形成了链状循环。

为了避免循环触发函数产生不必要的费用，建议您配置文件前缀或文件后缀，例如将触发函数的文件的文件前缀设置为`src`，函数执行完成后生成文件的文件前缀设置为`dst`，生成的文件将不会再次触发函数。如果不设置文件前缀和文件后缀，表示匹配任意文件前缀和文件后缀。具体操作，请参见[步骤一：创建OSS触发器](https://help.aliyun.com/zh/functioncompute/fc/user-guide/configure-a-native-oss-trigger-1#section-lo1-872-rwb)。

### 原生OSS触发器配置规则

为了避免在同一个Bucket下创建重复的触发器导致单个事件同时触发多个触发器，函数计算限制单个Bucket下触发器配置必须满足以下条件：

- 触发事件、文件前缀和文件后缀组成的组合必须唯一。
- 新建触发器只有在其“触发事件 + 文件前缀 + 文件后缀”组合与已有触发器不冲突时，才能成功创建。

以下通过具体示例说明原生OSS触发器的配置规则：

| **已有触发器** | **新建触发器** | **新建触发器是否成功** | **说明** |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **触发事件** | **文件前缀** | **文件后缀** | **触发事件** | **文件前缀** | **文件后缀** |  |  |
| oss:ObjectCreated:PutObject | source | zip | oss:ObjectCreated:* | source | zip | 不成功 | oss:ObjectCreated:*是所有ObjectCreated类型事件的全集。新建触发器的事件oss:ObjectCreated:*匹配已有相同文件前后缀的触发器的事件oss:ObjectCreated:PutObject。 |
| source1 | zip1 | 成功 | 新建触发器和已有触发器的事件类型和**文件前缀**匹配，但**文件后缀**不匹配。 |  |  |  |  |
| oss:ObjectCreated:PutObject | source | zip | 不成功 | 新建触发器与已有触发器的事件类型、**文件前缀**和**文件后缀**都匹配。 |  |  |  |
| source | 1zip | 不成功 |  |  |  |  |  |
| source1 | zip | 不成功 |  |  |  |  |  |
| source | 无 | 不成功 | 新建触发器与已有触发器的事件类型和**文件前缀**匹配，**文件后缀**不设置则包含了后缀为zip的对象，即**文件后缀**也匹配。 |  |  |  |  |
| 无 | zip | 不成功 | 新建触发器与已有触发器的事件类型和**文件后缀**匹配，**文件前缀**不设置则包含了前缀为source的对象，即**文件前缀**也匹配。 |  |  |  |  |
| source1 | zip1 | 成功 | 新建触发器与已有触发器的事件类型和**文件前缀**匹配，但**文件后缀**不匹配。 |  |  |  |  |
| 1source | 1zip | 成功 | 新建触发器与已有触发器的事件类型和**文件后缀**匹配，但**文件前缀**不匹配。 |  |  |  |  |
| oss:ObjectCreated:PostObject | source | zip | 成功 | 新建触发器与已有触发器的事件类型不匹配。 |  |  |  |

**

**说明**

文件前缀匹配原则为前向匹配，文件后缀匹配原则为后向匹配。

以下介绍两种冲突类型，两种冲突同时存在，则新建触发器不成功，两种冲突都不存在或只存在其中一种冲突，新建触发器可以成功。

#### 事件类型冲突

| **已有触发器事件类型** | **新建触发器事件类型** | **冲突说明** |
| --- | --- | --- |
| `oss:ObjectCreated:PutObject` | `oss:ObjectCreated:*` | `oss:ObjectCreated:*`包含`oss:ObjectCreated:PutObject`，事件冲突。 |
| `oss:ObjectCreated:*` | `oss:ObjectCreated:PostObject` |  |

#### 路径匹配冲突

| **已有触发器路径** | **新建触发器路径** | **冲突说明** |
| --- | --- | --- |
| `source/.zip` | `1source/.zip` | 前缀不匹配，后缀匹配，路径不冲突 |
| `source/.zip` | `source/.zip1` | 前缀匹配，后缀不匹配，路径不冲突 |
| `source/.zip` | `source/.zip` | 前缀匹配，后缀匹配，路径冲突 |

**

**重要**

如果您希望一个OSS事件类型可以触发不同的函数进行不同的处理，即为不同的函数配置相同的OSS触发器，可以[创建EventBridge类别的OSS触发器](https://help.aliyun.com/zh/functioncompute/fc/user-guide/configure-an-eventbridge-based-oss-trigger)。

## **常见问题**

- [触发器不能正常触发函数执行怎么办？](https://help.aliyun.com/zh/functioncompute/fc/what-to-do-if-a-trigger-cannot-trigger-function-execution)
- [文件上传到OSS触发函数执行多次，要如何处理？](https://help.aliyun.com/zh/functioncompute/fc/what-to-do-if-a-function-is-triggered-multiple-times-upon-object-uploads)

## **相关文档**

- 配置触发器
  
  关于如何配置和使用原生OSS触发器和EventBridge类别的OSS触发器，请参见[配置原生OSS触发器](https://help.aliyun.com/zh/functioncompute/fc/user-guide/configure-a-native-oss-trigger-1)和[配置EventBridge类别的OSS触发器](https://help.aliyun.com/zh/functioncompute/fc/user-guide/configure-an-eventbridge-based-oss-trigger)。
- 触发器相关问题
  
  - 如果您希望查看函数的执行触发了哪个事件，可以手动在代码逻辑中打印事件类型日志，具体请参见[日志记录](https://help.aliyun.com/zh/functioncompute/fc/basics#section-8ba-eug-2or)。
  - 如果您希望在函数中调用另一个函数，可以使用API调用指定函数，具体请参见[函数可以相互调用吗？](https://help.aliyun.com/zh/functioncompute/fc/can-functions-invoke-each-other-1)。
- 触发器实践教程
  
  - 如果您需要实现解压上传到OSS的ZIP文件，请参见[使用函数计算实现自动解压上传到OSS的ZIP文件](https://help.aliyun.com/zh/functioncompute/fc/use-cases/use-function-compute-to-automatically-decompress-zip-files-uploaded-to)。
