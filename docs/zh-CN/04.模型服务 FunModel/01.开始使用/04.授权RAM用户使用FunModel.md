# 授权RAM用户使用FunModel

本文介绍如何授予RAM用户使用 FunModel。

## 前提条件

已[创建RAM用户](https://help.aliyun.com/zh/ram/user-guide/create-a-ram-user#task-187540)。

## 背景信息

您可以通过如下两种方式授予RAM用户使用FunModel。

- 系统权限策略：权限范围较大，用户无法修改系统权限策略的内容，但配置步骤简单。
- 自定义权限策略：用户可以为所有RAM用户添加自定义权限策略，简化RAM用户配置。也可以修改自定义权限策略的内容，实现更精细的权限控制，配置步骤比系统权限策略更复杂。

## 系统权限策略

1. 使用阿里云账号（主账号）或RAM管理员登录[RAM控制台](https://ram.console.aliyun.com/)。
2. 为RAM用户授予以下列表权限，具体操作请参见[为RAM用户授权](https://help.aliyun.com/zh/ram/user-guide/grant-permissions-to-the-ram-user#section-sjg-7hb-xph)。
  
  | **权限策略** | **描述** |
  | --- | --- |
  | [AliyunDevsFCServicesDeployPolicy](https://ram.console.aliyun.com/policies/detail?policyType=System&policyName=AliyunDevsFCServicesDeployPolicy) | FunModel部署模型服务所需策略 |
  | [AliyunFCFullAccess](https://ram.console.aliyun.com/policies/AliyunFCFullAccess/System/content) | 管理函数计算（FC）服务的权限 |
  | [AliyunDevsFullAccess](https://ram.console.aliyun.com/policies/AliyunDevsFullAccess/System/content) | 管理 FunctionAI 开发平台的权限 |
  | [AliyunOSSReadOnlyAccess](https://ram.console.aliyun.com/policies/AliyunOSSReadOnlyAccess/System/content) | 只读访问对象存储服务（OSS）的权限 |
  | [AliyunLogReadOnlyAccess](https://ram.console.aliyun.com/policies/AliyunLogReadOnlyAccess/System/content) | 只读访问日志服务（Log）的权限 |
  | [AliyunCloudMonitorReadOnlyAccess](https://ram.console.aliyun.com/policies/AliyunCloudMonitorReadOnlyAccess/System/content) | 只读访问云监控（CloudMonitor）的权限 |
  | [AliyunNASReadOnlyAccess](https://ram.console.aliyun.com/policies/detail?policyType=System&policyName=AliyunNASReadOnlyAccess) | 只读访问文件存储服务（NAS）的权限 |
  | [AliyunVPCReadOnlyAccess](https://ram.console.aliyun.com/policies/detail?policyType=System&policyName=AliyunVPCReadOnlyAccess) | 只读访问专有网络（VPC）的权限 |
  | [AliyunRAMReadOnlyAccess](https://ram.console.aliyun.com/policies/detail?policyType=System&policyName=AliyunRAMReadOnlyAccess) | 只读访问控制（RAM）的权限 |

## **自定义权限策略**

1. 使用阿里云账号（主账号）或RAM管理员登录[RAM控制台](https://ram.console.aliyun.com/)。
2. 创建一个自定义权限策略，您可以授予RAM用户使用FunModel的**读写权限**。
  
  其中在**脚本编辑**页签，请使用以下脚本替换配置框中的原有内容。具体操作，请参见[创建自定义权限策略](https://help.aliyun.com/zh/ram/create-a-custom-policy#title-7x0-6hc-6p2)。
  
  ```
  { "Version": "1", "Statement": [ { "Action": [ "ram:Get*", "ram:List*", "ram:GenerateCredentialReport" ], "Resource": "*", "Effect": "Allow" }, { "Action": "devs:*", "Resource": "*", "Effect": "Allow" }, { "Action": "ram:PassRole", "Resource": "*", "Effect": "Allow", "Condition": { "StringEquals": { "acs:Service": "devs.aliyuncs.com" } } }, { "Effect": "Allow", "Action": "fc:*", "Resource": "*" }, { "Action": "ram:PassRole", "Resource": "*", "Effect": "Allow", "Condition": { "StringEquals": { "acs:Service": "fc.aliyuncs.com" } } }, { "Action": [ "log:Get*", "log:List*", "log:Query*" ], "Resource": "*", "Effect": "Allow" }, { "Action": [ "oss:Get*", "oss:List*", "oss:PutBucket", "oss:PutBucketCors" ], "Effect": "Allow", "Resource": "*" }, { "Action": [ "cms:Get*", "cms:List*", "cms:Query*", "cms:Describe*" ], "Resource": "*", "Effect": "Allow" }, { "Action": "vpc:DescribeVpc*", "Resource": "*", "Effect": "Allow" }, { "Action": "nas:Describe*", "Resource": "*", "Effect": "Allow" }, { "Action": "ecs:DescribeSecurityGroup*", "Resource": "*", "Effect": "Allow" }, { "Effect": "Allow", "Action": [ "vpc:CreateVpc", "vpc:CreateVSwitch", "vpc:ModifyVpcAttribute", "vpc:DescribeVSwitches", "vpc:DescribeVpcs", "ecs:AuthorizeSecurityGroup", "ecs:CreateSecurityGroup", "ecs:DescribeSecurityGroups" ], "Resource": "*" }, { "Effect": "Allow", "Action": [ "vpc:DescribeVpcAttribute", "vpc:DescribeVSwitchAttributes" ], "Resource": "*" }, { "Effect": "Allow", "Action": [ "nas:CreateFileSystem", "nas:DeleteFileSystem", "nas:DescribeFileSystems", "nas:ModifyFileSystem", "nas:DeleteMountTarget", "nas:ModifyMountTarget", "nas:DescribeMountTargets" ], "Resource": "acs:nas:*:*:filesystem/*" }, { "Effect": "Allow", "Action": "nas:CreateMountTarget", "Resource": [ "acs:nas:*:*:filesystem/*", "acs:vpc:*:*:vswitch/*" ] }, { "Effect": "Allow", "Action": [ "nas:CreateAccessGroup", "nas:CreateAccessRule" ], "Resource": "*" }, { "Effect": "Allow", "Action": [ "agentrun:Get*", "agentrun:List*" ], "Resource": "*" } ] }
  ```
3. 为RAM用户添加上一步创建的自定义权限策略。具体操作，请参见[为RAM用户授权](https://help.aliyun.com/zh/ram/user-guide/grant-permissions-to-the-ram-user)。
