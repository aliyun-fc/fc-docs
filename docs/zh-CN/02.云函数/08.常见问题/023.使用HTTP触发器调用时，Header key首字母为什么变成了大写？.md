# 使用HTTP触发器调用时，Header key首字母为什么变成了大写？

HTTP Header请求头以键值对的形式显示。根据HTTP标准，Header的键是大小写不敏感的。

当使用HTTP触发器调用内置运行时，函数计算3.0版会将HTTP请求转换成HTTP触发器的Event格式，在转换HTTP Header时，会基于Golang的net/http标准库，将HTTP请求Header的键进行规范化。

规范化的原则是将键的首字母和任何连字符后的字母转成大写，其余字母转换为小写。例如，"accept-encoding" 规范化后是 "Accept-Encoding"。
