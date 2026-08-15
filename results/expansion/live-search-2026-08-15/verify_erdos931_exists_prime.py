#!/usr/bin/env python3
"""Exhaustive finite search for a counterexample to

    Erdos931.erdos_931.variants.exists_prime
    (k1 k2 n1 n2 : ℕ) (h1 : k2 ≤ k1) (h2 : 3 ≤ k2) (h3 : n1 + k1 ≤ n2)
      (h4 : (∏ i ∈ Icc 1 k1, (n1+i)).primeFactors
          = (∏ j ∈ Icc 1 k2, (n2+j)).primeFactors) :
      ∃ p, p.Prime ∧ n1 ≤ p ∧ p ≤ n2

Negation certificate: one tuple (k1,k2,n1,n2) satisfying h1..h4 with the
closed interval [n1, n2] containing no prime.

Because the conclusion is `∃ p prime, n1 ≤ p ≤ n2`, a counterexample forces
[n1,n2] to be a prime-free closed interval of length n2-n1 >= k1 >= k2 >= 3.
So we enumerate maximal prime-free runs and test every admissible tuple inside.

Exact integer arithmetic only.  Hard 60s wall clock cap enforced by caller.
"""
import sys, time

LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000
T0 = time.time()
CAP = 55.0


def sieve_spf(n):
    spf = list(range(n + 1))
    i = 2
    while i * i <= n:
        if spf[i] == i:
            for j in range(i * i, n + 1, i):
                if spf[j] == j:
                    spf[j] = i
        i += 1
    return spf


PAD = 512
spf = sieve_spf(LIMIT + PAD)   # n2+j can exceed LIMIT by at most the run span
is_prime = [False] * (LIMIT + PAD + 1)
for v in range(2, LIMIT + PAD + 1):
    is_prime[v] = (spf[v] == v)


def pf(m):
    """set of prime factors of m (m >= 1); primeFactors 1 = {} , 0 = {} in Lean too"""
    s = set()
    while m > 1:
        p = spf[m]
        s.add(p)
        while m % p == 0:
            m //= p
    return s


# maximal runs of consecutive non-primes [a,b]
runs = []
a = None
for v in range(0, LIMIT + 1):
    if not is_prime[v]:
        if a is None:
            a = v
    else:
        if a is not None:
            runs.append((a, v - 1))
            a = None
if a is not None:
    runs.append((a, LIMIT))

runs = [(a, b) for (a, b) in runs if b - a >= 3]   # need n2-n1 >= k1 >= 3
print(f"# limit={LIMIT}  prime-free runs of span>=3: {len(runs)}  "
      f"max span {max(b-a for a,b in runs)}")

found = []
tested = 0
timeout = False
for (a, b) in runs:
    if time.time() - T0 > CAP:
        timeout = True
        print(f"# TIMEOUT after run starting {a}")
        break
    # cache cumulative prime-factor unions per start
    for n1 in range(a, b + 1):
        maxk = b - n1                       # k1 <= n2-n1 <= b-n1
        if maxk < 3:
            continue
        U1 = []
        acc = set()
        for i in range(1, maxk + 1):
            acc = acc | pf(n1 + i)
            U1.append(frozenset(acc))       # U1[k-1] = primes of prod_{i=1}^{k}(n1+i)
        for n2 in range(n1 + 3, b + 1):
            maxk2 = n2 - n1
            U2 = []
            acc2 = set()
            for j in range(1, maxk2 + 1):
                acc2 = acc2 | pf(n2 + j)
                U2.append(frozenset(acc2))
            for k1 in range(3, n2 - n1 + 1):
                s1 = U1[k1 - 1]
                for k2 in range(3, k1 + 1):
                    tested += 1
                    if s1 == U2[k2 - 1]:
                        found.append((k1, k2, n1, n2, sorted(s1)))
                        print("COUNTEREXAMPLE", k1, k2, n1, n2, sorted(s1))

print(f"# tuples tested: {tested}")
print(f"# counterexamples: {len(found)}")
print(f"# timeout: {timeout}   elapsed {time.time()-T0:.1f}s")
