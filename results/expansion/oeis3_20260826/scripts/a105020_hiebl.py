#!/usr/bin/env python3
"""A105020 audit v3: Lean reading — for ALL i with a(i)=2n+1>=3 and a(i+n+1)=2n+3,
   interior must contain a semiprime (Omega=2)."""
import sys, time
sys.set_int_max_str_digits(100000)
from sympy import isprime

TERMS = 300000
arr=[]
c=0
while len(arr)<TERMS:
    # diagonal c: k=0..c, i=c-k, m=c+1 -> (c+1)^2-(c-k)^2 ; per Lean i decreasing c..0
    for k in range(0,c+1):
        i=c-k
        m=c+1
        arr.append(m*m-i*i)
    c+=1

# cross-check against b-file
ok=True
with open("/Users/kuber.mehta/Personal-Projects/c5-k4/results/expansion/oeis3_20260826/bfiles/b105020.txt") as f:
    cnt=0
    for line in f:
        line=line.strip()
        if not line or line.startswith("#"): continue
        idx,v=line.split(); idx=int(idx); v=int(v)
        if idx<len(arr):
            ok &= (arr[idx]==v); cnt+=1
print(f"b-file agreement on first {cnt} terms:", ok)

def is_semiprime(v):
    fs=[]; x=v; d=2
    while d*d<=x and len(fs)<3:
        while x%d==0:
            fs.append(d); x//=d
        d+=1
    if x>1: fs.append(x)
    return len(fs)==2

t0=time.time()
viol=[]; checked=0
for i,v in enumerate(arr[:TERMS-60]):
    if v<3 or v%2==0: continue
    n=(v-1)//2
    j=i+n+1
    if j>=TERMS: continue
    if arr[j]==v+2:
        checked+=1
        if not any(is_semiprime(arr[k]) for k in range(i+1,j)):
            viol.append((i,j,v))
print(f"applicable pairs checked: {checked} ({time.time()-t0:.1f}s)")
print("violations:", viol[:8] if viol else "NONE")
