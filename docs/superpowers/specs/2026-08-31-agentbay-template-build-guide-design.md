# AgentBay Linux 桌面模板制作说明设计

## 目标

补充 AgentBay Linux 桌面迁移指南中的模板制作说明，让用户可以优先使用 FC 已发布的 Desktop 镜像制作 Template，并在需要定制软件或桌面环境时，基于 Docker Hub 官方 Ubuntu 24.04 镜像自行构建兼容镜像。

## 修改范围

同步更新以下中英文文档：

- `docs/zh-CN/01.云沙箱/04.功能说明/14.迁移/2.AgentBay Linux 桌面迁移指南.md`
- `docs/en-US/01.FC Agent Sandbox/04.Features/14.Migration/2.AgentBay Linux Desktop Migration Guide.md`

不新增面向用户的独立页面，不修改能力映射、SDK 迁移示例和 noVNC 集成示例的功能边界。

## 内容设计

### 推荐路径：使用 FC Desktop 镜像

- 保留并突出当前验证过的默认稳定版本 `desktop:v0.0.44`。
- 保留 `e2b-desktop==2.4.1` 与 `desktop:v0.0.44` 的 35/35 验证记录。
- 说明镜像仓库、API URL、Domain 和目标资源必须位于同一地域。
- 推荐使用 4 vCPU、8192 MB 内存。
- 要求每次验证新镜像或新配置时使用新的、可追溯的 Template 名称，避免已有 Template 被直接复用。
- Template 构建完成后，通过实际创建 Sandbox、启动桌面流和销毁 Sandbox 完成冒烟验证。

### 进阶路径：自行构建桌面镜像

- 不引用无法被外部用户访问的内部参考仓库。
- 使用 Docker Hub 官方 `ubuntu:24.04` 作为示例基础镜像；构建目标固定为 `linux/amd64`，生产发布建议进一步固定镜像 digest。
- 给出精简的项目目录结构和 Dockerfile 骨架，覆盖 GNOME/Xvfb、x11vnc/noVNC、Chrome、字体、普通用户、桌面启动脚本、FC Sandbox runtime 入口及必要端口。
- 说明静态检查、本地容器构建、本地 noVNC 验证、推送至同地域镜像仓库、创建新 Template 和 Sandbox 冒烟验证的顺序。
- 明确容器桌面不应依赖完整 `systemd`、USB 或宿主机能力；用户需要自行维护软件版本、漏洞修复、镜像大小和启动稳定性。

## 安全与发布约束

- 不在 Dockerfile、镜像层、Template 或示例配置中写入 API Key、AK/SK 或其他凭证。
- 不把 `latest` 作为生产环境可复现版本依据。
- 不暴露内部镜像供应链、CI 变量、内部证书或内部仓库地址。
- 文档中的公开基础镜像使用 Docker Hub 官方地址；FC 已发布镜像继续使用当前公开给用户的地域化地址。

## 一致性要求

- 中英文标题层级、步骤、代码示例和注意事项保持一一对应。
- `desktop:v0.0.44` 始终作为推荐路径的默认稳定版本；Ubuntu 24.04 自建镜像是进阶定制路径，不表示默认镜像被替换。
- 全文涉及桌面组件的描述应区分默认 FC 镜像与用户自建镜像，避免将两条路径混写。

## 验证

- 运行 `git diff --check`。
- 检查中英文标题和关键代码块结构一致。
- 扫描并确认没有内部 Code 链接、内部凭证名和不应公开的镜像地址。
- 检查相对链接有效。
- 检查 `desktop:v0.0.44`、`e2b-desktop==2.4.1`、`ubuntu:24.04` 和 `linux/amd64` 的语义一致。

## 非目标

- 不发布或维护一个新的公共示例代码仓库。
- 不宣称用户自建镜像享有与 FC 默认镜像相同的验证和支持范围。
- 不改变 AgentBay 与 e2b-desktop 的能力映射结论。
- 不更新 FC Desktop 默认版本；版本变更需有独立的发布和验证依据。
