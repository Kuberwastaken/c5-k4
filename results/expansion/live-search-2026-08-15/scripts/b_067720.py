import time, numpy as np
from nt import is_prime
t0=time.time()
LIM=5_000_000
phi=np.load('phi.npy')
# need phi(k^2+1) for k up to K where k^2+1 <= LIM  -> k <= 2236
K=int((LIM-1)**0.5)
res=[]
for k in range(1,K+1):
    if phi[k*k+1]==k*phi[k+1]: res.append(k)
print("A067720 members k<=%d:"%K, res, " (t=%.1fs)"%(time.time()-t0))
bad=[k for k in res if k!=8 and not is_prime(k+1)]
print("members k != 8 with k+1 NOT prime:", bad)
