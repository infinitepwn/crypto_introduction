Q:什么是ElGamal签名

ElGamal 签名是一种**基于离散对数困难问题**的数字签名算法。它和 ElGamal 加密同源，思想也类似：在有限域乘法群里，利用私钥生成签名，别人用公钥验证签名。

### 参数生成

选择一个大素数 p，以及模 p 下的生成元 (g)。

私钥为：
$$
x
$$
公钥为：
\[
y \equiv g^x \pmod p
\]
所以公钥是：

\[
(p,g,y)
\]
私钥是：

\[
x
\]

### 签名过程

假设消息为 (m)，一般先计算哈希：

$$
H(m)
$$
签名者随机选一个临时随机数 (k)，要求：

\[
\gcd(k,p-1)=1
\]
然后计算：

$$r \equiv g^k \pmod p$$

再计算：

$$s \equiv k^{-1}(H(m)-xr) \pmod{p-1}$$

最终签名为：

\[
(r,s)
\]

---

### 验证过程

验证者检查：

$$g^{H(m)} \equiv y^r r^s \pmod p$$

如果等式成立，则签名有效。

---

### 为什么验证公式成立？

因为：

$$y = g^x$$

$r = g^k$

所以：

$$y^r r^s
\equiv (g^x)^r (g^k)^s
\pmod p$$

即：

$$y^r r^s
\equiv g^{xr} g^{ks}
\pmod p$$

又因为签名时：

$s \equiv k^{-1}(H(m)-xr) \pmod{p-1}$

所以：

$ks \equiv H(m)-xr \pmod{p-1}$

因此：

$$xr+ks \equiv H(m) \pmod{p-1}$$

于是：

$$g^{xr+ks} \equiv g^{H(m)} \pmod p$$

所以验证公式成立。
