#!/usr/bin/env python3
"""A037274 audit v2: skip 49 (famously open); bounded trajectories elsewhere."""
import time
from sympy import factorint, isprime

def splice(n):
    s = "".join(str(p)*e for p,e in sorted(factorint(n).items()))
    return int(s)

def home_prime(n, steps=60, digcap=150):
    cur=n; k=0
    while k<steps:
        if isprime(cur): return k
        if len(str(cur))>digcap: return None
        cur=splice(cur); k+=1
    return None

t0=time.time()
unresolved=[]
for n in range(2,50):
    if n==49:
        unresolved.append((n,"known-open")); continue
    r=home_prime(n)
    if r is None: unresolved.append((n,"cap"))
print(f"n=2..49 done ({time.time()-t0:.1f}s)")
print("unresolved:", unresolved)

cur=25; traj=[25]
for _ in range(3):
    cur=splice(cur); traj.append(cur)
print("25 trajectory:", traj, "expect [25,55,511,773]")
