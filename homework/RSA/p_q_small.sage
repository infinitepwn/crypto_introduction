from sage.all import *
from Crypto.Util.number import *
def fermat_steps(n):
    """
    按题目中的算法运行，返回：
    S = 程序输出
    steps = while循环执行次数
    """
    x = ceil(2 * sqrt(Integer(n)))
    steps = 0
    while True:
        t = x*x - 4*n
        if is_square(t):
            return x - 1, steps
        x += 1
        steps += 1

def make_close_primes_example():
    """
    构造一个 3076-bit 的 n = p*q，且 p-q 很小
    """
    # q 取 1538 bit 左右素数
    q = getPrime(1538)

    # 让差值比较小，远小于 10*2^768
    bound = 10 * 2^768
    while True:
        delta = ZZ.random_element(1, bound)
        # 为了让 p 更可能是奇数素数，尽量取偶数增量
        if delta % 2 == 1:
            delta += 1
        p = q + delta
        if is_prime(p):
            break

    if p < q:
        p, q = q, p

    n = p * q
    return p, q, n

# 生成测试样例
p, q, n = make_close_primes_example()

print("bitlength(n) =", n.nbits())
print("p - q =", p - q)
print("bound  =", 10 * 2^768)
print("condition satisfied? ", p - q < 10 * 2^768)

# 运行题目算法
S, steps = fermat_steps(n)

print("\nProgram output S =", S)
print("Actual p + q     =", p + q)
print("Steps            =", steps)
print("Within 100?      =", steps < 100)
print("p bits =", p.nbits())
print("q bits =", Integer(q).nbits())
print("n bits =", Integer(n).nbits())
print("p+q bits =", (p+q).nbits())