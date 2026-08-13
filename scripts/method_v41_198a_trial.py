#!/usr/bin/env python3
"""Frozen bounded prospective trial for WOWII 198a. Prints JSON only."""

import itertools
import json
import networkx as nx


def traceable_dp(G):
    n = len(G)
    adj = [sum(1 << j for j in G.neighbors(i)) for i in range(n)]
    dp = [0] * (1 << n)
    for i in range(n):
        dp[1 << i] = 1 << i
    for mask in range(1, 1 << n):
        ends = dp[mask]
        while ends:
            bit = ends & -ends
            ends -= bit
            v = bit.bit_length() - 1
            nxt = adj[v] & ~mask
            while nxt:
                wbit = nxt & -nxt
                nxt -= wbit
                dp[mask | wbit] |= wbit
    return dp[-1] != 0


def bipartite_mask(G, mask):
    color = {}
    for s in range(len(G)):
        if not (mask >> s) & 1 or s in color:
            continue
        color[s] = 0
        stack = [s]
        while stack:
            u = stack.pop()
            for v in G.neighbors(u):
                if not (mask >> v) & 1:
                    continue
                if v not in color:
                    color[v] = color[u] ^ 1
                    stack.append(v)
                elif color[v] == color[u]:
                    return False
    return True


def exact_b(G):
    n = len(G)
    full = (1 << n) - 1
    for deleted in range(n + 1):
        for cut in itertools.combinations(range(n), deleted):
            mask = full
            for v in cut:
                mask ^= 1 << v
            if bipartite_mask(G, mask):
                return n - deleted
    raise AssertionError


def profile(G):
    G = nx.convert_node_labels_to_integers(G)
    n = len(G)
    connected = nx.is_connected(G)
    if not connected:
        return {"n": n, "connected": False}
    tr = traceable_dp(G)
    ecc = nx.eccentricity(G)
    se = sum(ecc.values())
    b = exact_b(G)
    return {"n": n, "m": G.number_of_edges(), "connected": True,
            "traceable": tr, "b": b, "sum_ecc": se,
            "cross_lhs": b * n, "cross_rhs": 2 * n + se,
            "crosses_hypothesis": b * n <= 2 * n + se,
            "graph6": nx.to_graph6_bytes(G, header=False).decode().strip()}


def blowup(base, sizes, kinds):
    G = nx.Graph()
    blobs = []
    for s, clique in zip(sizes, kinds):
        blob = list(range(len(G), len(G) + s))
        G.add_nodes_from(blob)
        if clique:
            G.add_edges_from(itertools.combinations(blob, 2))
        blobs.append(blob)
    for u, v in base.edges():
        G.add_edges_from(itertools.product(blobs[u], blobs[v]))
    return G


def frozen_candidates():
    seen = set()
    produced = 0
    bases = []
    for k in range(3, 8):
        bases += [(f"P{k}", nx.path_graph(k)), (f"C{k}", nx.cycle_graph(k))]
    bases += [("claw", nx.star_graph(3)),
              ("bowtie", nx.from_edgelist([(0,1),(1,2),(2,0),(0,3),(3,4),(4,0)]))]
    for name, base in bases:
        k = len(base)
        patterns = [(s,) * k for s in range(1, 5)]
        patterns += [tuple(1 + ((j + phase) % 4) for j in range(k)) for phase in range(4)]
        kind_patterns = [(False,) * k, (True,) * k,
                         tuple(j % 2 == 0 for j in range(k)),
                         tuple(j % 2 == 1 for j in range(k))]
        for sizes in patterns:
            if sum(sizes) > 18:
                continue
            for kinds in kind_patterns:
                G = blowup(base, sizes, kinds)
                key = nx.weisfeiler_lehman_graph_hash(G)
                if key not in seen:
                    seen.add(key); produced += 1
                    yield f"blowup:{name}:{sizes}:{kinds}", G
    # Sparse cut joins: clique sides, bridge/path handles, and shared cut.
    for left in range(2, 8):
        for right in range(2, 8):
            for handle in (1, 2, 3):
                n = left + right + handle - 1
                if n > 18: continue
                G = nx.disjoint_union(nx.complete_graph(left), nx.complete_graph(right))
                a, b = 0, left
                prev = a
                for _ in range(handle - 1):
                    w = len(G); G.add_node(w); G.add_edge(prev, w); prev = w
                G.add_edge(prev, b)
                key = nx.weisfeiler_lehman_graph_hash(G)
                if key not in seen:
                    seen.add(key); produced += 1
                    yield f"sparse_clique_join:{left}:{right}:{handle}", G
            # shared cut vertex (two cliques sharing vertex 0)
            G = nx.Graph(); G.add_nodes_from(range(left + right - 1))
            G.add_edges_from(itertools.combinations(range(left), 2))
            G.add_edges_from(itertools.combinations([0] + list(range(left, left + right - 1)), 2))
            key = nx.weisfeiler_lehman_graph_hash(G)
            if key not in seen:
                seen.add(key); produced += 1
                yield f"shared_cut_cliques:{left}:{right}", G


def main():
    controls = {
        "P5": nx.path_graph(5), "C5": nx.cycle_graph(5),
        "K1,3": nx.star_graph(3), "K3,3": nx.complete_bipartite_graph(3,3),
        "C5[K4]": blowup(nx.cycle_graph(5), (4,)*5, (True,)*5),
    }
    print(json.dumps({"event":"sanity_controls", "profiles":
        {k: profile(v) for k,v in controls.items()}}, sort_keys=True))
    generated = exact = 0
    best = []
    crossings = []
    for name, G in frozen_candidates():
        generated += 1
        if generated > 20000: break
        if not nx.is_connected(G) or traceable_dp(nx.convert_node_labels_to_integers(G)):
            continue
        exact += 1
        if exact > 2000: break
        pr = profile(G); pr["family"] = name
        best.append(pr)
        best.sort(key=lambda x: (x["cross_rhs"]-x["cross_lhs"], -x["n"]), reverse=True)
        best = best[:10]
        if pr["crosses_hypothesis"]:
            crossings.append(pr)
    print(json.dumps({"event":"trial_result", "generated":generated,
        "nontraceable_exact":exact, "crossings":crossings, "best":best}, sort_keys=True))


if __name__ == "__main__":
    main()
