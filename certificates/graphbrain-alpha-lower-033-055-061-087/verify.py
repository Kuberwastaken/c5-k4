#!/usr/bin/env python3
import math
import networkx as nx

EPS = 1e-6


def blowup(cycle_order, clique_order):
    return nx.lexicographic_product(
        nx.cycle_graph(cycle_order), nx.complete_graph(clique_order)
    )


def independence_number(g):
    return max(map(len, nx.find_cliques(nx.complement(g))))


def matching_number(g):
    return len(nx.max_weight_matching(g, maxcardinality=True))


def min_common_neighbors(g):
    return min(
        len(set(g[u]).intersection(g[v]))
        for u in g for v in g if u < v
    )


def szekeres_wilf(g):
    return max(nx.core_number(g).values()) + 1


def rhs(g, entry):
    degrees = dict(g.degree())
    if entry == 33:
        return -nx.girth(g) + min(
            min(degrees.values()), math.tan(nx.average_shortest_path_length(g))
        )
    if entry == 55:
        return min(nx.radius(g) ** 2, min_common_neighbors(g) / 2)
    if entry == 61:
        return min(
            szekeres_wilf(g),
            -(2 * g.number_of_edges() / len(g)) + matching_number(g),
        )
    if entry == 87:
        return min(
            2 * nx.girth(g), matching_number(g) - max(degrees.values())
        )
    raise ValueError(entry)


def named_gate():
    graphs = [nx.cycle_graph(n) for n in range(5, 10)]
    graphs += [nx.path_graph(7), nx.petersen_graph(), nx.complete_graph(7)]
    graphs += [nx.complete_bipartite_graph(3, 3)]
    graphs += [nx.star_graph(n) for n in range(3, 12)]
    graphs += [nx.complete_bipartite_graph(a, b) for a in range(2, 7) for b in range(2, 7)]
    return graphs


def verify_gate():
    atlas = [g for g in nx.graph_atlas_g() if len(g) > 1 and nx.is_connected(g)]
    assert len(atlas) == 995
    for entry in (33, 55, 61, 87):
        for g in atlas + named_gate():
            assert independence_number(g) + EPS >= rhs(g, entry)
    return len(atlas), len(named_gate())


def verify_witnesses():
    c5k3, c5k5, c9k3 = blowup(5, 3), blowup(5, 5), blowup(9, 3)
    assert independence_number(c5k3) == 2 == 5 // 2
    assert independence_number(c5k5) == 2 == 5 // 2
    assert independence_number(c9k3) == 4 == 9 // 2
    assert nx.average_shortest_path_length(c5k3) == 10 / 7
    assert min_common_neighbors(c5k5) == 5
    assert matching_number(c9k3) == 13 == len(c9k3) // 2
    assert max(dict(c9k3.degree()).values()) == 8
    assert szekeres_wilf(c9k3) == 9
    results = {
        33: (2, rhs(c5k3, 33)),
        55: (2, rhs(c5k5, 55)),
        61: (4, rhs(c9k3, 61)),
        87: (4, rhs(c9k3, 87)),
    }
    for alpha, bound in results.values():
        assert alpha + EPS < bound
    return results


if __name__ == "__main__":
    count, named = verify_gate()
    results = verify_witnesses()
    print(f"PASS: {count} connected Atlas graphs and {named} named controls")
    for entry, (alpha, bound) in results.items():
        print(f"lower-{entry:03d}: alpha={alpha} < rhs={bound:.12g}")

