# 使用函数Context参数中的AccessKey ID等信息访问其他云资源时，收到The Access Key ID does not exist的报错怎么办？

函数Context参数中提供了访问云资源的临时密钥，包含AccessKey ID、AccessKey Secret及Security Token，如果遗漏了Security Token，会收到The Access Key ID does not exist的报错。

以下是在Python函数中访问OSS代码的示例。

```
import json import oss2 def my_handler(event, context): evt = json.loads(event) creds = context.credentials # 身份验证时，请不要遗漏了security_token！ # Do not miss the "security_token" for the authentication! auth = oss2.StsAuth(creds.access_key_id, creds.access_key_secret, creds.security_token) bucket = oss2.Bucket(auth, evt['endpoint'], evt['bucket']) bucket.put_object(evt['objectName'], evt['message']) return 'success'
```
