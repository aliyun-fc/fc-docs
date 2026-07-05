# 访问Redis最佳实践

在函数计算中，不同的执行环境实例之间的状态是不共享的，通过数据库可以将结构化的数据持久化以实现状态共享。通过函数计算访问云上数据库，您可以进行数据查询和数据插入等操作。本文以Python 3为例，介绍如何在同VPC或跨VPC跨地域访问云数据库 Tair（兼容 Redis）。

## 前提条件

[创建Redis实例](https://help.aliyun.com/zh/redis/getting-started/step-1-create-an-apsaradb-for-redis-instance#ee9914c3cd4dc)

## 操作步骤

### **步骤一：设置数据库白名单**

## 场景一：访问同VPC内的Redis数据库

**

**重要**

- 请确保您所创建的数据库实例与需要访问该数据库实例的函数在同一地域。
- 您在函数计算支持的可用区创建数据库实例。更多信息，请参见[函数计算支持的可用区](https://help.aliyun.com/zh/functioncompute/fc-2-0/user-guide/configure-network-settings#section-40g-39j-s9a)。
- 如果您的数据库实例不在函数计算支持的可用区内，可以通过在您的VPC环境中创建一个与函数计算相同可用区的vSwitch，并在函数计算的服务的VPC配置中设置此vSwitch ID。由于同一VPC内不同vSwitch之间私网互通，因此函数计算可以通过该vSwitch访问在其他可用区VPC内资源。具体步骤，请参见[遇到vSwitch is in unsupported zone的错误怎么办？](https://help.aliyun.com/zh/functioncompute/fc-2-0/how-to-handle-the-vswitch-is-in-unsupported-zone-error#concept-1918315)。

1. 登录[云数据库Tair（兼容Redis）版管理控制台](https://kvstore.console.aliyun.com/Redis/instance/cn-hangzhou)，在上方选择地域，然后单击目标实例ID，点击**实例信息，**查看Redis实例的专有网络信息。
2. 登录[函数计算控制台](https://fcnext.console.aliyun.com/)，[创建Python Web函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/creating-a-web-function)，在函数详情页，选择**配置**页签，找到**高级配置**单击其右侧**编辑**，在**高级配置**面板找到**网络**区域，为函数开通VPC访问能力，并配置目标VPC资源。
  
  **
  
  **说明**
  
  请确保为函数配置的VPC与数据库实例绑定的VPC相同。
  
  网络配置区域包含**专有网络**、**交换机**和**安全组**三个必填项，分别通过下拉框选择对应资源。建议配置两个或更多可用区的交换机，以充分利用函数计算的多可用区容灾特性。
3. 在函数详情页，选择**配置**页签，然后在**网络**区域获取函数配置中的交换机网段CIDR。
4. 将上一步获取的函数配置中交换机的网段添加到数据库访问白名单。
  
  **
  
  **重要**
  
  请使用设置IP地址白名单方式授权函数访问数据库，请勿使用安全组方式。否则，可能导致函数偶尔连接不上数据库的情况，影响业务正常运行。
  
  1. 登录[管理控制台](https://kvstore.console.aliyun.com/Redis/instance/)，在上方选择地域，然后单击目标实例ID。
  2. 在实例详情页面的左侧导航栏，选择**白名单配置**，在**白名单设置**页签，找到目标白名单分组，单击右侧**操作**列的**修改**。
  3. 在弹出的**修改白名单分组**面板中，在**组内白名单**输入框输入目标实例绑定的vSwitch的IP地址段，然后单击**确定**。
    
    在**添加方式**中选择**手动添加**。IP 地址支持填写单个 IP（如`192.168.1.1`）或 IP 段（如`192.168.1.0/24`），多个 IP 使用英文逗号隔开。

完成配置后，函数可以通过数据库内网地址访问Redis数据库。

## 场景二：跨VPC或跨地域访问Redis数据库

不同VPC和不同地域之间属于完全的逻辑隔离，常规情况下，不能跨VPC和跨地域访问数据库。如果需要跨VPC或跨地域访问数据库，可以通过为函数配置固定公网IP的方式，此时系统会在函数绑定的专有网络VPC内创建公网NAT网关，通过公网网关即可实现通过公网IP访问数据库。

1. 登录[云数据库Tair（兼容Redis）版管理控制台](https://kvstore.console.aliyun.com/Redis/instance/cn-hangzhou/r-bp1jjonywmbfazr94n/Normal/VPC/redis.shard.small.2.ce/info)，点击**实例信息，**查看Redis实例的专有网络信息。
2. 登录[函数计算控制台](https://fcnext.console.aliyun.com/)，[创建Python Web函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/creating-a-web-function)，在函数详情页，选择**配置**页签，找到**高级配置**单击其右侧**编辑**，在**高级配置**面板找到**网络**区域，将配置**固定公网 IP**开关打开，将**允许函数默认网卡访问公网**开关关闭，使配置的固定公网IP生效，然后单击**部署**。
  
  **
  
  **说明**
  
  将参数**允许函数默认网卡访问公网**设置为**否**后使得固定公网IP生效。函数计算会禁用默认网卡，从而强制使流量通过 VPC 绑定的网卡访问外网。
3. 在函数详情页，选择**配置**页签，然后在**网络**区域获取函数配置的弹性公网IP地址。
4. 将上一步获取的函数固定公网IP地址添加到数据库访问白名单。
  
  **
  
  **重要**
  
  请使用设置IP地址白名单方式授权函数访问数据库，请勿使用安全组方式。否则，可能导致函数偶尔连接不上数据库的情况，影响业务正常运行。
  
  1. 登录[管理控制台](https://kvstore.console.aliyun.com/Redis/instance/)，在上方选择地域，然后单击目标实例ID。
  2. 在实例详情页面的左侧导航栏，选择**白名单设置**，在**白名单设置**页签，找到目标白名单分组，单击右侧**操作**列的**修改**。
  3. 在弹出的**修改白名单分组**面板中，在**组内白名单**对话框中，将获取的固定公网IP地址配置在白名单中，然后单击**确定**。
    
    弹窗顶部提示：只有已添加至白名单中的IP地址才可以访问本实例；`127.0.0.1`表示禁止访问，`0.0.0.0/0`表示允许任意地址访问；支持IP地址和IP段格式，多个IP地址间用英文逗号隔开。**添加方式**选择**手动添加**。

完成配置后，函数可以通过数据库公网地址访问Redis数据库。

### **步骤二：在函数中访问Redis**

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com/)，在函数列表找到目标函数，在函数详情页，单击**代码**页签，在代码编辑器编写如下示例代码。
  
  ```
  from flask import Flask,jsonify import os import redis app = Flask(__name__) # 全局变量用于存储 Redis 单例连接 _redis_connection = None # 创建数据库连接（单例模式） def getConnection(): global _redis_connection try: # 如果连接已经存在且未断开，直接返回 if _redis_connection is not None: try: # 测试连接是否有效（简单命令 ping） if _redis_connection.ping(): return _redis_connection except redis.ConnectionError: # 如果连接断开，重置连接 _redis_connection = None # 如果连接不存在或已断开，重新创建连接 _redis_connection = redis.Redis( host=os.environ['REDIS_HOST'], password=os.environ['REDIS_PASSWORD'], port=os.environ['REDIS_PORT'], db=1, decode_responses=True ) # 测试新连接是否成功 if not _redis_connection.ping(): raise Exception("Redis connection failed after creation.") return _redis_connection except Exception as e: print(f"Failed to initialize Redis connection: {e}") raise @app.route('/', defaults={'path': ''}) @app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE']) def hello_world(path): try: r = getConnection() counter = r.get('counter') if counter is None: counter = 0 else: counter = int(counter) print('counter: ' + str(counter)) r.set('counter', str(counter + 1)) return str(counter) except Exception as e: print(f"An error occurred: {e}") return jsonify({"error": str(e)}), 500 if __name__ == '__main__': app.run(host='0.0.0.0',port=9000)
  ```
2. 在函数详情页，选择**配置**页签，找到**高级配置**单击其右侧**编辑**，在**高级配置**面板找到**环境变量**区域，配置以下环境变量，然后单击**部署**。
  
  | **环境变量名称** | **环境变量值** | **说明** |
  | --- | --- | --- |
  | REDIS_HOST | r-bp*****.redis.rds.aliyuncs.com | 数据库实例的访问地址，如果您选择**同VPC内的Redis数据库**的场景，请将此环境变量值设置为数据库的专有网络地址。如果您选择**跨VPC或跨地域访问Redis数据库**的场景，请将此环境变量值设置为数据库的公网访问地址。<br>访问[实例列表](https://kvstore.console.aliyun.com/Redis/instance/cn-hangzhou)，在上方选择地域，然后单击目标实例ID。在左侧导航栏单击**实例信息**，在**连接信息**区域获取连接数据库的连接地址信息。<br>连接类型为**直连**，端口号为`6379`。 |
  | REDIS_PASSWORD | ***** | 数据库密码。 |
  | REDIS_PORT | 6379 | 数据库端口号 |
3. 在Redis数据库设置初始值，在函数详情页，选择**代码**页签，单击**测试函数**，执行成功后查看返回结果。
  
  在DMS控制台的SQLConsole中输入并执行命令`set counter 30`，为键`counter`（string 类型）设置初始值`30`。
  
  在**日志输出**页签中，可以看到输出`counter: 30`，表示函数已成功访问 Redis 并读取到 counter 值。

## **更多信息**

- 更多访问云数据库 Tair（兼容 Redis）的示例，请参见[函数计算Python访问云数据库 Tair（兼容 Redis）](https://github.com/devsapp/start-fc-db/tree/main/python/redis/src)。
- 更多关于访问云数据库 Tair（兼容 Redis）的异常案例，请参见[常见报错](https://help.aliyun.com/zh/redis/support/common-errors-and-troubleshooting)。
- 如果您遇到的异常问题还未解决，需要根据问题现象进行排查，详情请参见[数据库访问失败的常见原因](https://help.aliyun.com/zh/functioncompute/fc/how-to-troubleshoot-database-access-failures)。
- 如果您希望使用Serverless Devs命令行工具创建函数并访问云数据库 Tair（兼容 Redis）的数据库，请参见以下步骤。
  
  **单击此处查看Serverless Devs操作步骤**
  
  1. 安装Serverless Devs和Docker，并添加密钥信息。具体操作，请参见[快速入门](https://help.aliyun.com/zh/functioncompute/fc/developer-reference/install-serverless-devs-and-docker)。
  2. 创建代码目录`mycode`，准备`s.yaml`文件和代码文件`app.py`。`app.py`的示例代码请参见[步骤二：在函数中访问Redis](#3217282e25z30)提供的示例代码，`s.yaml`文件示例如下。
    
    以下`s.yaml`示例适用于同VPC内访问Redis数据库的场景，如果需要跨VPC跨地域访问数据库，请参见[场景二：跨VPC或跨地域访问Redis数据库](#a7856d0c7cqjn)。
    
    ```
    # ------------------------------------ # 官方手册: https://manual.serverless-devs.com/user-guide/aliyun/#fc3 # 常见小贴士: https://manual.serverless-devs.com/user-guide/tips/ # 有问题快来钉钉群问一下吧：33947367 # ------------------------------------ edition: 3.0.0 name: hello-world-app access: "default" vars: # 全局变量 region: "cn-hangzhou" # 如果您选择同VPC内访问RDS数据库的场景，请确保函数部署在与RDS数据库相同的地域 resources: hello_world: component: fc3 actions: pre-${regex('deploy|local')}: - component: fc3 build props: region: ${vars.region} functionName: "start-python-redis" runtime: custom.debian10 description: 'hello world by serverless devs' timeout: 10 memorySize: 512 cpu: 0.5 diskSize: 512 code: ./code customRuntimeConfig: port: 9000 command: - python3 - app.py internetAccess: true vpcConfig: vpcId: vpc-bp1dxqii29fpkc8pw**** # 数据库实例所在的VPC ID securityGroupId: sg-bp12ly2ie92ixrfc**** # 安全组ID vSwitchIds: - vsw-bp1ty76ijntee9z83**** # 请确保该vSwitch对应的网段已配置到数据库实例访问白名单中 environmentVariables: PYTHONPATH: /code/python PATH: /code/python/bin:/var/fc/lang/python3.10/bin:/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/bin REDIS_HOST: r-bp*****.redis.rds.aliyuncs.com # 数据库接入点 REDIS_PASSWORD: ***** #数据库密码 REDIS_PORT: "6379" #数据库端口
    ```
    
    代码的目录层级如下。
    
    ```
    ├── code │ ├── app.py │ └── requirements.txt └── s.yaml
    ```
    
    requirements.txt文件指定的依赖如下所示。
    
    ```
    flask==2.2.5
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
    
    请确保您为函数配置的交换机网段已添加到数据库实例访问白名单中。具体操作请参见[步骤4](#2f157145455h9)。
    
    ```
    sudo s invoke -e "{}"
    ```
