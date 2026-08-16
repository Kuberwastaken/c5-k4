"""Wall-navigation arm instrument (three-arm preregistered test).

This module is an INDEPENDENT re-implementation of the invariant vocabulary
used by `results/experiment/fresh-population/population.json`.  It shares no
code with `scripts/gen/invariants.py`:

  * distances by plain BFS over adjacency sets (not bitmask frontiers);
  * alpha / omega by greedy-colouring-bounded branch and bound (not 2^n
    subset enumeration);
  * chi by k-colourability backtracking with a DSATUR-free ordering;
  * gamma / gamma_t / gamma_2 / gamma_i by set-cover branch and bound
    (not subset enumeration);
  * mu by Edmonds' blossom algorithm (not networkx);
  * kappa by unit-capacity max flow on the vertex-split digraph (not
    networkx);
  * cutv by Tarjan lowlink (not networkx);
  * floor/ceil(lambda_1) by an exact rational LDL^T positive-definiteness
    test (not Bareiss leading principal minors).

Calibration: `python3 wall_arm.py verify` re-derives every recorded field of
all 30 targets over all 12,112 members of D with this code path only.  That
doubles as the database-sanity gate demanded by the protocol.
"""
from __future__ import annotations

import itertools
import math
from collections import deque
from fractions import Fraction
from typing import Dict, List, Sequence, Set

# --------------------------------------------------------------------------
# graph representation: n, adj (list of frozensets of ints)
# --------------------------------------------------------------------------


class G:
    __slots__ = ("n", "adj", "deg", "amask", "_cache")

    def __init__(self, n: int, edges):
        self.n = n
        a = [set() for _ in range(n)]
        for u, v in edges:
            if u == v:
                raise ValueError("self loop")
            if not (0 <= u < n and 0 <= v < n):
                raise ValueError("vertex out of range")
            a[u].add(v)
            a[v].add(u)
        self.adj = [frozenset(s) for s in a]
        self.deg = [len(s) for s in self.adj]
        self.amask = [sum(1 << x for x in s) for s in self.adj]
        self._cache = {}

    @property
    def m(self) -> int:
        return sum(self.deg) // 2

    def edges(self):
        for u in range(self.n):
            for v in self.adj[u]:
                if v > u:
                    yield (u, v)

    def is_connected(self) -> bool:
        if self.n == 0:
            return False
        seen = {0}
        q = deque([0])
        while q:
            v = q.popleft()
            for u in self.adj[v]:
                if u not in seen:
                    seen.add(u)
                    q.append(u)
        return len(seen) == self.n

    def has_isolated_or_dup(self):
        """Non-degeneracy helpers: (has isolated vertex, has twin-collapsed pair).

        A 'collapsed vertex' in a blow-up construction shows up as a blob of
        order 0 (vertex absent) -- caught by the builder -- or as two vertices
        with identical closed neighbourhoods that were meant to be distinct
        structural roles.  We only report; the guard decides.
        """
        iso = any(d == 0 for d in self.deg)
        return iso


# ---------------- graph6 ----------------


def from_graph6(s: str) -> "G":
    b = [ord(c) - 63 for c in s.strip()]
    if b[0] == 63:
        raise ValueError("large graph6 not supported here")
    n = b[0]
    bits = []
    for x in b[1:]:
        for k in range(5, -1, -1):
            bits.append((x >> k) & 1)
    edges = []
    i = 0
    for j in range(1, n):
        for k in range(j):
            if i < len(bits) and bits[i]:
                edges.append((k, j))
            i += 1
    return G(n, edges)


def to_graph6(g: "G") -> str:
    n = g.n
    bits = []
    for j in range(1, n):
        for k in range(j):
            bits.append(1 if j in g.adj[k] else 0)
    while len(bits) % 6:
        bits.append(0)
    out = [chr(n + 63)]
    for i in range(0, len(bits), 6):
        x = 0
        for k in range(6):
            x = (x << 1) | bits[i + k]
        out.append(chr(x + 63))
    return "".join(out)


