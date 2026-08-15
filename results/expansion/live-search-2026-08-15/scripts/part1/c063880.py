import numpy as np
LIM=10_000_001
sig=np.load('sig10m.npy')
# unitary sigma: usigma(n)=prod (1+p^e).  Build by sieving prime powers.
us=np.ones(LIM,dtype=np.int64)
isc=np.zeros(LIM,dtype=bool)
p=2
prime=np.ones(LIM,dtype=bool); prime[:2]=False
for i in range(2,int(LIM**0.5)+1):
    if prime[i]: prime[i*i::i]=False
for p in np.flatnonzero(prime).tolist():
    # for each n, multiply by (1+p^e) where p^e || n
    pe=p
    while pe<LIM:
        nxt=pe*p
        # n divisible by pe but not by nxt
        idx=np.arange(pe,LIM,pe)
        if nxt<LIM:
            mask=(idx % nxt)!=0
            idx=idx[mask]
        us[idx]*= (1+pe)
        if nxt>=LIM: break
        pe=nxt
n=np.arange(LIM,dtype=np.int64)
A=(n>0)&(sig==2*us)
terms=np.flatnonzero(A)
print("A063880 terms up to 10^7 (count %d):"%len(terms),terms[:40].tolist())
bad=terms[terms%216!=108]
print("terms with n%216 != 108 :",bad[:20].tolist(),"count",len(bad))
# primitive terms: n in A and no proper divisor in A
Aset=set(terms.tolist())
prim=[]
for t in terms.tolist():
    ok=True
    for d in range(1,int(t**0.5)+1):
        if t%d==0:
            if d!=t and d in Aset: ok=False;break
            e=t//d
            if e!=t and e in Aset: ok=False;break
    if ok: prim.append(t)
print("primitive terms:",prim)
print("unique_primitive_108 violations:",[x for x in prim if x!=108])
