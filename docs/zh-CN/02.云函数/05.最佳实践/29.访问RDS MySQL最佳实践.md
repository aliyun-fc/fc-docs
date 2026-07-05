# 访问RDS MySQL最佳实践

在函数计算中，不同的执行环境实例之间的状态是不共享的，通过数据库可以将结构化的数据持久化以实现状态共享。通过函数计算访问云上数据库，您可以进行数据查询和数据插入等操作。本文以Python函数为例，介绍如何同VPC或跨VPC跨地域访问云数据库 RDS MySQL 版。

## 前提条件

- [快捷创建RDS MySQL实例](https://help.aliyun.com/zh/rds/apsaradb-rds-for-mysql/step-1-create-an-apsaradb-rds-for-mysql-instance-and-configure-databases#section-z7d-gwc-42p)。
- [创建数据库和账号](https://help.aliyun.com/zh/rds/apsaradb-rds-for-mysql/step-1-create-an-apsaradb-rds-for-mysql-instance-and-configure-databases#c8c8beda5dwet)。
- 本文中index.py示例代码中的逻辑是查询名为users的数据库表中的所有数据，您可以根据实际情况修改表名，并确保表内至少有一条数据。

## **操作步骤**

### **步骤一：设置数据库白名单**

## 场景一：访问同VPC内的RDS数据库

如果您选择访问同VPC内数据库的场景，请确保数据库实例与函数处于同一地域。建议您在函数计算支持的可用区创建数据库实例。更多信息，请参见[函数计算支持的可用区](https://help.aliyun.com/zh/functioncompute/fc/user-guide/configure-network-settings#section-40g-39j-s9a)。如果您的数据库实例不在函数计算支持的可用区内，可以通过在您的VPC环境中创建一个与函数计算相同可用区的vSwitch，并在函数的VPC配置中设置此vSwitch ID。由于同一VPC内不同vSwitch之间私网互通，因此函数计算可以通过该vSwitch访问在其他可用区的VPC内的资源。具体步骤，请参见[遇到vSwitch is in unsupported zone的错误怎么办？](https://help.aliyun.com/zh/functioncompute/fc/vswitch-is-in-unsupported-zone)。

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com/)，[创建Python Web函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/creating-a-web-function)，在函数详情页，选择**配置**页签，找到**高级配置**单击其右侧**编辑**，在**高级配置**面板找到**网络**区域，为函数开通VPC访问能力，并配置目标VPC资源。
  
  **
  
  **说明**
  
  请确保为函数配置的VPC与数据库实例绑定的VPC相同。
  
  配置项包括**专有网络**、**交换机**和**安全组**。建议部署两个或更多可用区的交换机，以充分利用函数计算服务的多可用区容灾特性，增强业务系统的高可用性。当前地域支持的可用区为 cn-hangzhou-h/i/j/k/f/g/b。
2. 在函数详情页，选择**配置**页签，然后在**网络**区域获取函数配置中的交换机网段CIDR。
3. 将上一步获取的函数配置中交换机的网段添加到数据库访问白名单。
  
  **
  
  **重要**
  
  请使用设置IP地址白名单方式授权函数访问数据库，请勿使用安全组方式。否则，可能导致函数偶尔连接不上数据库的情况，影响业务正常运行。
  
  1. 访问[RDS实例列表](https://rdsnext.console.aliyun.com/rdsList/basic)，在上方选择地域，然后单击目标实例ID。
  2. 在左侧导航栏，单击**白名单与安全组**。
    
    在**白名单设置**页面，可查看当前的IP白名单模式。
    
    **
    
    **说明**
    
    较早创建的实例可能采用高安全模式。新创建的实例都采用通用白名单模式。
  3. 单击**default**分组右侧的**修改**，在弹出的**修改白名单分组**对话框中，将[步骤2](#fef09cc58fxw7)获取的交换机IPv4网段配置在白名单中，然后单击**确定**。
  
  完成配置后，函数可以通过数据库内网地址访问RDS数据库。

## 场景二：**跨VPC或跨地域访问RDS数据库**

不同VPC和不同地域之间属于完全的逻辑隔离，常规情况下不能跨VPC和跨地域访问数据库。如果需要跨VPC或跨地域访问数据库，可以通过为函数配置固定公网IP的方式，此时系统会在函数绑定的专有网络VPC内创建公网NAT网关，通过公网网关即可实现通过公网IP访问数据库。

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com/)，在左侧导航栏，选择**函数**，选择地域，然后根据界面提示[创建函数](https://help.aliyun.com/zh/functioncompute/fc/user-guide/function-instance-1/)。
2. 在函数详情页，选择**配置**页签，找到**高级配置**单击其右侧**编辑**，在**高级配置**面板找到**网络**区域，将配置**固定公网 IP**开关打开，将**允许函数默认网卡访问公网**开关关闭，使配置的固定公网IP生效，然后单击**部署**。
3. 在函数详情页，选择**配置**页签，然后在**网络**区域获取函数配置的弹性公网IP地址。
4. 将上一步获取的函数固定公网IP地址添加到数据库访问白名单。
  
  **
  
  **重要**
  
  请使用设置IP地址白名单方式授权函数访问数据库，请勿使用安全组方式。否则，可能导致函数偶尔连接不上数据库的情况，影响业务正常运行。
  
  1. 访问[RDS实例列表](https://rdsnext.console.aliyun.com/rdsList/basic)，在上方选择地域，然后单击目标实例ID。
  2. 在左侧导航栏，单击**白名单与安全组**。
    
    在**白名单设置**页面，可查看当前的IP白名单模式。
    
    **
    
    **说明**
    
    较早创建的实例可能采用高安全模式。新创建的实例都采用通用白名单模式。
  3. 单击**default**分组右侧的**修改**，在弹出的**修改白名单分组**对话框中，将[步骤2](#fef09cc58fxw7)获取的交换机IPv4网段配置在白名单中，然后单击**确定**。
    
    白名单支持指定 IP 地址（如`192.168.0.1`）和 IP 段（如`192.168.0.0/24`），多个 IP 用英文逗号隔开。注意：白名单设置为`0.0.0.0/0`表示对公网开放，设置为`127.0.0.1`表示禁止所有地址访问；新白名单将于 1 分钟后生效。
  
  完成配置后，函数可以通过数据库公网地址访问RDS数据库。

### **步骤二：在函数中访问RDS**

1. 登录[函数计算控制台](https://fcnext.console.aliyun.com/)，在函数列表找到目标函数，在函数详情页，单击**代码**页签，在代码编辑器编写如下示例代码。
  
  ```
  from flask import Flask, jsonify import pymysql import os from datetime import datetime import logging app = Flask(__name__) # 全局变量用于存储 MySQL 单例连接 _mysql_connection = None # 创建数据库连接（单例模式） def getConnection(): global _mysql_connection try: # 如果连接已经存在且未断开，直接返回 if _mysql_connection is not None: try: # 测试连接是否有效（简单命令测试） with _mysql_connection.cursor() as cursor: cursor.execute("SELECT 1") # 简单查询测试连接状态 result = cursor.fetchone() if result and result[0] == 1: return _mysql_connection except pymysql.OperationalError: # 如果连接断开，重置连接 _mysql_connection = None # 如果连接不存在或已断开，重新创建连接 _mysql_connection = pymysql.connect( host=os.environ['MYSQL_HOST'], port=int(os.environ['MYSQL_PORT']), user=os.environ['MYSQL_USER'], password=os.environ['MYSQL_PASSWORD'], db=os.environ['MYSQL_DBNAME'] ) return _mysql_connection except Exception as e: logging.error(f"Error occurred during database connection: {e}") raise @app.route('/', defaults={'path': ''}) @app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE']) def hello_world(path): conn = getConnection() try: with conn.cursor() as cursor: # 查询 users 表的所有记录,users 表需要根据实际表名进行修改 sql = "SELECT * FROM users" cursor.execute(sql) result = cursor.fetchall() columns = [desc[0] for desc in cursor.description] # 获取字段名列表 # 将查询结果转换为字典列表 users = [] for row in result: user = {} for idx, column_name in enumerate(columns): value = row[idx] if isinstance(value, datetime): # 处理日期类型字段 user[column_name] = value.strftime('%Y-%m-%d %H:%M:%S') else: user[column_name] = value users.append(user) if users: # 返回所有用户的 JSON 响应 return jsonify(users), 200 else: # 如果没有找到用户，返回 404 错误 return jsonify({'error': 'No users found'}), 404 except Exception as e: logging.error(f"Error occurred during database operation: {e}") return jsonify({'error': 'Database error'}), 500 if __name__ == '__main__': app.run(host='0.0.0.0', port=9000)
  ```
2. 在函数详情页，选择**配置**页签，找到**高级配置**单击其右侧**编辑**，在**高级配置**面板找到**环境变量**区域，配置以下环境变量，然后单击**部署**。
  
  | **环境变量名称** | **环境变量值** | **说明** |
  | --- | --- | --- |
  | MYSQL_HOST | rm-bp19u8e76ae****.mysql.rds.aliyuncs.com | 数据库实例的访问地址。<br>- 如果您选择**同VPC内的RDS数据库**的场景，请将此环境变量值设置为数据库的内网地址。<br>- 如果您选择**跨VPC或跨地域访问RDS数据库**的场景，请将此环境变量值设置为数据库的外网地址。<br>在[RDS实例列表](https://rdsnext.console.aliyun.com/rdsList/basic)，单击目标RDS实例ID，然后在左侧导航栏，选择**数据库连接**，在**数据库连接**页面获取数据库的内网地址或外网地址。 |
  | MYSQL_DBNAME | db_test | RDS实例中创建的数据库名称。 |
  | MYSQL_PASSWORD | ***** | 数据库密码。 |
  | MYSQL_PORT | 3306 | 数据库实例的私网端口。 |
  | MYSQL_USER | dms_user_**** | RDS实例中创建的账号名称。 |
3. 在函数详情页，选择**代码**页签，单击**测试函数**，执行成功后查看返回结果，已成功完成查询表格操作。
  
  返回的 JSON 数据包含用户记录，字段包括`id`、`username`、`email`、`password_hash`、`created_at`和`updated_at`。

## 更多信息

- 更多访问RDS MySQL数据库的示例，请参见[函数计算Python访问MySQL数据库](https://github.com/devsapp/start-fc-db/tree/main/python/mysql/src)。
- 如果您的数据库访问失败，需要根据问题现象进行排查，详情请参见[数据库访问失败的常见原因](https://help.aliyun.com/zh/functioncompute/fc/how-to-troubleshoot-database-access-failures)。
- RDS支持MySQL、SQL Server、PostgreSQL和MariaDB引擎。更多信息，请参见[云数据库RDS简介](https://help.aliyun.com/zh/rds/product-overview/what-is-apsaradb-rds-what-is-apsaradb-rds#concept-pc2-lv5-tdb)。
- 如果您希望使用Serverless Devs命令行工具创建函数并访问RDS MySQL数据库，请参见以下步骤。
  
  **单击此处查看Serverless Devs操作步骤**
  
  1. 安装Serverless Devs和Docker，并添加密钥信息。具体操作，请参见[快速入门](https://help.aliyun.com/zh/functioncompute/fc/developer-reference/install-serverless-devs-and-docker)。
  2. 创建代码目录`mycode`，准备`s.yaml`文件和代码文件`app.py`。`s.yaml`文件示例如下，示例代码请参见[步骤二：在函数中访问RDS](#795db778c0la9)提供的示例代码。
    
    以下`s.yaml`示例适用于同VPC内访问RDS数据库的场景，如果需要跨VPC跨地域访问数据库，请参见[场景二：跨VPC或跨地域访问RDS数据库](#e2ff866fd1174)。
    
    ```
    # ------------------------------------ # 官方手册: https://manual.serverless-devs.com/user-guide/aliyun/#fc3 # 常见小贴士: https://manual.serverless-devs.com/user-guide/tips/ # 有问题快来钉钉群问一下吧：33947367 # ------------------------------------ edition: 3.0.0 name: hello-world-app access: "default" vars: # 全局变量 region: "cn-hangzhou" # 如果您选择同VPC内访问RDS数据库的场景，请确保函数部署在与RDS数据库相同的地域 resources: hello_world: component: fc3 actions: pre-${regex('deploy|local')}: - component: fc3 build props: region: ${vars.region} functionName: "start-python-0t1m" runtime: custom.debian10 description: 'hello world by serverless devs' timeout: 10 memorySize: 512 cpu: 0.5 diskSize: 512 code: ./code customRuntimeConfig: port: 9000 command: - python3 - app.py internetAccess: true vpcConfig: vpcId: vpc-bp1dxqii29fpkc8pw**** # 数据库实例所在的VPC ID securityGroupId: sg-bp12ly2ie92ixrfc**** # 安全组ID vSwitchIds: - vsw-bp1ty76ijntee9z83**** # 请确保该vSwitch对应的网段已配置到数据库实例访问白名单中 environmentVariables: PYTHONPATH: /code/python PATH: /code/python/bin:/var/fc/lang/python3.10/bin:/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/bin MYSQL_HOST: rm-bp1j1y7657640z5****.mysql.rds.aliyuncs.com # 数据库实例的私网地址 MYSQL_PORT: "3306" # 数据库实例的私网端口 MYSQL_USER: dms_user_**** # 数据库实例中创建的数据库 MYSQL_PASSWORD: **** # 数据库实例的密码 MYSQL_DBNAME: db_test # 数据库实例中创建的数据库名称
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
