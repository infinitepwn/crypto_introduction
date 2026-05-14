from Crypto.Util.number import *

n = 3026533
e = 3
c = 152702
p, q = list(factor(n))[0][0], list(factor(n))[1][0]
phi = (p-1)*(q-1)
d = inverse(e, phi)

dp = d % (p-1)
dq = d % (q-1)
qinv = inverse(q, p)

def quick():
    mp = pow(c % p, dp, p)
    mq = pow(c % q, dq, q)
    h = (qinv * (mp - mq)) % p
    m = mq + h * q
    return m

def rsa():
    return pow(c, d, n)
%timeit quick()
%timeit rsa()