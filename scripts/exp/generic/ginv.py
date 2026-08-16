"""GENERIC ARM -- independent invariant evaluator.

Written from `invariant_definitions` in
`results/experiment/fresh-population/population.json` and the conventions pinned
in `results/experiment/fresh-population/GENERATION.md`.  This file shares no code
with `scripts/gen/invariants.py`; the two are cross-checked against each other by
`check_against_gen.py` (that is the "second code path" required by the
verification bar).

Everything is exact: `int` or `fractions.Fraction`.  No floating point value ever
reaches a statement (floats appear in exactly one place -- as an *unverified
guess* for the spectral radius, which is then confirmed or rejected by exact
rational arithmetic).

Graphs are (n, adj) with `adj` a list of vertex bitmasks.
"""
from __future__ import annotations

import math
import os
import random
from fractions import Fraction
from typing import Dict, List, Sequence

# --------------------------------------------------------------------------
# basics
# --------------------------------------------------------------------------


def pc(x: int) -> int:
    return bin(x).count("1")


def bits(x: int):
    while x:
        b = x & -x
        yield b.bit_length() - 1
        x ^= b


def from_graph6(s: str):
    """graph6 -> (n, adj).  Own decoder; no networkx."""
    data = [ord(c) - 63 for c in s.strip()]
    if data[0] == 63:  # 126 - 63, large-n forms
        if data[1] == 63:
            n = (data[2] << 30) | (data[3] << 24) | (data[4] << 18) | \
                (data[5] << 12) | (data[6] << 6) | data[7]
            rest = data[8:]
        else:
            n = (data[1] << 12) | (data[2] << 6) | data[3]
            rest = data[4:]
    else:
        n = data[0]
        rest = data[1:]
    adj = [0] * n
    bitstream = []
    for d in rest:
        for k in range(5, -1, -1):
            bitstream.append((d >> k) & 1)
    i = 0
    for j in range(1, n):
        for k in range(j):
            if i < len(bitstream) and bitstream[i]:
                adj[j] |= 1 << k
                adj[k] |= 1 << j
            i += 1
    return n, adj


def to_graph6(n: int, adj: Sequence[int]) -> str:
    bitstream = []
    for j in range(1, n):
        for k in range(j):
            bitstream.append(1 if (adj[j] >> k) & 1 else 0)
    while len(bitstream) % 6:
        bitstream.append(0)
    out = []
    if n <= 62:
        out.append(chr(n + 63))
    elif n <= 258047:
        out.append(chr(126))
        out.append(chr(((n >> 12) & 63) + 63))
        out.append(chr(((n >> 6) & 63) + 63))
        out.append(chr((n & 63) + 63))
    else:
        raise ValueError("n too large")
    for i in range(0, len(bitstream), 6):
        v = 0
        for b in bitstream[i:i + 6]:
            v = (v << 1) | b
        out.append(chr(v + 63))
    return "".join(out)


def is_connected(n: int, adj: Sequence[int]) -> bool:
    if n == 0:
        return False
    seen = 1
    frontier = 1
    while frontier:
        nxt = 0
        for v in bits(frontier):
            nxt |= adj[v]
        nxt &= ~seen
        seen |= nxt
        frontier = nxt
    return seen == (1 << n) - 1


# --------------------------------------------------------------------------
# independence / clique  (Tomita-style greedy-colouring branch and bound)
# --------------------------------------------------------------------------
def max_clique(n: int, adj: Sequence[int], S: int) -> int:
    """omega(G[S]) by MCS-style colouring-bounded branch and bound."""
    best = [0]

    def expand(P: int, size: int):
        # greedy colouring of P: colour class c is an independent set
        order = []
        colours = []
        Q = P
        klass = 0
        while Q:
            klass += 1
            Qk = Q
            while Qk:
                v = (Qk & -Qk).bit_length() - 1
                Qk &= ~(1 << v)
                Qk &= ~adj[v]
                Q &= ~(1 << v)
                order.append(v)
                colours.append(klass)
        for i in range(len(order) - 1, -1, -1):
            v = order[i]
            if size + colours[i] <= best[0]:
                return
            nxt = P & adj[v]
            if nxt:
                expand(nxt, size + 1)
            elif size + 1 > best[0]:
                best[0] = size + 1
            P &= ~(1 << v)

    if S:
        expand(S, 0)
    return best[0]


