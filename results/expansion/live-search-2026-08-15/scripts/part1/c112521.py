import sys
from functools import lru_cache
from math import comb
sys.setrecursionlimit(100000)
NM=90
# Lean a n  (exact, incl. .toNat)
def a_lean(n):
    s=0
    for j in range(n):
        c1=comb(2*j,j)
        c2top=max(0,2*n-(j+2)); c2bot=max(0,n-(j+1))
        c2=comb(c2top,c2bot) if c2bot<=c2top else 0
        t=c1*c2
        s+= t if j%2==0 else -t
    return max(s,0), s     # (toNat, raw)
# Lean T with Nat truncated subtraction on indices
T={}
def Tf(n,k):
    if n==0 or k==0: return 0
    if n==1 and k==1: return 1
    key=(n,k)
    if key in T: return T[key]
    v=Tf(n,max(k-2,0))+Tf(n,k-1)-2*Tf(n-1,k-1)+Tf(n-1,k)+Tf(max(n-2,0),k)
    T[key]=v; return v
# iterative fill to avoid recursion depth
for n in range(0,NM+1):
    for k in range(0,NM+1):
        Tf(n,k)
oeis=[0,1,0,6,4,60,84,700,1440,8910,23100,120120,360360,1684956,5552064,24302520,85101456,357502860,1302562404,5333981796,19947127200,80408748420,305922388200,1221485157360,4701015343440,18664243014300]
bad=[]
for n in range(1,NM+1):
    an,raw=a_lean(n); t=Tf(n,n)
    if an!=t: bad.append((n,an,raw,t))
print("a_lean(0..15):",[a_lean(n)[0] for n in range(16)])
print("OEIS   (0..15):",oeis[:16])
print("match OEIS a:", [a_lean(n)[0] for n in range(len(oeis))]==oeis)
print("T(n,n) n=1..15:",[Tf(n,n) for n in range(1,16)])
print("mismatches a n vs T n n, n=1..%d:"%NM, bad[:8], "count",len(bad))
print("any raw sum negative (toNat damage)?", [n for n in range(1,NM+1) if a_lean(n)[1]<0][:5])
