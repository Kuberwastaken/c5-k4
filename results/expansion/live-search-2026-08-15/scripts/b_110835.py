import time
import numpy as np
LIM=4_000_000
s=np.ones(LIM+1,dtype=bool); s[:2]=False
for i in range(2,int(LIM**0.5)+1):
    if s[i]: s[i*i::i]=False
pref=np.cumsum(s.astype(np.int64))   # pref[x] = pi(x)
def has_prime(lo,hi):
    if hi>LIM: return None
    lo=max(lo,0)
    return (pref[hi] - (pref[lo-1] if lo>=1 else 0))>0
def a(n):
    m=1
    while True:
        r=has_prime(n*m, n*(m+1))
        if r is None: return None
        if not r: return m
        m+=1
t0=time.time(); vals={}; bad=[]
n=1
while time.time()-t0<40:
    v=a(n)
    if v is None: break
    vals[n]=v
    if v<n: bad.append((n,v))
    n+=1
print("computed a(n) for n=1..%d (%.1fs)"%(n-1,time.time()-t0))
print("a(1..25):",[vals[k] for k in range(1,26)])
print("violations of Sierpinski a(n)>=n:", bad[:20], " count", len(bad))
print("tight cases a(n)==n:", [(k,v) for k,v in vals.items() if v==k][:20])
