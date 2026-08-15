# Independent re-implementation of the Lean `a`, the Lean hypothesis, and the true
# Carmichael condition.  Exact integer arithmetic throughout.
from math import gcd
def isprime(n):
    if n<2: return False
    i=2
    while i*i<=n:
        if n%i==0: return False
        i+=1
    return True

def divisors(n):
    ds=[]
    i=1
    while i*i<=n:
        if n%i==0:
            ds.append(i)
            if i!=n//i: ds.append(n//i)
        i+=1
    return sorted(ds)

def a(n):
    """Mirror of OeisA237271.a : 1 + #{consecutive divisor pairs (d,d') : d' odd and d' >= 2d}."""
    ds=divisors(n)
    return 1+sum(1 for x,y in zip(ds,ds[1:]) if y%2==1 and y>=2*x)

OEIS = [1,1,2,1,2,1,2,1,3,2,2,1,2,2,3,1,2,1,2,1,4,2,2,1,3,2,4,1,2,1,2,1,4,2,
        3,1,2,2,4,1,2,1,2,2,3,2,2,1,3,3,4,2,2,1,4,1,4,2,2,1,2,2,5,1,4,1,2,2,
        4,3,2,1,2,2,4,2,3,2,2,1,5,2,2,1,4,2,4,1,2,1]
mine=[a(n) for n in range(1,len(OEIS)+1)]
print("a matches OEIS DATA n=1..%d:"%len(OEIS), mine==OEIS)
if mine!=OEIS:
    print("first mismatch at n=", next(i+1 for i,(x,y) in enumerate(zip(mine,OEIS)) if x!=y))

# --- Lean hypothesis: ¬Prime k ∧ 1 < k ∧ ∀ a : ZMod k, a ≠ 0 → a^(k-1) = 1 ---
LIMIT=20000
sat=[]
for k in range(2,LIMIT+1):
    if isprime(k):        # first conjunct ¬k.Prime
        continue
    ok=True
    for x in range(1,k):  # nonzero elements of ZMod k
        if pow(x,k-1,k)!=1:
            ok=False; break
    if ok: sat.append(k)
print("k in 2..%d satisfying FULL Lean hypothesis: %s"%(LIMIT, sat if sat else "NONE"))

# --- also: how many nonzero residues actually fail, on the first Carmichaels ---
def carmichael(k):
    """True Carmichael: composite and a^(k-1)=1 mod k for all a coprime to k."""
    if k<2 or isprime(k): return False
    return all(pow(x,k-1,k)==1 for x in range(1,k) if gcd(x,k)==1)

carms=[k for k in range(2,LIMIT+1) if carmichael(k)]
print("Carmichael numbers <= %d: %s"%(LIMIT,carms))
print("a(k) on them: %s   min=%d"%([a(k) for k in carms], min(a(k) for k in carms)))

# explicit falsifying witnesses for the Lean premise on each Carmichael number
for k in carms[:5]:
    p=min(q for q in range(2,k) if k%q==0 and isprime(q))
    print("  k=%d  witness a=%d (a!=0 in ZMod %d), a^(k-1) mod k = %d != 1"%(k,p,k,pow(p,k-1,k)))

# --- general argument, machine-checked on a wide composite range ---
bad=0
for k in range(4,5000):
    if isprime(k): continue
    p=min(q for q in range(2,k+1) if k%q==0)      # least prime factor, p<k since k composite
    assert 1<p<k
    if pow(p,k-1,k)==1: bad+=1
print("composite k in 4..4999 whose least prime factor p satisfies p^(k-1)=1 mod k:", bad)
