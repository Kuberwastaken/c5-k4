#!/usr/bin/env python3
"""A100434 audit v2: Dement identities c+d=b, e+f=b, g+a=b as formalized in Lean.
   Check all n in [0,60] for failures (any failure = the 'conjecture' is FALSE
   as stated -> defect/crossing)."""
import sys

def linrec(init, N):
    """a(n+4) = -6 a(n+2) - a(n)."""
    out = list(init)
    while len(out) <= N:
        n = len(out)
        out.append(-6 * out[n - 2] - out[n - 4])
    return out

N = 60
c = linrec([1, -3, -7, 17], N)
d = linrec([2, 4, -10, -24], N)
a = linrec([3, 4, -17, -24], N)

def b(n):
    return c[n + 1] if n % 2 == 0 else c[n - 1]

def e(n):
    return d[n] // 2 if n % 2 == 0 else -(d[n - 1] // 2)

def f(n):
    m = n // 2
    return d[2 * m + 1] // 2

def g(n):
    return 0 if n % 2 == 0 else c[n]

print("n:  c   d   b   |c+d-b|   e   f  e+f-b   g    a  g+a-b")
f1, f2, f3 = [], [], []
for n in range(0, 30):
    r1 = c[n] + d[n] - b(n)
    r2 = e[n] if False else e(n) + f(n) - b(n)
    r3 = g(n) + a[n] - b(n)
    print(f"{n}: {c[n]:5d} {d[n]:5d} {b(n):5d}   {r1:4d}    {e(n):5d} {f(n):5d} {r2:4d}   {g(n):4d} {a[n]:5d} {r3:4d}")
    if r1 != 0:
        f1.append(n)
    if r2 != 0:
        f2.append(n)
    if r3 != 0:
        f3.append(n)
print("\nconjecture1 (c+d=b) failures:", f1 if f1 else "NONE")
print("conjecture2 (e+f=b) failures:", f2 if f2 else "NONE")
print("conjecture3 (g+a=b) failures:", f3 if f3 else "NONE")
