# Erdos 1055: Lean `IsOfClass` (exact unfolding of PNat.caseStrongInductionOn) vs the
# Erdos-Selfridge classification (source / A005113).  Exact integer arithmetic.
import sys
from functools import lru_cache
sys.setrecursionlimit(10000)

def isprime(n):
    if n<2: return False
    if n%2==0: return n==2
    d=3
    while d*d<=n:
        if n%d==0: return False
        d+=2
    return True

@lru_cache(maxsize=None)
def pf(n):
    """set of prime factors of n"""
    s=set(); m=n; d=2
    while d*d<=m:
        while m%d==0: s.add(d); m//=d
        d+=1
    if m>1: s.add(m)
    return frozenset(s)

# ---------- Lean semantics ----------
# PNat.caseStrongInductionOn: value at 1 is the base; value at n+1 is
#   hi n (fun m (hm : m <= n) => value at m).
# So, with r : PNat,
#   Lean 1 p  <->  pf(p+1) subseteq {2,3}
#   Lean (n+1) p <-> (forall q in pf(p+1), exists m in [1..n], Lean m q)
#                 /\ (exists q in pf(p+1), forall m in [1..n], Lean m q -> m = n)
@lru_cache(maxsize=None)
def lean(r, p):
    assert r>=1
    if r==1:
        return pf(p+1) <= frozenset({2,3})
    n=r-1
    F=pf(p+1)
    c1 = all(any(lean(m,q) for m in range(1,n+1)) for q in F)
    c2 = any(all((not lean(m,q)) or m==n for m in range(1,n+1)) for q in F)
    return c1 and c2

# ---------- source / Erdos-Selfridge semantics ----------
@lru_cache(maxsize=None)
def trueclass(p):
    """class 1 if p+1 is 3-smooth; else 1 + max class of prime factors of p+1."""
    F=pf(p+1)
    if F <= frozenset({2,3}): return 1
    return 1+max(trueclass(q) for q in F)

A005113 = [2, 13, 37, 73, 1021, 2917, 15013]

def least_prime_with(pred, cap):
    n=2
    while n<=cap:
        if isprime(n) and pred(n): return n
        n+=1
    return None

print("r | Lean `p r` = least prime with IsOfClass r | least prime of TRUE class r | A005113(r)")
for r in range(1,6):
    cap = 3000 if r<5 else 20000
    a = least_prime_with(lambda p, r=r: lean(r,p), cap)
    b = least_prime_with(lambda p, r=r: trueclass(p)==r, cap)
    print(f"{r} | {a} | {b} | {A005113[r-1]}   lean==A005113: {a==A005113[r-1]}   true==A005113: {b==A005113[r-1]}")

print()
print("Direct checks on the r=2 claim:")
print("  IsOfClass 1 3  (pf(4)={2} subseteq {2,3}) :", lean(1,3))
print("  IsOfClass 1 2  (pf(3)={3} subseteq {2,3}) :", lean(1,2))
print("  IsOfClass 2 2                             :", lean(2,2), "   <-- source: 2 has TRUE class", trueclass(2))
print("  hence Erdos1055.p 2 = Nat.find(least prime with IsOfClass 2) =", least_prime_with(lambda p: lean(2,p), 3000),
      " vs A005113(2) =", A005113[1])
print()
print("Where do Lean and truth disagree?  (primes p<=500)")
for r in range(1,5):
    dis=[p for p in range(2,501) if isprime(p) and (lean(r,p) != (trueclass(p)==r))]
    sub=[p for p in dis if lean(r,p)]
    print(f"  r={r}: {len(dis)} primes differ; Lean-true/source-false = {sub[:15]}{'...' if len(sub)>15 else ''}")
print()
print("Is Lean class 2 exactly 'true class <= 2'?  (primes p<=2000):",
      all(lean(2,p) == (trueclass(p)<=2) for p in range(2,2001) if isprime(p)))
for r in [3,4]:
    print(f"Is Lean class {r} exactly 'true class == {r}'? (primes p<=2000):",
          all(lean(r,p) == (trueclass(p)==r) for p in range(2,2001) if isprime(p)))
