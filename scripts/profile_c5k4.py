"""Ground-truth invariant profile of C5[K4] for the WOWII open-conjecture sweep.

C5[K4] = lexicographic product: 5 blobs of K4 arranged on a cycle, complete
join between adjacent blobs. Vertex v = 4*i + j, blob i in Z5, j in 0..3.
Everything here is exact; expensive invariants use the graph's structure
(vertex-transitivity, diameter 2) plus brute force where cheap.
"""
import itertools, json, math
from fractions import Fraction

import networkx as nx


def build():
    G = nx.Graph()
    G.add_nodes_from(range(20))
    blob = lambda v: v // 4
    for u in range(20):
        for v in range(u + 1, 20):
            if blob(u) == blob(v) or (blob(u) - blob(v)) % 5 in (1, 4):
                G.add_edge(u, v)
    return G


G = build()
n, m = G.number_of_nodes(), G.number_of_edges()
P = {"n": n, "m": m}
assert (n, m) == (20, 110)

degs = sorted(d for _, d in G.degree())
P["degree_sequence"] = degs
P["Delta"] = max(degs); P["delta"] = min(degs)
assert P["Delta"] == P["delta"] == 11  # 11-regular
P["regular"] = True
P["deg_avg"] = "11"; P["mode_deg"] = 11; P["median_deg"] = 11
P["dd_distinct_degrees"] = 1; P["second_smallest_deg"] = 11
P["second_largest_deg"] = 11; P["q1_deg"] = 11
P["even_mode"] = None  # all degrees are 11 (odd): no even degree exists — convention gap
P["freq_deg_1"] = 0; P["isolates"] = 0; P["support_vertices"] = 0
P["length_G"] = "sqrt(2420) = 2*sqrt(605) ~= 49.1935"
P["CW_caro_wei"] = str(Fraction(20, 12))  # sum 1/(1+11)
P["sum_degrees"] = 220

# ---- distances ----
dist = dict(nx.all_pairs_shortest_path_length(G))
ecc = {v: max(dist[v].values()) for v in G}
P["ecc_all"] = sorted(set(ecc.values()))
assert set(ecc.values()) == {2}
P["radius"] = 2; P["diameter"] = 2; P["ecc_avg"] = "2"
P["center"] = "V (all 20)"; P["periphery"] = "V (all 20)"
de = {v: sum(1 for u in G if dist[v][u] % 2 == 0) for v in G}  # counts v itself
do = {v: sum(1 for u in G if dist[v][u] % 2 == 1) for v in G}
assert set(de.values()) == {9} and set(do.values()) == {11}
P["dist_even_v"] = 9   # min=max=avg (self counted; 8 if not)
P["dist_odd_v"] = 11
P["Tdist_v"] = 27      # 11*1 + 8*2, all v
P["dist_avg_V"] = str(Fraction(sum(dist[u][v] for u in G for v in G if u != v), 20 * 19))
# horizontal(v): edges with both ends at same distance from v; even/odd variants
hor, ehor, ohor = set(), set(), set()
for v in G:
    h = sum(1 for a, b in G.edges() if dist[v][a] == dist[v][b])
    he = sum(1 for a, b in G.edges() if dist[v][a] == dist[v][b] and dist[v][a] % 2 == 0)
    ho = sum(1 for a, b in G.edges() if dist[v][a] == dist[v][b] and dist[v][a] % 2 == 1)
    hor.add(h); ehor.add(he); ohor.add(ho)
P["horizontal_v"] = sorted(hor); P["even_horizontal_v"] = sorted(ehor)
P["odd_horizontal_v"] = sorted(ohor)
P["diametrical_pairs"] = sum(1 for u in G for v in G if u < v and dist[u][v] == 2)
P["R_v_radial_circle_size"] = 8  # dist-2 set from any (center) vertex
P["G_squared"] = "K20 (diameter 2 => G^2 complete)"

# ---- independence / clique family ----
comp = nx.complement(G)
clq, _ = nx.max_weight_clique(comp, weight=None)
P["alpha"] = len(clq); assert P["alpha"] == 2
w, _ = nx.max_weight_clique(G, weight=None)
P["omega"] = len(w); assert P["omega"] == 8
P["vertex_cover"] = n - P["alpha"]  # 18
lam = {}
for v in G:
    Nv = G.subgraph(list(G[v]))
    c2, _ = nx.max_weight_clique(nx.complement(Nv), weight=None)
    lam[v] = len(c2)
assert set(lam.values()) == {2}
P["lambda_v"] = 2  # min=max=avg
# maxine: greedy delete a max-degree vertex until no edges remain; count survivors
H = G.copy()
while H.number_of_edges():
    vmax = max(H.degree(), key=lambda t: (t[1], -t[0]))[0]
    H.remove_node(vmax)
