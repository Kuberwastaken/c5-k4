"""Exact chromatic number by DSATUR branch and bound (path-A solver).

``scripts/gen/invariants._chromatic_brute`` is a static-order branch and bound;
it is exact and fine on the n <= 8 database, but it does not terminate in
reasonable time on the 21--36 vertex members of the frozen catalogue (T(9),
C5[K5], C5[K6] all exceed 60 s).  This computes the *same* invariant --- the
chromatic number --- by saturation-ordered branch and bound, closed between

  * an upper bound witnessed by an explicit greedy (saturation-ordered) colouring
    written here, and
  * the lower bound max(omega, ceil(n / alpha)), both standard and both exact.

No SAT solver is used, so it remains independent of the path-B chromatic number
(``arm_catalogue_pathb._chromatic``, which is SAT-based).
"""
from __future__ import annotations

import time


def _pc(x):
    return bin(x).count("1")


def greedy_saturation_colouring(adj, n):
    """Explicit proper colouring by saturation ordering; returns the colour list."""
    colour = [-1] * n
    forb = [0] * n
    uncol = (1 << n) - 1
    while uncol:
        bv, bkey = -1, None
        x = uncol
        while x:
            b = x & -x
            v = b.bit_length() - 1
            x ^= b
            key = (_pc(forb[v]), _pc(adj[v] & uncol), -v)
            if bkey is None or key > bkey:
                bv, bkey = v, key
        v = bv
        c = 0
        while forb[v] >> c & 1:
            c += 1
        colour[v] = c
        for u in range(n):
            if adj[v] >> u & 1:
                forb[u] |= 1 << c
        uncol &= ~(1 << v)
    return colour


def rlf_colouring(adj, n):
    """Recursive-largest-first colouring: build one colour class at a time.

    Standard heuristic (Leighton 1979).  Much tighter than sequential greedy on
    dense graphs with small independence number, which is exactly where the
    branch and bound below would otherwise have to close a wide gap.
    """
    colour = [-1] * n
    uncoloured = (1 << n) - 1
    k = 0
    while uncoloured:
        U = uncoloured                       # candidates for this colour class
        W = 0                                # excluded: adjacent to the class
        cls = 0
        while U:
            bv, bkey = -1, None
            x = U
            while x:
                b = x & -x
                v = b.bit_length() - 1
                x ^= b
                key = (_pc(adj[v] & W), _pc(adj[v] & U), -v)
                if bkey is None or key > bkey:
                    bv, bkey = v, key
            cls |= 1 << bv
            W |= adj[bv] & U
            U &= ~(adj[bv] | (1 << bv))
        x = cls
        while x:
            b = x & -x
            colour[b.bit_length() - 1] = k
            x ^= b
        uncoloured &= ~cls
        k += 1
    return colour


def check_colouring(adj, n, colour):
    """True iff `colour` is a proper colouring of the graph given by `adj`."""
    if any(c < 0 for c in colour):
        return False
    for v in range(n):
        a = adj[v]
        for u in range(n):
            if a >> u & 1 and colour[u] == colour[v]:
                return False
    return True


def chromatic_dsatur(adj, n, clique_size=1, alpha=None, deadline=None,
                     candidate_colourings=()):
    """Exact chi(G).

    `clique_size` and `alpha` are the (independently computed) clique and
    independence numbers; both only feed the lower bound max(omega, ceil(n/alpha)).

    `candidate_colourings` may contain colourings found anywhere else (e.g. by the
    SAT path).  Each is **checked here** with `check_colouring` before it is
    allowed to lower the upper bound, so an unchecked colouring can never enter
    the answer: a colouring is a certificate, not a claim.  When the checked upper
    bound meets the lower bound the chromatic number is proved without any search.

    Raises TimeoutError if `deadline` (a time.monotonic value) is passed.
    Returns (chi, lower_bound, upper_bound, colouring, from_certificate).
    """
    if n == 0:
        return 0, 0, 0, [], False
    if all(a == 0 for a in adj):
        return 1, 1, 1, [0] * n, False

    col = greedy_saturation_colouring(adj, n)
    assert check_colouring(adj, n, col)
    col2 = rlf_colouring(adj, n)
    assert check_colouring(adj, n, col2)
    if max(col2) < max(col):
        col = col2
    from_cert = False
    for cand in candidate_colourings:
        if cand and len(cand) == n and check_colouring(adj, n, cand) \
                and max(cand) < max(col):
            col = list(cand)
            from_cert = True
    ub = max(col) + 1
    lb = max(1, clique_size)
    if alpha:
        lb = max(lb, -(-n // alpha))
    if lb >= ub:
        return ub, lb, ub, col, from_cert

    best = [ub]
    best_col = [list(col)]
    colour = [-1] * n
    ncnt = [[0] * (n + 1) for _ in range(n)]     # ncnt[v][c] = coloured nbrs of v with c

    def assign(v, c):
        colour[v] = c
        for u in range(n):
            if adj[v] >> u & 1:
                ncnt[u][c] += 1

    def unassign(v, c):
        colour[v] = -1
        for u in range(n):
            if adj[v] >> u & 1:
                ncnt[u][c] -= 1

    def rec(uncol, k):
        if deadline is not None and time.monotonic() > deadline:
            raise TimeoutError("chromatic_dsatur deadline")
        if k >= best[0]:
            return
        if uncol == 0:
            best[0] = k
            best_col[0] = list(colour)
            return
        bv, bkey = -1, None
        x = uncol
        while x:
            b = x & -x
            v = b.bit_length() - 1
            x ^= b
            sat = sum(1 for c in range(k) if ncnt[v][c])
            key = (sat, _pc(adj[v] & uncol), -v)
            if bkey is None or key > bkey:
                bv, bkey = v, key
        v = bv
        for c in range(min(k, best[0] - 1) + 1):
            if c < k and ncnt[v][c]:
                continue
            if c == k and k + 1 >= best[0]:
                continue
            assign(v, c)
            rec(uncol & ~(1 << v), max(k, c + 1))
            unassign(v, c)
            if best[0] <= lb:
                return

    rec((1 << n) - 1, 0)
    assert check_colouring(adj, n, best_col[0])
    return best[0], lb, ub, best_col[0], from_cert and best[0] == ub
