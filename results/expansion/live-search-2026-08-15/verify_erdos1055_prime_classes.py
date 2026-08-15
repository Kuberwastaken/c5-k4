#!/usr/bin/env python3
"""Erdos 1055 — Erdos-Selfridge prime classes.

Two definitions are implemented and compared:

(A) SOURCE (erdosproblems.com/1055, A005113): class(p) = 1 iff p+1 is
    {2,3}-smooth; otherwise class(p) = 1 + max_{q | p+1} class(q).
    Classes partition the primes; p_r = least prime of class r.
    Site: p_r begins 2, 13, 37, 73, 1021.

(B) LEAN, upstream 1055.lean, transcribed literally:

      IsOfClass 1     p  :=  (p+1).primeFactors subset {2,3}
      IsOfClass (n+1) p  :=  (forall q in (p+1).primeFactors, exists m <= n, IsOfClass m q)
                          /\ (exists q in (p+1).primeFactors, forall m <= n,
                                IsOfClass m q -> m = n)
      p r := Nat.find (exists_p r)          -- least prime with IsOfClass r

    Note (B) never says "and p is not already of class 1", so a prime can
    satisfy IsOfClass for more than one r.
"""
import sys
from functools import lru_cache


def sieve(m):
    s = bytearray([1]) * (m + 1)
    s[0:2] = b"\x00\x00"
    i = 2
    while i * i <= m:
        if s[i]:
            s[i * i::i] = bytearray(len(s[i * i::i]))
        i += 1
    return s


LIM = 4_000_000
S = sieve(LIM)


def factors(n):
    f = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            f.add(d)
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        f.add(n)
    return f


# ---------- (A) source definition ----------
@lru_cache(maxsize=None)
def cls_source(p):
    fs = factors(p + 1)
    if fs <= {2, 3}:
        return 1
    return 1 + max(cls_source(q) for q in fs)


# ---------- (B) literal Lean definition ----------
@lru_cache(maxsize=None)
def lean_class(r, p):
    fs = factors(p + 1)
    if r == 1:
        return fs <= {2, 3}
    n = r - 1
    if not all(any(lean_class(m, q) for m in range(1, n + 1)) for q in fs):
        return False
    for q in fs:
        if all(m == n for m in range(1, n + 1) if lean_class(m, q)):
            return True
    return False


def least(pred, rmax, cap):
    out = {}
    for r in range(1, rmax + 1):
        for p in range(2, cap):
            if S[p] and pred(r, p):
                out[r] = p
                break
        else:
            out[r] = None
    return out


if __name__ == "__main__":
    rmax = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    cap = int(sys.argv[2]) if len(sys.argv) > 2 else 200000
    src = least(lambda r, p: cls_source(p) == r, rmax, cap)
    lea = least(lean_class, rmax, cap)
    print("r : source p_r (A005113) : Lean `p r`")
    for r in range(1, rmax + 1):
        print(f"{r} : {src[r]} : {lea[r]}")
    print()
    print("primes < 60 with >1 Lean class:",
          [(p, [r for r in range(1, rmax + 1) if lean_class(r, p)],
            cls_source(p)) for p in range(2, 60) if S[p]
           and len([r for r in range(1, rmax + 1) if lean_class(r, p)]) > 1])
