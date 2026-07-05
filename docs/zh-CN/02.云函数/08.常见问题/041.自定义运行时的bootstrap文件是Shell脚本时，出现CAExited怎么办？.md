# 自定义运行时的bootstrap文件是Shell脚本时，出现CAExited怎么办？

当自定义运行时的bootstrap文件是Shell脚本，且出现以下错误时，自定义运行时的bootstrap文件一定要添加`#!/bin/bash`。

```
{ "ErrorCode":"CAExited", "ErrorMessage":"The CA process either cannot be started or exited:ContainerStartDuration:25037266905. CA process cannot be started or exited already: rpc error: code = 106 desc = ContainerStartDuration:25000000000. Ping CA failed due to: dial tcp 21.0.XX.XX:9000: i/o timeout Logs : 2019-11-29T07:27:50.759658265Z panic: standard_init_linux.go:178: exec user process caused \"exec format error\" }
```

如果是二进制可执行文件，例如Go、C++直接编译出来的目标二进制文件，则不需要添加`#!/bin/bash`。
