#!/usr/bin/env python3
"""A063880 repair development:
   (1) verify exists_primitive_of_a shape: n = m*s, m=min divisor-in-A,
       s squarefree & coprime;
   (2) verify the stronger kernel reading: powerful-kernel of n is itself a term;
   (3) prove-closure direction sanity: A(m) => A(m*q) for new prime q.
"""
from sympy import factorint
def gcd(a,b):
    while b: a,b=b,a%b
    return a


def sigma(n):
    f = factorint(n)
    r = 1
    for p, e in f.items():
        r *= (p ** (e + 1) - 1) // (p - 1)
    return r

def usigma(n):
    f = factorint(n)
    r = 1
    for p, e in f.items():
        r *= (1 + p ** e)
    return r

def in_A(n):
    return n > 0 and sigma(n) == 2 * usigma(n)

def powerful_kernel(n):
    """m = prod p^e_p for e_p>=2 ; s = prod p for e_p==1."""
    f = factorint(n)
    m = 1
    s = 1
    for p, e in f.items():
        if e >= 2:
            m *= p ** e
        else:
            s *= p
    return m, s

def divisors_of(n):
    ds = [1]
    f = factorint(n)
    for p, e in f.items():
        pe = 1
        newds = []
        pk = 1
        for _ in range(e + 1):
            for d in ds:
                newds.append(d * pk)
            pk *= p
        ds = newds
    return sorted(set(ds))

t0 = __import__("time").time()
N = 100000
checked = 0
bad_shape = []
bad_kernel = []
bad_prim = []
terms = []
for n in range(108, N + 1):
    if not in_A(n):
        continue
    checked += 1
    terms.append(n)
    # (1) minimal-divisor decomposition shape
    mind = next(d for d in divisors_of(n) if d > 1 and in_A(d))
    # walk to smallest nontrivial divisor in A
    changed = True
    while changed:
        changed = False
        for d in divisors_of(mind):
            if d < mind and d > 1 and in_A(d):
                mind = d
                changed = True
                break
    s = n // mind
    fs = factorint(s)
    sqfree = all(e == 1 for e in fs.values())
    coprime = all(p not in factorint(mind) for p in fs)
    if not (sqfree and coprime):
        bad_shape.append((n, mind, s))
    # (2) powerful kernel is itself a term
    m, s2 = powerful_kernel(n)
    if not (in_A(m) and m * s2 == n):
        bad_kernel.append((n, m))
print(f"A-terms <= {N}: {checked} ({__import__('time').time()-t0:.1f}s)")
print("decomposition-shape failures:", bad_shape[:5] if bad_shape else "NONE")
print("powerful-kernel-not-term failures:", bad_kernel[:5] if bad_kernel else "NONE")

# (3) closure spot-checks
import random
okc = True
for _ in range(30):
    t = random.choice(terms)
    q = random.choice([7, 11, 13, 17, 19, 23])
    if q % 216 == 0:
        continue
    if gcd(t, q) == 1:
        if in_A(t) != in_A(t * q):
            okc = False
            print("closure FAIL:", t, q)
print("closure A(m)=>A(m*q) for coprime prime q holds in spot checks:", okc)


prims = [n for n in terms if all(not (d>1 and d<n and in_A(d)) for d in divisors_of(n))]
print("primitive terms found:", prims)
