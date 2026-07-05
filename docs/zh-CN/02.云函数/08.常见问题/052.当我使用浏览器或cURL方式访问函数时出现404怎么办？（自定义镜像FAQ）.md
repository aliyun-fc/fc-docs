# 当我使用浏览器或cURL方式访问函数时出现404怎么办？

## 问题现象

我创建了一个自定义镜像的HTTP函数，其中服务名为*CustomDemo*、函数名为*func-http*，并且设置了匿名的HTTP触发器，实现自定义镜像的HTTP Server的路由代码示例如下：

```
@app.route('/test', methods = ['POST','GET']) def test():
```

当我使用cURL工具或浏览器等方式访问HTTP函数的URL时，遇到

`404`

报错。

- 使用cURL工具访问HTTP函数。
  
  ```
  curl -v https://164901546557****.cn-hangzhou.fc.aliyuncs.com/2016-08-15/proxy/CustomDemo/func-http/test
  ```
- 使用浏览器访问HTTP函数。
  
  ```
  https://164901546557****.cn-hangzhou.fc.aliyuncs.com/2016-08-15/proxy/CustomDemo/func-http/test
  ```
  
  **
  
  **说明**
  
  HTTP函数的URL格式为：
  
  `https://<account_id>.<region_id>.fc.aliyuncs.com/<version>/proxy/<serviceName>/<functionName>/<path>`
  
  。

## 解决方案

您可以选择以下任意方式解决该问题：

- 使用
  
  函数计算
  
  为新建HTTP触发器分配的子域名重新访问。具体信息，请参见
  
  [步骤三：测试函数](https://help.aliyun.com/zh/functioncompute/fc-2-0/user-guide/configure-an-http-trigger-that-invokes-a-function-with-http-requests#section-swn-vhk-d8a)
  
  。
  
  子域名格式如下：
  
  ```
  https://<subdomain>.<region_id>.fcapp.run/[action?queries]
  ```
  
  本文的访问示例如下：
  
  ```
  https://funcname-svcname-khljsjksld.cn-shanghai.fcapp.run/action?hello=world
  ```
- 在访问的命令中增加名为
  
  `x-fc-invocation-target`
  
  的Header。访问格式如下：
  
  ```
  curl -v -H "x-fc-invocation-target: 2016-08-15/proxy/$ServiceName/$functionName" https://<account_id>.<region_id>.fc.aliyuncs.com/$path
  ```
  
  本文的访问示例如下：
  
  ```
  curl -v -H "x-fc-invocation-target: 2016-08-15/proxy/CustomDemo/func-http" https://164901546557****.cn-hangzhou.fc.aliyuncs.com/test
  ```
- 为您的函数绑定自定义域名，绑定成功后再执行以下命令重新访问即可。关于绑定域名的操作步骤，请参见
  
  [配置自定义域名](https://help.aliyun.com/zh/functioncompute/fc-2-0/user-guide/configure-a-custom-domain-name#multiTask145)
  
  。
  
  假设域名是
  
  `example.com`
  
  ，访问格式如下：
  
  ```
  curl -v https://example.com/$path
  ```
  
  本文的访问示例如下：
  
  ```
  curl -v https://example.com/test
  ```
  
  **
  
  **重要**
  
  您需要将路径
  
  `/$path`
  
  设置为绑定的自定义域名中设置的与
  
  函数名称
  
  和
  
  服务名称
  
  对应的路径。更多信息，请参见
  
  [路由匹配规则](https://help.aliyun.com/zh/functioncompute/fc-2-0/user-guide/configure-a-custom-domain-name#section-e4u-lg4-pgn)
  
  。
- 修改您的函数代码，并且成功部署函数后，重新使用默认的URL访问即可。函数代码修改示例如下：
  
  ```
  @app.route('/2016-08-15/proxy/CustomDemo/func-http/test', methods = ['POST','GET']) def test():
  ```
  
  本文的访问示例如下：
  
  ```
  curl -v https://164901546557****.cn-hangzhou.fc.aliyuncs.com/2016-08-15/proxy/CustomDemo/func-http/test
  ```
