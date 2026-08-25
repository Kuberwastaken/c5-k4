#!/usr/bin/env python3
"""STEP 5 — F5: EVERY connected graph on 8 vertices, generated as connected
atlas-7 + one attached vertex, isomorphism-deduplicated, exhaustively scored
under 305/RDG-B. Aggregate cap 900s CPU (contract §6)."""
import sys, json, time
sys.path.insert(0, "/Users/kuber.mehta/Personal-Projects/c5-k4/results/expansion/open_sweep2_20260826/trial_305_308")
from fractions import Fraction
import networkx as nx
from trial_common import *

t0 = time.monotonic()
CAP = 900.0
g7s = [(g, tuple(g.nodes())) for g in atlas_connected(7, 7)]
buckets = {}
uniques = []
raw = 0
for G7, verts in g7s:
    if time.monotonic() - t0 > CAP * 0.55:
        break
    edges7 = set(G7.edges())
    for r in range(1, 8):
        for S in __import__("itertools").combinations(verts, r):
            raw += 1
            g = nx.Graph(edges7)
            g.add_node(8)
            g.add_edges_from((8, s) for s in S)
            h = __import__("networkx.algorithms.graph_hashing", fromlist=["x"]).weisfeiler_lehman_graph_hash(g)
            b = buckets.get(h)
            if b is None:
                buckets[h] = [g]
                uniques.append(g)
            else:
                dup = False
                for rep in b:
                    if nx.is_isomorphic(rep, g):
                        dup = True
                        break
                if not dup:
                    b.append(g)
                    uniques.append(g)

gen_time = time.monotonic() - t0
print(f"raw candidates {raw}; unique connected n=8 graphs: {len(uniques)} "
      f"(generation+dedupe {gen_time:.1f}s)")

violations = []
equalities = 0
na_count = 0
min_pos = None
cross_shape = []   # gamma_t>=4 & M<=5 population (the only possible crossing shape)
diam2_count = 0
eval_start = time.monotonic()
for i, g in enumerate(uniques):
    assert time.monotonic() - t0 < CAP, "F5 aggregate cap exhausted"
    gtA, _ = gamma_t_enum(g)
    vals = nbar_readings(g)["B"]
    R = residual_305(vals, gtA)
    if R is None:
        na_count += 1
        continue
    if R == 0:
        equalities += 1
    elif R < 0:
        violations.append((nx.to_graph6_bytes(g, header=False).decode().strip(),
                           str(R), max(vals), gtA))
    elif min_pos is None or R < min_pos:
        min_pos = R
    if gtA >= 4 and max(vals) <= 5:
        cross_shape.append((gtA, max(vals)))
    if i % 4000 == 0:
        print(f"  ...{i}/{len(uniques)} evaluated ({time.monotonic()-eval_start:.0f}s)")

out = {
    "raw_candidates": raw,
    "unique_connected_n8": len(uniques),
    "generation_seconds": round(gen_time, 1),
    "violations": violations,
    "n_not_applicable_complete": na_count,
    "n_equalities_R0": equalities,
    "min_positive_slack": str(min_pos) if min_pos is not None else None,
    "gamma_t_ge4_and_M_le5_population": len(cross_shape),
}
with open("/Users/kuber.mehta/Personal-Projects/c5-k4/results/expansion/open_sweep2_20260826/trial_305_308/f5_rows.json", "w") as f:
    json.dump(out, f, indent=1)
print(f"F5 COMPLETE: violations={len(violations)} equalities={equalities} "
      f"min_positive_slack={min_pos} gamma_t>=4&M<=5 pop={len(cross_shape)} "
      f"({time.monotonic()-t0:.1f}s total)")
