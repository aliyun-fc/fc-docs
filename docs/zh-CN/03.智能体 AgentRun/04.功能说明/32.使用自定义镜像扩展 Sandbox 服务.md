# 使用自定义镜像扩展 Sandbox 服务

AgentRun Sandbox 的 AIO（All-In-One）镜像内置了 Code Interpreter 和 BrowserTool 两类能力。如果您需要在同一沙箱实例中运行自己的服务（例如自定义 API、数据处理进程），可以通过扩展 AIO 基础镜像的方式实现，无需修改 AIO 原有代码。

本文以一个简单的 Python Echo Server 为例，介绍如何将自定义服务集成到 AIO 沙箱中。同样的方式适用于 CodeInterpreter、Browser 等其他基础镜像。

## **工作原理**

由于 AgentRun 的运行环境限制，沙箱实例对外只暴露一个端口（5000）。所有外部请求都通过 OpenResty 按路径分发到内部的不同服务。

AIO 镜像的启动脚本（`entrypoint.sh`）不会在运行时自动扫描或遍历`/etc/sandbox/config/`目录。它通过`-f`参数显式指定配置文件路径，并将这些文件传给 process-compose 进行管理。具体加载机制如下：

- **Process Compose**：`entrypoint.sh`通过`-f`参数逐个指定配置文件路径（如`-f /etc/sandbox/config/process-compose.base.yaml -f /etc/sandbox/config/process-compose.<name>.yaml`）。配置文件可放置在`/etc/sandbox/config/`目录下，但其路径必须被追加到`/etc/sandbox/process-compose-files.txt`静态登记列表中，以便在镜像构建阶段纳入加载范围。
- **Nginx（OpenResty）**：OpenResty 实际加载的是`/usr/local/openresty/nginx/conf/http.d/*.conf`、`/usr/local/openresty/nginx/conf/server.d/*.conf`和`/usr/local/openresty/nginx/conf/conf.d/*.conf`。如果将 Nginx 配置先放到`/etc/sandbox/config/nginx/`目录下，还需要在镜像构建阶段显式复制到 OpenResty 实际配置目录。

对应配置类型与加载路径：

| **配置类型** | **推荐放置/登记方式** | **运行时加载位置** | **是否需要显式登记** |
| --- | --- | --- | --- |
| Process Compose | 文件可放`/etc/sandbox/config/process-compose.<name>.yaml`，但路径必须追加到`/etc/sandbox/process-compose-files.txt` | 通过`-f`参数指定 | **是**：追加到静态加载列表 |
| Nginx Upstream | `/usr/local/openresty/nginx/conf/http.d/*.conf` | 同左 | **是**：构建阶段复制到 OpenResty 目录 |
| Nginx 路由 | `/usr/local/openresty/nginx/conf/conf.d/*.conf` | 同左 | **是**：构建阶段复制到 OpenResty 目录 |

**

**说明**

`/etc/sandbox/config/nginx/`只能作为派生镜像里的源码组织目录（构建时使用），不能作为运行时加载目录。OpenResty 不会从该目录读取配置。

## **前提条件**

开始前，请确认以下条件已满足：

- 已完成 AgentRun SLR 服务角色授权（首次使用时在控制台根据提示完成）。
- 已在控制台创建 AIO 沙箱模板。
- 本地已安装 Docker，能够构建和运行容器镜像。
- 熟悉 Docker、Nginx 基本概念。

## **操作步骤**

以下示例将一个 Python Echo Server 集成到 AIO 沙箱中，通过`/echo`路径对外提供服务。

您可以下载完整的示例代码包：[echoserver.zip](https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20260527/negzzs/echoserver-fixed.zip)

### **文件结构**

新建`echoserver/`目录，按以下结构组织文件：

```
echoserver/ ├── echo_server.py └── config/ ├── process-compose.echoserver.yaml ├── nginx-echoserver-upstream.conf └── nginx-echoserver-routes.conf
```

### **步骤一：编写服务代码**

