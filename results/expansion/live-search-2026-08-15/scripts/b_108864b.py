# INDEPENDENT recomputation: no sieve, direct divisor-sum by trial division.
def sigma(n):
    s=0; d=1
    while d*d<=n:
        if n%d==0:
            s+=d
            e=n//d
            if e!=d: s+=e
        d+=1
    return s
mem=[]
n=0
while len(mem)<=100:
    n+=1
    if abs(sigma(n)-2*n)<=10: mem.append(n)
print("Lean-predicate members, 0-indexed a(50..100):")
for i in range(50,101):
    print("   a(%d) = %d   %s"%(i,mem[i], "ODD" if mem[i]%2 else ""))
