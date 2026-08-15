# Exact triangular-lattice check for Erdos 1084.
# Lattice points p = i*(1,0) + j*(1/2, sqrt3/2); squared distance between
# (i1,j1),(i2,j2) with di=i1-i2, dj=j1-j2 is di^2 + di*dj + dj^2  (exact integer).
from math import isqrt
from itertools import combinations

def q(di, dj):  # exact squared distance in lattice units
    return di*di + di*dj + dj*dj

def hex_patch(n):
    """Centered hexagonal patch of 'radius' n in axial coords: |i|<=n,|j|<=n,|i+j|<=n."""
    pts = [(i, j) for i in range(-n, n+1) for j in range(-n, n+1) if abs(i+j) <= n]
    return pts

for n in range(0, 6):
    P = hex_patch(n)
    N = 3*n*n + 3*n + 1
    assert len(P) == N, (len(P), N)
    unit = 0
    mind = None
    for a, b in combinations(P, 2):
        d2 = q(a[0]-b[0], a[1]-b[1])
        if d2 == 1:
            unit += 1
        mind = d2 if mind is None or d2 < mind else mind
    rhs = 9*n*n + 3*n
    # Harborth closed form floor(3N - sqrt(12N-3)) computed exactly
    rad = 12*N - 3
    s = isqrt(rad)
    harb = 3*N - (s + 1) if s*s < rad and (s+1)*(s+1) <= rad else 3*N - s
    # careful exact floor of 3N - sqrt(rad):
    # floor(3N - sqrt(rad)) = 3N - ceil(sqrt(rad))
    ceil_s = s if s*s == rad else s+1
    harb = 3*N - ceil_s
    print(f"n={n} N={N} points={len(P)} min_sq_dist={mind} unitpairs={unit} "
          f"9n^2+3n={rhs} harborth_floor={harb} rad={rad} sqrt_exact={s*s==rad} "
          f"unit==rhs:{unit==rhs} harb==rhs:{harb==rhs} strict_lt_holds:{unit<rhs}")
