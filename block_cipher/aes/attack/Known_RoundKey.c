//如果已知轮密钥，恢复主密钥
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>
#include "../implementation/aes.h"
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
    uint8_t roundKey[176]; //11轮密钥，每轮16字节
    key_expansion(mainKey, roundKey, 10);
    //假设我们知道第5轮的轮密钥（roundKey[5*16]到roundKey[5*16+15]）
    uint8_t knownRoundKey[16];
    memcpy(knownRoundKey, roundKey + 5 * 16, 16);
    printf("已知的第5轮轮密钥：");
    for (int i = 0; i < 16; i++)    {
        printf("%02x ", knownRoundKey[i]);
    }
    printf("\n");
    //从已知的第5轮轮密钥反推主密钥
    uint8_t recoveredKey[16];
    //反向轮密钥扩展：从第5轮回退到第0
    for (int round = 5; round > 0; round--)
    {
        uint8_t temp[16];
        memcpy(temp, knownRoundKey, 16);
        
    }
    printf("恢复的主密钥：");
    for (int i = 0; i < 16; i++)    {
        printf("%02x ", recoveredKey[i]);
    }
    printf("\n");
    //验证恢复的主密钥是否正确
    if (memcmp(mainKey, recoveredKey, 16) == 0)
    {
        printf("成功恢复主密钥！\n");
    }
    else
    {
        printf("恢复失败，主密钥不匹配。\n");
    }
    return 0;

}