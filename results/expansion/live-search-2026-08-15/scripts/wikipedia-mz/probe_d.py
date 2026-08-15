import numpy as np, time, math, sys
from math import gcd, isqrt
t0=time.time()
NMAX=int(sys.argv[1]) if len(sys.argv)>1 else 40
QMAX=int(sys.argv[2]) if len(sys.argv)>2 else 20000
SAFE=int(sys.argv[3]) if len(sys.argv)>3 else 4
best={N:(0,[]) for N in range(1,NMAX+1)}   # N -> (Qmax, list of (q,a))
def consider(N,cnt,q,a):
    b,lst=best[N]
    if cnt>b: best[N]=(cnt,[(q,a)])
    elif cnt==b and (q,a) not in lst and len(lst)<12: lst.append((q,a))

# q = 1 : AP is a, a+1, ...  ; a >= 1 but (1,1) excluded -> a >= 2
MB=isqrt(SAFE*QMAX*NMAX)+2
sq_all=np.arange(1,MB+1,dtype=np.int64)**2
for N in range(1,NMAX+1):
    # squares in window [a, a+N-1], a>=2
    s=sq_all[sq_all<=SAFE*NMAX*4+10**6]
    bestc=0;besta=None
    for a in range(2, 4000):
        c=int(((s>=a)&(s<=a+N-1)).sum())
        if c>bestc: bestc=c;besta=a
    consider(N,bestc,1,besta)

for q in range(2,QMAX+1):
    mb=isqrt(SAFE*q*NMAX)+2
    m=np.arange(1,mb+1,dtype=np.int64); sq=m*m
    r=sq % q
    o=np.argsort(r,kind='stable')
    rr=r[o]; ss=sq[o]
    # residue blocks
    cut=np.flatnonzero(np.diff(rr))+1
    st=np.concatenate([[0],cut]); en=np.concatenate([cut,[len(rr)]])
    for bi in range(len(st)):
        a=int(rr[st[bi]])
        if a==0 or gcd(a,q)!=1: continue
        vals=ss[st[bi]:en[bi]]
        L=len(vals)
        if L<2: 
            consider(1,1,q,a) if L==1 else None
            continue
        # two pointer for each N
        for N in range(2,NMAX+1):
            span=q*(N-1)
            j=0;bestc=1
            for i in range(L):
                if j<i: j=i
                while j+1<L and vals[j+1]-vals[i]<=span: j+=1
                if j-i+1>bestc: bestc=j-i+1
            consider(N,bestc,q,a)
    if q%4000==0: print("q",q,round(time.time()-t0,1),file=sys.stderr)

def Q(N,q,a): return sum(1 for n in range(N) if isqrt(q*n+a)**2==q*n+a)
print("N  Qmax  Q(N;24,1)  argmax(q,a) list")
bad=[]
for N in range(6,NMAX+1):
    b,lst=best[N]
    q241=Q(N,24,1)
    qs=sorted({q for q,_ in lst})
    flag=""
    if q241!=b: flag=" <-- STRONG FAILS"; bad.append(('strong',N,b,q241))
    if qs!=[24]: flag+=" <-- UNIQUE q!=[24]"; bad.append(('unique',N,qs))
    print(N,b,q241,lst[:8],flag)
print("failures:",bad[:20])
print("elapsed",round(time.time()-t0,1))
