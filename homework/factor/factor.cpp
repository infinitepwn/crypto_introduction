#include <NTL/ZZ.h>
#include <iostream>
#include <chrono>
#include <vector>
#include <string>
using namespace std;
using namespace NTL;
bool MillerRabin(ZZ n) {
    if(n == 2) return true;
    if(n < 2 || n % 2 == 0) return false;
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
ZZ F(ZZ x,ZZ n) {
    ZZ c = RandomBnd(n-1) + 1;
    return (PowerMod(x, 2, n) + c) % n;
}
ZZ Pollard_rho(ZZ n) {
    if (n <= 1) return n;
    if (n % 2 == 0) return ZZ(2);
    if (MillerRabin(n)) return n;

    while (true) {
        ZZ x = RandomBnd(n - 2) + 2;
        ZZ y = x;
        ZZ p = ZZ(1);


        while (p == 1) {
            x = F(x, n);
            y = F(F(y, n), n);
            p = GCD(abs(x - y), n);
        }

        if (p != n) return p;

        // p == n：本轮失败，重新随机 x,y,c
    }
}
ZZ hex_to_ZZ(const std::string& s) {
    ZZ res(0);
    for (char c : s) {
        res *= 16;
        if ('0' <= c && c <= '9') res += c - '0';
        else if ('a' <= c && c <= 'f') res += c - 'a' + 10;
        else if ('A' <= c && c <= 'F') res += c - 'A' + 10;
    }
    return res;
}
string ZZ_to_hex(const ZZ& n) {
    if (n == 0) return "0";
    string res;
    ZZ temp = n;
    while (temp > 0) {
        int digit = to_int(temp % 16);
        char c = (digit < 10) ? ('0' + digit) : ('A' + digit - 10);
        res = c + res;
        temp /= 16;
    }
    return res;
}
void factor(ZZ n, vector<ZZ>& factors) {
    if (n <= 1) return;

    // 叶子节点：素数
    if (MillerRabin(n)) {
        factors.push_back(n);
        return;
    }

    // 内部节点：拆成左右儿子
    ZZ p = Pollard_rho(n);
    factor(p, factors);       // 左子树
    factor(n / p, factors);   // 右子树
}
int main() {
    string s = "47F09C8B318A52E3D335A7395CACD2B15E";
    ZZ n = hex_to_ZZ(s);
    vector<ZZ> factors;
    auto start = chrono::high_resolution_clock::now();
    factor(n, factors);
    auto end = chrono::high_resolution_clock::now();
    auto duration = chrono::duration_cast<chrono::milliseconds>(end - start);
    cout << "因子分解耗时: " << duration.count() << " ms" << endl;
    cout << "因子分解结果：";
    for (const auto& f : factors) {
        cout << ZZ_to_hex(f);
        if (&f != &factors.back()) cout << "*";
    }
    cout << endl;
    ZZ res = ZZ(1);
    for (const auto& f : factors) {
        res *= f;
    }
    cout << "验证：";
    if (res == n) cout << "分解成功！" << endl;
    return 0;
}