P["maxine"] = H.number_of_nodes()
# critical independence: max over independent S of |S|-|N(S)| ; alpha' = largest
# critical independent set. Independent sets here have size <= 2.
best_sur, best_size = 0, 0  # empty set
for k in (1, 2):
    for S in itertools.combinations(G, k):
        if k == 2 and G.has_edge(*S):
            continue
        NS = set().union(*(set(G[v]) for v in S)) - set(S)
        sur = k - len(NS)
        if sur > best_sur or (sur == best_sur and k > best_size):
            best_sur, best_size = sur, k
P["critical_independence_alpha_prime"] = best_size if best_sur >= 0 else 0
P["critical_surplus_max"] = best_sur
# alphacore: intersection of all maximum independent sets
maxis = [S for S in itertools.combinations(G, 2)
         if not G.has_edge(*S)]
inter = set(G.nodes())
for S in maxis:
    inter &= set(S)
P["alphacore"] = len(inter)
P["num_max_independent_sets"] = len(maxis)
# k-independence (max induced subgraph with max degree <= k-1) via ILP
import pulp
def alpha_k(k):
    pr = pulp.LpProblem("ak", pulp.LpMaximize)
    x = {v: pulp.LpVariable(f"x{v}", cat="Binary") for v in G}
    pr += pulp.lpSum(x.values())
    for v in G:
        pr += pulp.lpSum(x[u] for u in G[v]) <= (k - 1) + 11 * (1 - x[v])
    pr.solve(pulp.PULP_CBC_CMD(msg=0))
    return int(sum(x[v].value() for v in G))
P["alpha_k"] = {k: alpha_k(k) for k in (1, 2, 3, 4, 5)}
assert P["alpha_k"][1] == 2

# ---- matching / paths / hamiltonicity ----
P["mu_matching"] = len(nx.max_weight_matching(G, maxcardinality=True))
assert P["mu_matching"] == 10
ham = [4 * (i % 5) + j for i in range(5) for j in range(4)]
path_order = []
for i in range(5):
    path_order += [4 * i + j for j in range(4)]
assert all(G.has_edge(path_order[t], path_order[t + 1]) for t in range(19))
assert G.has_edge(path_order[-1], path_order[0])
P["traceable"] = True; P["hamiltonian_cycle"] = True
P["path_cover_p"] = 1
P["kappa_connectivity"] = nx.node_connectivity(G)
P["cut_vertices"] = len(list(nx.articulation_points(G)))
P["components"] = 1
P["girth"] = 3
P["triangles_total"] = sum(nx.triangles(G).values()) // 3
tri = nx.triangles(G)
P["T_v_triangles_at_vertex"] = sorted(set(tri.values()))
assert set(tri.values()) == {39}

# ---- degree-sequence machinery ----
def residue(seq):
    s = sorted(seq, reverse=True)
    while s and s[0] > 0:
        d = s.pop(0)
        for i in range(d):
            s[i] -= 1
        s.sort(reverse=True)
    return len(s)
def hh_first_zero(seq):
    s = sorted(seq, reverse=True)
    k = 0
    if 0 in s: return 0
    while s and s[0] > 0:
        d = s.pop(0); k += 1
        for i in range(d):
            s[i] -= 1
        s.sort(reverse=True)
        if 0 in s:
            return k
    return k
P["residue"] = residue([11] * 20)
P["HH_k_first_zero"] = hh_first_zero([11] * 20)
P["annihilation"] = 10
P["SW_szekeres_wilf"] = 11  # d-regular => degeneracy = d
P["WP_complement"] = 12     # complement 8-regular: max k with k + 8 <= 20

# ---- domination family (exact brute force, small k first) ----
Ncl = {v: set(G[v]) | {v} for v in G}
Nop = {v: set(G[v]) for v in G}
def min_set(pred, kmax=8):
    for k in range(1, kmax + 1):
        for S in itertools.combinations(G, k):
            if pred(set(S)):
                return k
    return None
P["gamma"] = min_set(lambda S: set().union(*(Ncl[v] for v in S)) == set(G))
P["gamma_t"] = min_set(lambda S: all(Nop[v] & S for v in G))
P["gamma_i"] = min_set(lambda S: set().union(*(Ncl[v] for v in S)) == set(G)
                       and not any(G.has_edge(a, b) for a, b in itertools.combinations(S, 2)))
P["gamma_2"] = min_set(lambda S: all(v in S or len(Nop[v] & S) >= 2 for v in G))
P["gamma_c"] = min_set(lambda S: set().union(*(Ncl[v] for v in S)) == set(G)
                       and nx.is_connected(G.subgraph(S)))