def _complement(n: int, adj: Sequence[int]) -> List[int]:
    full = (1 << n) - 1
    return [full & ~(adj[v] | (1 << v)) for v in range(n)]


def independence_number(n: int, adj: Sequence[int], S: int, comp=None) -> int:
    comp = _complement(n, adj) if comp is None else comp
    return max_clique(n, comp, S)


# --------------------------------------------------------------------------
# chromatic number  (clique-seeded DSATUR backtracking, "is it k-colourable?")
# --------------------------------------------------------------------------
def _greedy_dsatur_colours(n: int, adj: Sequence[int]) -> int:
    colour = [-1] * n
    satur = [0] * n            # bitmask of colours seen in the neighbourhood
    deg = [pc(a) for a in adj]
    used = 0
    for _ in range(n):
        best = -1
        bkey = None
        for v in range(n):
            if colour[v] >= 0:
                continue
            key = (pc(satur[v]), deg[v])
            if bkey is None or key > bkey:
                bkey, best = key, v
        c = 0
        while satur[best] >> c & 1:
            c += 1
        colour[best] = c
        used = max(used, c + 1)
        for u in bits(adj[best]):
            satur[u] |= 1 << c
    return used


def _k_colourable(n: int, adj: Sequence[int], k: int, clique: List[int]) -> bool:
    if len(clique) > k:
        return False
    colour = [-1] * n
    forb = [0] * n
    for i, v in enumerate(clique):
        colour[v] = i
        for u in bits(adj[v]):
            forb[u] |= 1 << i
    ncoloured = len(clique)
    maxused = len(clique)

    def rec(ncol: int, maxused: int) -> bool:
        if ncol == n:
            return True
        # DSATUR: most saturated uncoloured vertex
        best, bkey = -1, None
        for v in range(n):
            if colour[v] >= 0:
                continue
            key = (pc(forb[v]), pc(adj[v]))
            if bkey is None or key > bkey:
                bkey, best = key, v
        v = best
        hi = min(k, maxused + 1)
        for c in range(hi):
            if forb[v] >> c & 1:
                continue
            colour[v] = c
            touched = []
            for u in bits(adj[v]):
                if colour[u] < 0 and not (forb[u] >> c & 1):
                    forb[u] |= 1 << c
                    touched.append(u)
            if rec(ncol + 1, max(maxused, c + 1)):
                return True
            for u in touched:
                forb[u] &= ~(1 << c)
            colour[v] = -1
        return False

    return rec(ncoloured, maxused)


def chromatic_number(n: int, adj: Sequence[int]) -> int:
    if n == 0:
        return 0
    comp = _complement(n, adj)
    # a maximum clique, kept as an explicit vertex list, to seed and to bound
    cl = _max_clique_set(n, adj, (1 << n) - 1)
    lb = len(cl)
    ub = _greedy_dsatur_colours(n, adj)
    for k in range(lb, ub):
        if _k_colourable(n, adj, k, cl):
            return k
    return ub


def _max_clique_set(n: int, adj: Sequence[int], S: int) -> List[int]:
    """A maximum clique of G[S], as a vertex list."""
    best = [0, []]

    def expand(P: int, cur: List[int]):
        order, colours = [], []
        Q = P
        klass = 0
        while Q:
            klass += 1
            Qk = Q
            while Qk:
                v = (Qk & -Qk).bit_length() - 1
                Qk &= ~(1 << v)
                Qk &= ~adj[v]
                Q &= ~(1 << v)
                order.append(v)
                colours.append(klass)
        for i in range(len(order) - 1, -1, -1):
            v = order[i]
            if len(cur) + colours[i] <= best[0]:
                return
            cur.append(v)
            nxt = P & adj[v]
            if nxt:
                expand(nxt, cur)
            elif len(cur) > best[0]:
                best[0] = len(cur)
                best[1] = list(cur)
            cur.pop()
            P &= ~(1 << v)

    if S:
        expand(S, [])
    return best[1]


