import math, numpy as np
N=2_000_000
idx=np.arange(N,dtype=np.int64)
c=((np.sqrt(8.0*idx+1).astype(np.int64))-1)//2
# fix isqrt rounding
c=np.where((c+1)*(c+2)//2<=idx, c+1, c)
c=np.where(c*(c+1)//2>idx, c-1, c)
k=idx-c*(c+1)//2
i_=c-k
m=c+1
vals=m*m-i_*i_
print("a(0..15):",vals[:16].tolist())
assert vals[:28].tolist()==[1,3,4,5,8,9,7,12,15,16,9,16,21,24,25,11,20,27,32,35,36,13,24,33,40,45,48,49]
VM=int(vals.max())+2
print("index range",N,"max value",VM)
om=np.zeros(VM,dtype=np.int8)
p=2
while p<VM:
    if om[p]==0:
        pk=p
        while pk<VM:
            om[pk::pk]+=1
            if pk> VM//p: break
            pk*=p
    p+=1
semi=(om==2)
semi[:2]=False
# enumerate ALL i with a(i) odd >=3
odd_i=np.flatnonzero((vals%2==1)&(vals>=3))
print("candidate i count:",len(odd_i))
fails=[];checked=0
for i in odd_i.tolist():
    n=(int(vals[i])-1)//2
    if n<1: continue
    j=i+n+1
    if j>=N: continue
    if int(vals[j])!=2*n+3: continue
    checked+=1
    seg=vals[i+1:j]
    if len(seg)==0 or not semi[seg].any():
        fails.append((n,i,j,seg.tolist()))
print("premise-satisfying triples:",checked,"FAILURES:",len(fails))
for f in fails[:15]:
    print("   n=%d i=%d j=%d a(i)=%d a(j)=%d interior=%s"%(f[0],f[1],f[2],2*f[0]+1,2*f[0]+3,f[3][:20]))
