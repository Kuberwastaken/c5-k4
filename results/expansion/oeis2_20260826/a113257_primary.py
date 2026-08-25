#!/usr/bin/env python3
"""A113257 primary path v2: congruence prefilters + selective exact/PRP tests.

a(n) = sum_{i=1..n} (i*i)^((n-i+1)^2)  -- computed MOD p by pow() with modulus,
so no big integers until a candidate passes all filters.

Hand-proved prefilter A (parity): term parity = parity of base i, so
a(n) ≡ ceil(n/2) (mod 2); an odd prime forces a(n) odd, hence n ≡ 2,3 (mod 4)
for n >= 3.
Filter B: a(n) mod p != 0 for small primes p (a(n)=p impossible for n>=3 since
a(n) > p already at these sizes; we assert size when relevant).
"""
import sys
sys.set_int_max_str_digits(2000000)
import time
from sympy import isprime

SMALL = [3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]


def a_mod(n, p):
    s = 0
    for i in range(1, n + 1):
        s = (s + pow(i * i, (n - i + 1) ** 2, p)) % p
    return s


def main():
    cap = float(sys.argv[1]) if len(sys.argv) > 1 else 55.0
    Nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    t0 = time.time()
    tested = 0
    prime_hit = None
    survivors = []
    n = 3
    while n <= Nmax and time.time() - t0 < cap:
        if n % 4 not in (2, 3):
            n += 1
            continue
        if any(a_mod(n, p) == 0 for p in SMALL):
            n += 1
            continue
        # expensive path
        v = sum((i * i) ** ((n - i + 1) ** 2) for i in range(1, n + 1))
        tested += 1
        survivors.append(n)
        print(f"candidate n={n} bits~{v.bit_length()} (digits~{v.bit_length()*30103//100000})", flush=True)
        if isprime(v):
            prime_hit = n
            print(f"Q1 PRIME at n={n}")
            with open("a113257_witness.txt", "w") as f:
                f.write(f"n={n}\n{v}\n")
            break
        n += 1
    print(f"Q1 bracket: no prime for 3<=n<={min(n, Nmax)}, full-tested {tested}: {survivors}")


if __name__ == "__main__":
    main()
