import sys
from sympy import factorint
B=int(sys.argv[1]); ks=[(3,3),(4,4)]
def supp(a,b):
    s=set()
    for m in range(a+1,b+1):
        if m>1: s|=set(factorint(m).keys())
    return frozenset(s)
for (k1,k2) in ks:
    sols=[]
    for n1 in range(0,min(B,1500)+1):
        s1=supp(n1,n1+k1)
        for n2 in range(n1+k1, min(B-k2+1, 3000)):
            if supp(n2,n2+k2)==s1 and s1:
                sols.append((n1,n2))
    print(f"k=({k1},{k2}): {len(sols)}: {sols}", flush=True)
