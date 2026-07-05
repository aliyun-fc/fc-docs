# 为Python Agent应用安装ARMS探针

本文介绍如何在AgentRun中，为使用自定义镜像部署的 Python Agent 应用安装应用实时监控服务 ARMS探针。安装后，您可以通过 ARMS 提供的专属监控大盘，实时观测大模型（LLM）应用的调用次数、Token 消耗、费用、Trace 链路以及会话详情等关键指标。

## **核心价值**

安装 ARMS Python 探针后，可实现：

- **成本与性能监控**：实时追踪 LLM（如 OpenAI、DashScope）的 API 调用次数、Token 消耗及费用；
- **全链路追踪**：自动关联业务请求与 LLM 调用，形成完整 Trace 链路；
- **错误与会话分析**：捕获异常详情，聚合用户会话数据；
- **零代码侵入**：通过 Auto-instrumentation 技术自动注入，无需修改业务逻辑。

**性能开销参考（典型场景）**：

- **CPU**：额外开销通常低于 5%。
- **内存**：额外占用约 50-100MB。
- **延迟**：对请求的平均延迟影响通常在毫秒级别。

注：以上为典型场景下的参考值，实际开销可能因应用负载和复杂度而异。

## **环境约束**

- 网络要求：构建环境需能访问公网或阿里云内网，并开放`TCP 80/443`出站权限；
- Python 版本：3.8 ≤ Python ≤ 3.12；
- 依赖版本：
  
  - `protobuf >= 3.20.0, < 6.0`
  - `opentelemetry-api <= 1.35.0`

