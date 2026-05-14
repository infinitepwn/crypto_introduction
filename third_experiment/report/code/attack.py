import requests
from tqdm import *
IV = '46307250616464316e674f7261636c33'
C1 = '9ae0735429869542efc40dcdc3f4c170'
C2 = '649463f719c5ddf4ce8c6d1ef0e5d41a' 
C3 = 'c5d137629e3fe1340cfaad7e21d65d14'
cipher = [IV,C1,C2,C3]
#获取第i到j字节
def get_bytes(s,i,j):  
    if j < i:
        return ""
    else:
        return s[2*i:2*i+2*(j-i+1)]
#str转成列表
def get_list(s):
    lst = [s[i:i+2] for i in range(0, len(s), 2)]
    return lst
#列表转成str
def list_to_str(lst):
    return ''.join(f'{x & 0xff:02x}' for x in lst)
p = []
for idx in trange(2,-1,-1):
    y = cipher[idx+1]
    r = cipher[idx]
    #恢复只涉及最后两块，前面都设成0就行
    pfx = 64*'0'
    rb = int(get_bytes(r,15,15),16)
    #最后一块不用遍历rb（r15）
    if(idx != 2):
        for i in trange(256):
            c = pfx + r[:-2] + f"{i:02x}" + y
            url = f"http://10.102.33.67:8208/dec_2?data={c}"
            response = requests.get(url)
            if response.status_code == 200:
                rb = i
                break
        #修改r，前面的块这时候至少填充为1了
        r =  r[:-2] + f'{rb:02x}'
    padding_length = 1
    for j in trange(14,-1,-1):
        #修改rj,比如都加1
        rj = (int(get_bytes(r,j,j),16) + 1) & 0xff
        c = pfx + get_bytes(r,0,j-1) + f'{rj:02x}' + get_bytes(r,j+1,15) + y
        url = f"http://10.102.33.67:8208/dec_2?data={c}"
        response = requests.get(url)
        if response.status_code == 500:
            padding_length += 1
        else:
            print("填充长度是",padding_length)
            break
    #填充长度是k，那么把a_{16-k}一直到a15还原出来
    a = get_list(get_bytes(r,16-padding_length,15))
    a = [int(a[i],16) ^ padding_length for i in range(len(a))]
    for j in range(16-padding_length):
        #修改r，使得填充变成padding_length+1
        rr = [a[i] ^ (padding_length+1) for i in range((len(a)))]
        #搜索r_{j-1},恢复a_{j-1}
        rj_1 = 0
        for i in trange(256):
            r_ = get_bytes(r,0,14-padding_length)+f'{i:02x}'+list_to_str(rr)
            c = pfx + r_ + y
            url = f"http://10.102.33.67:8208/dec_2?data={c}"
            response = requests.get(url)
            if response.status_code == 200:
                rj_1 = i
                break
        a = [rj_1 ^ (padding_length+1)] + a
        padding_length +=1 
    r_n = get_list(r)
    p  = [int(r_n[i],16) ^ a[i] for i in range(len(a))] + p
for i in range(len(p)):
    print(chr(p[i]),end='')