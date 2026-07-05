# 函数实例生命周期回调

当您实现并配置函数实例生命周期回调后，函数计算将在相关实例生命周期事件发生时调用对应的回调程序。本文介绍自定义镜像实现函数实例生命周期回调的方法。

## **背景信息**

函数实例生命周期涉及Initializer和PreStop回调。Initializer回调包含**调用代码**和**执行指令**两种类型，目前仅GPU函数支持执行**指令类型**的Initializer回调。更多信息，请参见[配置实例生命周期](https://help.aliyun.com/zh/functioncompute/fc/function-instance-lifecycle)。

函数实例生命周期回调程序与正常调用请求计费规则一致，但其执行日志只能在**实时日志**、**函数日志**或**高级日志**中查询，**调用请求列表**不会展示回调程序日志。具体操作，请参见[查看实例生命周期回调函数日志](#title-xnu-2fa-v8w)。

**

**说明**

目前执行指令类型回调产生的日志暂不支持写入函数日志。

## 回调方法实现

函数计算会在相关实例生命周期事件发生时调用对应的回调程序。函数实例生命周期涉及Initializer和PreStop回调。Initializer回调程序包含**调用代码**和**执行指令**两种类型，二者不允许同时配置，只能有一个生效。

### **调用代码**

配置调用代码类型的回调程序后，函数实例启动或停止时，系统会向您的函数发送HTTP请求POST /initialize或GET /pre-stop，您需要在业务代码中响应该请求。

| **Path** | **输入请求** | **期望的响应** |
| --- | --- | --- |
| （可选）POST`/initialize` | - 请求体：无。<br>- 请求头：Common Request Headers。具体信息，请参见[函数计算公共请求头](https://help.aliyun.com/zh/functioncompute/fc/user-guide/context-and-log-format-1#section-3f8-5y1-i77)。 | 响应体：函数Initializer的返回值。<br>StatusCode<br>- 2xx：成功状态。<br>- 非2xx：失败状态。<br>**<br>**说明**<br>当Initializer回调程序执行超时或失败时，服务端始终返回HTTP 200状态码，必须通过响应头`X-Fc-Error-Type:InitializationError`或响应体中的errorMessage字段判断是否因初始化失败导致错误。 |
| （可选）GET`/pre-stop` | - 请求体：无。<br>- 请求头：Common Request Headers。具体信息，请参见[函数计算公共请求头](https://help.aliyun.com/zh/functioncompute/fc/user-guide/context-and-log-format-1#section-3f8-5y1-i77)。 | 响应体：函数PreStop的返回值。<br>StatusCode<br>- 2xx：成功状态。<br>- 非2xx：失败状态。 |

如果您想在自定义镜像使用Initializer回调方法，您需要在您的HTTP Server中实现Path为/initialize和Method为POST的对应逻辑，使用PreStop回调方法同理。本文以自定义运行时Python 3.10为例，具体示例程序如下所示。

**

**说明**

创建的函数不设置Initializer时，无需实现/initialize。此时，即使HTTP Server实现了/initialize，代码中的/initialize逻辑也无法被调用执行，PreStop同理。

```
import os from flask import Flask from flask import request app = Flask(__name__) @app.route('/initialize', methods=['POST']) def init_invoke(): rid = request.headers.get('x-fc-request-id') print("FC Initialize Start RequestId: " + rid) # do your things print("FC Initialize End RequestId: " + rid) return "OK" @app.route('/', defaults={'path': ''}) @app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE']) def hello_world(path): rid = request.headers.get('x-fc-request-id') print("FC invoke Start RequestId: " + rid) # do your things print("FC invoke End RequestId: " + rid) return "Hello, World!", 200, [('Function-Name', os.getenv('FC_FUNCTION_NAME'))] @app.route('/pre-stop', methods=['GET']) def prestop_invoke(): rid = request.headers.get('x-fc-request-id') print("FC PreStop Start RequestId: " + rid) # do your things print("FC PreStop End RequestId: " + rid) return "OK" if __name__ == '__main__': app.run(host='0.0.0.0', port=9000)
```

除了上面正确的代码程序，Python语言中还有函数执行报错的场景，`/initialize`示例代码如下。

```
@app.route('/initialize', methods=['POST']) def init(): raise Exception("hahaha") return "OK", 200, []
```

```
@app.route('/initialize', methods=['POST']) def init(): return "OK", 404, []
```

### **执行指令**

如果您希望函数实例启动后，向函数发送HTTP请求来做一些初始化操作，可以通过配置回调指令来实现。支持用户自定义Shell实现方式，例如`/bin/bash`、`/bin/sh`、`/bin/csh`和`/bin/zsh`等，需要确保函数运行时环境支持对应的Shell实现方式。

函数计算控制台目前预置了`/bin/bash`和`/bin/sh`两种方式，本文以`/bin/sh`方式为例，具体示例程序如下。

```
#!/bin/sh URL="http://localhost:7860" REQUEST_PATH="sdapi/v1/txt2img" JSON_DATA='{ "prompt": "", "steps": 1, "height": 8, "width": 8 }' temp_file=$(mktemp) trap 'rm -f "$temp_file"' EXIT if ! http_code=$(curl -s -w "%{http_code}" \ -H "Content-Type: application/json" \ -d "$JSON_DATA" \ -o "$temp_file" \ -X POST "$URL"/"$REQUEST_PATH"); then echo "{\"status\": \"curl_error\", \"code\": $curl_exit_code}" \ | jq . >&2 exit 1 fi response=$(<"$temp_file") echo "http code $http_code" if [ "$http_code" -eq 200 ]; then echo "$response" | jq -r '.' || printf "%s\n" "$response" exit 0 else echo "$response_body" \ | jq -c 'if type == "object" then . else {raw: .} end' 2>/dev/null \ | jq -s '{status: "http_error", code: $code, response: .[0]}' \ --arg code "$http_code" \ >&2 exit 1 fi
```

当回调指令退出码为0时，表示执行成功，否则表示执行失败。您可以在脚本中适当将一些错误信息输出至标准错误（stderr）中，方便定位错误原因，例如下面代码片段表示curl请求执行失败后，输出相关错误信息，并将退出码置为1。

```
if ! http_code=$(curl -s -w "%{http_code}" \ -H "Content-Type: application/json" \ -d "$JSON_DATA" \ -o "$temp_file" \ -X POST "$URL"/"$REQUEST_PATH"); then echo "{\"status\": \"curl_error\", \"code\": $curl_exit_code}" \ | jq . >&2 exit 1 fi
```

## 回调错误码

### **调用代码**

| **错误码ID** | **解释说明** |
| --- | --- |
| 400 | - 函数Initializer回调失败返回400或404，不会重新发送请求，但系统会继续重试直到调用成功为止。<br>- 函数PreStop回调失败返回400或404，不会影响函数实例的冷冻和停止。 |
| 404 |  |
| 500 | 函数计算重启实例。 |

### **执行指令**

若指令退出码为非0，不会重新执行，系统会返回相关错误。

## **配置生命周期回调函数**

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com)，在左侧导航栏，选择**函数管理**>**函数列表**。
2. 在顶部菜单栏，选择地域，然后在**函数列表**页面，单击目标函数。
3. 在函数详情页，选择**配置**页签，然后在**实例配置**区域，单击**编辑**。
4. 在**实例配置**面板，设置Initializer回调程序和**Initializer回调超时时间**。
  
  - **调用代码**
    
    开启**Initializer 回调程序**开关后，设置**Initializer 回调超时时间**为`300`秒，**回调程序类型**可选择**调用代码**或**执行指令**。开启后，函数计算在启动实例时会向函数发送 HTTP POST`/initialize`请求，业务代码需响应该请求并返回 200 状态码，否则返回 4xx/5xx 时函数计算将返回错误或重启实例。
  - **执行指令**
    
    控制台执行指令前置了`/bin/bash`和`/bin/sh`两种Shell实现方式。
    
    开启**Initializer 回调程序**，将**Initializer 回调超时时间**设为**300**秒，回调程序类型选择**执行指令**，指令内容选择**/bin/sh**。在代码编辑器中编写健康检查脚本，通过`curl`向`localhost:7860/sdapi/v1/txt2img`发送POST请求，JSON参数包含`prompt`、`steps`、`height`、`width`字段，使用`mktemp`创建临时文件并通过`trap`设置清理。
5. 在实例配置面板，继续设置PreStop回调程序和回调超时时间，然后单击**部署**。
  
  开启**PreStop 回调程序**开关，将**PreStop 回调超时时间**设置为`3`秒。

## 查看实例生命周期回调函数日志

**

**说明**

目前执行指令类型回调产生的日志暂不支持写入函数日志。

您可以通过**函数日志**功能查看回调函数日志。

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com)，在左侧导航栏，选择**函数管理**>**函数列表**。
2. 在顶部菜单栏，选择地域，然后在**函数列表**页面，单击目标函数。
3. 在函数详情页面，选择**测试**页签，单击**测试函数**，然后选择**日志**>**函数日志**。
  
  在**函数日志**页签，您可以查看函数的调用日志和Initializer回调日志，示例如下。
  
  ```
  2024-06-26 10:59:23FC Initialize Start RequestId: 529eab23-9b3a-4ffc-88c8-9a686******* 2024-06-26 10:59:23FC Initialize End RequestId: 529eab23-9b3a-4ffc-88c8-9a686******* 2024-06-26 10:59:25FC Invoke Start RequestId: 1-667b840c-15c49df0-b7dc1******* 2024-06-26 10:59:25FC Invoke End RequestId: 1-667b840c-15c49df0-b7dc1*******
  ```
  
  因为每个函数实例会缓存一段时间，不会马上销毁，因此不能立即查看PreStop回调日志。如需快速触发PreStop回调，可更新函数配置或者函数代码。更新完成后，再次查看**函数日志**，您可以查看PreStop回调日志。示例如下。
  
  ```
  2024-06-26 11:04:33FC PreStop Start RequestId: c4385899-f071-490e-a8b7-e33c5******* 2024-06-26 11:04:33FC PreStop End RequestId: c4385899-f071-490e-a8b7-e33c5*******
  ```
