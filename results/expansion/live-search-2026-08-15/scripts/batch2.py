import sys, time
from nt import is_prime, is_square, isqrt
t0=time.time()
def hdr(t): print("\n########## "+t+"  (t=%.1fs)"%(time.time()-t0))

# --- A113250 / A113252 / A113255 : IsSquare(a(2n+1)) over ZZ
hdr("A113250/113252/113255  IsSquare(a(2n+1))")
def run(m, init, N=60):
    A,B,C = -4, m*m*4, m**4   # a(n) = -4a(n-1) + (2m)^2 a(n-3) + m^4 a(n-4)
    s=list(init)
    for n in range(4,N):
        s.append(A*s[n-1] + B*s[n-3] + C*s[n-4])
    return s
for m,init,name in ((4,[-1,4,32,64],'A113250'),(6,[-1,4,92,784],'A113252'),(9,[-1,4,227,5329],'A113255')):
    s=run(m,init)
    print(name,"coeffs -4,%d,%d"%(4*m*m,m**4),"first 8:",s[:8])
    bad=[(n,s[n]) for n in range(1,len(s),2) if not (s[n]>=0 and isqrt(s[n])**2==s[n])]
    print("   odd-index non-squares (n<%d):"%len(s), bad[:6], " count", len(bad))
    print("   odd-index sqrt sample:", [(n,isqrt(s[n])) for n in range(1,14,2)])

# --- A112970 : generalized Stern
hdr("A112970  conj1/2/3")
import sys
sys.setrecursionlimit(100000)
from functools import lru_cache
@lru_cache(maxsize=None)
def st(n):
    if n==0 or n==1: return 1
    k=n//2
    if n%2==1: return st(k)
    return st(k) + (0 if k<2 else st(k-2))
print("a[0..20]", [st(n) for n in range(21)])
b1=[n for n in range(0,40) if st(2**n)!=st(2**(n+1)+1)]
b2=[n for n in range(0,40) if st(2**n-1)!=st(3*2**n-1)]
b3=[n for n in range(0,40) if st(2**n-1)!=1]
print("conj1 failures n<40:",b1,"  conj2:",b2,"  conj3:",b3)

# --- A113010 : fixed points of digits-length^digitsum
hdr("A113010  fixed points")
fix=[]
for d in range(1,60):
    for s in range(1, 9*d+1):
        v=d**s
        if v==0: continue
        ds=str(v)
        if len(ds)==d and sum(int(ch) for ch in ds)==s:
            fix.append(v)
print("fixed points n>0 with digitlen(n)^digitsum(n)==n, digits<=59:", sorted(set(fix)))

# --- A104320 : zeros in ternary of 2^n
hdr("A104320  zeros in base-3 rep of 2^n")
def base3zeros(x):
    z=0
    while x: 
        if x%3==0: z+=1
        x//=3
    return z
bad=[]; N=6000
for n in range(0,N+1):
    if base3zeros(2**n)==0: bad.append(n)
print("n<=%d with a(n)=0:"%N, bad, " -> violations of 'n>15 => a(n)>0':", [n for n in bad if n>15])

# --- A109905 : {n>0 | a n = 0}
hdr("A109905  greatest prime k(n-k)+1")
zer=[]; N=20000
for n in range(1,N+1):
    ok=False
    for k in range(1,n//2+1):
        if is_prime(k*(n-k)+1): ok=True; break
    if not ok: zer.append(n)
print("n<=%d with a(n)=0:"%N, zer)
