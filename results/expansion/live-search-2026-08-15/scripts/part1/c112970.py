import sys
sys.setrecursionlimit(200000)
memo={}
def a(n):
    if n in memo: return memo[n]
    if n==0 or n==1: v=1
    else:
        k=n//2
        if n%2==1: v=a(k)
        else: v=a(k)+(0 if k<2 else a(k-2))
    memo[n]=v; return v
# warm up iteratively
for n in range(0,300000): a(n)
print("a(0..30):",[a(n) for n in range(31)])
b1=[n for n in range(0,17) if a(2**n)!=a(2**(n+1)+1)]
b2=[n for n in range(0,17) if a(max(2**n-1,0))!=a(3*2**n-1)]
b3=[n for n in range(0,17) if a(max(2**n-1,0))!=1]
print("conjecture1 (a(2^n)=a(2^(n+1)+1)) fails at n=",b1)
print("conjecture2 (a(2^n-1)=a(3*2^n-1)) fails at n=",b2)
print("conjecture3 (a(2^n-1)=1)          fails at n=",b3)
print("samples c1:",[(n,a(2**n),a(2**(n+1)+1)) for n in range(0,10)])
print("samples c2:",[(n,a(2**n-1),a(3*2**n-1)) for n in range(0,10)])
