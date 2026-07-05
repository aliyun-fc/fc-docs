# Agent集成与发布

## 功能介绍

在AgentRun运行时中创建的Agent，支持被其他系统调用，将已开发好的 Agent 快速集成到前端网页、后端服务等业务系统中

## **前提条件**

- 已创建可用的 Agent （[快速创建Agent（无代码）](https://help.aliyun.com/zh/functioncompute/fc/quickly-create-agent-no-code)/[通过代码创建Agent（高代码）](https://help.aliyun.com/zh/functioncompute/fc/create-agent-by-code-high-code)）并完成发布；
- 为Agent配置了管理Serverless开发平台（Devs）的权限（AliyunDevsFullAccess）。

## **操作步骤**

### 进入集成与发布页面

1. 进入[AgentRun运行时](https://functionai.console.aliyun.com/agent/runtime/agent-list)页面；
2. 在需要被集成的Agent卡片中，点击**详情**；
3. 在Agent详情页，选择左侧目录的**集成与发布**，进入集成与发布页面。

此时可以在页面中看到三种集成方式，按需选择被集成方式，分别为：

**UI集成**：

- 支持一键生成前后端一体的 Agent 应用界面；
- 可以将该界面以 iframe、独立域名等形式嵌入到现有网页或其他应用中；
- 适合快速提供“可视化对话界面”的场景（如内部工作台、门户网站等）。

**代码集成**：

- 提供标准的 HTTP API 接口（如兼容 OpenAI Chat Completions 协议）；
- 外部系统可以按标准协议API/SDK直接调用 Agent 的接口，适合多语言、多平台集成。

**生态集成**：

支持在Dify、n8n等平台集成Agent。

### **配置UI集成**

1. 选择**集成模板**：通过集成模板，来指定UI**集成方式**与**风格模板**，选择完成后，可以点击**预览效果**，查看当前配置的最终效果；
  
  - **集成方式**：**全屏嵌入**、**浮窗聊天**、**侧边栏**；
  - **风格模板**：**简约风格**、**商务风格**、**科技风格**、**温馨风格**。
2. **开始集成**：点击**开始集成**后，需要指定集成的Agent对应版本的EndPoint，进行**API绑定配置**，配置完成后，单击**下一步**；
3. **等待部署完成**：查看部署日志，等待部署完成；
4. **测试部署结果**：部署成功后，会在页面中显示**已部署的集成资源**，并生成一个临时的**访问地址**，可以点击访问地址，进行Agent访问和使用；
  
  **
  
  **重要**
  
  当前访问地址是 CNCF SandBox 项目 Serverless Devs 社区所提供，仅供学习和测试使用，不可用于任何生产使用；社区会对该域名进行不定期地拨测，并在域名下发 1 天后进行回收，强烈建议您绑定自定义域名以获得更好的使用体验。
5. 绑定**自定义域名**：点击访问地址右侧的**增加**，可以选择已有域名或新增域名进行正式域名的绑定，自定义域名配置可以参考[配置自定义域名](https://help.aliyun.com/zh/functioncompute/fc/configure-custom-domain-names)。

### **代码集成**

按标准协议API/SDK直接调用 Agent 的接口，适合多语言、多平台集成，代码示例如下：

```
curl https://12**********.agentrun-data.cn-hangzhou.aliyuncs.com/agent-runtimes/agent-code-XVe7d/endpoints/Default/invocations/openai/v1/chat/completions -XPOST \ -H "content-type: application/json" \ -H "X-AgentRun-Session-ID: your-session-id" \ -d '{ "messages": [{"role": "user", "content": "写一段代码,查询现在是几点?"}], "stream":true }'
```

**

**说明**

X-AgentRun-Session-ID header 用于实现会话亲和功能。使用相同 Session ID 的请求会被路由到同一个 Agent 实例，适用于需要保持会话上下文的场景。您可以使用任意唯一字符串作为 Session ID（如 UUID）。
