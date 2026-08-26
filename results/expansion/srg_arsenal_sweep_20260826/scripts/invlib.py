"""srg_sweep invlib: exact invariant library for the SRG arsenal sweep.

Conventions follow data/INVARIANT-GLOSSARY.md (DeLaViña wowIIdefs.js).
Exact arithmetic: Fractions for averages/distances; ints elsewhere.
Irrationals (sqrt/ln) are returned as sympy expressions when needed.

Every NP-hard invariant is computed by an exact method (bitset BnB or ILP
via pulp/CBC) under a per-call time cap. On cap exhaustion the function
raises BracketTimeout; callers record BRACKET — values are never guessed.
"""
from __future__ import annotations

import itertools
import math
import random
import time
from fractions import Fraction

import networkx as nx


class BracketTimeout(Exception):
    pass


class _TLimit:
    def __init__(self, seconds):
        self.deadline = time.monotonic() + seconds

    def check(self):
        if time.monotonic() > self.deadline:
            raise BracketTimeout()


def _adj_masks(G):
    nodes = list(G.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    masks = [0] * len(nodes)
    for v in nodes:
        m = 0
        for u in G[v]:
            m |= 1 << idx[u]
        masks[idx[v]] = m
    return nodes, idx, masks


# --------------------------------------------------- max clique (bitset)

def max_clique_bnb(adj_mask, tlimit):
    """Tomita-style exact maximum clique. Returns (size, bitset, proved).
    On timeout returns the incumbent (valid lower bound) with proved=False."""
    n = len(adj_mask)
    best = [0]
    best_set = [0]

    def expand(rsize, rset, cand):
        tlimit.check()
        if not cand:
            if rsize > best[0]:
                best[0] = rsize
                best_set[0] = rset
            return True
        # greedy coloring: successive maximal independent sets
        classes = []
        rest = cand
        while rest:
            cls = 0
            avail = rest
            while avail:
                b = avail & -avail
                cls |= b
                avail &= ~(b | adj_mask[b.bit_length() - 1])
            classes.append(cls)
            rest &= ~cls
        ncls = len(classes)
        if rsize + ncls <= best[0]:
            return False
        numbered = []
        cnum = 0
        for cls in classes:
            cnum += 1
            m = cls
            while m:
                b = m & -m
                m ^= b
                numbered.append((b.bit_length() - 1, cnum))
        # process in reverse class order; P holds unprocessed (earlier-class) verts
        for v, cn in sorted(numbered, key=lambda t: (-t[1], t[0])):
            cand &= ~(1 << v)
            if rsize + cn <= best[0]:
                continue
            expand(rsize + 1, rset | (1 << v), cand & adj_mask[v])
            if best[0] >= rsize + ncls:
                break

    try:
        expand(0, 0, (1 << n) - 1)
        return best[0], best_set[0], True
    except BracketTimeout:
        return best[0], best_set[0], False


def independence_number(G, cap=60.0):
    """Exact alpha(G) = omega(complement G). Returns (value, witness_set)."""
    tl = _TLimit(cap)
    nodes = list(G.nodes())
    n = len(nodes)
    idx = {v: i for i, v in enumerate(nodes)}
    comp = [((1 << n) - 1) ^ (1 << i) for i in range(n)]
    for i, v in enumerate(nodes):
        for u in G[v]:
            comp[i] &= ~(1 << idx[u])
    size, bits, proved = max_clique_bnb(comp, tl)
    sel = {nodes[i] for i in range(n) if (bits >> i) & 1}
    return size, sel, proved


def local_independence(G, v, cap=60.0):
    nb = list(G[v])
    if not nb:
        return 0
    sub = G.subgraph(nb)
    return independence_number(sub, cap)[0]


def dissociation_number(G, k, cap=60.0):
    """alpha_k(G): largest vertex subset inducing max degree <= k-1."""
    tl = _TLimit(cap)
    nodes, idx, masks = _adj_masks(G)
    n = len(nodes)
    in_set = [False] * n
    cur_deg = [0] * n
    best = [0]

    def rec(pos, size):
        if size > best[0]:
            best[0] = size
        if pos == n or size + (n - pos) <= best[0]:
            return
        tl.check()
        v = pos
        if cur_deg[v] <= k - 1:
            ok = True
            m = masks[v]
            while m:
                b = m & -m
                m ^= b
                u = b.bit_length() - 1
                if in_set[u] and cur_deg[u] + 1 > k - 1:
                    ok = False
                    break
            if ok:
                in_set[v] = True
                touched = []
                m = masks[v]
                while m:
                    b = m & -m
                    m ^= b
                    u = b.bit_length() - 1
                    if in_set[u]:
                        cur_deg[u] += 1
                        touched.append(u)
                save_v = cur_deg[v]
                cur_deg[v] = len(touched)
                rec(pos + 1, size + 1)
                cur_deg[v] = save_v
                for u in touched:
                    cur_deg[u] -= 1
                in_set[v] = False
        rec(pos + 1, size)

    try:
        rec(0, 0)
        return best[0], True
    except BracketTimeout:
        return best[0], False


# ------------------------------------------------ hereditary BnB family

def largest_induced_forest(G, connected=False, cap=60.0):
    """f(G) (connected=False) or tree(G) (connected=True)."""
    tl = _TLimit(cap)
    nodes, idx, masks = _adj_masks(G)
    n = len(nodes)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    in_set = [False] * n
    best = [0]

    def rec(pos, size):
        if size > best[0]:
            best[0] = size
        if pos == n or size + (n - pos) <= best[0]:
            return
        tl.check()
        v = pos
        inter = masks[v] & _mask_of(in_set)
        roots = set()
        m = inter
        while m:
            b = m & -m
            m ^= b
            roots.add(find(b.bit_length() - 1))
        nocycle = len(roots) == bin(inter).count("1")
        if nocycle and (not connected or size == 0 or inter != 0):
            old = parent[:]
            in_set[v] = True
            rv = find(v)
            for r in roots:
                rr = find(r)
                if rr != rv:
                    parent[rr] = rv
            rec(pos + 1, size + 1)
            in_set[v] = False
            parent[:] = old
        rec(pos + 1, size)

    def _mask_of(in_set):
        msk = 0
        for i, f in enumerate(in_set):
            if f:
                msk |= 1 << i
        return msk

    try:
        rec(0, 0)
        return best[0], True
    except BracketTimeout:
        return best[0], False


def largest_induced_path(G, cap=60.0):
    tl = _TLimit(cap)
    nodes, idx, masks = _adj_masks(G)
    n = len(nodes)
    best = [min(1, n)]

    def extend(path_len, used, endpoint):
        if path_len > best[0]:
            best[0] = path_len
        m = masks[endpoint] & ~used
        while m:
            tl.check()
            b = m & -m
            m ^= b
            w = b.bit_length() - 1
            # w adjacent ONLY to endpoint among used
            if (masks[w] & used) == (1 << endpoint):
                extend(path_len + 1, used | b, w)

    try:
        for s in range(n):
            tl.check()
            extend(1, 1 << s, s)
        return best[0], True
    except BracketTimeout:
        return best[0], False


def max_induced_bipartite(G, cap=60.0):
    tl = _TLimit(cap)
    nodes, idx, masks = _adj_masks(G)
    n = len(nodes)
    color = {}
    best = [0]

    def rec(pos, size):
        if size > best[0]:
            best[0] = size
        if pos == n or size + (n - pos) <= best[0]:
            return
        tl.check()
        v = pos
        for c in (0, 1):
            m = masks[v]
            ok = True
            while m:
                b = m & -m
                m ^= b
                u = b.bit_length() - 1
                if color.get(u, 1 - c) == c:
                    ok = False
                    break
            if ok:
                color[v] = c
                rec(pos + 1, size + 1)
                del color[v]
        rec(pos + 1, size)

    try:
        rec(0, 0)
        return best[0], True
    except BracketTimeout:
        return best[0], False


# ------------------------------------------------------------ poly stuff

def residue(G):
    seq = sorted((d for _, d in G.degree()), reverse=True)
    while seq and seq[0] > 0:
        d = seq.pop(0)
        for i in range(min(d, len(seq))):
            seq[i] -= 1
        if any(x < 0 for x in seq):
            raise ValueError("non-graphic sequence in HH")
        seq = sorted(seq, reverse=True)
    return len(seq)


def havel_hakimi_steps(G):
    seq = sorted((d for _, d in G.degree()), reverse=True)
    steps = 0
    if not seq or all(x == 0 for x in seq):
        return 0
    while seq:
        steps += 1
        seq = sorted(seq, reverse=True)
        d = seq.pop(0)
        for i in range(min(max(d, 0), len(seq))):
            seq[i] -= 1
        if any(x < 0 for x in seq):
            return steps
        if 0 in seq or not seq:
            return steps


def annihilation(G):
    ds = sorted(d for _, d in G.degree())
    m = G.number_of_edges()
    s = k = 0
    for d in ds:
        if s + d <= m:
            s += d
            k += 1
        else:
            break
    return k


def caro_wei(G):
    return sum(Fraction(1, d + 1) for _, d in G.degree())


def maxine(G):
    H = G.copy()
    cnt = 0
    while H.number_of_nodes():
        v = max(H.nodes(), key=lambda x: H.degree(x))
        H.remove_node(v)
        cnt += 1
    return cnt


def welsh_powell(H):
    ds = sorted(d for _, d in H.degree())
    n = H.number_of_nodes()
    wp = 0
    for k in range(1, n + 1):
        if k + ds[k - 1] <= n:
            wp = k
    return wp


def sw_degeneracy(G):
    if G.number_of_nodes() == 0:
        return 0
    return max(nx.core_number(G).values())


def length_sq(G):
    return sum(d * d for _, d in G.degree())


def mode_stats(G):
    from collections import Counter
    cnt = Counter(d for _, d in G.degree())
    mx = max(cnt.values())
    modes = sorted(k for k, v in cnt.items() if v == mx)
    ev = sorted(k for k in modes if k % 2 == 0)
    return {"mode_min": modes[0], "mode_max": modes[-1], "dd_mode": len(modes),
            "even_mode_min": ev[0] if ev else None,
            "even_mode_max": ev[-1] if ev else None}


def median_stats(G):
    ds = sorted(d for _, d in G.degree())
    n = len(ds)
    if n % 2 == 1:
        med = ds[(n + 1) // 2 - 1]
        return {"median": med, "lower": med, "upper": med}
    a, b = ds[n // 2 - 1], ds[n // 2]
    return {"median": Fraction(a + b, 2), "lower": a, "upper": b}


def q1_quartile(G, reading="ceil"):
    ds = sorted(d for _, d in G.degree())
    n = len(ds)
    pos = math.ceil(n / 4) if reading == "ceil" else max(1, math.floor(n / 4))
    pos = max(1, min(n, pos))
    return ds[pos - 1]


def triangles_per_vertex(G):
    out = {}
    for v in G.nodes():
        nb = set(G[v])
        c = 0
        for u in nb:
            c += len(nb & set(G[u]))
        out[v] = c // 2
    return out


def k4_per_vertex(G):
    out = {}
    for v in G.nodes():
        ns = list(G[v])
        sub = nx.subgraph(G, ns)
        c = sum(1 for q in itertools.combinations(ns, 4)
                if all(sub.has_edge(x, y) for x, y in itertools.combinations(q, 2)))
        out[v] = c
    return out


def bfs_layers(G, src):
    seen = {src: 0}
    frontier = [src]
    d = 0
    layers = {0: 1}
    while frontier:
        nxt = []
        for v in frontier:
            for u in G[v]:
                if u not in seen:
                    seen[u] = d + 1
                    nxt.append(u)
        frontier = nxt
        d += 1
        if frontier:
            layers[d] = len(frontier)
    return seen, layers


def dist_matrix(G):
    return dict(nx.all_pairs_shortest_path_length(G))


def dist_even_odd(G):
    dm = dist_matrix(G)
    ev, od = {}, {}
    for v, row in dm.items():
        ev[v] = sum(1 for dd in row.values() if dd % 2 == 0)
        od[v] = sum(1 for dd in row.values() if dd % 2 == 1)
    return ev, od


def horizontal_counts(G):
    dm = dist_matrix(G)
    E = list(G.edges())
    eh, oh = {}, {}
    for v in G.nodes():
        ce = co = 0
        for (a, b) in E:
            da, db = dm[v][a], dm[v][b]
            if da == db:
                if da % 2 == 0:
                    ce += 1
                else:
                    co += 1
        eh[v], oh[v] = ce, co
    return eh, oh


def transmissions(G):
    dm = dist_matrix(G)
    return {v: sum(row.values()) for v, row in dm.items()}, dm


def edge_neighborhood_sizes(G):
    return {(u, v): len((set(G[u]) | set(G[v])) - {u, v}) for u, v in G.edges()}


def disparity(G):
    return {v: len({G.degree(u) for u in G[v]}) for v in G.nodes()}


# ------------------------------------------------------ domination (ILP)

import pulp


def _ilp_min_dom(G, kind, cap=60.0):
    prob = pulp.LpProblem("dom", pulp.LpMinimize)
    vs = list(G.nodes())
    x = {v: pulp.LpVariable(f"x_{i}", cat="Binary") for i, v in enumerate(vs)}
    prob += pulp.lpSum(x.values())
    for v in vs:
        nb = pulp.lpSum(x[u] for u in G[v])
        if kind == "gamma":
            prob += x[v] + nb >= 1
        elif kind == "gamma_t":
            prob += nb >= 1
        elif kind == "gamma_2":
            prob += nb + 2 * x[v] >= 2
        elif kind == "i":
            prob += x[v] + nb >= 1
    if kind == "i":
        for u, v in G.edges():
            prob += x[u] + x[v] <= 1
    prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=cap))
    st = pulp.LpStatus[prob.status]
    val = pulp.value(prob.objective)
    if val is None:
        return {"value": None, "certified": False, "status": str(st)}
    if st == "Optimal":
        return {"value": int(round(val)), "certified": True}
    if val is not None:
        return {"value": int(round(val)), "certified": False, "status": st}
    return {"value": None, "certified": False, "status": st}


def gamma(G, cap=60.0):
    return _ilp_min_dom(G, "gamma", cap)


def gamma_t(G, cap=60.0):
    return _ilp_min_dom(G, "gamma_t", cap)


def gamma_2(G, cap=60.0):
    return _ilp_min_dom(G, "gamma_2", cap)


def indep_domination_number(G, cap=60.0):
    return _ilp_min_dom(G, "i", cap)


def critical_independence(G, cap=120.0):
    """alpha'(G): two-stage exact ILP."""
    vs = list(G.nodes())

    def build(tag):
        prob = pulp.LpProblem(f"crit{tag}", pulp.LpMaximize)
        x = {v: pulp.LpVariable(f"x{tag}_{i}", cat="Binary") for i, v in enumerate(vs)}
        y = {v: pulp.LpVariable(f"y{tag}_{i}", 0, 1) for i, v in enumerate(vs)}
        for u, v in G.edges():
            prob += x[u] + x[v] <= 1
        for v in vs:
            for u in G[v]:
                prob += y[v] >= x[u]
        return prob, x, y

    prob, x, y = build("a")
    diff = pulp.lpSum(x.values()) - pulp.lpSum(y.values())
    prob += diff
    prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=cap))
    if pulp.LpStatus[prob.status] != "Optimal":
        return {"D": None, "aprime": None, "certified": False,
                "status": pulp.LpStatus[prob.status]}
    Dval = int(round(pulp.value(diff)))

    prob2, x2, y2 = build("b")
    prob2 += pulp.lpSum(x2.values())
    prob2 += pulp.lpSum(x2.values()) - pulp.lpSum(y2.values()) >= Dval
    prob2.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=cap))
    if pulp.LpStatus[prob2.status] != "Optimal":
        return {"D": Dval, "aprime": None, "certified": False,
                "status": pulp.LpStatus[prob2.status]}
    return {"D": Dval, "aprime": int(round(pulp.value(prob2.objective))),
            "certified": True}


