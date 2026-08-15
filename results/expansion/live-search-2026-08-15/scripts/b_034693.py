import time
import numpy as np
t0=time.time()
LIM=40_000_000
s=np.ones(LIM+1,dtype=bool); s[:2]=False
for i in range(2,int(LIM**0.5)+1):
    if s[i]: s[i*i::i]=False
print("sieve %.1fs"%(time.time()-t0))
bad1=[]; bad2=[]; maxn=0
n=1
while time.time()-t0<45:
    n+=1
    k=1
    while n*k+1<=LIM and not s[n*k+1]: k+=1
    if n*k+1>LIM: break
    maxn=n
    if k>=n: bad1.append((n,k))
    if k >= 1 + n**0.75: bad2.append((n,k,1+n**0.75))
print("checked n=2..%d"%maxn)
print("A034693 exists_k  (need k<n): violations:", bad1[:10], "count",len(bad1))
print("stronger (need k < 1+n^0.75): violations:", bad2[:10], "count",len(bad2))
