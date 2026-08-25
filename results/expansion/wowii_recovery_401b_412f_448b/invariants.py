"""Evaluate recovered/published wordings of WOWII 401b / 412f / 448b
under ALL plausible readings, against the c5-k4 arsenal + mandatory DB-sanity gate.
Exact integer/Fraction arithmetic throughout (no spectral quantities involved).
"""
import networkx as nx
from fractions import Fraction
from itertools import combinations
from functools import lru_cache

# ---------------------------------------------------------------- basic invariants

def dist_matrix(G):
    return dict(nx.all_pairs_shortest_path_length(G))

def tdist(G, v, dm):
    return sum(dm[v][u] for u in G.nodes)

def tdist_max(G, dm=None):
    dm = dm or dist_matrix(G)
    return max(tdist(G, v, dm) for v in G.nodes)

def triangles_at(G):
    T = {}
    for v in G.nodes:
        nb = list(G.neighbors(v))
        c = 0
        for i in range(len(nb)):
            for j in range(i+1, len(nb)):
                if G.has_edge(nb[i], nb[j]):
                    c += 1
        T[v] = c
    return T

def mu(G):
    """matching number, exact"""
    return len(nx.max_weight_matching(G, maxcardinality=True))

def radius(G):
    return nx.radius(G)

def gamma_2_brute(G):
    """2-domination number by exhaustive search (small n)."""
    V = list(G.nodes)
    n = len(V)
    adj = {v: set(G.neighbors(v)) for v in V}
    best = n
    for r in range(0, n+1):
        for combo in combinations(V, r):
            D = set(combo)
            ok = True
            for v in V:
                if v in D:
                    continue
                if len(adj[v] & D) < 2:
                    ok = False
                    break
            if ok:
                return r
    return best

def gamma_2_ilp(G, timeLimit=60):
    try:
        import pulp
    except ImportError:
        return gamma_2_brute(G)
    V = list(G.nodes)
    prob = pulp.LpProblem("gamma2", pulp.LpMinimize)
    x = {v: pulp.LpVariable(f"x_{v}", cat="Binary") for v in V}
    prob += pulp.lpSum(x.values())
    for v in V:
        nb = list(G.neighbors(v))
        prob += 2*x[v] + pulp.lpSum(x[w] for w in nb) >= 2
    solver = pulp.PULP_CBC_CMD(msg=0, timeLimit=timeLimit)
    prob.solve(solver)
    if pulp.LpStatus[prob.status] not in ("Optimal",):
        return None
    return int(round(sum(pulp.value(x[v]) for v in V)))

def gamma_2(G):
    return gamma_2_brute(G) if G.number_of_nodes() <= 18 else gamma_2_ilp(G)

def alpha_2_brute(G):
    """2-independence number: largest vertex set inducing max degree <= 1."""
    V = list(G.nodes)
    n = len(V)
    idx = {v: i for i, v in enumerate(V)}
    for r in range(n, 0, -1):
        for combo in combinations(V, r):
            S = set(combo)
            bad = False
            for v in combo:
                d = sum(1 for w in G.neighbors(v) if w in S)
                if d >= 2:
                    bad = True
                    break
            if not bad:
                return r
    return 0

def alpha_2_ilp(G, timeLimit=60):
    try:
        import pulp
    except ImportError:
        return alpha_2_brute(G)
    V = list(G.nodes)
    Delta = max(dict(G.degree()).values())
    prob = pulp.LpProblem("alpha2", pulp.LpMaximize)
    x = {v: pulp.LpVariable(f"x_{v}", cat="Binary") for v in V}
    prob += pulp.lpSum(x.values())
    for v in V:
        nb = list(G.neighbors(v))
        # if x_v=1 then at most 1 selected neighbor
        prob += pulp.lpSum(x[w] for w in nb) <= 1 + Delta * (1 - x[v])
    solver = pulp.PULP_CBC_CMD(msg=0, timeLimit=timeLimit)
    prob.solve(solver)
    if pulp.LpStatus[prob.status] != "Optimal":
        return None
    return int(round(sum(pulp.value(x[v]) for v in V)))

