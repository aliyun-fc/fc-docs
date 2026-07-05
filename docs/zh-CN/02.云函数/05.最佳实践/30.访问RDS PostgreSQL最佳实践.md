# 访问RDS PostgreSQL最佳实践

在函数计算中，不同的执行环境实例之间的状态是不共享的，通过数据库可以将结构化的数据持久化以实现状态共享。通过函数计算访问云上数据库，您可以进行数据查询和数据插入等操作。本文以Python 3为例，介绍如何在同VPC或跨VPC跨地域访问云数据库 RDS PostgreSQL 版。

## 前提条件

- [快速创建RDS PostgreSQL实例](https://help.aliyun.com/zh/rds/apsaradb-rds-for-postgresql/create-an-apsaradb-rds-for-postgresql-instance#concept-kzn-qcg-wdb)
- 本文中index.py示例代码中的逻辑是查询名为users的数据库表中的所有数据，您可以根据实际情况修改表名，并确保表内至少有一条数据。

## 操作步骤

### **步骤一：设置数据库白名单**

## 场景一：访问同VPC内的PostgreSQL数据库

**

**重要**

- 请确保您所创建的数据库实例与需要访问该数据库实例的函数在同一地域。
- 您在函数计算支持的可用区创建数据库实例。更多信息，请参见[函数计算支持的可用区](https://help.aliyun.com/zh/functioncompute/fc-2-0/user-guide/configure-network-settings#section-40g-39j-s9a)。
- 如果您的数据库实例不在函数计算支持的可用区内，可以通过在您的VPC环境中创建一个与函数计算相同可用区的vSwitch，并在函数计算的服务的VPC配置中设置此vSwitch ID。由于同一VPC内不同vSwitch之间私网互通，因此函数计算可以通过该vSwitch访问在其他可用区VPC内资源。具体步骤，请参见[遇到vSwitch is in unsupported zone的错误怎么办？](https://help.aliyun.com/zh/functioncompute/fc-2-0/how-to-handle-the-vswitch-is-in-unsupported-zone-error#concept-1918315)。

1. 访问[RDS实例列表](https://rdsnext.console.aliyun.com/rdsList/basic?spm=a2c4g.11186623.0.0.57305849PCh9wF)，在上方选择地域，然后单击目标实例ID，单击**基本信息**，单击**专有网络**后的**查看连接详情**，查看PostgreSQL的专有网络信息。
2. 登录[函数计算控制台](https://fcnext.console.aliyun.com/)，[创建Python Web函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/creating-a-web-function)，在函数详情页，选择**配置**页签，找到**高级配置**单击其右侧**编辑**，在**高级配置**面板找到**网络**区域，为函数开通VPC访问能力，并配置目标VPC资源。
  
  **
  
  **说明**
  
  请确保为函数配置的VPC与数据库实例绑定的VPC相同。
  
  具体需配置**专有网络**、**交换机**和**安全组**三项。建议配置两个或更多可用区的交换机，以利用函数计算的多可用区容灾特性提升高可用性。跨可用区 VPC 交换机访问可能带来 1~2ms 延迟。
3. 在函数详情页，选择**配置**页签，然后在**网络**区域获取函数配置中的交换机网段CIDR。
4. 将上一步获取的函数配置中交换机的网段添加到访问白名单。
  
  **
  
  **重要**
  
  请使用设置IP地址白名单方式授权函数访问数据库，请勿使用安全组方式。否则，可能导致函数偶尔连接不上数据库的情况，影响业务正常运行。
  
  1. 登录[RDS管理控制台](https://rdsnext.console.aliyun.com/rdsList/cn-hangzhou)，在上方选择地域，然后单击目标实例ID。
  2. 在左侧导航栏，选择**白名单与安全组**，在**白名单设置**页签，找到目标白名单模板名称，单击右侧**修改**。
  3. 在弹出的**修改白名单分组**面板中，在**组内白名单：**输入框输入目标实例绑定的vSwitch的IP地址段，然后单击**确定**。

完成配置后，函数可以通过数据库内网地址访问PostgreSQL数据库。

## 场景二：跨VPC或跨地域访问PostgreSQL数据库

不同VPC和不同地域之间属于完全的逻辑隔离，常规情况下，不能跨VPC和跨地域访问数据库。如果需要跨VPC或跨地域访问数据库，可以通过为函数配置固定公网IP的方式，此时系统会在函数绑定的专有网络VPC内创建公网NAT网关，通过公网网关即可实现通过公网IP访问数据库。

1. 访问[RDS实例列表](https://rdsnext.console.aliyun.com/rdsList/basic?spm=a2c4g.11186623.0.0.57305849PCh9wF)，在上方选择地域，然后单击目标实例ID，单击**基本信息**，单击**专有网络**后的**查看连接详情**，查看PostgreSQL的专有网络信息。
2. 登录[函数计算控制台](https://fcnext.console.aliyun.com/)，[创建Python Web函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/creating-a-web-function)，选择**配置**页签，找到**高级配置**单击其右侧**编辑**，在**高级配置**面板找到**网络**区域，将配置**固定公网 IP**开关打开，将**允许函数默认网卡访问公网**开关关闭，使配置的固定公网IP生效，然后单击**部署**。
3. 在函数详情页，选择**配置**页签，然后在**网络**区域获取函数配置的弹性公网IP地址。
4. 将上一步获取的函数固定公网IP地址添加到访问白名单。
  
  **
  
  **重要**
  
  请使用设置IP地址白名单方式授权函数访问数据库，请勿使用安全组方式。否则，可能导致函数偶尔连接不上数据库的情况，影响业务正常运行。
  
  1. 登录[RDS管理控制台](https://rdsnext.console.aliyun.com/rdsList/cn-hangzhou)，在上方选择地域，然后单击目标实例ID。
  2. 在左侧导航栏，选择**白名单与安全组**，在**白名单设置**页签，找到目标白名单模板名称，单击右侧的**修改**。
  3. 在弹出的**修改白名单分组**面板中，在**组内白名单：**输入框输入要绑定的固定公网IP地址，然后单击**确定**。

完成配置后，函数可以通过数据库公网地址访问PostgreSQL数据库。

### **步骤二：在函数中访问**PostgreSQL数据库

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com/)，在函数列表找到目标函数，在函数详情页，单击**代码**页签，在代码编辑器根据数据库表编写如下示例代码。
  
  ```
  from flask import Flask, jsonify import psycopg2 # 需先安装psycopg2库 import os import sys from datetime import datetime import logging app = Flask(__name__) # 全局变量用于存储 PostgreSQL 单例连接 _postgresql_connection = None # 创建数据库连接（单例模式） def getConnection(): global _postgresql_connection try: # 如果连接已经存在且未断开，直接返回 if _postgresql_connection is not None: try: # 测试连接是否有效（简单命令测试） with _postgresql_connection.cursor() as cursor: cursor.execute("SELECT 1") # 简单查询测试连接状态 result = cursor.fetchone() if result and result[0] == 1: return _postgresql_connection except psycopg2.OperationalError: # 如果连接断开，重置连接 _postgresql_connection = None # 如果连接不存在或已断开，重新创建连接 _postgresql_connection = psycopg2.connect( database=os.environ['DATABASE'], user=os.environ['USER'], password=os.environ['PASSWORD'], host=os.environ['HOST'], port=os.environ['PORT'], ) return _postgresql_connection except Exception as e: print(f"ERROR: Unexpected error: Could not connect to PostgreSQL instance: {e}") raise @app.route('/', defaults={'path': ''}) @app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE']) def hello_world(path): conn = getConnection() try: with conn.cursor() as cursor: # 查询 users 表的所有记录,users 表需要根据实际表名进行修改 sql = "SELECT * FROM users" cursor.execute(sql) result = cursor.fetchall() columns = [desc[0] for desc in cursor.description] # 获取字段名列表 # 将查询结果转换为字典列表 users = [] for row in result: user = {} for idx, column_name in enumerate(columns): value = row[idx] if isinstance(value, datetime): # 处理日期类型字段 user[column_name] = value.strftime('%Y-%m-%d %H:%M:%S') else: user[column_name] = value users.append(user) if users: # 返回所有用户的 JSON 响应 return jsonify(users), 200 else: # 如果没有找到用户，返回 404 错误 return jsonify({'error': 'No users found'}), 404 except Exception as e: logging.error(f"Error occurred during database operation: {e}") return jsonify({'error': 'Database error'}), 500 if __name__ == '__main__': app.run(host='0.0.0.0', port=9000)
  ```
2. 为函数安装所需依赖：`pip3 install -t . psycopg2`，点击**部署代码**使依赖生效。详细步骤请参见[通过控制台Web IDE终端安装依赖](https://help.aliyun.com/zh/functioncompute/fc/user-guide/install-third-party-dependencies-for-a-function#p-z8m-m8n-zak)。
3. 在**函数详情**页签，找到**高级配置**单击其右侧**编辑****，**在高级配置面板找到**环境变量**区域，配置以下环境变量，然后单击**部署**。
  
  | **环境变量名称** | **环境变量值** | **说明** |
  | --- | --- | --- |
  | HOST | pgm-*****q.pg.rds.aliyuncs.com | 数据库实例的访问地址，如果您选择**同VPC内的PostgreSQL数据库**的场景，请将此环境变量值设置为数据库的内网地址。如果您选择**跨VPC或跨地域访问PostgreSQL数据库**的场景，请将此环境变量值设置为数据库的外网地址。<br>访问[实例列表](https://rdsnext.console.aliyun.com/rdsList/cn-hangzhou)，在上方选择地域，然后单击目标实例ID。在左侧导航栏单击**数据库连接**，在**数据库连接**信息区域获取连接数据库的连接地址信息。 |
  | PORT | 5432 | 数据库内网端口号 |
  | USER | ***** | PostgreSQL实例中创建的账号名称。 |
  | PASSWORD | ***** | 数据库密码 |
  | DATABASE | ***** | 实例中创建的数据库名称。 |
4. 在函数详情页，选择代码页签，单击测试函数，执行成功后查看返回结果。
  
  返回结果为一个JSON数组，包含一条数据库记录：`{"age": 25, "create_date": "2025-04-17 14:08:46", "id": 1, "name": "Alice"}`，表明函数已成功访问PostgreSQL数据库并读取到数据。

## 更多信息

- 更多访问RDS PostgreSQL数据库的示例，请参见[函数计算Python访问PostgreSQL数据库](https://github.com/devsapp/start-fc-db/tree/main/python/postgresql/src)。
- 关于如何查看函数计算配置的交换机信息以及如何在RDS MySQL数据库放行函数计算的交换机网段，请分别参见[配置网络](https://help.aliyun.com/zh/functioncompute/fc/user-guide/configure-network-settings)和[PostgreSQL设置白名单](https://help.aliyun.com/zh/rds/apsaradb-rds-for-postgresql/configure-an-ip-address-whitelist-for-an-apsaradb-rds-for-postgresql-instance#concept-sfx-kdg-wdb)。
- 如果数据库访问失败，需根据问题现象进行排查，详情请参见[数据库访问失败的常见原因](https://help.aliyun.com/zh/functioncompute/fc/how-to-troubleshoot-database-access-failures)。
- 如果您希望使用Serverless Devs命令行工具创建函数并访问云数据库 RDS PostgreSQL 版的数据库，请参见以下步骤。
  
  **单击此处查看Serverless Devs操作步骤**
  
  1. 安装Serverless Devs和Docker，并添加密钥信息。具体操作，请参见[快速入门](https://help.aliyun.com/zh/functioncompute/fc/developer-reference/install-serverless-devs-and-docker)。
  2. 创建代码目录`mycode`，准备`s.yaml`文件和代码文件`app.py`。`app.py`的示例代码请参见[步骤二：在函数中访问PostgreSQL数据库](#3217282e25z30)提供的示例代码，`s.yaml`文件示例如下。
    
    以下`s.yaml`示例适用于同VPC内访问SQL Server数据库的场景，如果需要跨VPC跨地域访问数据库，请参见[场景二：跨VPC或跨地域访问PostgreSQL数据库](#537de3b43axeu)。
    
    ```
    # ------------------------------------ # 官方手册: https://manual.serverless-devs.com/user-guide/aliyun/#fc3 # 常见小贴士: https://manual.serverless-devs.com/user-guide/tips/ # 有问题快来钉钉群问一下吧：33947367 # ------------------------------------ edition: 3.0.0 name: hello-world-app access: "default" vars: # 全局变量 region: "cn-hangzhou" # 如果您选择同VPC内访问RDS数据库的场景，请确保函数部署在与RDS数据库相同的地域 resources: hello_world: component: fc3 actions: pre-${regex('deploy|local')}: - component: fc3 build props: region: ${vars.region} functionName: "start-python-PostgreSQL" runtime: custom.debian10 description: 'hello world by serverless devs' timeout: 10 memorySize: 512 cpu: 0.5 diskSize: 512 code: ./code customRuntimeConfig: port: 9000 command: - python3 - app.py internetAccess: true vpcConfig: vpcId: vpc-bp1dxqii29fpkc8pw**** # 数据库实例所在的VPC ID securityGroupId: sg-bp12ly2ie92ixrfc**** # 安全组ID vSwitchIds: - vsw-bp1ty76ijntee9z83**** # 请确保该vSwitch对应的网段已配置到数据库实例访问白名单中 environmentVariables: PYTHONPATH: /code/python PATH: /code/python/bin:/var/fc/lang/python3.10/bin:/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/bin HOST: rm-*****.sqlserver.rds.aliyuncs.com # 数据库接入点 USER: ****** #实例中创建的账号名称 PASSWORD: ***** #数据库密码 DATABASE: ***** #实例中创建的数据库名称。 PORT: "5432" #数据库端口
    ```
    
    代码的目录层级如下。
    
    ```
    ├── code │ ├── app.py │ └── requirements.txt └── s.yaml
    ```
    
    requirements.txt文件指定的依赖如下所示。
    
    ```
    flask==2.2.5 psycopg2==2.9.10
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
    
    请确保您为函数配置的交换机网段已添加到数据库实例访问白名单中。具体操作请参见[步骤4](#95b44e8f6407i)。
    
    ```
    sudo s invoke -e "{}"
    ```
