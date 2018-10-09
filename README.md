# publicSDK

## Interface 接口

公共SDK服务端一般需要对接如下三个接口：

```python
def login(login_data, sdk_config={}):
    """登陆验证

    :param login_data: (dict)客户端传过来用于验证登陆的参数，一般有openID、token、timestamp
    :param sdk_config: (dict)服务端配置，一般有appId、appKey
    :return: (tuple)登陆结果：status, message, userid[, other]
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
        'err_msg': '',
        'result_msg': 'success'
    }
```

**强调一下，三个函数都有返回值，如果是调用其他sdk的函数，该sdk的返回不要忽略，否则上层拿不到任何想要的结果。**

## Login 登陆

### 旧接口

旧接口是这样定义的：

```python
def login(uid, sign, timestamp, sdk_config={})
```

前三个参数都是客户端传过来的，uid就是openId，sign一般是token，timestamp是10位长度的数字，sdk_config就是服务端参数。

### 不同方式提交参数

```python
# 1. 表单方式
headers = {"Content-Type": "application/x-www-form-urlencoded"}

# 2. 键值对方式
headers = {"Content-Type": "application/json"}

response = requests.post(verify_url, params, headers=headers)
```

### 忽略requests对https请求的SSL证书验证

否则可能看到这样的报错：

`requests.exceptions.SSLError: bad handshake: Error([('SSL routines', 'tls_process_server_certificate', 'certificate verify failed')],)`

```python
import requests

verify_url = "https://sdk.example.com/login"
params = {"openId": uid}

response = requests.post(verify_url, params, verify=False)
```

### 登陆成功后返回客户端结果

通常情况下返回三个参数给上层调用:

```python
return 0, "success", uid
```

上层会取出uid放到openId中返回给客户端的公共层。

有的特殊情况，需要多传一个token或其他对象回客户端，这时返回应该这样：

```python
return 0, "success", uid, token
```

第四个元素最好是字符串类型，token值会被上层调用取出放到other返回客户端。

需要注意的是，如果元素四是字典对象，那字典中的other值会被取出返回客户端，而不是整个字典对象，可能导致意想不到的结果。详见代码`server.py`中的`LogincheckHandler`类。

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

### 返回值

需要非常注意，create函数的返回值，是会被存入到action表的other字段，同时返回给客户端。

通常这个返回值是渠道订单号，所以是字符串。如果返回很多值一般用json字符串，这时一定要把dict转成json再返回，不然存到mysql的时候就会出错。

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
def get_sign_str(param, link="=", join="&",
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

### 收到get方式的支付通知

一般情况下支付通知是post请求，也有的渠道会使用get，此时读取参数的方式就不一样了。

```python
# post方式读取参数
def confirm(request, sdk_config):
    data = request.REQUEST
    if not data and request.body:
        data = json.loads(request.body)

# get方式读取参数
def confirm(request, sdk_config):
    data = {}
    for key in request.request.arguments.keys():
        data[key] = request.get_argument(key, strip=False)

# get方式也可以这样读取参数
def confirm(request, sdk_config):
    rg = lambda x, y='': request.get_argument(x, y)
    rg('query_id', '')
```

### result_msg的返回值类型

返回渠道的result_msg类型一般是字符串或者字典，如果是其他类型，tornado就不接受了。

例如如果返回整形数字而非字符串数字，就会看到这样的报错：

```python
    {'remark': 'success', 'result_msg': 0, 'order_id': u'10011608176537015', 'err_msg': '', 'amount': 6.0, 'query_id': u'20180817114924837334D098'}
Traceback (most recent call last):
  File "/data/www/sdk_validator_server/server.py", line 135, in _call_back
    func(*argv)
  File "/data/www/sdk_validator_server/server.py", line 487, in handler
    self.write(result_msg)
  File "/data/www/sdk_validator_server/server.py", line 249, in write
    super(BaseSDKHandler,self).write(rsp)
  File "/usr/local/lib/python2.7/site-packages/tornado-4.2-py2.7-linux-x86_64.egg/tornado/web.py", line 695, in write
    raise TypeError(message)
TypeError: write() only accepts bytes, unicode, and dict objects
```

### 返回结果中的remark/err_msg/result_msg区别

#### 区别：

* remark 将会被存在数据库表中，说明订单支付/发货情况
* result_msg 返回给渠道的信息，一般是普通的字符串或数字，也有可能是json字符串
* err_msg 错误信息，如果发货失败，就会使用这个值返回渠道，而且是覆盖了result_msg的返回

#### 要留心err_msg的使用

这里涉及两个问题：

* err_msg字符串包含%s和不包含时的区别
* 为什么发货失败会覆盖result_msg的返回值

如果发货正常，那返回渠道的就是result_msg，但是一旦发货失败，返回的就是err_msg字符串了。

而且，如果err_msg为空字符串，返回值将会被重写，这样导致渠道收到的返回值格式不对。

下面就是发货失败后主程序执行的代码：

```python
if "%s" not in err_msg:
    result_msg = err_msg or '%s callback to game error %s' % (
        pay_action.queryId,pay_action.remark)
else:
    result_msg = err_msg % (u'订单:%s, 游戏发货状态:%s' % (
        pay_action.queryId, pay_action.remark))
```

#### 最佳实践：

```python
def confirm(request, sdk_config):
    ret = {'err_msg': '{"ResultCode": 1, "ResultMessage": "%s"}'}

    # your code in here

    if success:
        ret["amount"] = amount
        ret["query_id"] = query_id
        ret["order_id"] = order_id
        ret["remark"] = "success"
        ret["result_msg"] = make_result_msg(0, "success")

    return ret
```

### 暂停充值

如果想停止对应sdk的充值通知接口confirm执行，需要给对应的sdk服务端参数增加一个参数：

`stop_pay`: 如要暂停充值填写true，否则填其他任意值

控制confirm是否执行是在主程序中的，所以不需要改动sdk中的任何代码。新增参数后到游戏配置页面设置`stop_pay`的值，再更新配置就完成了。

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

### xml document 和 dict 互转

* 使用bs4库将xml文档转成字典

```python
def trans_xml_to_dict(xml):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(xml, features='xml')
    xml = soup.find('xml')
    if not xml:
        return {}

    data = dict([(item.name, item.text) for item in xml.find_all()])
    return data
```

* 字段转成xml文档的格式

```python
def trans_dict_to_xml(data):
    xml = []
    for k in sorted(data.keys()):
        v = data.get(k)
        if k == 'detail' and not v.startswith('<![CDATA['):
            v = '<![CDATA[{}]]>'.format(v)
        xml.append('<{key}>{value}</{key}>\n'.format(key=k, value=v))
    return '<xml>\n{}</xml>'.format(''.join(xml))
```

