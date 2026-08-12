"""Sweep the blown-up cycle family C5[K_m] against WOWII conjectures 63, 85, 64.

Confirms: all three are violated for every m >= 4 and are TIGHT (equality) at
m = 3. Also prints the invariants driving the cliff. Exact computations only.
"""
import itertools
import math

import networkx as nx


def blowup(k, m):
    """C_k[K_m]: k blobs of K_m on a cycle, complete join between adjacent blobs."""
    G = nx.Graph()
    G.add_nodes_from(range(k * m))
    blob = lambda v: v // m
    for u in range(k * m):
        for v in range(u + 1, k * m):
            if blob(u) == blob(v) or (blob(u) - blob(v)) % k in (1, k - 1):
                G.add_edge(u, v)
    return G


def alpha(G):
    c, _ = nx.max_weight_clique(nx.complement(G), weight=None)
    return len(c)


def max_induced_upto(G, prop, cap=8):
    """Largest t <= cap with some t-subset inducing prop; assumes monotone-ish
    check by scanning sizes upward until a size has no witness."""
    nodes = list(G.nodes())
    best = 0
    for t in range(1, cap + 1):
        found = False
        for S in itertools.combinations(nodes, t):
            if prop(G.subgraph(S)):
                found = True
                break
        if not found:
            return best
        best = t
    return best


def dist_even_min(G):
    dist = dict(nx.all_pairs_shortest_path_length(G))
    return min(sum(1 for u in G if dist[v][u] % 2 == 0) for v in G)


def ceil_sqrt(x):
    return 0 if x <= 0 else math.isqrt(x - 1) + 1


print(f"{'m':>2} {'n':>3} {'Δ':>3} {'f':>2} {'b':>2} {'tr':>2} {'de':>3} "
      f"{'C63 rhs':>8} {'C85 rhs':>8} {'C64 rhs':>8}  verdicts (violated?)")
for m in range(1, 6):
    G = blowup(5, m)
    n, Delta = G.number_of_nodes(), max(d for _, d in G.degree())
    a = alpha(G)
    f = max_induced_upto(G, nx.is_forest)
    b = max_induced_upto(G, nx.is_bipartite)
    tr = max_induced_upto(G, lambda g: nx.is_tree(g) if g.number_of_nodes() else False)
    de = dist_even_min(G)
    rhs63 = -((-(de + b + 1)) // 3)              # ceil((de + b + 1)/3)
    rhs85 = ceil_sqrt(1 + 2 * de)
    rhs64 = ceil_sqrt(a * (1 + (n % Delta)))
    v63, v85, v64 = f < rhs63, tr < rhs85, f < rhs64
    print(f"{m:>2} {n:>3} {Delta:>3} {f:>2} {b:>2} {tr:>2} {de:>3} "
          f"{rhs63:>8} {rhs85:>8} {rhs64:>8}  "
          f"C63:{'VIOLATED' if v63 else 'holds'} "
          f"C85:{'VIOLATED' if v85 else 'holds'} "
          f"C64:{'VIOLATED' if v64 else 'holds'}")

print("\nAnalytic (m >= 4): f=b=tree=4, alpha=2, dist_even=2m+1, "
      "n mod Delta = 5m mod (3m-1) = 2m+1;")
print("C63 rhs = ceil((2m+6)/3) >= 5, C85 rhs = ceil(sqrt(4m+3)) >= 5, "
      "C64 rhs = ceil(2*sqrt(m+1)) >= 5  -- all exceed 4 for every m >= 4.")
