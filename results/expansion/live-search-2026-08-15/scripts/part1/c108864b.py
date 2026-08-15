# Independent path: no sieve, direct divisor enumeration.
def sigma(n):
    s=0; d=1
    while d*d<=n:
        if n%d==0:
            s+=d
            if d!=n//d: s+=n//d
        d+=1
    return s
def leanA(n): return n>0 and abs(sigma(n)-2*n)<=10
lst=[n for n in range(1,9000) if leanA(n)]
print("independent Lean-A list up to 9000 (count %d):"%len(lst))
print(lst)
print("index of 8925:",lst.index(8925))
print("a(67) =",lst[67], " odd?",lst[67]%2==1)
print("sigma(8925)=",sigma(8925)," 2n=",2*8925," dev=",abs(sigma(8925)-2*8925))
print("terms at Lean indices 59..70:",[(i,lst[i]) for i in range(59,71)])
# A109883 perfect deficiency (source definition), independent
def pdef(n):
    divs=[d for d in range(1,n) if n%d==0]
    r=n
    for d in divs:
        r-=d
        if r<d: return r
    return r
print("A109883 check (n=1..30):",[pdef(n) for n in range(1,31)])
print("  OEIS A109883 head:  [0,1,2,1,4,0,6,1,5,2,10,2,12,4,6,1,16,6,18,8,10,8,22,0,19,10,14,0,28,3]")
print("A109883(8925) =",pdef(8925))
print("A109883(315)=",pdef(315)," A109883(1155)=",pdef(1155))
true_terms=[n for n in range(1,20000) if pdef(n)<=10]
print("TRUE A108864 terms <20000 (count %d): %s"%(len(true_terms),true_terms[:70]))
print("  odd true terms:",[t for t in true_terms if t%2==1])
print("  0-indexed position of 1155 in TRUE seq:",true_terms.index(1155))
