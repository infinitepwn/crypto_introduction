//aes的头文件
#include <stdio.h>
#include <string.h>
#include <stdint.h>
//使用Eculid算法求逆元
//原理：对于一个数a和模多项式m，如果存在一个数x，使得a*x ≡ 1 (mod m)
//也就是a*x = 1 + k*m，为了求解这个方程，我们可以使用扩展欧几里得算法来找到x和k的值
// ax-km = 1,相当于求a，m的最大公因数时的系数x和k
uint8_t gf_mult(uint8_t a, uint8_t b);
uint8_t gf_inverse(uint8_t a);
