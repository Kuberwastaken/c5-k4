# A108306 conjecture: invertSeqD a b n = (genMatrix a b ^ n) 0 0
from functools import lru_cache
def C(a,b,k):
    if k==0: return 0
    if k==1: return 1
    return a*b**(k-2)
def D(a,b,n,memo):
    if n in memo: return memo[n]
    if n==0: v=1
    else: v=sum(C(a,b,n-i)*D(a,b,i,memo) for i in range(n))
    memo[n]=v; return v
def mat00(a,b,n):
    M=[[1,a],[1,b]]; R=[[1,0],[0,1]]
    for _ in range(n):
        R=[[R[0][0]*M[0][0]+R[0][1]*M[1][0], R[0][0]*M[0][1]+R[0][1]*M[1][1]],
           [R[1][0]*M[0][0]+R[1][1]*M[1][0], R[1][0]*M[0][1]+R[1][1]*M[1][1]]]
    return R[0][0]
bad=[]
for a in range(0,8):
    for b in range(0,8):
        memo={}
        for n in range(0,16):
            if D(a,b,n,memo)!=mat00(a,b,n): bad.append((a,b,n,D(a,b,n,memo),mat00(a,b,n)))
print("mismatches over a,b in 0..7, n in 0..15:",bad[:12],"count",len(bad))
memo={}
print("a=1,b=5 (file's m matrix) D(0..10):",[D(1,5,n,memo) for n in range(11)])
print("                          M00(0..10):",[mat00(1,5,n) for n in range(11)])
# also the sequence a of the file
seq=[1,6]
for _ in range(12): seq.append(3*seq[-1]+3*seq[-2])
print("A108306 a(0..13):",seq)
