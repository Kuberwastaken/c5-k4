#!/usr/bin/env python3
"""A102847 audit: a(n)=a(n-1)^2+2. Verify published factorization claims incl. a(7);
   hunt next prime after a(4)=15131 (bracket)."""
import time
from sympy import factorint, isprime

seq = [1]
for _ in range(10):
    seq.append(seq[-1] ** 2 + 2)

print("head:", seq[:6], "expect [1, 3, 11, 123, 15131, 228947163]")
assert seq[5] == 228947163

print("\n== published claims ==")
f5 = factorint(seq[5])
print("a(5) =", seq[5], "=", f5, "-> semiprime 3*76315721?", f5 == {3:1, 76315721:1},
      "; 76315721 prime?", isprime(76315721))

t0 = time.time()
f6 = factorint(seq[6])
print(f"a(6) = {seq[6]} factors({len(f6)}): {f6} ({time.time()-t0:.1f}s)")
print("a(6) has 4 prime factors counted with multiplicity:",
      sum(e for e in f6.values()) == 4)

t0 = time.time()
f7 = factorint(seq[7])
claimed = {41:1, 811:2, 106693969:1, 317171188688357726699:1,
           8272236925540996054440172449761:1}
print(f"a(7) digits={len(str(seq[7]))} factored in {time.time()-t0:.1f}s")
print("matches claimed factorization exactly:", f7 == claimed)

print("\n== next-prime hunt after a(4) ==")
for n in range(5, len(seq)):
    v = seq[n]
    pr = isprime(v)
    print(f"n={n}: digits={len(str(v))} prime={pr}")
