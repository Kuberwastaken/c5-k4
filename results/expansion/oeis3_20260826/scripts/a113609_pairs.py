#!/usr/bin/env python3
"""A113609 audit: pairs (q,q+2) both non-prime prime powers.
   (25,27) smallest; conjecture: another exists with q>=10^6."""
import time
from sympy import isprime, integer_nthroot

def is_prime_power_nonprime(q):
    """q = p^e, e>=2 (so q itself not prime)."""
    if q < 4 or isprime(q):
        return False
    for e in range(2, q.bit_length()):
        r, ok = integer_nthroot(q, e)
        if not ok:
            break
    # proper check: exponents 2..log2
    for e in range(2, q.bit_length() + 1):
        r, ok = integer_nthroot(q, e)
        if ok and isprime(r):
            return True
    return False

t0 = time.time()
pairs = []
N = 2_000_000
for q in range(1, N + 1):
    if time.time() - t0 > 55:
        N = q
        break
    if not isprime(q + 2) and is_prime_power_nonprime(q + 2) and not isprime(q) \
       and is_prime_power_nonprime(q):
        pairs.append((q, q + 2))
print(f"scanned q<= {N} ({time.time()-t0:.1f}s)")
print("both-nonprime-prime-power pairs:", pairs)
big = [p for p in pairs if p[0] >= 1_000_000]
print("with q >= 10^6:", big if big else "NONE -> bracket")
