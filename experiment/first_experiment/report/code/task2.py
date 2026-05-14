import random

# AES指定加密轮数实现


class AES:
    def __init__(self,m,main_k,rounds = 10):
        self.m = self._bytes2matrix(m)
        # 转换为4*4分组,类似转置
        self.m = [list(x) for x in zip(*self.m)]

        self.main_k = main_k # 主密钥

        self.rounds = rounds # 操作轮数

        self.mixMatrix = [[2,3,1,1],[1,2,3,1],[1,1,2,3],[3,1,1,2]] # 列混合所用矩阵

        self.sbox = (
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
        

    def subbytes(self):
        # 每一位共8bit,前4bit指示行号,后4bit指示列号
        for i in range(4):
            for j in range(4):
                curr_m = f"{self.m[i][j]:08b}" # 转换为8位二进制
                row = int(curr_m[:4],2)
                col = int(curr_m[4:],2)
                self.m[i][j] = self.sbox[row * 16 + col]
    
    def shiftrows(self):
        # 行移位
        for i in range(4):
            # 在第row行左移row个位置
            self.m[i] = self.m[i][i:] + self.m[i][:i]
    
    def gmul(self,a,b):
        # 实现a,b在有限域上的乘法
        p = 0
        for _ in range(8):
            if b & 1:
                p^=a
            hi_bit = a & 0x80
            a <<= 1
            if hi_bit:
                a^= 0x1b
            a &= 0xff
            b >>= 1
        return p

    def _mix_single_col(self,col):
        # x为要混合的列,返回混合后的列
        return [
        self.gmul(2,col[0]) ^ self.gmul(3,col[1]) ^ col[2] ^ col[1],
        col[0] ^ self.gmul(2,col[1]) ^ self.gmul(3,col[2]) ^ col[3],
        col[0] ^ col[1] ^ self.gmul(2,col[2]) ^ self.gmul(3,col[3]),
        self.gmul(3,col[0]) ^ col[1] ^ col[2] ^ self.gmul(2,col[3])    
        ]

    def mixcolumns(self):
        # 列混合
        for i in range(4):
            curr_colum = [self.m[x][i] for x in range(4)] # 第i列
            mix_curr_colum = self._mix_single_col(curr_colum)
            # 返回本列
            self.m[0][i],self.m[1][i],self.m[2][i],self.m[3][i] = mix_curr_colum
        
    def addroundkeys(self,k):
        # 轮密钥相加,即逐位异或
        for i in range(4):
            for j in range(4):
                self.m[i][j] = self.m[i][j] ^ k[i][j]
    

    def _bytes2matrix(self,text):
        # 16bytes->4*4matrix
        return [list(text[i:i+4]) for i in range(0,len(text),4)]

    def _sub_word(self,word):
        # 按字节过S盒
        return [self.sbox[b] for b in word]


    def _rot_word(self,word):
        # 左移一位 
        return word[1:]+word[:1]   


    def expand_key(self):
        # 根据主密钥进行密钥拓展,生成轮密钥
        # 本处简易128位AES NR = self.rounds,Nk = 4
        main_k = self.main_k
        r_con = (
            0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40,
            0x80, 0x1B, 0x36)
        
        Nk = 4
        Nb = 4
        Nr = self.rounds
        words = self._bytes2matrix(main_k)
        words = [list(w) for w in words]

        # 拓展,Nr轮加密需要将主密钥拓展为Nr+1个128bit轮密钥
        for i in range(Nk,Nb * (Nr+1)):
            temp = words[i-1][:]
            
            if i % Nk == 0:
                # w[i] = subWord(rotWord(w[i-1])) ^ rcon[i] ^ w[4i-4]
                # rotWord:
                temp = self._rot_word(temp)
                # subWord:
                temp = self._sub_word(temp)
                # Rcon
                temp[0] ^= r_con[ i // Nk]
            
            # XOR
            new_word = [a ^ b for a,b in zip(words[i - Nk],temp)]
            words.append(new_word)
        
        # 分组为轮密钥并返回
        round_keys = [words[4*i : 4*(i+1)] for i in range(Nr+1)]
        return round_keys
    
    def encrypt(self,is_MC = True):
        # is_MC 对比是否执行列混合
        # 实现加密
        K = self.expand_key()# 实现密钥拓展
        # 先密钥相加
        self.addroundkeys(K[0])

        # 进行轮加密,这里根据实验加密轮数,每轮四个步骤都执行
        for i in range(1,self.rounds+1):
            self.subbytes() # 过S盒
            self.shiftrows() # 行移位
            if is_MC:
                self.mixcolumns() # 列混合
            self.addroundkeys(K[i]) # 轮密钥相加
        
        return self.m # 此时为加密后的密文
    

def generate_plaintext(fixed_bytes,active_index):
    # fixed_bytes:长度固定的list
    # active_index : 遍历位
    plaintext = []
    for i in range(256):
        pt = fixed_bytes[:]
        pt[active_index] = i
        plaintext.append(bytes(pt))

    return plaintext

def encrypt_all(plaintext,key,rounds,is_MC = True):
    # 所有明文做加密
    ciphertexts = []
    for pt in plaintext:
        aes = AES(pt,key,rounds = rounds)
        ct_matrix = aes.encrypt(is_MC=is_MC)

        # 转回16字节
        ct = []
        for col in zip(*ct_matrix):
            ct.extend(col)
        ciphertexts.append(ct)
    return ciphertexts

def xor_all(ciphertexts):
    result = [0] * 16
    for ct in ciphertexts:
        for i in range(16):
            result[i] ^= ct[i]
        
    return result

def main(rounds = 3,is_MC = True):
    print("="*50)
    p0 = [
            0x10, 0x22, 0x34, 0x46,
            0x58, 0x6A, 0x7C, 0x8E,
            0x91, 0xA3, 0xB5, 0xC7,
            0xD9, 0xEB, 0xFD, 0x0F
        ]
    p1 = [
            0x01, 0x13, 0x25, 0x37,
            0x49, 0x5B, 0x6D, 0x7F,
            0x80, 0x92, 0xA4, 0xB6,
            0xC8, 0xDA, 0xEC, 0xFE
        ]
    p2 = [
            0xFF, 0xEE, 0xDD, 0xCC,
            0xBB, 0xAA, 0x99, 0x88,
            0x77, 0x66, 0x55, 0x44,
            0x33, 0x22, 0x11, 0x00
        ]
    fixed_groups = [p0,p1,p2] # 三组

    Makter_Key = "0xabf266f7a189b08e5db4a56ea585ae0f" 
    key = bytes.fromhex(Makter_Key.replace("0x",""))
    print(f"加密密钥为{key}")
    idx = 4 # 移动位,即(1,0)
    print(f"加密轮数{rounds},是否MC变换{is_MC}")
    for i in range(len(fixed_groups)):
        plaintexts = generate_plaintext(fixed_groups[i],idx)
        ct = encrypt_all(plaintexts,key,rounds = rounds,is_MC= is_MC)
        xor = xor_all(ct)
        print(f"第{i+1}组异或结果:{xor}")

if __name__ == "__main__":
    # main(3,True)
    # main(4,True)
    for i in range(3,11):
        main(i,False)

    







        

