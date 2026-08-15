import sys, math
sys.set_int_max_str_digits(2000000)
sys.path.insert(0,'/Users/kuber.mehta/Projects/c5-k4/results/expansion/live-search-2026-08-15/scripts')
from nt import is_prime
import time

print("### A103662 variant a_40 : no b>1 with b^40 zeroless in decimal")
t0=time.time(); found=[]
b=2
while time.time()-t0<120:
    if '0' not in str(b**40): found.append(b)
    b+=1
print("  bases scanned: 2..%d ; zeroless b^40 found: %s"%(b-1,found))

print("### A000041 : any partition number a perfect power (k^m, k>1,m>1)?")
t0=time.time()
NP=60000
p=[0]*(NP+1); p[0]=1
for n in range(1,NP+1):
    s=0;k=1
    while True:
        g1=k*(3*k-1)//2; g2=k*(3*k+1)//2
        if g1>n and g2>n: break
        sgn=-1 if k%2==0 else 1
        if g1<=n: s+=sgn*p[n-g1]
        if g2<=n: s+=sgn*p[n-g2]
        k+=1
    p[n]=s
def isperfpow(v):
    if v<4: return False
    for m in range(2,v.bit_length()+1):
        r=round(v**(1.0/m)) if v< 10**300 else None
        if r is None:
            lo,hi=1,1<<((v.bit_length()//m)+2)
            while lo<hi:
                mid=(lo+hi)//2
                if mid**m<v: lo=mid+1
                else: hi=mid
            r=lo
        for c in (r-1,r,r+1):
            if c>1 and c**m==v: return True
    return False
hits=[n for n in range(0,NP+1) if isperfpow(p[n])]
print("  p(n) for n=0..%d : perfect powers at n = %s (time %.1fs)"%(NP,hits,time.time()-t0))
print("  p(0..10):",p[:11])

print("### A001157 : Sun conjecture, distinct fract(sigma_k(n)/n^k)")
from fractions import Fraction
for K in (2,3,4,5):
    seen={}; coll=[]
    N=300000
    # sigma_k via divisor sieve on small N
    sk=[0]*(N+1)
    for d in range(1,N+1):
        dk=d**K
        for m in range(d,N+1,d): sk[m]+=dk
    for n in range(1,N+1):
        f=Fraction(sk[n],n**K)
        fr=f-int(f)
        if fr in seen: coll.append((K,seen[fr],n,fr))
        else: seen[fr]=n
    print("  k=%d, n<=%d : collisions %s"%(K,N,coll[:5]))