# --------------------------------------------------------------------------
# domination family  (branch on the most constrained unsatisfied constraint)
# --------------------------------------------------------------------------
def domination(n: int, adj: Sequence[int], kind: str) -> int:
    """kind in {gamma, gamma_t, gamma_2, gamma_i}; exact."""
    closed = [adj[v] | (1 << v) for v in range(n)]
    need2 = kind == "gamma_2"
    indep = kind == "gamma_i"
    pool0 = list(adj) if kind == "gamma_t" else closed

    def shortfall(v: int, picked: int) -> int:
        if need2:
            if picked >> v & 1:
                return 0
            return max(0, 2 - pc(adj[v] & picked))
        return 0 if (pool0[v] & picked) else 1

    # -- greedy incumbent
    picked = 0
    guard = 0
    while guard <= n:
        guard += 1
        short = [v for v in range(n) if shortfall(v, picked)]
        if not short:
            break
        bu, bg = -1, 0
        for u in range(n):
            if picked >> u & 1:
                continue
            if indep and (adj[u] & picked):
                continue
            g = 0
            for v in short:
                if pool0[v] >> u & 1:
                    g += 1
            if g > bg:
                bu, bg = u, g
        if bu < 0:
            picked = (1 << n) - 1
            break
        picked |= 1 << bu
    best = [pc(picked)]

    def lower_bound(unsat) -> int:
        used = 0
        lb = 0
        for v, need, pl in unsat:
            if pl & used:
                continue
            used |= pl
            lb += 1 if (pl >> v & 1) else need
        return lb

    def rec(picked: int, banned: int, k: int):
        if k + 1 > best[0]:
            return
        unsat = []
        for v in range(n):
            need = shortfall(v, picked)
            if not need:
                continue
            pl = (closed[v] if need2 else pool0[v]) & ~(picked | banned)
            if indep:
                for u in list(bits(pl)):
                    if adj[u] & picked:
                        pl &= ~(1 << u)
            if not (pl >> v & 1) and pc(adj[v] & pl) < need:
                return
            unsat.append((v, need, pl))
        if not unsat:
            if k < best[0]:
                best[0] = k
            return
        unsat.sort(key=lambda z: (pc(z[2]), -z[1], z[0]))
        if k + lower_bound(unsat) >= best[0]:
            return
        _, _, pl = unsat[0]
        ban = banned
        for u in bits(pl):
            rec(picked | (1 << u), ban, k + 1)
            ban |= 1 << u

    rec(0, 0, 0)
    return best[0]


# --------------------------------------------------------------------------
# matching number  (Tutte matrix rank over a large prime field, seeded)
# --------------------------------------------------------------------------
_TUTTE_P = (1 << 61) - 1


