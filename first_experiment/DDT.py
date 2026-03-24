import pandas as pd
import numpy as np
# 选择S1
S1 = [
    [14,  4, 13,  1,  2, 15, 11,  8,  3, 10,  6, 12,  5,  9,  0,  7],  
    [0, 15,  7,  4, 14,  2, 13,  1, 10,  6, 12, 11,  9,  5,  3,  8],  
    [4,  1, 14,  8, 13,  6,  2, 11, 15, 12,  9,  7,  3, 10,  5,  0],  
    [15, 12,  8,  2,  4,  9,  1,  7,  5, 11,  3, 14, 10,  0,  6, 13]  
]
def Sbox(x):
    row = (x>>5<<1) | (x&0b1)  # 第一位+最后一位决定行
    col = (x>>1) & 0b1111      # 中间四位决定列
    return S1[row][col]
#alpha遍历了6bit，beta遍历了4bit
DDT = [[0 for _ in range(16)] for _ in range(64)]
#遍历alpha
for alpha in range(64):
    #遍历所有x，计算差分
    for x in range(64):
        beta = Sbox(x) ^ Sbox(x ^ alpha)  # 计算输出差分
        DDT[alpha][beta] += 1  # 更新DDT计数
print("差分分布表（DDT）:")

df = pd.DataFrame(DDT)
df.index = [f"{i:02X}" for i in range(64)] 
df.columns = [f"{i:X}" for i in range(16)]   


df.index.name = "Input XOR" 
df.columns.name = "Output XOR"

table = df.to_string(col_space=4, justify='center')

print(table)
#该DDT中概率最大的（输入差分，输出差分）对应有多少种情况？概率为多少？
DDT = np.array(DDT)
size = 16*64  # 输入空间大小
sortddt = np.argsort(DDT.ravel())[::-1]
import numpy as np

print("概率最大的前5个（输入差分，输出差分）及其概率：")
for i in range(5):
    idx = sortddt[i]
    # 使用 unravel_index 获取坐标
    r, c = np.unravel_index(idx, DDT.shape)
    row, col = int(r), int(c)
    val = int(DDT[row, col])
    prob = val / size
    print(f"{i+1:>3}  |  {prob:<10.6f}  |  (0x{row:02X}, 0x{col:X})")

ddt = np.array(DDT).flatten()

eff_ddt = ddt[ddt > 0]

eff_ddt = sorted(list(set(eff_ddt)))

print(f"该 S 盒共有 {len(eff_ddt)} 种概率传播：")
print("-" * 30)
for count in eff_ddt:
    prob = count / 64.0
    print(f"计数 {count:2} -> 概率 {prob:.4f} (即 {count}/64)")
#对该S盒，输入差分非0，输出差分可能为0吗？为什么？
# 获取除第一行外的第一列数据
data = df.iloc[1:, 0]

# 使用布尔索引筛选出计数大于 0 的项
zero = data[data > 0]
print("输入差分非 0 但输出差分为 0 的情况：")
for alpha, count in zero.items():
    print(f"输入差分{alpha}: 有 {count} 个输入导致输出差分为 0")