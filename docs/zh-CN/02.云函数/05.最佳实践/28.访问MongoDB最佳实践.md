# 访问MongoDB最佳实践

在函数计算中，不同的执行环境实例之间的状态是不共享的，通过数据库可以将结构化的数据持久化以实现状态共享。通过函数计算访问云上数据库，您可以进行数据查询和数据插入等操作。本文以Python函数为例，介绍如何同VPC或跨VPC跨地域访问云数据库 MongoDB 版。

## 前提条件

- 创建云数据库MongoDB实例，本文以分片集群实例为例。关于云数据库MongoDB实例的类型，请参见[单节点实例](https://help.aliyun.com/zh/mongodb/create-a-standalone-instance#task-hwt-zlx-p2b)、[副本集实例](https://help.aliyun.com/zh/mongodb/create-a-replica-set-instance-1#task-hwt-zlx-p2b)和[分片集群实例](https://help.aliyun.com/zh/mongodb/create-a-sharded-cluster-instance-1#task-g3q-hyq-w2b)。
- 本文中index.py示例代码中的逻辑是在数据库名为test-db和数据库集合名为fc_col中插入一条文档数据。您可以根据实际情况修改数据库名和集合名称，具体操作，请参见[创建数据库和集合并写入数据](https://help.aliyun.com/zh/mongodb/create-a-database-and-a-collection-and-write-data-1)。

## **操作步骤**

### **步骤一：设置数据库白名单**

## 场景一：访问同VPC内的MongoDB数据库

如果您选择访问同VPC内数据库的场景，请确保数据库实例与函数处于同一地域。建议您在函数计算支持的可用区创建数据库实例。更多信息，请参见[函数计算支持的可用区](https://help.aliyun.com/zh/functioncompute/fc/user-guide/configure-network-settings#section-40g-39j-s9a)。如果您的数据库实例不在函数计算支持的可用区内，可以通过在您的VPC环境中创建一个与函数计算相同可用区的vSwitch，并在函数的VPC配置中设置此vSwitch ID。由于同一VPC内不同vSwitch之间私网互通，因此函数计算可以通过该vSwitch访问在其他可用区的VPC内的资源。具体步骤，请参见[遇到vSwitch is in unsupported zone的错误怎么办？](https://help.aliyun.com/zh/functioncompute/fc/vswitch-is-in-unsupported-zone)。

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com/)，[创建Python Web函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/creating-a-web-function)，在函数详情页，选择**配置**页签，找到**高级配置**单击其右侧**编辑**，在**高级配置**面板找到**网络**区域，为函数开通VPC访问能力，并配置目标VPC资源。
  
  **
  
  **说明**
  
  请确保为函数配置的VPC与数据库实例绑定的VPC相同。
  
  具体需选择**专有网络**、**交换机**和**安全组**三项资源。建议配置两个及以上可用区的交换机，以充分利用函数计算的多可用区容灾特性。
2. 在函数详情页，选择**配置**页签，然后在**网络**区域获取函数配置中的交换机网段CIDR。
3. 将上一步获取的函数配置中交换机的网段添加到数据库访问白名单。
  
  **
  
  **重要**
  
  请使用设置IP地址白名单方式授权函数访问数据库，请勿使用安全组方式。否则，可能导致函数偶尔连接不上数据库的情况，影响业务正常运行。
  
  1. 登录[MongoDB管理控制台](https://mongodb.console.aliyun.com/)，在左侧导航栏，选择**分片集群实例列表**，单击目标实例ID。
  2. 在实例详情页，左侧导航栏，选择。
  3. 单击**default**分组右侧的**手动修改**，在**手动修改**面板，将获取的交换机IPv4网段配置在白名单中，然后单击**确定**。
    
    在**允许访问IP名单**输入框中填写获取的 IPv4 网段，使用 CIDR 格式，例如`192.168.xxx.xxx/24`。
  
  完成配置后，函数可以通过数据库内网地址访问MongoDB数据库。

## 场景二：**跨VPC或跨地域访问**MongoDB**数据库**

不同VPC和不同地域之间属于完全的逻辑隔离，常规情况下不能跨VPC和跨地域访问数据库。如果需要跨VPC或跨地域访问数据库，可以通过为函数配置固定公网IP的方式，此时系统会在函数绑定的专有网络VPC内创建公网NAT网关，通过公网网关即可实现通过公网IP访问数据库。

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com/)，在左侧导航栏，选择**函数**，选择地域，然后根据界面提示[创建函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/function-instance-1/)。
2. 在函数详情页，选择**配置**页签，找到**高级配置**单击其右侧**编辑**，在高级配置面板找到**网络**区域，将配置**固定公网 IP**开关打开，将**允许函数默认网卡访问公网**开关关闭，使配置的固定公网IP生效，然后单击**部署**。
3. 在函数详情页，选择**配置**页签，然后在**网络**区域获取函数配置的弹性公网IP地址。
4. 将上一步获取的函数固定公网IP地址添加到数据库访问白名单。
  
  **
  
  **重要**
  
  请使用设置IP地址白名单方式授权函数访问数据库，请勿使用安全组方式。否则，可能导致函数偶尔连接不上数据库的情况，影响业务正常运行。
  
  1. 登录[MongoDB管理控制台](https://mongodb.console.aliyun.com/)，在左侧导航栏，选择**分片集群实例列表**，单击目标实例ID。
  2. 在实例详情页，左侧导航栏，选择。
  3. 单击**default**分组右侧的**手动修改**，在**手动修改**面板，将获取的交换机IPv4网段配置在白名单中，然后单击**确定**。
    
    白名单IP地址支持以下格式：指定单个IP（如`192.168.0.1`）、指定IP段（如`192.168.0.0/24`），多个IP用英文逗号分隔；填写`0.0.0.0/0`表示不限制访问，存在高安全风险。
  
  完成配置后，函数可以通过数据库公网地址访问MongoDB数据库。

## **步骤二：在函数中访问MongoDB**

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com/)，在函数列表找到目标函数，在函数详情页，单击**代码**页签，在代码编辑器编写如下示例代码。
  
  ```
  from flask import Flask import os from pymongo import MongoClient app = Flask(__name__) # 全局变量用于存储 MongoDB 单例连接 _mongo_client = None # 创建数据库连接（单例模式） def getConnection(): global _mongo_client try: # 如果连接已经存在且未断开，直接返回 if _mongo_client is not None: try: # 测试连接是否有效（简单命令测试） _mongo_client.admin.command('ping') # 使用 admin 数据库的 ping 命令测试连接状态 return _mongo_client except Exception: # 如果连接断开，重置连接 _mongo_client = None # 如果连接不存在或已断开，重新创建连接 url = os.environ['MONGO_URL'] _mongo_client = MongoClient(url) return _mongo_client except Exception as e: print(f"ERROR: Failed to connect to MongoDB instance: {e}") raise @app.route('/', defaults={'path': ''}) @app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE']) def hello_world(path): dbName = os.environ['MONGO_DATABASE'] # 获取 MongoDB 连接 client = getConnection() # 操作集合，集合fc_col请根据实际情况进行修改 col = client[dbName]['fc_col'] col.insert_one(dict(DEMO="FC", MSG="Hello FunctionCompute For MongoDB")) doc = col.find_one(dict(DEMO="FC")) print('find documents:' + str(doc)) return str(doc) if __name__ == '__main__': app.run(host='0.0.0.0', port=9000)
  ```
2. 在**代码**页签，WebIDE界面，选择，打开终端窗口，执行以下命令安装pymongo库。
  
  ```
  pip install -t . pymongo
  ```
3. 在函数详情页，选择**配置**页签，找到**高级配置**单击其右侧**编辑**，在**高级配置**面板找到**环境变量**区域，配置以下环境变量，然后单击**部署**。
  
  | **环境变量名称** | **环境变量值** | **说明** |
  | --- | --- | --- |
  | MONGO_DATABASE | test-db | MongoDB数据库实例中创建的数据库名称。<br>**<br>**说明**<br>如果使用root账号，MongoDB 7.0.4及以后的版本没有admin默认数据库的写权限，建议您使用手动创建的数据库。 |
  | MONGO_URL | mongodb://root:password@s-bp132a4e334e****.mongodb.rds.aliyuncs.com:3717,s-bp1b486e9aa4****.mongodb.rds.aliyuncs.com:3717 | MongoDB数据库实例的访问地址。<br>- 如果您选择**同VPC内的MongoDB数据库**的场景，请将此环境变量值设置为数据库的内网地址。<br>- 如果您选择**跨VPC或跨地域访问MongoDB数据库**的场景，请将此环境变量值设置为数据库的外网地址。<br>登录[MongoDB管理控制台](https://mongodb.console.aliyun.com/)，单击目标实例，然后在实例详情页的左侧导航栏，选择**数据库连接**，在**数据库连接**页面获取数据库的内网地址或外网地址。 |
4. 在函数详情页，选择**代码**页签，单击**测试函数**，执行成功后查看返回结果，已成功向MongoDB数据库插入一条数据。
  
  返回结果为一条 MongoDB 文档：`{'_id': ObjectId('xxx'), 'DEMO': 'FC', 'MSG': 'Hello FunctionCompute For MongoDB'}`。

## **更多信息**

- 更多访问MongoDB数据库的示例代码，请参见[函数计算Python访问MongoDB数据库](https://github.com/devsapp/start-fc-db/tree/main/python/mongodb/src)。
- 如果您的数据库访问失败，需根据问题现象进行排查，详情请参见[数据库访问失败的常见原因](https://help.aliyun.com/zh/functioncompute/fc/how-to-troubleshoot-database-access-failures)。
- 如果您希望使用Serverless Devs命令行工具创建函数并访问RDS MySQL数据库，请参见以下步骤。
  
  **单击此处查看Serverless Devs操作步骤**
  
  1. 安装Serverless Devs和Docker，并添加密钥信息。具体操作，请参见[快速入门](https://help.aliyun.com/zh/functioncompute/fc/developer-reference/install-serverless-devs-and-docker).
  2. 创建代码目录`mycode`，准备`s.yaml`文件和代码文件`app.py`。`app.py`的示例代码请参见[步骤二：在函数中访问MongoDB](#3005a99337dt7)提供的代码，`s.yaml`文件的示例如下。
    
    以下`s.yaml`示例适用于同VPC内访问MongoDB数据库的场景，如果需要跨VPC跨地域访问数据库，请参见[场景二：跨VPC或跨地域访问MongoDB数据库](#e2ff866fd1174)。
    
    ```
    # ------------------------------------ # 官方手册: https://manual.serverless-devs.com/user-guide/aliyun/#fc3 # 常见小贴士: https://manual.serverless-devs.com/user-guide/tips/ # 有问题快来钉钉群问一下吧：33947367 # ------------------------------------ edition: 3.0.0 name: hello-world-app access: "default" vars: # 全局变量 region: "cn-hangzhou" # 如果您选择同VPC内访问RDS数据库的场景，请确保函数部署在与RDS数据库相同的地域 resources: hello_world: component: fc3 actions: pre-${regex('deploy|local')}: - component: fc3 build props: region: ${vars.region} functionName: "start-python-0t1m" runtime: custom.debian10 description: 'hello world by serverless devs' timeout: 10 memorySize: 512 cpu: 0.5 diskSize: 512 code: ./code customRuntimeConfig: port: 9000 command: - python3 - app.py internetAccess: true vpcConfig: vpcId: vpc-bp1dxqii29fpkc8pw**** # 数据库实例所在的VPC ID securityGroupId: sg-bp12ly2ie92ixrfc**** # 安全组ID vSwitchIds: - vsw-bp1ty76ijntee9z83**** # 请确保该vSwitch对应的网段已配置到数据库实例访问白名单中 environmentVariables: PYTHONPATH: /code/python PATH: /code/python/bin:/var/fc/lang/python3.10/bin:/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/bin MONGO_DATABASE: test-db # 数据库名称 MONGO_URL: mongodb://username:password@d-bp1b05cac9df0dd****.mongodb.rds.aliyuncs.com:37** # 数据库接入点,其中username和password为数据库的用户名和密码，如果用户名和密码中包含特殊字数，需按照RFC 3986标准进行转义
    ```
  3. 执行以下命令构建项目。
    
    ```
    sudo s build --use-docker
    ```
  4. 执行以下命令部署项目。
    
    ```
    sudo s deploy -y
    ```
  5. 执行以下命令调用函数。
    
    **
    
    **说明**
    
    请确保您为函数配置的交换机网段或固定公网IP地址已添加到数据库实例访问白名单中。具体操作，请参见[步骤3](#06a0ee83aamhh)。
    
    ```
    sudo s invoke -e "{}"
    ```
