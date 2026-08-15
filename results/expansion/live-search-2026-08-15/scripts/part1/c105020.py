import math
from collections import defaultdict
N=400000
def a(n):  # exact replay of Lean defs (Nat.sqrt = isqrt, ℕ subtraction)
    c=(math.isqrt(8*n+1)-1)//2
    k=n-(c*(c+1)//2)
    i=c-k if c>=k else 0
    m=c+1
    return m*m-i*i if m*m>=i*i else 0
# Omega sieve for semiprime test (n>1 and Omega(n)==2)
LIM=4_000_005
om=[0]*(LIM)
for p in range(2,LIM):
    if om[p]==0:
        for q in range(p,LIM,p):
            x=q
            while x%p==0:
                om[q]+=1; x//=p
def issemi(x): return x>1 and x<LIM and om[x]==2
vals=[a(n) for n in range(N)]
print("a(0..15):",vals[:16])
oeis=[1,3,4,5,8,9,7,12,15,16,9,16,21,24,25,11,20,27,32,35,36,13,24,33,40,45,48,49]
print("match OEIS DATA head:", vals[:len(oeis)]==oeis)
pos=defaultdict(list)
for n,v in enumerate(vals): pos[v].append(n)
fails=[]
checked=0
maxn=(max(vals)-3)//2
for n in range(1,3000):
    for i in pos.get(2*n+1,[]):
        j=i+n+1
        if j>=N: continue
        if vals[j]!=2*n+3: continue
        checked+=1
        if not any(issemi(vals[k]) for k in range(i+1,j)):
            fails.append((n,i,j,[vals[k] for k in range(i+1,j)]))
print("premise-satisfying (n,i,j) triples checked:",checked)
print("FAILURES:",len(fails))
for f in fails[:10]: print("   n=%d i=%d j=%d  a(i)=%d a(j)=%d  interior a(k)=%s"%(f[0],f[1],f[2],2*f[0]+1,2*f[0]+3,f[3]))
