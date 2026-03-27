# DES S boxes
S1 = [
    [14,4,13,1,2,15,11,8,3,10,6,12,5,9,0,7],
    [0,15,7,4,14,2,13,1,10,6,12,11,9,5,3,8],
    [4,1,14,8,13,6,2,11,15,12,9,7,3,10,5,0],
    [15,12,8,2,4,9,1,7,5,11,3,14,10,0,6,13]
]

S2 = [
    [15,1,8,14,6,11,3,4,9,7,2,13,12,0,5,10],
    [3,13,4,7,15,2,8,14,12,0,1,10,6,9,11,5],
    [0,14,7,11,10,4,13,1,5,8,12,6,9,3,2,15],
    [13,8,10,1,3,15,4,2,11,6,7,12,0,5,14,9]
]

S3 = [
    [10,0,9,14,6,3,15,5,1,13,12,7,11,4,2,8],
    [13,7,0,9,3,4,6,10,2,8,5,14,12,11,15,1],
    [13,6,4,9,8,15,3,0,11,1,2,12,5,10,14,7],
    [1,10,13,0,6,9,8,7,4,15,14,3,11,5,2,12]
]

def sbox_lookup(x, sbox):
    # x is 6-bit integer
    row = ((x & 0b100000) >> 4) + (x & 0b000001)
    col = (x >> 1) & 0b1111
    return sbox[row][col]

def compute_ddt(sbox):
    ddt = [[0 for _ in range(16)] for _ in range(64)]
    for dx in range(64):
        for x in range(64):
            y1 = sbox_lookup(x, sbox)
            y2 = sbox_lookup(x ^ dx, sbox)
            dy = y1 ^ y2
            ddt[dx][dy] += 1
    return ddt

def print_ddt(ddt):
    print("     ", end="")
    for dy in range(16):
        print(f"{dy:>3}", end=" ")
    print()
    for dx in range(64):
        print(f"{dx:>3}: ", end="")
        for dy in range(16):
            print(f"{ddt[dx][dy]:>3}", end=" ")
        print()

def analyze_ddt(ddt):
    # 忽略 dx=0 的平凡情况
    max_count = 0
    max_pairs = []

    values = set()
    nonzero_to_zero = []

    for dx in range(1, 64):
        for dy in range(16):
            c = ddt[dx][dy]
            if c > 0:
                values.add(c / 64)

            if c > max_count:
                max_count = c
                max_pairs = [(dx, dy)]
            elif c == max_count:
                max_pairs.append((dx, dy))

            if dy == 0 and c > 0:
                nonzero_to_zero.append((dx, c))

    return max_count, max_pairs, sorted(values), nonzero_to_zero

# 处理多个S盒
sboxes = [("S1", S1), ("S2", S2), ("S3", S3)]

for name, sbox in sboxes:
    print(f"\n=====================================")
    print(f"分析 {name} 盒:")
    print(f"=====================================")
    
    ddt = compute_ddt(sbox)
    print_ddt(ddt)
    
    max_count, max_pairs, probs, nonzero_to_zero = analyze_ddt(ddt)
    
    print("\n最大出现次数:", max_count)
    print("对应概率:", max_count / 64)
    print("达到最大值的 (dx, dy):", max_pairs)
    print("该S盒所有可能的非零概率传播:", probs)
    print("输入差分非0而输出差分为0的情况:", nonzero_to_zero)
    