创建`echo_server.py`，实现一个简单的 HTTP 服务，GET 请求返回`ok`：

```
#!/usr/bin/env python3 import os from http.server import HTTPServer, BaseHTTPRequestHandler DEFAULT_PORT = 9000 class EchoHandler(BaseHTTPRequestHandler): def do_GET(self): self.send_response(200) self.send_header('Content-Type', 'text/plain; charset=utf-8') self.end_headers() self.wfile.write(b'ok\n') def main(): port = int(os.environ.get('ECHO_SERVER_PORT', DEFAULT_PORT)) host = os.environ.get('ECHO_SERVER_HOST', '0.0.0.0') server = HTTPServer((host, port), EchoHandler) print(f"[echoserver] Starting echo server on {host}:{port}") try: server.serve_forever() except KeyboardInterrupt: server.shutdown() if __name__ == '__main__': main()
```

### **步骤二：配置Process Compose**

创建`process-compose.echoserver.yaml`，定义服务的启动方式、健康检查和日志：

```
version: "0.5" log_level: info environment: - PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin processes: echoserver: command: "python3 /usr/local/bin/echo_server.py" availability: restart: "always" backoff_seconds: 2 max_restarts: 5 readiness_probe: http_get: host: localhost port: ${ECHO_SERVER_PORT:-9000} path: / initial_delay_seconds: 1 period_seconds: 5 timeout_seconds: 2 success_threshold: 1 failure_threshold: 3 environment: - ECHO_SERVER_HOST=0.0.0.0 - ECHO_SERVER_PORT=9000 - PYTHONUNBUFFERED=1 - PYTHONDONTWRITEBYTECODE=1 log_configuration: disable_json: true no_metadata: false add_timestamp: true timestamp_format: "2006-01-02 15:04:05.000" fields_to_append: - level=INFO
```

### **步骤三：配置Nginx**

**Upstream 配置**：创建`nginx-echoserver-upstream.conf`，定义后端服务地址：

```
upstream echoserver { server localhost:9000; keepalive 16; }
```

**路由配置**：创建`nginx-echoserver-routes.conf`，将`/echo`路径代理到 echo server：

```
location /echo { proxy_pass http://echoserver; proxy_set_header Host $host; proxy_set_header X-Real-IP $remote_addr; proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; proxy_set_header X-Forwarded-Proto $scheme; proxy_connect_timeout 60s; proxy_send_timeout 60s; proxy_read_timeout 60s; proxy_http_version 1.1; proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection $connection_upgrade; }
```

### **步骤四：编写Dockerfile**

创建`Dockerfile`，以 AIO 基础镜像为基础，将服务代码和配置文件复制到对应目录：

```
FROM serverless-registry.cn-hangzhou.cr.aliyuncs.com/functionai/sandbox-all-in-one:v0.9.29 USER root # 1. 将服务代码复制到容器内 COPY echo_server.py /usr/local/bin/echo_server.py RUN chmod +x /usr/local/bin/echo_server.py # 2. Process Compose 配置：放入配置目录后，必须显式登记到静态加载列表 COPY config/process-compose.echoserver.yaml /etc/sandbox/config/process-compose.echoserver.yaml RUN grep -qxF '/etc/sandbox/config/process-compose.echoserver.yaml' /etc/sandbox/process-compose-files.txt || \ printf '%s\n' '/etc/sandbox/config/process-compose.echoserver.yaml' >> /etc/sandbox/process-compose-files.txt # 3. Nginx 配置：复制到 OpenResty 实际加载目录 RUN mkdir -p /usr/local/openresty/nginx/conf/http.d /usr/local/openresty/nginx/conf/conf.d COPY config/nginx-echoserver-upstream.conf /usr/local/openresty/nginx/conf/http.d/echoserver-upstream.conf COPY config/nginx-echoserver-routes.conf /usr/local/openresty/nginx/conf/conf.d/echoserver-routes.conf # 4. 设置环境变量 ENV ECHO_SERVER_HOST=0.0.0.0 \ ECHO_SERVER_PORT=9000 ENTRYPOINT ["/usr/local/bin/entrypoint.sh"] CMD ["process-compose", "up", "--tui=false", "--no-server"]
```

