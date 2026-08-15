# Erdos 931 exists_prime: independent check of the AlphaProof witness and a bounded
# exhaustive hunt for premise-satisfying tuples where closed vs open endpoints differ.
from math import prod

NMAX2 = 6000
def sieve_lpf(N):
    spf=list(range(N+1))
    i=2
    while i*i<=N:
        if spf[i]==i:
            for j in range(i*i,N+1,i):
                if spf[j]==j: spf[j]=i
        i+=1
    return spf
SPF=sieve_lpf(NMAX2+50)
def pf(n):
    s=set()
    if n<len(SPF):
        while n>1:
            p=SPF[n]; s.add(p)
            while n%p==0: n//=p
        return s
    d=2
    while d*d<=n:
        while n%d==0: s.add(d); n//=d
        d+=1
    if n>1: s.add(n)
    return s
def isprime(n): return n>1 and SPF[n]==n
def S(n,k):  # primeFactors of prod_{i=1..k}(n+i)
    s=set()
    for i in range(1,k+1): s |= pf(n+i)
    return frozenset(s)

# --- 1. the repo's own AlphaProof witness (k1,k2,n1,n2) = (10,3,0,13) ---
A=prod(range(1,11)); B=14*15*16
print("10! =",A,"primeFactors",sorted(pf(A)))
print("14*15*16 =",B,"primeFactors",sorted(pf(B)))
print("h4 (equal prime supports):", pf(A)==pf(B))
print("h1 k2<=k1:",3<=10,"h2 3<=k2:",3<=3,"h3 n1+k1<=n2:",0+10<=13)
cl=[p for p in range(0,14) if isprime(p)]
op=[p for p in range(1,13) if isprime(p)]
print("primes in CLOSED [n1,n2]=[0,13]:",cl)
print("primes in OPEN  (n1,n2)=(0,13):",op)
print("=> both readings are satisfied (least witness p=2); the closed/open change is IMMATERIAL here")

# --- 2. Tijdeman example from the source page: 19,20,21,22 and 54,55,56,57 ---
n1,k1,n2,k2 = 18,4,53,4
print("\nTijdeman: S(18,4)=",sorted(S(18,4)),"  S(53,4)=",sorted(S(53,4)),"equal:",S(18,4)==S(53,4))
print("  primes in CLOSED [18,53]:",[p for p in range(18,54) if isprime(p)][:5],"...")
print("  primes in OPEN  (18,53):",[p for p in range(19,53) if isprime(p)][:5],"...")

# --- 3. bounded exhaustive hunt for ALL premise-satisfying tuples ---
from collections import defaultdict
D=defaultdict(list)
N1MAX, KMAX = 500, 25
for n1 in range(0,N1MAX+1):
    for k1 in range(3,KMAX+1):
        D[S(n1,k1)].append((n1,k1))
hits=[]
for n2 in range(0,NMAX2+1):
    for k2 in range(3,KMAX+1):
        t=S(n2,k2)
        if t in D:
            for (n1,k1) in D[t]:
                if k2<=k1 and n1+k1<=n2:
                    hits.append((k1,k2,n1,n2))
print("\npremise-satisfying tuples with n1<=%d, k<=%d, n2<=%d : %d"%(N1MAX,KMAX,NMAX2,len(hits)))
diff=0
for (k1,k2,n1,n2) in hits:
    c=any(isprime(p) for p in range(n1,n2+1))
    o=any(isprime(p) for p in range(n1+1,n2))
    if c!=o: diff+=1
    if len(hits)<=40: print("   (k1,k2,n1,n2)=%s closed_has_prime=%s open_has_prime=%s"%((k1,k2,n1,n2),c,o))
print("tuples where CLOSED and OPEN readings disagree:",diff)
print("tuples with NO prime in the closed interval:",sum(1 for (k1,k2,n1,n2) in hits if not any(isprime(p) for p in range(n1,n2+1))))
