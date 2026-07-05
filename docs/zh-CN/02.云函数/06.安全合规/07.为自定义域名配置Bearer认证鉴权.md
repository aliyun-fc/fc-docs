# 为自定义域名配置Bearer认证鉴权

Bearer认证是通过在HTTP请求头携带令牌Token进行身份验证的机制，适用于 API 或微服务等需安全访问的场景。为函数绑定自定义域名后，可以通过配置Bearer认证配置Token信息，客户端在发起访问时，需在请求头添加有效的Token信息，仅当访问请求中携带的Token与自定义域名配置的Token匹配时，客户端才能正常访问函数。

## **注意事项**

- 配置Bearer认证时，请在生产环境中使用HTTPS协议，HTTP协议仅用于开发测试，因使用HTTP协议导致的Token泄露，FC不承担安全责任。
- 函数计算仅负责存储和验证您配置的Token信息，Token的生成与生命周期管理需由用户自行负责。建议定期轮换Token，特别是在发现其已泄露或可能存在安全风险的情况下，以确保系统的安全性。

## **使用限制**

- 不同自定义域名或同一个自定义域名绑定的Token必须唯一，且尽可能不要使用常见的排列组合作为Token的值，以免Token数据过于简单导致的安全问题。
- 每个Token的值长度需要在32字符到128字符之间，并且只允许包含标准 Base64 字符 ‘A-Z’, ‘a-z’, ‘0-9’, ‘+’, ‘/’，‘=’，‘-’, ‘~’, ‘.’ 。不能以数字、中划线开头。
- 每个自定义域名允许配置的Token数量在1到20之间。

## **前提条件**

已[创建函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/function-instance-1/)，并为其绑定[自定义域名](https://help.aliyun.com/zh/functioncompute/fc/configure-custom-domain-names)。

## **操作步骤**

### **步骤一：配置Bearer认证**

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com)，在左侧导航栏，选择**函数管理**>**域名管理**。
2. 在顶部菜单栏，选择地域，然后在域名列表，找到目标域名，单击**操作**列的**编辑**。
3. 在编辑自定义域名页面，展开**认证设置**，**认证方式**选择**Bearer认证**，填写**认证Token**，然后单击保存。
  
  **认证Token**的格式要求参见以下示例：
  
  ```
  { "tokens": [ { "tokenName": "tokenName-7jd", "enable": true, "tokenData": "token-dfi34ij25gd1ed6ec80g35****" }, { "enable": true, "tokenData": "token-8g7f2a2c9fc23hid82593****", "tokenName": "tokenName-20i" } ] }
  ```
  
  - 以上示例为配置多个Token，如果只需配置一个Token，保留其中一个即可。
  - 请确保每个Token认证中Token的唯一性。
  - 如果需要禁用某个Token，只需要将对应的`enable`字段设置为`false`。

### **步骤二：操作验证**

本文以Curl工具为例，携带Authorization: Bearer <token>发起HTTP请求，命令格式如下：

```
curl --data 您的数据 -X 访问方式 -H "Authorization: Bearer <token>" https://<your-custom-domain>
```

示例如下：

```
curl -X POST -H "Authorization: Bearer token-dfi34ij25gd1ed6ec80g35****" example.com
```

## **常见问题**

### **为什么开启Bearer认证后，访问域名提示**`**Authorization header is expected but missing**`**？**

该提示表示客户端通过自定义域名访问函数时未携带Authorization头，请在请求中添加`Authorization: Bearer <token>`。

### **为什么开启Bearer认证后，访问域名提示**`**access denied due to invalid bearer token**`**？**

该提示表示客户端通过自定义域名访问函数时未携带有效的Token信息，请检查Token是否正确，Token数据来自于[步骤一：配置Bearer认证](#dea3e3bcddjvn)时，配置的**认证Token**中`tokenData`字段的值。

### **开启Bearer认证后，是否会产生额外的费用？**

不会。函数计算默认提供的网关相关的功能计费都是在函数调用次数中进行收费，所以不管您是否开启Bearer认证，都不会产生额外的费用。
