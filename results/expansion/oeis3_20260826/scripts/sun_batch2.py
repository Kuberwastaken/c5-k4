#!/usr/bin/env python3
"""Sun batch 2 v2 (fixed bounds)."""
import time
from math import isqrt

def two_squares_upto(n):
    S=set(); a=0
    while a*a<=n:
        b=0; aa=a*a
        while aa+b*b<=n:
            S.add(aa+b*b); b+=1
        a+=1
    return S

t0=time.time()
print("== 303656 fixed: n>1 = a^2+b^2+3^c+5^d, n<=5000 ==")
N=5000
TS=two_squares_upto(N)
p35=set()
c=0
while 3**c<=N:
    d=0
    while 3**c+5**d<=N:
        p35.add(3**c+5**d); d+=1
    c+=1
missing=[n for n in range(2,N+1) if not any((n-q) in TS for q in p35 if q<=n)]
print("missing:", missing if missing else "NONE", f"({time.time()-t0:.1f}s)")

t0=time.time()
print("== 308734 fixed: n<=8000 ==")
N=8000
def gen_23(N):
    v=set(); a=0
    while 4**a<=N:
        b=0; va=4**a
        while va*3**(2*b)<=N:
            v.add(va*3**(2*b)); b+=1
        a+=1
    return sorted(v)
g1=gen_23(N)
g2=[]; a=0
while 4**a<=N:
    b=0; va=4**a
    while va*5**(2*b)<=N:
        g2.append(va*5**(2*b)); b+=1
    a+=1
G12=set(u+v for u in g1 for v in g2 if u+v<=N)
TS2=two_squares_upto(N)
missing=[n for n in range(2,N+1) if not any((n-s) in TS2 for s in G12 if s<=n)]
print("missing:", missing if missing else "NONE", f"({time.time()-t0:.1f}s)")

t0=time.time()
print("== 281976 fixed: n<=300 ==")
missing=[]
for n in range(0,301):
    found=False
    for x in range(isqrt(n)+1):
        if isqrt(x)**2!=x: continue
        r1=n-x*x
        if r1<0: continue
        for y in range(0,isqrt(r1)+1):
            if isqrt(x+24*y)**2 != x+24*y: continue
            r2=r1-y*y
            if r2<0: continue
            for z in range(0,isqrt(r2)+1):
                w2=r2-z*z; w=isqrt(w2)
                if w*w==w2 and z<=w:
                    found=True; break
            if found: break
        if found: break
    if not found: missing.append(n)
print("missing:", missing if missing else "NONE", f"({time.time()-t0:.1f}s)")
