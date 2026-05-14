import aes  
import random

cipher = aes.AES(N_ROUNDS=3)
master_key = random.randbytes(16)
round_keys = cipher.expand_key(master_key)

# 构造初始 Lambda-集合 (256个矩阵)
states = []
for x in range(256):
    p = [[0]*4 for _ in range(4)]
    p[1][0] = x  
    states.append(p)


# --- 第 0 轮 ---
for i in range(256):
    states[i] = cipher.add_round_key(states[i], round_keys[0])

# --- 第 1 轮 ---
for i in range(256):
    states[i] = cipher.sub_bytes(states[i])
    cipher.shift_rows(states[i])
    cipher.mix_columns(states[i])
    states[i] = cipher.add_round_key(states[i], round_keys[1])

# --- 第 2 轮 ---
for i in range(256):
    states[i] = cipher.sub_bytes(states[i])
    cipher.shift_rows(states[i])
    cipher.mix_columns(states[i])
    states[i] = cipher.add_round_key(states[i], round_keys[2])

# --- 第 3 轮  ---
for i in range(256):
    states[i] = cipher.sub_bytes(states[i])
    cipher.shift_rows(states[i])

for i in range(256):
    cipher.mix_columns(states[i])

# 统计第 3 轮 MixColumns 输出端 (y0) 的取值个数
col_output_vals = [states[i][0][0] for i in range(256)]
unique_count = len(set(col_output_vals))
print(f"字节 y0 的唯一值个数: {unique_count}")

# 验证异或平衡性
xor_sum = 0
for val in col_output_vals:
    xor_sum ^= val
print(f"字节 y0 的异或和: {xor_sum}")

z0_output_vals = []
for val in col_output_vals:
    # 模拟 S盒 变换
    z0_output_vals.append(cipher.s_box[val])

print("第 4 轮 SubBytes 输出")
unique_count_z = len(set(z0_output_vals))
print(f"字节 z0 的唯一值个数: {unique_count_z}")

# 验证第四轮后的平衡性 (异或和)
xor_sum_z = 0
for val in z0_output_vals:
    xor_sum_z ^= val
print(f"字节 z0 的异或和: {xor_sum_z}")

if xor_sum_z != 0:
    print("异或和不为0")