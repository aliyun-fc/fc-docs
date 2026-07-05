# 「不兼容」Cloud buckets

E2B Storage 中的 Cloud buckets 文档介绍了通过 FUSE 工具把对象存储挂载到沙箱目录，包括 Google Cloud Storage、Amazon S3 和 Cloudflare R2。典型方式是在模板中安装 `gcsfuse` 或 `s3fs`，再在沙箱运行时写入凭证并执行挂载命令。

云沙箱当前不兼容该接入方式，不应在官方功能说明中提供基于 FUSE 的对象存储挂载教程。

## 不建议使用的接入方式

- 在模板中安装 `gcsfuse`、`s3fs` 等挂载工具。
- 在沙箱内写入云厂商 Access Key、Service Account Key 或 R2 凭证。
- 在沙箱运行时执行 `gcsfuse`、`s3fs` 挂载命令。
- 将挂载后的目录作为跨沙箱持久化存储。

## 替代方向

如果业务需要访问对象存储，建议由业务服务端或受控 SDK 完成上传、下载和权限控制。需要把数据交给沙箱处理时，可以先通过 Filesystem API 写入输入文件，处理完成后再通过下载 URL 或业务系统取回结果。

