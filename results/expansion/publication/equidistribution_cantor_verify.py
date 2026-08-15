#!/usr/bin/env python3
"""
Independent re-verification of the nested-interval (Cantor) construction refuting

  isEquidistributedModuloOne_transcendental_three_halves_pow :
      forall x transcendental, IsEquidistributedModuloOne (fun n => x * (3/2)^n)

Exact rational arithmetic throughout; no floating point in any decision.

lam = 3/2, c = 1/10, G = 8.

We build nested closed intervals I_0 >= I_1 >= ... with |I_j| = c * lam^(-jG)
such that  xi in I_j  =>  fract(xi * lam^(iG)) in [0, c]  for all i <= j.
At each step the image of I_j under xi |-> xi*lam^((j+1)G) is an interval of
length c*lam^G; if that length is >= 2 + c the image contains at least two
disjoint unit-blocks [k, k+c] (k integer), giving two branch choices.
"""
from fractions import Fraction as F
import math

lam = F(3, 2)
c = F(1, 10)
G = 8

L = c * lam**G
print(f"lambda = {lam}, c = {c}, G = {G}")
print(f"image-interval length c*lambda^G = {L} = {float(L):.6f}")
print(f"  >= 1+c = {float(1+c):.4f} (one block)  : {L >= 1 + c}")
print(f"  >= 2+c = {float(2+c):.4f} (two blocks) : {L >= 2 + c}")
print()


def blocks_in(u, v, c):
    """Integers k with [k, k+c] subset of [u, v]. Exact."""
    lo = math.ceil(u)                       # Fraction -> exact ceil
    hi = math.floor(v - c)                  # exact floor
    return list(range(lo, hi + 1))


def build(levels, branch):
    """branch: callable j -> index into the available block list at level j."""
    # I_0 : choose the block [1, 1+c] so that x > 1 (not required, but tidy)
    a = F(1)
    b = F(1) + c
    ivs = [(a, b)]
    for j in range(levels):
        s = lam ** ((j + 1) * G)
        u, v = a * s, b * s
        ks = blocks_in(u, v, c)
        assert len(ks) >= 2, (j, u, v, ks)
        k = ks[branch(j) % len(ks)]
        a, b = F(k) / s, (F(k) + c) / s
        ivs.append((a, b))
        assert ivs[-2][0] <= a and b <= ivs[-2][1], "not nested"
    return ivs


LEVELS = 60
for name, br in [("all-0", lambda j: 0), ("all-1", lambda j: 1),
                 ("mixed", lambda j: (j * j + 1) % 2)]:
    ivs = build(LEVELS, br)
    a, b = ivs[-1]
    # every point of the final interval satisfies all constraints up to LEVELS
    x = a  # exact rational representative inside I_LEVELS
    viol = []
    for i in range(LEVELS + 1):
        y = x * lam ** (i * G)
        fr = y - math.floor(y)
        if not (0 <= fr <= c):
            viol.append((i, fr))
    print(f"branch {name:6s}: x ~ {float(a):.17f}  |I_{LEVELS}| = {float(b-a):.3e}")
    print(f"  fract(x*lam^(iG)) in [0,c] for i=0..{LEVELS}: violations = {viol}")

# distinctness of branches (=> 2^aleph0 solutions => a transcendental one exists)
i0 = build(LEVELS, lambda j: 0)[-1]
i1 = build(LEVELS, lambda j: 1)[-1]
print(f"\nbranch all-0 and all-1 intervals disjoint: {i0[1] < i1[0] or i1[1] < i0[0]}")

# density lower bound actually achieved by one such x, over n < N
x = build(LEVELS, lambda j: 0)[-1][0]
N = 8 * LEVELS
hits = 0
for n in range(N):
    y = x * lam ** n
    fr = y - math.floor(y)
    if 0 <= fr <= c:
        hits += 1
print(f"\nover n < {N}: hits in [0,1/10] = {hits}  (density {float(F(hits,N)):.4f})")
print(f"  guaranteed by construction: >= ceil(N/G) = {-(-N//G)} (density >= {1/G})")
print(f"  required by equidistribution: density -> d - c = {float(c)}")
print(f"  1/G = {F(1,G)} > c = {c}: {F(1,G) > c}   => equidistribution FAILS at (0, 1/10)")
