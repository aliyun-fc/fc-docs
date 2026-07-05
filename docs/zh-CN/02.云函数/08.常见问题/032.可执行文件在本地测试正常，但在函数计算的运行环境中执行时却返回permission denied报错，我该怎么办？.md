# 可执行文件在本地测试正常，但在函数计算的运行环境中执行时却返回permission denied报错，我该怎么办？

## 问题现象

当我在本地使用Windows操作系统或macOS操作系统开发函数时，可执行文件在本地测试正常，但当我将函数部署到函数计算运行时，报错`permission denied`。

## 可能原因

由于在开发函数的过程中需要打包代码，在打包代码时，Windows操作系统和macOS操作系统中有些压缩工具在打包文件时可能会丢失文件或文件夹的属性。由于文件或文件夹的属性已丢失，文件已不具备可执行权限，代码再次在函数计算的运行环境（Linux）中解压部署运行时，就会遇到`permission denied`报错。

## 解决方案

请确保您的压缩工具保留了文件或文件夹的Others权限，例如755权限。当您的文件或文件夹不具备该类似权限时，您可以选择以下方法解决。

- 在[函数计算控制台](https://fcnext.console.aliyun.com)的WebIDE，打开终端窗口，执行命令`chmod +x 文件名`为文件授权。更多信息，请参见[什么是WebIDE](https://help.aliyun.com/zh/functioncompute/fc/developer-reference/how-to-use-webide)。
- 在本地开发函数时，使用Linux操作系统开发。
