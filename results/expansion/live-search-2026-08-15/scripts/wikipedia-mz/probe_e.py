# UnionClosed.variants.cardinality_even_of_union_closed_tight
# hypothesis: A union-closed, A != {emptyset}, A != empty, and EVERY element i of the
# ground type lies in exactly |A|/2 members.  conclusion: |A| = 2^k.
import itertools, time
t0=time.time()
def run(n):
    full=1<<n
    P=list(range(full))           # subsets as bitmasks
    hits=[]; sat=0
    # iterate over all subsets of P([n])
    for mask in range(1, 1<<full):
        A=[s for s in P if mask>>s & 1]
        k=len(A)
        if k%2: continue
        # union closed?
        As=set(A); ok=True
        for x in A:
            for y in A:
                if (x|y) not in As: ok=False; break
            if not ok: break
        if not ok: continue
        if A==[0]: continue        # A = {emptyset}
        # every element of [n] in exactly k/2 sets
        good=True
        for i in range(n):
            c=sum(1 for s in A if s>>i & 1)
            if 2*c != k: good=False; break
        if not good: continue
        sat+=1
        if k & (k-1): hits.append(sorted(A))
    return sat, hits
for n in (1,2,3,4):
    sat,hits=run(n)
    print(f"n={n}: families satisfying the Lean hypothesis: {sat}; with |A| NOT a power of 2: {len(hits)} {hits[:3]}")
print("elapsed",round(time.time()-t0,1))
