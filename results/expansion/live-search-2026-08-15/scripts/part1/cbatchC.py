import sys, math
sys.path.insert(0,'/Users/kuber.mehta/Projects/c5-k4/results/expansion/live-search-2026-08-15/scripts')
from nt import is_prime

print("### A001146: k>1 with (k^4-1) | (2^k-1) must be 2^(2^n), n>=2")
hits=[]
for k in range(2,2_000_001):
    m=k*k*k*k-1
    if m%2==0: continue          # 2^k-1 odd => k^4-1 must be odd => k even; k^4-1 odd iff k even
    if pow(2,k,m)==1: hits.append(k)
print("  k in 2..2e6 with k^4-1 | 2^k-1 :",hits)
allowed={2**(2**n) for n in range(2,6)}
print("  allowed set {2^(2^n): n>=2} ∩ range:",sorted(x for x in allowed if x<=2_000_000))
print("  violations:",[k for k in hits if k not in allowed])

print("### A113010: a n = (#digits n)^(digitsum n); conj a n = n & n>0 -> n in {1,32}")
sol=[]
for n in range(1,10_000_000):
    s=str(n); v=len(s)**sum(int(c) for c in s)
    if v==n: sol.append(n)
print("  n<=10^7 with a n = n:",sol)
# provable bound: d digits => n >= 10^(d-1), digitsum <= 9d, so d^(9d) >= 10^(d-1) needed and d^s=n
extra=[]
for d in range(1,40):
    for s in range(0,9*d+1):
        v=d**s
        if v>0 and len(str(v))==d and sum(int(c) for c in str(v))==s:
            extra.append((d,s,v))
print("  exhaustive over (numdigits d<=39, digitsum s<=9d):",extra)

print("### A114216: a(0)=0, a(n)= odd part of a(n-1)+prime(n); conj: forall n>33900, a n != 1")
import numpy as np
LIM=20_000_000
pr=np.ones(LIM,dtype=bool); pr[:2]=False
for i in range(2,int(LIM**0.5)+1):
    if pr[i]: pr[i*i::i]=False
P=np.flatnonzero(pr)
print("  primes available:",len(P))
a=0; ones=[]
for n in range(1,len(P)+1):
    a=a+int(P[n-1])
    while a%2==0: a//=2
    if a==1: ones.append(n)
print("  n with a(n)=1, n<=%d: last 12 = %s ; count %d"%(len(P),ones[-12:],len(ones)))
print("  violations (n>33900 with a n = 1):",[n for n in ones if n>33900][:20])