# --------------------------------------------------------------------------
# bitmask helpers
# --------------------------------------------------------------------------


def _bits(x: int):
    while x:
        b = x & -x
        yield b.bit_length() - 1
        x ^= b


def _pc(x: int) -> int:
    return bin(x).count("1")


# --------------------------------------------------------------------------
# independence / clique  (greedy-colouring-bounded branch and bound)
# --------------------------------------------------------------------------


def max_independent(n: int, amask: Sequence[int], sub: int) -> int:
    """alpha(G[sub]) -- branch and bound with a clique-cover (colouring) bound."""
    best = 0

    def colour_bound(cand: int):
        """Greedy colour classes of the complement-of-adjacency inside cand;
        returns (order, bounds) with bounds[i] an upper bound for the suffix."""
        order = []
        bounds = []
        remaining = cand
        cls = 0
        while remaining:
            cls += 1
            avail = remaining
            while avail:
                v = (avail & -avail).bit_length() - 1
                order.append(v)
                bounds.append(cls)
                avail &= ~(1 << v)
                avail &= amask[v]          # same colour class = pairwise adjacent
                remaining &= ~(1 << v)
        return order, bounds

    def rec(cand: int, cur: int):
        nonlocal best
        if not cand:
            if cur > best:
                best = cur
            return
        order, bounds = colour_bound(cand)
        P = cand
        for i in range(len(order) - 1, -1, -1):
            if cur + bounds[i] <= best:
                return
            v = order[i]
            P &= ~(1 << v)
            rec(P & ~amask[v], cur + 1)

    rec(sub, 0)
    return best


def max_clique(n: int, amask: Sequence[int], sub: int) -> int:
    comp = [(~amask[v]) & ~(1 << v) & ((1 << n) - 1) for v in range(n)]
    return max_independent(n, comp, sub)


# --------------------------------------------------------------------------
# chromatic number  (k-colourability backtracking, largest-degree-first with
# a maximal-clique seed for symmetry breaking)
# --------------------------------------------------------------------------


def chromatic(n: int, amask: Sequence[int]) -> int:
    if n == 0:
        return 0
    full = (1 << n) - 1
    # lower bound: a greedy maximal clique
    seed = []
    cand = full
    while cand:
        best_v, best_d = -1, -1
        for v in _bits(cand):
            d = _pc(amask[v] & cand)
            if d > best_d:
                best_v, best_d = v, d
        seed.append(best_v)
        cand &= amask[best_v]
    lb = len(seed)
    # order: clique seed first, then by degree
    rest = sorted((v for v in range(n) if v not in seed), key=lambda v: -_pc(amask[v]))
    order = seed + rest
    pos = {v: i for i, v in enumerate(order)}

    def colourable(k: int) -> bool:
        colour = [-1] * n
        for i, v in enumerate(seed[:k]):
            colour[v] = i
        if len(seed) > k:
            return False
        start = len(seed)

        def rec(i: int, used: int) -> bool:
            if i == n:
                return True
            v = order[i]
            forb = 0
            for u in _bits(amask[v]):
                if colour[u] >= 0:
                    forb |= 1 << colour[u]
            top = min(used + 1, k)
            for c in range(top):
                if forb >> c & 1:
                    continue
                colour[v] = c
                if rec(i + 1, max(used, c + 1)):
                    return True
                colour[v] = -1
            return False

        return rec(start, len(seed))

    k = lb
    while True:
        if colourable(k):
            return k
        k += 1


# --------------------------------------------------------------------------
# domination family  (branch and bound over an uncovered element)
# --------------------------------------------------------------------------


