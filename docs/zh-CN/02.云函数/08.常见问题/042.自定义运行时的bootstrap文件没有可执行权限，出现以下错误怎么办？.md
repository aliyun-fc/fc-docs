# 自定义运行时的bootstrap文件没有可执行权限，出现以下错误怎么办？

自定义运行时的bootstrap文件，一定要具备777或755权限，否则会出现以下错误：

```
{ "ErrorCode":"CAFilePermission", "ErrorMessage":"The CA process cannot be started due to bootstrap file don't have execute permissions" }
```

您可以在打包文件前执行chmod 777 bootstrap或chmod 755 bootstrap命令获取权限。
