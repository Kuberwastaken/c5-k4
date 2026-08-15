import time
t0=time.time(); found=[]; k=2
while time.time()-t0<45:
    m=k**4-1
    if m>0 and pow(2,k,m)==1:
        found.append(k)
    k+=1
print("k in 2..%d with (k^4-1) | (2^k-1):"%(k-1), found)
print("expected {2^(2^n): n>=2} = 16,256,65536,...")
print("extraneous k (not of form 2^(2^n), n>=2):", [x for x in found if x not in (16,256,65536,4294967296)])
