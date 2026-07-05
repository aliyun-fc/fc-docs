# 使用 Sandbox Agent & Skills（公测中）

AgentRun Sandbox 的内置增强能力。启用后，沙箱自动装载一个内置 Agent 和一组开箱即用的 Skills，无需自行开发工具链。内置 Agent 负责任务路由与编排，可通过 MCP 协议暴露给外部 Agent 调用，处理代码编写与执行、网页浏览、Office 文档处理、文件操作等多类任务。

**

**说明**

使用过程涉及模型调用，公测期间免费。

## **适用场景**

| **痛点** | **Sandbox Agent & Skills 的解法** |
| --- | --- |
| 主 Agent 上下文过长，影响推理质量 | 将独立子任务下发给 Sandbox 执行，主 Agent 只接收结果 |
| 每个项目重复开发文档、浏览器等 Skills | 预置 docx/pdf/pptx 等常用 Skills，开箱即用 |
| Skills 脚本依赖污染主 Agent 运行环境 | Skills 在独立沙箱中执行，与主 Agent 完全隔离 |
| 恶意提示词或可执行脚本可能破坏主环境 | 沙箱提供隔离执行边界，规避安全风险 |

**典型场景：**

- 让 Agent 读取并总结 PDF 合同，生成 Word 修订版
- 让 Agent 爬取竞品网页后填写电子表格
- 将文档处理、代码执行等重型任务卸载给 Sandbox，主 Agent 专注业务逻辑

## **前提条件**

- 已开通 AgentRun 服务，并完成账号授权。如使用 RAM 子账号，需确保已开通函数计算和 AgentRun 相关权限。
- 使用新版控制台界面（进入控制台后选择体验新版）。

## **操作步骤**

### **步骤一：创建启用了 Agent & Skills 的沙箱**

