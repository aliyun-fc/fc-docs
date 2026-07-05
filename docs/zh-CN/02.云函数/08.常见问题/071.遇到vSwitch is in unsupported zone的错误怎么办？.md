# 遇到vSwitch is in unsupported zone的错误怎么办？

根据错误信息，找到函数计算所支持的可用区（Zone），在您的VPC中，在此可用区创建一个虚拟交换机（vSwitch），然后以此交换机配置函数的VPC。如果在此交换机中未能找到函数计算，说明您的虚拟交换机未创建成功，您需要重新在VPC环境中的函数计算支持的可用区内，创建一个虚拟交换机（vSwitch），并在函数的VPC配置中设置此vSwitch ID。

配置成功后，在函数中就可以访问您的VPC资源了。同一个VPC内不同可用区的交换机默认内网互通，详细信息，请参见[创建和管理专有网络](https://help.aliyun.com/zh/vpc/user-guide/create-and-manage-a-vpc#task-1012575)。
