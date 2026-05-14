def delta(a,b,p):
    if 16*(4*a**3+27*b**2)%p==0:
        print("不是一个椭圆曲线")
        return 0
    else:
        print(16*(4*a**3+27*b**2)%p)
        print("是一个椭圆曲线")
        return 1
delta(0,6,13)
delta(2,8,13)
delta(2,0,13)
for i in range(13):
    print((i**3+6)%13)