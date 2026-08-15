N=300000
divs=[[] for _ in range(N+1)]
for d in range(1,N//2+1):
    for m in range(2*d,N+1,d):
        divs[m].append(d)
def pdef(n):
    if n==1: return 0
    D=divs[n]; r=n
    for i,d in enumerate(D):
        r-=d
        if i+1<len(D) and r<D[i+1]: return r
    return r
head=[pdef(n) for n in range(1,31)]
ref=[0,1,2,1,4,0,6,1,5,2,10,2,12,4,6,1,16,6,18,8,10,8,22,0,19,10,14,0,28,3]
print("A109883(1..30):",head); print("match OEIS:",head==ref)
head2=[pdef(n) for n in range(1,80)]
ref2=[0,1,2,1,4,0,6,1,5,2,10,2,12,4,6,1,16,6,18,8,10,8,22,0,19,10,14,0,28,3,30,1,18,14,22,11,36,16,22,10,40,9,42,4,12,20,46,12,41,7,30,6,52,15,38,20,34,26,58,2,60,28,22,1,46,21,66,10,42,31,70,9,72,34,26,12,58,27,78]
print("match first 79:",head2==ref2)
tt=[n for n in range(1,N+1) if pdef(n)<=10]
oeis=[1,2,3,4,5,6,7,8,9,10,11,12,14,15,16,18,20,21,22,24,26,28,30,32,40,42,44,50,52,60,64,68,72,110,120,126,128,130,136,144,150,152,180,184,204,228,256,315,462,496,512,528,592,656,750,884,1012,1024,1155,1188,1248]
print("TRUE A108864 first 61:",tt[:61])
print("matches OEIS DATA head:",tt[:61]==oeis)
odd=[(i,t) for i,t in enumerate(tt) if t%2==1]
print("odd TRUE terms (0-idx pos,val):",odd)
print("pos of 1155 in TRUE seq:",tt.index(1155) if 1155 in tt else None)
print("count to %d: %d"%(N,len(tt)))
print("is 8925 in TRUE seq? pdef(8925)=",pdef(8925))
