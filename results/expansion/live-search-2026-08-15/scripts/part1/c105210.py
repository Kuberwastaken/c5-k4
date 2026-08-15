import numpy as np
LIM=20_000_000
spf=np.zeros(LIM,dtype=np.int32)
for i in range(2,LIM):
    if spf[i]==0:
        spf[i::i]=np.where(spf[i::i]==0,i,spf[i::i])
def distinct_pf(n):
    s=set()
    while n>1:
        p=int(spf[n]); s.add(p)
        while n%p==0: n//=p
    return s
def nxt(n):
    return n+1+sum(p for p in distinct_pf(n) if p<n) if n>1 else n+1
starts=[1,393,412,668,932]
sets={}
for k in starts:
    S=set(); x=k
    while x<LIM:
        S.add(x); x=nxt(x)
    sets[k]=S
    print("start %d: %d terms, first 12 %s, last %d"%(k,len(S),sorted(S)[:12],max(S)))
print("--- pairwise intersections (all terms < %d) ---"%LIM)
bad=0
for i,j in [(a,b) for ai,a in enumerate(starts) for b in starts[ai+1:]]:
    inter=sets[i]&sets[j]
    if inter: bad+=1; print("  COLLISION",i,j,sorted(inter)[:10])
    else: print("  %d vs %d : disjoint"%(i,j))
print("collisions:",bad)
