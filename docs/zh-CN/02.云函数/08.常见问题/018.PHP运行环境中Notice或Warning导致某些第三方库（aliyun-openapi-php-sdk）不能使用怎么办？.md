# PHP运行环境中Notice或Warning导致某些第三方库（aliyun-openapi-php-sdk）不能使用怎么办？

PHP运行环境对异常处理严格，针对一些第三方库的引入，可能会出现因Warning或Notice而无法使用的情况。函数计算允许您通过自定义`set_error_handler`来覆盖运行环境中的默认处理。
