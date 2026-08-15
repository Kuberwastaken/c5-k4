import sys,time
sys.set_int_max_str_digits(200000)
sys.path.insert(0,'/Users/kuber.mehta/Projects/c5-k4/results/expansion/live-search-2026-08-15/scripts')
from nt import is_prime, sieve_primes
import numpy as np
s=sieve_primes(3000)
P=np.flatnonzero(s).tolist()
def a(n):
    if n==0: return 0
    pN=P[n-1]
    bits=[1 if (i>=2 and s[i]) else 0 for i in range(pN+1)]
    # dropWhile (=0)
    i=0
    while i<len(bits) and bits[i]==0: i+=1
    tr=bits[i:]
    return int(''.join(str(b) for b in tr))
print("a(1..12):",[a(n) for n in range(1,13)])
print("OEIS head:[1,11,1101,110101,1101010001,110101000101,1101010001010001,110101000101000101,1101010001010001010001,1101010001010001010001000001,110101000101000101000100000101,110101000101000101000100000101000001]")
print("match:",[str(a(n)) for n in range(1,13)]==['1','11','1101','110101','1101010001','110101000101','1101010001010001','110101000101000101','1101010001010001010001','1101010001010001010001000001','110101000101000101000100000101','110101000101000101000100000101000001'])
t0=time.time(); primes=[]
n=1
while n<=260 and time.time()-t0<240:
    v=a(n)
    if v>1 and n%3!=0 and is_prime(v): primes.append(n)
    n+=1
print("n scanned 1..%d ; n with a(n) prime: %s  (%.0fs)"%(n-1,primes,time.time()-t0))
