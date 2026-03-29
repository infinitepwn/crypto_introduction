import aes
import random
plain = [[[random.randint(0, 255) for _ in range(4)] for _ in range(4)] for _ in range(3)]
key = random.randbytes(16)

for i in range(3):
    print(f"plain{i}:")
    print(plain[i])
print("key:", key.hex())
def xor(aes_,plain):
    cipher = [[] for _ in range(3)]
    for i in range(3):
        for x in range(256):
            plain[i][1][0] = x
            cipher[i].append(aes_.encrypt(key, aes_.matrix2bytes(plain[i])))
    res = []
    for _ in range(3):
        val = 0
        for x in range(256):
            val ^= int.from_bytes(cipher[i][x])
        res.append(val)
    return res

aes_3 = aes.AES(N_ROUNDS=3)
print("三轮aes异或输出")
print(xor(aes_3,plain))

#四轮
aes_4 = aes.AES(N_ROUNDS=4)
print("四轮aes异或输出")
print(xor(aes_4,plain))

def xor1(aes_,plain):
    cipher = [[] for _ in range(3)]
    for i in range(3):
        for x in range(256):
            plain[i][1][0] = x
            cipher[i].append(aes_.encrypt1(key, aes_.matrix2bytes(plain[i])))
    res = []
    for _ in range(3):
        val = 0
        for x in range(256):
            val ^= int.from_bytes(cipher[i][x])
        res.append(val)
    return res
print("不含MC")
success = True
for Round in range(4,32):
    if xor1(aes.AES(N_ROUNDS=Round),plain) != [0,0,0]:
        print(xor1(aes.AES(N_ROUNDS=Round),plain))
        success = False
if success:
    print("所有轮数都通过了测试")