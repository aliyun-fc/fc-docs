# 想要RAM用户A访问部分函数，RAM用户B访问另外一部分函数，如何操作？

您可以通过标签功能将函数进行分组，实现不同RAM用户对不同分组的函数的操作权限。例如阿里云主账号在函数计算中创建了10个函数，需要将5个函数授权给dev团队，另外5个函数授权给ops团队。每个团队只能管理被授权的函数，不能管理未被授权的函数。此时可以通过标签功能将10个函数进行分组，然后为不同团队（RAM用户或用户组）授予不同的权限。

## **前提条件**

已在[函数计算控制台](https://fcnext.console.aliyun.com/)创建10个函数，并为其中5个函数添加一对标签，标签键*team*，标签值*dev*，为另外5个函数添加标签键*team*，标签值*ops*。关于函数标签的配置说明，请参见[标签管理](https://help.aliyun.com/zh/functioncompute/fc/user-guide/function-tags-management#section-npa-jen-09l)。

## **操作步骤**

**

**重要**

- 如果您操作的函数是在函数计算2.0控制台创建的函数（名称中含有$符号），标签会绑定到2.0的服务，而不是绑定到函数，详情请参见[管理标签](https://help.aliyun.com/zh/functioncompute/fc-2-0/user-guide/tag-management)。
- 为遵循最小授权原则，请不要为RAM用户授予权限策略`AliyunFCFullAccess`或`AliyunFCReadOnlyAccess`等权限级别过高的策略，否则将不能使用本文介绍的通过函数标签分组管理函数。

1. 在阿里云主账号下创建两个RAM用户。具体操作，请参见[创建RAM用户](https://help.aliyun.com/zh/ram/user-guide/create-a-ram-user#task-187540)。
2. 创建dev和ops两个用户组。具体操作，请参见[创建RAM用户组](https://help.aliyun.com/zh/ram/user-guide/create-a-user-group#task-187540)。
3. 将已创建的两个RAM用户分别添加到用户组dev和ops下。具体操作，请参见[为RAM用户组添加RAM用户](https://help.aliyun.com/zh/ram/user-guide/add-a-ram-user-to-a-ram-user-group#task-187540)。
4. 为两个用户组dev和ops授予不同权限策略。
  
  权限策略分为系统权限策略和自定义权限策略，根据实际场景选择合适的权限策略。本文以为用户组授予自定义权限策略为例进行介绍。
  
  1. [创建自定义权限策略](https://help.aliyun.com/zh/ram/create-a-custom-policy#task-glf-vwf-xdb)。
    
    假设给dev团队创建的自定义策略名称为*policyForDevTeam*，策略示例如下。
    
    ```
    { "Statement": [ { "Action": "fc:*", "Effect": "Allow", "Resource": "*", "Condition": { "StringEquals": { "fc:tag/team": "dev" } } }, { "Action": "fc:ListFunctions", "Effect": "Allow", "Resource": "*" }, { "Action": "fc:ListTagResources", "Effect": "Allow", "Resource": "*" } ], "Version": "1" }
    ```
    
    假设给ops团队创建的自定义策略名称为*policyForOpsTeam*，策略示例如下。
    
    ```
    { "Statement": [ { "Action": "fc:*", "Effect": "Allow", "Resource": "*", "Condition": { "StringEquals": { "fc:tag/team": "ops" } } }, { "Action": "fc:ListFunctions", "Effect": "Allow", "Resource": "*" }, { "Action": "fc:ListTagResources", "Effect": "Allow", "Resource": "*" } ], "Version": "1" }
    ```
  2. 分别为用户组dev和ops授予自定义权限策略*policyForDevTeam**和**policyForOpsTeam**。具体操作，请参见*[为RAM用户组授权](https://help.aliyun.com/zh/ram/user-guide/grant-permissions-to-a-ram-user-group#task-187800)。
5. 分别使用两个RAM用户登录[函数计算控制台](https://fcnext.console.aliyun.com/)验证结果。关于使用RAM用户登录控制台的操作步骤，请参见[RAM用户登录阿里云控制台](https://help.aliyun.com/zh/ram/user-guide/log-on-to-the-alibaba-cloud-management-console-as-a-ram-user)。
  
  您可以看到从属于用户组dev的RAM用户仅拥有添加了标签`team:dev`的函数的操作权限，从属于用户组ops的RAM用户仅拥有添加了标签`team:ops`的函数的操作权限。
