import time, numpy as np
t0=time.time()
LIM=5_000_000
# sigma_1 sieve
sig=np.zeros(LIM+1,dtype=np.int64)
for d in range(1,LIM+1):
    sig[d::d]+=d
print("sigma sieve %.1fs"%(time.time()-t0))
# totient sieve
phi=np.arange(LIM+1,dtype=np.int64)
for p in range(2,LIM+1):
    if phi[p]==p:
        phi[p::p]-= phi[p::p]//p
print("phi sieve %.1fs"%(time.time()-t0))
np.save('sig.npy',sig); np.save('phi.npy',phi)

# ---- A056777: composite n with phi(n+12)=phi(n)+12 and sigma(n+12)=sigma(n)+12
print("\n### A056777")
N=LIM-12
isp=np.ones(LIM+1,dtype=bool); isp[:2]=False
for i in range(2,int(LIM**0.5)+1):
    if isp[i]: isp[i*i::i]=False
n=np.arange(2,N+1)
mask=(~isp[2:N+1]) & (phi[14:N+13]==phi[2:N+1]+12) & (sig[14:N+13]==sig[2:N+1]+12)
members=n[mask]
print("A056777 members <= %d:"%N, members[:40].tolist(), "count",len(members))
# check each comes from a prime quadruple p,p+2,p+6,p+8 with n=p(p+8)
bad=[]
for v in members.tolist():
    ok=False
    # p(p+8)=v -> p = -4+sqrt(16+v)
    import math
    disc=16+v; r=math.isqrt(disc)
    if r*r==disc and r>=4:
        p=r-4
        if p>=2 and isp[p] and p+8<=LIM and isp[p+2] and isp[p+6] and isp[p+8] and p*(p+8)==v: ok=True
    if not ok: bad.append(v)
print("members NOT of the form p(p+8) with (p,p+2,p+6,p+8) all prime:", bad[:20], "count",len(bad))
print("mod 72 of members:", sorted(set(int(v)%72 for v in members.tolist())))
print("t=%.1fs"%(time.time()-t0))
