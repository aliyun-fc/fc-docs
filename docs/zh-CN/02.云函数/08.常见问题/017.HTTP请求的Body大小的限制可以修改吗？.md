# HTTP请求的Body大小的限制可以修改吗？

函数计算对HTTP请求Body大小设置了上限，即同步调用请求Body的总大小不得超过32 MB，异步调用请求Body的总大小不得超过128 KB（最大支持调整到256 KB，如有需要，可[提交工单](https://selfservice.console.aliyun.com/ticket/createIndex)申请）。更多限制，请参见[HTTP/HTTPS协议使用限制](https://help.aliyun.com/zh/functioncompute/fc/user-guide/http-triggers-overview#p-m72-etl-83j)。

- 降低Body大小限制
  
  如果您需要自行调小HTTP Body大小的限制以拦截过大请求，可以在函数代码中主动设置Body限制。
- 分片上传
  
  超过函数计算设置的HTTP请求Body大小限制后，将在平台侧进行拦截，无法达到您的函数。您可以使用HTTP协议支持的分片上传功能将大的Body进行拆分传输。
