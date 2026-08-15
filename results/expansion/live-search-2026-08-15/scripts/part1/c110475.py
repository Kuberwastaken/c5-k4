import numpy as np
NB=300000
om=np.zeros(NB+1,dtype=np.int16); npf=np.zeros(NB+1,dtype=np.int16)
isp=np.ones(NB+1,dtype=bool); isp[:2]=False
for p in range(2,NB+1):
    if isp[p]:
        if p*p<=NB: isp[p*p::p]=False
        npf[p::p]+=1
        q=p
        while q<=NB:
            om[q::q]+=1
            if q>NB//p: break
            q*=p
# Lean a(x) = (k-1 in Nat) + #{p : e_p>1};  a(x)=1 iff  (k=1 and some e>1) or (k=2 and all e=1)
k=npf; c=np.zeros(NB+1,dtype=np.int16)
# c = #primes with exponent>1 = k - #primes with exponent exactly 1 ; compute via squarefree-part
sqfree_pf=np.zeros(NB+1,dtype=np.int16)
for p in range(2,NB+1):
    if isp[p] or True:
        pass
# simpler: recompute c by marking p^2 | x
c=np.zeros(NB+1,dtype=np.int16)
for p in range(2,int(NB**0.5)+1):
    if om[p]==1:  # p prime
        c[p*p::p*p]+=1
aL=np.maximum(k.astype(np.int32)-1,0)+c.astype(np.int32)
S=np.flatnonzero(aL==1)
print("x with a x = 1 (first 30):",S[:30].tolist())
print("a(1..40) (Lean):",aL[1:41].tolist())
print("OEIS A110475(1..40): [0,0,0,1,0,1,0,1,1,1,0,2,0,1,1,1,0,2,0,2,1,1,0,2,1,1,1,2,0,2,0,1,1,1,1,3,0,1,1,2]")
print("match:",aL[1:41].tolist()==[0,0,0,1,0,1,0,1,1,1,0,2,0,1,1,1,0,2,0,2,1,1,0,2,1,1,1,2,0,2,0,1,1,1,1,3,0,1,1,2])
rep=np.zeros(NB+1,dtype=bool)
lst=S.tolist()
import bisect
for x in lst:
    if 2*x>NB: break
    hi=bisect.bisect_right(lst,NB-x)
    idx=np.array(lst[:hi],dtype=np.int64)+x
    rep[idx]=True
exc={1,2,3,4,5,6,7,9,11}
viol=[m for m in range(1,NB+1) if ((m not in exc) != bool(rep[m]))]
print("iff violations up to %d:"%NB,viol[:20],"count",len(viol))
