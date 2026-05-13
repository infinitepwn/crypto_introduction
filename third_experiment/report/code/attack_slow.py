import requests
from tqdm import *
ciphertext = '''46307250616464316e674f7261636c339ae0735429869542ef
                c40dcdc3f4c170649463f719c5ddf4ce8c6d1ef0e5d
                41ac5d137629e3fe1340cfaad7e21d65d14'''
cipher = [ciphertext[:32],ciphertext[32:64],ciphertext[64:96],ciphertext[96:128]]
def get_bytes(s,i,j):
    if j < i:
        return ""
    else:
        return s[2*i:2*i+2*(j-i+1)]
def get_list(s):
    lst = [s[i:i+2] for i in range(0, len(s), 2)]
    return lst
def list_to_str(lst):
    return ''.join(f'{x & 0xff:02x}' for x in lst)
p = []
for idx in range(2,-1,-1):
    y = cipher[idx+1]
    r = cipher[idx]
    pfx = 64*'0'
    rb = 0
    for i in trange(256):
        c = pfx + r[:-2] + f"{i:02x}" + y
        url = f"http://10.102.33.67:8208/dec_2?data={c}"
        response = requests.get(url)
        if 'HTTP 200' in response.text:
            rb = i
            print(rb)
            break
    padding_length = 1
    if(idx != 2):
        r =  r[:-2] + f'{rb:02x}'
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
        #搜搜r_{15-k},恢复a_{15-k}
        rj_1 = 0
        for i in trange(256):
            r_ = get_bytes(r,0,14-padding_length)+f'{i:02x}'+list_to_str(rr)
            c = pfx + r_ + y
            url = f"http://10.102.33.67:8208/dec_2?data={c}"
            response = requests.get(url)
            if 'HTTP 200' in response.text:
                rj_1 = i
                break
        a = [rj_1 ^ (padding_length+1)] + a
        padding_length +=1 
    r_n = get_list(r)
    p  = [int(r_n[i],16) ^ a[i] for i in range(len(a))] + p
for i in range(len(p)):
    print(chr(p[i]),end='')