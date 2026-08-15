import time
from nt import is_prime, sieve_primes
import numpy as np
t0=time.time()
s=sieve_primes(3_000_000); pr=np.flatnonzero(s)
def tri(n): return n*(n+1)//2
a={1:1}
res=[]
for n in range(2,26):
    lo=tri(n-1)-1; hi=tri(n)-1
    if hi>len(pr): break
    P=1
    for i in range(lo,hi): P*=int(pr[i])
    a[n]=P-a[n-1]
    res.append((n,a[n],is_prime(a[n])))
print("a(1..5):",[a[k] for k in range(1,6)])
for n,v,p in res:
    if p: print("  PRIME at n=%d: %d"%(n,v))
print("n range checked: 2..%d ; primes found for n>2:"%res[-1][0], [n for n,v,p in res if p and n>2])
print("digits of a(n):",[(n,len(str(v))) for n,v,p in res][-3:])
