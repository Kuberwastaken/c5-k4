#!/usr/bin/env python3
"""Exact finite refutation search for

    Erdos677.erdos_677 :
      ∀ (m n k : ℕ), k > 0 → m ≥ n + k → lcmInterval m k ≠ lcmInterval n k

with  lcmInterval n k = (Finset.Ioc n (n+k)).lcm id = lcm{n+1, …, n+k}
(FormalConjecturesForMathlib/Algebra/GCDMonoid/Finset.lean).

Negation certificate: one triple (m, n, k) with k>0, m ≥ n+k and
lcm{n+1..n+k} = lcm{m+1..m+k}.

Calibration fixtures (from the repo's own `@[category test]` lemma
`lcmInterval_eq_example1`, which uses *different* k on the two sides and is
therefore NOT a counterexample to erdos_677):
    lcmInterval 4 3 = lcmInterval 13 2   (both 210)
    lcmInterval 3 4 = lcmInterval 19 2   (both 420)

Exact big-integer arithmetic.  Hard 60s wall clock cap enforced by caller.
"""
import sys, time
from math import gcd

NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 60000
KMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 12
T0 = time.time()
CAP = 52.0


def lcm_interval(n, k):
    v = 1
    for i in range(n + 1, n + k + 1):
        v = v * i // gcd(v, i)
    return v


# --- calibration ---
assert lcm_interval(4, 3) == 210 and lcm_interval(13, 2) == 210
assert lcm_interval(3, 4) == 420 and lcm_interval(19, 2) == 420
print("# calibration OK: lcmInterval 4 3 = lcmInterval 13 2 = 210, "
      "lcmInterval 3 4 = lcmInterval 19 2 = 420")

found = []
timeout = False
for k in range(1, KMAX + 1):
    seen = {}                       # value -> smallest n producing it
    for n in range(0, NMAX + 1):
        v = lcm_interval(n, k)
        prev = seen.get(v)
        if prev is None:
            seen[v] = n
        else:
            # collision: prev < n; need m ≥ n + k with same value, i.e. n ≥ prev + k
            if n >= prev + k:
                found.append((n, prev, k, v))
                print(f"COUNTEREXAMPLE m={n} n={prev} k={k} value={v}")
            else:
                print(f"# near-collision (gap {n-prev} < k={k}): "
                      f"lcmInterval {prev} {k} = lcmInterval {n} {k} = {v}")
        if (n & 0x3FF) == 0 and time.time() - T0 > CAP:
            timeout = True
            break
    print(f"# k={k} done to n={n}  distinct values {len(seen)}  "
          f"elapsed {time.time()-T0:.1f}s")
    if timeout:
        print(f"# TIMEOUT inside k={k}")
        break

print(f"# counterexamples: {len(found)}")
print(f"# timeout: {timeout}  elapsed {time.time()-T0:.1f}s")

# ---------------------------------------------------------------------------
# Second, COMPLETE-in-m search for small (n,k):  m+1,…,m+k must all divide
# V = lcmInterval n k, so they form a run of k consecutive divisors of V.
# Enumerating divisors of V settles *every* m at once (not just m ≤ NMAX).
# ---------------------------------------------------------------------------
def factor(v):
    f = {}
    d = 2
    while d * d <= v:
        while v % d == 0:
            f[d] = f.get(d, 0) + 1
            v //= d
        d += 1
    if v > 1:
        f[v] = f.get(v, 0) + 1
    return f


def divisors(f, cap):
    ds = [1]
    for p, e in f.items():
        nds = []
        pe = 1
        for _ in range(e + 1):
            for d in ds:
                x = d * pe
                if x <= cap:
                    nds.append(x)
            pe *= p
        ds = nds
        if len(ds) > 4_000_000:
            return None
    return ds


print("\n# --- complete-in-m divisor-run search, small (n,k) ---")
NS, KS = 40, 24
hits = 0
for n in range(0, NS + 1):
    for k in range(3, KS + 1):
        if time.time() - T0 > CAP:
            print(f"# TIMEOUT in divisor-run search at n={n} k={k}")
            n = NS + 1
            break
        V = lcm_interval(n, k)
        f = factor(V)
        ds = divisors(f, V)
        if ds is None:
            print(f"# skipped n={n} k={k}: too many divisors")
            continue
        S = set(ds)
        for d in ds:
            m = d - 1
            if m < n + k:
                continue
            if all((m + j) in S for j in range(1, k + 1)):
                print(f"COUNTEREXAMPLE(divisor-run) m={m} n={n} k={k} V={V}")
                hits += 1
print(f"# divisor-run counterexamples: {hits}   n<= {NS}, k in [3,{KS}]")
print(f"# total elapsed {time.time()-T0:.1f}s")
