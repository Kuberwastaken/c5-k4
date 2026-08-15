"""Shared exact number-theory helpers (no sympy on this box)."""
import numpy as np

_SMALL_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37]

def is_prime(n):
    if n < 2: return False
    for p in _SMALL_PRIMES:
        if n % p == 0: return n == p
    d = n - 1; s = 0
    while d % 2 == 0: d //= 2; s += 1
    for a in _SMALL_PRIMES:
        x = pow(a, d, n)
        if x == 1 or x == n-1: continue
        for _ in range(s-1):
            x = x*x % n
            if x == n-1: break
        else:
            return False
    return True

def sieve_primes(n):
    """numpy bool array of primality for 0..n"""
    s = np.ones(n+1, dtype=bool); s[:2] = False
    for i in range(2, int(n**0.5)+1):
        if s[i]: s[i*i::i] = False
    return s

def smallest_prime_factor_sieve(n):
    spf = np.zeros(n+1, dtype=np.int64)
    for i in range(2, n+1):
        if spf[i] == 0:
            spf[i::i] = np.where(spf[i::i] == 0, i, spf[i::i])
    return spf

def factorint(n, spf=None):
    f = {}
    if spf is not None and n < len(spf):
        while n > 1:
            p = int(spf[n]); f[p] = f.get(p,0)+1; n //= p
        return f
    d = 2
    while d*d <= n:
        while n % d == 0: f[d] = f.get(d,0)+1; n //= d
        d += 1 if d == 2 else 2
    if n > 1: f[n] = f.get(n,0)+1
    return f

def isqrt(n):
    if n < 0: return -1
    x = int(n**0.5)
    while x*x > n: x -= 1
    while (x+1)*(x+1) <= n: x += 1
    return x

def is_square(n):
    if n < 0: return False
    r = isqrt(n); return r*r == n