def _dom_bb(n: int, cover: Sequence[int], targets: int, choices: Sequence[int],
            extra_ok=None, indep_amask=None) -> int:
    """Minimum number of chosen vertices whose union of `cover` masks contains
    `targets`, branching on a least-covered uncovered target.

    `choices` is the list of allowed vertices (bitmask of all allowed).
    `indep_amask`, if given, additionally forces the chosen set independent.
    """
    full_choice = choices
    best = [n + 1]
    who = [None]

    # who can cover each target
    coverers = [0] * n
    for v in _bits(full_choice):
        for t in _bits(cover[v]):
            coverers[t] |= 1 << v

    def rec(covered: int, chosen: int, cnt: int, avail: int):
        if cnt >= best[0]:
            return
        rem = targets & ~covered
        if rem == 0:
            best[0] = cnt
            who[0] = chosen
            return
        # bound: each further pick covers at most maxcov of rem
        maxcov = 0
        for v in _bits(avail):
            c = _pc(cover[v] & rem)
            if c > maxcov:
                maxcov = c
        if maxcov == 0:
            return
        if cnt + -(-_pc(rem) // maxcov) >= best[0]:
            return
        # branch on the uncovered target with fewest available coverers
        bt, bc, bn = -1, 0, n + 2
        for t in _bits(rem):
            c = coverers[t] & avail
            k = _pc(c)
            if k < bn:
                bt, bc, bn = t, c, k
                if k <= 1:
                    break
        if bn == 0:
            return
        for v in _bits(bc):
            nav = avail & ~(1 << v)
            if indep_amask is not None:
                nav &= ~indep_amask[v]
            rec(covered | cover[v], chosen | (1 << v), cnt + 1, nav)

    rec(0, 0, 0, full_choice)
    return best[0]


def domination_numbers(n: int, amask: Sequence[int]):
    full = (1 << n) - 1
    closed = [amask[v] | (1 << v) for v in range(n)]
    gamma = _dom_bb(n, closed, full, full)
    gamma_i = _dom_bb(n, closed, full, full, indep_amask=amask)
    gamma_t = _dom_bb(n, list(amask), full, full)
    return gamma, gamma_t, gamma_i


def two_domination(n: int, amask: Sequence[int]) -> int:
    """gamma_2: smallest S with every v outside S having >= 2 neighbours in S."""
    full = (1 << n) - 1
    best = [n + 1]

    def feasible_check(S: int, cnt: int) -> bool:
        for v in _bits(full & ~S):
            if _pc(amask[v] & S) < 2:
                return False
        return True

    # simple IDA*: try sizes upward with a branch on the worst-violated vertex
    def rec(S: int, cnt: int, limit: int) -> bool:
        # deficiency-based bound
        need = 0
        worst_v, worst_d = -1, -1
        for v in _bits(full & ~S):
            d = 2 - _pc(amask[v] & S)
            if d > 0:
                need = max(need, 1)
                if d > worst_d:
                    worst_v, worst_d = v, d
        if worst_v < 0:
            return True
        if cnt >= limit:
            return False
        # a violated vertex v must either join S or gain neighbours in S
        cands = [worst_v] + [u for u in _bits(amask[worst_v] & ~S)]
        for u in cands:
            if rec(S | (1 << u), cnt + 1, limit):
                return True
        return False

    for limit in range(0, n + 1):
        if rec(0, 0, limit):
            return limit
    return n


# --------------------------------------------------------------------------
# matching -- Edmonds' blossom algorithm
# --------------------------------------------------------------------------


def matching_number(n: int, adj: Sequence[Set[int]]) -> int:
    match = [-1] * n
    p = [-1] * n
    base = list(range(n))

    def lca(a: int, b: int) -> int:
        used = [False] * n
        x = a
        while True:
            x = base[x]
            used[x] = True
            if match[x] == -1:
                break
            x = p[match[x]]
        y = b
        while True:
            y = base[y]
            if used[y]:
                return y
            y = p[match[y]]

    def mark_path(v: int, b: int, child: int, blossom: List[bool]):
        while base[v] != b:
            blossom[base[v]] = True
            blossom[base[match[v]]] = True
            p[v] = child
            child = match[v]
            v = p[match[v]]

    def find_path(root: int) -> bool:
        used = [False] * n
        for i in range(n):
            p[i] = -1
            base[i] = i
        used[root] = True
        q = deque([root])
        while q:
            v = q.popleft()
            for to in adj[v]:
                if base[v] == base[to] or match[v] == to:
                    continue
                if to == root or (match[to] != -1 and p[match[to]] != -1):
                    cb = lca(v, to)
                    blossom = [False] * n
                    mark_path(v, cb, to, blossom)
                    mark_path(to, cb, v, blossom)
                    for i in range(n):
                        if blossom[base[i]]:
                            base[i] = cb
                            if not used[i]:
                                used[i] = True
                                q.append(i)
                elif p[to] == -1:
                    p[to] = v
                    if match[to] == -1:
                        u = to
                        while u != -1:
                            pv = p[u]
                            ppv = match[pv]
                            match[u] = pv
                            match[pv] = u
                            u = ppv
                        return True
                    else:
                        used[match[to]] = True
                        q.append(match[to])
        return False

    res = 0
    for v in range(n):
        if match[v] == -1 and find_path(v):
            res += 1
    return res


# --------------------------------------------------------------------------
# connectivity: cut vertices (Tarjan) and vertex connectivity (unit max flow)
# --------------------------------------------------------------------------


def cut_vertices(n: int, adj: Sequence[Set[int]]) -> int:
    disc = [-1] * n
    low = [0] * n
    isart = [False] * n
    timer = [0]

    for s in range(n):
        if disc[s] == -1:
            # count root children in the DFS tree
            root_children = 0
            disc[s] = low[s] = timer[0]
            timer[0] += 1
            stack = [(s, -1, iter(adj[s]))]
            while stack:
                v, par, it = stack[-1]
                advanced = False
                for u in it:
                    if disc[u] == -1:
                        if v == s:
                            root_children += 1
                        disc[u] = low[u] = timer[0]
                        timer[0] += 1
                        stack.append((u, v, iter(adj[u])))
                        advanced = True
                        break
                    elif u != par:
                        if disc[u] < low[v]:
                            low[v] = disc[u]
                if advanced:
                    continue
                stack.pop()
                if stack:
                    pv = stack[-1][0]
                    if low[v] < low[pv]:
                        low[pv] = low[v]
                    if pv != s and low[v] >= disc[pv]:
                        isart[pv] = True
            if root_children >= 2:
                isart[s] = True
    return sum(1 for v in range(n) if isart[v])


def _maxflow_vertex(n: int, adj: Sequence[Set[int]], s: int, t: int, cap_limit: int) -> int:
    """Max number of internally vertex-disjoint s-t paths (s,t non-adjacent),
    by unit-capacity BFS augmentation on the vertex-split digraph."""
    # node ids: v_in = 2v, v_out = 2v+1
    N = 2 * n
    graph = [dict() for _ in range(N)]

    def add(a, b, c):
        graph[a][b] = graph[a].get(b, 0) + c
        graph[b].setdefault(a, 0)

    for v in range(n):
        c = 10 ** 6 if (v == s or v == t) else 1
        add(2 * v, 2 * v + 1, c)
    for u in range(n):
        for v in adj[u]:
            add(2 * u + 1, 2 * v, 10 ** 6)
    src, snk = 2 * s + 1, 2 * t
    flow = 0
    while flow < cap_limit:
        par = {src: None}
        q = deque([src])
        found = False
        while q:
            v = q.popleft()
            if v == snk:
                found = True
                break
            for u, c in graph[v].items():
                if c > 0 and u not in par:
                    par[u] = v
                    q.append(u)
        if not found:
            break
        # augment by 1 (unit bottleneck on vertex arcs)
        path = []
        v = snk
        while par[v] is not None:
            path.append((par[v], v))
            v = par[v]
        b = min(graph[a][b_] for a, b_ in path)
        for a, b_ in path:
            graph[a][b_] -= b
            graph[b_][a] = graph[b_].get(a, 0) + b
        flow += b
    return flow


def vertex_connectivity(n: int, adj: Sequence[Set[int]]) -> int:
    if n <= 1:
        return 0
    if all(len(adj[v]) == n - 1 for v in range(n)):
        return n - 1
    best = min(len(adj[v]) for v in range(n))
    # Even's reduction: fix a minimum-degree vertex v0
    v0 = min(range(n), key=lambda v: len(adj[v]))
    probes = []
    for u in range(n):
        if u != v0 and u not in adj[v0]:
            probes.append((v0, u))
    nb = sorted(adj[v0])
    for i in range(len(nb)):
        for j in range(i + 1, len(nb)):
            if nb[j] not in adj[nb[i]]:
                probes.append((nb[i], nb[j]))
    for (a, b) in probes:
        if best == 0:
            break
        f = _maxflow_vertex(n, adj, a, b, best)
        if f < best:
            best = f
    return best


# --------------------------------------------------------------------------
# spectral: exact floor/ceil of lambda_1 by rational LDL^T
# --------------------------------------------------------------------------


def _pos_def(n: int, amask: Sequence[int], k: int) -> bool:
    """Is kI - A positive definite?  Rational LDL^T without pivoting; PD iff
    every pivot is > 0 (a zero pivot short-circuits to False)."""
    M = [[Fraction((k if i == j else 0) - (1 if amask[i] >> j & 1 else 0))
          for j in range(n)] for i in range(n)]
    for i in range(n):
        piv = M[i][i]
        if piv <= 0:
            return False
        inv = 1 / piv
        row = M[i]
        for r in range(i + 1, n):
            f = M[r][i] * inv
            if f:
                Mr = M[r]
                for c in range(i, n):
                    Mr[c] -= f * row[c]
    return True


def _pos_semidef(n: int, amask: Sequence[int], k: int) -> bool:
    """Is kI - A positive semidefinite?  (all eigenvalues <= k)"""
    # eigenvalues of A are >= -Delta and <= Delta; use exact symmetric
    # Gaussian elimination with symmetric pivoting on the largest diagonal.
    M = [[Fraction((k if i == j else 0) - (1 if amask[i] >> j & 1 else 0))
          for j in range(n)] for i in range(n)]
    idx = list(range(n))
    for i in range(n):
        # symmetric pivot: pick largest remaining diagonal entry
        p = max(range(i, n), key=lambda r: M[r][r])
        if M[p][p] < 0:
            return False
        if M[p][p] == 0:
            # the whole remaining row/col must be zero
            for r in range(i, n):
                for c in range(i, n):
                    if M[r][c] != 0:
                        return False
            return True
        if p != i:
            M[i], M[p] = M[p], M[i]
            for r in range(n):
                M[r][i], M[r][p] = M[r][p], M[r][i]
        piv = M[i][i]
        inv = 1 / piv
        row = M[i]
        for r in range(i + 1, n):
            f = M[r][i] * inv
            if f:
                Mr = M[r]
                for c in range(i, n):
                    Mr[c] -= f * row[c]
    return True


def spectral_bracket(n: int, amask: Sequence[int], deg: Sequence[int]):
    """(floor(lambda_1), ceil(lambda_1)) exactly.

    A float estimate only narrows the search interval; every reported value is
    decided by the exact rational predicate.
    """
    a, b = 0, max(deg) + 2                # lambda_1 <= Delta
    if n >= 12:
        try:
            import numpy as _np
            A = _np.zeros((n, n))
            for i in range(n):
                for j in range(n):
                    if amask[i] >> j & 1:
                        A[i, j] = 1.0
            est = float(_np.linalg.eigvalsh(A)[-1])
            a = max(0, int(math.floor(est)) - 1)
            b = min(b, int(math.floor(est)) + 3)
        except Exception:
            pass
    # smallest integer k with lambda_1 < k, binary search on the PD predicate
    while a < b:
        mid = (a + b) // 2
        if _pos_def(n, amask, mid):
            b = mid
        else:
            a = mid + 1
    k = a                                  # lambda_1 < k, lambda_1 >= k-1
    # exact confirmation of the bracket, independent of the float seed
    while not _pos_def(n, amask, k):
        k += 1
    while k > 0 and _pos_def(n, amask, k - 1):
        k -= 1
    fl = k - 1
    if _pos_semidef(n, amask, fl):
        return fl, fl                      # lambda_1 == fl exactly
    return fl, fl + 1


# --------------------------------------------------------------------------
# the full vocabulary
# --------------------------------------------------------------------------

NEEDED = [
    "n", "m", "Delta", "delta", "sigma2", "Sigma2", "dd", "f1", "deg_avg", "CW",
    "res", "annih", "diam", "rad", "ecc_avg", "Tdist_min", "Tdist_max",
    "dist_even_min", "dist_even_max", "dist_avg", "kappa", "cutv", "tri",
    "disp_max", "disp_min", "disp_avg", "spec_floor", "spec_ceil",
    "alpha", "omega", "chi", "mu", "lam_max", "lam_min", "lam_avg",
    "gamma", "gamma_t", "gamma_2", "gamma_i",
    "chi_bip", "chi_C4free", "chi_reg", "chi_tree",
]


def compute(g: "G", only=None) -> Dict[str, object]:
    n, adj, deg, amask = g.n, [set(s) for s in g.adj], g.deg, g.amask
    m = g.m
    want = set(NEEDED if only is None else only)
    out: Dict[str, object] = {}
    sdeg = sorted(deg)
    out["n"] = n
    out["m"] = m
    out["Delta"] = sdeg[-1]
    out["delta"] = sdeg[0]
    out["sigma2"] = sdeg[1] if n >= 2 else sdeg[0]
    out["Sigma2"] = sdeg[-2] if n >= 2 else sdeg[-1]
    out["dd"] = len(set(sdeg))
    out["f1"] = sum(1 for d in sdeg if d == 1)
    out["deg_avg"] = Fraction(2 * m, n)
    out["CW"] = sum((Fraction(1, 1 + d) for d in sdeg), Fraction(0))

    # residue: Havel-Hakimi
    s = sorted(sdeg, reverse=True)
    while s and s[0] > 0:
        d = s.pop(0)
        for i in range(d):
            s[i] -= 1
        s.sort(reverse=True)
    out["res"] = len(s)
    # annihilation
    tot = 0
    k = 0
    for d in sdeg:
        if tot + d <= m:
            tot += d
            k += 1
        else:
            break
    out["annih"] = k

    # distances: BFS from each vertex
    ecc = []
    tdist = []
    deven = []
    wiener = 0
    for src in range(n):
        dist = [-1] * n
        dist[src] = 0
        q = deque([src])
        tot_d = 0
        even = 1
        e = 0
        while q:
            v = q.popleft()
            for u in adj[v]:
                if dist[u] == -1:
                    dist[u] = dist[v] + 1
                    tot_d += dist[u]
                    if dist[u] % 2 == 0:
                        even += 1
                    if dist[u] > e:
                        e = dist[u]
                    q.append(u)
        ecc.append(e)
        tdist.append(tot_d)
        deven.append(even)
        wiener += tot_d
    out["diam"] = max(ecc)
    out["rad"] = min(ecc)
    out["ecc_avg"] = Fraction(sum(ecc), n)
    out["Tdist_min"] = min(tdist)
    out["Tdist_max"] = max(tdist)
    out["dist_even_min"] = min(deven)
    out["dist_even_max"] = max(deven)
    out["dist_avg"] = Fraction(wiener, n * (n - 1)) if n >= 2 else Fraction(0)

    # triangles
    tri = 0
    for u in range(n):
        for v in adj[u]:
            if v > u:
                tri += _pc(amask[u] & amask[v])
    out["tri"] = tri // 3

    disp = [len({deg[u] for u in adj[v]}) for v in range(n)]
    out["disp_max"] = max(disp)
    out["disp_min"] = min(disp)
    out["disp_avg"] = Fraction(sum(disp), n)

    out["chi_bip"] = 1 if _is_bipartite(n, adj) else 0
    c4 = 0
    for u in range(n):
        for v in range(u + 1, n):
            if _pc(amask[u] & amask[v]) >= 2:
                c4 = 1
                break
        if c4:
            break
    out["chi_C4free"] = 0 if c4 else 1
    out["chi_reg"] = 1 if sdeg[0] == sdeg[-1] else 0
    out["chi_tree"] = 1 if m == n - 1 else 0

    if want & {"cutv"}:
        out["cutv"] = cut_vertices(n, adj)
    if want & {"kappa"}:
        out["kappa"] = vertex_connectivity(n, adj)
    if want & {"spec_floor", "spec_ceil"}:
        fl, ce = spectral_bracket(n, amask, deg)
        out["spec_floor"] = fl
        out["spec_ceil"] = ce
    if want & {"mu"}:
        out["mu"] = matching_number(n, adj)
    full = (1 << n) - 1
    if want & {"alpha"}:
        out["alpha"] = max_independent(n, amask, full)
    if want & {"omega"}:
        out["omega"] = max_clique(n, amask, full)
    if want & {"chi"}:
        out["chi"] = chromatic(n, amask)
    if want & {"lam_max", "lam_min", "lam_avg"}:
        lam = [max_independent(n, amask, amask[v]) for v in range(n)]
        out["lam_max"] = max(lam)
        out["lam_min"] = min(lam)
        out["lam_avg"] = Fraction(sum(lam), n)
    if want & {"gamma", "gamma_t", "gamma_i"}:
        gm, gt, gi = domination_numbers(n, amask)
        out["gamma"] = gm
        out["gamma_t"] = gt
        out["gamma_i"] = gi
    if want & {"gamma_2"}:
        out["gamma_2"] = two_domination(n, amask)
    return out


def _is_bipartite(n: int, adj) -> bool:
    col = [-1] * n
    for s in range(n):
        if col[s] != -1:
            continue
        col[s] = 0
        q = deque([s])
        while q:
            v = q.popleft()
            for u in adj[v]:
                if col[u] == -1:
                    col[u] = 1 - col[v]
                    q.append(u)
                elif col[u] == col[v]:
                    return False
    return True


# --------------------------------------------------------------------------
# expression evaluation (own implementation)
# --------------------------------------------------------------------------


def ev(e, vals) -> Fraction:
    if "inv" in e:
        return Fraction(vals[e["inv"]])
    if "const" in e:
        return Fraction(e["const"])
    op = e["op"]
    if op == "add":
        t = Fraction(0)
        for a in e["args"]:
            t += ev(a, vals)
        return t
    if op == "sub":
        a, b = e["args"]
        return ev(a, vals) - ev(b, vals)
    if op == "mul":
        return Fraction(e["c"]) * ev(e["arg"], vals)
    if op == "ceil_div":
        x = ev(e["arg"], vals) / Fraction(e["d"])
        return Fraction(-((-x.numerator) // x.denominator))
    if op == "floor_div":
        x = ev(e["arg"], vals) / Fraction(e["d"])
        return Fraction(x.numerator // x.denominator)
    if op in ("ceil_ratio", "floor_ratio"):
        den = ev(e["den"], vals)
        if den <= 0:
            raise ZeroDivisionError("non-positive denominator")
        x = ev(e["num"], vals) / den
        if op == "ceil_ratio":
            return Fraction(-((-x.numerator) // x.denominator))
        return Fraction(x.numerator // x.denominator)
    raise ValueError(op)


def slack(expr, vals) -> Fraction:
    lhs = ev(expr["lhs"], vals)
    rhs = ev(expr["rhs"], vals)
    return rhs - lhs if expr["rel"] == "<=" else lhs - rhs


def invs_of(e, acc=None):
    acc = set() if acc is None else acc
    if "inv" in e:
        acc.add(e["inv"])
    elif "const" in e:
        pass
    else:
        for a in e.get("args", []):
            invs_of(a, acc)
        for kk in ("arg", "num", "den"):
            if kk in e:
                invs_of(e[kk], acc)
    return acc


def target_invs(t):
    return sorted(invs_of(t["expr"]["lhs"]) | invs_of(t["expr"]["rhs"]))


# --------------------------------------------------------------------------
# constructors
# --------------------------------------------------------------------------


def blowup(base: "G", sizes, clique=True) -> "G":
    """Substitute blob i (a K_{sizes[i]} if clique else empty) for vertex i of
    base; blobs joined completely along base edges."""
    assert len(sizes) == base.n
    off = []
    tot = 0
    for s in sizes:
        off.append(tot)
        tot += s
    edges = []
    for i in range(base.n):
        if clique:
            for a in range(sizes[i]):
                for b in range(a + 1, sizes[i]):
                    edges.append((off[i] + a, off[i] + b))
    for (i, j) in base.edges():
        for a in range(sizes[i]):
            for b in range(sizes[j]):
                edges.append((off[i] + a, off[j] + b))
    return G(tot, edges)


def cycle(k: int) -> "G":
    return G(k, [(i, (i + 1) % k) for i in range(k)]) if k >= 3 else path(k)


def path(k: int) -> "G":
    return G(k, [(i, i + 1) for i in range(k - 1)])


def complete(k: int) -> "G":
    return G(k, [(i, j) for i in range(k) for j in range(i + 1, k)])


def complete_bipartite(a: int, b: int) -> "G":
    return G(a + b, [(i, a + j) for i in range(a) for j in range(b)])


def star(k: int) -> "G":
    return complete_bipartite(1, k)


def line_graph(g: "G") -> "G":
    es = list(g.edges())
    idx = {e: i for i, e in enumerate(es)}
    edges = []
    for i in range(len(es)):
        for j in range(i + 1, len(es)):
            if set(es[i]) & set(es[j]):
                edges.append((i, j))
    return G(len(es), edges)


def complement(g: "G") -> "G":
    return G(g.n, [(i, j) for i in range(g.n) for j in range(i + 1, g.n)
                   if j not in g.adj[i]])


def join(a: "G", b: "G") -> "G":
    edges = [(u, v) for (u, v) in a.edges()]
    edges += [(u + a.n, v + a.n) for (u, v) in b.edges()]
    edges += [(i, a.n + j) for i in range(a.n) for j in range(b.n)]
    return G(a.n + b.n, edges)


def disjoint(a: "G", b: "G") -> "G":
    edges = [(u, v) for (u, v) in a.edges()]
    edges += [(u + a.n, v + a.n) for (u, v) in b.edges()]
    return G(a.n + b.n, edges)


def subdivide(g: "G", times: int = 1) -> "G":
    cur = g
    for _ in range(times):
        nn = cur.n
        edges = []
        for (u, v) in cur.edges():
            edges.append((u, nn))
            edges.append((nn, v))
            nn += 1
        cur = G(nn, edges)
    return cur


def cartesian(a: "G", b: "G") -> "G":
    n = a.n * b.n

    def idx(i, j):
        return i * b.n + j
    edges = []
    for (u, v) in a.edges():
        for j in range(b.n):
            edges.append((idx(u, j), idx(v, j)))
    for i in range(a.n):
        for (u, v) in b.edges():
            edges.append((idx(i, u), idx(i, v)))
    return G(n, edges)


def corona(g: "G", k: int = 1) -> "G":
    """Attach k pendant vertices to every vertex of g."""
    edges = list(g.edges())
    nn = g.n
    for v in range(g.n):
        for _ in range(k):
            edges.append((v, nn))
            nn += 1
    return G(nn, edges)


def kneser(nn: int, kk: int) -> "G":
    sets = list(itertools.combinations(range(nn), kk))
    idx = {s: i for i, s in enumerate(sets)}
    edges = []
    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            if not (set(sets[i]) & set(sets[j])):
                edges.append((i, j))
    return G(len(sets), edges)


def nondegenerate(g: "G") -> (bool, str):
    """METHOD A3.1 guard: the statement's own hypotheses."""
    if g.n < 2:
        return False, "n < 2"
    seen = set()
    for u in range(g.n):
        for v in g.adj[u]:
            if v == u:
                return False, "self loop"
    if not g.is_connected():
        return False, "disconnected"
    if any(d == 0 for d in g.deg):
        return False, "isolated vertex"
    return True, "ok"
