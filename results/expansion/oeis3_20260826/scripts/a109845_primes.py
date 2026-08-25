#!/usr/bin/env python3
"""A109845 audit v2: verify polynomial==lcm recurrence on modest range; prime hunt to digit cap."""
import sys
import time
sys.set_int_max_str_digits(200000)
from math import gcd
from sympy import isprime

def gen_poly(N):
    out=[None,2,3]
    for n in range(3,N+1):
        prev=out[n-1]
        out.append(prev*prev-prev-1 if n%2==1 else prev*prev+prev+1)
    return out

N=24
p=gen_poly(N)
# lcm cross-check only up to n=16 (lcm explodes beyond)
L=2; ok=True
lcmvals=[None,2]
for n in range(2,17):
    t=L+1 if n%2==0 else L-1
    lcmvals.append(t)
    L=L*t//gcd(L,t)
ok = lcmvals[1:]==p[1:17]
print("lcm-recurrence == polynomial recurrence for n=1..16:", ok)

t0=time.time()
primes_at=[]
for n in range(1,N+1):
    d=len(str(p[n]))
    if d>4000:
        print(f"n={n}: {d} digits - beyond BPSW cap")
        break
    if isprime(p[n]): primes_at.append((n,d))
print(f"prime terms within cap: {[(n) for n,_ in primes_at]}")
for n,d in primes_at: print(f"  a({n}) prime ({d} digits)")
print(f"({time.time()-t0:.1f}s)")
