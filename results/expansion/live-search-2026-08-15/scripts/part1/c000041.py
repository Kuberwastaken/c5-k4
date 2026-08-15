import sys,time
sys.set_int_max_str_digits(2000000)
NP=30000
p=[0]*(NP+1); p[0]=1
for n in range(1,NP+1):
    s=0;k=1
    while True:
        g1=k*(3*k-1)//2; g2=k*(3*k+1)//2
        if g1>n and g2>n: break
        sgn=-1 if k%2==0 else 1
        if g1<=n: s+=sgn*p[n-g1]
        if g2<=n: s+=sgn*p[n-g2]
        k+=1
    p[n]=s
print("p(0..10):",p[:11],"  p(50)=",p[50],"  (OEIS p(50)=204226)")
def iroot(v,m):
    lo,hi=1,1<<((v.bit_length()//m)+2)
    while lo<hi:
        mid=(lo+hi)//2
        if mid**m<v: lo=mid+1
        else: hi=mid
    return lo
def isperfpow(v):
    if v<4: return False
    for m in range(2,v.bit_length()+1):
        r=iroot(v,m)
        if r>1 and r**m==v: return True
    return False
t0=time.time()
hits=[n for n in range(0,NP+1) if isperfpow(p[n])]
print("A000041: perfect-power partition numbers for n=0..%d : %s   (%.1fs)"%(NP,hits,time.time()-t0))
