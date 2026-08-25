#!/usr/bin/env python3
"""A100475 audit v4: bounded classification; escapes recorded honestly."""
import time
lim = 9000000
is_c = bytearray(lim + 1)
for i in range(2, int(lim ** 0.5) + 1):
    if not is_c[i]:
        is_c[i*i::i] = b"\x01" * len(is_c[i*i::i])
primes = [i for i in range(2, lim + 1) if not is_c[i]]
NP = len(primes)
print("primes tabulated:", NP)

def rev(n): return int(str(n)[::-1])
def nxt(k):
    if k == 0: return 0
    if k > NP: return None
    return rev(primes[k - 1])

seq=[1]
cur=1
for _ in range(14):
    cur=nxt(cur)
    if cur is None: break
    seq.append(cur)
print("main head (within table):", seq)
try:
    bf={}
    for line in open("/Users/kuber.mehta/Personal-Projects/c5-k4/results/expansion/oeis3_20260826/bfiles/b100475.txt"):
        line=line.strip()
        if not line or line.startswith("#"): continue
        i,v=line.split(); bf[int(i)]=int(v)
    print("b-file matches head:", all(bf.get(i)==v for i,v in enumerate(seq)))
except FileNotFoundError:
    print("no bfile")

def traj(x, cap=300):
    seen={}; cur=x; step=0
    while cur!=0 and step<cap:
        if cur in seen: return ("loop", step-seen[cur], cur)
        seen[cur]=step
        c=nxt(cur)
        if c is None: return ("beyond-table", step, cur)
        cur=c; step+=1
    return ("cap-or-zero", step, cur)

t0=time.time(); loops=0; esc=[]; res={}
starts=list(range(0,120))
for x in starts:
    r=traj(x); res[x]=r
    if r[0]=="loop": loops+=1
    elif r[0]=="beyond-table": esc.append((x,r[2]))
print(f"{time.time()-t0:.1f}s; entered loop: {loops}/{len(starts)}")
print("escaped beyond table (start,index-at-exit):", esc[:10])
cyc={}
for x,(k,l,c) in res.items():
    if k=="loop": cyc[(l,c)]=cyc.get((l,c),0)+1
print("cycle shapes (len,entry,count):", cyc)
