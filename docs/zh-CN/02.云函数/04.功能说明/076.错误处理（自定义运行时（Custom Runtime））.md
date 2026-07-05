# 错误处理

本文介绍自定义运行时运行环境常见的错误类型及排查方法。

## 实例启动失败（Failed to start function instance）

### 报错示例

```
The function cannot be started. Failed to start function instance. Error: the file /code/bootstrap is not exist
```

### 报错排查

函数实例启动失败，一般是启动命令异常或者启动命令不存在。

- 如果未设置**启动命令**，函数计算默认使用`/code/bootstrap`作为启动命令。如果代码包中没有该文件，可增加`/code/bootstrap`脚本，或修改**启动命令**。
- 如果已设置**启动命令**，请参考报错信息中的`Error: the file xxx is not exist`，确认该文件是否存在。

关于设置**启动命令**的具体操作，请参见[基本原理](https://help.aliyun.com/zh/functioncompute/fc/user-guide/principles-1#section-twg-3fh-n6l)。

## 实例健康检查失败（Function instance health check failed）

### 报错示例

```
Function instance health check failed on port 9001 in 120 seconds.\nLogs:
```

### 报错排查

函数实例健康检查失败，一般是代码中监听的IP地址或者端口设置错误导致。函数实例启动后，平台会根据函数配置的端口进行4层连通性检查，若在超时时间内检查不通过，则返回`Function instance health check failed`报错。

监听地址和端口必须满足以下条件。

- 监听地址
  
  代码中的监听IP地址必须设置为`0.0.0.0`或`*`，不能设置为`127.0.0.0`或`localhost`。
- 监听端口
  
  监听端口必须和函数配置中的端口保持一致。自定义运行时默认监听端口为`9000`。
  
  - 如果使用默认端口，请确保代码中HTTP Server监听的端口也是`9000`。
  - 如果设置了**监听端口**，请确保代码中HTTP Server监听的端口与其一致。

关于设置**监听端口**的具体操作，请参见[HTTP Server配置要求](https://help.aliyun.com/zh/functioncompute/fc/user-guide/principles-1#title-wps-1wx-lyx)。

## 实例进程异常退出（Function instance exited unexpectedly）

### 报错示例

```
Function instance exited unexpectedly(code 2, message:no such file or directory) with start command '/code/bootstrap '. Logs:
```

- `Function instance exited unexpectedly`：表示实例启动进程异常退出。
- `code 2, message:no such file or directory`：表示实例启动进程的Linux退出码和该退出码的含义。
- `with start command '/code/bootstrap '`：表示该实例的启动命令。

**

**说明**

进程退出码及其含义仅作为问题排查的参考，不能完全确定实例退出原因，因为该退出码可能是代码中实现，与Linux退出码含义不完全相匹配。

### 报错排查

- **启动命令没有可执行权限**
  
  ```
  The function cannot be started. Function instance exited unexpectedly(code 13, message:permission denied) with start command '/code/bootstrap '.
  ```
  
  如果实例启动命令没有可执行权限，报错信息中的退出码一般为`code 13, message:permission denied`。可以在打包代码前，执行`chmod 755 bootstrap`、`chmod 777 bootstrap`或`chmod +x bootstrap`赋予文件的可执行权限。
- **文件不存在**
  
  ```
  Function instance exited unexpectedly(code 2, message:no such file or directory) with start command 'python3 not_exist_file.py '. Logs:xxx
  ```
  
  如果启动参数中的文件不存在，则报错信息中的退出码一般为`code 2, message:no such file or directory`。特殊情况下，报错信息中的退出码可能不是`code 2, message:no such file or directory`或无退出码，此时，需要根据报错日志进行排查。
  
  下文列举不同启动命令下，文件不存在的报错信息。
  
  - **Python**
    
    当实例启动命令为`python3 not_exist_file.py`时，退出码为`code 2, message:no such file or directory`。
    
    如果将该启动命令放到Shell脚本中，示例如下，然后修改启动命令为`/code/bootstrap`。执行函数会出现报错`/code/not_exist_file.py`不存在。
    
    Shell脚本示例
    
    ```
    #!/bin/bash python3 not_exist_file.py
    ```
    
    报错信息
    
    ```
    Function instance exited unexpectedly(code 2, message:no such file or directory) with start command '/code/bootstrap '. Logs:python3: can't open file '/code/not_exist_file.py': [Errno 2] No such file or directory
    ```
  - **Node.js**
    
    当实例启动命令为`npm run start`，在package.json中配置的脚本启动命令为`node ./not_exist_file.js`，报错信息如下。
    
    ```
    Function instance exited unexpectedly(code 1, message:operation not permitted) with start command 'npm run start '. Logs:> nodejs-express@0.0.0 start /code > node ./not_exist_file.js internal/modules/cjs/loader.js:905 throw err; ^ Error: Cannot find module '/code/not_exist_file.js' at Function.Module._resolveFilename (internal/modules/cjs/loader.js:902:15) at Function.Module._load (internal/modules/cjs/loader.js:746:27) at Function.executeUserEntryPoint [as runMain] (internal/modules/run_main.js:75:12) at internal/main/run_main_module.js:17:47 { code: 'MODULE_NOT_FOUND', requireStack: [] } npm ERR! code ELIFECYCLE npm ERR! errno 1 ERR! nodejs-express@0.0.0 start: `node ./not_exist_file.js` npm ERR! ERR! Failed at the nodejs-express@0.0.0 start script. npm ERR! This is probably not a problem with npm. There is likely additional logging output above. npm ERR! A complete log of this run can be found in: npm ERR! /root/.npm/_logs/2022-10-31T08_02_29_434Z-debug.log
    ```
    
    从报错日志中可以找到原因`Error: Cannot find module '/code/not_exist_file.js'`，即`/code/not_exist_file.js`不存在。报错的退出码为`code 1, message:operation not permitted`。
    
    当实例启动命令为`node ./not_exist_file.js`时，报错类似。
  - **Java**
    
    当实例启动命令为`java -Dserver.port=9000 -jar target/not_exist_file.jar`时，报错信息如下。
    
    ```
    Function instance exited unexpectedly(code 1, message:operation not permitted) with start command 'java -Dserver.port=9000 -jar target/not_exist_file.jar '. Logs:Error: Unable to access jarfile target/not_exist_file.jar
    ```
    
    从报错日志中可以找到原因`Unable to access jarfile target/not_exist_file.jar`，即`target/not_exist_file.jar`文件不存在。报错的退出码为`code 1, message:operation not permitted`。
  - **PHP**
    
    当实例启动命令为`php not_exist_file.php`时，报错信息如下。
    
    ```
    Function instance exited unexpectedly(code 1, message:operation not permitted) with start command 'php not_exist_file.php '. Logs:Could not open input file: not_exist_file.php
    ```
    
    从报错日志中可以找到原因`Could not open input file: not_exist_file.php`，即`not_exist_file.php`文件不存在。报错的退出码为`code 1, message:operation not permitted`。
  - **.NET Core**
    
    当实例启动命令为`dotnet ./target/NotExistFile.dll`时，报错信息如下。
    
    ```
    Function instance exited unexpectedly(code 145) with start command 'dotnet ./target/NotExistFile.dll '. Logs:Could not execute because the application was not found or a compatible .NET SDK is not installed. Possible reasons for this include: * You intended to execute a .NET program: The application './target/NotExistFile.dll' does not exist. * You intended to execute a .NET SDK command: It was not possible to find any installed .NET SDKs. Install a .NET SDK from: https://aka.ms/dotnet-download
    ```
    
    其报错日志中有详细的排查方法，`./target/NotExistFile.dll`文件不存在或`.NET SDK`没有安装。报错的退出码为`code 145`。
  - **Ruby**
    
    当实例启动命令为`ruby not_exist_file.rb`时，报错信息如下。
    
    ```
    Function instance exited unexpectedly(code 1, message:operation not permitted) with start command 'ruby not_exist_file.rb '. Logs:Traceback (most recent call last): ruby: No such file or directory -- not_exist_file.rb (LoadError)
    ```
    
    从报错日志中可以找到原因`No such file or directory -- not_exist_file.rb`，即`not_exist_file.rb`文件不存在。报错的退出码为`code 1, message:operation not permitted`。
- **文件格式错误**
  
  ```
  Function instance exited unexpectedly(code 8, message:exec format error) with start command '/code/bootstrap '. Logs:
  ```
  
  自定义运行时环境为`x86-64`架构的Linux，需要保证启动文件兼容该系统环境。如果启动命令为Shell脚本，需要确保文件为Linux格式，并且文件包含Shell的解释行`#!`。如果启动命令为二进制可执行文件，需要确保该文件为兼容Linux系统的ELF文件格式。具体信息如下。
  
  - **启动命令Shell脚本解释行错误**
    
    当Shell脚本缺少首行解释行，或者解释行错误时，实例退出码一般为`8 exec format error`。因此，需要在文件首行添加正确的解释行。
    
    如您需要使用Bash运行该脚本，可以在文件首行加上命令`#!/usr/bin/env bash`或`#!/bin/bash`，推荐使用`#!/usr/bin/env bash`。在自定义运行时系统环境中，`/bin/sh`默认为`/bin/bash`，因此，也可以使用命令`#!/usr/bin/env sh`或`#!/bin/sh`。
  - **启动命令Shell脚本为Windows格式**
    
    执行以下测试脚本。
    
    ```
    #!/usr/bin/env bash node /code/index.js
    ```
    
    报错如下。
    
    ```
    Function instance exited unexpectedly(code 127, message:key has expired) with start command '/code/bootstrap '. Logs:/usr/bin/env: ‘bash\r’: No such file or directory
    ```
    
    在错误日志中`bash\r`表示在`bash`后面多余一个字符`\r`。Unix文件换行符为`\n`，Windows文件换行符为`\r\n`，因此，该文件是Windows格式。
    
    如果您的脚本在Windows系统下创建，需要将脚本格式转换为Unix格式。您可以在Linux系统下通过执行命令`dos2unix`进行转换，或者使用函数计算的WebIDE进行转换。更多信息，请参见[如何使用函数计算的WebIDE转换文件格式？](https://help.aliyun.com/zh/functioncompute/fc/how-to-convert-file-formats-by-using-webide-provided-by-function-compute)。
  - **启动命令为二进制可执行文件**
    
    如果启动命令为可执行文件，请确保该文件为兼容Linux系统的ELF文件格式。例如，在一台M1芯片的Mac机器上，使用默认配置`GOOS=darwin GOARCH=arm64`编译Golang代码，然后进行打包上传并测试，报错信息如下所示。
    
    ```
    Function instance exited unexpectedly(code 8, message:exec format error) with start command './main '. Logs:
    ```
    
    实例退出码为`8 exec format error`，表示文件格式错误。需要在编译时添加配置`GOOS=linux GOARCH=amd64`。具体信息，请参见[编译部署代码包](https://help.aliyun.com/zh/functioncompute/fc/user-guide/compile-and-deploy-code-packages-in-a-go-runtime)。
    
    展开查看如何判断可执行文件的格式。
    
    - 查看使用`GOOS=darwin GOARCH=arm64`编译的可执行文件格式，如下所示。
      
      ```
      $ file main main: Mach-O 64-bit arm64 executable, flags:<|DYLDLINK|PIE>
      ```
      
      其文件格式为`Mach-O`，CPU架构为`arm64`，与自定义运行时底层环境不兼容。
    - 查看使用`GOOS=linux GOARCH=amd64`编译的可执行文件格式，如下所示。
      
      ```
      $ file main main: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), statically linked, Go BuildID=xxx, not stripped
      ```
      
      其文件格式为`ELF`，CPU架构为`x86-64`，与自定义运行时底层环境兼容。
    
    **
    
    **说明**
    
    - Linux系统的可执行文件格式一般为ELF格式。
    - Mac系统的可执行文件是Mach-O格式。
    - Windows系统的可执行文件是PE格式。
- **常见退出码**
  
  除了以上列举的退出码以外，还有其他的常见错误情况，具体信息如下。
  
  - **Exit Code 137**
    
    程序收到信号SIGKILL异常退出，一般情况是`OOMKilled（Out of Memory）`问题，程序因内存不足而退出。此时，可以尝试调大函数的内存规格。

## 更多信息

如果遇到的错误类型未包含在本文列举的错误列表中，请参见[自定义运行时 FAQ](https://help.aliyun.com/zh/functioncompute/fc/faq-about-custom-runtimes/)进一步排查原因。
