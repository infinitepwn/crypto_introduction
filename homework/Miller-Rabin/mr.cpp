#include <NTL/ZZ.h>
#include <iostream>
#include <chrono>
using namespace std;
using namespace NTL;
bool MillerRabin(ZZ n) {
    ZZ m = n - 1;
    int l = 0;
    while (m % 2 == 0) {
        m /= 2;
        l++;
    }
    ZZ a = RandomBnd(n-3) + 2;
    ZZ b = PowerMod(a, m, n);
    if (b == 1) {
        //printf("素数\n");
        return true;
    }
    for(int i = 0;i<l;i++) {
        if (b == n - 1) {
            //printf("素数\n");
            return true;
        }
        b = PowerMod(b, 2, n);
    }
    //printf("合数\n");
    return false;

}
void test(ZZ n) {
    auto start = chrono::high_resolution_clock::now();
    bool result = MillerRabin(n);
    auto end = chrono::high_resolution_clock::now();
    auto duration = chrono::duration_cast<chrono::milliseconds>(end - start);
    cout << "Miller-Rabin算法判定" << n << "为" << (result ? "素数" : "合数") << " 耗时: " << duration.count() << " ms" << endl;
}
int main() {
    printf("测试2048bit的素数\n");
    ZZ P = GenPrime_ZZ(2048);
    test(P);
    printf("测试2048bit的数\n");
    ZZ N = RandomBits_ZZ(2048);
    test(N);
    printf("测试4096bit的素数\n");
    ZZ P1 = GenPrime_ZZ(4096);
    test(P1);
    printf("测试4096bit的数\n");
    ZZ N1 = RandomBits_ZZ(4096);
    test(N1);
    return 0;
}