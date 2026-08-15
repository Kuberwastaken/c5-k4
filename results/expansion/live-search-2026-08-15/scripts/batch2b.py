import sys,time
from nt import is_prime
t0=time.time()
# --- A109905 : {n>0 | a n = 0}
hdr("A109905  greatest prime k(n-k)+1")
zer=[]; N=20000
for n in range(1,N+1):
    ok=False
    for k in range(1,n//2+1):
        if is_prime(k*(n-k)+1): ok=True; break
    if not ok: zer.append(n)
print("n<=%d with a(n)=0:"%N, zer)
