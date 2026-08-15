import numpy as np
LIM=30_000_000
prime=np.ones(LIM,dtype=bool); prime[:2]=False
for i in range(2,int(LIM**0.5)+1):
    if prime[i]: prime[i*i::i]=False
pc=np.cumsum(prime).astype(np.int64)
def cnt(lo,hi): return int(pc[hi]-(pc[lo-1] if lo>0 else 0))
res={};bad=[]
for n in range(1,400):
    m=1
    while n*(m+1)<LIM:
        if cnt(n*m,n*(m+1))==0: res[n]=m;break
        m+=1
    if n in res and res[n]<n: bad.append((n,res[n]))
ks=sorted(res)
print("resolved n:",len(ks),"max resolved n:",max(ks))
print("a(1..30):",[res[n] for n in range(1,31)])
print("OEIS head: [8,4,8,6,18,15,17,25,13,20,29,44,87,81,35,83,79,74,70,67,118,330,58,223,172,229,179,471,292,360]")
print("match:",[res[n] for n in range(1,31)]==[8,4,8,6,18,15,17,25,13,20,29,44,87,81,35,83,79,74,70,67,118,330,58,223,172,229,179,471,292,360])
print("violations a(n)<n:",bad,"count",len(bad))
print("min slack a(n)-n over resolved:",min(res[n]-n for n in ks),"at n=",min(ks,key=lambda n:res[n]-n))
