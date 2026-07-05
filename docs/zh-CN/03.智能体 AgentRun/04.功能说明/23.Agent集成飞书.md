# Agent集成飞书

本文介绍如何将函数计算 AgentRun 中的 Agent 接入飞书，实现在飞书群聊或私聊中通过 @机器人 与 Agent 进行对话交互。

## 前提条件

- 已开通函数计算服务并创建 AgentRun Agent。具体操作，可参见[快速创建Agent（无代码）](https://help.aliyun.com/zh/functioncompute/fc/quickly-create-agent-no-code)。
- 拥有飞书企业管理员权限，可登录[飞书开放平台](https://open.feishu.cn/)。

## 步骤一：创建飞书应用

### 1. 创建应用并获取凭证

1. 登录[飞书开放平台](https://open.feishu.cn/)。
2. 单击**创建企业自建应用**，填写应用名称和描述，选择应用图标，单击**创建**。
3. 在左侧导航栏单击**凭证与基础信息**，复制**App ID**和**App Secret**。
  
  App Secret 仅在创建时显示一次，请妥善保存。如果遗失，需要重新生成。

### 2. 导入所需权限

1. 在左侧导航栏单击**权限管理**。
2. 单击**批量导入/导出权限**按钮，粘贴以下 JSON 配置：
  
  ```
  { "scopes": { "tenant": [ "aily:file:read", "aily:file:write", "application:application.app_message_stats.overview:readonly", "application:application:self_manage", "application:bot.menu:write", "cardkit:card:write", "contact:user.employee_id:readonly", "corehr:file:download", "docs:document.content:read", "event:ip_list", "im:chat", "im:chat.access_event.bot_p2p_chat:read", "im:chat.members:bot_access", "im:message", "im:message.group_at_msg:readonly", "im:message.group_msg", "im:message.p2p_msg:readonly", "im:message:readonly", "im:message:send_as_bot", "im:resource", "sheets:spreadsheet", "wiki:wiki:readonly" ], "user": [ "aily:file:read", "aily:file:write", "im:chat.access_event.bot_p2p_chat:read" ] } }
  ```
3. 单击**下一步**，确认新增权限，单击**申请开通**。

以上 JSON 包含 22 项 tenant 范围权限和 3 项 user 范围权限，涵盖即时消息、文件读写、文档读取、电子表格、知识库等能力。请确保所有权限均已成功开通，否则 Agent 部分功能可能无法正常使用。

### 3. 启用机器人能力

1. 在左侧导航栏单击**添加应用能力**。
2. 选择**按能力添加**页签，找到**机器人**卡片，单击**配置**。

## 步骤二：在 AgentRun 配置飞书集成

1. 登录[AgentRun 控制台](https://functionai.console.aliyun.com/agent/runtime/agent-list)。
2. 单击目标 Agent 名称，进入 Agent 详情页。
3. 单击**集成与发布**页签，单击**IM集成**，单击**添加IM机器人**。
4. 在**添加IM机器人**面板中，**机器人模式**选择**标准机器人**，**选择平台**选择**飞书机器人**，并填写以下信息：
  
  | 参数 | 说明 |
  | --- | --- |
  | **机器人名称** | 输入机器人的展示名称，最多 128 个字符。 |
  | **描述** | （可选）输入机器人的描述信息，最多 256 个字符。 |
  | **机器人模式** | 选择**标准机器人**，使用 Agent Endpoint 进行消息处理。 |
  | **选择 Endpoint** | 选择已发布的 Agent Endpoint，机器人将通过该 Endpoint 处理消息。 |
  | **选择协议规范** | 选择消息处理的协议规范。如尚未创建，可单击**添加协议**新建，或单击**刷新协议列表**更新。 |
  | **飞书 App ID** | 在[步骤一](#section-step1)中获取的飞书应用 App ID。可在**飞书开放平台**的**应用管理 - 应用详情 - 凭证**页面获取。 |
  | **飞书 App Secret** | 在[步骤一](#section-step1)中获取的飞书应用 App Secret。 |
  | **创建后立即启用** | 默认勾选。创建成功后机器人立即运行并响应 IM 消息；若取消勾选，创建后机器人为停用状态，可在列表中手动启用。 |
5. 单击**创建机器人**，完成飞书集成配置。
  
  **
  
  **说明**
  
  机器人配置后将自动在企业账号下部署 IM 服务函数（一个主账号复用同一个函数），并预留 1 个实例（规格 1C/1G、可按需手动扩缩容），用于与机器人保持长连接通信，函数预留涉及计费，详见[计费概述](https://help.aliyun.com/zh/functioncompute/fc/product-overview/billing-overview-of-fc)。

### 配置飞书事件订阅

完成 AgentRun 侧配置后，返回飞书开放平台配置事件订阅，使机器人能够接收用户消息。

1. 在飞书开放平台左侧导航栏单击**事件与回调**。
2. 在**事件配置**页签中单击**订阅方式**，选择**使用长连接接收事件**，单击**保存**。
3. 在**事件配置**页面，单击**添加事件**，搜索事件`im.message.receive_v1`（接收消息），单击**确认添加**。

### 发布飞书应用

1. 在飞书开放平台左侧导航栏单击**版本管理与发布**。
2. 单击**创建版本**，填写应用版本号和更新说明，单击**保存**。
3. 提交审核并发布应用。
  
  应用发布后，在可见范围内的飞书用户才能使用该机器人。

## 步骤三：在飞书中使用 Agent

完成配置后，您可以在飞书群聊或私聊中与 Agent 进行对话。

### 群聊中使用

1. 在飞书中创建群聊或打开已有群聊。
2. 在群设置中添加您在步骤一中创建的机器人。
3. 在群聊中 @机器人名称并输入问题，即可与 Agent 对话。

### 私聊中使用

在飞书搜索栏中搜索机器人名称，打开机器人对话窗口，直接发送消息即可与 Agent 进行私聊对话。
