# 「不兼容」挂载 Volumes

E2B 支持创建沙箱时通过 `volumeMounts` 挂载 Volume。云沙箱当前不兼容 E2B Volume 挂载能力。

不要依赖以下配置在沙箱内获得持久目录：

```typescript
await Sandbox.create({
  volumeMounts: {
    "/data": "my-volume",
  },
});
```

如果业务需要共享或持久目录，应使用云上存储方案，并在业务架构中显式处理挂载、读写和权限。

