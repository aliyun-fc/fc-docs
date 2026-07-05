# PHP运行环境内置的Tablestore PHP SDK使用有问题怎么办？

由于内置Protobuf扩展和Tablestore依赖的PHP实现的Protobuf有冲突，导致PHP运行环境内置的Tablestore PHP SDK使用有问题。解决方法，请参见[PHP运行环境动态加载卸载内置扩展](https://yq.aliyun.com/articles/645670)。同时，PHP运行环境动态加载卸载内置扩展，建议您通过环境变量裁剪不必要的扩展，优化运行环境的启动速度。
