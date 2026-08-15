from fractions import Fraction
from nt import is_prime
import time
t0=time.time()
S=Fraction(0); bad=[]
vals={}
for n in range(1,3001):
    S += Fraction(2**n, n)
    if n>3:
        q = S - Fraction(2,n)
        num = q.numerator
        cond = (num % (n*n) == 0)
        p = is_prime(n)
        if cond != p: bad.append((n,cond,p,num % (n*n)))
    if time.time()-t0>45: break
print("checked n=4..%d in %.1fs"%(n,time.time()-t0))
print("counterexamples (n, num%%n^2==0, isprime):", bad[:20], " count",len(bad))
