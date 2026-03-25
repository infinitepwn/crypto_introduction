# S盒子6进4出
# alpha 2^6,beta 2^4
# X 0~2^6 - 1
# 不妨取S1
S1 = (14,4,13,1,2,15,11,8,3,10,6,12,5,9,0,7,0,15,7,4,14,2,13,1,10,6,12,11,9,5,3,8,4,1,14,8,13,6,2,11,15,12,9,7,3,10,5,0,15,12,8,2,4,9,1,7,5,11,3,14,10,0,6,13)

def S(X):
    # 6位长过S盒返回4位长
    X_2 = f"{X:06b}";
    row = int(X_2[0]+X_2[5],2)
    col = int(X_2[1:5],2)
    pos = row * 16 + col
    return S1[pos]


def creat_DDT():
    # 构建DDT
    DDT  = [0 for _ in range(1024)]
    for a in range(64):
        for x in range(64):
            b = S(x) ^ S(a^x)
            DDT[a*16+b] += 1
    return DDT

def calc_prob(DDT):
    # 根据输入的DDT统计总共多少种可能以及对应概率
    DDT_= sorted(list(set(DDT)),reverse = True)
    print(f"该S盒共{len(DDT_)}种概率传播,分别为:{DDT_}")

    Prob = []
    for i in DDT_:
        num = DDT.count(i)
        prob = f"{num / 1024:.6f}"
        Prob.append([i,num,prob])
    Prob.sort(key = lambda x : (x[1],x[0]),reverse = True) # 按出现概率从大到小排列
    for i in Prob:
        print(f"计数{i[0]}->概率{i[2]}(共{i[1]}种)")



def main():
    # 获取DDT并打印
    DDT = creat_DDT()
    for i in range(64):
        for j in range(16):
            pos = i * 16 + j
            print(DDT[pos],end=' ')
        print()

    
    # 计算概率
    calc_prob(DDT)


main()




