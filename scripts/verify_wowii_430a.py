#!/usr/bin/env python3
"""Exact verifier for the P7 clique-blowup disproof of WOWII 430a."""

from fractions import Fraction
from itertools import combinations
import networkx as nx


SIZES = (1, 4, 12, 19, 12, 4, 1)


def path_clique_blowup(sizes: tuple[int, ...]) -> nx.Graph:
    graph = nx.Graph()
    blobs = []
    start = 0
    for size in sizes:
        blob = tuple(range(start, start + size)); start += size; blobs.append(blob)
        graph.add_edges_from(combinations(blob, 2))
    for left, right in zip(blobs, blobs[1:]):
        graph.add_edges_from((u, v) for u in left for v in right)
    return graph


def independent_domination_number(graph: nx.Graph) -> int:
    # Maximal independent sets of G are maximal cliques of its complement.
    return min(map(len, nx.find_cliques(nx.complement(graph))))


def independence_number(graph: nx.Graph) -> int:
    return max(map(len, nx.find_cliques(nx.complement(graph)))) if graph else 0


def harmonic_caro_wei(graph: nx.Graph) -> Fraction:
    return sum((Fraction(1, graph.degree(v) + 1) for v in graph), Fraction())


def neighborhood(graph: nx.Graph, vertices: set[int], closed: bool = False) -> set[int]:
    result = {u for v in vertices for u in graph.neighbors(v)}
    # DeLaViña's N(S) is the union of the open vertex-neighborhoods.  It may
    # intersect S when G[S] has edges; it is not the external boundary N(S)-S.
    return result | vertices if closed else result


def holds(graph: nx.Graph, closed: bool = False) -> bool:
    eccentricities = nx.eccentricity(graph)
    radius = min(eccentricities.values())
    center = {v for v, eccentricity in eccentricities.items() if eccentricity == radius}
    alpha = independence_number(graph.subgraph(neighborhood(graph, center, closed)))
    rhs = alpha + 2 * ((harmonic_caro_wei(graph) - 1).numerator //
                       (harmonic_caro_wei(graph) - 1).denominator)
    return independent_domination_number(graph) <= rhs


def main() -> None:
    atlas = [g for g in nx.graph_atlas_g() if 4 <= len(g) <= 7 and nx.is_connected(g)]
    assert all(holds(g) and holds(g, closed=True) for g in atlas)
    named = [(f"C{n}", nx.cycle_graph(n)) for n in range(5, 10)]
    named += [("P7", nx.path_graph(7)), ("Petersen", nx.petersen_graph()),
              ("K3,3", nx.complete_bipartite_graph(3, 3)),
              ("K7", nx.complete_graph(7))]
    named += [(f"K1,{n}", nx.star_graph(n)) for n in range(2, 8)]
    named += [(f"K{a},{b}", nx.complete_bipartite_graph(a, b))
              for a in range(2, 5) for b in range(a, 6)]
    assert all(holds(g) and holds(g, closed=True) for _, g in named)

    graph = path_clique_blowup(SIZES)
    eccentricities = nx.eccentricity(graph)
    center = {v for v, e in eccentricities.items() if e == min(eccentricities.values())}
    open_neighborhood = neighborhood(graph, center)
    closed_neighborhood = neighborhood(graph, center, closed=True)
    caro_wei = harmonic_caro_wei(graph)
    assert (len(graph), graph.number_of_edges()) == (53, 875)
    assert caro_wei == Fraction(51123, 25585) < 2
    assert independent_domination_number(graph) == 3
    assert independence_number(graph.subgraph(open_neighborhood)) == 2
    assert independence_number(graph.subgraph(closed_neighborhood)) == 2
    assert not holds(graph) and not holds(graph, closed=True)

    for scale in range(1, 5):
        scaled = path_clique_blowup(tuple(scale * size for size in SIZES))
        assert harmonic_caro_wei(scaled) == caro_wei
        assert independent_domination_number(scaled) == 3
        ecc = nx.eccentricity(scaled); c = {v for v, e in ecc.items() if e == min(ecc.values())}
        assert independence_number(scaled.subgraph(neighborhood(scaled, c))) == 2

    print(f"atlas gate: {len(atlas)} connected graphs on 4..7 vertices, open/closed N(C) hold")
    print(f"named gate: {len(named)} controls, open/closed N(C) hold")
    print("P7[K_(1,4,12,19,12,4,1)]: n=53, m=875")
    print(f"i=3 > 2=alpha(G[N(C)])+2 floor(CW-1); CW={caro_wei}")
    print("uniform scaling t=1..4 preserves CW and the violating quotient invariants")


if __name__ == "__main__":
    main()
