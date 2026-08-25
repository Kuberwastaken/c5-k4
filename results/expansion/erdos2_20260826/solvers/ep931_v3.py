import sys, time
from collections import defaultdict

def spf_sieve(n):
    spf=list(range(n+1))
    for i in range(2,int(n**0.5)+1):
        if spf[i]==i:
            for j in range(i*i,n+1,i):
                if spf[j]==j: spf[j]=i
    return spf

def run(B, ks):
    t0=time.time()
    spf=spf_sieve(B+2)
    cache=[None]*(B+2)
    def sup_of(m):
        if cache[m] is None:
            s=frozenset(); x=m
            while x>1:
                p=spf[x]; s=s|{p}
                while x%p==0: x//=p
            cache[m]=s
        return cache[m]
    out={}
    for (k1,k2) in ks:
        idx=defaultdict(list)
        for s in range(2, B-k2+2):
            u=frozenset()
            for j in range(k2): u=u|sup_of(s+j)
            idx[u].append(s)
        sols=[]
        for n1 in range(0,B+1):
            lo=n1+k1
            if lo+k2>B: break
            u=frozenset()
            for i in range(1,k1+1):
                m=n1+i
                if m>1: u=u|sup_of(m)
            for s2 in idx.get(u,[]):
                if s2-1>=lo: sols.append((n1,s2-1))
        out[(k1,k2)]=sols
    print(f"B={B}: elapsed {time.time()-t0:.1f}s")
    for kk,v in out.items():
        print(f"  k={kk}: {len(v)} sols; last5={[x for x in v[-5:]]}")
    return out

ks=[(3,3),(4,4)]
o1=run(20000, ks)
o2=run(100000, ks)
o3=run(400000, ks)
print("ratio (3,3):", len(o1[(3,3)]), len(o2[(3,3)]), len(o3[(3,3)]))
print("ratio (4,4):", len(o1[(4,4)]), len(o2[(4,4)]), len(o3[(4,4)]))
# largest solutions found
print("max n2 seen (3,3):", max(x[1] for x in o3[(3,3)]))
