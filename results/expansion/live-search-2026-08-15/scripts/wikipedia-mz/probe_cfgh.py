import time, sys, numpy as np
sys.path.insert(0,'/tmp/claude-1000/-Users-kuber-mehta-Projects-scratch/21f73cfa-6e97-457f-8bb8-ae31d911cc43/scratchpad/mz')
from util import sieve_primes, is_prime
t0=time.time()
def tetra(n): return n*(n+1)*(n+2)//6

# ---- C: is 343867 a sum of 4 tetrahedral numbers?
def sum4(N):
    T=[]; n=0
    while tetra(n)<=N: T.append(tetra(n)); n+=1
    Ts=set(T)
    for a in T:
        for b in T:
            if a+b>N: break
            for c in T:
                s=a+b+c
                if s>N: break
                if N-s in Ts: return (a,b,c,N-s)
    return None
print("C: 343867 sum of 4 tetra ->", sum4(343867))
for x in (343866,343868,17,27,100,343867-1):
    print("   control",x,sum4(x))
print("C elapsed",round(time.time()-t0,1))

# ---- G: Pollock
LIM=3*10**6
T2=[]; n=0
while tetra(n)<=LIM: T2.append(tetra(n)); n+=1
r=np.zeros(LIM+1,dtype=bool); r[0]=True
reach=[r]
for k in range(5):
    prev=reach[-1]; out=prev.copy()
    for t in T2:
        if t==0: continue
        out[t:] |= prev[:LIM+1-t]
    reach.append(out)
bad5=np.nonzero(~reach[5])[0]; bad4=np.nonzero(~reach[4])[0]
print("G: not sum of <=5 tetra, N<=%d: %s"%(LIM,bad5[:10]))
print("G: not sum of <=4 tetra: count=%d max=%s"%(len(bad4), bad4[-1] if len(bad4) else None))
print("G: is 343867 in bad4?", 343867 in set(bad4.tolist()))
print("G elapsed",round(time.time()-t0,1))

# ---- F: Oppermann sanity
LIMX=300000
pr=sieve_primes(LIMX*(LIMX+1)//1 if False else 0) if False else None
# use segmented check with is_prime scanning
bad=[]
for x in range(2,50001):
    a=x*(x-1); b=x*x; c=x*(x+1)
    found=False
    for m in range(a+1,b):
        if is_prime(m): found=True; break
    if not found: bad.append((x,'i'))
    found=False
    for m in range(b+1,c):
        if is_prime(m): found=True; break
    if not found: bad.append((x,'ii'))
    if bad: break
print("F: Oppermann failures 2<=x<=50000:", bad)
print("F elapsed",round(time.time()-t0,1))

# ---- H: Wall-Sun-Sun
def lucas_mod(n,m):
    def fp(k):
        if k==0: return (0,1)
        a,b=fp(k>>1)
        c=a*((2*b-a)%m)%m
        d=(a*a+b*b)%m
        return (d,(c+d)%m) if k&1 else (c,d)
    f,g=fp(n)
    return (2*g-f)%m
P=sieve_primes(2*10**6)
hits=[p for p in P.tolist() if lucas_mod(p,p*p)==1%(p*p)]
print("H: WSS primes p<2e6:",hits)
ctl=[p for p in P.tolist()[:500] if lucas_mod(p,p)!=1%p]
print("H control L_p!=1 mod p:",ctl)
print("H elapsed",round(time.time()-t0,1))
