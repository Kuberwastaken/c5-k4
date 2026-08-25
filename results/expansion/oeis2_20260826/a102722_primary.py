#!/usr/bin/env python3
"""A102722 primary path: fully exact computation with Fraction.

a(n) = floor( sum_{k=1}^n {n/k} ), computed as
   sum_{k=1}^n Fraction(n mod k, k)
with exact rational arithmetic. Feasible to n ~ 2000 within the cap.
Also downloads-free cross-check against the OEIS b-file terms supplied by
Robert Israel (b102722.txt fetched separately into oeis_pages/).
"""
import sys
from fractions import Fraction


def a_exact(n):
    s = Fraction(0)
    for k in range(1, n + 1):
        s += Fraction(n % k, k)
    return s.numerator // s.denominator


def load_bfile(path):
    terms = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 2 and parts[0].isdigit():
                terms.append(int(parts[1]))
    return terms


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    vals = [a_exact(n) for n in range(1, N + 1)]
    try:
        bf = load_bfile("/Users/kuber.mehta/Personal-Projects/c5-k4/results/expansion/oeis2_20260826/oeis_pages/b102722.txt")
        ok = vals == bf[:N]
        print(f"match b-file first {N}: {ok}")
        if not ok:
            for i, (x, y) in enumerate(zip(vals, bf), 1):
                if x != y:
                    print("first mismatch at", i, x, y)
                    break
    except FileNotFoundError:
        print("b-file not present; skipped")
    print("first20:", vals[:20])


if __name__ == "__main__":
    main()
