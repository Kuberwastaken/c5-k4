from fractions import Fraction
import time
N=200000
for K in (2,3,4,5,6):
    t0=time.time()
    sk=[0]*(N+1)
    for d in range(1,N+1):
        dk=d**K
        for m in range(d,N+1,d): sk[m]+=dk
    seen={}; coll=[]
    for n in range(1,N+1):
        num=sk[n]; den=n**K
        g=1
        # fract = (num mod den)/den in lowest terms
        r=num%den
        f=Fraction(r,den)
        if f in seen: coll.append((seen[f],n,f))
        else: seen[f]=n
    print("k=%d n<=%d : collisions %s  (%.1fs)"%(K,N,coll[:5],time.time()-t0))
