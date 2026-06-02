涉及公钥密码学的数学基础

[[费马小定理]]



由Michael O. Rabin （1979）提出
安全性基于求合数的模平方根的难度
该问题等价于因子分解

## 参数选择
选取两个素数p，q，满足
$$p\equiv 3 \pmod 4$$
$$q\equiv 3 \pmod 4$$
公钥为$n=pq$
## 加密
加密消息M，M< n
$$C = M^2 \pmod n$$
## 解密
考虑模p的情况下
[[模平方根#$p equiv 3 pmod 4$的情况]]
$$M = \pm C^{\frac{p+1}{4}} \pmod p$$
模q的情况下

## 安全性
[[Las Vegas算法]]