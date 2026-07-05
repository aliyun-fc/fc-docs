# 授权RAM用户使用 AgentRun

本文介绍如何为RAM用户授予AgentRun产品不同级别的权限策略。

## **前提条件**

已[创建RAM用户](https://help.aliyun.com/zh/ram/user-guide/create-a-ram-user#task-187540)。

## **背景信息**

本文提供通过[自定义权限策略](#4dead0b503vj5)的方式授予 RAM 用户使用 AgentRun 的权限。

若您想了解权限策略的更多信息，请参考[权限策略基本元素](https://help.aliyun.com/zh/ram/policy-elements)和[权限策略判定流程](https://help.aliyun.com/zh/ram/policy-evaluation-process)。

## **自定义权限策略**

使用阿里云账号（主账号）或 RAM 管理员登录[RAM控制台](https://ram.console.aliyun.com/overview)。为 RAM 用户授予以下自定义权限，具体操作请参见[管理RAM用户的权限](https://help.aliyun.com/zh/ram/user-guide/grant-permissions-to-the-ram-user)。

### **完整权限策略**

此自定义策略包含了 AgentRun 所有功能所需的所有权限。推荐配置此策略以获得最佳体验。

**完整自定义策略**

```
{ "Version": "1", "Statement": [ { "Effect": "Allow", "Action": [ "fnf:List*", "fnf:Describe*", "fnf:Get*", "fnf:CreateFlow", "fnf:UpdateFlow", "fnf:DeleteFlow", "fnf:DeleteFlowVersion", "fnf:UpdateFlowDraft", "fnf:PublishFlowVersion", "fnf:CreateFlowAlias", "fnf:UpdateFlowAlias", "fnf:DeleteFlowAlias", "fnf:StartExecution", "fnf:StartSyncExecution", "fnf:StartDebugExecution", "fnf:StopExecution" ], "Resource": "*" }, { "Effect": "Allow", "Action": [ "agentrun:List*", "agentrun:Get*", "agentrun:CreateAgentRuntime", "agentrun:UpdateAgentRuntime", "agentrun:DeleteAgentRuntime", "agentrun:PublishRuntimeVersion", "agentrun:CreateAgentRuntimeEndpoint", "agentrun:UpdateAgentRuntimeEndpoint", "agentrun:DeleteAgentRuntimeEndpoint", "agentrun:CreateModelService", "agentrun:UpdateModelService", "agentrun:DeleteModelService", "agentrun:CreateModelProxy", "agentrun:UpdateModelProxy", "agentrun:DeleteModelProxy", "agentrun:CreateCredential", "agentrun:UpdateCredential", "agentrun:DeleteCredential", "agentrun:CreateTemplate", "agentrun:UpdateTemplate", "agentrun:DeleteTemplate", "agentrun:ActivateTemplateMCP", "agentrun:StopTemplateMCP", "agentrun:StopSandbox", "agentrun:RetrieveMemory", "agentrun:UpdateMemory", "agentrun:CreateMemory", "agentrun:DeleteMemory", "agentrun:StartBrowserSession", "agentrun:StopBrowserSession", "agentrun:CreateCustomDomain", "agentrun:UpdateCustomDomain", "agentrun:DeleteCustomDomain", "agentrun:CreateSandbox", "agentrun:CreateMemoryCollection", "agentrun:UpdateMemoryCollection", "agentrun:DeleteMemoryCollection", "agentrun:CreateKnowledgeBase", "agentrun:UpdateKnowledgeBase", "agentrun:DeleteKnowledgeBase", "agentrun:InvokeRuntime", "agentrun:InvokeSandbox" ], "Resource": "*" }, { "Effect": "Allow", "Action": [ "devs:List*", "devs:Get*", "devs:Fetch*", "devs:Preview*", "devs:CreateProject", "devs:UpdateProject", "devs:UpdateEnvironment", "devs:DeployEnvironment", "devs:RenderServicesByTemplate", "devs:DeployServices", "devs:CreateToolset", "devs:UpdateToolset", "devs:DeleteToolset", "devs:CreateArtifact" ], "Resource": "*" }, { "Effect": "Allow", "Action": [ "fc:List*", "fc:Get*", "fc:Describe*", "fc:CreateFunction", "fc:UpdateFunction", "fc:DeleteFunction", "fc:CreateCustomDomain", "fc:UpdateCustomDomain", "fc:DeleteCustomDomain", "fc:PutProvisionConfig", "fc:DeleteProvisionConfig", "fc:InstanceExec" ], "Resource": "*" }, { "Effect": "Allow", "Action": [ "ram:List*", "ram:Check*", "ram:Get*", "ram:GenerateCredentialReport", "ram:CreateRole", "ram:AttachPolicyToRole", "ram:CreateServiceLinkedRole" ], "Resource": "*" }, { "Effect": "Allow", "Action": "ram:CreateServiceLinkedRole", "Resource": "*", "Condition": { "StringEquals": { "ram:ServiceName": [ "agentrun.fc.aliyuncs.com" ] } } }, { "Action": "bss:DescribeAcccount", "Resource": "*", "Effect": "Allow" }, { "Action": "bssapi:Query*", "Resource": "*", "Effect": "Allow" }, { "Effect": "Allow", "Action": "ram:PassRole", "Resource": "*", "Condition": { "StringEquals": { "acs:Service": [ "devs.aliyuncs.com", "fnf.aliyuncs.com", "fc.aliyuncs.com", "agentrun.fc.aliyuncs.com" ] } } }, { "Effect": "Allow", "Action": [ "resourcemanager:Check*", "resourcemanager:CreateServiceLinkedRole" ], "Resource": "*" }, { "Effect": "Allow", "Action": [ "oss:List*", "oss:Get*", "oss:PutBucket", "oss:PutBucketCors" ], "Resource": "*" }, { "Effect": "Allow", "Action": [ "vpc:List*", "vpc:Describe*", "vpc:CreateVpc", "vpc:CreateVSwitch", "vpc:ModifyVpcAttribute" ], "Resource": "*" }, { "Effect": "Allow", "Action": [ "ecs:Describe*", "ecs:AuthorizeSecurityGroup", "ecs:CreateSecurityGroup" ], "Resource": "*" }, { "Effect": "Allow", "Action": [ "arms:List*", "arms:Get*", "arms:Describe*", "arms:Search*", "arms:Query*", "arms:Check*", "arms:DoInsightsAction", "arms:ConfigApp", "arms:SaveTraceAppConfig", "arms:TagResources", "arms:UntagResources" ], "Resource": "*" }, { "Effect": "Allow", "Action": [ "xtrace:Get*", "xtrace:Read*", "xtrace:Describe*" ], "Resource": "*" }, { "Effect": "Allow", "Action": [ "cms:List*", "cms:Get*", "cms:Query*", "cms:Describe*", "cms:Cursor", "cms:BatchGet", "cms:BatchExport", "cms:Check*", "cms:BatchQuery*", "cms:CreatePrometheusVirtualInstance", "cms:OpenCmsService" ], "Resource": "*" }, { "Effect": "Allow", "Action": "cdn:Describe*", "Resource": "*" }, { "Effect": "Allow", "Action": "yundun-greenweb:Get*", "Resource": "*" }, { "Effect": "Allow", "Action": "cr:List*", "Resource": "*" }, { "Effect": "Allow", "Action": "yundun-cert:Describe*", "Resource": "*" }, { "Effect": "Allow", "Action": [ "log:Get*", "log:List*", "log:Query*", "log:ListProject", "log:DescribeService", "log:GetMLServiceResults", "log:OpenSlsService", "log:GetAgentInstanceConfig", "log:UpdateAgentInstanceConfig", "log:DeleteAgentInstanceConfig", "log:CreateAgentInstanceConfig" ], "Resource": "*" }, { "Effect": "Allow", "Action": [ "log:GetLogStoreLogs", "log:PostLogStoreLogs", "log:QueryPrometheusMetrics", "log:QueryMetrics", "log:RemoteWritePrometheus", "log:RemoteWrite" ], "Resource": "acs:log:*:*:project/*/logstore/aliyun-prom-*" }, { "Effect": "Allow", "Action": [ "log:GetLogStoreLogs", "log:GetIndex" ], "Resource": "acs:log:*:*:project/proj-xtrace-*/logstore/*" }, { "Effect": "Allow", "Action": [ "log:CreateIndex", "log:CreateLogStore", "log:CreateLogging", "log:CreateProject", "log:CreateMetricStore", "log:EnableService" ], "Resource": "*" }, { "Effect": "Allow", "Action": [ "bailiancontrol:ListWorkspaces", "bailiancontrol:CreateUser", "bailiancontrol:ListRoles", "bailiancontrol:ListUsers", "bailiancontrol:AttachWorkspaceToUser", "bailiancontrol:AttachRoleToUser", "sfm:ListIndex" ], "Resource": "*" }, { "Effect": "Allow", "Action": [ "ots:Get*", "ots:List*", "ots:CreateInstance", "ots:OpenOtsService" ], "Resource": "*" }, { "Effect": "Allow", "Action": [ "nas:Describe*", "nas:CreateFileSystem", "nas:DeleteFileSystem", "nas:ModifyFileSystem", "nas:CreateMountTarget", "nas:DeleteMountTarget", "nas:ModifyMountTarget", "nas:CreateAccessGroup", "nas:CreateAccessRule" ], "Resource": "*" }, { "Effect": "Allow", "Action": [ "apig:ListGateways", "apig:ListHttpApis", "apig:GetHttpApi", "apig:GetGateway", "apig:QueryConsumerAuthorizationRules", "apig:ListHttpApiRoutes", "apig:GetConsumer" ], "Resource": "*" } ] }
```

### **最小权限策略**

此自定义策略仅包含了 AgentRun 核心功能所需的权限。如需增加更多权限，可前往[AgentRun 服务与权限页面](https://functionai.console.aliyun.com/cn-hangzhou/agent/infra/permission)按需生成自定义策略 JSON。

**最小权限策略**

```
{ "Version": "1", "Statement": [ { "Effect": "Allow", "Action": [ "agentrun:List*", "agentrun:Get*", "agentrun:CreateAgentRuntime", "agentrun:UpdateAgentRuntime", "agentrun:DeleteAgentRuntime", "agentrun:PublishRuntimeVersion", "agentrun:CreateAgentRuntimeEndpoint", "agentrun:UpdateAgentRuntimeEndpoint", "agentrun:DeleteAgentRuntimeEndpoint", "agentrun:CreateModelService", "agentrun:UpdateModelService", "agentrun:DeleteModelService", "agentrun:CreateModelProxy", "agentrun:UpdateModelProxy", "agentrun:DeleteModelProxy", "agentrun:CreateCredential", "agentrun:UpdateCredential", "agentrun:DeleteCredential", "agentrun:CreateTemplate", "agentrun:UpdateTemplate", "agentrun:DeleteTemplate", "agentrun:ActivateTemplateMCP", "agentrun:StopTemplateMCP", "agentrun:StopSandbox", "agentrun:RetrieveMemory", "agentrun:UpdateMemory", "agentrun:CreateMemory", "agentrun:DeleteMemory", "agentrun:StartBrowserSession", "agentrun:StopBrowserSession", "agentrun:CreateCustomDomain", "agentrun:UpdateCustomDomain", "agentrun:DeleteCustomDomain", "agentrun:CreateSandbox", "agentrun:CreateMemoryCollection", "agentrun:UpdateMemoryCollection", "agentrun:DeleteMemoryCollection", "agentrun:CreateKnowledgeBase", "agentrun:UpdateKnowledgeBase", "agentrun:DeleteKnowledgeBase", "agentrun:InvokeRuntime", "agentrun:InvokeSandbox" ], "Resource": "*" }, { "Effect": "Allow", "Action": [ "devs:List*", "devs:Get*", "devs:Fetch*", "devs:Preview*", "devs:CreateProject", "devs:UpdateProject", "devs:UpdateEnvironment", "devs:DeployEnvironment", "devs:RenderServicesByTemplate", "devs:DeployServices", "devs:CreateToolset", "devs:UpdateToolset", "devs:DeleteToolset", "devs:CreateArtifact" ], "Resource": "*" }, { "Effect": "Allow", "Action": [ "fc:List*", "fc:Get*", "fc:Describe*", "fc:CreateFunction", "fc:UpdateFunction", "fc:DeleteFunction", "fc:CreateCustomDomain", "fc:UpdateCustomDomain", "fc:DeleteCustomDomain", "fc:PutProvisionConfig", "fc:DeleteProvisionConfig", "fc:InstanceExec" ], "Resource": "*" }, { "Effect": "Allow", "Action": [ "ram:List*", "ram:Check*", "ram:Get*", "ram:GenerateCredentialReport" ], "Resource": "*" }, { "Effect": "Allow", "Action": "ram:PassRole", "Resource": "*", "Condition": { "StringEquals": { "acs:Service": [ "devs.aliyuncs.com", "fnf.aliyuncs.com", "fc.aliyuncs.com", "agentrun.fc.aliyuncs.com" ] } } }, { "Effect": "Allow", "Action": [ "resourcemanager:Check*", "resourcemanager:CreateServiceLinkedRole" ], "Resource": "*" }, { "Effect": "Allow", "Action": [ "oss:List*", "oss:Get*" ], "Resource": "*" }, { "Effect": "Allow", "Action": [ "vpc:List*", "vpc:Describe*" ], "Resource": "*" }, { "Effect": "Allow", "Action": [ "arms:List*", "arms:Get*", "arms:Describe*", "arms:Search*", "arms:Query*", "arms:Check*" ], "Resource": "*" }, { "Effect": "Allow", "Action": [ "log:Get*", "log:List*", "log:Query*", "log:ListProject", "log:DescribeService", "log:GetMLServiceResults", "log:OpenSlsService", "log:GetAgentInstanceConfig" ], "Resource": "*" }, { "Effect": "Allow", "Action": [ "log:GetLogStoreLogs", "log:QueryPrometheusMetrics", "log:QueryMetrics" ], "Resource": "acs:log:*:*:project/*/logstore/aliyun-prom-*" }, { "Effect": "Allow", "Action": [ "log:GetLogStoreLogs", "log:GetIndex" ], "Resource": "acs:log:*:*:project/proj-xtrace-*/logstore/*" }, { "Effect": "Allow", "Action": [ "bailiancontrol:ListWorkspaces", "bailiancontrol:ListRoles", "bailiancontrol:ListUsers", "sfm:ListIndex" ], "Resource": "*" }, { "Effect": "Allow", "Action": [ "cms:GetCmsService", "ots:GetOtsServiceStatus", "arms:GetCommercialStatus", "arms:CheckCommercialStatus", "log:GetSlsService", "log:DescribeService" ], "Resource": "*" } ] }
```

## **角色创建与授权**

### **创建与授权流程**

AgentRun 依赖特定角色来执行操作。权限授权完毕后，首次进入页面，若必需的角色权限存在缺失，会有授权指引弹窗。按照弹窗提示操作即可完成角色创建和授权。

### **所需角色列表**

#### **AgentRun 整体**

| **角色** | **信任主体** | **策略/权限** | **说明** |
| --- | --- | --- | --- |
| AliyunDevsCustomRole | devs.aliyuncs.com | AliyunDevsAgentrunDeployPolicy | AgentRun 部署所需权限策略 |
| AliyunDevsFCServicesDeployPolicy | 函数服务部署所需权限策略 |  |  |
| AliyunDevsDefaultRole | devs.aliyuncs.com | AliyunDevsDefaultRolePolicy | 用于 AgentRun 服务角色的授权策略 |
| AliyunServiceRoleForFC | fc.aliyuncs.com | - | FC 服务关联角色 |
| AliyunServiceRoleForAgentRun | agentrun.aliyuncs.com | - | AgentRun 服务关联角色 |

#### **Flow Agent（可选）**

| **角色** | **信任主体** | **策略/权限** | **说明** |
| --- | --- | --- | --- |
| AliyunFnFExecutionRole | fnf.aliyuncs.com | AliyunFCInvocationAccess | 函数计算节点执行所需权限 |
| AliyunDevsReadOnlyAccess | 工具、MCP 节点执行所需权限 |  |  |
| AliyunFnFFullAccess | Flow Agent 内执行其他工作流所需权限 |  |  |
| AliyunAgentRunReadOnlyAccess | 使用 AgentRun 沙箱、工具等资源所需权限 |  |  |
| AliyunEventBridgePutEventsPolicy | 使用触发器所需权限 |  |  |
| AliyunBailianDataFullAccess | 知识库节点执行所需权限 |  |  |

## **功能模块权限详情**

### 1. Agent 管理

| **接口名称** | **产品/服务** | **说明** |
| --- | --- | --- |
| ListAgentRuntimes | AgentRun | 获取 Agent 列表 |
| GetAgentRuntime | AgentRun | 获取 Agent 详情 |
| CreateAgentRuntime | AgentRun | 创建 Agent |
| UpdateAgentRuntime | AgentRun | 更新 Agent |
| DeleteAgentRuntime | AgentRun | 删除 Agent |
| ListAgentRuntimeVersions | AgentRun | 获取版本列表 |
| PublishRuntimeVersion | AgentRun | 发布 Agent 版本 |
| ListAgentRuntimeEndpoints | AgentRun | 获取端点列表 |
| CreateAgentRuntimeEndpoint | AgentRun | 创建端点 |
| UpdateAgentRuntimeEndpoint | AgentRun | 更新端点 |
| DeleteAgentRuntimeEndpoint | AgentRun | 删除端点 |
| InstanceExec | FC | 登录实例 |

### 2. 工作流（Flow）管理

| **接口名称** | **产品/服务** | **说明** |
| --- | --- | --- |
| ListFlows | FNF | 获取 Flow 列表 |
| DescribeFlow | FNF | 获取 Flow 详情 |
| CreateFlow | FNF | 创建 Flow |
| UpdateFlow | FNF | 更新 Flow |
| DeleteFlow | FNF | 删除 Flow |
| DeleteFlowVersion | FNF | 删除 Flow 版本 |
| UpdateFlowDraft | FNF | 更新 Flow 草稿 |
| ListFlowVersions | FNF | 获取版本列表 |
| PublishFlowVersion | FNF | 发布 Flow 版本 |
| ListFlowAliases | FNF | 获取别名列表 |
| DescribeFlowAlias | FNF | 获取别名详情 |
| CreateFlowAlias | FNF | 创建别名 |
| UpdateFlowAlias | FNF | 更新别名 |
| DeleteFlowAlias | FNF | 删除别名 |
| StartExecution | FNF | 启动执行 |
| StartSyncExecution | FNF | 同步执行 |
| StartDebugExecution | FNF | 启动调试执行 |
| StopExecution | FNF | 停止执行 |
| ListExecutions | FNF | 获取执行列表 |
| DescribeExecution | FNF | 获取执行详情 |
| GetExecutionHistory | FNF | 获取执行历史 |
| DescribeAgentRunLogs | FNF | 获取 Agent 运行日志 |
| ListModelSets | Devs | 获取模型集列表 |
| GetModelSet | Devs | 获取模型集详情 |
| ListToolsets | Devs | 获取工具集列表 |
| GetToolset | Devs | 获取工具集详情 |
| FetchModelSetAuthorization | Devs | 获取模型集授权信息 |
| ListFunctions | FC | 获取函数列表（函数计算节点） |
| ListAliases | FC | 获取函数别名列表（函数计算节点） |
| ListFunctionVersions | FC | 获取函数版本列表（函数计算节点） |
| ListTriggers | FC | 获取触发器列表（函数计算节点） |
| GetCmsService | CMS | 获取 CMS 服务状态（基础监控） |
| OpenCmsService | CMS | 开通 CMS 服务（基础监控） |
| ListWorkspaces | Bailian | 获取百炼工作空间列表（知识库节点） |
| CreateUser | Bailian | 创建百炼用户（知识库节点） |
| ListRoles | Bailian | 获取百炼角色列表（知识库节点） |
| ListUsers | Bailian | 获取百炼用户列表（知识库节点） |
| AttachWorkspaceToUser | Bailian | 将工作空间关联到用户（知识库节点） |
| AttachRoleToUser | Bailian | 将角色关联到用户（知识库节点） |
| ListIndex | SFM | 获取索引列表（知识库节点） |
| ListModelServices | AgentRun | 获取 AgentRun 服务列表 |
| ListTemplates | AgentRun | 获取沙箱列表 |
| GetCredential | AgentRun | 获取模型服务、沙箱鉴权信息 |
| ListAgentRuntimes | AgentRun | 获取 Agent Runtime 列表 |
| ListAgentRuntimeEndpoints | AgentRun | 获取 Agent Runtime 端点列表 |

### 3. 模型服务管理

| **接口名称** | **产品/服务** | **说明** |
| --- | --- | --- |
| ListModelProviders | AgentRun | 获取模型提供商列表 |
| ListModelServices | AgentRun | 获取模型服务列表 |
| GetModelService | AgentRun | 获取模型服务详情 |
| CreateModelService | AgentRun | 创建模型服务 |
| UpdateModelService | AgentRun | 更新模型服务 |
| DeleteModelService | AgentRun | 删除模型服务 |
| ListModelProxies | AgentRun | 获取模型代理列表 |
| GetModelProxy | AgentRun | 获取模型代理详情 |
| CreateModelProxy | AgentRun | 创建模型代理 |
| UpdateModelProxy | AgentRun | 更新模型代理 |
| DeleteModelProxy | AgentRun | 删除模型代理 |

### 4. 凭证管理

| **接口名称** | **产品/服务** | **说明** |
| --- | --- | --- |
| ListCredentials | AgentRun | 获取凭证列表 |
| GetCredential | AgentRun | 获取凭证详情 |
| CreateCredential | AgentRun | 创建凭证 |
| UpdateCredential | AgentRun | 更新凭证 |
| DeleteCredential | AgentRun | 删除凭证 |
| GetAccessToken | AgentRun | 获取访问令牌 |

### 5. 沙箱与模板管理

| **接口名称** | **产品/服务** | **说明** |
| --- | --- | --- |
| ListTemplates | AgentRun | 获取沙箱列表 |
| GetTemplate | AgentRun | 获取沙箱详情 |
| CreateTemplate | AgentRun | 创建沙箱 |
| UpdateTemplate | AgentRun | 更新沙箱 |
| DeleteTemplate | AgentRun | 删除沙箱 |
| ActivateTemplateMCP | AgentRun | 激活沙箱 MCP |
| StopTemplateMCP | AgentRun | 停止沙箱 MCP |
| GetSandbox | AgentRun | 获取沙箱实例详情 |
| StopSandbox | AgentRun | 停止沙箱实例 |
| CreateSandbox | AgentRun | 创建沙箱实例 |
| ListSandboxes | AgentRun | 获取沙箱实例列表 |

### 6. 记忆存储

#### **6.1. 记忆存储管理**

| **接口名称** | **产品/服务** | **说明** |
| --- | --- | --- |
| ListMemoryCollections | AgentRun | 获取记忆存储列表 |
| GetMemoryCollection | AgentRun | 获取记忆存储详情 |
| CreateMemoryCollection | AgentRun | 创建记忆存储 |
| UpdateMemoryCollection | AgentRun | 更新记忆存储 |
| DeleteMemoryCollection | AgentRun | 删除记忆存储 |
| ListInstances | OTS | 获取 OTS 实例列表 |
| GetInstance | OTS | 获取 OTS 实例信息 |
| CreateInstance | OTS | 创建 OTS 实例 |

#### **6.2 可观测性**

| **接口名称** | **产品/服务** | **说明** |
| --- | --- | --- |
| GetChartData | OTS | 获取图表数据（用于监控指标展示） |
| GetTableData | OTS | 获取表格数据（用于状态统计） |

### 7. 自定义域名管理

| **接口名称** | **产品/服务** | **说明** |
| --- | --- | --- |
| ListCustomDomains | AgentRun | 获取自定义域名列表 |
| GetCustomDomain | AgentRun | 获取自定义域名详情 |
| CreateCustomDomain | AgentRun | 创建自定义域名 |
| UpdateCustomDomain | AgentRun | 更新自定义域名 |
| DeleteCustomDomain | AgentRun | 删除自定义域名 |
| DescribeUserCertificateList | Yundun | 获取用户证书列表 |
| DescribeUserCertificateDetail | Yundun | 获取证书详情 |

### 8. 工具管理

| **接口名称** | **产品/服务** | **说明** |
| --- | --- | --- |
| ListToolsets | Devs | 获取工具集列表 |
| GetToolset | Devs | 获取工具集详情 |
| CreateToolset | Devs | 创建工具集 |
| UpdateToolset | Devs | 更新工具集 |
| DeleteToolset | Devs | 删除工具集 |
| FetchToolsetAuthorization | Devs | 获取工具集授权 |
| GetArtifact | Devs | 获取 Artifact 信息 |
| CreateArtifact | Devs | 创建 Artifact |
| FetchArtifactTempBucketToken | Devs | 获取 Artifact 临时凭证 |
| PreviewEnvironment | Devs | 预览待部署配置内容 |

### 9. 模型集管理

| **接口名称** | **产品/服务** | **说明** |
| --- | --- | --- |
| ListModelSets | Devs | 获取模型集列表 |
| GetModelSet | Devs | 获取模型集详情 |
| FetchModelSetAuthorization | Devs | 获取模型集授权 |

### 10. 项目与环境管理

| **接口名称** | **产品/服务** | **说明** |
| --- | --- | --- |
| ListProjects | Devs | 获取项目列表 |
| GetProject | Devs | 获取项目详情 |
| CreateProject | Devs | 创建项目 |
| UpdateProject | Devs | 更新项目 |
| GetEnvironment | Devs | 获取环境信息 |
| UpdateEnvironment | Devs | 更新环境 |
| DeployEnvironment | Devs | 部署环境 |
| RenderServicesByTemplate | Devs | 根据模板渲染服务 |
| DeployServices | Devs | 部署服务 |
| ListServiceDeployments | Devs | 获取部署列表 |

### 11. 函数计算管理

| **接口名称** | **产品/服务** | **说明** |
| --- | --- | --- |
| GetFunction | FC | 获取函数信息 |
| CreateFunction | FC | 创建函数 |
| DeleteFunction | FC | 删除函数 |
| GetFunctionCode | FC | 获取函数代码 |
| ListFunctions | FC | 获取函数列表 |
| ListAliases | FC | 获取函数别名列表 |
| ListFunctionVersions | FC | 获取函数版本列表 |
| ListTriggers | FC | 获取触发器列表 |
| ListInstances | FC | 列出函数实例 |
| DescribeRegions | FC | 获取支持的区域 |
| ListCustomDomains | FC | 获取自定义域名列表 |
| CreateCustomDomain | FC | 创建自定义域名 |
| UpdateCustomDomain | FC | 更新自定义域名 |
| DeleteCustomDomain | FC | 删除自定义域名 |
| ListProvisionConfigs | FC | 列出弹性配置 |
| GetProvisionConfig | FC | 获取弹性配置 |
| PutProvisionConfig | FC | 更新弹性配置 |
| DeleteProvisionConfig | FC | 删除弹性配置 |

### 12. 网络配置

| **接口名称** | **产品/服务** | **说明** |
| --- | --- | --- |
| DescribeVpcs | VPC | 获取 VPC 列表 |
| DescribeVSwitches | VPC | 获取交换机列表 |
| DescribeSecurityGroups | ECS | 获取安全组列表 |

### 13. 对象存储

| **接口名称** | **产品/服务** | **说明** |
| --- | --- | --- |
| ListBuckets | OSS | 获取 Bucket 列表 |
| ListObjectsV2 | OSS | 获取 Bucket 内容 |

### 14. 日志服务

| **接口名称** | **产品/服务** | **说明** |
| --- | --- | --- |
| GetSlsService | Log | 获取 SLS 服务状态 |
| OpenSlsService | Log | 开通 SLS 服务 |
| ListProject | Log | 列出日志项目 |
| CreateProject | Log | 创建日志项目 |
| CreateLogStore | Log | 创建日志存储 |
| CreateIndex | Log | 创建索引 |
| CreateLogging | Log | 为Project创建服务日志。 |
| CreateMetricStore | Log | 创建时序库（MetricStore），用于存储时序数据。 |
| GetLogStoreLogs | Log | 获取日志数据 |
| GetIndex | Log | 查询指定Logstore的索引信息。 |
| EnableService | Log | 启用服务 |
| ListLogstore | Log | 获取日志存储列表 |
| GetMLServiceResults | Log | 获取指定场景任务的算法分析结果 |
| QueryPrometheusMetrics | Log | Prometheus 协议查询权限 |
| QueryMetrics | Log | 查询监控指标 |
| RemoteWritePrometheus | Log | 通过 Prometheus Remote Write 协议向 MetricStore 写入时序指标数据 |
| RemoteWrite | Log | 写入时序指标数据 |

### 14. 可观测性

| **接口名称** | **产品/服务** | **说明** |
| --- | --- | --- |
| CheckCommercialStatus | ARMS | 检查商业状态 |
| GetCommercialStatus | ARMS | 获取商业状态 |
| DescribeTraceLicenseKey | ARMS | 获取 Trace License |
| SearchTraceAppByName | ARMS | 按名称搜索应用 |
| ListAppInstances | ARMS | 获取应用实例列表 |
| ListLLMSessions | ARMS | 获取 LLM 会话列表 |
| QueryLLMSessionDetail | ARMS | 获取会话详情 |
| ListAllServices | ARMS | 获取所有服务列表 |
| DoInsightsAction | ARMS | 洞察操作 |
| ConfigApp | ARMS | 配置应用 |
| SaveTraceAppConfig | ARMS | 保存链路追踪配置 |
| DoInsightsAction | ARMS | 访问Insights相关的各种子功能 |
| GetTraceApp | ARMS | 获取应用监控任务详情 |
| GetTrace | ARMS | 获取调用链详情 |
| GetStack | ARMS | 获取调用链方法栈信息 |
| GetMultipleTrace | ARMS | 获取多个调用链的详情 |
| GetTraceAppConfig | ARMS | 查询应用监控中，某个应用的全部自定义设置（如调用链采样设置、Agent开关等）。此 |
| ConfigApp | ARMS | 打开或关闭应用监控的Agent总开关，或者查询Agent总开关的状态。 |
| SaveTraceAppConfig | ARMS | 进行应用监控的自定义设置（如调用链采样设置、Agent开关等）。 |
| TagResources | ARMS | 用于给ARMS资源实例打标签。 |
| UntagResources | ARMS | 用于删除ARMS资源实例标签。 |

### 16. 云监控

| **接口名称** | **产品/服务** | **说明** |
| --- | --- | --- |
| ListPrometheusVirtualInstances | CMS | 获取 Prometheus 实例 |
| CreatePrometheusVirtualInstance | CMS | 创建 Prometheus 实例 |
| GetCmsService | CMS | 获取 CMS 服务状态 |
| OpenCmsService | CMS | 开通 CMS 服务 |
| QueryCommercialUsage | CMS | 查询可观测用量数据 |
| DescribeEnvironment | CMS | 查询环境详情 |
| Cursor | CMS | 定义导出监控数据的范围 |
| BatchGet | CMS | 批量获取监控数据 |
| BatchExport | CMS | 批量导出监控数据 |

### 17. 链路追踪

| **接口名称** | **产品/服务** | **说明** |
| --- | --- | --- |
| GetTraceLicenseKey | Xtrace | 获取 Trace License |
| DescribeTraceApps | Xtrace | 描述链路追踪应用 |

### 18. 访问控制

| **接口名称** | **产品/服务** | **说明** |
| --- | --- | --- |
| ListRolesForService | RAM | 获取服务角色列表 |
| ListPoliciesForRole | RAM | 获取角色策略列表 |
| CheckServiceLinkedRoleExistence | ResourceManager | 检查服务关联角色 |
| CreateServiceLinkedRole | RAM | 创建服务关联角色 |
| PassRole | RAM | 传递角色 |

### 19. CDN

| **接口名称** | **产品/服务** | **说明** |
| --- | --- | --- |
| DescribeUserDomains | CDN | 获取用户 CDN 域名列表 |

### 20. 容器镜像服务

| **接口名称** | **产品/服务** | **说明** |
| --- | --- | --- |
| ListRepoTag | ACR | 获取镜像仓库标签列表 |

### 21. 安全服务

| **接口名称** | **产品/服务** | **说明** |
| --- | --- | --- |
| GetUserBuyStatus | Yundun | 获取用户购买状态 |

### 22. 商业状态查询

| **接口名称** | **产品/服务** | **说明** |
| --- | --- | --- |
| DescribeUserBusinessStatus | Ubsms | 获取用户商业状态 |

### 23. 知识库管理

| **接口名称** | **产品/服务** | **说明** |
| --- | --- | --- |
| GetKnowledgeBase | AgentRun | 获取知识库详情 |
| CreateKnowledgeBase | AgentRun | 创建知识库 |
| UpdateKnowledgeBase | AgentRun | 更新知识库 |
| DeleteKnowledgeBase | AgentRun | 删除知识库 |
| ListKnowledgeBases | AgentRun | 列出知识库列表 |
| ListWorkspaces | Bailian | 获取百炼工作空间列表 |
| CreateUser | Bailian | 创建百炼用户 |
| ListRoles | Bailian | 获取百炼角色列表 |
| ListUsers | Bailian | 获取百炼用户列表 |
| AttachWorkspaceToUser | Bailian | 将工作空间关联到用户 |

### 24. 调用 Agent 与 Sandbox

| **接口名称** | **产品/服务** | **说明** |
| --- | --- | --- |
| InvokeRuntime | AgentRun | 调用 Agent |
| InvokeSandbox | AgentRun | 调用 Sandbox |

这两个接口用于通过 AgentRun 服务调用 Agent 实例和 Sandbox 沙箱实例，属于调用类动作。在创建自定义权限策略时，需包含`agentrun:InvokeRuntime`和`agentrun:InvokeSandbox`两个 Action。