关键变化说明：

- Process Compose 配置文件放入`/etc/sandbox/config/`后，必须通过`printf`或`echo`追加到`/etc/sandbox/process-compose-files.txt`中，否则不会被加载。
- Nginx 配置文件不能仅放在`/etc/sandbox/config/nginx/`目录下，必须在构建阶段`COPY`到`/usr/local/openresty/nginx/conf/http.d/`（Upstream 配置）和`/usr/local/openresty/nginx/conf/conf.d/`（路由配置）。

### **步骤五：构建并运行**

```
cd echoserver # 构建镜像 docker build -f Dockerfile -t echoserver-extension:latest . # 本地运行（将容器的 5000 端口映射到本地 5000） docker run --rm \ -p 5000:5000 \ --name echoserver-test \ echoserver-extension:latest
```

### **步骤六：验证**

```
# 通过 Nginx 代理访问 echo server curl http://localhost:5000/echo # 预期返回: ok
```

在 AgentRun 上部署后，访问地址格式如下：

```
https://{账号ID}.agentrun-data.cn-hangzhou.aliyuncs.com/sandboxes/{沙箱ID}/echo
```

## **配置参考**

### **Process Compose 配置**

文件名建议使用`process-compose.<服务名>.yaml`格式，放置于`/etc/sandbox/config/`目录下。但该配置文件只有被写入`/etc/sandbox/process-compose-files.txt`后才会被 entrypoint 加载。

登记方式（在 Dockerfile 中）：

```
RUN grep -qxF '/etc/sandbox/config/process-compose.<服务名>.yaml' /etc/sandbox/process-compose-files.txt || \ printf '%s\n' '/etc/sandbox/config/process-compose.<服务名>.yaml' >> /etc/sandbox/process-compose-files.txt
```

支持以下核心配置项：

| **配置项** | **说明** |
| --- | --- |
| `command` | 服务启动命令 |
| `availability.restart` | 重启策略，`"always"`表示异常退出时自动重启 |
| `readiness_probe.http_get` | HTTP 健康检查，服务提供`/health`等端点时推荐使用 |
| `readiness_probe.exec` | 进程健康检查，服务未提供 HTTP 端点时使用 |
| `environment` | 服务运行所需的环境变量 |
| `log_configuration` | 日志格式配置 |

### **Nginx Upstream 配置**

Nginx Upstream 配置路径：`/usr/local/openresty/nginx/conf/http.d/*.conf`

`/etc/sandbox/config/nginx/http.d/`只能作为构建阶段的源码组织目录。在 Dockerfile 中需显式复制到 OpenResty 实际加载目录：

```
COPY config/nginx-<服务名>-upstream.conf /usr/local/openresty/nginx/conf/http.d/<服务名>-upstream.conf
```

定义后端服务地址示例：

```
upstream your_service { server localhost:9001; # 自定义服务内部端口 keepalive 16; }
```

### **Nginx 路由配置**

Nginx 路由配置路径：`/usr/local/openresty/nginx/conf/conf.d/*.conf`

`/etc/sandbox/config/nginx/conf.d/`只能作为构建阶段的源码组织目录。在 Dockerfile 中需显式复制到 OpenResty 实际加载目录：

```
COPY config/nginx-<服务名>-routes.conf /usr/local/openresty/nginx/conf/conf.d/<服务名>-routes.conf
```

定义 URL 路径到 upstream 的映射。

**基本路由：**

```
location /your-service { proxy_pass http://your_service; proxy_set_header Host $host; proxy_set_header X-Real-IP $remote_addr; proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; proxy_set_header X-Forwarded-Proto $scheme; }
```

**使用 rewrite 转换路径：**

如果需要在转发前改写 URL 路径，可以使用`rewrite`指令。例如，将外部路径`/api/v1/echo`转换为后端期望的`/echo`：

