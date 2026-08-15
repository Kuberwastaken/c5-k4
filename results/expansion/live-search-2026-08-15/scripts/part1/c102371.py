def a102371(N):
    s=[0,1]
    for n in range(2,N+1): s.append(s[-1]^(s[-1]+n))
    return s
def a105033(n):
    t=0
    for k in range(0,n):
        if 2**(k+1)<=n and n%2**(k+1)==k: t+=2**(k+1)
    return max(n-t,0)
N=400
A=a102371(N)
bad=[]
for n in range(1,N+1):
    rhs=(2**n-1)-a105033(n-1)
    rhs=max(rhs,0)   # Nat truncation
    if A[n]!=rhs: bad.append((n,A[n],rhs))
print("A102371 a(1..12):",A[1:13])
print("OEIS DATA head : [1,2,7,12,29,62,123,248,505,1018,2047,4084]")
print("match:",A[1:13]==[1,2,7,12,29,62,123,248,505,1018,2047,4084])
print("A105033 a(0..12):",[a105033(n) for n in range(13)])
print("identity violations n=1..%d:"%N,bad[:10],"count",len(bad))
