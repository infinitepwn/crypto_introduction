#include "aes.h"
#include <stdio.h>
#include <stdint.h>

// AES S-box的仿射变换（GF(2)上的矩阵乘法+加法）
// 正确的公式（来自AES标准）：
// 对于输入字节x，先求逆元inv，然后应用仿射变换：
// b_i = inv_i ⊕ inv_{(i+4) mod 8} ⊕ inv_{(i+5) mod 8} ⊕ 
//        inv_{(i+6) mod 8} ⊕ inv_{(i+7) mod 8} ⊕ c_i
// 其中c = 0x63
// 注意：这里i从0到7，b0是最低位(LSB)
static uint8_t affine_transform(uint8_t x) {
    uint8_t result = 0;
    
    // AES仿射变换矩阵（从LSB到MSB）
    for (int i = 0; i < 8; i++) {
        uint8_t bit = 0;
        // 公式：b_i = x_i ⊕ x_{(i+4) mod 8} ⊕ x_{(i+5) mod 8} ⊕ 
        //              x_{(i+6) mod 8} ⊕ x_{(i+7) mod 8} ⊕ c_i
        bit ^= (x >> ((i+0) % 8)) & 1;      // x_i
        bit ^= (x >> ((i+4) % 8)) & 1;      // x_{(i+4) mod 8}
        bit ^= (x >> ((i+5) % 8)) & 1;      // x_{(i+5) mod 8}
        bit ^= (x >> ((i+6) % 8)) & 1;      // x_{(i+6) mod 8}
        bit ^= (x >> ((i+7) % 8)) & 1;      // x_{(i+7) mod 8}
        bit ^= (0x63 >> i) & 1;             // 常数c的第i位
        
        result |= (bit << i);
    }
    
    return result;
}

int main()
{
    uint8_t sbox[256]={0};
    
    printf("生成AES S-box...\n");
    
    //生成s盒
    for (int i = 0; i < 256; i++)
    {
        uint8_t inv = gf_inverse(i); // 求逆元
        sbox[i] = affine_transform(inv); // 应用仿射变换
    }
    
    //打印s盒
    printf("S-box:\n");
    for (int i = 0; i < 256; i++)
    {
        printf("%02x ", sbox[i]);
        if ((i + 1) % 16 == 0)
        {
            printf("\n");
        }
    }
    
    // 验证几个关键值
    printf("\n关键值验证:\n");
    printf("S[0x00] = %02x (应该为63)\n", sbox[0x00]);
    printf("S[0x01] = %02x (应该为7c)\n", sbox[0x01]);
    printf("S[0x53] = %02x (应该为ed)\n", sbox[0x53]);
    printf("S[0xA5] = %02x (应该为06)\n", sbox[0xA5]);
    
    return 0;
}