def alpha_2(G):
    return alpha_2_brute(G) if G.number_of_nodes() <= 20 else alpha_2_ilp(G)

# ------------------------------------------------- critical independent sets / H

def all_independent_sets(G, cap=400000):
    """Enumerate ALL independent subsets (as frozensets). Tailored fast paths for
    lexically-structured arsenal graphs; generic bitmask otherwise."""
    n = G.number_of_nodes()
    if n > 22:
        raise ValueError(f"generic enumeration too big for n={n}")
    V = list(G.nodes)
    adjmask = []
    for v in V:
        m = 0
        for w in G.neighbors(v):
            m |= 1 << idx_of(V, w)
        adjmask.append(m)
    out = []

    def rec(i, cur, banned):
        if i == n:
            out.append(cur.copy())
            return
        # branch: include V[i] if not banned
        if not (banned >> i) & 1:
            cur.append(V[i])
            rec(i+1, cur, banned | adjmask[i])
            cur.pop()
        rec(i+1, cur, banned)
    rec(0, [], 0)
    return [frozenset(s) for s in out]

def idx_of(V, v):
    return V.index(v)

def indep_sets_structured(G, kind, param=None):
    """Structured enumeration for arsenal graphs (returns list[frozenset])."""
    V = list(G.nodes)
    if kind == "C5Km":
        m = param
        blobs = [[m*b + i for i in range(m)] for b in range(5)]
        sets = [frozenset()]
        for b in range(5):
            for v in blobs[b]:
                sets.append(frozenset([v]))
            for bb in [(b+2) % 5]:
                pass
        for b in range(5):
            j = (b+2) % 5
            for u in blobs[b]:
                for w in blobs[j]:
                    sets.append(frozenset([u, w]))
        return sets
    if kind == "compC5K4":
        m = 4
        blobs = [[4*b+i for i in range(m)] for b in range(5)]
        from itertools import chain, combinations as combs
        def subsets(S):
            return [frozenset(c) for r in range(len(S)+1) for c in combs(S, r)]
        out = set()
        for b in range(5):
            out |= set(subsets(blobs[b]))
            j = (b+1) % 5  # adjacent-in-C5 blobs are NOT joined in the complement
            for A in subsets(blobs[b]):
                for B in subsets(blobs[j]):
                    out.add(A | B)
            j2 = (b-1) % 5
            for A in subsets(blobs[b]):
                for B in subsets(blobs[j2]):
                    out.add(A | B)
        return list(out)
    if kind == "CycK3":
        L = param  # 7 or 9
        blobs = [[3*b+i for i in range(3)] for b in range(L)]
        # independent sets pick <=1 per blob from pairwise non-adjacent blobs,
        # and any number of blobs forming an independent set in C_L (alpha<=floor(L/2))
        import itertools as it
        out = {frozenset()}
        # all independent blob-sets of C_L up to size floor(L/2)
        blobsets = []
        for r in range(1, L//2 + 1):
            for bs in combs(range(L), r):
                ok = all((bs[i]-bs[j]) % L not in (1, L-1)
                         for i in range(r) for j in range(i+1, r))
                if ok:
                    blobsets.append(bs)
        for bs in blobsets:
            pools = [blobs[b] for b in bs]
            for pick in it.product(*pools):
                out.add(frozenset(pick))
        return list(out)
    if kind == "Petersen":
        return all_independent_sets(G)
    if kind == "Paley":
        return all_independent_sets(G)
    raise ValueError(kind)

def critical_analysis(G, struct=None, param=None):
    """Return dict with deficits and H under both conventions.
    deficit(S) = |S| - |N(S)|.
    CONV-LIT: U quantifies over ALL independent sets (incl. empty);
              critical := argmax deficit; H = union of argmax sets (of any size).
    CONV-NE : restrict to NONEMPTY independent sets;
              critical := argmax deficit among nonempty;
              'maximum critical independent set' := maximum-cardinality members
              of the argmax family; H = union of those.
    """
    sets = struct if isinstance(struct, list) else all_independent_sets(G)
    info = []
    for S in sets:
        nb = set()
        for v in S:
            nb |= set(G.neighbors(v))
        d = len(S) - len(nb)
        info.append((S, d))
    best_lit = max(d for _, d in info)
    arg_lit = [S for S, d in info if d == best_lit]
    H_lit = frozenset().union(*arg_lit) if arg_lit else frozenset()
    ne = [(S, d) for S, d in info if S]
    best_ne = max(d for _, d in ne)
    arg_ne = [S for S, d in ne if d == best_ne]
    mx = max(len(S) for S in arg_ne)
    arg_ne_max = [S for S in arg_ne if len(S) == mx]
    H_ne = frozenset().union(*arg_ne_max)
    H_ne_all_argmax = frozenset().union(*arg_ne)
    return {
        "alpha_crit_lit": max(len(S) for S in arg_lit),
        "best_deficit_lit": best_lit,
        "H_lit_size": len(H_lit),
        "best_deficit_ne": best_ne,
        "n_argmax_ne": len(arg_ne),
        "max_card_among_argmax_ne": mx,
        "H_ne_size": len(H_ne),
        "H_ne_allargmax_size": len(H_ne_all_argmax),
        "alpha_crit_ne": mx,
    }

# ---------------------------------------------------------------- arsenal & gate

def C5Km(m):
    G = nx.Graph()
    G.add_nodes_from(range(5*m))
    blob = lambda v: v // m
    for u in range(5*m):
        for v in range(u+1, 5*m):
            if blob(u) == blob(v) or (blob(u)-blob(v)) % 5 in (1, 4):
                G.add_edge(u, v)
    return G

def CycKL(L, m):
    G = nx.Graph()
    G.add_nodes_from(range(L*m))
    blob = lambda v: v // m
    for u in range(L*m):
        for v in range(u+1, L*m):
            if blob(u) == blob(v) or (blob(u)-blob(v)) % L in (1, L-1):
                G.add_edge(u, v)
    return G

def paley(q):
    G = nx.Graph()
    G.add_nodes_from(range(q))
    sq = {(i*i) % q for i in range(1, q)}
    for u in range(q):
        for v in range(u+1, q):
            if (v-u) % q in sq:
                G.add_edge(u, v)
    return G

def arsenal():
    A = {}
    for m in range(2, 9):
        A[f"C5[{m}]"] = (C5Km(m), ("C5Km", m))
    for n in (7, 8, 9):
        A[f"T({n})"] = (nx.line_graph(nx.complete_graph(n)), ("generic", None))
    A["comp(C5[4])"] = (nx.complement(C5Km(4)), ("compC5K4", 4))
    A["C7[3]"] = (CycKL(7, 3), ("CycK3", 7))
    A["C9[3]"] = (CycKL(9, 3), ("CycK3", 9))
    A["Petersen"] = (nx.petersen_graph(), ("Petersen", None))
    A["Paley13"] = (paley(13), ("Paley", None))
    A["Paley17"] = (paley(17), ("Paley", None))
    return A

def gate_battery():
    B = {}
    for i, G in enumerate(nx.graph_atlas_g()):
        if 1 <= G.number_of_nodes() <= 7 and nx.is_connected(G):
            B[f"atlas{i}"] = G
    for k in range(5, 10):
        B[f"C{k}"] = nx.cycle_graph(k)
    B["P7"] = nx.path_graph(7)
    B["K3"] = nx.complete_graph(3)
    B["K7"] = nx.complete_graph(7)
    B["K3,3"] = nx.complete_bipartite_graph(3, 3)
    B["K4,4"] = nx.complete_bipartite_graph(4, 4)
    B["K5,5"] = nx.complete_bipartite_graph(5, 5)
    for lvs in range(2, 9):
        B[f"star(1,{lvs})"] = nx.star_graph(lvs)
    B["Petersen"] = nx.petersen_graph()
    return B
