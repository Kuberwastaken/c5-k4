#!/usr/bin/env python3
"""Independent re-verification of items 1-3 before upstream write."""
from math import comb, gcd, isqrt

def isprime(n):
    if n < 2: return False
    if n % 2 == 0: return n == 2
    f = 3
    while f * f <= n:
        if n % f == 0: return False
        f += 2
    return True

def divisors(n):
    ds = []
    for i in range(1, isqrt(n) + 1):
        if n % i == 0:
            ds.append(i)
            if i != n // i: ds.append(n // i)
    return sorted(ds)

def prime_factors(n):
    fs = set(); d = 2
    while d * d <= n:
        while n % d == 0: fs.add(d); n //= d
        d += 1
    if n > 1: fs.add(n)
    return fs

# ---------- item 1: A237271 ----------
def a237271(n):
    """1 + #{consecutive divisor pairs (d_k,d_{k+1}) : d_{k+1} odd and d_{k+1} >= 2 d_k}"""
    ds = divisors(n)
    return 1 + sum(1 for x, y in zip(ds, ds[1:]) if y % 2 == 1 and y >= 2 * x)

print("=== ITEM 1: OEIS A237271 observation_carmichael ===")
# OEIS A237271 DATA, n=1..40
oeis = [1,1,2,1,2,1,2,1,3,2,2,1,2,2,4,1,2,1,2,2,4,2,2,1,3,2,4,1,2,2,2,1,4,2,4,2,2,2,4,2]
mine = [a237271(n) for n in range(1, 41)]
print("a(n) matches OEIS DATA n=1..40:", mine == oeis)

# Carmichael numbers (composite k, a^(k-1)=1 mod k for all a coprime to k)
carm = []
for k in range(3, 20001, 2):
    if isprime(k): continue
    if all(pow(a, k - 1, k) == 1 for a in range(2, k) if gcd(a, k) == 1):
        carm.append(k)
print("Carmichael numbers <= 20000:", carm)
print("a(k) on them:              ", [a237271(k) for k in carm])
print("min a(k) =", min(a237271(k) for k in carm), " (observation needs >= 3)")

# Lean hypothesis: composite k>1 with a^(k-1)=1 for EVERY nonzero a in ZMod k
sat = [k for k in range(2, 20001)
       if not isprime(k) and all(pow(a, k - 1, k) == 1 for a in range(1, k))]
print("composite k<=20000 satisfying the LEAN hypothesis (all nonzero a):", sat)

# premise-falsifying witnesses on the first Carmichael numbers
print("premise-falsifying witnesses (a != 0 mod k, a^(k-1) != 1 mod k):")
for k in carm[:5]:
    p = min(prime_factors(k))
    print(f"   k={k:6d}  a={p:3d}  a^(k-1) mod k = {pow(p, k-1, k)}")

# ---------- item 2: Erdos 1093 ----------
print()
print("=== ITEM 2: Erdos 1093 deficiency threshold ===")
def deficiency(n, k, strict):
    """#{0<=i<k : n-i is k-smooth}; strict=True -> primes < k (Mathlib), False -> primes <= k (source)"""
    c = 0
    for i in range(k):
        m = n - i
        if m <= 0: continue
        pf = prime_factors(m)
        ok = all(p < k for p in pf) if strict else all(p <= k for p in pf)
        if ok: c += 1
    return c

for (n, k) in [(7, 3), (23, 5), (47, 11)]:
    le = deficiency(n, k, strict=False)
    lt = deficiency(n, k, strict=True)
    sep = [n - i for i in range(k)
           if n - i > 0 and all(p <= k for p in prime_factors(n - i))
           and not all(p < k for p in prime_factors(n - i))]
    print(f"C({n},{k}): source (p<=k) = {le}   Mathlib smoothNumbers k (p<k) = {lt}   "
          f"k prime={isprime(k)}  separating n-i={sep}")

# eligibility side condition: 2k<=n and no prime <= k divides C(n,k)
for (n, k) in [(7, 3), (23, 5), (47, 11)]:
    c = comb(n, k)
    bad = [p for p in prime_factors(c) if p <= k]
    print(f"   C({n},{k})={c}  2k<=n:{2*k<=n}  primes<=k dividing it: {bad}")

# ---------- item 3: Erdos 1055 ----------
print()
print("=== ITEM 3: Erdos 1055 IsOfClass ===")
from functools import lru_cache

@lru_cache(None)
def lean_class(r, p):
    """Literal unfolding of IsOfClass (r : PNat) p."""
    pf = prime_factors(p + 1)
    if r == 1:
        return pf <= {2, 3}
    n = r - 1                      # r = n+1
    c1 = all(any(lean_class(m, q) for m in range(1, n + 1)) for q in pf)
    c2 = any(all((not lean_class(m, q)) or m == n for m in range(1, n + 1)) for q in pf)
    return c1 and c2

@lru_cache(None)
def true_class(p):
    """Source classification: class 1 if p+1 is 3-smooth, else 1 + max class of prime factors of p+1."""
    pf = prime_factors(p + 1)
    if pf <= {2, 3}: return 1
    return 1 + max(true_class(q) for q in pf)

primes = [p for p in range(2, 4000) if isprime(p)]
print("r | least prime with Lean IsOfClass r | least prime of true class r | A005113")
a005113 = {1: 2, 2: 13, 3: 37, 4: 73, 5: 1021}
for r in range(1, 6):
    lean_p = next((p for p in primes if lean_class(r, p)), None)
    true_p = next((p for p in primes if true_class(p) == r), None)
    flag = "" if lean_p == a005113[r] else "   <-- MISMATCH"
    print(f"{r} | {lean_p:6} | {true_p:6} | {a005113[r]:6}{flag}")

print("IsOfClass 1 2 =", lean_class(1, 2), " (2 has true class", true_class(2), ")")
print("IsOfClass 2 2 =", lean_class(2, 2))
diff = [p for p in primes if p < 500 and lean_class(2, p) != (true_class(p) == 2)]
print("primes < 500 where IsOfClass 2 disagrees with 'true class = 2':", diff)
print("all of those have true class 1:", all(true_class(p) == 1 for p in diff))
