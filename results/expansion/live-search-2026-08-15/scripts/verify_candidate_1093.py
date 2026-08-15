# Independent recomputation of Erdos 1093 deficiency under the two smoothness thresholds.
from math import comb

def factors(m):
    """multiset of prime factors of m (m>=1); [] for m==1."""
    f=[]; d=2
    while d*d<=m:
        while m%d==0: f.append(d); m//=d
        d+=1
    if m>1: f.append(m)
    return f

def smooth_le(m,k): return m!=0 and all(p<=k for p in factors(m))   # source:  p <= k
def smooth_lt(m,k): return m!=0 and all(p< k for p in factors(m))   # Mathlib: p <  k

def defic(n,k,pred): return sum(1 for i in range(k) if pred(n-i,k))

def eligible(n,k):
    """Lean/site side condition: 2k<=n and every prime divisor of C(n,k) exceeds k."""
    if 2*k>n: return (False,"2k>n")
    c=comb(n,k)
    bad=[p for p in sorted(set(factors(c))) if p<=k]
    return (not bad, "prime<=k divides C(n,k): %s"%bad if bad else "ok")

CAT = {1:[(7,3),(13,4),(14,4),(23,5),(62,6),(94,10),(95,10)],
       2:[(44,8),(74,10),(174,12),(239,14),(5179,27),(8413,28),(8414,28),(96622,42)],
       3:[(46,10),(47,10),(241,16),(2105,25),(1119,27),(6459,33)],
       4:[(47,11)],
       9:[(284,28)]}

print(f"{'n':>7} {'k':>3} {'site_def':>8} {'src(p<=k)':>9} {'lean(p<k)':>9} {'k prime':>7} {'eligible':>9}  note")
diffs=[]
for want,lst in sorted(CAT.items()):
    for (n,k) in lst:
        a=defic(n,k,smooth_le); b=defic(n,k,smooth_lt)
        el,note=eligible(n,k)
        kp = len(factors(k))==1 and k>1
        flag="  <-- DIFFERS" if a!=b else ""
        if a!=b: diffs.append((n,k,want,a,b))
        ok = "OK" if a==want else "MISMATCH-vs-site"
        print(f"{n:>7} {k:>3} {want:>8} {a:>9} {b:>9} {str(kp):>7} {str(el):>9}  {ok}{flag}  {note}")
print()
print("catalogue entries whose deficiency changes under the Mathlib threshold:", diffs)

# General reason, machine-checked: the two predicates differ only when k is prime.
bad=0
for k in range(2,60):
    kp = len(factors(k))==1
    for m in range(1,4000):
        if smooth_le(m,k)!=smooth_lt(m,k):
            if not kp: bad+=1
print("counterexamples to 'thresholds differ only for prime k' (k<60, m<4000):", bad)

# Sanity: for prime k the witnesses that separate them are exactly multiples of k that are
# otherwise (k-1)-smooth.
for (n,k) in [(7,3),(23,5),(47,11)]:
    sep=[n-i for i in range(k) if smooth_le(n-i,k) and not smooth_lt(n-i,k)]
    print(f"  n={n} k={k}: values n-i that are k-smooth for p<=k but not p<k: {sep} (factorisations {[factors(v) for v in sep]})")
