import sys, time
from collections import defaultdict

B = int(sys.argv[1]) if len(sys.argv)>1 else 200000
t0=time.time()

def spf_sieve(n):
    spf = list(range(n+1))
    for i in range(2, int(n**0.5)+1):
        if spf[i]==i:
            step=i
            spf[i*i:n+1:step] = [x for x in spf[i*i:n+1:step]]
            for j in range(i*i, n+1, i):
                if spf[j]==j: spf[j]=i
    return spf

spf = spf_sieve(B)
sup=[0]*(B+1)
for m in range(2,B+1):
    p=spf[m]
    sup[m]=sup[m//p]|p  # store as product of distinct primes? use set instead
# use actual sets lazily
def support(m):
    s=frozenset()
    while m>1:
        p=spf[m]; s=s|{p}
        while m%p==0: m//=p
    return s

KS = [(3,3),(4,3),(4,4),(5,3),(6,3),(10,3)]
supnum=[None]*(B+1)
def sup_of(m):
    if supnum[m] is None: supnum[m]=support(m)
    return supnum[m]

for (k1,k2) in KS:
    # index windows of length k2 by support
    idx=defaultdict(list)
    for s in range(2, B-k2+2):
        u=frozenset()
        ok=True
        for j in range(k2):
            u=u|sup_of(s+j)
        idx[u].append(s)
    sols=[]
    for n1 in range(0, B+1):
        lo=n1+k1
        if lo>B: break
        u=frozenset()
        for i in range(1,k1+1):
            if n1+i<=B and n1+i>1: u=u|sup_of(n1+i)
        for s2 in idx.get(u,[]):
            if s2>=lo:
                sols.append((n1,s2))
                if len(sols)>200: break
        if len(sols)>200: break
    print(f"k=({k1},{k2}): {len(sols)} sols <=B={B}: {sols[:15]}", flush=True)
print(f"elapsed {time.time()-t0:.1f}s")
