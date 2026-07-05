# 使用go build编译的速度较慢怎么办？

执行

`go build`

编译速度过慢、卡顿时，可以尝试使用代理加速。代码如下。

```
export GOPROXY=https://goproxy.cn
```
