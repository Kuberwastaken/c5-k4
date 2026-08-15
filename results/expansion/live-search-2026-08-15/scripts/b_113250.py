from nt import isqrt
def run(m, init, N=80):
    A,B,C = -4, 4*m*m, m**4
    s=list(init)
    for n in range(4,N): s.append(A*s[n-1]+B*s[n-3]+C*s[n-4])
    return s
for m,init,name in ((4,[-1,4,32,64],'A113250'),(6,[-1,4,92,784],'A113252'),(9,[-1,4,227,5329],'A113255')):
    s=run(m,init)
    print(name,"recurrence -4,%d,%d  first 8:"%(4*m*m,m**4), s[:8])
    bad=[(n,s[n]) for n in range(1,len(s),2) if s[n]<0 or isqrt(s[n])**2!=s[n]]
    print("   odd-index non-squares (n<%d): %s  count=%d"%(len(s),bad[:4],len(bad)))
    print("   sqrt(a(2k+1)) k=0..6:", [isqrt(s[n]) for n in range(1,14,2)])
    ev=[(n,s[n]) for n in range(0,12,2)]
    print("   even-index terms:", ev)
