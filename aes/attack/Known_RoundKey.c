//如果已知轮密钥，恢复主密钥
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>
int main()
{
    uint8_t mainKey[16];
    //随机生成一个主密钥
    for (int i = 0; i < 16; i++)
    {
        mainKey[i] = rand() % 256;
    }
    printf("主密钥：");
    for (int i = 0; i < 16; i++)    {
        printf("%02x ", mainKey[i]);
    }
    printf("\n");
    //轮密钥生成
    uint8_t roundKey[11][16];
    memcpy(roundKey[0], mainKey, 16);
    for (int i = 1; i < 11; i++)
    {
        for (int j = 0; j < 16; j++)
        {
            roundKey[i][j] = roundKey[i - 1][j] ^ (
    return 0;
}