```
location /api/v1/echo { rewrite ^/api/v1/echo(.*)$ /echo$1 break; proxy_pass http://echoserver; proxy_set_header Host $host; }
```

`rewrite`指令说明：

- `^/api/v1/echo(.*)$`：匹配路径，`(.*)`捕获尾部内容。
- `/echo$1`：改写后的路径，`$1`为捕获内容。
- `break`：停止后续 rewrite 规则处理，直接将改写后的路径传给`proxy_pass`。

**更多 rewrite 示例：**

```
# 移除路径前缀：/api/echo/xxx → /echo/xxx location /api/echo { rewrite ^/api/echo(.*)$ /echo$1 break; proxy_pass http://echoserver; }
```

```
# 添加路径前缀：/echo → /v1/echo location /echo { rewrite ^/echo(.*)$ /v1/echo$1 break; proxy_pass http://echoserver; }
```

### **文件命名规范**

建议遵循以下命名约定，保持团队一致性：

| **配置类型** | **命名格式** | **示例** |
| --- | --- | --- |
| Process Compose | `process-compose.<服务名>.yaml` | `process-compose.echoserver.yaml` |
| Nginx Upstream | `nginx-<服务名>-upstream.conf` | `nginx-echoserver-upstream.conf` |
| Nginx 路由 | `nginx-<服务名>-routes.conf` | `nginx-echoserver-routes.conf` |

## **注意事项**

- **端口冲突**：自定义服务的内部端口不能与 AIO 内置服务冲突，建议使用 9000 及以上端口。AIO 内置服务端口：
  
  - Nginx 内置网关：5000
  - Code Interpreter：5001
  - BrowserTool：3000
- **健康检查**：如果服务提供 HTTP 健康检查端点（如`/health`），建议在`process-compose.*.yaml`中使用`readiness_probe.http_get`；否则使用`readiness_probe.exec`检查进程是否存活。
- **服务命名唯一性**：`process-compose.*.yaml`中`processes`下的服务名（key）在同一沙箱内必须唯一。
- **路由路径唯一性**：`location`路径不能与 AIO 内置路由冲突。AIO 内置路由：
  
  - Code Interpreter 占用：`/`、`/contexts`、`/execute`等
  - BrowserTool 占用：`/ws/automation`、`/recordings`等

## **故障排查**

### **服务未启动**

```
# 查看 process-compose 日志 docker logs echoserver-test | grep echoserver # 确认进程是否运行 docker exec echoserver-test pgrep -f echo_server.py # 检查配置文件是否在静态加载列表中 docker exec echoserver-test grep echoserver /etc/sandbox/process-compose-files.txt # 查看 entrypoint.sh 启动参数 docker exec echoserver-test ps -p 1 -o args= # 确认自定义进程是否在运行 docker exec echoserver-test pgrep -af echo_server.py
```

### **Nginx 配置错误**

确认 Nginx 配置已部署到 OpenResty 实际加载目录：

```
# 检查 Upstream 配置 docker exec echoserver-test ls -la /usr/local/openresty/nginx/conf/http.d/ # 检查路由配置 docker exec echoserver-test ls -la /usr/local/openresty/nginx/conf/conf.d/ # 验证 Nginx 配置语法 docker exec echoserver-test /usr/local/openresty/nginx/sbin/nginx -t \ -p /usr/local/openresty/nginx/ \ -c /usr/local/openresty/nginx/conf/nginx.conf # 查看 Nginx 错误日志 docker exec echoserver-test tail -f /var/log/nginx/error.log
```

### **路由不工作**

```
# 确认 OpenResty conf.d 目录内容 docker exec echoserver-test ls -la /usr/local/openresty/nginx/conf/conf.d/ # 直接访问内部服务（绕过 Nginx），确认服务本身是否正常 docker exec echoserver-test curl http://localhost:9000/ # 查看 Nginx 访问日志，确认请求是否到达 docker exec echoserver-test tail -f /var/log/nginx/access.log
```
