#!/usr/bin/env python3
"""A100800 audit: iterate f(n)=n+digitsum(n) until multiple of n; a(n)=first such value.
   Lean conjecture: never zero (always succeeds)."""
import time

def digitsum(x):
    s = 0
    while x:
        x, r = divmod(x, 10)
        s += r
    return s

def first_multiple_hit(n, cap=200000):
    m = n
    for _ in range(cap):
        m = m + digitsum(m)
        if m % n == 0:
            return m
    return None  # cap hit (not a disproof: iteration is strictly increasing)

print("== head vs Lean tests ==")
for n, want in [(1,2),(2,4),(3,6),(4,8),(5,10)]:
    got = first_multiple_hit(n)
    print(f"a({n})={got} expect {want} {'OK' if got==want else 'FAIL'}")

t0 = time.time()
fails = []
slow = {}
N = 5000
for n in range(1, N + 1):
    if time.time() - t0 > 55:
        N = n
        break
    r = first_multiple_hit(n)
    if r is None:
        fails.append(n)
print(f"scanned n<= {N} ({time.time()-t0:.1f}s)")
print("no-hit within 200000 iterations:", fails if fails else "NONE")
