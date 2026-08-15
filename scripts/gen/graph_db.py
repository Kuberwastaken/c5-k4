"""Build the frozen verification database `D` for the fresh-population generator.

`D` = every connected graph on `2 <= n <= 8` vertices, up to isomorphism.

  n=2..7  come from `networkx.graph_atlas_g()` (the Read--Wilson atlas, complete
          through n=7).
  n=8     is generated here by one-vertex extension of *all* 1044 graphs on 7
          vertices (every 8-vertex graph has a 7-vertex vertex-deleted subgraph,
          so this is exhaustive), followed by exact isomorphism rejection.

Isomorphism rejection uses a cheap invariant certificate as a bucket key and
`networkx.is_isomorphic` (VF2, exact) inside each bucket, so correctness does not
depend on the strength of the certificate.

`K_1` is excluded: almost every invariant in the vocabulary is degenerate or
undefined on it (no edges, no neighbourhoods, deg_avg = 0), and Graffiti-lineage
databases do not contain it.  The emitted statements are therefore quantified
over connected graphs with `n >= 2`.

Deterministic: no randomness anywhere; output is the sorted list of graph6
strings.

Usage:
    python3 scripts/gen/graph_db.py          # build + cache + print counts
"""
from __future__ import annotations

import os
import sys
from typing import Dict, List, Tuple

import networkx as nx

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(HERE, "data")
DB_PATH = os.path.join(CACHE_DIR, "connected_n2_n8.g6")

MAX_N = 8


def g6(G: nx.Graph) -> str:
    """graph6 string with vertices relabelled 0..n-1 in sorted order."""
    H = nx.convert_node_labels_to_integers(G, ordering="sorted")
    return nx.to_graph6_bytes(H, header=False).decode().strip()


def from_g6(s: str) -> nx.Graph:
    return nx.from_graph6_bytes(s.encode())


def _certificate(G: nx.Graph) -> Tuple:
    """Cheap isomorphism-invariant bucket key (exactness comes from VF2 later)."""
    deg = {v: G.degree(v) for v in G}
    tri = tuple(sorted(nx.triangles(G).values()))
    nbr = tuple(sorted((deg[v], tuple(sorted(deg[u] for u in G[v]))) for v in G))
    return (G.number_of_nodes(), G.number_of_edges(), tuple(sorted(deg.values())), tri, nbr)


def connected_upto7() -> List[nx.Graph]:
    """All connected graphs on 2..7 vertices, from the networkx atlas."""
    out = []
    for G in nx.graph_atlas_g():
        if G.number_of_nodes() >= 2 and nx.is_connected(G):
            out.append(G)
    return out


def connected_n8() -> List[nx.Graph]:
    """All connected graphs on exactly 8 vertices, by exhaustive extension."""
    seven = [G for G in nx.graph_atlas_g() if G.number_of_nodes() == 7]
    assert len(seven) == 1044, len(seven)
    buckets: Dict[Tuple, List[nx.Graph]] = {}
    for G in seven:
        nodes = sorted(G.nodes())
        for mask in range(1, 1 << 7):          # mask == 0 => vertex 7 isolated
            H = G.copy()
            H.add_node(7)
            for i in range(7):
                if mask >> i & 1:
                    H.add_edge(7, nodes[i])
            if not nx.is_connected(H):
                continue
            key = _certificate(H)
            bucket = buckets.setdefault(key, [])
            if not any(nx.is_isomorphic(H, X) for X in bucket):
                bucket.append(H)
    return [H for bucket in buckets.values() for H in bucket]


def build(max_n: int = MAX_N) -> List[str]:
    graphs = connected_upto7()
    if max_n >= 8:
        graphs = graphs + connected_n8()
    codes = sorted({g6(G) for G in graphs})
    return codes


def load(max_n: int = MAX_N, rebuild: bool = False) -> List[nx.Graph]:
    """Return `D` as a list of nx.Graph, in a fixed deterministic order.

    Order = graph6 strings sorted by (n, graph6 string).  Cached on disk.
    """
    if rebuild or not os.path.exists(DB_PATH):
        os.makedirs(CACHE_DIR, exist_ok=True)
        codes = build(max_n)
        with open(DB_PATH, "w") as fh:
            fh.write("\n".join(codes) + "\n")
    with open(DB_PATH) as fh:
        codes = [ln.strip() for ln in fh if ln.strip()]
    graphs = [from_g6(c) for c in codes]
    order = sorted(range(len(graphs)), key=lambda i: (graphs[i].number_of_nodes(), codes[i]))
    return [graphs[i] for i in order]


# Known exact counts of connected graphs on n vertices (OEIS A001349) --- used as
# a build-time self-check, not as a source of graphs.
EXPECTED = {2: 1, 3: 2, 4: 6, 5: 21, 6: 112, 7: 853, 8: 11117}


def main() -> int:
    rebuild = "--rebuild" in sys.argv
    D = load(rebuild=rebuild)
    by_n: Dict[int, int] = {}
    for G in D:
        by_n[G.number_of_nodes()] = by_n.get(G.number_of_nodes(), 0) + 1
    for n in sorted(by_n):
        ok = "ok" if by_n[n] == EXPECTED.get(n) else "MISMATCH expected %s" % EXPECTED.get(n)
        print("n=%d  %6d  %s" % (n, by_n[n], ok))
    print("|D| = %d" % len(D))
    assert all(by_n[n] == EXPECTED[n] for n in by_n), "database count self-check failed"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
