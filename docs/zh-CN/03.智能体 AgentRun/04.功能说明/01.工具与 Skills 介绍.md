# 工具与 Skills 介绍

AgentRun 支持创建和管理多种类型的工具和技能，供 Agent 在运行时调用。您可以根据业务场景选择合适的类型和创建方式，将外部能力快速集成到 Agent 中。

登录[AgentRun 控制台](https://functionai.console.aliyun.com)，在左侧导航栏选择**工具与Skills**，即可管理和创建各类工具与技能。

## 工具与技能类型

AgentRun 支持以下类型的工具与技能：

| **类型** | **说明** | **适用场景** |
| --- | --- | --- |
| Skills | 通过 Markdown 或技能包定义的可复用技能 | 快速为 Agent 添加自定义能力，支持 AI 辅助生成 |
| MCP 工具 | 基于 Model Context Protocol 协议的工具 | 支持 MCP 协议的 Agent 平台，需要流式交互的场景 |
| Function Call 工具 | 基于函数调用能力的工具 | 支持 Function Calling 的大模型，如通义千问、GPT 等 |

## 创建方式

各类型工具支持以下创建方式：

| **类型** | **创建方式** | **说明** |
| --- | --- | --- |
| Skills | Markdown 定义 / 上传技能包 | 创建或导入技能包，支持 AI 辅助生成 |
| MCP 工具 | 远程连接 / 代码或代码包创建 / API/MCP 打包 | 支持远程 MCP Server 接入、本地部署，以及将多个 MCP 工具和 RESTful API 聚合为统一 MCP 网关 |
| Function Call 工具 | 导入 OpenAPI Spec / 手动录入 API / 代码或代码包创建 | 支持 OpenAPI 规范和 RESTful API |
| 工具市场 | 一键安装 | 从预置工具市场选择开箱即用的工具 |

## 在 Agent 中使用工具

工具的配置方式因 Agent 创建方式不同而有所差异：

- **快速创建 Agent**：在**工具与上下文**配置区域，通过以下标签页添加工具：
  
  - **Skills**标签页：添加已创建的 Skill，并可开启**允许 Skill 执行脚本**选项。
  - **工具**标签页：添加已创建的 MCP 工具和 Function Call 工具。
  - **沙箱**标签页：配置 Agent 运行的 Sandbox 沙箱环境。
  - **知识库**标签页：关联知识库，为 Agent 提供领域知识。
  - **记忆**标签页：配置 Agent 的记忆能力，使 Agent 在多轮对话中保持上下文。
- **代码创建 Agent**：先在**资源配置**>**工具与Skills**中创建所需工具，然后在代码中通过 AgentRun SDK 引用这些工具。
- **Flow 低代码创建 Agent**：在 Flow 编排画布中，通过添加工具节点来配置 Agent 可调用的工具。

添加后，Agent 在运行时可根据用户指令自动调用对应工具。

详情请参见[快速创建 Agent](https://help.aliyun.com/zh/functioncompute/fc/quickly-create-agent-no-code)、[代码创建 Agent](https://help.aliyun.com/zh/functioncompute/fc/create-agent-by-code-high-code)和[Flow 低代码创建 Agent](https://help.aliyun.com/zh/functioncompute/fc/create-agent-through-flow-low-code/)。

## 在 Sandbox 中使用工具

Sandbox 沙箱为 Agent 提供安全的隔离执行环境。Skill 可以在 Sandbox 中通过 MCP 协议加载和执行。

在创建 Sandbox 时，可在**Agent 和 Skills**中挂载 Skill，使 Agent 在沙箱环境内调用这些技能。

详情请参见[Sandbox 沙箱服务](https://help.aliyun.com/zh/functioncompute/fc/sandbox-service/)和[为沙箱动态挂载自定义 Skills](https://help.aliyun.com/zh/functioncompute/fc/dynamically-mount-custom-skills-for-sandboxes)。

## 相关操作

| **操作** | **说明** |
| --- | --- |
| [创建 Skill](https://help.aliyun.com/zh/functioncompute/fc/create-skills) | 通过 Markdown 定义或上传技能包创建 Skill |
| [创建 MCP 工具](https://help.aliyun.com/zh/functioncompute/fc/create-the-mcp-tool) | 通过远程连接、代码或 MCP 打包方式创建 MCP 工具 |
| [创建 Function Call 工具](https://help.aliyun.com/zh/functioncompute/fc/create-a-function-call-tool) | 通过导入 OpenAPI、手动录入或代码方式创建 Function Call 工具 |
| [工具市场](https://help.aliyun.com/zh/functioncompute/fc/tool-marketplace) | 从预置市场一键安装工具 |
