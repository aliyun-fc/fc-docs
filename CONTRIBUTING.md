# 贡献指南

感谢你帮助改进阿里云函数计算文档。本指南说明如何在本地预览文档、运行检查并提交变更。

## 准备环境

本仓库使用 Python 3.12、MkDocs Material 和 Make。安装依赖：

```bash
make install
```

## 本地预览

启动本地开发服务器：

```bash
make serve
```

脚本会从 `docs/`、`assets/` 和根目录 README 生成临时 MkDocs 源目录及配置。请勿手工修改 `_mkdocs_src/`、`_site/` 或 `mkdocs.generated.yml`。

## 提交前检查

运行以下命令完成脚本测试、文档结构检查和严格构建：

```bash
make check
```

Pull Request 的 CI 会运行同一命令；MkDocs 产生任何警告都会导致检查失败。

检查内容包括：

- Markdown 标题层级和 H1 数量；
- 本地文档、图片和媒体引用；
- 文件路径首尾空格；
- 单个资源文件大小；
- MkDocs 严格构建。

## 修改文档

- 中文文档放在 `docs/zh-CN/`，英文文档放在 `docs/en-US/`。
- 图片和媒体分别放在 `assets/zh-CN/` 与 `assets/en-US/`。
- 文件名沿用同级目录的数字前缀和命名方式。
- 每篇文档只保留一个 H1，标题层级逐级递进。
- 使用相对路径引用仓库内文档和资源。
- 不要提交真实 AccessKey、API Key、Token 或其他凭证。
- 平台自动生成的 API Reference 只放在各开发参考目录的 `API Reference/` 子目录。

如需自定义导航显示名称，可在文档 front matter 中设置：

```yaml
---
nav_title: 简短导航标题
---
```

## 提交 Pull Request

Pull Request 应说明修改范围、问题原因和验证结果。新增或替换图片时，请同时提交对应资源，并确认 `make check` 通过。
