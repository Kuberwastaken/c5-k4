import sys; sys.setrecursionlimit(200000)
from functools import lru_cache
@lru_cache(maxsize=None)
def st(n):
    if n<=1: return 1
    k=n//2
    if n%2==1: return st(k)
    return st(k) + (0 if k<2 else st(k-2))
print("a[0..24]", [st(n) for n in range(25)])
print("conj1 a(2^n)=a(2^(n+1)+1) failures n<=200:", [n for n in range(201) if st(2**n)!=st(2**(n+1)+1)])
print("conj2 a(2^n-1)=a(3*2^n-1) failures n<=200:", [n for n in range(201) if st(2**n-1)!=st(3*2**n-1)])
print("conj3 a(2^n-1)=1 failures n<=200:", [n for n in range(201) if st(2**n-1)!=1])
print("a(2^n) n=0..12:", [st(2**n) for n in range(13)], " (A033638: 1,1,2,3,5,7,10,13,17,21,26,31,37)")
