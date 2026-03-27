SBOX = (
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
    0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
    0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
    0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
    0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
    0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
    0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
    0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
    0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
    0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
    0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
    0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
    0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
    0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
    0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
    0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16,
)

RCON = (0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36)

# =========================
# 基础工具
# =========================

def bytes_to_state(block):
    """
    16字节 -> AES状态矩阵 state[row][col]
    按 AES 标准列优先填充：
    [ 0  4  8 12 ]
    [ 1  5  9 13 ]
    [ 2  6 10 14 ]
    [ 3  7 11 15 ]
    """
    state = [[0] * 4 for _ in range(4)]
    for col in range(4):
        for row in range(4):
            state[row][col] = block[4 * col + row]
    return state

def state_to_bytes(state):
    """AES状态矩阵 -> 16字节"""
    block = [0] * 16
    for col in range(4):
        for row in range(4):
            block[4 * col + row] = state[row][col]
    return block

def xor_bytes(a, b):
    return [x ^ y for x, y in zip(a, b)]

def all_zero(vec):
    for x in vec:
        if x != 0:
            return False
    return True

def fmt_block(block):
    return "[" + ", ".join(f"{x:02x}" for x in block) + "]"

# =========================
# AES 轮函数
# =========================

def sub_bytes(state):
    for row in range(4):
        for col in range(4):
            state[row][col] = SBOX[state[row][col]]

def shift_rows(state):
    state[1] = state[1][1:] + state[1][:1]
    state[2] = state[2][2:] + state[2][:2]
    state[3] = state[3][3:] + state[3][:3]

def gmul(a, b):
    """
    GF(2^8) 上乘法，模多项式 x^8 + x^4 + x^3 + x + 1
    """
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi_bit = a & 0x80
        a = (a << 1) & 0xFF
        if hi_bit:
            a ^= 0x1B
        b >>= 1
    return p

def mix_single_column(col):
    """
    修正版 MixColumns
    [
      2 3 1 1
      1 2 3 1
      1 1 2 3
      3 1 1 2
    ]
    """
    c0, c1, c2, c3 = col
    return [
        gmul(2, c0) ^ gmul(3, c1) ^ c2 ^ c3,
        c0 ^ gmul(2, c1) ^ gmul(3, c2) ^ c3,
        c0 ^ c1 ^ gmul(2, c2) ^ gmul(3, c3),
        gmul(3, c0) ^ c1 ^ c2 ^ gmul(2, c3)
    ]

def mix_columns(state):
    for col in range(4):
        old_col = [state[row][col] for row in range(4)]
        new_col = mix_single_column(old_col)
        for row in range(4):
            state[row][col] = new_col[row]

def add_round_key(state, round_key_state):
    for row in range(4):
        for col in range(4):
            state[row][col] ^= round_key_state[row][col]

# =========================
# AES-128 密钥扩展
# =========================

def rot_word(word):
    return word[1:] + word[:1]

def sub_word(word):
    return [SBOX[b] for b in word]

