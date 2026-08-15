import time, itertools, sys
from collections import defaultdict
t0=time.time()
LIMR=int(sys.argv[1])
cubes=[i**3 for i in range(1,LIMR+1)]
bysum=defaultdict(list)
for i in range(len(cubes)):
    ci=cubes[i]
    for j in range(i+1,len(cubes)):
        s2=ci+cubes[j]
        for k in range(j+1,len(cubes)):
            bysum[s2+cubes[k]].append((ci,cubes[j],cubes[k]))
cands=[(t,v) for t,v in bysum.items() if len(v)>=3]
print("sums with >=3 triples:",len(cands),"time",round(time.time()-t0,1), file=sys.stderr)
found=[]
for t,tris in cands:
    n=len(tris)
    for i in range(n):
        A=tris[i]; sA=frozenset(A)
        for j in range(i+1,n):
            B=tris[j]
            if sA & frozenset(B): continue
            sAB=sA|frozenset(B)
            for k in range(j+1,n):
                C=tris[k]
                if sAB & frozenset(C): continue
                for pb in itertools.permutations(B):
                    for pc in itertools.permutations(C):
                        if A[0]+pb[0]+pc[0]==t and A[1]+pb[1]+pc[1]==t and A[2]+pb[2]+pc[2]==t:
                            found.append((t,A,pb,pc))
    if len(found)>=3: break
print("B: results roots<=%d:"%LIMR, len(found))
for f in found[:3]:
    t,A,B,C=f
    M=[list(A),list(B),list(C)]
    print("  t=",t)
    for row in M: print("    ",row,"roots",[round(v**(1/3)) for v in row],"sum",sum(row))
    print("     cols",[sum(M[r][c] for r in range(3)) for c in range(3)],"distinct",len({v for r in M for v in r}))
print("B elapsed",round(time.time()-t0,1))
