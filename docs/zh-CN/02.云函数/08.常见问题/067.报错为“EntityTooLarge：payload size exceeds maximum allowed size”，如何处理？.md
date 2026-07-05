# 报错为“EntityTooLarge：payload size exceeds maximum allowed size”，如何处理？

函数调用分为同步调用和异步调用，其中同步调用的最大Payload为32 MB，异步调用的最大Payload为128 KB。Payload大小不支持后台修改，如果您的业务的Payload超过了对应的限制，并且无法减小，建议您将输入作为文件上传到OSS，然后再通过OSS触发器触发函数。
