# HTTP触发器调用内置运行时函数时，如何获取客户端原始IP地址？

- 如果请求没有经过代理服务器转发，可以直接使用请求结构体中的requestContext.http.sourceIp字段获取客户端IP地址。
- 如果请求经过代理服务器转发，可以通过请求结构体中的headers字段获取HTTP请求头X-Forwarded-For，然后从中获取IP地址。当请求通过多个代理时，X-Forwarded-For可能包含多个IP地址，这些地址通常按照请求通过代理的顺序排列，第一个IP地址就是最原始的客户端IP地址。
  
  除了请求头X-Forwarded-For外，您还可以通过其他类似功能的HTTP请求头获取，例如X-Real-IP或X-Client-IP等。
  
  **
  
  **重要**
  
  通过请求头X-Forwarded-For或类似请求头（例如X-Real-IP或X-Client-IP等）获取客户端IP地址时需要谨慎，因为这些头部信息可能被恶意用户伪造。
