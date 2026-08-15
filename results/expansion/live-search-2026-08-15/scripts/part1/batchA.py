import numpy as np, sys
LIM=10_000_001
sig=np.load('sig10m.npy'); phi=np.load('phi10m.npy')
prime=np.ones(LIM,dtype=bool); prime[:2]=False
for i in range(2,int(LIM**0.5)+1):
    if prime[i]: prime[i*i::i]=False

print("### A067720: A k :  phi(k^2+1) = k*phi(k+1) ; conj: k!=8 -> (k+1) prime")
# need phi(k^2+1) -> k^2+1 up to 10^7 => k <= 3162
hits=[]
for k in range(0,3163):
    if phi[k*k+1]==k*phi[k+1]: hits.append(k)
print("  A-terms k<=3162:",hits)
print("  violations (k!=8 and k+1 composite):",[k for k in hits if k!=8 and not (k+1<LIM and prime[k+1])])

print("### A056777: composite n, phi(n+12)=phi(n)+12, sigma(n+12)=sigma(n)+12 -> n=p(p+8) prime quadruple")
N=LIM-13
n=np.arange(N,dtype=np.int64)
mask=(n>1)&(~prime[:N])&(phi[12:12+N]==phi[:N]+12)&(sig[12:12+N]==sig[:N]+12)
terms=np.flatnonzero(mask)
print("  A056777 terms up to %d (count %d):"%(N,len(terms)),terms[:30].tolist())
def quad(nv):
    for p in range(2,int(nv**0.5)+2):
        if p*(p+8)==nv:
            return prime[p] and prime[p+2] and prime[p+6] and prime[p+8]
    return False
bad=[int(t) for t in terms.tolist() if not quad(int(t))]
print("  violations (not p(p+8) with prime quadruple):",bad[:20],"count",len(bad))

print("### A109905: {n>0 : a n = 0} == {1,6,30,54} ?")
NB=2_000_000
zeros=[]
for nv in range(1,NB):
    z=True
    for k in range(1,nv//2+1):
        v=k*(nv-k)+1
        if v<LIM and prime[v]: z=False;break
        if v>=LIM:
            # fallback MR
            import math
            x=v; ok=True
            for q in (2,3,5,7,11,13,17,19,23,29,31,37):
                if x%q==0: ok=(x==q);break
            else:
                d=x-1;s=0
                while d%2==0: d//=2;s+=1
                for aa in (2,3,5,7,11,13,17,19,23,29,31,37):
                    y=pow(aa,d,x)
                    if y==1 or y==x-1: continue
                    for _ in range(s-1):
                        y=y*y%x
                        if y==x-1: break
                    else: ok=False;break
            if ok: z=False;break
    if z: zeros.append(nv)
    if nv%200000==0: print("   ...n=%d zeros so far %s"%(nv,zeros))
print("  zeros up to %d:"%NB, zeros)
print("  equals {1,6,30,54}?", zeros==[1,6,30,54])