1. 登录[AgentRun 控制台](https://functionai.console.aliyun.com/agentrun)，在左侧导航栏单击**运行时与沙箱**>**Sandbox沙箱**。
2. 单击**创建沙箱模板**，在弹出的对话框中选择沙箱类型。
  
  **说明**：Agent & Skills 功能支持**代码解释器沙箱**、**浏览器沙箱**和**AIO 沙箱**。AIO 沙箱集成了代码解释器与浏览器的一体化环境，可处理代码执行和网页操作两类任务，推荐使用。
3. 在创建沙箱页面，填写以下配置：
  
  | **配置项** | **说明** |
  | --- | --- |
  | **名称** | 英文字母和数字，不能含中文 |
  | **资源配置** | 按业务负载选择 CPU 和内存规格。代码解释器沙箱默认 2 核 4 GB，浏览器沙箱和 AIO 沙箱默认 4 核 8 GB |
  | **运行时环境** | **默认运行时**（推荐）：预配置的多语言运行环境，开箱即用；或选择**自定义运行时**使用容器镜像 |
  | **浏览器类型** | Chromium（默认，仅浏览器沙箱和 AIO 沙箱需配置） |
  | **分辨率** | 1280×1024（默认） |
  | **执行角色** | 授予函数计算服务访问其他阿里云服务的权限（如需访问 OSS，需添加 AliyunOSSFullAccess 策略） |
  | **凭证配置** | 选择已有凭证或匿名访问 |
4. 在**Agent 和 Skills**配置区域，打开**启用 Agent 和 Skills**开关。
  
  - **代码解释器沙箱**：内置 Coding Agent，专注代码生成、代码优化、代码 Review 等编程任务。
  - **浏览器沙箱 / AIO 沙箱**：内置 Agent，可处理网页访问和浏览器操作、Word/PDF/PPT 等文档处理、文件操作等任务
5. 按需展开**高级配置**完成其他设置，然后单击**创建沙箱**。

### **步骤二：启动 MCP 服务并获取接入地址**

1. 沙箱创建完成后，在沙箱列表中单击该沙箱卡片右下角的**详情**。
2. 在沙箱详情页，单击**集成与案例**标签页。
3. 在**MCP 集成**子页面，单击**启动服务**。
  
  服务启动后，页面显示**MCP 服务已启动**，并提供以下信息：
  
  | **项目** | **内容** |
  | --- | --- |
  | 传输协议 | Streamable HTTP |
  | 服务地址 | `https://<账号ID>.agentrun-data.<地域>.aliyuncs.com/templates/<沙箱名称>/mcp` |
  | 支持的工具 | 浏览器操作、文件系统、Office 文档处理等内置工具 |
4. 单击**配置 MCP 服务器**子标签，复制标准 MCP 配置示例：
  
  ```
  { "mcpServers": { "<沙箱名称>": { "url": "https://<账号ID>.agentrun-data.<地域>.aliyuncs.com/templates/<沙箱名称>/mcp" } } }
  ```

### **步骤三：在 Agent 中通过 MCP 调用沙箱**

将 MCP 服务地址配置到您的 Agent 或编排工具中，Agent 即可通过 MCP 协议调用沙箱内置的所有工具。

支持任意兼容 MCP Streamable HTTP 协议的客户端：

- DeepChat：开源 AI 对话客户端，支持可视化配置 MCP 服务器。下载地址：[github.com/ThinkInAIXYZ/deepchat](https://github.com/ThinkInAIXYZ/deepchat)
  
  配置指南：
  
  1. 进入 DeepChat 的**MCP 设置**，点击**新增**。
  2. 在**添加服务器**页面点击**跳过至手动配置**。
  3. **服务器类型**：选择**可流式传输的 HTTP 请求 (HTTP)**。
  4. **基础 URL**：填入 Sandbox 中的 URL。
    
    （格式：`https://<账号ID>.agentrun-data.<地域>.aliyuncs.com/templates/<沙箱名称>/mcp`）
- Claude Desktop、Cursor 等支持 MCP 的 Agent 工具
- Dify、n8n、Langchain 等编排框架。

## **内置 Skills 列表**

| **内置 Skill** | **功能描述** | **适用沙箱类型** |
| --- | --- | --- |
| [docx](https://github.com/anthropics/skills/blob/main/skills/docx/SKILL.md) | 文档创建、编辑和分析，支持修订追踪、批注、格式保留和文本提取 | 全部 |
| [pdf](https://github.com/anthropics/skills/blob/main/skills/pdf/SKILL.md) | PDF 处理工具包，支持文本/表格提取、创建、合并/拆分及表单处理 | 全部 |
| [pptx](https://github.com/anthropics/skills/blob/main/skills/pptx/SKILL.md) | 演示文稿创建、编辑和分析，支持内容修改、布局调整和批注 | 全部 |
| [xlsx](https://github.com/anthropics/skills/blob/main/skills/xlsx/SKILL.md) | 电子表格创建、编辑和分析，支持公式、格式设置、数据分析和可视化 | 全部 |
| [internal-comms](https://github.com/anthropics/skills/tree/main/skills/internal-comms) | 编写状态报告、领导层更新、新闻通讯等内部沟通文档 | 全部 |
| [mcp-builder](https://github.com/anthropics/skills/blob/main/skills/mcp-builder/SKILL.md) | 构建高质量 MCP 服务器的专家指南，支持 Python（FastMCP）和 Node/TypeScript | 全部 |
| [frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design) | 创建生产级前端界面，构建 Web 组件、页面和应用程序 | 全部 |
| **filesystem** | 文件系统操作工具集，支持内容搜索（grep/find/glob）、批量文件操作、目录管理 | 全部 |
| **browseruse-expert** | 浏览器自动化专家，使用结构化 accessibility tree 完成网页访问、表单填写、数据爬取、截图等任务 | 浏览器沙箱 / AIO 沙箱 |

## **关闭 MCP 服务**

在沙箱**详情**>**集成与案例**>**MCP集成**页面，单击**关闭服务**即可停止 MCP 服务。沙箱模板本身不受影响，下次需要时重新启动即可。

## **使用建议**

- **合理控制工具数量**：Agent 在工具列表较少时推理质量更优。建议仅启用与当前任务匹配的 Skills，避免同时挂载过多工具。
- **注意 AIO 沙箱的性能特点**：AIO 沙箱集成了浏览器能力，内置 Agent 处理任务时可能自动调用浏览器工具，响应时间比纯代码解释器沙箱略长。如任务不涉及网页操作，可考虑使用代码解释器沙箱。
- **沙箱空闲超时**：沙箱实例默认闲置 30 分钟后自动销毁，创建模板时可按需调整超时时长（沙箱 TTL 默认 6 小时）。销毁后重新发起调用即可自动恢复。
