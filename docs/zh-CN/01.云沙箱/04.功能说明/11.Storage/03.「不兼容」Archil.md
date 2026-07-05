# 「不兼容」Archil

E2B Storage 中的 Archil 文档介绍了在模板中安装 Archil CLI，并在沙箱运行时通过挂载令牌把 Archil disk 挂载到沙箱目录中。该能力依赖第三方 Archil 服务、挂载令牌、运行时挂载命令以及沙箱内文件系统挂载能力。

云沙箱当前不兼容该接入方式，不应提供 Archil 安装、挂载或共享磁盘示例。

## 不建议使用的接入方式

- 在模板中预装 Archil CLI。
- 在沙箱中执行 `archil mount`。
- 在沙箱销毁前执行 `archil unmount`。
- 依赖 Archil disk 在多个沙箱之间共享状态。

## 替代方向

如果业务需要跨沙箱共享数据，应使用云上持久化存储或业务系统管理状态。对于临时输入和输出，可以使用沙箱 Filesystem API 或下载 URL 完成单次任务的数据交换。

