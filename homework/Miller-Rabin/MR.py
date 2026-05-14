import random
from Crypto.Util.number import *
import time
def Miller_Rabin(n):
    if n == 2 or n == 3:
        print(f"{n} 是素数")
        return 1
    if n % 2 == 0:
        print(f"{n} 是合数,并且是偶数")
        return 0
    l = 0
    m = n - 1
    while(m%2==0):
        m //= 2
        l += 1
    a = random.randint(2,n-2)
    b = pow(a,m,n)
    if b == 1:
        print(f"{n} 是素数")
        return 1
    for i in range(0,l):
        if b == n-1:
            print(f"{n} 是素数")
            return 1
        else:
            b = pow(b,2,n)
    print(f"{n} 是合数")
    return 0
def test(N):
    start = time.time()
    Miller_Rabin(N)
    end = time.time()
    return (end - start)*1000
N = random.randint(2**2047,2**2048-1)
P = getPrime(2048)
N1 = random.randint(2**4095,2**4096-1)
P1 = getPrime(4096)
print(f"测试2048bit的数")
print(f"{test(N)} ms")
print(f"测试2048bit素数")
print(f"{test(P)} ms")
print(f"测试4096bit的数")
print(f"{test(N1)} ms")
print(f"测试4096bit素数")
print(f"{test(P1)} ms")