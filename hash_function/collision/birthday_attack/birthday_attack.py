#实现FNV-1a 32位哈希函数
def fnv1a_32(data: bytes) -> int:
    hash_value = 0x811c9dc5
    for byte in data:
        hash_value ^= byte
        hash_value = (hash_value * 0x01000193) & 0xFFFFFFFF
    return hash_value
#哈希表，直接用python字典实现就行了
import os
import binascii

def birthday_attack(target_func):
    seen = {}
    attempts = 0
    
    while True:
        # 1. 生成随机输入 (可以是随机字节)
        m = os.urandom(8) 
        # 2. 计算 32-bit 哈希
        h = target_func(m)
        attempts += 1
        
        # 3. 碰撞检查
        if h in seen:
            if seen[h] != m: # 确保不是同一个输入
                # print(f"找到碰撞! 尝试次数: {attempts}")
                # print(f"m1: {binascii.hexlify(seen[h])}")
                # print(f"m2: {binascii.hexlify(m)}")
                # print(f"Hash: {hex(h)}")
                break
        else:
            seen[h] = m
            
        if attempts > 500000: # 安全阈值
            print("超过预期尝试次数，请检查哈希分布。")
            break
    return attempts
average_attempts = 0
from tqdm import *
for _ in trange(1000):
    attempts = birthday_attack(fnv1a_32)
    average_attempts += attempts
print(f"平均尝试次数: {average_attempts / 1000}")
print("理论次数: 约 2^16 = 65536")