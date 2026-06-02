## 盲签名
![image.png](https://raw.githubusercontent.com/infinitepwn/note_picbed/main/20260601153538022.png)
即使签名泄漏，签名者也无法追踪签名是谁的

##  基于RSA的盲签名

![cover387_20260601135109_副本.jpg](https://raw.githubusercontent.com/infinitepwn/note_picbed/main/cover387_20260601135109_副本.jpg)
### 盲花因子

## E-cash主要流程
![image.png](https://raw.githubusercontent.com/infinitepwn/note_picbed/main/20260601154003151.png)
1. 提款协议
2. 支付协议
3. 存款协议
### 提款协议
1. 用户发送盲化后的消息c(x),其中x为伪随机数
2. 银行签署盲化消息c(x),并扣除付款方账户固定金额
3. 银行发送签名 $$\sigma' = Sig(sk,c(x))$$
4. 用户消除盲化因子，得到
$\sigma = Sig(sk,x),(\sigma,x)$表示固定金额的电子现金
### 支付协议

### 存款协议