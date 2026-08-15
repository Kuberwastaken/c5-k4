# Independent re-derivation: no shared code with probe_d.py.
# Brute force over (q,a) directly, a allowed to exceed q (no sliding-window logic).
from math import gcd, isqrt
def issq(x): 
    r=isqrt(x); return r*r==x
def Q(N,q,a): return sum(1 for n in range(N) if issq(q*n+a))
def nontrivial(q,a): return q>=1 and a>=1 and gcd(q,a)==1 and (q,a)!=(1,1)

print("=== direct term listing ===")
for (q,a) in [(24,1),(120,49),(168,121),(8,1)]:
    terms=[q*n+a for n in range(6)]
    print(f"q={q} a={a} gcd={gcd(q,a)} terms={terms} squares={[t for t in terms if issq(t)]} Q6={Q(6,q,a)}")

print("=== brute force Qmax(N) over q<=3000, a<=q*(N+40) ===")
NMAX=30
best={N:0 for N in range(1,NMAX+1)}
arg={N:set() for N in range(1,NMAX+1)}
QB=3000
for q in range(1,QB+1):
    amax=q*(NMAX+60)+2000
    # only a with gcd(q,a)=1; iterate a over squares' residues implicitly by scanning a
    # scan a from 1..amax is too big for large q; instead scan squares
    # positions: for each square s, n=(s-a)/q ; enumerate a as s - q*n for n in 0..N-1
    maxm=isqrt(q*(NMAX)+amax)+2
    from collections import defaultdict
    byres=defaultdict(list)
    for m in range(1,maxm+1):
        s=m*m
        byres[s%q].append(s)
    for r,lst in byres.items():
        L=len(lst)
        for i in range(L):
            a=lst[i]
            if not nontrivial(q,a): continue
            for N in range(1,NMAX+1):
                c=sum(1 for s in lst[i:] if (s-a)%q==0 and 0<=(s-a)//q<N)
                if c>best[N]: best[N]=c; arg[N]={(q,a)}
                elif c==best[N] and len(arg[N])<15: arg[N].add((q,a))
    if q%500==0: print(" q",q,flush=True)
print("N Qmax Q(N;24,1) distinct-q-attaining")
for N in range(6,NMAX+1):
    qs=sorted({q for q,_ in arg[N]})
    print(N, best[N], Q(N,24,1), qs, "UNIQUE-FAILS" if qs!=[24] else "")
