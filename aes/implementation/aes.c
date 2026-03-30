#include "aes.h"
uint8_t gf_mult(uint8_t a, uint8_t b) {
    uint8_t p = 0; // 结果
    for (int i = 0; i < 8; i++) {
        if (b & 1) { // 如果b的最低位是1
            p ^= a; // 将a加到结果中
        }
        uint8_t hi_bit = a & 0x80; // 保存a的最高位
        a <<= 1; // a左移一位
        if (hi_bit) { // 如果a的最高位是1
            a ^= 0x1b; // 将a与0x1b进行异或（相当于模多项式）
        }
        b >>= 1; // b右移一位
    }
    return p;
}
// 快速幂算法计算 a^b 在 GF(2^8) 中
static uint8_t gf_pow(uint8_t a, int b) {
    uint8_t result = 1;
    while (b > 0) {
        if (b & 1) {
            result = gf_mult(result, a);
        }
        a = gf_mult(a, a);
        b >>= 1;
    }
    return result;
}

// GF(2^8) 上的乘法逆元
// 原理：在 GF(2^8) 中，非零元素 a 的乘法逆元是 a^(254)
// 因为群的阶是 255 (2^8 - 1)，所以 a * a^(254) = a^(255) = 1
uint8_t gf_inverse(uint8_t a) {
    if (a == 0) return 0; // 0没有逆元，AES规定返回0
    return gf_pow(a, 254); // a^(254)
}