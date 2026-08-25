#!/usr/bin/env python3
"""A115366 audit v2: counts by sieve array + isprime fallback; ratio bracket."""
import time
from sympy import isprime

def count(N):
    return sum(1 for k in range(1, N+1) if isprime(k*k+3*k+1))

def prime_count(N):
    from sympy import primepi
    return primepi(N)

for n, want in [(1,9),(2,50),(3,313)]:
    c=count(10**n)
    print(f"a({n})={c} expect {want} {'OK' if c==want else 'FAIL'}")

t0=time.time()
c5=count(10**5); pi5=int(prime_count(10**5))
print(f"n=5: a={c5} pi={pi5} ratio={c5/pi5:.4f} ({time.time()-t0:.1f}s)")
t0=time.time()
c6=count(10**6); pi6=int(prime_count(10**6))
print(f"n=6: a={c6} pi={pi6} ratio={c6/pi6:.4f} ({time.time()-t0:.1f}s)")
