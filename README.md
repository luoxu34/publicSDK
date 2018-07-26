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
    return {
        'amount': u'1.00',
        'order_id': u'xxx',
        'query_id': u'xxx',
        'remark': '',
        'result_msg': 'success'
    }
```

## Login 登陆

### 忽略requests对https请求的SSL证书验证

否则可能看到这样的报错：

`requests.exceptions.SSLError: bad handshake: Error([('SSL routines', 'tls_process_server_certificate', 'certificate verify failed')],)`

```python
import requests

verify_url = "https://sdk.example.com/login"
params = {"openId": uid}

response = requests.post(verify_url, params, verify=False)
```

## Create 下单

### 服务端下单生成渠道回调地址

```python
protocol = request.request.protocol
host = request.request.host
if host == "public.sdk.gzyouai.com":
    protocol = "https"

notifyUrl = "%s://%s/paycheck/confirm" % (protocol, host)
notifyUrl = "%s/%s/%s/%s" % (notifyUrl, request.game_code, request.sdk_code, request.sdk_version_name)

# req_body["notify_url"] = notifyUrl
```

## Confirm 支付通知

### 验证发起回调的游戏服在白名单中

```python
ips = ["1.2.3.4", "4.3.2.1"]

if request.remote_ip not in ips:
    return {"remark": "非法回调,发起请求IP:%s" % request.remote_ip}
```

### 生成签名串的公共方法 

要求：

1. 所有收到的参数按key排序，sign/flag除外
2. 空值和None不参与运算
3. 如果是布尔型，转换成0或1

```python
def get_sign_str1(param, link="=", join="&", 
                  ignore_key=("sign", "flag"), 
                  ignore_value=("", None), 
                  change_bool=False):
    str_list = []
    
    for k, v in sorted(param.iteritems()):
        if k in ignore_key or v in ignore_value:
            continue
            
        if change_bool and isinstance(v, bool):
            v = "1" if v is True else "0"

        str_list.append("%s%s%s" % (k, link, "" if v is None else v))

    return join.join(str_list)
```

### 对签名value进行urlencode编码

有的时候渠道回调，会传中文的value，而签名的时候要求先对中文进行urlencode编码，接着计算哈希值，最后才比对。

```python
import urllib
str_list.append("%s%s%s" % (k, link, urllib.quote("" if v is None else v)))
```

> **[warning] warning**
> 
> 千万不要拼完整个字符串后再编码，应该只对value编码

## Attention

### 被join的每个元素必须是字符串

```python
>>> # 正确的例子
>>> ''.join(['1', '2'])
'12'

>>> # 错误的例子
>>> ''.join([1, 2])
TypeError: sequence item 0: expected string, int found
```

### '{}'.format参数不能是unicode

(only py2)由于python2中str和unicode两种编码共存导致

```python
s = u'60\u5143\u5b9d'

# %s 可以格式化unicode字符串
>>> '%s' % s
u'60\u5143\u5b9d'

# 字符串的format方法不能格式化unicode字符串
>>> '{}'.format(s)
UnicodeEncodeError: 'ascii' codec can't encode characters in position 2-3: ordinal not in range(128)

# 同样的错误
>>> u'{}'.format('中国')
UnicodeDecodeError: 'ascii' codec can't decode byte 0xe4 in position 0: ordinal not in range(128)

# 正常的例子
>>> u'{}'.format(u'中国')

# 内置format函数可以格式化unicode字符串
>>> format(s)
u'60\u5143\u5b9d'
```

