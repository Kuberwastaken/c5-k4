#!/usr/bin/env python3
"""A000945 audit: Euclid-Mullin sequence; verify head terms by exact factorization."""
import time
from sympy import factorint, isprime

def em(N):
    """first N official terms (a(1)=2, ...)."""
    terms = []
    prod = 1
    while len(terms) < N:
        cand = prod + 1
        f = factorint(cand)
        p = min(f)
        terms.append(p)
        prod *= p
    return terms

t0 = time.time()
terms = em(12)
print("Euclid-Mullin first 12:", terms)
expect = [2, 3, 7, 43, 13, 53, 5, 6221671, 38709183810571, 139, 2801, 11]
print("matches published:", terms == expect, f"({time.time()-t0:.1f}s)")

# Lean head (with a(0)=1): a1..a7 = 2,3,7,43,13,53,5
print("Lean a_1..a_7 tests:", [2,3,7,43,13,53,5], "match:", terms[:7]==[2,3,7,43,13,53,5])
