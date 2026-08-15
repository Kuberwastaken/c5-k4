import time, itertools, sys, numpy as np
t0=time.time()
LIMR=int(sys.argv[1])
cubes=np.array([i**3 for i in range(1,LIMR+1)],dtype=np.int64)
CBIG=set()
r=1
while r**3 <= 3*LIMR**3: CBIG.add(r**3); r+=1
n=LIMR
I,J,K=np.triu_indices(n,1)  # placeholder
# build all i<j<k triples
tri=[]
for i in range(n):
    for j in range(i+1,n):
        s=cubes[i]+cubes[j]
        kk=np.arange(j+1,n)
        if len(kk)==0: continue
        sums=s+cubes[j+1:]
        tri.append(np.stack([sums, np.full(len(kk),i), np.full(len(kk),j), kk]))
T=np.concatenate(tri,axis=1).T  # rows: sum,i,j,k
print("triples",T.shape,round(time.time()-t0,1),file=sys.stderr)
order=np.argsort(T[:,0],kind='stable'); T=T[order]
sums=T[:,0]
bounds=np.flatnonzero(np.diff(sums))+1
starts=np.concatenate([[0],bounds]); ends=np.concatenate([bounds,[len(sums)]])
mult=ends-starts
sel=np.flatnonzero(mult>=2)
print("groups with >=2 triples:",len(sel),"max mult",mult.max(),"pairs",int(((mult[sel]*(mult[sel]-1))//2).sum()),round(time.time()-t0,1),file=sys.stderr)
found=[]
cub=cubes
for gi in sel:
    a,b=starts[gi],ends[gi]
    t=int(sums[a])
    grp=T[a:b,1:]
    m=b-a
    for x in range(m):
        A=[int(cub[grp[x,0]]),int(cub[grp[x,1]]),int(cub[grp[x,2]])]
        sA=set(A)
        for y in range(x+1,m):
            B0=[int(cub[grp[y,0]]),int(cub[grp[y,1]]),int(cub[grp[y,2]])]
            if sA & set(B0): continue
            for B in itertools.permutations(B0):
                C=[t-A[0]-B[0], t-A[1]-B[1], t-A[2]-B[2]]
                if C[0]<=0 or C[1]<=0 or C[2]<=0: continue
                if C[0] in CBIG and C[1] in CBIG and C[2] in CBIG:
                    if len(set(A)|set(B)|set(C))==9:
                        found.append((t,A,list(B),C))
    if len(found)>=3: break
print("B3: found",len(found))
for f in found[:3]:
    t,A,B,C=f
    M=[A,B,C]
    print(" t=",t)
    for row in M: print("   ",row,"roots",[round(v**(1/3)) for v in row],"sum",sum(row))
    print("    cols",[sum(M[r][c] for r in range(3)) for c in range(3)])
print("B3 elapsed",round(time.time()-t0,1))
