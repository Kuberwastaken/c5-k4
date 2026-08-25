#!/usr/bin/env python3
"""Independent recomputation of A110835 (second code path: global bytearray sieve,
no sympy), plus comparison against the OEIS-published terms pasted from the
recovered source page (%S/%T lines, oeis_pages/A110835.html)."""
import sys

OEIS_TERMS = [8,4,8,6,18,15,17,25,13,20,29,44,87,81,35,83,79,74,70,67,118,330,
              58,223,172,229,179,471,292,360,506,367,586,577,645,545,424,743,
              503,637,766,467,937,579,698,683,542,1443,641,628,616,604]


def sieve(limit):
    is_comp = bytearray(limit + 1)
    primes = []
    for i in range(2, limit + 1):
        if not is_comp[i]:
            primes.append(i)
            for j in range(i * i, limit + 1, i):
                is_comp[j] = 1
    return primes


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 52
    max_m = max(OEIS_TERMS[:N]) + 2
    # need primes up to n*(max_m+1); compute bound generously then sieve once
    limit = N * (max_m + 2)
    primes = sieve(limit)
    pset = set(primes)

    def prime_free(lo, hi):
        return not any(p in pset for p in range(lo, hi + 1))

    out = []
    for n in range(1, N + 1):
        m = 1
        while not prime_free(n * m, n * (m + 1)):
            m += 1
        out.append(m)
    print("recomputed:", out)
    print("match OEIS published terms:", out == OEIS_TERMS[:N])
    print("all a(n)>=n:", all(v >= i + 1 for i, v in enumerate(out)))
    viol = [(i + 1, v) for i, v in enumerate(out) if v < i + 1]
    print("violations:", viol)


if __name__ == "__main__":
    main()