def expand_key(master_key, rounds):
    """
    master_key: 16字节列表
    返回 rounds+1 个轮密钥，每个轮密钥都是 state[row][col] 形式
    """
    if len(master_key) != 16:
        raise ValueError("这里只实现 AES-128，所以密钥长度必须是16字节")

    words = []
    for i in range(4):
        words.append(master_key[4 * i: 4 * i + 4])

    total_words = 4 * (rounds + 1)

    for i in range(4, total_words):
        temp = words[i - 1][:]

        if i % 4 == 0:
            temp = rot_word(temp)
            temp = sub_word(temp)
            temp[0] ^= RCON[i // 4]

        new_word = [words[i - 4][j] ^ temp[j] for j in range(4)]
        words.append(new_word)

    round_keys = []
    for r in range(rounds + 1):
        key16 = []
        for i in range(4):
            key16.extend(words[4 * r + i])
        round_keys.append(bytes_to_state(key16))

    return round_keys

# =========================
# AES 指定轮数加密
# 题目要求“每轮4步都执行”
# 所以这里不是标准AES末轮，而是每一轮都执行 SB, SR, MC, ARK
# =========================

def encrypt_block(block, master_key, rounds, use_mc=True):
    state = bytes_to_state(block)
    round_keys = expand_key(master_key, rounds)

    add_round_key(state, round_keys[0])

    for r in range(1, rounds + 1):
        sub_bytes(state)
        shift_rows(state)
        if use_mc:
            mix_columns(state)
        add_round_key(state, round_keys[r])

    return state_to_bytes(state)

# =========================
# 构造明文集合
# =========================

def generate_plaintexts(fixed_bytes, active_index):
    """
    fixed_bytes: 长度16的常数字节列表
    active_index: 哪一个字节遍历 0~255
    """
    pts = []
    for x in range(256):
        p = fixed_bytes[:]
        p[active_index] = x
        pts.append(p)
    return pts

def xor_all_blocks(blocks):
    acc = [0] * 16
    for block in blocks:
        for i in range(16):
            acc[i] ^= block[i]
    return acc

# =========================
# 实验部分
# =========================

# 你把下面三个 active_index 改成题图里三个红色位置对应的下标
# 这里先给你一个可运行模板：
GROUPS = [
    {
        "name": "第1组",
        "active_index": 0,
        "fixed": [
            0x10, 0x22, 0x34, 0x46,
            0x58, 0x6A, 0x7C, 0x8E,
            0x91, 0xA3, 0xB5, 0xC7,
            0xD9, 0xEB, 0xFD, 0x0F
        ]
    },
    {
        "name": "第2组",
        "active_index": 5,
        "fixed": [
            0x01, 0x13, 0x25, 0x37,
            0x49, 0x5B, 0x6D, 0x7F,
            0x80, 0x92, 0xA4, 0xB6,
            0xC8, 0xDA, 0xEC, 0xFE
        ]
    },
    {
        "name": "第3组",
        "active_index": 10,
        "fixed": [
            0xFF, 0xEE, 0xDD, 0xCC,
            0xBB, 0xAA, 0x99, 0x88,
            0x77, 0x66, 0x55, 0x44,
            0x33, 0x22, 0x11, 0x00
        ]
    }
]

# 固定主密钥，方便实验结果可复现
MASTER_KEY = [
    0x2B, 0x7E, 0x15, 0x16,
    0x28, 0xAE, 0xD2, 0xA6,
    0xAB, 0xF7, 0x15, 0x88,
    0x09, 0xCF, 0x4F, 0x3C
]

def run_one_group(group, rounds, use_mc):
    pts = generate_plaintexts(group["fixed"], group["active_index"])
    cts = []

    for pt in pts:
        ct = encrypt_block(pt, MASTER_KEY, rounds, use_mc)
        cts.append(ct)

    x = xor_all_blocks(cts)
    return x

def experiment(rounds, use_mc):
    print("=" * 70)
    print(f"加密轮数 = {rounds}，是否执行 MixColumns = {use_mc}")
    print(f"主密钥 = {fmt_block(MASTER_KEY)}")
    print("-" * 70)

    for group in GROUPS:
        x = run_one_group(group, rounds, use_mc)
        print(f'{group["name"]}，active_index = {group["active_index"]}')
        print("异或结果 =", fmt_block(x))
        print("是否全0  =", all_zero(x))
        print("-" * 70)

def experiment_without_mc_more_rounds(max_rounds=10):
    print("=" * 70)
    print("删除 MixColumns 后，多轮测试")
    print("=" * 70)

    for rounds in range(1, max_rounds + 1):
        ok = True
        for group in GROUPS:
            x = run_one_group(group, rounds, use_mc=False)
            if not all_zero(x):
                ok = False
                break
        print(f"rounds = {rounds:2d}, 三组是否全为0: {ok}")

def main():
    # 题目第 2 问：3轮 AES
    experiment(rounds=3, use_mc=True)

    # 题目第 3 问：4轮 AES
    experiment(rounds=4, use_mc=True)

    # 题目第 4 问：删除 MC 后保持多少轮
    experiment_without_mc_more_rounds(max_rounds=10)

if __name__ == "__main__":
    main()