def matching_number(n: int, adj: Sequence[int], seeds=(1, 2)) -> int:
    """mu(G) = rank(Tutte matrix)/2.

    An evaluation of the Tutte matrix has rank <= the generic rank 2*mu, so this
    is always a valid lower bound and equals mu except on a set of evaluations of
    density < n/p (p = 2^61-1).  Two independent evaluations are taken.
    """
    best = 0
    for sd in seeds:
        rng = random.Random(sd * 1000003 + n)
        M = [[0] * n for _ in range(n)]
        for u in range(n):
            for v in bits(adj[u]):
                if v > u:
                    x = rng.randrange(1, _TUTTE_P)
                    M[u][v] = x
                    M[v][u] = _TUTTE_P - x
        # rank mod p
        r = 0
        row = 0
        for col in range(n):
            piv = -1
            for i in range(row, n):
                if M[i][col]:
                    piv = i
                    break
            if piv < 0:
                continue
            M[row], M[piv] = M[piv], M[row]
            inv = pow(M[row][col], _TUTTE_P - 2, _TUTTE_P)
            for i in range(row + 1, n):
                if M[i][col]:
                    f = M[i][col] * inv % _TUTTE_P
                    Mi, Mr = M[i], M[row]
                    for j in range(col, n):
                        if Mr[j]:
                            Mi[j] = (Mi[j] - f * Mr[j]) % _TUTTE_P
            row += 1
            r += 1
        best = max(best, r // 2)
    return best


# --------------------------------------------------------------------------
# vertex connectivity  (own Dinic on the vertex-split digraph)
# --------------------------------------------------------------------------
def _local_connectivity(n: int, adj: Sequence[int], s: int, t: int, cap: int) -> int:
    """Number of internally vertex-disjoint s-t paths, capped at `cap`."""
    if cap <= 0:
        return 0
    N = 2 * n
    INF = n + 5
    graph: List[List[int]] = [[] for _ in range(N)]
    to: List[int] = []
    capa: List[int] = []

    def add(u, v, c):
        graph[u].append(len(to))
        to.append(v)
        capa.append(c)
        graph[v].append(len(to))
        to.append(u)
        capa.append(0)

    for v in range(n):
        add(2 * v, 2 * v + 1, INF if (v == s or v == t) else 1)
    for u in range(n):
        for v in bits(adj[u]):
            if v > u:
                add(2 * u + 1, 2 * v, INF)
                add(2 * v + 1, 2 * u, INF)
    src, snk = 2 * s + 1, 2 * t
    flow = 0
    while flow < cap:
        level = [-1] * N
        level[src] = 0
        q = [src]
        qi = 0
        while qi < len(q):
            x = q[qi]
            qi += 1
            for e in graph[x]:
                if capa[e] > 0 and level[to[e]] < 0:
                    level[to[e]] = level[x] + 1
                    q.append(to[e])
        if level[snk] < 0:
            break
        it = [0] * N

        def dfs(x, f):
            if x == snk:
                return f
            while it[x] < len(graph[x]):
                e = graph[x][it[x]]
                y = to[e]
                if capa[e] > 0 and level[y] == level[x] + 1:
                    d = dfs(y, min(f, capa[e]))
                    if d > 0:
                        capa[e] -= d
                        capa[e ^ 1] += d
                        return d
                it[x] += 1
            return 0

        pushed = 0
        while True:
            f = dfs(src, cap - flow - pushed)
            if f <= 0:
                break
            pushed += f
            if flow + pushed >= cap:
                break
        if pushed == 0:
            break
        flow += pushed
    return min(flow, cap)


def vertex_connectivity(n: int, adj: Sequence[int]) -> int:
    if n <= 1:
        return 0
    deg = [pc(a) for a in adj]
    if min(deg) == n - 1:
        return n - 1
    v = min(range(n), key=lambda x: deg[x])
    K = deg[v]
    nonnb = [u for u in range(n) if u != v and not (adj[v] >> u & 1)]
    for u in nonnb:
        K = min(K, _local_connectivity(n, adj, v, u, K))
        if K == 0:
            return 0
    nb = list(bits(adj[v]))
    for i in range(len(nb)):
        for j in range(i + 1, len(nb)):
            x, y = nb[i], nb[j]
            if not (adj[x] >> y & 1):
                K = min(K, _local_connectivity(n, adj, x, y, K))
                if K == 0:
                    return 0
    return K


# --------------------------------------------------------------------------
# articulation points  (iterative Tarjan low-link)
# --------------------------------------------------------------------------
def cut_vertices(n: int, adj: Sequence[int]) -> int:
    disc = [-1] * n
    low = [0] * n
    parent = [-1] * n
    is_cut = [False] * n
    timer = 0
    for root in range(n):
        if disc[root] >= 0:
            continue
        stack = [(root, iter(list(bits(adj[root]))))]
        disc[root] = low[root] = timer
        timer += 1
        rootkids = 0
        while stack:
            x, it = stack[-1]
            advanced = False
            for y in it:
                if disc[y] < 0:
                    parent[y] = x
                    disc[y] = low[y] = timer
                    timer += 1
                    if x == root:
                        rootkids += 1
                    stack.append((y, iter(list(bits(adj[y])))))
                    advanced = True
                    break
                elif y != parent[x]:
                    if disc[y] < low[x]:
                        low[x] = disc[y]
            if not advanced:
                stack.pop()
                if stack:
                    p = stack[-1][0]
                    if low[x] < low[p]:
                        low[p] = low[x]
                    if p != root and low[x] >= disc[p]:
                        is_cut[p] = True
        if rootkids > 1:
            is_cut[root] = True
    return sum(1 for b in is_cut if b)


# --------------------------------------------------------------------------
# exact floor/ceil of the adjacency spectral radius
# --------------------------------------------------------------------------
def _pd_status(n: int, adj: Sequence[int], k: int) -> str:
    """Sylvester test on `kI - A`, fraction-free (Bareiss), all-integer.

    After Bareiss step `j` the entry `A[j][j]` *is* the `j`-th leading principal
    minor, so one O(n^3) integer pass settles positive definiteness.

    Returns "PD"   -- every leading principal minor is positive;
            "NEG"  -- the first non-positive leading principal minor is negative
                      (so the matrix has a negative eigenvalue);
            "ZERO" -- the first non-positive leading principal minor is zero
                      (undecided: semidefinite or indefinite).
    """
    M = [[(k if i == j else 0) - (1 if adj[i] >> j & 1 else 0)
          for j in range(n)] for i in range(n)]
    prev = 1
    for p in range(n):
        d = M[p][p]
        if d < 0:
            return "NEG"
        if d == 0:
            return "ZERO"
        Mp = M[p]
        for i in range(p + 1, n):
            Mi = M[i]
            a = Mi[p]
            if a:
                for j in range(p + 1, n):
                    Mi[j] = (Mi[j] * d - a * Mp[j]) // prev
            else:
                for j in range(p + 1, n):
                    Mi[j] = (Mi[j] * d) // prev
        prev = d
    return "PD"


def _is_psd(n: int, adj: Sequence[int], k: int) -> bool:
    """Exact positive-semidefiniteness of `kI - A`, symmetric elimination with
    diagonal pivoting.  Only ever called on the rare "ZERO" branch."""
    A = [[Fraction((k if i == j else 0) - (1 if adj[i] >> j & 1 else 0))
          for j in range(n)] for i in range(n)]
    size = n
    while size > 0:
        p = -1
        best = Fraction(0)
        for i in range(size):
            if A[i][i] < 0:
                return False
            if A[i][i] > best:
                best, p = A[i][i], i
        if p < 0:                       # every diagonal entry is 0
            for i in range(size):
                for j in range(size):
                    if A[i][j] != 0:
                        return False
            return True
        A[0], A[p] = A[p], A[0]
        for r in range(size):
            A[r][0], A[r][p] = A[r][p], A[r][0]
        d = A[0][0]
        for i in range(1, size):
            f = A[i][0] / d
            if f:
                for j in range(1, size):
                    A[i][j] -= f * A[0][j]
        A = [row[1:] for row in A[1:]]
        size -= 1
    return True


def _det_int(n: int, M: List[List[int]]) -> int:
    """Exact integer determinant, Bareiss with row pivoting."""
    A = [row[:] for row in M]
    sign = 1
    prev = 1
    for k in range(n - 1):
        if A[k][k] == 0:
            piv = -1
            for i in range(k + 1, n):
                if A[i][k] != 0:
                    piv = i
                    break
            if piv < 0:
                return 0
            A[k], A[piv] = A[piv], A[k]
            sign = -sign
        d = A[k][k]
        for i in range(k + 1, n):
            a = A[i][k]
            for j in range(k + 1, n):
                A[i][j] = (A[i][j] * d - a * A[k][j]) // prev
            A[i][k] = 0
        prev = d
    return sign * A[n - 1][n - 1] if n else 1


# "true"      -- ceil(lambda_1) faithful to the definition: it equals f only when
#                lambda_1 == f, i.e. when fI - A is positive *semi*definite.
# "generator" -- reproduces `scripts/gen/invariants._spectral_bracket`, which
#                returns f whenever det(fI - A) == 0.  Those differ on graphs
#                where f is an eigenvalue but is not the largest one; there are
#                19 such graphs in `D` (see check_against_gen.py --spectral-audit).
SPEC_CONVENTION = os.environ.get("GINV_SPEC", "true")


def spectral_floor_ceil(n: int, adj: Sequence[int]):
    """(floor(lambda_1), ceil(lambda_1)), exact.

    `lambda_1 < k` iff `kI - A` is positive definite, so
    `floor(lambda_1) = max{k : kI - A is not positive definite}`.  A float
    eigenvalue is used only to *guess* where to start; the guess is then
    confirmed by exact integer arithmetic and widened until proved, so no float
    can enter the answer.

    `ceil(lambda_1) = f` iff `lambda_1 = f` iff `fI - A` is positive
    semidefinite; otherwise `ceil(lambda_1) = f + 1`.
    """
    guess = 1
    try:
        import numpy as _np
        A = _np.zeros((n, n))
        for u in range(n):
            for v in bits(adj[u]):
                A[u, v] = 1.0
        guess = int(math.floor(float(max(_np.linalg.eigvalsh(A)))))
    except Exception:
        guess = 1
    guess = max(0, min(guess, n - 1))
    f = guess
    while f >= 0 and _pd_status(n, adj, f) == "PD":
        f -= 1
    while _pd_status(n, adj, f + 1) != "PD":
        f += 1
    if SPEC_CONVENTION == "generator":
        M = [[(f if i == j else 0) - (1 if adj[i] >> j & 1 else 0)
              for j in range(n)] for i in range(n)]
        return (f, f) if _det_int(n, M) == 0 else (f, f + 1)
    if _pd_status(n, adj, f) != "ZERO":
        return f, f + 1
    return (f, f) if _is_psd(n, adj, f) else (f, f + 1)


# --------------------------------------------------------------------------
# the vocabulary needed by the frozen population
# --------------------------------------------------------------------------
POLY = {
    "n", "m", "Delta", "delta", "Sigma2", "dd", "f1", "res", "annih",
    "diam", "rad", "ecc_avg", "dist_avg", "Tdist_min", "Tdist_max",
    "dist_even_min", "dist_even_max", "cutv", "tri", "disp_max", "disp_min",
    "disp_avg", "chi_bip", "chi_C4free", "chi_reg", "chi_tree", "deg_avg", "CW",
}


class Inv:
    """Lazy exact invariant bundle for one graph."""

    __slots__ = ("n", "adj", "c", "_comp")

    def __init__(self, n: int, adj: Sequence[int]):
        self.n = n
        self.adj = list(adj)
        self.c: Dict[str, object] = {}
        self._comp = None

    # -- helpers
    def comp(self):
        if self._comp is None:
            self._comp = _complement(self.n, self.adj)
        return self._comp

    def _degrees(self):
        if "_deg" not in self.c:
            self.c["_deg"] = [pc(a) for a in self.adj]
        return self.c["_deg"]

    def _bfs(self):
        if "_bfs" in self.c:
            return self.c["_bfs"]
        n, adj = self.n, self.adj
        ecc, tdist, deven = [], [], []
        wiener = 0
        for src in range(n):
            seen = 1 << src
            frontier = 1 << src
            d = 0
            tot = 0
            even = 1
            while frontier:
                nxt = 0
                for v in bits(frontier):
                    nxt |= adj[v]
                nxt &= ~seen
                if not nxt:
                    break
                d += 1
                cnt = pc(nxt)
                tot += d * cnt
                if d % 2 == 0:
                    even += cnt
                seen |= nxt
                frontier = nxt
            ecc.append(d)
            tdist.append(tot)
            deven.append(even)
            wiener += tot
        self.c["_bfs"] = (ecc, tdist, deven, wiener)
        return self.c["_bfs"]

    def _disp(self):
        if "_disp" in self.c:
            return self.c["_disp"]
        deg = self._degrees()
        out = []
        for v in range(self.n):
            out.append(len({deg[u] for u in bits(self.adj[v])}))
        self.c["_disp"] = out
        return out

    def _lam(self):
        if "_lam" in self.c:
            return self.c["_lam"]
        comp = self.comp()
        out = [max_clique(self.n, comp, self.adj[v]) for v in range(self.n)]
        self.c["_lam"] = out
        return out

    # -- public
    def get(self, key: str):
        v = self.c.get(key)
        if v is not None:
            return v
        v = self._compute(key)
        self.c[key] = v
        return v

    def _compute(self, key: str):
        n, adj = self.n, self.adj
        deg = self._degrees()
        if key == "n":
            return n
        if key == "m":
            return sum(deg) // 2
        if key == "Delta":
            return max(deg)
        if key == "delta":
            return min(deg)
        if key == "Sigma2":
            return sorted(deg)[-2] if n >= 2 else max(deg)
        if key == "dd":
            return len(set(deg))
        if key == "f1":
            return sum(1 for d in deg if d == 1)
        if key == "deg_avg":
            return Fraction(2 * (sum(deg) // 2), n)
        if key == "CW":
            return sum((Fraction(1, 1 + d) for d in deg), Fraction(0))
        if key == "res":
            s = sorted(deg, reverse=True)
            while s and s[0] > 0:
                d = s.pop(0)
                for i in range(d):
                    s[i] -= 1
                s.sort(reverse=True)
            return len(s)
        if key == "annih":
            m = sum(deg) // 2
            sd = sorted(deg)
            tot, k = 0, 0
            for i, d in enumerate(sd):
                tot += d
                if tot <= m:
                    k = i + 1
            return k
        if key in ("diam", "rad", "ecc_avg", "Tdist_min", "Tdist_max",
                   "dist_even_min", "dist_even_max", "dist_avg"):
            ecc, tdist, deven, wiener = self._bfs()
            return {
                "diam": max(ecc), "rad": min(ecc),
                "ecc_avg": Fraction(sum(ecc), n),
                "Tdist_min": min(tdist), "Tdist_max": max(tdist),
                "dist_even_min": min(deven), "dist_even_max": max(deven),
                "dist_avg": Fraction(wiener, n * (n - 1)) if n >= 2 else Fraction(0),
            }[key]
        if key in ("disp_max", "disp_min", "disp_avg"):
            d = self._disp()
            return {"disp_max": max(d), "disp_min": min(d),
                    "disp_avg": Fraction(sum(d), n)}[key]
        if key == "cutv":
            return cut_vertices(n, adj)
        if key == "kappa":
            return vertex_connectivity(n, adj)
        if key == "tri":
            t = 0
            for u in range(n):
                for v in bits(adj[u]):
                    if v > u:
                        t += pc(adj[u] & adj[v])
            return t // 3
        if key == "chi_bip":
            colour = [-1] * n
            for s in range(n):
                if colour[s] >= 0:
                    continue
                colour[s] = 0
                st = [s]
                while st:
                    x = st.pop()
                    for y in bits(adj[x]):
                        if colour[y] < 0:
                            colour[y] = 1 - colour[x]
                            st.append(y)
                        elif colour[y] == colour[x]:
                            return 0
            return 1
        if key == "chi_C4free":
            for u in range(n):
                for v in range(u + 1, n):
                    if pc(adj[u] & adj[v]) >= 2:
                        return 0
            return 1
        if key == "chi_reg":
            return 1 if max(deg) == min(deg) else 0
        if key == "chi_tree":
            return 1 if sum(deg) // 2 == n - 1 else 0
        if key in ("spec_floor", "spec_ceil"):
            f, c = spectral_floor_ceil(n, adj)
            self.c["spec_floor"] = f
            self.c["spec_ceil"] = c
            return f if key == "spec_floor" else c
        if key == "alpha":
            return max_clique(n, self.comp(), (1 << n) - 1)
        if key == "omega":
            return max_clique(n, adj, (1 << n) - 1)
        if key == "chi":
            return chromatic_number(n, adj)
        if key == "mu":
            return matching_number(n, adj)
        if key in ("lam_max", "lam_min", "lam_avg"):
            lam = self._lam()
            return {"lam_max": max(lam), "lam_min": min(lam),
                    "lam_avg": Fraction(sum(lam), n)}[key]
        if key in ("gamma", "gamma_t", "gamma_2", "gamma_i"):
            return domination(n, adj, key)
        raise KeyError(key)


# --------------------------------------------------------------------------
# expression evaluation (own reading of the AST grammar)
# --------------------------------------------------------------------------
def ev(expr, inv: Inv) -> Fraction:
    if "inv" in expr:
        return Fraction(inv.get(expr["inv"]))
    if "const" in expr:
        return Fraction(expr["const"])
    op = expr["op"]
    if op == "add":
        t = Fraction(0)
        for a in expr["args"]:
            t += ev(a, inv)
        return t
    if op == "sub":
        a, b = expr["args"]
        return ev(a, inv) - ev(b, inv)
    if op == "mul":
        return Fraction(expr["c"]) * ev(expr["arg"], inv)
    if op == "ceil_div":
        return Fraction(math.ceil(ev(expr["arg"], inv) / Fraction(expr["d"])))
    if op == "floor_div":
        return Fraction(math.floor(ev(expr["arg"], inv) / Fraction(expr["d"])))
    if op == "ceil_ratio":
        d = ev(expr["den"], inv)
        if d <= 0:
            raise ZeroDivisionError("non-positive denominator")
        return Fraction(math.ceil(ev(expr["num"], inv) / d))
    if op == "floor_ratio":
        d = ev(expr["den"], inv)
        if d <= 0:
            raise ZeroDivisionError("non-positive denominator")
        return Fraction(math.floor(ev(expr["num"], inv) / d))
    raise ValueError(op)


def slack(relation, inv: Inv) -> Fraction:
    lhs = ev(relation["lhs"], inv)
    rhs = ev(relation["rhs"], inv)
    return rhs - lhs if relation["rel"] == "<=" else lhs - rhs


def lhs_rhs(relation, inv: Inv):
    return ev(relation["lhs"], inv), ev(relation["rhs"], inv)


def invariants_of(expr, acc=None):
    acc = set() if acc is None else acc
    if "inv" in expr:
        acc.add(expr["inv"])
    elif "const" in expr:
        pass
    else:
        for a in expr.get("args", []):
            invariants_of(a, acc)
        for k in ("arg", "num", "den"):
            if k in expr:
                invariants_of(expr[k], acc)
    return acc
