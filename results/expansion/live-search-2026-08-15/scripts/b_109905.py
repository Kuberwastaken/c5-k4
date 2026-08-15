import time
from nt import is_prime
t0=time.time(); zer=[]; N=0
while time.time()-t0 < 45:
    N+=1
    ok=False
    for k in range(1,N//2+1):
        if is_prime(k*(N-k)+1): ok=True; break
    if not ok: zer.append(N)
print("searched n=1..%d in %.1fs"%(N,time.time()-t0))
print("n>0 with a(n)=0:", zer)
print("conjecture set {1,6,30,54} ; extra found:", [z for z in zer if z not in (1,6,30,54)])
