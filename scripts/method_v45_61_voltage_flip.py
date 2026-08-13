#!/usr/bin/env python3
"""Exact frozen canonical 2-lift voltage-flip trial for WOWII 61."""

import argparse
import itertools
import json
import math
from collections import Counter

import networkx as nx


BASE_G6 = "G?aN]w"


def hh_trajectory(degrees):
    seq = sorted(map(int, degrees), reverse=True); states = [seq.copy()]
    while seq and seq[0] > 0:
        d = seq.pop(0)
        if d > len(seq): raise ValueError("nongraphical")
        for i in range(d):
            seq[i] -= 1
            if seq[i] < 0: raise ValueError("nongraphical")
        seq.sort(reverse=True); states.append(seq.copy())
    return states


def induced_is_forest(n, edges, mask):
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for u, v in edges:
        if (mask >> u) & 1 and (mask >> v) & 1:
            a, b = find(u), find(v)
            if a == b: return False
            parent[a] = b
    return True


def largest_forest(G):
    n = len(G); edges = list(G.edges()); checked = 0
    for k in range(n, -1, -1):
        for S in itertools.combinations(range(n), k):
            mask = sum(1 << v for v in S); checked += 1
            if induced_is_forest(n, edges, mask):
                return k, list(S), checked
    raise AssertionError


def diameter_witness(G):
    best = (-1, None, None, None)
    for s in G:
        paths = nx.single_source_shortest_path(G, s)
        for t, p in paths.items():
            if len(p)-1 > best[0]: best = (len(p)-1, s, t, p)
    return best


def profile(G, assignment=None):
    G = nx.convert_node_labels_to_integers(G, ordering="sorted")
    deg = sorted((d for _, d in G.degree()), reverse=True)
    traj = hh_trajectory(deg); residue = len(traj[-1])
    forest, witness, checked = largest_forest(G)
    diameter, u, v, path = diameter_witness(G)
    ceil = math.ceil(diameter / 3)
    return {"assignment": assignment, "graph6": nx.to_graph6_bytes(G, header=False).decode().strip(),
            "n": len(G), "m": G.number_of_edges(), "degree_sequence": deg,
            "hh_trajectory": traj, "residue": residue, "diameter": diameter,
            "diameter_endpoints": [u,v], "diameter_path": path,
            "ceil_diameter_over_3": ceil, "forest": forest,
            "forest_witness": witness, "larger_subsets_checked": checked-1,
            "residual": forest-residue-ceil,
            "edges": [list(e) for e in sorted(G.edges())]}


def gauge_data(base):
    tree = {tuple(sorted(e)) for e in nx.bfs_edges(base, source=0)}
    edges = sorted(tuple(sorted(e)) for e in base.edges())
    cotree = [e for e in edges if e not in tree]
    assert len(tree) == 7 and len(cotree) == 6
    return sorted(tree), cotree


def lift(base, mask, tree, cotree):
    voltage = {e: 0 for e in tree}
    voltage.update({e: (mask >> i) & 1 for i,e in enumerate(cotree)})
    H = nx.Graph(); H.add_nodes_from(range(2*len(base)))
    for (u,v), z in voltage.items():
        for s in (0,1): H.add_edge(2*u+s, 2*v+(s^z))
    return H


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("mode",choices=("base","lifts")); a=ap.parse_args()
    base=nx.from_graph6_bytes(BASE_G6.encode()); base=nx.convert_node_labels_to_integers(base)
    tree,cotree=gauge_data(base)
    if a.mode == "base":
        print(json.dumps({"event":"BASE_RECHECK","tree_edges":tree,"cotree_edges":cotree,
                          "cycle_rank":len(cotree),"profile":profile(base)},sort_keys=True)); return
    rows={}
    disconnected=[]
    for mask in range(64):
        H=lift(base,mask,tree,cotree)
        if not nx.is_connected(H): disconnected.append(mask); continue
        rows[mask]=profile(H,mask)
    flips=[]; crossing_pairs=[]
    for mask,src in rows.items():
        if src["residual"] != 0: continue
        for bit in range(6):
            target_mask=mask^(1<<bit)
            if target_mask not in rows: continue
            dst=rows[target_mask]
            rec={"source":mask,"target":target_mask,"bit":bit,
                 "source_ceil":src["ceil_diameter_over_3"],"target_ceil":dst["ceil_diameter_over_3"],
                 "source_forest":src["forest"],"target_forest":dst["forest"],
                 "source_residue":src["residue"],"target_residue":dst["residue"],
                 "target_residual":dst["residual"]}
            if dst["ceil_diameter_over_3"] > src["ceil_diameter_over_3"]:
                flips.append(rec)
                if dst["forest"] <= src["forest"] and dst["residual"] < 0:
                    crossing_pairs.append(rec)
    best=sorted(rows.values(),key=lambda r:(r["residual"],-r["diameter"],r["forest"],r["assignment"]))[:8]
    print(json.dumps({"event":"LIFT_CLASS_RESULT","tree_edges":tree,"cotree_edges":cotree,
        "assignments":64,"connected":len(rows),"disconnected":disconnected,
        "common_degree_sequences":len({tuple(r['degree_sequence']) for r in rows.values()}),
        "common_residues":sorted({r['residue'] for r in rows.values()}),
        "residual_histogram":dict(sorted(Counter(r['residual'] for r in rows.values()).items())),
        "diameter_histogram":dict(sorted(Counter(r['diameter'] for r in rows.values()).items())),
        "forest_histogram":dict(sorted(Counter(r['forest'] for r in rows.values()).items())),
        "tight_assignments":[m for m,r in rows.items() if r['residual']==0],
        "ceil_raising_flips_from_tight":flips,"crossing_pairs":crossing_pairs,
        "best":best,"rows":list(rows.values())},sort_keys=True))


if __name__ == "__main__": main()
