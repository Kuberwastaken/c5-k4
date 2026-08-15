import numpy as np
LIM=6_000_001
pr=np.ones(LIM,dtype=bool); pr[:2]=False
for i in range(2,int(LIM**0.5)+1):
    if pr[i]: pr[i*i::i]=False
pi=np.cumsum(pr).astype(np.int64)   # pi[x] = #primes <= x
M=np.arange(1,LIM//5)
bad=np.flatnonzero(pi[5*M]>M)+1
print("A100478 boundedness lemma: M with pi(5M) > M, M < %d :"%(LIM//5), bad.tolist()[-10:], " max such M =",int(bad.max()))
print("  => pi(5M) <= M for all M >= %d (checked to %d; Rosser-Schoenfeld pi(x)<1.26x/ln x gives it for M>=109)"%(int(bad.max())+1,LIM//5))
# orbit test on many starting 5-tuples
import itertools, random
random.seed(1)
def orbit(v,steps=4000):
    s=list(v); seen={}; 
    for t in range(steps):
        key=tuple(s[-5:])
        if key in seen: return ('periodic',t-seen[key],max(s))
        seen[key]=t
        nxt=int(pi[sum(s[-5:])])
        s.append(nxt)
    return ('nonterminating',None,max(s))
tests=[(1,1,1,1,1),(2,2,2,2,2),(1,2,3,4,5),(100,1,1,1,1),(1000,2000,3,4,5),(66,66,66,66,66),(70,70,70,70,70),(5,7,11,13,17)]
tests+= [tuple(random.randint(1,5000) for _ in range(5)) for _ in range(40)]
res=[orbit(v) for v in tests]
print("  all orbits eventually periodic:",all(r[0]=='periodic' for r in res))
from collections import Counter
print("  cycle lengths seen:",Counter(r[1] for r in res))
print("  A100478 a(1..20) from v=(1,1,1,1,1):")
s=[1,1,1,1,1]
for _ in range(20): s.append(int(pi[sum(s[-5:])]))
print("   ",s[:25])
print("  OEIS head: [1,1,1,1,1,3,4,4,6,7,9,10,11,14,15,17,19,21,23,24,27]")
