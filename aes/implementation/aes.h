//aes的头文件
#include <stdio.h>
#include <string.h>
#include <stdint.h>
uint8_t gf_mult(uint8_t a, uint8_t b);
uint8_t gf_inverse(uint8_t a);
uint8_t* sub_bytes(uint8_t* state);
uint8_t* shift_rows(uint8_t* state);
uint8_t* mix_columns(uint8_t* state);
uint8_t* add_round_key(uint8_t* state, uint8_t* roundKey);
uint8_t affine_transform(uint8_t x);
void key_expansion(const uint8_t *key, uint8_t *roundKeys, int rounds);
uint8_t* encrypt(uint8_t* plaintext, uint8_t* roundKeys, int rounds);
void rot_word(uint8_t *word);
void sub_word(uint8_t *word);

