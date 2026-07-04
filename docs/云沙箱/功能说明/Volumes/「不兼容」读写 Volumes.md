# 「不兼容」读写 Volumes

E2B Volume 提供独立的文件读写 API。云沙箱当前不兼容这些接口。

不要在云沙箱文档中提供以下正式示例：

- `volume.readFile()`
- `volume.writeFile()`
- `volume.list()`
- `volume.makeDir()`
- `volume.remove()`

沙箱内临时文件读写请使用[Filesystem](../Filesystem/概览.md)。跨沙箱持久数据请使用外部存储。

