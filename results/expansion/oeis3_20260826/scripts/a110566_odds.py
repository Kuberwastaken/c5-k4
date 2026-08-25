#!/usr/bin/env python3
"""A110566 audit v2: a(n) = lcm(1..n)/den(H_n) = gcd(S_n, L_n)
   where H_n = S_n/L_n, L_n = lcm(1..n). Conjecture: every odd number occurs."""
import sys
import time
from math import gcd

N = 20000
L = 1   # lcm(1..n)
S = 0   # sum_{k<=n} L/k
t0 = time.time()
odds = set()
head = []
for n in range(1, N + 1):
    if n % L != 0 if False else False:
        pass
    # update L to lcm(L, n)
    g = gcd(L, n)
    Lnew = L * (n // g)
    # rescale S from basis L to basis Lnew
    S *= (Lnew // L)
    L = Lnew
    S += L // n
    a = gcd(S, L)
    if n <= 8:
        head.append(a)
    if a % 2 == 1:
        odds.add(a)
print(f"generated to {N} ({time.time()-t0:.1f}s)")
print("head:", head, "expect [1,1,1,1,1,3,...]")
missing = [m for m in range(1, 999) if m % 2 == 1 and m not in odds]
print("odd values <1000 never seen:", missing if missing else "NONE")
print("largest odd value seen:", max(odds))
