import time, numpy as np
t0=time.time()
LIM=5_000_000
sig=np.load('sig.npy')
# usigma: multiplicative, usigma(p^a)=1+p^a  -> sieve via smallest prime factor
usig=np.ones(LIM+1,dtype=np.int64); usig[0]=0
spf=np.zeros(LIM+1,dtype=np.int32)
for i in range(2,int(LIM**0.5)+1):
    if spf[i]==0:
        spf[i*i::i]=np.where(spf[i*i::i]==0,i,spf[i*i::i])
spf[spf==0]=np.arange(LIM+1)[spf==0]
print("spf %.1fs"%(time.time()-t0))
us=np.ones(LIM+1,dtype=np.int64)
for n in range(2,LIM+1):
    p=int(spf[n]); m=n; pk=1
    while m%p==0: m//=p; pk*=p
    us[n]=us[m]*(1+pk)
print("usigma %.1fs"%(time.time()-t0))
idx=np.arange(LIM+1)
mask=(idx>0)&(sig[:LIM+1]==2*us)
mem=idx[mask]
print("A063880 members <= %d:"%LIM, mem[:30].tolist(), "count",len(mem))
print("violations of n%%216==108:", [int(v) for v in mem if v%216!=108][:20])
# primitive terms: no proper divisor in the set
S=set(int(v) for v in mem.tolist())
prim=[]
for v in sorted(S):
    ok=True
    for d in range(1,int(v**0.5)+1):
        if v%d==0:
            if d!=v and d in S: ok=False;break
            e=v//d
            if e!=v and e in S: ok=False;break
    if ok: prim.append(v)
print("primitive terms:", prim)
print("t=%.1f"%(time.time()-t0))
