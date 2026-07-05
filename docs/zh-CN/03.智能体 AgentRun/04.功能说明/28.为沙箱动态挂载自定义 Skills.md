# 为沙箱动态挂载自定义 Skills

AgentRun Sandbox 支持通过 OSS 动态挂载自定义 Skills，使沙箱内置 Agent 在原有内置 Skills 之外，额外获得定制专属能力。自定义 Skills 存储在阿里云 OSS 中，沙箱启动时按配置从 Bucket 自动加载。

## **前提条件**

- 已在[AgentRun控制台](https://functionai.console.aliyun.com/cn-hangzhou/agent/runtime/agent-list)具备创建或管理沙箱的权限（代码解释器、浏览器、AIO 沙箱均支持动态挂载自定义 Skills，下文以 AIO 沙箱为例）。
- 持有阿里云账号，如使用 RAM 子账号，需已开通**OSS**相关权限。

**重要**：OSS Bucket 的创建与上传见下文**步骤二**。创建 Bucket 时，地域须与后续沙箱一致，或为沙箱创建页**OSS 配置**中下拉列表所支持的地域；生产环境下以**AgentRun 当前支持的地域**及控制台为准。

## **操作步骤**

### **步骤一：准备自定义 Skill 文件**

自定义 Skill 以目录形式组织，每个 Skill 对应一个独立目录：须包含`SKILL.md`；可按需增加`RULES`等文件（见下表）。

| **文件** | **说明** |
| --- | --- |
| `SKILL.md` | Skill 的功能说明，供内置 Agent 理解该 Skill 的用途和调用方式（必填） |
| `RULES` | （可选）Skill 的执行规则，定义约束与行为规范 |

完整目录结构示例：

```
skills/ ├── <your-skill-name>/ │ ├── SKILL.md │ └── RULES（可选） ├── <another-skill-name>/ │ └── SKILL.md
```

### **步骤二：创建 OSS Bucket 并上传 Skill 文件**

若无现成 Bucket，按下列步骤在目标地域新建并完成上传；若已有 Bucket，可从对应步骤进入并完成上传。地域须与后续沙箱一致，或为沙箱创建页**OSS 配置**中可选 Bucket 所在地域。更详细的 OSS 操作可参考[OSS 控制台创建 Bucket](https://help.aliyun.com/zh/oss/user-guide/create-buckets)、[上传文件](https://help.aliyun.com/zh/oss/user-guide/upload-objects)。

1. 登录[OSS 控制台](https://oss.console.aliyun.com/)，在**Bucket 列表**中单击**创建 Bucket**，地域请选择与后续沙箱所在地域一致，或在 AgentRun 沙箱创建页的**OSS 配置**中下拉列表所支持的地域，创建完成后进入该 Bucket。
2. 在 Bucket 的**文件管理**中单击**新建目录**，目录名填写`skills`（目录命名需符合 OSS 规范：UTF-8、长度 1～254 字符等）。
3. 进入`skills`目录，按照步骤一的目录结构上传 Skill 文件：单击**上传文件**，将本地已准备好的 Skill 子目录（每个目录内至少含`SKILL.md`，可按需包含`RULES`）上传到当前目录；或使用**上传文件夹**批量上传。上传目标路径为：`<your-bucket>/skills/<your-skill-name>/`。
  
  等待上传完成后，确认 Bucket 中路径结构如下：
  
  ```
  <your-bucket>/ └── skills/ ├── <your-skill-name>/ │ ├── SKILL.md │ └── RULES（可选） ...
  ```

### **步骤三：创建启用了动态 Skills 的沙箱**

1. 登录[AgentRun控制台](https://functionai.console.aliyun.com/cn-hangzhou/agent/runtime/agent-list)，在左侧导航栏单击**运行时与沙箱**>**Sandbox 沙箱**。
2. 单击**创建沙箱模板**，在弹出的对话框中选择沙箱类型（本文以**AIO 沙箱**为例，代码解释器、浏览器沙箱操作类似）。
3. 填写沙箱基本配置（名称、资源规格、浏览器类型、分辨率等）。
4. 打开**OSS配置**开关，添加挂载点以配置自定义 Skills 的 OSS 路径：
  
  **Bucket名称**选择步骤二中创建的 Bucket（可单击**刷新 Bucket 列表**）；
  
  **OSS目录**填写`skills`（与步骤二中 Bucket 内的目录名一致）。
  
  **挂载目录**为沙箱内挂载路径，可填写`/mnt/workspace`或保留默认；
  
  目录读写权限选择**只读**即可。
5. **添加环境变量**（必做）：在创建页的**环境变量**区域，按控制台要求添加与 OSS/Skills 相关的环境变量（变量名与取值以控制台当前说明为准）。未正确配置可能导致沙箱无法加载自定义 Skills。
6. 配置**执行角色**，选择一个有权访问步骤二中 OSS Bucket 的角色。
  
  **重要**：默认的`Agentrun-role`角色**没有**OSS 访问权限。须在 RAM 控制台为所用角色添加`AliyunOSSReadOnlyAccess`或`AliyunOSSFullAccess`策略，或选择一个已具备目标 Bucket 访问权限的自定义角色。跳过此步骤将导致沙箱无法加载自定义 Skills，MCP 服务也无法正常启动。
7. 按需配置凭证、网络等，单击**创建沙箱**，等待创建完成。
8. **创建完成后确认**：进入沙箱**详情**>**概览与配置**，在**环境变量**与**OSS存储配置**中确认：环境变量已按上一步正确填充；OSS 存储配置中 Bucket 名称、区域（与所选 Bucket 一致）、OSS 目录（如`/skills/`）、挂载路径已正确填充。

### **步骤四：启用 MCP 服务**

1. 沙箱创建完成后，在沙箱列表中单击目标沙箱卡片右下角的**详情**。
2. 在详情页左侧单击**集成与案例**，进入**MCP 集成**子标签页；再次确认**环境变量**与**OSS 配置**已正确填充（参见步骤三最后一步）。
3. 单击**启动服务配置**（或页面提示的**启动服务**），启动 MCP 服务。服务启动后，页面显示 MCP 服务地址，格式为：
  
  ```
  https://<账号ID>.agentrun-data.<地域>.aliyuncs.com/templates/<沙箱名称>/mcp
  ```
4. 在**配置**中查看或生成 API 密钥，供 MCP 客户端连接时使用。

### **步骤五：验证自定义 Skills 已生效**

将 MCP 服务地址和 API 密钥配置到 Agent 工具（如 DeepChat、Dify、n8n 等），发起以下验证：

1. 向 Agent 询问当前可用的 Skills 列表，确认自定义 Skills 出现在列表中。
2. 发起一个需要调用自定义 Skill 的任务，观察 Agent 是否正确调用。

**沙箱文件下载地址**：`https://${主账号id}.agentrun-data.${region}.aliyuncs.com/sandboxes/${sandboxid}/filesystem/download?path=/home/user/skills-output/{文件名}`

## **在 DeepChat 中使用 Skill Sandbox MCP（示例）**

以下以**DeepChat**客户端为例，说明如何配置并使用已启用动态 Skills 的**Skill Sandbox MCP**。更多生态工具集成方式请参见[在生态工具中集成 AgentRun Sandbox](在生态工具中集成 AgentRun Sandbox_6447608.xdita)。

1. **安装与配置 DeepChat**：从[DeepChat 开源仓库](https://github.com/ThinkInAIXYZ/deepchat)下载对应操作系统版本，在客户端中配置大模型（如 qwen-max 等）。
2. **配置 MCP 服务器**：打开 DeepChat，进入**设置**（或**MCP 设置**）页面；添加新的 MCP 服务器，选择**手动配置**或粘贴 JSON 配置，填写步骤四中获取的**MCP 服务地址**与**Bearer Token**（API 密钥）；保存后，DeepChat 会自动发现并列出该 Skill Sandbox 暴露的工具（含动态挂载的自定义 Skills）。
3. **使用 Skill Sandbox MCP**：在对话中直接描述任务，Agent 将自动选择并调用 Sandbox 中的工具（含已挂载的自定义 Skill）；可通过「列出当前可用工具/Skills」等提示，确认自定义 Skill 已出现在列表中并参与调用。

**提示**：若 MCP 服务启动失败，可到沙箱**详情**>**集成与案例**>**MCP 集成**检查环境变量与 OSS 配置，或重试启动服务。

## **支持说明与使用限制**

以下内容已与当前控制台能力对齐，便于判断动态挂载的适用范围与约束。

| **项目** | **说明** |
| --- | --- |
| **支持的沙箱类型** | **代码解释器**、**浏览器**、**AIO 沙箱**均支持动态挂载自定义 Skills；本文以 AIO 沙箱为例说明操作步骤，其他类型沙箱配置方式一致。 |
| **OSS 地域** | 生产环境下，**AgentRun 已开服地域**均可使用；OSS Bucket 地域需与沙箱所在地域一致或为创建沙箱时**OSS 配置**中可选列表所支持的地域（具体以控制台为准）。 |
| **Skill 目录结构** | Bucket 内需存在名为`skills`的目录；其下每个子目录对应一个 Skill，子目录内至少包含`SKILL.md`。`RULES`等文件为可选。目录与文件名需符合 OSS 命名规范。 |
| **执行角色** | 沙箱使用的执行角色必须具备目标 OSS Bucket 的读权限（如`AliyunOSSReadOnlyAccess`或自定义策略），否则 MCP 服务无法启动、自定义 Skills 无法加载。 |
| **与内置 Skills 关系** | 动态挂载的 Skills 与沙箱内置 Skills（如 docx、pdf、浏览器等）并存，内置 Agent 会同时识别并择优调用。 |

## **常见问题**

**Q：MCP 服务无法启动，控制台日志显示权限错误。**

A：这通常是因为沙箱执行角色没有 OSS 访问权限。请检查：

1. 进入沙箱**详情**>**沙箱管理**，手动新建一个实例，查看实例日志中的具体错误信息。
2. 如提示 OSS 访问被拒绝，请参考步骤三中的执行角色配置，为所用角色添加 OSS 访问策略后重试。

**Q：Agent 没有调用自定义 Skills，只使用了内置 Skills。**

A：请检查：

- OSS 中的文件路径和目录结构是否正确（需与[步骤一](#步骤一准备自定义-skill-文件)一致）。
- `SKILL.md`文件中的说明是否清晰，足以让 Agent 识别该 Skill 的用途。
- 尝试在提示词中明确说明希望使用的 Skill 名称。

**Q：沙箱实例销毁后文件下载链接失效。**

A：沙箱销毁后，沙箱内文件及下载链接随之失效。沙箱默认闲置 30 分钟后自动销毁，如需下载请在沙箱活跃期内完成。
