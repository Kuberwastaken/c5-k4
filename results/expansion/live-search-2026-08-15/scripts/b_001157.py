import time
from fractions import Fraction
t0=time.time()
import numpy as np
LIM=300000
# sigma_k(n)/n^k  as reduced fraction; collision search
for kk in (2,3,4):
    sk=np.zeros(LIM+1,dtype=object)
    for d in range(1,LIM+1):
        v=d**kk
        for m in range(d,LIM+1,d): sk[m]+=v
    seen={}; coll=[]
    for n in range(1,LIM+1):
        f=Fraction(int(sk[n]), n**kk)
        fr=f - (f.numerator//f.denominator)
        if fr in seen: coll.append((seen[fr],n,fr))
        else: seen[fr]=n
        if time.time()-t0>40: break
    print("k=%d: scanned n<=%d, fractional-part collisions:"%(kk,n), coll[:5], "count",len(coll))
    if time.time()-t0>40: break
