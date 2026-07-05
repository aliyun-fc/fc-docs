# 文件上传到OSS触发函数执行多次，要如何处理？

将文件上传到OSS后发现OSS触发器被多次触发，您需要查看OSS触发器设置的**触发事件**是否符合预期。

## **问题原因**

OSS触发器被多次触发，可能原因是设置的触发规则中包含通配符，因此单个文件上传过程中产生的多个事件均匹配成功，导致触发了多次函数执行。

例如，您通过分片上传功能上传文件到OSS，这个过程会依次触发`oss:ObjectCreated:InitiateMultipartUpload`、`oss:ObjectCreated:UploadPart`和`oss:ObjectCreated:CompleteMultipartUpload`事件。假如您将OSS触发器的**触发事件**设置为`oss:ObjectCreated:*`，通过OSS Browser工具上传一个12 MB的文件，分片大小设置为5 MB，那么您的函数将被触发执行5次。5次触发的事件分别为：

- `oss:ObjectCreated:InitiateMultipartUpload`
- `oss:ObjectCreated:UploadPart`
- `oss:ObjectCreated:UploadPart`
- `oss:ObjectCreated:UploadPart`
- `oss:ObjectCreated:CompleteMultipartUpload`

所以对于分片上传，**触发事件**需要设置为`oss:ObjectCreated:CompleteMultipartUpload`才只会被触发一次。

## **解决方案**

去除匹配规则中的通配符，精确添加所需的[事件类型](https://help.aliyun.com/zh/functioncompute/fc/user-guide/overview-of-oss-trigger#section-mf3-l4l-1nf)。例如，您可以设置触发器的**触发事件**为`oss:ObjectCreated:PutObject`、`oss:ObjectCreated:PostObject`和`oss:ObjectCreated:CompleteMultipartUpload`。这三个触发事件覆盖通过以下方式上传文件的情况：

- `oss:ObjectCreated:PutObject`：通过简单上传创建或覆盖文件。
- `oss:ObjectCreated:PostObject`：通过表单上传创建或覆盖文件。
- `oss:ObjectCreated:CompleteMultipartUpload`：完成分片上传。
