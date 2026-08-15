import numpy as np
LIM=20_000_000
prime=np.ones(LIM,dtype=bool); prime[:2]=False
for i in range(2,int(LIM**0.5)+1):
    if prime[i]: prime[i*i::i]=False
pc=np.cumsum(prime)   # pc[x] = #primes <= x
def a(n):
    m=1
    while n*(m+1)<LIM:
        lo=n*m; hi=n*(m+1)
        if pc[hi]-(pc[lo-1] if lo>0 else 0)==0: return m
        m+=1
    return None
NB=8000
bad=[];unres=0
for n in range(1,NB+1):
    v=a(n)
    if v is None: unres+=1; continue
    if v<n: bad.append((n,v))
print("A110835 a(1..20):",[a(n) for n in range(1,21)])
print("OEIS DATA head:  [8,4,8,6,18,15,17,25,13,20,29,44,87,81,35,83,79,74,70,67]")
print("Sierpinski violations a(n)<n for n=1..%d:"%NB,bad[:10],"count",len(bad),"unresolved",unres)
