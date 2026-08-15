from fractions import Fraction
import sys
sys.path.insert(0,'/Users/kuber.mehta/Projects/c5-k4/results/expansion/live-search-2026-08-15/scripts')
from nt import is_prime
bad=[];rows=[]
S=Fraction(0)
for n in range(1,1201):
    S+=Fraction(2**n,n)
    if n<=3: continue
    r=S-Fraction(2,n)
    num=r.numerator
    lhs=(num%(n*n)==0)
    rhs=is_prime(n)
    if n<=20: rows.append((n,num%(n*n),rhs))
    if lhs!=rhs: bad.append((n,lhs,rhs,num%(n*n)))
print("sample (n, num mod n^2, isPrime):",rows)
print("A108866 conjecture violations for n=4..1200:",bad[:20],"count",len(bad))
