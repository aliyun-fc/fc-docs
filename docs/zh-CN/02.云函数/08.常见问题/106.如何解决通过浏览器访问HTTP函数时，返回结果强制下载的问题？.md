# 如何解决通过浏览器访问HTTP函数时，返回结果强制下载的问题？

自2018年11月19日起，新创建的HTTP触发器，在调用函数时，服务端会在`response header`中强制添加`content-disposition: attachment`字段，此字段会使返回结果在浏览器中以附件的方式打开。

为了避免强制下载的问题，您可以使用以下方法。

- 设置使用自定义域名去访问函数，代替函数计算的默认域名`aliyuncs.com`。具体操作，请参见[配置自定义域名](https://help.aliyun.com/zh/functioncompute/fc/configure-custom-domain-names)。
- 添加响应头配置`content-type: text/html`。
