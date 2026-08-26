#!/usr/bin/env python3
"""A113019 audit: fixed points of a(n) = (#digits of n)^digitalroot(n).
Path 1: EXHAUSTIVE enumeration via constraint n = d^r, d=#digits(n), r=dr(n).
  Complete (no bound needed): if n=a(n) then n=d^r with r<=9, so
  n <= 10^9 < 10^10 => d <= 10. Enumerate all (d,r) pairs and test.
Path 2: brute-force direct scan n<=10^7 recomputing a(n) from scratch.
Also: term head vs OEIS %S, Lean tests a_0..a_4, and the specific claim
  n=387420489=9^9 (OEIS %C Kenta Kitamura 2026-08-14).
"""
import sys, time

def digits_len(n):
    return len(str(n))

def digital_root(n):
    if n == 0:
        return 0
    return (n - 1) % 9 + 1

def a_lean(n):
    # faithful port of the Lean def (max 1 n)
    return digits_len(max(1, n)) ** digital_root(n)

print("=== PATH 1: exhaustive (d,r) enumeration ===")
t0 = time.time()
fixed = []
for d in range(1, 11):          # number-of-digits candidate
    for r in range(0, 10):      # exponent = digital root candidate
        n = d ** r
        if digits_len(n) == d and digital_root(n) == r:
            fixed.append((n, d, r))
            print(f"  FIXED POINT n={n}  (d={d}, r={r})")
print(f"complete set: {[n for n,_,_ in sorted(fixed)]}")
assert all(a_lean(n) == n for n, _, _ in fixed), "self-check failed"
# completeness argument printed
print("completeness: n=a(n) => n=d^r, r=dr(n)<=9 => n<=10^9 => d<=10; all pairs checked")

print("=== Lean test values a_0..a_4 ===")
for n in range(5):
    print(f"  a({n}) = {a_lean(n)}")

print("=== Kitamura candidate 387420489 = 9^9 ===")
n = 387420489
print(f"  digits={digits_len(n)} dr={digital_root(n)} a(n)={a_lean(n)} fixed={a_lean(n)==n}")

print("=== PATH 2: brute scan n<=10^7 (cap 60 s) ===")
t0 = time.time()
found = []
CAP = 10_000_000
for n in range(1, CAP + 1):
    if time.time() - t0 > 58:
        print(f"  TIME CAP hit at n={n}")
        break
    if a_lean(n) == n:
        found.append(n)
print(f"  fixed points found n<= {min(CAP, n)}: {found}")

print("=== verdict inputs ===")
print("Lean RHS 'forall n, a n = n -> n = 1 \\/ n = 32' refuted by n = 387420489:",
      a_lean(387420489) == 387420489)
