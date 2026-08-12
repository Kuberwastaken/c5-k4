#!/usr/bin/env python3
"""Independent exact checks for the stronger theorem behind WOWII 438b.

The proof report derives the result by partitioning matching edges.  This
verifier instead computes alpha and alpha_2 directly over vertex subsets and
checks the resulting inequality for every H on the Graph Atlas, plus the
source H_2 specialization on structured frozen-family controls.
"""

from __future__ import annotations

import itertools

import networkx as nx


def popcount(value: int) -> int:
    return bin(value).count("1")


def adjacency_masks(graph: nx.Graph) -> list[int]:
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    masks = [0] * graph.number_of_nodes()
    for u, v in graph.edges():
        masks[u] |= 1 << v
        masks[v] |= 1 << u
    return masks


def independent(mask: int, adjacency: list[int]) -> bool:
    remaining = mask
    while remaining:
        bit = remaining & -remaining
        vertex = bit.bit_length() - 1
        if adjacency[vertex] & mask:
            return False
        remaining ^= bit
    return True


def two_independent(mask: int, adjacency: list[int]) -> bool:
    remaining = mask
    while remaining:
        bit = remaining & -remaining
        vertex = bit.bit_length() - 1
        if popcount(adjacency[vertex] & mask) > 1:
            return False
        remaining ^= bit
    return True


def alpha_in(mask: int, adjacency: list[int]) -> int:
    best = 0
    subset = mask
    while True:
        size = popcount(subset)
        if size > best and independent(subset, adjacency):
            best = size
        if subset == 0:
            return best
        subset = (subset - 1) & mask


def alpha_two(adjacency: list[int]) -> int:
    best = 0
    for mask in range(1 << len(adjacency)):
        size = popcount(mask)
        if size > best and two_independent(mask, adjacency):
            best = size
    return best


def induced_edges(mask: int, adjacency: list[int]) -> int:
    return sum(popcount(adjacency[v] & mask) for v in range(len(adjacency)) if mask >> v & 1) // 2


def values(adjacency: list[int], h_mask: int, a2: int, a: int) -> tuple[int, int, int, int]:
    all_mask = (1 << len(adjacency)) - 1
    a_core = alpha_in(all_mask ^ h_mask, adjacency)
    e_h = induced_edges(h_mask, adjacency)
    return a2, a, a_core, e_h


def assert_inequality(
    graph: nx.Graph,
    h_mask: int,
    label: str,
    adjacency: list[int] | None = None,
    a2: int | None = None,
    a: int | None = None,
) -> None:
    adjacency = adjacency if adjacency is not None else adjacency_masks(graph)
    all_mask = (1 << len(adjacency)) - 1
    a2 = alpha_two(adjacency) if a2 is None else a2
    a = alpha_in(all_mask, adjacency) if a is None else a
    a2, a, a_core, e_h = values(adjacency, h_mask, a2, a)
    assert a2 <= a + a_core + e_h, (
        label,
        a2,
        a,
        a_core,
        e_h,
        nx.to_graph6_bytes(graph, header=False).decode().strip(),
    )


def h_two_mask(graph: nx.Graph) -> int:
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    return sum(1 << vertex for vertex, degree in graph.degree() if degree <= 2)


def named_controls() -> list[tuple[str, nx.Graph]]:
    controls: list[tuple[str, nx.Graph]] = []
    for n in range(5, 10):
        controls.append((f"C{n}", nx.cycle_graph(n)))
    controls.extend(
        [
            ("P7", nx.path_graph(7)),
            ("Petersen", nx.petersen_graph()),
            ("K3,3", nx.complete_bipartite_graph(3, 3)),
            ("K7", nx.complete_graph(7)),
            ("K1,7", nx.star_graph(7)),
        ]
    )
    return controls


