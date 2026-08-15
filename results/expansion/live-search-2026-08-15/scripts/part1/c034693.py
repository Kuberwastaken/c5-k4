import numpy as np
LIM=10_000_001
prime=np.ones(LIM,dtype=bool); prime[:2]=False
for i in range(2,int(LIM**0.5)+1):
    if prime[i]: prime[i*i::i]=False
NB=1_000_000
bad1=[];bad2=[];unres=0
for nv in range(1,NB+1):
    k=1;found=-1
    while nv*k+1<LIM:
        if prime[nv*k+1]: found=k;break
        k+=1
    if found<0: unres+=1; continue
    if nv>1 and found>=nv: bad1.append((nv,found))
    if found>=1+nv**0.75: bad2.append((nv,found,1+nv**0.75))
print("A034693 n=1..%d  unresolved:%d"%(NB,unres))
print(" exists_k violations (n>1, a(n)>=n):",bad1[:10],"count",len(bad1))
print(" exists_k_stronger violations (a(n)>=1+n^0.75):",bad2[:10],"count",len(bad2))
print(" a(1..30):",[next(k for k in range(1,10**6) if prime[nv*k+1]) for nv in range(1,31)])
