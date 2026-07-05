# 调用函数时，日志中出现警告could not determine the L2 cache size on this system, assuming 256k如何解决？

## **错误解析**

函数日志中出现下方的警告，表示无法确定系统的L2缓存大小，因此假设默认值为256 KB。

```
could not determine the L2 cache size on this system, assuming 256k
```

## **可能原因**

某些依赖库试图自动检测系统的L2缓存大小以便优化其性能。但是函数计算的运行时环境是一个强隔离的沙箱环境，无法设置L2缓存大小，设置L2 cache size也不会生效。

## **解决方案**

此警告不会影响函数正常运行，忽略即可，无需处理。
