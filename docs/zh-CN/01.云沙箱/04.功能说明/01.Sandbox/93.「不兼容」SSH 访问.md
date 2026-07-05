# 「不兼容」SSH 访问

E2B 文档中包含 SSH access。云沙箱当前不兼容 E2B SSH 访问方式。

需要调试沙箱时，建议优先使用：

- `sandbox.commands.run()` 执行诊断命令。
- `sandbox.files.read()` 读取日志文件。
- `sandbox.getHost(port)` 暴露临时 HTTP 服务。
- PTY 能力完成需要交互终端的场景。

