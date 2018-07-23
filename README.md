# publicSDK

## Interface 接口

公共SDK服务端一般需要对接如下三个接口：

```python
def login(login_data, sdk_config={}):
    """登陆验证
    
    :param login_data: (dict)客户端传过来用于验证登陆的参数，一般有openID、token、timestamp
    :param sdk_config: (dict)服务端配置，一般有appId、appKey
    :return: (tuple)登陆结果：status, message, userid, [other]
    """
    return ""

def create(request, pay_channel):
    """服务端下单
    
    :param request: (object)客户端的创建订单请求
    :param pay_channel: (dict)服务端配置，一般有appId、appKey
    :return: (string)渠道订单号
    """
    return ""

def confirm(request, sdk_config):
    """支付通知
    
    :param request: (object)渠道支付后的回调请求
    :param sdk_config: (dict)服务端配置，一般有appId、appKey
    :return: (dict)处理结果
    """
    return ""
```

