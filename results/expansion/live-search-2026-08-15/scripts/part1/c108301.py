import sys
import sys as _s; _s.set_int_max_str_digits(2000000)
sys.path.insert(0,'/Users/kuber.mehta/Projects/c5-k4/results/expansion/live-search-2026-08-15/scripts')
from nt import is_prime
oeis=[3,5,8,14,26,59,89,167,377,734,1376,2741,5624,11120,22166,44222,88262,176180,353042,707648,1419974,2836751,5679620,11365592,22723865,45445442,90899234,181828850]
# recompute digit sums independently for n=0..21 (2^(2^21)+1 has ~631306 digits; keep to n<=20)
comp=[]
for n in range(0,19):
    v=2**(2**n)+1
    comp.append(sum(int(c) for c in str(v)))
print("recomputed a(0..20):",comp)
print("OEIS    a(0..20):",oeis[:19])
print("match:",comp==oeis[:19])
print("primality of a(n) for n>11 (OEIS DATA up to n=27):")
for n in range(12,28):
    print("   n=%2d a=%d prime=%s"%(n,oeis[n],is_prime(oeis[n])))
print("primes among n<=11:",[(n,oeis[n]) for n in range(12) if is_prime(oeis[n])])
