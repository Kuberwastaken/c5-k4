import numpy as np, os
LIM=10_000_001
def build():
    sig=np.zeros(LIM,dtype=np.int64); phi=np.arange(LIM,dtype=np.int64)
    usig=np.ones(LIM,dtype=np.int64)
    # sigma via divisor sum
    for d in range(1,LIM):
        sig[d::d]+=d
    # phi
    for p in range(2,LIM):
        if phi[p]==p:  # prime
            phi[p::p]-=phi[p::p]//p
    # unitary sigma: multiplicative, usigma(p^e)=1+p^e
    # compute largest power of p dividing n via repeated
    return sig,phi
sig,phi=build()
np.save('sig10m.npy',sig); np.save('phi10m.npy',phi)
print("sieves built", sig[6], phi[10])
