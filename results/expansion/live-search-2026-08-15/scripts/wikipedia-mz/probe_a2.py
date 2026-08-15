import numpy as np, time, sys
t0=time.time()
M = 6_000_000
sig = np.zeros(M+1, dtype=np.int64)
for d in range(1, M+1):
    sig[d::d] += d
print("sieve", time.time()-t0, file=sys.stderr)
N = M//5   # need sigma(n) <= M ; sigma(n) < 5n for n in range mostly; guard below
hits=[]; skipped=0
for n in range(1, N+1):
    s = sig[n]
    if s > M: skipped+=1; continue
    if sig[s] == 5*n: hits.append(n)
print("A: sigma(sigma(n))==5n for n<=%d -> %s (skipped %d)" % (N, hits[:30], skipped))
# control: reproduce known (2,k)-perfect rows to validate the code
for k in (2,3,4,6,7):
    hs=[n for n in range(1,200001) if sig[n]<=M and sig[int(sig[n])]==k*n]
    print("control (2,%d)-perfect n<=200000:"%k, hs[:12])
print("elapsed", time.time()-t0)
