#!/usr/bin/env python3
"""Sun's conjectures family: witness searches for
   232174: n=x+y, x,y>0, x+ny and x^2+ny^2 prime          (n>1)
   280831: n=x^2+y^2+z^2+w^2, x^4+1680y^3z square         (n>=0)
   281976: four squares, z<=w, x and x+24y squares        (n>=0)
   287616: n=T_x + P_y + Hh_z generalized polygonals      (n>=0)
   303656: n=a^2+b^2+3^c+5^d                              (n>1)
   308734: n=(2^a*3^b)^2+(2^c*5^d)^2+x^2+y^2              (n>1)
"""
import time
from sympy import isprime

def sun_232174(N):
    bad = []
    for n in range(2, N + 1):
        found = False
        for x in range(1, n):
            y = n - x
            if isprime(x + n * y) and isprime(x * x + n * y * y):
                found = True
                break
        if not found:
            bad.append(n)
    return bad

def squares_rep(n):
    """Lagrange via naive bounded search with pruning."""
    reps = []
    for x in range(int(n ** 0.5) + 1):
        r1 = n - x * x
        for y in range(int(r1 ** 0.5) + 1):
            r2 = r1 - y * y
            for z in range(int(r2 ** 0.5) + 1):
                w2 = r2 - z * z
                w = int(w2 ** 0.5)
                if w * w == w2:
                    return (x, y, z, w)
    return None

def sun_280831(N):
    bad = []
    for n in range(0, N + 1):
        found = False
        rep = squares_rep(n)
        # try to find any rep satisfying square condition; brute force over reps
        for x in range(0, int(n ** 0.5) + 1):
            for y in range(0, int((n - x*x) ** 0.5) + 1):
                v = x ** 4 + 1680 * y ** 3
                # need z,w: x^2+y^2+z^2+w^2=n and v = s^2 -> condition on remaining
                r2 = n - x * x - y * y
                if r2 < 0:
                    continue
                s = int(v ** 0.5)
                if s * s != v:
                    continue
                for z in range(0, int(r2 ** 0.5) + 1):
                    w2 = r2 - z * z
                    w = int(w2 ** 0.5)
                    if w * w == w2:
                        found = True
                        break
                if found:
                    break
            if found:
                break
        if not found:
            bad.append(n)
    return bad

t0 = time.time()
print("== 232174 (n<=800) ==")
bad = sun_232174(800)
print("no-witness n:", bad if bad else "NONE", f"({time.time()-t0:.1f}s)")

t0 = time.time()
print("== 287616 polygonal sum (n<=2000) ==")
# T=x(x+1)/2, P=y(3y+1)/2, H=z(5z+1)/2; precompute lists then 3-sum set
Np = 400
T = [x*(x+1)//2 for x in range(Np) if x*(x+1)//2 <= 300000]
P = [y*(3*y+1)//2 for y in range(-0+Np)]
H = [z*(5*z+1)//2 for z in range(Np)]
PH = set(p+h for p in P[:600] for h in H[:600])
missing = []
for n in range(0, 3000):
    okf = any((n-t) in PH for t in T if t <= n)
    if not okf:
        missing.append(n)
print("missing:", missing if missing else "NONE", f"({time.time()-t0:.1f}s)")