详细支持组件列表见[ARMS 应用监控支持的 Python 组件和框架](https://help.aliyun.com/zh/arms/application-monitoring/developer-reference/python-libraries-supported-by-arms-application-monitoring)。

## **安装步骤**

### **1、修改Dockerfile**

1. **配置 pip 镜像源**
  
  ```
  RUN pip3 config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \ pip3 config set install.trusted-host mirrors.aliyun.com
  ```
2. **安装探针**
  
  ```
  RUN pip3 install aliyun-bootstrap RUN aliyun-bootstrap -a install # 可选：指定版本 → RUN aliyun-bootstrap -a install -v 2.10.1
  ```
  
  **
  
  **说明**
  
  参考[探针（Python Agent）版本说明](https://help.aliyun.com/zh/arms/application-monitoring/user-guide/python-agent-version-description)查看所有已发布的Python探针版本。
3. **配置启动命令**
  
  使用`aliyun- instrument`启动应用：
  
  ```
  CMD ["aliyun-instrument", "python3", "main.py"]
  ```
  
  针对 Web 框架的建议：
  
  - **uvicorn 应用**：推荐改用`gunicorn + UvicornWorker`，并前置`aliyun-instrument`；
    
    ```
    CMD ["aliyun-instrument", "gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "main:app"]
    ```
    
    或在入口文件首行添加：
    
    ```
    from aliyun.opentelemetry.instrumentation.auto_instrumentation import sitecustomize
    ```
  - **uWSGI 应用**：参见[在使用uWSGI启动Django或Flask项目时接入Python探针](https://help.aliyun.com/zh/arms/application-monitoring/use-cases/install-the-arms-agent-for-python-when-you-use-uwsgi-to-start-a-django-or-flask-application)；
  - **gevent 协程**：需设置环境变量`GEVENT_ENABLE=true`。

### **2、配置探针环境变量**

必须配置以下三项：

- `ARMS_APP_NAME`：应用名称（如`MyLlmApp`）；
- `ARMS_REGION_ID`：地域 ID（如`cn-hangzhou`）；
- `ARMS_LICENSE_KEY`：ARMS 为您生成的应用接入凭证，可以通过 OpenAPI 获取，具体方法可参见[列出LicenseKey](https://help.aliyun.com/zh/arms/application-monitoring/developer-reference/api-arms-2019-08-08-describetracelicensekey-apps)。

**方式一**：直接在 Dockerfile 中配置：

```
# 应用名 ENV ARMS_APP_NAME={app_name} # 应用所在地域，例如cn-hangzhou ENV ARMS_REGION_ID={region_id} # ARMS 接入凭证 ENV ARMS_LICENSE_KEY={LicenseKey}
```

**方式二（推荐）**：AgentRun 控制台支持在部署或配置 Agent 阶段定义环境变量，可不在此处 Dockerfile 中配置。

### **3、构建并上传镜像**

将包含探针的 Dockerfile 构建成镜像，并上传至[容器镜像服务ACR](https://cr.console.aliyun.com/cn-hangzhou/instances)或其他可访问的镜像仓库。

```
# 示例：将镜像上传至阿里云 ACR # 1. 为镜像添加标签 docker tag {本地镜像TAG} registry.cn-hangzhou.aliyuncs.com/{您的ACR命名空间}/{您的ACR仓库名}:{镜像版本号} # 2. 上传镜像 docker push registry.cn-hangzhou.aliyuncs.com/{您的ACR命名空间}/{您的ACR仓库名}:{镜像版本号}
```

### **4、在 AgentRun中部署Agent并配置探针**

1. 登录[AgentRun控制台](https://fcnext.console.aliyun.com/agent-run/cn-hangzhou/agent/runtime/agent-list)，在**Agent 运行时**页签下，点击**创建 Agent**。
2. 选择**通过代码创建**，并填写**Agent名称**和**功能描述**。
3. 在**代码配置**部分，配置如下：
  
  - **代码来源**：选择**容器镜像**。
  - **容器镜像实例、****ACR 镜像仓库**：选择您在[步骤3](#d34f0f82f1lbn)中上传的镜像。
4. **启动命令**：若已在 Dockerfile 中通过`CMD`配置，此处可留空。
5. **启动端口**：填入您应用实际监听的端口，例如`8000`。
6. **资源配置**：根据需要为 Agent 分配CPU和内存。
7. **配置探针环境变量（推荐）：**参考[步骤2](#2f4fa6e71d7og)配置ARMS探针所需环境变量
8. **开启链路追踪**
  
  在高级配置中，找到并务必启用链路追踪开关。如果此开关关闭，所有探针配置将不会生效，应用无法上报任何监控数据。
9. 点击**开始部署**。

### **5、验证**

部署成功 1–2 分钟后，进入 Agent**详情**页 →**可观测性**页面，检查：

- “概览”中是否出现请求数、LLM 调用次数、Token 使用量；
- “Trace 列表”中是否包含`openai`或`dashscope`的调用链。

## **完整 Dockerfile 示例**

以下是一个基于 FastAPI 和 OpenAI SDK 的应用示例，展示了一个推荐的、安全的 Dockerfile 配置。

**应用代码（main.py）**

```
from openai import OpenAI from fastapi import FastAPI import uvicorn app = FastAPI() @app.get("/") def call_openai(): # 建议通过环境变量等安全方式管理 API Key client = OpenAI( api_key="sk-********************************", base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", ) response = client.chat.completions.create( model="qwen-max", messages=[{"role": "user", "content": "Write a haiku about the weather."}], ) return {"data": f"{response}"} if __name__ == "__main__": # 启动命令建议在 Dockerfile 的 CMD 中统一管理 uvicorn.run(app, host="0.0.0.0", port=8000)
```

**依赖文件（**`**requirements.txt**`**）**

```
fastapi==0.120.0 uvicorn==0.38.0 openai==2.6.1 pydantic==2.12.3
```

**Dockerfile**

```
FROM mirrors-ssl.aliyuncs.com/python:3.11.14-slim # 设置工作目录 WORKDIR /app ENV PYTHONUNBUFFERED=1 \ PYTHONDONTWRITEBYTECODE=1 \ PIP_NO_CACHE_DIR=1 \ PIP_DISABLE_PIP_VERSION_CHECK=1 # # ====================================================== # 配置 pip 使用阿里云镜像源（加速探针安装） # ====================================================== RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \ pip config set install.trusted-host mirrors.aliyun.com COPY requirements.txt . RUN pip install --no-cache-dir -r requirements.txt # # ====================================================== # 安装探针安装器，并安装 ARMS 探针 # ====================================================== RUN pip install --no-cache-dir aliyun-bootstrap RUN aliyun-bootstrap -a install # demo应用代码 COPY main.py . EXPOSE 8000 # # ====================================================== # 设置探针环境变量 # ====================================================== ENV ARMS_APP_NAME=OpenAI_Demo_Python \ ARMS_REGION_ID=cn-hangzhou \ ARMS_LICENSE_KEY={LicenseKey} # # ====================================================== # 启动命令：使用 aliyun-instrument 启动应用以启用监控 # ====================================================== CMD ["aliyun-instrument", "python3", "main.py"]
```

## **故障排查**

若无数据上报，请依次检查：

1. 日志：查看容器日志是否有`ARMS Agent started successfully`；
2. 配置：确认链路追踪已开启，环境变量无拼写错误；
3. 网络：测试容器内能否访问`https://tracing-analysis-dc-{region}.aliyuncs.com`；
4. 依赖：执行`pip check`排查版本冲突。

## **常见问题**

- 探针安装运行的常见问题参考：[Python探针使用常见问题](https://help.aliyun.com/zh/arms/application-monitoring/user-guide/python-agent-faq)
- 探针性能开销数据可以参考：[Python探针性能压测报告](https://help.aliyun.com/zh/arms/application-monitoring/developer-reference/python-probe-performance-pressure-test-report)
- 探针支持的组件和框架可以参考：[ARMS 应用监控支持的 Python 组件和框架](https://help.aliyun.com/zh/arms/application-monitoring/developer-reference/python-libraries-supported-by-arms-application-monitoring)
