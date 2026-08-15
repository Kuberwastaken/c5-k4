#!/usr/bin/env python3
"""Finite refutation searches for the remaining CANDIDATE_FOR_DEPTH declarations.

MODES
  es242    Erdos242.erdos_242 : ∀ n>2, ∃ 1 ≤ x < y < z, 4/n = 1/x+1/y+1/z
           (Erdos-Straus WITH the distinctness x<y<z demanded by the source).
  q324     Erdos324.erdos_324.variants.quintic :
           {(a,b) | a<b}.InjOn fun (a,b) => a^5 + b^5
  p364     Erdos364.erdos_364 : ¬∃ n, Powerful n ∧ Powerful (n+1) ∧ Powerful (n+2)
  d406     Erdos406.erdos_406.variants.one_two :
           IsGreatest {n | n.isPowerOfTwo ∧ Nat.digits 3 n ⊆ [1,2]} (2^15)
  d779     Erdos779.erdos_779 : ∀ n ≥ 1, letI P = ∏_{i<n+1} p_i,
           ∃ p prime, (P+p).Prime ∧ p_n < p < P

Exact integer / Fraction arithmetic.  Hard 60s wall clock cap by caller.
"""
import sys, time
from fractions import Fraction
from math import isqrt

MODE = sys.argv[1]
ARG = int(sys.argv[2]) if len(sys.argv) > 2 else 0
T0 = time.time()
CAP = 52.0


def prime_sieve(n):
    s = bytearray([1]) * (n + 1)
    s[0:2] = b'\x00\x00'
    i = 2
    while i * i <= n:
        if s[i]:
            s[i * i::i] = bytearray(len(s[i * i::i]))
        i += 1
    return s