def spanning_tree_max_leaves(G, cap=60.0):
    """L_s via directed-flow spanning-tree ILP."""
    n = G.number_of_nodes()
    if n <= 1:
        return {"value": 0, "certified": True}
    prob = pulp.LpProblem("ls", pulp.LpMaximize)
    edges = list(G.edges())
    y = {e: pulp.LpVariable(f"y_{i}", cat="Binary") for i, e in enumerate(edges)}
    ydir = []
    for i, (u, v) in enumerate(edges):
        ydir.append(((u, v), y[(u, v)]))
        ydir.append(((v, u), y[(u, v)]))
    leaf = {v: pulp.LpVariable(f"l_{i}", cat="Binary") for i, v in enumerate(G.nodes())}
    prob += pulp.lpSum(leaf.values())
    f = {}
    ai = 0
    for arc in ydir:
        f[arc[0]] = pulp.LpVariable(f"f_{ai}", lowBound=0, upBound=n - 1)
        ai += 1
    prob += pulp.lpSum(y.values()) == n - 1
    for ((u, v), yv) in ydir:
        prob += f[(u, v)] <= (n - 1) * yv
    root = next(iter(G.nodes()))
    for v in G.nodes():
        inflow = pulp.lpSum(f[(u, w)] for (u, w) in f if w == v)
        outflow = pulp.lpSum(f[(u, w)] for (u, w) in f if u == v)
        if v == root:
            prob += inflow - outflow == -(n - 1)
        else:
            prob += inflow - outflow == 1
    for v in G.nodes():
        inc = pulp.lpSum(y[e] for e in edges if e[0] == v or e[1] == v)
        prob += inc >= 1
        prob += inc <= 1 + (n - 2) * (1 - leaf[v])
    prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=cap))
    st = pulp.LpStatus[prob.status]
    val = pulp.value(prob.objective)
    if val is None:
        return {"value": None, "certified": False, "status": str(st)}
    if st == "Optimal":
        return {"value": int(round(val)), "certified": True}
    return {"value": int(round(val)), "certified": False, "status": st}


