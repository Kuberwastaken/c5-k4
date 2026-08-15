import time
from nt import factorint
t0=time.time()
def nxt(n):
    if n<2: return n+1
    return n+1+sum(p for p in factorint(n) if p<n)
def seq(k, cap=10**9, tmax=8):
    s=set(); x=k; t=time.time()
    while x<=cap and time.time()-t<tmax:
        s.add(x); x=nxt(x)
    return s, x
starts=[1,393,412,668,932]
sets={}
for k in starts:
    s,last=seq(k)
    sets[k]=s
    print("start %d: %d terms, reached %d (%.1fs)"%(k,len(s),last,time.time()-t0))
import itertools
for j,k in itertools.combinations(starts,2):
    inter=sets[j]&sets[k]
    print("  %d ^ %d : %s"%(j,k, sorted(inter)[:5] if inter else "EMPTY"))
