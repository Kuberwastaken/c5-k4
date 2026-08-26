"""Set-quantity helpers for WOWII reading evaluation (glossary defs)."""
from fractions import Fraction

import networkx as nx


def induced_edges(G, S):
    return G.subgraph(S).number_of_edges()


def induced_components(G, S):
    return nx.number_connected_components(G.subgraph(S))


def induced_isolates(G, S):
    H = G.subgraph(S)
    return sum(1 for v in H.nodes() if H.degree(v) == 0)


def induced_largest_component_order(G, S):
    H = G.subgraph(S)
    if H.number_of_nodes() == 0:
        return 0
    return max(len(c) for c in nx.connected_components(H))


def induced_max_degree(G, S):
    H = G.subgraph(S)
    if H.number_of_nodes() == 0:
        return 0
    return max(dict(H.degree()).values())


def induced_min_degree(G, S):
    H = G.subgraph(S)
    if H.number_of_nodes() == 0:
        return 0
    return min(dict(H.degree()).values())


def induced_mu(G, S):
    return len(nx.max_weight_matching(G.subgraph(S), maxcardinality=True))


def induced_alpha(G, S, cap=30.0):
    import invlib as iv
    val, _w, proved = iv.independence_number(G.subgraph(S), cap)
    if not proved:
        import xctx
        raise xctx.Undef(f"alpha(G[S]) uncertified (incumbent {val})")
    return val


def induced_gamma(G, S, cap=30.0):
    import invlib as iv
    r = iv.gamma(G.subgraph(S), cap)
    if not r.get("certified") or r.get("value") is None:
        import xctx
        raise xctx.Undef(f"gamma(G[S]) uncertified: {r}")
    return r["value"]


def induced_radius(G, S):
    H = G.subgraph(S)
    if H.number_of_nodes() == 0:
        return None  # undefined
    if nx.number_connected_components(H) > 1:
        return None  # undefined
    e = dict(nx.eccentricity(H))
    return min(e.values())


def N_of(G, S):
    out = set()
    for v in S:
        out |= set(G[v])
    return out - set(S)


def Nclosed_of(G, S):
    return N_of(G, S) | set(S)


def ecc_set(G, S):
    """Glossary def 52: max over v in V-S of dist(v, S)."""
    import networkx as _nx
    dm = dict(_nx.all_pairs_shortest_path_length(G))
    best = 0
    for v in G.nodes():
        if v in set(S):
            continue
        d = min(dm[v][s] for s in S) if S else None
        if d is None:
            return None
        best = max(best, d)
    return best


def dist_avg_within(G, S):
    """avg of all NONZERO pairwise distances within S."""
    import networkx as _nx
    S = list(S)
    tot = 0
    cnt = 0
    dm = dict(_nx.all_pairs_shortest_path_length(G))
    for i, a in enumerate(S):
        for b in S[i + 1:]:
            d = dm[a][b]
            if d > 0:
                tot += d
                cnt += 1
    return Fraction(tot, cnt) if cnt else Fraction(0)


def dist_avg_S_to_V(G, S):
    """avg of all nonzero dist(s,v), s in S, v in V."""
    import networkx as _nx
    dm = dict(_nx.all_pairs_shortest_path_length(G))
    tot = cnt = 0
    for s in S:
        for v in G.nodes():
            d = dm[s][v]
            if d > 0:
                tot += d
                cnt += 1
    return Fraction(tot, cnt) if cnt else Fraction(0)


def dist_avg_V_from_S(G, S):
    """avg over v in V of dist(v,S) (each v counted once; glossary def 95 style).
    Uses min distance to S; v in S contributes 0 -> excluded (>0 filter)."""
    import networkx as _nx
    dm = dict(_nx.all_pairs_shortest_path_length(G))
    vals = []
    for v in G.nodes():
        d = min(dm[v][s] for s in S) if S else None
        if d and d > 0:
            vals.append(d)
    return Fraction(sum(vals), len(vals)) if vals else Fraction(0)


def private_external_neighbors(G, S):
    """peN(S): vertices OUTSIDE S with exactly one neighbor in S."""
    Sset = set(S)
    cnt = 0
    for v in G.nodes():
        if v in Sset:
            continue
        k = sum(1 for u in G[v] if u in Sset)
        if k == 1:
            cnt += 1
    return cnt


def private_neighbors(G, S):
    """pN(S): vertices of V(G) (any) with exactly one neighbor in S."""
    Sset = set(S)
    cnt = 0
    for v in G.nodes():
        k = sum(1 for u in G[v] if u in Sset)
        if k == 1:
            cnt += 1
    return cnt


def degree_class(G, pred):
    return [v for v in G.nodes() if pred(G.degree(v))]


def neighbor_dominators(G, strict=True):
    """D = {v : exists u (u != v if strict) with N[u] subseteq N[v]}."""
    nodes = list(G.nodes())
    Nc = {v: frozenset(set(G[v]) | {v}) for v in nodes}
    D = []
    for v in nodes:
        for u in nodes:
            if strict and u == v:
                continue
            if Nc[u] <= Nc[v]:
                D.append(v)
                break
    return D


def girth_safe(G):
    try:
        g = min(len(c) for c in nx.cycle_basis(G)) if nx.cycle_basis(G) else None
    except Exception:
        g = None
    # cycle_basis misses some short cycles in dense graphs; do BFS-based girth
    best = None
    for src in G.nodes():
        # BFS girth from src
        dist = {src: 0}
        parent = {src: None}
        queue = [src]
        while queue:
            nxt = []
            for v in queue:
                for u in G[v]:
                    if u not in dist:
                        dist[u] = dist[v] + 1
                        parent[u] = v
                        nxt.append(u)
                    elif parent[v] != u:
                        cyc = dist[v] + dist[u] + 1
                        if best is None or cyc < best:
                            best = cyc
            queue = nxt
        if best == 3:
            break
    return best


def square_graph(G):
    """G^2."""
    H = nx.Graph()
    H.add_nodes_from(G.nodes())
    dm = dict(nx.all_pairs_shortest_path_length(G))
    for v in G.nodes():
        for u, d in dm[v].items():
            if 0 < d <= 2:
                H.add_edge(v, u)
    return H


def complement_local_lambda_stats(H, cap_each=8.0, max_vertices=None):
    """lambda stats of graph H (usually the complement): alpha of H[N(v)] per v."""
    import invlib as iv
    vals = {}
    vs = list(H.nodes()) if max_vertices is None else list(H.nodes())[:max_vertices]
    for v in vs:
        nb = list(H[v])
        if not nb:
            vals[v] = 0
            continue
        try:
            vals[v] = iv.local_independence(H, v, cap_each)
        except iv.BracketTimeout:
            return None
    return vals