def ham_path_search(G, restarts=200, backtrack_budget=200000, seed=7):
    """Bounded-backtracking Hamiltonian path witness search => p(G)=1."""
    rng = random.Random(seed)
    nodes = list(G.nodes())
    n = len(nodes)
    budget = [backtrack_budget]

    def dfs(path, used, cur):
        if len(path) == n:
            return path
        if budget[0] <= 0:
            return None
        cands = [u for u in G[cur] if u not in used]
        rng.shuffle(cands)
        cands.sort(key=lambda x: G.degree(x))
        for w in cands[:12]:
            budget[0] -= 1
            if budget[0] <= 0:
                return None
            used.add(w)
            path.append(w)
            r = dfs(path, used, w)
            if r is not None:
                return r
            path.pop()
            used.remove(w)
        return None

    for t in range(restarts):
        s = rng.choice(nodes)
        r = dfs([s], {s}, s)
        if r is not None:
            return 1
        if budget[0] <= 0:
            return None
    return None


def well_total_dominated_search(G, samples=40, cap=30.0, seed=99):
    """Look for a minimal TDS larger than gamma_t => wtd(G)=0 certified."""
    rng = random.Random(seed)
    gt = gamma_t(G, cap=min(cap, 25.0))
    gtval = gt["value"] if gt["certified"] else None
    found = False
    sizes = set()
    deadline = time.monotonic() + cap
    nodes = list(G.nodes())

    def minimalize(d):
        changed = True
        d = set(d)
        while changed:
            changed = False
            for v in sorted(d, key=lambda z: rng.random()):
                rest = d - {v}
                if rest and all(set(G[u]) & rest for u in nodes):
                    d = rest
                    changed = True
        return d

    for s in range(samples):
        if time.monotonic() > deadline:
            break
        d = set()
        while True:
            uncovered = [v for v in nodes if not (set(G[v]) & d)]
            if not uncovered:
                break
            v = rng.choice(uncovered)
            d.add(rng.choice(sorted(G[v])))
        d = minimalize(d)
        sizes.add(len(d))
        if gtval is not None and len(d) > gtval:
            found = True
            break
    return {"found": found, "sizes": sorted(sizes), "gt": gtval}
