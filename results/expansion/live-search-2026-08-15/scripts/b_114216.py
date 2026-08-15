import time, numpy as np
t0=time.time()
NP=2_000_000   # number of primes needed
LIM=33_000_000
s=np.ones(LIM+1,dtype=bool); s[:2]=False
for i in range(2,int(LIM**0.5)+1):
    if s[i]: s[i*i::i]=False
pr=np.flatnonzero(s)
print("primes available:",len(pr)," up to",pr[-1]," (%.1fs)"%(time.time()-t0))
a=0; ones=[]
N=min(len(pr), 2_000_000)
for i in range(N):
    v=a+int(pr[i])
    v>>= (v & -v).bit_length()-1
    a=v
    if a==1: ones.append(i+1)
print("n with a(n)=1 (n<=%d):"%N, ones)
print("max n with a(n)=1:", ones[-1] if ones else None)
print("t=%.1fs"%(time.time()-t0))
