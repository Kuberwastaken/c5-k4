import numpy as np
LIM=10_000_001
sig=np.load('sig10m.npy')
n=np.arange(LIM,dtype=np.int64)
dev=np.abs(sig-2*n)
terms=np.flatnonzero((n>0)&(dev<=10))
print("Lean-A terms count to 10^7:",len(terms))
print("Lean-A first 70:",terms[:70].tolist())
oeis=[1,2,3,4,5,6,7,8,9,10,11,12,14,15,16,18,20,21,22,24,26,28,30,32,40,42,44,50,52,60,64,68,72,110,120,126,128,130,136,144,150,152,180,184,204,228,256,315,462,496,512,528,592,656,750,884,1012,1024,1155,1188,1248]
print("OEIS A108864 first 61:",oeis)
L=terms.tolist()
print("Lean seq == OEIS DATA head?", L[:61]==oeis)
# symmetric differences within 1..1300
sl=set(x for x in L if x<=1300); so=set(oeis)
print("in OEIS(<=1248) but NOT in Lean seq:",sorted(so-sl))
print("in Lean seq(<=1248) but NOT in OEIS:",sorted(x for x in sl if x<=1248 and x not in so))
odd=[(i,t) for i,t in enumerate(L) if t%2==1]
print("odd terms with Lean 0-indexed position:",odd)
print("Lean index of 1155:", L.index(1155) if 1155 in L else None)
print("VIOLATIONS of (forall n>58, Even (a n)):",[(i,t) for i,t in odd if i>58])
