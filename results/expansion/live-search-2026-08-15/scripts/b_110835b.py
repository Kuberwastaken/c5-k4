import time, numpy as np
LIM=60_000_000
t0=time.time()
s=np.ones(LIM+1,dtype=bool); s[:2]=False
for i in range(2,int(LIM**0.5)+1):
    if s[i]: s[i*i::i]=False
print("sieve to %d done %.1fs"%(LIM,time.time()-t0))
def a(n):
    m=1
    while True:
        hi=n*(m+1)
        if hi>LIM: return None
        if not s[n*m:hi+1].any(): return m
        m+=1
bad=[]; n=0; last=0
while time.time()-t0<50:
    n+=1
    v=a(n)
    if v is None: break
    last=n
    if v<n: bad.append((n,v))
print("computed a(n) for n=1..%d  (%.1fs)"%(last,time.time()-t0))
print("violations of a(n)>=n:", bad[:20], "count",len(bad))
print("min slack a(n)-n over n<=%d:"%last, min((a(k)-k,k) for k in range(1,min(last,4000)+1)))
