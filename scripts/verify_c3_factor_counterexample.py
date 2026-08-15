"""Independent verification that the C3/C3 analogue of the C4-factor theorem fails.

Builds X (cubic, bipartite, 20 vertices: three K(3,3)-e gadgets joined through
two hubs), checks X has no dominating cycle, then checks L(X) directly:
30 vertices, 4-regular, edges decomposing into two edge-disjoint triangle
factors, and non-Hamiltonian by exhaustive search with pruning.

Written independently of the report that first claimed this witness.
"""
import itertools
import sys

import networkx as nx


def build_X():
    X = nx.Graph()
    # three copies of K(3,3) minus the edge a1-b1
    for g in range(3):
        a = [(g, "a", i) for i in range(3)]
        b = [(g, "b", i) for i in range(3)]
        for u in a:
            for v in b:
                if u[2] == 0 and v[2] == 0:
                    continue  # the deleted edge a1-b1
                X.add_edge(u, v)
    # hubs: u to every a1, w to every b1
    for g in range(3):
        X.add_edge("u", (g, "a", 0))
        X.add_edge("w", (g, "b", 0))
    return X


def has_dominating_cycle(G):
    """True iff some cycle C dominates every edge (each edge has an end on C)."""
    nodes = list(G.nodes())
    n = len(nodes)
    # enumerate cycles via simple_cycles on the graph (n=20, cubic: feasible)
    for cyc in nx.simple_cycles(G):
        if len(cyc) < 3:
            continue
        S = set(cyc)
        if all((u in S) or (v in S) for u, v in G.edges()):
            return True, cyc
    return False, None


def triangle_factors(L, X):
    """The two triangle factors of L(X) for X cubic bipartite: vertex-triangles
    of X's two bipartition classes."""
    part = nx.bipartite.sets(X)
    factors = []
    for side in part:
        edges = []
        for v in side:
            inc = [frozenset(e) for e in L.nodes() if v in e]
            assert len(inc) == 3, f"degree {len(inc)} at {v}"
            for e, f in itertools.combinations(inc, 2):
                edges.append((tuple(sorted(e, key=str)), tuple(sorted(f, key=str))))
        factors.append(edges)
    return factors


def is_hamiltonian(G, cap_nodes=50_000_000):
    """Exhaustive DFS with degree pruning; returns (verdict, nodes_explored)."""
    nodes = sorted(G.nodes(), key=str)
    start = nodes[0]
    n = len(nodes)
    adj = {v: sorted(G[v], key=str) for v in nodes}
    visited = {start}
    path = [start]
    explored = 0

    def connected_rest(cur):
        # remaining graph (unvisited + cur) must be connected
        rest = [v for v in nodes if v not in visited] + [cur]
        if len(rest) <= 1:
            return True
        sub = G.subgraph(rest)
        return nx.is_connected(sub)

    def dfs(cur):
        nonlocal explored
        explored += 1
        if explored > cap_nodes:
            raise TimeoutError("search cap exceeded")
        if len(path) == n:
            return start in adj[cur]
        if not connected_rest(cur):
            return False
        for nxt in adj[cur]:
            if nxt in visited:
                continue
            visited.add(nxt)
            path.append(nxt)
            if dfs(nxt):
                return True
            path.pop()
            visited.remove(nxt)
        return False

    sys.setrecursionlimit(10000)
    return dfs(start), explored


X = build_X()
print(f"X: n={X.number_of_nodes()} m={X.number_of_edges()} "
      f"cubic={all(d == 3 for _, d in X.degree())} "
      f"bipartite={nx.is_bipartite(X)} connected={nx.is_connected(X)}")

dom, cyc = has_dominating_cycle(X)
print(f"X has a dominating cycle: {dom}")

L = nx.line_graph(X)
L = nx.relabel_nodes(L, {e: frozenset(e) for e in L.nodes()})
print(f"L(X): n={L.number_of_nodes()} m={L.number_of_edges()} "
      f"4-regular={all(d == 4 for _, d in L.degree())} connected={nx.is_connected(L)}")

f0, f1 = triangle_factors(L, X)
F0 = nx.Graph(f0)
F1 = nx.Graph(f1)
print(f"factor 0: {F0.number_of_edges()} edges, all-degree-2={all(d == 2 for _, d in F0.degree())}, "
      f"components={nx.number_connected_components(F0)} (all triangles="
      f"{all(len(c) == 3 for c in nx.connected_components(F0))})")
print(f"factor 1: {F1.number_of_edges()} edges, all-degree-2={all(d == 2 for _, d in F1.degree())}, "
      f"components={nx.number_connected_components(F1)} (all triangles="
      f"{all(len(c) == 3 for c in nx.connected_components(F1))})")
# normalise both sides to frozenset-of-frozensets before comparing; L's nodes are
# frozensets while the factor edges were built from tuples, and comparing the two
# label types directly reports a spurious mismatch.
def norm(edges):
    return {frozenset((frozenset(a), frozenset(b))) for a, b in edges}


shared = norm(F0.edges()) & norm(F1.edges())
union_ok = (norm(F0.edges()) | norm(F1.edges())) == norm(L.edges())
print(f"factors edge-disjoint: {len(shared) == 0}; union == L(X): {union_ok}")

ham, explored = is_hamiltonian(L)
print(f"L(X) Hamiltonian: {ham}  (DFS nodes explored: {explored})")
