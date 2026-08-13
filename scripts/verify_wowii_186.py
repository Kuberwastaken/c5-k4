#!/usr/bin/env python3
"""Independent exact audit of the apparent WOWII 186 co-Petersen crossing."""

from __future__ import annotations

import itertools
import json
import time

import networkx as nx


def subsets(vertices, size):
    return itertools.combinations(tuple(vertices), size)


def square_graph(graph: nx.Graph) -> nx.Graph:
    square = nx.Graph()
    square.add_nodes_from(graph.nodes)
    distances = dict(nx.all_pairs_shortest_path_length(graph, cutoff=2))
    for u, v in itertools.combinations(graph.nodes, 2):
        if distances[u].get(v, 3) <= 2:
            square.add_edge(u, v)
    return square


def maximum_induced_bipartite_order(graph: nx.Graph) -> tuple[int, tuple[int, ...]]:
    vertices = tuple(graph.nodes)
    for size in range(len(vertices), -1, -1):
        for chosen in subsets(vertices, size):
            if nx.is_bipartite(graph.subgraph(chosen)):
                return size, tuple(chosen)
    raise AssertionError("empty induced subgraph must be bipartite")


def connected_domination_number(graph: nx.Graph) -> tuple[int, tuple[int, ...]]:
    vertices = tuple(graph.nodes)
    for size in range(1, len(vertices) + 1):
        for chosen in subsets(vertices, size):
            chosen_set = set(chosen)
            if size > 1 and not nx.is_connected(graph.subgraph(chosen)):
                continue
            dominated = chosen_set | set().union(*(set(graph.neighbors(v)) for v in chosen))
            if dominated == set(vertices):
                return size, tuple(chosen)
    raise AssertionError("the full vertex set is connected and dominating")


def center(graph: nx.Graph) -> frozenset[int]:
    eccentricities = nx.eccentricity(graph)
    radius = min(eccentricities.values())
    return frozenset(v for v, value in eccentricities.items() if value == radius)


def neighborhood(graph: nx.Graph, chosen: frozenset[int], external_only: bool) -> frozenset[int]:
    result = frozenset().union(*(frozenset(graph.neighbors(v)) for v in chosen))
    return result - chosen if external_only else result


def set_eccentricity(graph: nx.Graph, chosen: frozenset[int]) -> int:
    outside = set(graph.nodes) - set(chosen)
    if not outside:
        # This is the convention used by the recovered Graffiti.pc definition
        # implementation and the project's already-gated source reading.
        return 0
    distances = nx.multi_source_dijkstra_path_length(graph, chosen)
    return max(distances[v] for v in outside)


def member_eccentricity(graph: nx.Graph, chosen: frozenset[int]) -> int:
    eccentricities = nx.eccentricity(graph)
    return max(eccentricities[v] for v in chosen)


def terms(graph: nx.Graph) -> dict:
    graph = nx.convert_node_labels_to_integers(graph)
    graph2 = square_graph(graph)
    chosen = center(graph2)
    b, b_witness = maximum_induced_bipartite_order(graph)
    gamma_c, gamma_c_witness = connected_domination_number(graph)
    # L_s=n-gamma_c for connected graphs of order >=3.  The project follows
    # the source's one-leaf convention for K2, also yielding n-gamma_c.
    leaf_number = len(graph) - gamma_c
    readings = {}
    for n_scope, n_graph in (("G2", graph2), ("G", graph)):
        for external_only in (False, True):
            n_key = "external" if external_only else "definition"
            n_size = len(neighborhood(n_graph, chosen, external_only))
            for e_kind, e_fun in (("set", set_eccentricity), ("member", member_eccentricity)):
                for e_scope, e_graph in (("G2", graph2), ("G", graph)):
                    e_value = e_fun(e_graph, chosen)
                    rhs = n_size + 2 * e_value
                    key = f"N_{n_scope}_{n_key}__ecc_{e_scope}_{e_kind}"
                    readings[key] = {
                        "N": n_size,
                        "ecc": e_value,
                        "rhs": rhs,
                        "residual": leaf_number + b - rhs,
                    }
    return {
        "n": len(graph),
        "m": graph.number_of_edges(),
        "graph6": nx.to_graph6_bytes(graph, header=False).decode().strip(),
        "degree_sequence": sorted((d for _, d in graph.degree()), reverse=True),
        "diameter": nx.diameter(graph),
        "square_edges": graph2.number_of_edges(),
        "square_is_complete": graph2.number_of_edges() == len(graph) * (len(graph) - 1) // 2,
        "square_center": sorted(chosen),
        "b": b,
        "b_witness": list(b_witness),
        "gamma_c": gamma_c,
        "gamma_c_witness": list(gamma_c_witness),
        "L_s": leaf_number,
        "lhs": leaf_number + b,
        "readings": readings,
    }


