import numpy as np, sys
sys.path.insert(0,'/Users/kuber.mehta/Projects/c5-k4/results/expansion/live-search-2026-08-15/scripts')
from nt import sieve_primes
L=4_000_000
s=sieve_primes(L)
P=np.flatnonzero(s).tolist()   # P[i] = (i+1)-th prime  (0-indexed like Nat.nth Nat.Prime)
def p(k):  # Lean: p k = Nat.nth Nat.Prime (k-1)  with k:ℕ truncated subtraction
    return P[k-1] if k>=1 else P[0]
def a(n):
    if n==0: return 0
    return p(2*n+2)-p(2*n+1)-p(2*n)+p(2*n-1)
NMAX=(len(P)-3)//2
print("primes available:",len(P),"n up to",NMAX)
vals=[a(n) for n in range(1,min(NMAX,300000))]
print("a(1..12) =",vals[:12])
odd=[i+1 for i,v in enumerate(vals) if v%2!=0]
print("n>0 with a(n) ODD:",odd[:20],"count",len(odd))
print("any |a(n)|==3 for n in 1..%d ?"%len(vals), any(abs(v)==3 for v in vals))
print("set of odd |a(n)| values:",sorted({abs(v) for v in vals if v%2!=0}))
# hypothesis witness for d=3
print("3 = |5-2|, 5 prime, 2 prime ->", abs(5-2)==3)
