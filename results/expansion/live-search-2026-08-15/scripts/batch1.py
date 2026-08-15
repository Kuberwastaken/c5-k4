import sys, time
sys.setrecursionlimit(100000)
from nt import is_prime, is_square, factorint

def hdr(t): print("\n########## "+t)

# ---------------- A100434 ----------------
hdr("A100434  c/d/b/e/f/g conjectures")
def lin(i0,i1,i2,i3,N=40):
    s=[i0,i1,i2,i3]
    for n in range(N): s.append(-6*s[n+2]-s[n])
    return s
c=lin(1,-3,-7,17); d=lin(2,4,-10,-24); a=lin(3,4,-17,-24)
b=[c[n+1] if n%2==0 else c[n-1] for n in range(1,30)]  # careful n=0
b=[]
for n in range(30):
    b.append(c[n+1] if n%2==0 else c[n-1])
e=[]
for n in range(30):
    e.append(d[n]//2 if n%2==0 else -(d[n-1]//2))
f=[]
for n in range(30):
    m=n//2; f.append(d[2*m+1]//2)
g=[0 if n%2==0 else c[n] for n in range(30)]
print("c ",c[:13]); print("d ",d[:12]); print("a ",a[:8])
print("b ",b[:12]); print("e ",e[:14]); print("f ",f[:12]); print("g ",g[:16])
for name,lhs in (("conj1 c+d",[c[n]+d[n] for n in range(30)]),
                 ("conj2 e+f",[e[n]+f[n] for n in range(30)]),
                 ("conj3 g+a",[g[n]+a[n] for n in range(30)])):
    bad=[n for n in range(30) if lhs[n]!=b[n]]
    print(f"  {name}: first 8 lhs={lhs[:8]}  b={b[:8]}  FAILING n (n<30) = {bad[:12]}")
    if bad: n=bad[0]; print(f"    smallest failure n={n}: lhs={lhs[n]} b={b[n]} (b={'c[%d]'%(n+1) if n%2==0 else 'c[%d]'%(n-1)})")

# ---------------- A102371 ----------------
hdr("A102371  a(n) = 2^n-1-A105033(n-1)")
def A102371(N):
    s=[0,1]
    for n in range(2,N+1): s.append(s[n-1]^(s[n-1]+n))
    return s
def A105033(N):
    # a(n) = n - sum_{k>=0, 2^(k+1)<=n, n == k mod 2^(k+1)} 2^(k+1)
    out=[]
    for n in range(N+1):
        s=0; k=0
        while 2**(k+1)<=n:
            if n % 2**(k+1) == k % 2**(k+1): s+=2**(k+1)
            k+=1
        out.append(n-s)
    return out
N=400
A1=A102371(N); A2=A105033(N)
print("A102371[1..12]",A1[1:13]); print("A105033[0..21]",A2[:22])
bad=[n for n in range(1,N+1) if A1[n] != (2**n-1) - A2[n-1] if (2**n-1)>=A2[n-1]]
bad2=[n for n in range(1,N+1) if A2[n-1] > 2**n-1]
print("mismatches n<=%d:"%N, bad[:10], " truncating-sub cases:", bad2[:5])

# ---------------- A108306 ----------------
hdr("A108306  INVERT transform == matrix power")
def invertD(A,B,N):
    def c(k):
        if k==0: return 0
        if k==1: return 1
        return A*B**(k-2)
    d=[1]
    for m in range(1,N+1):
        d.append(sum(c(m-i)*d[i] for i in range(m)))
    return d
def matpow00(A,B,n):
    M=[[1,0],[0,1]]; G=[[1,A],[1,B]]
    for _ in range(n):
        M=[[M[0][0]*G[0][0]+M[0][1]*G[1][0], M[0][0]*G[0][1]+M[0][1]*G[1][1]],
           [M[1][0]*G[0][0]+M[1][1]*G[1][0], M[1][0]*G[0][1]+M[1][1]*G[1][1]]]
    return M[0][0]
bad=[]
for A in range(0,13):
    for B in range(0,13):
        D=invertD(A,B,25)
        for n in range(0,26):
            if D[n]!=matpow00(A,B,n): bad.append((A,B,n,D[n],matpow00(A,B,n)))
print("a,b in 0..12, n<=25: mismatches =", bad[:6], "count",len(bad))

# ---------------- A110475 ----------------
hdr("A110475  sums of two indices with a(n)=1")
LIM=200000
import numpy as np
spf=np.zeros(LIM+1,dtype=np.int32)
for i in range(2,LIM+1):
    if spf[i]==0: spf[i::i]=np.where(spf[i::i]==0,i,spf[i::i])
def aval(n):
    if n<2: return 0
    m=n; fac={}
    while m>1:
        p=int(spf[m]); fac[p]=fac.get(p,0)+1; m//=p
    k=len(fac); return (k-1 if k>=1 else 0) + sum(1 for p in fac if fac[p]>1)
S=set(n for n in range(2,LIM+1) if aval(n)==1)
Ssort=sorted(S)
print("S (a(n)=1) first 22:",Ssort[:22])
MAXM=20000
rep=set()
for x in Ssort:
    if x>MAXM: break
    for y in Ssort:
        if x+y>MAXM: break
        rep.add(x+y)
miss=[m for m in range(1,MAXM+1) if m not in rep]
print("m in 1..%d NOT a sum of two S-elements:"%MAXM, miss)
print("exceptionalSet = [1,2,3,4,5,6,7,9,11]; match:", miss==[1,2,3,4,5,6,7,9,11])

# ---------------- A112521 ----------------
hdr("A112521  a(n) == T(n,n)")
from math import comb
def a112521(n):
    tot=0
    for j in range(n):
        c1=comb(2*j,j); c2=comb(2*n-(j+2), n-(j+1)) if 2*n-(j+2)>=0 else 0
        t=c1*c2
        tot += t if j%2==0 else -t
    return max(tot,0), tot   # Lean .toNat, raw
from functools import lru_cache
@lru_cache(maxsize=None)
def T(n,k):
    if n==0 or k==0: return 0
    if n==1 and k==1: return 1
    return T(n,max(k-2,0))+T(n,k-1)-2*T(max(n-1,0),max(k-1,0))+T(max(n-1,0),k)+T(max(n-2,0),k)
print(" n | a_toNat | a_raw | T(n,n)")
bad=[]
for n in range(1,26):
    at,ar=a112521(n); t=T(n,n)
    if at!=t: bad.append((n,at,ar,t))
    if n<=14: print(f" {n:2d} | {at} | {ar} | {t}")
print("mismatches n<=25:",bad[:8])
