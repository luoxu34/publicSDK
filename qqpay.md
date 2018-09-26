# SDK接入 - QQ钱包服务端接入

接入文档：https://qpay.qq.com/buss/wiki/38/1195

交互时序图：

![](../images/QQPay.png)

## 接入接口

* [服务端统一下单](https://qpay.qq.com/buss/wiki/38/1203)
* [生成带签名的客户端支付信息](https://qpay.qq.com/buss/wiki/38/1196)
* [支付结果通知](https://qpay.qq.com/buss/wiki/38/1204)

## 参数

* mch_id：商户号
* appid：应用ID
* appkey：应用密钥
* key：下单签名key

## 服务端运行流程

### 下单部分

1. 服务端收到客户端的订单信息，根据[签名算法](https://qpay.qq.com/buss/wiki/38/1192)下单，得到预支付会话标识——`prepay_id`，也叫`tokenId`
2. 服务端使用HMAC-SHA1加密算法，生成提交订单用的sign参数，将参数prepay_id、sign等回传客户端

**注意**：sign是以`=`结尾，末尾没有换行符`\n`，若有需去除否则客户端提交订单失败

### 支付通知部分

1. 从请求的body中取出xml文档，转换成字典数据结构
2. 验证sign和其他参数，处理完后响应请求

## 服务端和客户端参数对应说明

* QQ钱包支付商户号：mch_id == bargainorId
* QQ钱包的预支付会话标识：prepay_id == tokenId

## 接入注意

1. 签名算法一共有两个，一个是服务端下单和支付通知用的，一个是服务端生成客户端参数sign用于提交订单用的
2. 生成支付用的sign是在服务端执行的，使用的密钥是appkey
3. 下单和支付通知用的密钥是key，跟appkey不是同一个
4. 常见错误就是把密钥key和appkey用反了，或者签名串排错顺序，或者值赋错了

