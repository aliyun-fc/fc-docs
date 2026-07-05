# 为Python Agent接入ARMS应用监控

AgentRun 自定义运行时中的 Python 3.10 和 Python 3.12 环境已预集成 ARMS Python 探针能力。您只需通过配置环境变量和启动命令，即可接入[什么是应用实时监控服务ARMS？](https://help.aliyun.com/zh/arms/product-overview/what-is-arms)，实时监控 LLM 调用次数、Token 消耗、Trace 链路及会话等关键指标。本文介绍如何在代码创建的 Agent 接入 ARMS 应用监控。

## **前提条件**

- [开通ARMS](https://help.aliyun.com/zh/arms/getting-started/activate-arms)；
- Agent 运行时选择`Python 3.10`或`Python 3.12`自定义运行时。

## **配置步骤**

### **1、设置探针环境变量**

在创建 Agent 时，需要在 Agent 运行时**详情**页面，选择**概览与配置**页签，单击**编辑配置**，添加以下**环境变量**：

```
ARMS_APP_NAME={您的应用名称} ARMS_REGION_ID={地域ID，如 cn-hangzhou} ARMS_LICENSE_KEY={从ARMS获取的LicenseKey}
```

变量含义说明：

- **ARMS_APP_NAME**：Agent 名字，用于在 ARMS 应用监控中显示。
- **ARMS_REGION_ID**：地域，比如：`cn-hangzhou`。
- **ARMS_LICENSE_KEY**：ARMS 为您生成的应用接入凭证，可以通过 OpenAPI 获取，具体方法可参见[列出LicenseKey](https://help.aliyun.com/zh/arms/application-monitoring/developer-reference/api-arms-2019-08-08-describetracelicensekey-apps)。

### **2、修改启动命令**

在中，将**启动命令**修改为：

```
/opt/python/bin/aliyun-instrument python3 main.py
```

其中：

- `/opt/python/bin/aliyun-instrument`是 AgentRun 预置的探针启动器；
- 后续参数为您的原始启动命令（如`python3 app.py --port 8000`）。

该启动器会在应用初始化前自动加载 ARMS 探针，实现零代码侵入的自动埋点。

### **3、特殊框架适配（按需配置）**

#### 使用 uvicorn

改用`gunicorn + UvicornWorker`，并在命令前加`aliyun-instrument`：

```
/opt/python/bin/aliyun-instrument gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app
```

#### 使用 uWSGI

请参考官方指南：[在使用uWSGI启动Django或Flask项目时接入Python探针](https://help.aliyun.com/zh/arms/application-monitoring/use-cases/install-the-arms-agent-for-python-when-you-use-uwsgi-to-start-a-django-or-flask-application)

#### 使用 gevent 协程

若代码中包含：

```
from gevent import monkey monkey.patch_all()
```

需额外添加环境变量：

```
GEVENT_ENABLE=true
```

## **验证接入**

1. 保存配置更新Agent；
2. 发起几次业务调用；
3. 约 1 分钟后，前往以下任一位置查看数据：
  
  - 
  -

若能看到调用链、Token 消耗、LLM 调用次数等数据，即表示接入成功。
