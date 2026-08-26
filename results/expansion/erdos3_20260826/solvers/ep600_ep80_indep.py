#!/usr/bin/env python
"""EP600/EP80 implementation 2: networkx-based full enumeration, independent book-count
path (nx.triangles per common-neighbor via nx.common_neighbors). Cross-checks impl 1."""
import itertools, sys
from fractions import Fraction
import networkx as nx

def analyze(G):
    ne = G.number_of_edges()
    if ne == 0:
        return ne, 0, 0
    mb, mb1 = 0, ne
    for u, v in G.edges():
        b = sum(1 for _ in nx.common_neighbors(G, u, v))
        mb = max(mb, b)
        mb1 = min(mb1, b)
    return ne, mb, mb1

def run(ns, cs):
    eres, fres = {}, {}
    for n in ns:
        bad, adm = {}, {}
        edges = list(itertools.combinations(range(n), 2))
        for bits in range(1 << len(edges)):
            G = nx.Graph()
            G.add_nodes_from(range(n))
            for i, e in enumerate(edges):
                if bits >> i & 1:
                    G.add_edge(*e)
            ne, mb, mb1 = analyze(G)
            if mb1 >= 1 or ne == 0:
                for r in (2, 3, 4, 5):
                    if mb < r:
                        bad[r] = max(bad.get(r, -1), ne)
                for c in cs:
                    if Fraction(str(c)) * n * n <= ne:
                        adm[c] = min(adm.get(c, 10**9), mb)
        for r in (2, 3, 4, 5):
            eres[(n, r)] = bad.get(r, -1) + 1
        for c in cs:
            fres[(n, c)] = adm.get(c, 0)
    return eres, fres

if __name__ == "__main__":
    ns = [int(x) for x in sys.argv[1].split(",")]
    cs = [float(x) for x in sys.argv[2].split(",")]
    eres, fres = run(ns, cs)
    for n in ns:
        print(f"n={n}: " + " ".join(f"e({r})={eres[(n,r)]}" for r in (2,3,4,5))
              + " | " + " ".join(f"f_{c}={fres[(n,c)]}" for c in cs))
