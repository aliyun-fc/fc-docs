# 「不兼容」管理 Volumes

E2B 支持创建、列出、连接和删除 Volume。云沙箱当前不兼容 E2B Volume 管理 API。

不要在云沙箱接入路径中使用以下能力：

- `Volume.create()`
- `Volume.list()`
- `Volume.connect()`
- `Volume.getInfo()`
- `Volume.delete()` 或同类删除能力

需要持久化数据时，请使用 OSS、NAS、数据库或业务系统已有存储。

