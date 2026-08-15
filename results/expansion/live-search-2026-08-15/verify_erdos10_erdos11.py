#!/usr/bin/env python3
"""Exact finite refutation search for two Erdos Problems declarations.

(A) Erdos10.erdos_10.variants.granville_soundararajan_odd
      {n | Odd n ∧ 1 < n} ⊆ sumPrimeAndTwoPows 3
    ∧ {n | Even n ∧ n ≠ 0} ⊆ sumPrimeAndTwoPows 4

    sumPrimeAndTwoPows k = { p + Σ_{a∈pows} 2^a | p prime, pows : Multiset ℕ,
                             pows.card ≤ k }.
    A multiset of k exponents sums to a number of binary popcount ≤ k, and every
    number of popcount ≤ k is such a sum (take its binary expansion, pad with
    splits 2^a = 2^(a-1)+2^(a-1) if a shorter multiset is wanted).  Hence
        n ∈ sumPrimeAndTwoPows k  ⟺  ∃ prime p ≤ n with popcount(n - p) ≤ k.
    (popcount 0 = 0 covers the empty multiset, i.e. n itself prime.)

(B) Erdos11.erdos_11              (n odd, 1 < n)      → ∃ k l, Squarefree k ∧ n = k + 2^l
    Erdos11.erdos_11.variants.not_four_dvd (¬4∣n, 1<n) → same
    Erdos11.erdos_11.variants.two_pow_two (n odd,1<n) → ∃ k l m, Squarefree k ∧ n = k+2^l+2^m
    Mathlib `Squarefree 0` is False and `Squarefree 1` is True.

Exact integer arithmetic.  Hard 60s wall clock cap enforced by caller.
"""
import sys, time

MODE = sys.argv[1]
LIMIT = int(sys.argv[2])
T0 = time.time()


def prime_sieve(n):
    s = bytearray([1]) * (n + 1)
    s[0:2] = b'\x00\x00'
    i = 2
    while i * i <= n:
        if s[i]:
            s[i * i::i] = bytearray(len(s[i * i::i]))
        i += 1
    return s


def squarefree_sieve(n):
    """sf[m] = True iff m is squarefree (m>=1).  sf[0] = False (Mathlib)."""
    sf = bytearray([1]) * (n + 1)
    sf[0] = 0
    d = 2
    while d * d <= n:
        dd = d * d
        sf[dd::dd] = bytearray(len(sf[dd::dd]))
        d += 1
    return sf


if MODE == 'erdos10':
    isp = prime_sieve(LIMIT)
    # numbers of binary popcount <= 4, ascending: the "at most 4 powers of 2" part
    B = LIMIT.bit_length() + 1
    d4 = [0]
    for a in range(B):
        d4.append(1 << a)
        for b in range(a):
            d4.append((1 << a) + (1 << b))
            for c in range(b):
                d4.append((1 << a) + (1 << b) + (1 << c))
                for e in range(c):
                    d4.append((1 << a) + (1 << b) + (1 << c) + (1 << e))
    d4 = sorted(set(x for x in d4 if x <= LIMIT))
    d3 = [x for x in d4 if bin(x).count('1') <= 3]
    bad_odd, bad_even = [], []
    n = 2
    for n in range(2, LIMIT + 1):
        ds = d3 if (n & 1) else d4
        ok = False
        for d in ds:
            if d > n - 2:
                break
            if isp[n - d]:
                ok = True
                break
        if not ok:
            (bad_odd if (n & 1) else bad_even).append(n)
            print(f"COUNTEREXAMPLE n={n} parity={'odd' if n&1 else 'even'} "
                  f"k={3 if n&1 else 4}")
        if (n & 0xFFFF) == 0 and time.time() - T0 > 52:
            print(f"# TIMEOUT at n={n}")
            break
    print(f"# erdos10 scanned to {n}; odd failures {len(bad_odd)}, even failures {len(bad_even)}")
    print(f"# elapsed {time.time()-T0:.1f}s")

elif MODE == 'erdos10_grechuk':
    # calibration: 1117175146 ∉ sumPrimeAndTwoPows 3   (research solved decl)
    N = 1117175146
    isp = prime_sieve(int(N ** 0.5) + 1)
    small = [i for i in range(2, len(isp)) if isp[i]]

    def is_prime(m):
        if m < 2:
            return False
        for p in small:
            if p * p > m:
                return True
            if m % p == 0:
                return m == p
        return True
    hit = None
    # popcount(N-p) <= 3 : enumerate all d>0 with popcount<=3 and d<=N, test N-d prime
    bits = N.bit_length()
    cands = [0]
    for a in range(bits + 1):
        cands.append(1 << a)
    for a in range(bits + 1):
        for b in range(a + 1):
            cands.append((1 << a) + (1 << b))
    for a in range(bits + 1):
        for b in range(a + 1):
            for c in range(b + 1):
                cands.append((1 << a) + (1 << b) + (1 << c))
    for d in set(cands):
        if 0 <= d <= N - 2 and is_prime(N - d):
            hit = d
            break
    print(f"# Grechuk calibration: 1117175146 in sumPrimeAndTwoPows 3 ? {hit is not None} (witness d={hit})")
    print(f"# elapsed {time.time()-T0:.1f}s")

elif MODE == 'erdos11':
    sf = squarefree_sieve(LIMIT)
    pows = [1 << l for l in range(LIMIT.bit_length() + 1)]
    bad1, bad2, bad3 = [], [], []
    for n in range(2, LIMIT + 1):
        odd = bool(n & 1)
        nf4 = (n % 4 != 0)
        if not (odd or nf4):
            continue
        ok1 = False
        for q in pows:
            if q > n:
                break
            if sf[n - q]:
                ok1 = True
                break
        if not ok1:
            if odd:
                bad1.append(n)
                print(f"COUNTEREXAMPLE erdos_11 n={n}")
            if nf4:
                bad2.append(n)
                print(f"COUNTEREXAMPLE erdos_11.variants.not_four_dvd n={n}")
        if odd and not ok1:
            ok3 = False
            for q in pows:
                if q >= n:
                    break
                for q2 in pows:
                    if q + q2 > n:
                        break
                    if sf[n - q - q2]:
                        ok3 = True
                        break
                if ok3:
                    break
            if not ok3:
                bad3.append(n)
                print(f"COUNTEREXAMPLE erdos_11.variants.two_pow_two n={n}")
        if time.time() - T0 > 52:
            print(f"# TIMEOUT at n={n}")
            break
    print(f"# erdos11 scanned to {n}: odd failures {len(bad1)}, "
          f"not-4-dvd failures {len(bad2)}, two-power failures {len(bad3)}")
    print(f"# elapsed {time.time()-T0:.1f}s")
