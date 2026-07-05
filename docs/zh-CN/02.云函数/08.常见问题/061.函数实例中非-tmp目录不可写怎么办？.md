# 函数实例中非/tmp目录不可写怎么办？

实例的非`/tmp`目录无法写入，一般是由于实例使用了非Root用户启动。本文介绍实例使用非Root用户启动的可能原因以及解决方法。

## 原因一：函数的创建时间早于2022年08月

在函数计算中，如果是2022年08月以前创建的函数，函数的执行用户默认为用户ID大于等于10000的非Root用户，详情请参见[2022年08月发布记录](https://help.aliyun.com/zh/functioncompute/fc-2-0/product-overview/release-notes-in-2022#section-rr3-54n-bw5)。

### **解决方案**

创建新函数，并将2022年08月之前创建的目标函数的代码及配置等迁移到新创建的函数。新建函数默认使用Root用户执行，且支持写文件至所有目录。

## **原因二：**为函数配置了NAS文件系统，而用户ID和用户组ID配置为非Root

为函数配置NAS文件系统时，用户ID和用户组ID设置为非Root时，实例会使用非Root用户启动，非`/tmp`目录不可写。

### **解决方案**

将NAS文件系统配置中的用户ID和用户组ID改为Root，即UID=0，GID=0。具体操作，请参见[配置NAS文件系统](https://help.aliyun.com/zh/functioncompute/fc-2-0/user-guide/configure-a-nas-file-system)。
