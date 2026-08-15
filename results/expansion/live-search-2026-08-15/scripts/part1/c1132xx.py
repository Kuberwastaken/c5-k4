import math
def run(name,init,coef,oeis_head,N=400):
    s=list(init)
    c3,c1,c0=coef  # a(n+4) = -4 a(n+3) + c1*a(n+1) + c0*a(n)
    for n in range(N): s.append(-4*s[n+3]+c1*s[n+1]+c0*s[n])
    print("==",name,"a(0..12):",s[:13])
    print("   OEIS head match:", s[:len(oeis_head)]==oeis_head)
    bad=[]
    for n in range(0,(len(s)-1)//2):
        v=s[2*n+1]
        if v<0: bad.append((n,2*n+1,v,'NEGATIVE')); continue
        r=math.isqrt(v)
        if r*r!=v: bad.append((n,2*n+1,v,'not square'))
    print("   IsSquare(a(2n+1)) failures for n=0..%d:"%((len(s)-2)//2), bad[:6], "count",len(bad))
    ex=[]
    for n in range(0,10):
        v=s[2*n+1]; r=math.isqrt(v) if v>=0 else None
        ex.append((2*n+1,v,r))
    print("   odd-index (idx,val,sqrt):",ex)
run("A113250",[-1,4,32,64],(None,64,256),[-1,4,32,64,-256,4096,-4096,16384,131072,262144,-1048576,16777216,-16777216,67108864,536870912,1073741824])
run("A113252",[-1,4,92,784],(None,144,1296),[-1,4,92,784,-3856,33856,96704,73984,-418048,59474944,-101917696,443355136])
run("A113255",[-1,4,227,5329],(None,324,6561),[-1,4,227,5329,-26581,206116,2391479,16785409,-174757993,2826198244,9824173259,14210785681])
