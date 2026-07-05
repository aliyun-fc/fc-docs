# Sandbox 公网 URL

`sandbox.getHost(port)` 用于获取沙箱内指定端口的公网访问域名。它适合预览 Web 应用、暴露临时 API 或连接沙箱中的调试服务。

## 启动服务并获取访问地址

```typescript
const handle = await sandbox.commands.run("python3 -m http.server 8000", {
  background: true,
});

const host = sandbox.getHost(8000);
const url = `https://${host}`;

console.log(url);

await sandbox.commands.kill(handle.pid);
```

## 使用建议

- 服务必须监听对应端口，否则访问地址无法正常响应。
- 长时间运行的服务应使用后台命令，并保存进程 `pid`。
- 访问地址适合临时服务预览，不建议作为长期生产域名。