def named_controls() -> list[tuple[str, nx.Graph]]:
    controls = []
    controls.extend((f"C{n}", nx.cycle_graph(n)) for n in range(5, 10))
    controls.append(("P7", nx.path_graph(7)))
    controls.append(("Petersen", nx.petersen_graph()))
    controls.append(("K3,3", nx.complete_bipartite_graph(3, 3)))
    controls.append(("K7", nx.complete_graph(7)))
    controls.extend((f"K1,{r}", nx.star_graph(r)) for r in range(2, 10))
    controls.extend(
        (f"K{a},{b}", nx.complete_bipartite_graph(a, b))
        for a in range(1, 7)
        for b in range(a, 7)
    )
    return controls


def main() -> None:
    started = time.monotonic()
    witness = nx.complement(nx.petersen_graph())
    witness_data = terms(witness)
    leaf_tree_edges = [(0, 3), (3, 1), (0, 2), (1, 4), (1, 5), (0, 6), (0, 7), (0, 8), (0, 9)]
    leaf_tree = nx.Graph()
    leaf_tree.add_nodes_from(witness.nodes)
    leaf_tree.add_edges_from(leaf_tree_edges)
    assert nx.is_tree(leaf_tree)
    assert all(witness.has_edge(*edge) for edge in leaf_tree_edges)
    leaf_tree_leaves = sorted(v for v, degree in leaf_tree.degree if degree == 1)
    witness_data["leaf_tree_edges"] = [list(edge) for edge in leaf_tree_edges]
    witness_data["leaf_tree_leaves"] = leaf_tree_leaves

    atlas = [
        graph
        for graph in nx.graph_atlas_g()
        if 2 <= len(graph) <= 7 and nx.is_connected(graph)
    ]
    atlas_controls = [(f"atlas:{i}", graph) for i, graph in enumerate(atlas)]
    named = named_controls()
    controls = [("atlas", name, graph) for name, graph in atlas_controls]
    controls += [("named", name, graph) for name, graph in named]
    reading_names = tuple(witness_data["readings"])
    gate = {
        name: {
            "atlas_violations": 0,
            "named_violations": 0,
            "total_violations": 0,
            "first": None,
        }
        for name in reading_names
    }
    for control_group, control_name, graph in controls:
        result = terms(graph)
        for reading_name in reading_names:
            residual = result["readings"][reading_name]["residual"]
            if residual < 0:
                gate[reading_name][f"{control_group}_violations"] += 1
                gate[reading_name]["total_violations"] += 1
                if gate[reading_name]["first"] is None:
                    gate[reading_name]["first"] = {
                        "name": control_name,
                        "graph6": result["graph6"],
                        "n": result["n"],
                        "residual": residual,
                    }

    output = {
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "atlas_connected_n2_to_n7": len(atlas),
        "named_control_rows": len(named),
        "gate_rows_total_with_named_duplicates": len(controls),
        "witness": witness_data,
        "gate": gate,
    }
    print(json.dumps(output, indent=2, sort_keys=True))

    faithful = "N_G2_definition__ecc_G2_set"
    assert witness_data["n"] == 10
    assert witness_data["m"] == 30
    assert witness_data["degree_sequence"] == [6] * 10
    assert witness_data["diameter"] == 2
    assert witness_data["square_is_complete"]
    assert witness_data["b"] == 4
    assert witness_data["gamma_c"] == 3
    assert witness_data["L_s"] == 7
    assert len(witness_data["leaf_tree_leaves"]) == 7
    assert witness_data["lhs"] == 11
    assert witness_data["readings"][faithful] == {"N": 10, "ecc": 0, "rhs": 10, "residual": 1}
    assert gate[faithful]["total_violations"] == 0
    assert witness_data["readings"]["N_G2_definition__ecc_G2_member"]["residual"] == -1
    assert gate["N_G2_definition__ecc_G2_member"]["total_violations"] > 0


if __name__ == "__main__":
    main()
