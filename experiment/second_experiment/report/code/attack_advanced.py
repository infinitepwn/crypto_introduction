import asyncio
import aiohttp
from time import perf_counter

try:
    from tqdm import tqdm
except ImportError as exc:
    raise SystemExit("请先安装 tqdm: pip install tqdm") from exc

# ================= 实验环境配置 =================
# 密文顺序: IV(16B) + C1(16B) + C2(16B) + C3(16B) = 128位 Hex
TARGET_HEX = (
    "46307250616464316e674f7261636c33"
    "9ae0735429869542efc40dcdc3f4c170"
    "649463f719c5ddf4ce8c6d1ef0e5d41a"
    "c5d137629e3fe1340cfaad7e21d65d14"
)
ORACLE_URL = "http://10.102.33.67:8208/dec_2?data="
BLOCK_SIZE = 16
MAX_CONCURRENT = 32
REQUEST_TIMEOUT = 5
REQUEST_DELAY = 0.05
BYTE_DELAY = 0.10
BLOCK_DELAY = 0.20
# ===============================================


def format_plain_byte(value):
    if 32 <= value <= 126:
        return chr(value)
    return f"\\x{value:02x}"

async def check_padding(session, sem, payload_hex):
    async with sem:
        if REQUEST_DELAY > 0:
            await asyncio.sleep(REQUEST_DELAY)
        try:
            async with session.get(ORACLE_URL + payload_hex, timeout=REQUEST_TIMEOUT) as resp:
                # 200 表示填充正确 [cite: 158], 500 表示填充错误 [cite: 159]
                return resp.status == 200
        except (asyncio.TimeoutError, aiohttp.ClientError):
            return False

async def solve_block(session, sem, blocks, target_idx, progress):
    target_c_hex = blocks[target_idx]
    
    # 构造 Prefix: 凑齐 3 个分组。
    # 逻辑：取目标块 Ci 之前的所有原始块作为前缀，如果不足两个，则用第一个块填充。
    if target_idx == 1:
        prefix_hex = blocks[0] + blocks[0]  # IV + IV
    else:
        prefix_hex = "".join(blocks[:target_idx-1])
        if len(prefix_hex) < 64: # 如果不足两个分组(32字节)，则补齐
            prefix_hex = blocks[0] + prefix_hex

    # 只取最后两个块作为 Prefix，保证总共是 3 分组: Prefix_1 + r + Target_C
    prefix_hex = prefix_hex[-64:] 

    intermediate_a = [0] * BLOCK_SIZE
    progress.set_description(f"Padding Oracle C{target_idx}")
    progress.write(f"[*] 正在破解第 {target_idx} 分组 (C{target_idx})...")

    for byte_pos in range(BLOCK_SIZE - 1, -1, -1):
        pad_val = BLOCK_SIZE - byte_pos # 目标填充值，如 0x01
        
        # 构造伪造块 r 的已知后缀部分
        suffix = bytes([intermediate_a[k] ^ pad_val for k in range(byte_pos + 1, BLOCK_SIZE)])
        
        tasks = []
        for guess in range(256):
            # r 块 = [byte_pos个0] + [测试字节guess] + [已知后缀]
            r_block = bytes([0] * byte_pos + [guess]) + suffix
            # Payload = 前缀 (32字节) + r (16字节) + 目标C (16字节)
            # 注意：这里的 prefix_hex 长度如果是 64 Hex，则 Payload 总长为 96 Hex (3分组)
            payload = prefix_hex + r_block.hex() + target_c_hex
            tasks.append(check_padding(session, sem, payload))
            
        results = await asyncio.gather(*tasks)
        
        found_guess = None
        for guess, is_valid in enumerate(results):
            if is_valid:
                # 0x01 陷阱防御：扰动前一个字节确保填充确实是 0x01 [cite: 85]
                if pad_val == 1:
                    r_check = bytearray(bytes([0]*15 + [guess]))
                    r_check[14] ^= 0xFF
                    if not await check_padding(session, sem, prefix_hex + r_check.hex() + target_c_hex):
                        continue
                found_guess = guess
                break
        
        if found_guess is None:
            raise RuntimeError(f"Block {target_idx} Byte {byte_pos} 破解失败！请检查服务器状态。")
            
        intermediate_a[byte_pos] = found_guess ^ pad_val
        
        # 计算明文 P = a ^ C_prev 
        prev_c_byte = int(blocks[target_idx-1][byte_pos*2 : byte_pos*2+2], 16)
        plain_byte = intermediate_a[byte_pos] ^ prev_c_byte
        progress.update(1)
        progress.set_postfix_str(
            f"byte={byte_pos:02d} value={format_plain_byte(plain_byte)}"
        )

        if BYTE_DELAY > 0:
            await asyncio.sleep(BYTE_DELAY)

    if BLOCK_DELAY > 0:
        await asyncio.sleep(BLOCK_DELAY)

    return bytes([intermediate_a[k] ^ int(blocks[target_idx-1][k*2:k*2+2], 16) for k in range(BLOCK_SIZE)])

async def main():
    start_time = perf_counter()
    # 拆分密文 [IV, C1, C2, C3] [cite: 46]
    blocks = [TARGET_HEX[i:i+32] for i in range(0, len(TARGET_HEX), 32)]
    sem = asyncio.Semaphore(MAX_CONCURRENT)
    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT, limit_per_host=MAX_CONCURRENT)

    try:
        async with aiohttp.ClientSession(connector=connector) as session:
            all_plaintext = b""
            total_bytes = (len(blocks) - 1) * BLOCK_SIZE

            with tqdm(total=total_bytes, desc="Padding Oracle", unit="byte", dynamic_ncols=True) as progress:
                for i in range(1, len(blocks)):
                    block_plaintext = await solve_block(session, sem, blocks, i, progress)
                    all_plaintext += block_plaintext
                    progress.write(f"[+] 第 {i} 块结果: {block_plaintext!r}")

            print("\n" + "="*50)
            try:
                # 自动去除 PKCS#7 填充 [cite: 37]
                pad_len = all_plaintext[-1]
                if 1 <= pad_len <= 16:
                    all_plaintext = all_plaintext[:-pad_len]
                print("最终明文结果:", all_plaintext.decode("utf-8"))
            except:
                print("最终明文结果 (原始):", all_plaintext)
            print("="*50)
    finally:
        elapsed = perf_counter() - start_time
        print(f"总运行时间: {elapsed:.2f} 秒 ({elapsed / 60:.2f} 分钟)")

if __name__ == "__main__":
    asyncio.run(main())
