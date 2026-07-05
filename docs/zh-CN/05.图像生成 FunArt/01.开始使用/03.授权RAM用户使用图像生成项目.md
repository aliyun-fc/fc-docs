# 授权RAM用户使用图像生成项目

本文介绍如何授予RAM用户使用图像生成项目的权限。

## 前提条件

已[创建RAM用户](https://help.aliyun.com/zh/ram/user-guide/create-a-ram-user#task-187540)。

## 背景信息

您可以通过如下两种方式授予RAM用户**使用图像生成**项目的权限。

- 系统权限策略：权限范围较大，用户无法修改系统权限策略的内容，但配置步骤简单。
- 自定义权限策略：用户可以为所有RAM用户添加自定义权限策略，简化RAM用户配置。也可以修改自定义权限策略的内容，做更精细的权限控制，配置步骤比系统权限策略更复杂。

## 系统权限策略

1. 使用阿里云账号（主账号）或RAM管理员登录[RAM控制台](https://ram.console.aliyun.com/)。
2. 为RAM用户授予以下列表权限，具体操作请参见[为RAM用户授权](https://help.aliyun.com/zh/ram/user-guide/grant-permissions-to-the-ram-user#section-sjg-7hb-xph)。
  
  | **权限策略** | **描述** |
  | --- | --- |
  | [AliyunRAMReadOnlyAccess](https://ram.console.aliyun.com/policies/AliyunRAMReadOnlyAccess/System/content) | 访问控制 RAM（Resource Access Management）的只读访问权限，即查看用户、用户组以及授权信息的权限。 |
  | [AliyunFCFullAccess](https://ram.console.aliyun.com/policies/AliyunFCFullAccess/System/content) | 管理函数计算（FC）服务的权限。 |
  | [AliyunDevsFullAccess](https://ram.console.aliyun.com/policies/AliyunDevsFullAccess/System/content) | 管理Serverless开发平台（Devs）的权限。 |
  | [AliyunOSSReadOnlyAccess](https://ram.console.aliyun.com/policies/AliyunOSSReadOnlyAccess/System/content) | 只读访问对象存储服务（OSS）的权限。 |
  | [AliyunLogReadOnlyAccess](https://ram.console.aliyun.com/policies/AliyunLogReadOnlyAccess/System/content) | 只读访问日志服务（Log）的权限。 |
  | [AliyunCloudMonitorReadOnlyAccess](https://ram.console.aliyun.com/policies/AliyunCloudMonitorReadOnlyAccess/System/content) | 只读访问云监控（CloudMonitor）的权限。 |
  | [AliyunNASReadOnlyAccess](https://ram.console.aliyun.com/policies/detail?policyType=System&policyName=AliyunNASReadOnlyAccess) | 只读访问文件存储服务（NAS）的权限。 |
  | [AliyunVPCReadOnlyAccess](https://ram.console.aliyun.com/policies/detail?policyType=System&policyName=AliyunVPCReadOnlyAccess) | 只读访问专有网络（VPC）的权限。 |
  | [AliyunECSReadOnlyAccess](https://ram.console.aliyun.com/policies/detail?policyType=System&policyName=AliyunECSReadOnlyAccess) | 只读访问云服务器服务（ECS）的权限。 |

## **自定义权限策略**

1. 使用阿里云账号（主账号）或RAM管理员登录[RAM控制台](https://ram.console.aliyun.com/)。
2. 创建一个自定义权限策略，您可以授予RAM用户使用图像生成项目的**读写权限**。
  
  其中在**脚本编辑**页签，请使用以下脚本替换配置框中的原有内容。具体操作，请参见[创建自定义权限策略](https://help.aliyun.com/zh/ram/create-a-custom-policy#title-7x0-6hc-6p2)。
  
  ```
  { "Version": "1", "Statement": [ { "Action": [ "ram:Get*", "ram:List*", "ram:GenerateCredentialReport" ], "Resource": "*", "Effect": "Allow" }, { "Action": "devs:*", "Resource": "*", "Effect": "Allow" }, { "Action": "ram:PassRole", "Resource": "*", "Effect": "Allow", "Condition": { "StringEquals": { "acs:Service": "devs.aliyuncs.com" } } }, { "Action": [ "fc:Get*", "fc:List*", "fc:PutConcurrencyConfig", "fc:DeleteConcurrencyConfig", "fc:PutProvisionConfig", "fc:InstanceExec", "fc:EnableFunctionInvocation", "fc:DisableFunctionInvocation", "fc:DeleteScalingConfig", "fc:PutScalingConfig", "fc:UpdateFunction" ], "Resource": "*", "Effect": "Allow" }, { "Action": [ "log:Get*", "log:List*", "log:Query*" ], "Resource": "*", "Effect": "Allow" }, { "Action": [ "oss:Get*", "oss:List*" ], "Effect": "Allow", "Resource": "*" }, { "Action": [ "cms:Get*", "cms:List*", "cms:Query*", "cms:Describe*" ], "Resource": "*", "Effect": "Allow" }, { "Action": "vpc:DescribeVpc*", "Resource": "*", "Effect": "Allow" }, { "Action": "nas:Describe*", "Resource": "*", "Effect": "Allow" }, { "Action": "ecs:DescribeSecurityGroup*", "Resource": "*", "Effect": "Allow" } ] }
  ```
3. 为RAM用户添加上一步创建的自定义权限策略。具体操作，请参见[为RAM用户授权](https://help.aliyun.com/zh/ram/user-guide/grant-permissions-to-the-ram-user)。
