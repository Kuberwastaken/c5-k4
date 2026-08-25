#!/usr/bin/env python3
"""A001146 primary path: search for counterexamples to Hasler's conjecture
(k^4 - 1 divides 2^k - 1  =>  k = 2^(2^n), n >= 2).
Exhaustive scan over k; divisibility tested exactly by modular exponentiation.
"""
import sys


def main():
    B = int(sys.argv[1]) if len(sys.argv) > 1 else 2000000
    special = set()
    v = 4
    while v <= max(B, 100):
        pass
    # powers 2^(2^n), n>=2: 16, 256, 65536, ...
    n = 2
    while 2 ** (2 ** n) <= B * 16:
        special.add(2 ** (2 ** n))
        n += 1
    hits = []
    for k in range(2, B + 1):
        if k % 2 == 1:
            continue  # k^4-1 even then (divisible by 8), LHS odd -> impossible
        m = k ** 4 - 1
        if pow(2, k, m) == 1 % m:
            hits.append(k)
            tag = "SPECIAL (2^(2^n))" if k in special else "COUNTEREXAMPLE??"
            print(k, tag)
    print("hits up to", B, ":", hits)
    print("counterexamples (non-special hits):", [k for k in hits if k not in special])


if __name__ == "__main__":
    main()
