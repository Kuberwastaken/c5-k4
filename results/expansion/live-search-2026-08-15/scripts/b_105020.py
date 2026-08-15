from nt import isqrt
def tri(c): return c*(c+1)//2
def adiag(n): return (isqrt(8*n+1)-1)//2
def a(n):
    c=adiag(n); k=n-tri(c); i=c-k; m=c+1
    return m*m-i*i
def semiprime(x):
    if x<2: return False
    cnt=0; m=x; d=2
    while d*d<=m:
        while m%d==0: m//=d; cnt+=1
        if cnt>2: return False
        d+=1 if d==2 else 2
    if m>1: cnt+=1
    return cnt==2
N=300000
A=[a(i) for i in range(N)]
print("a(0..14):",A[:15])
bad=[]
for i in range(N):
    v=A[i]
    if v%2==0 or v<3: continue
    n=(v-1)//2
    if n<1: continue
    j=i+n+1
    if j>=N: continue
    if A[j]!=2*n+3: continue
    if not any(semiprime(A[k]) for k in range(i+1,j)):
        bad.append((n,i,j,[A[k] for k in range(i+1,j)]))
print("triples (n,i,j) satisfying hypotheses with NO semiprime strictly between:")
for b in bad[:10]: print("   ",b)
print("count",len(bad),"  scanned i<%d"%N)