def exact_twin_control_values(core_order: int, neighbor_count: int, layer_size: int) -> tuple[int, int, int, int]:
    """Enumerate core subsets and a twin-layer count; symmetry makes this exact."""
    best_a = 0
    best_a2 = 0
    for core_mask in range(1 << core_order):
        core_size = popcount(core_mask)
        for layer_count in range(layer_size + 1):
            total = core_size + layer_count
            core_independent = core_size <= 1
            layer_to_core_edges = layer_count * popcount(core_mask & ((1 << neighbor_count) - 1))
            if core_independent and layer_to_core_edges == 0:
                best_a = max(best_a, total)

            degrees: list[int] = []
            for vertex in range(core_order):
                if core_mask >> vertex & 1:
                    degree = core_size - 1
                    if vertex < neighbor_count:
                        degree += layer_count
                    degrees.append(degree)
            if layer_count:
                degrees.extend([popcount(core_mask & ((1 << neighbor_count) - 1))] * layer_count)
            if all(degree <= 1 for degree in degrees):
                best_a2 = max(best_a2, total)

    # H_2 is precisely the independent twin layer for core_order >= 4.
    return best_a2, best_a, 1, 0


def exact_cycle_blowup_values(cycle_order: int, weight: int) -> tuple[int, int, int, int]:
    """Enumerate selected counts per true-twin clique; symmetry makes this exact."""
    best_a = 0
    best_a2 = 0
    for counts in itertools.product(range(weight + 1), repeat=cycle_order):
        total = sum(counts)
        if all(counts[index] <= 1 for index in range(cycle_order)) and all(
            not (counts[index] and counts[(index + 1) % cycle_order]) for index in range(cycle_order)
        ):
            best_a = max(best_a, total)
        if all(
            counts[index] == 0
            or counts[(index - 1) % cycle_order] + counts[index] + counts[(index + 1) % cycle_order] <= 2
            for index in range(cycle_order)
        ):
            best_a2 = max(best_a2, total)

    # Every vertex has degree 3*weight-1, so H_2 is empty for weight >= 2.
    return best_a2, best_a, best_a, 0


def main() -> None:
    atlas_graphs = nx.graph_atlas_g()
    arbitrary_h_checks = 0
    source_checks = 0
    for index, graph in enumerate(atlas_graphs):
        graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
        adjacency = adjacency_masks(graph)
        all_mask = (1 << graph.number_of_nodes()) - 1
        a2 = alpha_two(adjacency)
        a = alpha_in(all_mask, adjacency)
        for h_mask in range(1 << graph.number_of_nodes()):
            assert_inequality(graph, h_mask, f"atlas#{index},H={h_mask}", adjacency, a2, a)
            arbitrary_h_checks += 1
        if graph.number_of_nodes() > 3 and nx.is_connected(graph):
            assert_inequality(graph, h_two_mask(graph), f"atlas-source#{index}", adjacency, a2, a)
            source_checks += 1

    named = named_controls()
    for label, graph in named:
        assert nx.is_connected(graph), label
        assert graph.number_of_nodes() > 3, label
        assert_inequality(graph, h_two_mask(graph), label)

    structured_checks = 0
    for core_order in range(4, 9):
        for neighbor_count in (1, 2):
            for layer_size in (1, 2, 4, 8, 16, 24):
                if core_order + layer_size > 48:
                    continue
                a2, a, a_core, e_h = exact_twin_control_values(core_order, neighbor_count, layer_size)
                assert a2 <= a + a_core + e_h, (
                    "false-twin",
                    core_order,
                    neighbor_count,
                    layer_size,
                    a2,
                    a,
                    a_core,
                    e_h,
                )
                structured_checks += 1
    for cycle_order, weight in ((5, 2), (5, 3), (5, 4), (7, 2), (7, 3), (9, 3)):
        a2, a, a_core, e_h = exact_cycle_blowup_values(cycle_order, weight)
        assert a2 <= a + a_core + e_h, (
            "cycle-blowup",
            cycle_order,
            weight,
            a2,
            a,
            a_core,
            e_h,
        )
        structured_checks += 1

    print(f"PASS arbitrary-H atlas checks: {arbitrary_h_checks}")
    print(f"PASS source H_2 atlas checks: {source_checks}")
    print(f"PASS named H_2 checks: {len(named)}")
    print(f"PASS structured compressed-exact H_2 checks: {structured_checks}")
    print("PASS WOWII 438b stronger arbitrary-subset theorem")


if __name__ == "__main__":
    main()
