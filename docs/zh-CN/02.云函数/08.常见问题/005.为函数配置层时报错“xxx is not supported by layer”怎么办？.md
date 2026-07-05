# 为函数配置层时报错“xxx is not supported by layer”怎么办？

报错“xxx is not supported by layer”表示该层与函数的运行时不兼容，使用自定义层、官方公共层或非官方公共层均可能会遇到该报错，本文分别从使用以上三种不同类型的层的场景给出解决方案。

## **问题现象**

为函数配置层时，报错“xxx is not supported by layer”。

```
InvalidArgument: code: 400, runtime: custom is not supported by layer:acs:fc:cn-hangzhou:official:layers/Java21/versions/1
```

## **问题原因**

函数的运行时与该层不兼容，即该层的兼容运行时配置中，不包括该函数的运行时。

## **解决方案**

### **自定义层**

您可以更换其他兼容函数运行时的层，或者您可以重新发布刚才使用的自定义层，即创建层的新版本，然后将函数的运行时添加到层的兼容运行时列表中。具体操作，请参见[创建自定义层](https://help.aliyun.com/zh/functioncompute/fc/user-guide/create-a-custom-layer-1)。

### **官方公共层**

您可以查询[函数计算支持的官方公共层](https://help.aliyun.com/zh/functioncompute/fc/user-guide/configure-common-layers-for-a-function-1#section-wh2-xpc-2xu)列表，获取该层的兼容运行时和使用方法，然后根据情况选择更换函数的运行时或更换官方公共层。如果当前所有官方公共层都无法满足您的需求，请[联系我们](https://help.aliyun.com/zh/functioncompute/fc/support/contact-us-1)。

函数计算官方文档仅列举部分常见的官方公共层，更多官方公共层及其说明，请参见[公共层](https://github.com/awesome-fc/awesome-layers/blob/main/README.md)。

### **非官方公共层**

函数计算不对非官方公共层提供技术支持和维护，请联系为您提供该公共层的用户，确认层的兼容运行时和使用方法。
