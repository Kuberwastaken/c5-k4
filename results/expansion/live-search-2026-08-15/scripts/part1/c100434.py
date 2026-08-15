# A100434: replay Lean defs exactly (exact integer arithmetic)
N=40
def mkrec(i0,i1,i2,i3):
    s=[i0,i1,i2,i3]
    for n in range(N): s.append(-6*s[n+2]-s[n])
    return s
c=mkrec(1,-3,-7,17)
d=mkrec(2,4,-10,-24)
a=mkrec(3,4,-17,-24)
# Lean b : if n%2=0 then c(n+1) else c(n-1)
b=[c[n+1] if n%2==0 else c[n-1] for n in range(N)]
# Lean e : if n%2=0 then d n / 2 else -(d (n-1) / 2)   (Int division; all d even)
def idiv(x,y):
    q=abs(x)//abs(y)
    return q if (x<0)==(y<0) else -q
e=[idiv(d[n],2) if n%2==0 else -idiv(d[n-1],2) for n in range(N)]
# Lean f : let m := n/2 ; d (2*m+1) / 2
f=[idiv(d[2*(n//2)+1],2) for n in range(N)]
# Lean g : if n%2=0 then 0 else c n
g=[0 if n%2==0 else c[n] for n in range(N)]
print("c   ",c[:12]); print("d   ",d[:12]); print("a   ",a[:12])
print("b   ",b[:12]); print("e   ",e[:12]); print("f   ",f[:12]); print("g   ",g[:12])
for name,lhs in (("c+d",[c[n]+d[n] for n in range(N)]),("e+f",[e[n]+f[n] for n in range(N)]),("g+a",[g[n]+a[n] for n in range(N)])):
    bad=[n for n in range(N) if lhs[n]!=b[n]]
    print(name, "first 12:",lhs[:12], "| mismatches vs b at n =", bad[:10], "count", len(bad))
print("three-way equal (c+d==e+f==g+a):", all(c[n]+d[n]==e[n]+f[n]==g[n]+a[n] for n in range(N)))
print("c+d == -b at even n, == b at odd n:", all((c[n]+d[n])==(-b[n] if n%2==0 else b[n]) for n in range(N)))
