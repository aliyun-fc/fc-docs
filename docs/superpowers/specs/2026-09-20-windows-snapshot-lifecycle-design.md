# Windows Snapshot 生命周期最佳实践设计

## 背景

`docs/zh-CN/01.云沙箱/05.最佳实践/11.使用 Windows Computer Use Sandbox.md`
目前只覆盖 Windows Desktop 模板构建、桌面操作和 noVNC 访问，没有说明如何从运行中的
Windows 沙箱创建 Snapshot，再从 Snapshot 恢复新的 Windows 沙箱。

本次参考
`/Users/chenquan/Workspace/fc/fc-sandbox/e2b-demos/e2b-windows-demos/01_windows_snapshot_lifecycle.py`
补充一套可直接运行的完整生命周期示例。

## 目标

- 保留现有 Windows Computer Use 和 noVNC 示例。
- 新增 Windows Template → Sandbox → Snapshot → Sandbox → noVNC 的完整流程。
- 文档内提供完整、可复制运行的 Python 脚本，不依赖仓库外示例文件。
- 删除参考脚本中只用于排查耗时的里程碑日志，但保留影响正确性的重试、就绪检测和资源清理。
- 与现有 Snapshot 功能文档互相引用，避免重复维护所有 API 规则。

## 非目标

- 不修改平台 API 或 SDK。
- 不新增 Windows 镜像制作说明；Windows 镜像仍由官方提供。
- 不补充英文版 Windows 最佳实践。
- 不在文档中公开真实镜像地址、API Key、Token 或 noVNC 凭证。

## 文档结构

在现有最佳实践中新增“使用 Snapshot 保存和恢复 Windows 沙箱”章节，包含：

1. 使用场景和五步生命周期。
2. 白名单、第二代运行时、镜像、规格、SDK 版本和网络配置等前置条件。
3. `.env` 配置模板。
4. 完整 Python 脚本。
5. 运行命令、预期输出、资源清理和常见失败处理。
6. 指向 Snapshot 功能说明的链接。

## 脚本设计

### 配置

脚本从同目录 `.env` 加载配置，并用 `override=True` 保证地域、Endpoint、镜像和 VPC 参数
来自同一份配置。必填项为 `E2B_API_KEY`、`E2B_API_URL`、`E2B_DOMAIN` 和
`ROOTFS_IMAGE`；其余参数提供安全默认值。

### 生命周期

1. 使用官方 Windows 镜像构建 `windows-osworld` 第二代运行时模板。
2. 使用模板 ID 创建源沙箱。
3. 等待 Windows 命令服务和 noVNC 首帧就绪后创建有名 Snapshot。
4. 使用 Snapshot ID 创建恢复沙箱，并再次验证 Windows 命令服务。
5. 输出恢复沙箱的 noVNC URL。

### 可靠性

- Template 构建轮询直到 `ready`，遇到 `error` 或超时立即失败。
- `Sandbox.create` 响应断开时，按源 Template/Snapshot ID 查找已创建实例，避免重复创建。
- Snapshot 请求断开或暂时返回 503 时，按 Snapshot 名和源沙箱查询服务端结果，避免重放
  非幂等请求。
- 创建 Snapshot 前完成 Windows 服务探测和 RFB 首帧探测，避免保存尚未完成桌面初始化的状态。
- 默认销毁源沙箱、保留恢复沙箱供用户访问；失败时清理所有已创建沙箱。用户可通过环境变量
  改变清理策略。

### 精简原则

- 删除耗时里程碑、重复状态输出和调试日志。
- 保留参考脚本中已经验证过的最小 WebSocket/RFB 首帧探测实现，不再引入额外依赖；该实现
  只覆盖桌面就绪检查所需的握手和原始帧读取。
- 保留清晰的阶段输出以及最终的 Template ID、Snapshot ID、恢复沙箱 ID 和 noVNC URL。

## 安全性

- `.env` 示例只使用占位符。
- 明确 noVNC URL 包含访问凭证，不得写入持久日志、提交到仓库或公开分享。
- 生产环境建议通过受控后端代理访问，或采用带鉴权的 Desktop Stream。
- 示例使用 `finally` 清理资源，避免异常路径遗留持续计费的沙箱。

## 验证

- 从 Markdown 代码块提取完整脚本，使用 Python 3.12 执行 `py_compile`。
- 检查 `.env` 中使用的变量与脚本读取项一致。
- 运行仓库单元测试、文档结构检查和 MkDocs 严格构建：`make check`。
- 人工审查相对链接、标题层级、占位凭证和清理路径。
