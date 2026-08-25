#!/usr/bin/env python3
"""A107247 repair development: verify all 9 conjuncts of known_prime_and_semiprimes
   via a THIRD independent implementation (sliding-window nonacci + manual semiprime
   certification by trial division), and emit the Lean witness table."""
from sympy import isprime

def nonacci_window(N):
    """Path C: iterative 9-step Fibonacci with explicit window (no recursion)."""
    vals = [0]*8 + [1]
    if N < 9:
        return (vals + [0]*(9-N))[:N+1]
    for _ in range(9, N+1):
        vals.append(sum(vals[-9:]))
    return vals

def squaresum_prefix(vals, upto):
    return sum(v*v for v in vals[:upto+1])

def certify_semiprime(n):
    """Path C primality/semiprime certification without factorint:
       find smallest factor d by trial division, then test n/d prime."""
    if isprime(n):
        return ("prime", None)
    d = 2
    while d*d <= n:
        if n % d == 0:
            q = n // d
            return (("semiprime", (d, q)) if isprime(q) else ("other", (d, q)))
        d += 1
    return ("other", None)

# Published %C anchors (1-based OEIS indices shifted per file note):
# Lean a(k) values claimed: a(8)=2 prime; a(9)=6; a(10)=22; a(11)=86;
# a(13)=1366; a(14)=5462; a(16)=87382; a(17)=348503; a(27)=358201316657.
claims = {
    8:  ("prime", 2),
    9:  ("semiprime", 6),
    10: ("semiprime", 22),
    11: ("semiprime", 86),
    13: ("semiprime", 1366),
    14: ("semiprime", 5462),
    16: ("semiprime", 87382),
    17: ("semiprime", 348503),
    27: ("semiprime", 358201316657),
}

vals = nonacci_window(29)
print("== nonacci head (window impl):", vals[:12])
a = {n: squaresum_prefix(vals, n+1) for n in range(0, 28)}
print("== Lean-index sumsquares:", [a[i] for i in range(7, 12)])

print("\n== conjunct-by-conjunct certification (path C) ==")
all_ok = True
witnesses = []
for n, (kind, val) in sorted(claims.items()):
    v = a[n]
    assert v == val, f"term mismatch at {n}: {v} != {val}"
    c = certify_semiprime(v)
    ok = (c[0] == kind)
    all_ok &= ok
    print(f"a({n}) = {v}: expected {kind}, got {c}" + ("" if ok else "  <-- FAIL"))
    witnesses.append((n, v, c))
print("\nALL NINE CONJUNCTS VERIFY (path C):", all_ok)

print("\n== lean witness table ==")
for n, v, c in witnesses:
    if c[0] == "prime":
        print(f"a({n}) = {v}: Prime := by decide")
    else:
        p, q = c[1]
        print(f"a({n}) = {v} = {p} * {q}  ({p},{q} prime)")