P["L_s_max_leaves_spanning_tree"] = n - P["gamma_c"]
assert (P["gamma"], P["gamma_t"], P["gamma_i"], P["gamma_2"], P["gamma_c"]) == (2, 3, 2, 4, 3)
# well-total-dominated? find a minimal TDS larger than gamma_t
S = {0, 1, 8, 9}  # 2 in blob0 + 2 in blob2
assert all(Nop[v] & S for v in G)
def is_tds(T): return all(Nop[v] & T for v in G)
assert not any(is_tds(S - {x}) for x in S)  # minimal
P["well_total_dominated"] = False
P["wtd_witness"] = "minimal TDS {0,1,8,9} (size 4) > gamma_t=3"

# ---- induced-order invariants: certify max = 4 by exhausting 5-subsets ----
def max_induced(prop):
    best = 0
    for k in (5, 4):
        found = False
        for S in itertools.combinations(range(20), k):
            g = G.subgraph(S)
            if prop(g):
                found = True; break
        if found:
            return k, S
    return None
def is_forest(g): return nx.is_forest(g)
def is_tree(g): return nx.is_tree(g)
def is_path(g):
    return nx.is_tree(g) and max(d for _, d in g.degree()) <= 2 if g.number_of_nodes() else False
for name, prop in [("f_induced_forest", is_forest), ("b_induced_bipartite", nx.is_bipartite),
                   ("tree_induced_tree", is_tree), ("path_induced_path", is_path)]:
    k, _ = max_induced(prop)
    P[name] = k
assert P["f_induced_forest"] == P["b_induced_bipartite"] == P["tree_induced_tree"] == 4
# largest induced cycle
best_cyc = 0
for k in (5, 6):
    for S in itertools.combinations(range(20), k):
        g = G.subgraph(S)
        if g.number_of_edges() == k and nx.is_connected(g) and all(d == 2 for _, d in g.degree()):
            best_cyc = max(best_cyc, k)
P["induced_circumference"] = best_cyc

# ---- edge neighborhoods ----
ne = [len((set(G[u]) | set(G[v])) - {u, v}) for u, v in G.edges()]
P["N_edge_min"] = min(ne); P["N_edge_max"] = max(ne)
nonedges = [(u, v) for u in G for v in G if u < v and not G.has_edge(u, v)]
nne = [len((set(G[u]) | set(G[v])) - {u, v}) for u, v in nonedges]
P["N_nonedge_in_G_min"] = min(nne); P["N_nonedge_in_G_max"] = max(nne)
cne = [len((set(comp[u]) | set(comp[v])) - {u, v}) for u, v in comp.edges()]
P["N_edge_in_complement_min"] = min(cne); P["N_edge_in_complement_max"] = max(cne)
P["neighbor_dominator_pairs_exist"] = True  # same-blob: N[u]=N[v]

# ---- complement profile (complement = C5-blowup with independent 4-blobs) ----
P["complement"] = {
    "regular_degree": 8, "m": 80,
    "connected": nx.is_connected(comp),
    "diameter": nx.diameter(comp),
    "radius": nx.radius(comp),
    "triangle_free": sum(nx.triangles(comp).values()) == 0,
    "girth": 4,
    "alpha": 8,   # = omega-ish: max independent in comp = max clique-ish... = blob-pair
    "note": "comp = C5[empty_4]: blobs independent, complete join between blobs 2 apart",
}
cc, _ = nx.max_weight_clique(comp, weight=None)  # = alpha(G) = 2
ci, _ = nx.max_weight_clique(G, weight=None)     # alpha(comp) = omega(G) = 8
P["complement"]["omega"] = len(cc); P["complement"]["alpha"] = len(ci)
cl = {}
for v in comp:
    Nv = comp.subgraph(list(comp[v]))
    c2, _ = nx.max_weight_clique(nx.complement(Nv), weight=None)
    cl[v] = len(c2)
P["complement"]["lambda_v"] = sorted(set(cl.values()))
cdist = dict(nx.all_pairs_shortest_path_length(comp))
cde = {v: sum(1 for u in comp if cdist[v][u] % 2 == 0) for v in comp}
P["complement"]["dist_even_v"] = sorted(set(cde.values()))
P["complement"]["Tdist_v"] = sorted(set(sum(cdist[v].values()) for v in comp))
P["complement"]["length"] = "sqrt(20*64) = sqrt(1280) ~= 35.777"

print(json.dumps(P, indent=1, default=str))
with open("data/profile.json", "w") as fh:
    json.dump(P, fh, indent=1, default=str)
