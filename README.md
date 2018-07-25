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

## Login

### 对于https的登陆验证，取消requests默认的证书验证

```python
import requests

verify_url = "https://sdk.youximao.com/cp/getUserByOpenId"
params = {"openId": uid}
response = requests.post(verify_url, params, verify=False)
```

## Create

### 服务端下单生成渠道回调地址

```python
protocol = request.request.protocol
host = request.request.host
if host == "public.sdk.gzyouai.com":
    protocol = "https"

notifyUrl = "%s://%s/paycheck/confirm" % (protocol, host)
notifyUrl = "%s/%s/%s/%s" % (notifyUrl, request.game_code, request.sdk_code, request.sdk_version_name)

#req_body["notify_url"] = notifyUrl
```

## Confirm

### 验证发起回调的游戏服在白名单中

```python
ips = ["1.2.3.4", "4.3.2.1"]

if request.remote_ip not in ips:
    return {"remark": "非法回调,发起请求IP:%s" % request.remote_ip}
```

