## Secure Electronic Transaction
保障用户、商家和银行之间通过**网络**使用信用卡交易的安全性：保密性和认证性
1. 认证交易双方（签名）
2. 交易信息的保密性（加密）
3. 交易数据的完整性、 不可抵赖性（Hash、签名）


## 双签名

如（[Stallings 2000](https://en.wikipedia.org/wiki/Secure_Electronic_Transaction#CITEREFStallings2000)）所述：

> SET 引入的一项重要创新是_双重签名_。双重签名的目的是将两条分别发送给不同接收者的消息关联起来。例如，客户希望将订单信息 (OI) 发送给商家，将支付信息 (PI) 发送给银行。商家无需知道客户的信用卡号，银行也无需知道客户的订单详情。通过将这两项信息分开，客户的隐私得到了额外的保护。然而，这两项信息必须以某种方式关联起来，以便在必要时解决争议。这种关联对于客户证明此笔付款是用于此订单，而不是用于其他商品或服务至关重要。

客户分别独立计算出对象标识符 (OI) 和个人信息标识符 (PI) 的消息[摘要](https://en.wikipedia.org/wiki/Cryptographic_hash_function "加密哈希函数")(MD)。将这两个 MD 连接起来，并由此计算出另一个 MD。最后，使用客户的私钥对 MD 进行加密，生成双重签名。该双重签名会同时发送给商户和银行。协议确保商户能够看到 PI 的 MD，但看不到 PI 本身；银行能够看到 OI 的 MD，但看不到 OI 本身。双重签名可以通过 OI 或 PI 的 MD 进行验证，而无需 OI 或 PI 本身。由于 MD 不可逆，因此可以保护隐私，因为逆向操作会泄露 OI 或 PI 的内容。
## SET主要流程
![image.png|415](https://raw.githubusercontent.com/infinitepwn/note_picbed/main/20260601142418312.png)
商家是没法确认买家账户是否合法，以及是否有足够的金额
需要委托支付网关

持卡人、商家、支付网关、银行都需要认证中心

### 购买请求阶段
![image.png|443](https://raw.githubusercontent.com/infinitepwn/note_picbed/main/20260601143640503.png)
![image.png|446](https://raw.githubusercontent.com/infinitepwn/note_picbed/main/20260601144452692.png)

1. 发送购买请求REQ
2. 回应购买请求RES1
$$Sig(sk_M,H(RES1)),Cert_M,Cert_P$$
3. 验证响应合法性：确认商家身份
4. 发送订单与支付信息
$$Sig(sk_C,H(H(OI)||H(PI))),OI,H(PI),Cert_C$$
商家可以通过收到的OI和H(PI)验证签名，对PI进行哈希函数是因为不希望被购物网站知晓？（注意这个签名同时被商家和支付网关验证了）
同时还要发送[[混合加密]]的密文
实际加密用的是对称密码DES，密钥是sk1，但是sk1要通过非对称密码来加密
$$
Enc(pk_p,acc||sk_1),Enc(sk_1,Sig(sk_C,H(OI)||H(PI))||H(OI)||PI)$$
sk1是持卡人临时生成的，商家是无法解开这个密文的，只有支付网关可以

5. 验证订单信息

### 支付授权阶段
![image.png](https://raw.githubusercontent.com/infinitepwn/note_picbed/main/20260601150950642.png)

1. 请求支付授权
$$Enc(pk_P,sk_2),Enc(sk_2,Sig(sk_M,H(AuthREQ)||AuthREQ))$$
再附加上之前持卡人发过来的
$$Enc(pk_p,acc||sk_1),Enc(sk_1,Sig(sk_C,H(OI)||H(PI))||H(OI)||PI)$$
2. 验证支付授权请求
3. 支付授权回应
4. 验证支付授权回应
5. 回应订单并发货
6. 验证订单回应

### 支付请款阶段
![image.png](https://raw.githubusercontent.com/infinitepwn/note_picbed/main/20260601151439864.png)
1. 发送支付请款请求
2. 验证支付请款请求
3. 支付请款请求
4. 支付请款回应
5. 验证支付请款回应

## SET协议失败
SET 的目标是成为互联网上商家、买家和信用卡公司之间 [事实上的标准支付方式。](https://en.wikipedia.org/wiki/De_facto_standard "事实上的标准")

遗憾的是，各主要利益相关方的实施要么成本高昂，要么繁琐复杂。此外，一些外部因素也可能使消费者元素集成到浏览器中变得更加复杂。大约在 1994 年至 1995 年间，曾有传言称，微软希望从其集成到浏览器中的、符合 SET 标准的组件所保障的每笔交易中抽取 0.25% 的收入。