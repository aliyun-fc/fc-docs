# 投递 Flow 执行日志到日志服务

Flow 执行事件默认只能通过[GetExecutionHistory API 参考](https://help.aliyun.com/zh/document_detail/2590644.html)按需查询，无法实时推送到外部系统。通过日志投递功能，可将 Flow 执行事件实时写入指定的日志服务（SLS）日志库（Logstore），用于自定义日志分析、监控和告警。

**

**说明**

日志投递遵循 best-effort 原则，系统尽力投递但不保证 100% 送达。网络异常或服务故障期间，部分执行事件可能无法写入日志库。

## 前提条件

- 已在日志服务（SLS）控制台创建目标[日志项目（Project）](https://help.aliyun.com/zh/sls/manage-a-project/)和[日志库（Logstore）](https://help.aliyun.com/zh/sls/manage-a-logstore)。系统不会自动创建 SLS 资源，需预先完成创建。
- Flow 绑定的 RAM 角色（执行角色）需具备目标 Logstore 的写入权限。系统通过扮演角色（AssumeRole）获取临时凭证后向 SLS 写入日志，该角色需包含`log:PutLogs`权限。
- RAM 角色的信任策略需允许云工作流（CloudFlow）服务扮演该角色。在[RAM 控制台](https://ram.console.aliyun.com/)配置角色信任策略时，服务主体（Service）填写`fnf.aliyuncs.com`。示例：
  
  ```
  {"Statement": [{"Action": "sts:AssumeRole","Effect": "Allow","Principal": {"Service": ["fnf.aliyuncs.com"]}}],"Version": "1"}
  ```

## 配置日志投递

日志投递配置入口位于 AgentRun 控制台的 Flow 创建 Agent 页面，支持在创建流程或更新流程时启用。

访问路径：登录[AgentRun 控制台](https://functionai.console.aliyun.com)，在 Agent 运行时列表页面单击**创建 Agent**，在弹出的对话框中选择**工作流创建**。

### 创建流程时配置日志投递

1. 登录[AgentRun 控制台](https://functionai.console.aliyun.com)。
2. 在 Agent 运行时列表页面，单击**创建 Agent**，在弹出的对话框中选择**工作流创建**。
3. 在 Flow 创建 Agent 页面，填写 Agent 名称、描述等基础信息。
4. 在**执行角色配置**区域的**执行角色 ARN**下拉列表中，选择具备`log:PutLogs`权限的 RAM 角色。执行角色是 Flow 的全局权限配置，用于授权包括 SLS 日志写入在内的所有服务操作。若列表中无可用角色，单击**创建**跳转到 RAM 控制台创建角色。
5. 在**访问凭证**区域，选择访问凭证类型。建议选择**使用已有凭证**以保障数据安全；如选择**匿名访问**，系统将提示风险。
6. 在**日志投递**区域，打开**启用日志**开关。开关开启后，将展示日志项目和日志库配置字段。
7. 在**日志项目**下拉列表中，选择目标日志项目（Project）。
8. 在**日志库**下拉列表中，选择目标日志库（Logstore）。
9. 完成其他配置后，单击**下一步：流程编排**继续创建流程。

### 更新流程时修改日志投递配置

对于已创建的流程，可在编辑配置时启用或修改日志投递。

1. 在 AgentRun 控制台的 Agent 运行时列表中，单击目标 Agent 名称进入详情页，然后单击**编辑配置**。
2. 在**日志投递**区域，打开**启用日志**开关（若需关闭投递，则关闭该开关）。
3. 根据需要修改**日志项目**、**日志库**和**执行角色**配置。
4. 保存配置后，新的执行事件将按更新后的配置投递。

## 投递的日志格式

投递到日志库的事件内容与`GetExecutionHistory`API 返回的事件内容一致。每条日志记录包含以下顶层字段：

| SLS 字段 | 类型 | 示例值 | 说明 |
| --- | --- | --- | --- |
| `FlowName` | String | my-flow | 流程名称 |
| `FlowID` | String | flow-uuid-1234 | 流程唯一 ID |
| `ExecutionName` | String | exec-name 或 exec-name:uuid | 执行名称。Express 执行模式下会追加 :uuid 后缀 |
| `RoleArn` | String | acs:ram::1234567890:role/fnf-role | Flow 绑定的 RAM 角色 ARN |
| `EventType` | String | StateMachine | 事件类型分类，当前固定值为 StateMachine |
| `StateMachine` | String（JSON） | {"StepName":"Pass",...} | 步骤级事件详情，JSON 序列化字符串，结构见下表 |
| `Time` | String | 2025-01-01T00:00:00Z | 事件产生时间，RFC3339 格式 |

`StateMachine`字段的 JSON 结构：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `StepName` | String | 步骤名称 |
| `StepType` | String | 步骤类型，如 Pass、Task、Choice 等 |
| `Type` | String | 事件类型 |
| `EventDetail` | String（JSON） | 事件详情，包含 input、output、parameters、error 等信息 |
| `EventId` | Number | 事件 ID |
| `ScheduleEventId` | Number | 调度事件 ID |

## SLS 查询建议

### 配置字段索引

为通过`ExecutionName`、`FlowName`等字段查询投递的日志，建议为目标 Logstore 建立字段索引。

顶层字段（text 类型）：

| 字段（Key） | 索引类型 |
| --- | --- |
| `FlowName` | text |
| `FlowID` | text |
| `ExecutionName` | text |
| `RoleArn` | text |
| `EventType` | text |
| `Time` | text |

StateMachine 字段（json 类型，添加以下 JSON 子字段索引）：

| 子字段（JsonKey） | 索引类型 |
| --- | --- |
| `Type` | text |
| `StepName` | text |
| `StepType` | text |
| `EventId` | long |
| `ScheduleEventId` | long |
| `EventDetail` | text |
