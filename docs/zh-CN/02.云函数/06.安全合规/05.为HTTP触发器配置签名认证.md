# 为HTTP触发器配置签名认证

函数计算支持为HTTP触发器配置签名认证，当请求消息到达函数计算网关后，网关会对开启签名认证的HTTP触发器上的请求进行认证，您的函数无需再次对请求签名进行认证，只需关注业务逻辑即可。本文介绍如何通过控制台为HTTP触发器配置签名认证以及如何验证通过签名访问HTTP触发器。

## **开启HTTP触发器签名认证**

本文介绍如何在函数已有的HTTP触发器中开启签名认证，您需要先创建函数，具体操作，请参见[创建函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/function-instance-1/)。

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com)，在左侧导航栏，选择**函数管理**>**函数列表**。
2. 在顶部菜单栏，选择地域，然后在**函数列表**页面，单击目标函数。
3. 在函数配置页面，选择**触发器**页签，然后单击目标触发器右侧**操作**列的**编辑**。
4. 在编辑触发器面板，将**认证方式**修改为**签名认证**，然后单击**确定**。

## **通过签名访问HTTP触发器地址**

HTTP触发器的签名方式遵循阿里云SDK的签名机制，详情请参见[签名机制](https://help.aliyun.com/zh/sdk/product-overview/v3-request-structure-and-signature#section-ie8-ul4-4pk)。阿里云SDK提供了各种语言的签名方法，使用流程如下：

1. 通过阿里云SDK生成签名字符串。
2. 将签名字符串设置到HTTP请求的Authorization Header中。
3. 使用任意的HTTP客户端发起请求。

### **各语言签名SDK**

阿里云提供的各语言签名SDK，您可以使用如下快捷方式安装。

| **语言类型** | **SDK** |
| --- | --- |
| Golang | go get github.com/alibabacloud-go/openapi-util/service |
| Python | pip install alibabacloud-openapi-util |
| Node.js | npm install @alicloud/openapi-util |
| Java | ```<br><dependency> <groupId>com.aliyun</groupId> <artifactId>openapiutil</artifactId> <version>0.2.1</version> </dependency> <dependency> <groupId>com.aliyun</groupId> <artifactId>tea-openapi</artifactId> <version>0.3.1</version> </dependency><br>``` |

### **各语言请求示例**

本文提供以下请求示例，仅供参考，完整的签名机制请参见[签名机制](https://help.aliyun.com/zh/sdk/product-overview/v3-request-structure-and-signature#section-ie8-ul4-4pk)。

Python

```
# -*- coding: utf-8 -*- import os from datetime import datetime from urllib.parse import urlparse, parse_qs import requests from alibabacloud_openapi_util.client import Client as util from Tea.request import TeaRequest accessKeyId = os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'] accessKeySecret = os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'] securityToken = os.environ.get('ALIBABA_CLOUD_SECURITY_TOKEN', '') # 可选，使用STS时需要提供 # method参数请求方式要求必须大写，如：POST、GET，如果您的请求方式为GET，需要将下方requests.post改为requests.get method = 'POST' body = 'hello world' url = 'https://xx.cn-shanghai.fcapp.run/hello?foo=bar' # 你的HTTP触发器地址 date = datetime.utcnow().isoformat('T')[:19]+'Z' headers = { 'x-acs-date': date, 'x-acs-security-token': securityToken } parsedUrl = urlparse(url) authRequest = TeaRequest() authRequest.method = method authRequest.pathname = parsedUrl.path.replace('$', '%24') authRequest.headers = headers authRequest.query = {k: v[0] for k, v in parse_qs(parsedUrl.query).items()} auth = util.get_authorization(authRequest, 'ACS3-HMAC-SHA256', '', accessKeyId, accessKeySecret) headers['authorization'] = auth #如果method请求方式为GET，需要将下方requests.post改为requests.get resp = requests.post(url, body, headers=headers) print(resp.text)
```

Node.js

```
const util = require("@alicloud/openapi-util"); const axios = require('axios'); async function main() { const accessKeyId = process.env['ALIBABA_CLOUD_ACCESS_KEY_ID']; const accessKeySecret = process.env['ALIBABA_CLOUD_ACCESS_KEY_SECRET']; const securityToken = process.env['ALIBABA_CLOUD_SECURITY_TOKEN'] || ''; // 可选，使用STS时需要提供 //method参数请求方式要求必须大写，如：POST、GET，如果您的请求方式为GET，需要将下方axios.post改为axios.get const method = 'POST'; const body = 'hello world'; const url = 'https://xx.cn-shanghai.fcapp.run/hello?foo=bar' // 你的HTTP触发器地址 const date = new Date().toISOString(); let headers = { 'x-acs-date': date, 'x-acs-security-token': securityToken }; const parsedUrl = new URL(url); const authRequest = { method: method, pathname: parsedUrl.pathname.replace('$', '%24'), headers: headers, query: Object.fromEntries(parsedUrl.searchParams), }; console.log('auth: ', authRequest); const auth = util.default.getAuthorization(authRequest, 'ACS3-HMAC-SHA256', '', accessKeyId, accessKeySecret); headers['authorization'] = auth; //如果method请求方式为GET，需要将下方axios.post改为axios.get const resp = await axios.post(url, body, { headers: headers, }); console.log('resp: ', resp.data); } main().catch(console.error);
```

Go

```
package main import ( "io/ioutil" "log" "net/http" "os" "strings" "time" openapiutil "github.com/alibabacloud-go/openapi-util/service" "github.com/alibabacloud-go/tea/tea" ) func main() { accessKeyId := tea.String(os.Getenv("ALIBABA_CLOUD_ACCESS_KEY_ID")) accessKeySecret := tea.String(os.Getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET")) securityToken := tea.String(os.Getenv("ALIBABA_CLOUD_SECURITY_TOKEN")) // 可选，使用STS时需要提供 //method参数请求方式要求必须大写 method := "POST" body := "hello world" url := "https://xx.cn-shanghai.fcapp.run/hello?foo=bar" // 你的HTTP触发器地址 req, err := http.NewRequest(method, url, strings.NewReader(body)) if err != nil { log.Printf("new request error: %v", err) return } date := time.Now().UTC().Format(time.RFC3339) req.Header.Set("x-acs-date", date) req.Header.Set("x-acs-security-token", *securityToken) authRequest := &tea.Request{ Method: &method, Pathname: tea.String(strings.ReplaceAll(req.URL.Path, "$", "%24")), Headers: make(map[string]*string), Query: make(map[string]*string), } for k := range req.URL.Query() { authRequest.Query[k] = tea.String(req.URL.Query().Get(k)) } for k := range req.Header { authRequest.Headers[k] = tea.String(req.Header.Get(k)) } auth := openapiutil.GetAuthorization(authRequest, tea.String("ACS3-HMAC-SHA256"), nil, accessKeyId, accessKeySecret) req.Header.Set("authorization", *auth) resp, err := http.DefaultClient.Do(req) if err != nil { log.Printf("post error: %v", err) return } defer resp.Body.Close() buf, err := ioutil.ReadAll(resp.Body) if err != nil { log.Printf("read body error: %v", err) return } log.Printf("resp: %v, body: %s", resp, string(buf)) }
```

Java

```
package com.aliyun.sample; import org.apache.http.NameValuePair; import org.apache.http.client.methods.HttpPost; import org.apache.http.client.utils.URLEncodedUtils; import org.apache.http.entity.StringEntity; import org.apache.http.impl.client.CloseableHttpClient; import org.apache.http.impl.client.HttpClients; import org.apache.http.util.EntityUtils; import java.net.URI; import java.nio.charset.StandardCharsets; import java.time.Instant; import java.util.HashMap; import java.util.Map; import com.aliyun.tea.*; public class Sample { public static void main(String[] args_) throws Exception { String accessKeyId = System.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID"); String accessKeySecret = System.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET"); String securityToken = System.getenv("ALIBABA_CLOUD_SECURITY_TOKEN"); // 可选，使用STS时需要提供 if (securityToken == null) { securityToken = ""; } //method参数请求方式要求必须大写，如：POST、GET，如果您的请求方式为GET，需要将下方HttpPost改为HttpGet String method = "POST"; String body = "hello world"; String url = "https://xx.cn-shanghai.fcapp.run/hello?foo=bar"; // 你的HTTP触发器地址 Map<String, String> headers = new HashMap<String, String>(); String date = Instant.now().toString(); headers.put("x-acs-date", date); headers.put("x-acs-security-token", securityToken); URI uri = new URI(url); Map<String, String> query = new HashMap<String, String>(); for (NameValuePair pair : URLEncodedUtils.parse(uri, StandardCharsets.UTF_8)) { query.put(pair.getName(), pair.getValue()); } TeaRequest req = new TeaRequest(); req.method = method; req.pathname = uri.getPath().replace("$", "%24"); req.headers = headers; req.query = query; String auth = com.aliyun.openapiutil.Client.getAuthorization( req, "ACS3-HMAC-SHA256", "", accessKeyId, accessKeySecret); headers.put("authorization", auth); //如果method请求方式为GET，需要将下方HttpPost改为HttpGet HttpPost request = new HttpPost(url); for (Map.Entry<String, String> entry : headers.entrySet()) { request.setHeader(entry.getKey(), entry.getValue()); } StringEntity entity = new StringEntity(body); request.setEntity(entity); // Execute the request try (CloseableHttpClient httpClient = HttpClients.createDefault()) { org.apache.http.HttpResponse response = httpClient.execute(request); String responseString = EntityUtils.toString(response.getEntity(), StandardCharsets.UTF_8); System.out.println(responseString); } } }
```

### **操作步骤**

本文以Go语言为例，演示如何通过签名访问HTTP触发器。

1. 执行`go get github.com/alibabacloud-go/openapi-util/service`安装SDK。
2. 在本地准备代码文件`main.go`。
  
  您可以直接使用本文提供的示例代码，详情请参见[各语言请求示例](#0945a8a8d2mp4)。
3. 执行`go run main.go`运行代码。
  
  执行成功后返回结果如下，表示已正确地获取函数的Response。
  
  ```
  2024/02/22 17:21:31 resp: &{200 OK 200 HTTP/1.1 1 1 map[Access-Control-Expose-Headers:[Date,x-fc-request-id] Content-Disposition:[attachment] Content-Length:[14] Content-Type:[text/plain; charset=utf-8] Date:[Thu, 22 Feb 2024 09:21:31 GMT] X-Fc-Request-Id:[1-65d71219-15d63510-fecf237c590c]] 0xc000120040 14 [] false false map[] 0xc000100100 0xc0000e0370}, body: Hello, Golang!
  ```

## **常见问题**

### **为什么HTTP触发器开启签名认证之后，通过HTTP触发器访问函数提示：required HTTP header Date was not specified？**

该提示说明认证失败，可能原因如下：

1. 没有在请求中进行签名。
2. 在请求中做了签名，但是没有提供Date这个Header。

### **为什么HTTP触发器开启签名认证之后，通过HTTP触发器访问函数提示：the difference between the request time 'Thu, 04 Jan 2024 01:33:13 GMT' and the current time 'Thu, 04 Jan 2024 08:34:58 GMT' is too large？**

该提示说明签名过期，请您重新使用当前时间进行签名。

### **为什么HTTP触发器开启签名认证之后，通过HTTP触发器访问函数提示：The request signature we calculated does not match the signature you provided. Check your access key and signing method？**

请求中的签名与函数计算计算得到的签名不一致，认证失败。
