from decimal import Decimal, getcontext
import math, sys
sys.path.insert(0,'/Users/kuber.mehta/Projects/c5-k4/results/expansion/live-search-2026-08-15/scripts')
from nt import is_prime
# Chudnovsky-free: use integer pi digits via arctan (Machin) with big ints
D=3005
scale=10**(D+20)
def arctan_inv(x, one):
    total=term=one//x; x2=x*x; n=1; sign=-1
    while term:
        term//=x2; t=term//(2*n+1)
        total+= sign*t; sign=-sign; n+=1
    return total
one=scale
pi=4*(4*arctan_inv(5,one)-arctan_inv(239,one))
pistr=str(pi)  # digits of pi*10^(D+20)
# a(n) = floor(pi*10^n) = int of first n+1 digits
sq=[]
for n in range(0,D):
    a=int(pistr[:n+1])
    r=math.isqrt(a)
    if r*r==a: sq.append((n,a))
print("A011545 a(0..8):",[int(pistr[:n+1]) for n in range(9)])
print("OEIS head     : [3,31,314,3141,31415,314159,3141592,31415926,314159265]")
print("conjecture1 (no a(n) is a perfect square): squares found for n<%d :"%D, sq)
# conjecture2: integer strictly inside (pi*10^n, pi/arctan(1/10^n)) ?
# pi/arctan(1/m) with m=10^n, computed to high precision using integer arithmetic
getcontext().prec=D+40
PI=Decimal(pi)/Decimal(scale)
viol=[]
for n in range(0,600):
    m=Decimal(10)**n
    # arctan(1/m) = 1/m - 1/(3m^3) + 1/(5m^5) - ...
    inv=Decimal(1)/m; term=inv; s=Decimal(0); k=0; sign=1
    while True:
        t=term/(2*k+1)
        if t==0: break
        s+=sign*t; sign=-sign; k+=1; term=term/(m*m)
        if k>60: break
    hi=PI/s; lo=PI*m
    import math as _m
    lo_f=lo; hi_f=hi
    # integers strictly between
    import decimal
    lo_i=int(lo_f.to_integral_value(rounding=decimal.ROUND_FLOOR))
    cand=lo_i+1
    if Decimal(cand)>lo_f and Decimal(cand)<hi_f: viol.append((n,cand,str(lo_f)[:25],str(hi_f)[:25]))
print("conjecture2 violations (integer in (pi*10^n, pi/arctan(10^-n))) for n<600:",viol[:5],"count",len(viol))
print("  sample n=0: lo,hi =",str(PI)[:12], str(PI/(Decimal(1).atan() if False else Decimal(0)+ (Decimal(1)) ))[:0])
