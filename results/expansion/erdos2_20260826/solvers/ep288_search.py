import sys
from fractions import Fraction
N=int(sys.argv[1]) if len(sys.argv)>1 else 500
S=[Fraction(0)]*(N+1)
for n in range(1,N+1): S[n]=S[n-1]+Fraction(1,n)
sols=[]
for a in range(1,N+1):
    for b in range(a,min(N,a+400)+1):
        r=S[b]-S[a-1]
        # single-number second "interval": c in [a..N]
        for c in range(1,N+1):
            v=r+Fraction(1,c)
            if v.denominator==1:
                sols.append((a,b,c,int(v)))
print(f"interval+[c] integer-sum solutions with all values <= {N}: {len(sols)}")
print(sols[:30])
# pure two-interval check would be heavier; record single-interval sanity: only ({1}) sums integer
one=[(a,b) for a in range(1,N+1) for b in range(a,min(N,a+400)+1) if (S[b]-S[a-1]).denominator==1]
print("single-interval integer sums:", one)
