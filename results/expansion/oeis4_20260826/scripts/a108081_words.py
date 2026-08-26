#!/usr/bin/env python3
"""A108081 audit.
Lean def: a(n)=Sum_{k=0..n} C(n+k-1,k)*F(n-k+1)  (Barry's formula)
OEIS main formula: a(n)=Sum_{i=0..n} C(2n-i,n+i).
Conjecture (Li-yao Xia word set X): |{words of length n in smallest set X}|
 = a(n-1) for n>=1 (Lean: count_words_in_x_is_a_shifted).
Checks:
 (0) two formulas agree exactly n=0..40; heads vs b-file.
 (1) BRUTE-FORCE word enumeration by levels (dedup sets), lengths 1..8:
     |X_L| == a(L-1)?
Words over Z; l(u)=reverse(u)-1 per term; r(v)=reverse(v)+1; base [0];
closure under l(u)++v and u++r(v) for ANY u,v already in X.
"""
from math import comb
import sympy as sp

def fibs(N):
    F=[0,1]
    while len(F)<=N: F.append(F[-1]+F[-2])
    return F
F = fibs(80)

def a_barry(n):
    return sum(comb(n+k-1 if n+k-1>=0 else 0, k)*F[n-k+1] for k in range(n+1))
def a_main(n):
    return sum(comb(2*n-i, n+i) for i in range(n+1))

print("=== formulas agree n=0..40 ===")
bad=[n for n in range(41) if a_barry(n)!=a_main(n)]
print("  mismatches:", bad if bad else "NONE")

print("=== head vs b-file ===")
mine=[a_main(n) for n in range(13)]
print("  ", mine)
bf=[]
for line in open('bfiles/b108081.txt'):
    line=line.strip()
    if line and not line.startswith('#'):
        k,v=line.split(); bf.append((int(k),int(v)))
print("  b-file:", [v for _,v in bf[:13]])
print("  match:", mine==[v for _,v in bf[:13]])

print("=== WORD ENUMERATION by levels (cap 55 s) ===")
import time
t0=time.time()
words = {1: {(0,)}}          # length -> set of tuples ; base word [0]
L = 1
results={1:1}
while L <= 8:
    if time.time()-t0>50:
        print(f"  TIME CAP at level {L}")
        break
    nxt=set()
    src = sorted(words.get(L, []))
    # build length L+1 from pairs i+j=L+1 using existing levels
    target=L+1
    for i in range(1, target):
        j=target-i
        Wi=words.get(i); Wj=words.get(j)
        if not Wi or not Wj: continue
        for u in Wi:
            lu=tuple(x-1 for x in reversed(u))
            for v in Wj:
                nxt.add(lu+v)
        for u in Wi:
            ru=tuple(x+1 for x in reversed(u))
            # r(v) applied to v then prefix u? step_right: u ++ r(v)
            pass
        for v in Wj:
            rv=tuple(x+1 for x in reversed(v))
            for u in Wi:
                nxt.add(u+rv)
    words[target]=nxt
    results[target]=len(nxt)
    print(f"  |X_{target}| = {len(nxt)}   a({target-1}) = {a_main(target-1)}   match={len(nxt)==a_main(target-1)}")
    L+=1
print("  NOTE: enumeration counts DISTINCT derived words (XWord is a minimal")
print("  closed set; every derivation of valid parts is valid)")
