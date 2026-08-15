# A104320: number of 0 digits in base-3 rep of 2^n; conj a(n)>0 for n>15
N=12000
d=[1]  # base-3 digits of 2^0, little endian
zeroless=[]
cnt=[]
for n in range(0,N+1):
    if n>0:
        carry=0; out=[]
        for x in d:
            v=2*x+carry; out.append(v%3); carry=v//3
        while carry: out.append(carry%3); carry//=3
        d=out
    z=d.count(0)
    cnt.append(z)
    if z==0: zeroless.append(n)
print("a(0..30):",cnt[:31])
print("OEIS head:[0,0,0,0,0,1,1,1,2,2,1,1,1,4,1,0,4,2,3,3,3,3,3,7,7,9,5,6,6,4,4]")
print("match:",cnt[:31]==[0,0,0,0,0,1,1,1,2,2,1,1,1,4,1,0,4,2,3,3,3,3,3,7,7,9,5,6,6,4,4])
print("n with a(n)=0 (zeroless base-3 2^n), n<=%d:"%N,zeroless)
print("violations of (n>15 -> a n > 0):",[n for n in zeroless if n>15])