# ---------------------------------------------------------------- Erdos 242
def es242_solve(n, ycap=None, budget=None):
    """Return (x,y,z) with 1<=x<y<z and 4/n = 1/x+1/y+1/z, or None.
    Exhaustive when ycap is None and budget is None."""
    ops = 0
    xlo = n // 4 + 1                    # x > n/4
    xhi = (3 * n) // 4                  # 3/x >= 4/n  =>  x <= 3n/4
    for x in range(xhi, xlo - 1, -1):   # descending: largest residual first
        # r = 4/n - 1/x = (4x-n)/(n x)
        p = 4 * x - n
        q = n * x
        if p <= 0:
            continue
        g = __import__('math').gcd(p, q)
        p //= g
        q //= g
        # 1/y + 1/z = p/q with y < z  =>  q/p < y < 2q/p
        ylo = max(x + 1, q // p + 1)
        yhi = (2 * q) // p
        if ycap is not None:
            yhi = min(yhi, ycap)
        for y in range(ylo, yhi + 1):
            ops += 1
            if budget is not None and ops > budget:
                return 'BUDGET'
            den = p * y - q
            if den <= 0:
                continue
            num = q * y
            if num % den == 0:
                z = num // den
                if z > y:
                    return (x, y, z)
    return None


if MODE == 'es242':
    N = ARG or 2000
    unresolved = []
    for n in range(3, N + 1):
        s = es242_solve(n, ycap=20000, budget=400000)
        if s is None or s == 'BUDGET':
            unresolved.append(n)
        if time.time() - T0 > CAP:
            print(f"# phase1 TIMEOUT at n={n}")
            break
    print(f"# es242 phase1 (capped) scanned to n={n}: {len(unresolved)} unresolved")
    hard = []
    for n in unresolved:
        if time.time() - T0 > CAP:
            print(f"# phase2 TIMEOUT, {len(unresolved)} left unchecked")
            break
        s = es242_solve(n)
        if s is None:
            hard.append(n)
            print(f"COUNTEREXAMPLE erdos_242 n={n}: no distinct 1<=x<y<z")
    print(f"# es242 exhaustive failures: {len(hard)}   elapsed {time.time()-T0:.1f}s")

# ---------------------------------------------------------------- Erdos 324
elif MODE == 'q324':
    B = ARG or 2000
    seen = {}
    hits = 0
    for a in range(0, B):
        a5 = a ** 5
        for b in range(a + 1, B):
            v = a5 + b ** 5
            prev = seen.get(v)
            if prev is not None:
                print(f"COUNTEREXAMPLE erdos_324.quintic: {prev} and {(a,b)} both give {v}")
                hits += 1
            else:
                seen[v] = (a, b)
        if time.time() - T0 > CAP:
            print(f"# TIMEOUT at a={a}")
            break
    print(f"# q324 a<b<{B} (a up to {a}); collisions {hits}; "
          f"{len(seen)} distinct sums; elapsed {time.time()-T0:.1f}s")

# ---------------------------------------------------------------- Erdos 364
elif MODE == 'p364':
    N = ARG or 10 ** 12
    # powerful numbers = a^2 * b^3 (b squarefree, but the over-generated set is fine)
    pw = set()
    b = 1
    while b ** 3 <= N:
        b3 = b ** 3
        a = 1
        while a * a * b3 <= N:
            pw.add(a * a * b3)
            a += 1
        b += 1
    pw.add(0)   # Mathlib: 0 is Powerful (∀ p prime, p ∣ 0 → p^2 ∣ 0)
    print(f"# powerful numbers ≤ {N}: {len(pw)}")
    hits = 0
    for n in sorted(pw):
        if (n + 1) in pw and (n + 2) in pw:
            print(f"COUNTEREXAMPLE erdos_364: n={n}, {n},{n+1},{n+2} all Powerful")
            hits += 1
    # also report consecutive pairs as a sanity control
    pairs = sum(1 for n in pw if (n + 1) in pw)
    print(f"# consecutive powerful PAIRS ≤ {N}: {pairs} (control; Mahler: infinitely many)")
    print(f"# triples: {hits}; elapsed {time.time()-T0:.1f}s")

# ---------------------------------------------------------------- Erdos 406
elif MODE == 'd406':
    MMAX = ARG or 3000

    def base3_digits(v):
        ds = []
        while v:
            v, r = divmod(v, 3)
            ds.append(r)
        return ds
    # membership of 2^15
    d15 = base3_digits(2 ** 15)
    print(f"# base-3 digits of 2^15 = 32768 (little-endian): {d15}  "
          f"all in {{1,2}}: {set(d15) <= {1, 2}}")
    hits = []
    v = 1
    for m in range(0, MMAX + 1):
        ds = base3_digits(v)
        if ds and set(ds) <= {1, 2}:
            hits.append(m)
        v <<= 1
        if time.time() - T0 > CAP:
            print(f"# TIMEOUT at m={m}")
            break
    print(f"# 2^m with base-3 digits ⊆ {{1,2}} for m ≤ {m}: {hits}")
    bigger = [h for h in hits if 2 ** h > 2 ** 15]
    print(f"# counterexamples to IsGreatest (2^m > 2^15 in the set): {bigger}")
    # companion: digits ⊆ {0,1}  (the erdos_406 answer(sorry) statement)
    v = 1
    hits01 = []
    for m in range(0, min(m, MMAX) + 1):
        ds = base3_digits(v)
        if ds and set(ds) <= {0, 1}:
            hits01.append(m)
        v <<= 1
    print(f"# (companion) 2^m with base-3 digits ⊆ {{0,1}}: {hits01}")
    print(f"# elapsed {time.time()-T0:.1f}s")

# ---------------------------------------------------------------- Erdos 779
elif MODE == 'd779':
    NMAX = ARG or 300
    isp_small = prime_sieve(2_000_000)
    small = [i for i in range(2, 2_000_000) if isp_small[i]]

    def mr(nn):
        """deterministic-ish Miller-Rabin (BPSW-strength bases) for big ints"""
        if nn < 2:
            return False
        for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
            if nn % p == 0:
                return nn == p
        d, s = nn - 1, 0
        while d % 2 == 0:
            d //= 2
            s += 1
        for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
            x = pow(a, d, nn)
            if x == 1 or x == nn - 1:
                continue
            for _ in range(s - 1):
                x = x * x % nn
                if x == nn - 1:
                    break
            else:
                return False
        return True

    P = 1
    worst = (0, 0)
    fails = []
    for n in range(0, NMAX + 1):
        P *= small[n]                    # P = ∏_{i ∈ range(n+1)} p_i
        if n < 1:
            continue
        pn = small[n]                    # nth Nat.Prime n  (0-indexed) = largest factor
        found = None
        for p in small:
            if p <= pn:
                continue
            if p >= P:
                break
            if mr(P + p):
                found = p
                break
            if time.time() - T0 > CAP:
                break
        if found is None:
            fails.append(n)
            print(f"NO WITNESS FOUND (not a proof of failure) at n={n}")
        else:
            if found > worst[1]:
                worst = (n, found)
        if time.time() - T0 > CAP:
            print(f"# TIMEOUT at n={n}")
            break
    print(f"# d779 verified n=1..{n} (Lean indexing; = source n=2..{n+1} primes); "
          f"witnesses found for all but {len(fails)}")
    print(f"# largest witness prime needed: p={worst[1]} at n={worst[0]}")
    print(f"# elapsed {time.time()-T0:.1f}s")
