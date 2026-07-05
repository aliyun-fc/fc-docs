# 遇到SDK.ServerUnreachable : SocketTimeoutException has occurred on a socket read or accept的问题怎么办？

请检查您调用Java SDK的代码，确保配置的ReadTimeoutMillis要大于您的函数超时时间。
