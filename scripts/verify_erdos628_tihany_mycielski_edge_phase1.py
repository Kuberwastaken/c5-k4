#!/usr/bin/env python3
"""Independent SAT/replay audit for the frozen Erdős 628 Phase 1 result."""

from __future__ import annotations

import argparse
import hashlib
import json

import networkx as nx
from pysat.solvers import Glucose4


def graph_independent() -> nx.Graph:
    h5 = nx.mycielskian(nx.cycle_graph(5), iterations=2)
    graph = h5.copy()
    graph.add_nodes_from((23, 24))
    graph.add_edge(23, 24)
    graph.add_edges_from((23, vertex) for vertex in h5 if vertex != 22)
    graph.add_edges_from((24, vertex) for vertex in h5)
    graph.remove_edge(1, 2)
    return graph


def four_colorable_sat(graph: nx.Graph) -> tuple[bool, list[int] | None]:
    n = graph.number_of_nodes()
    colors = 4

    def var(vertex: int, color: int) -> int:
        return vertex * colors + color + 1

    solver = Glucose4()
    for vertex in range(n):
        solver.add_clause([var(vertex, color) for color in range(colors)])
        for left in range(colors):
            for right in range(left + 1, colors):
                solver.add_clause([-var(vertex, left), -var(vertex, right)])
    for left, right in graph.edges():
        for color in range(colors):
            solver.add_clause([-var(left, color), -var(right, color)])
    satisfiable = solver.solve()
    if not satisfiable:
        solver.delete()
        return False, None
    model = set(solver.get_model())
    coloring = [next(color for color in range(colors) if var(v, color) in model)
                for v in range(n)]
    solver.delete()
    assert all(coloring[a] != coloring[b] for a, b in graph.edges())
    return True, coloring


def replay_coloring(graph: nx.Graph, coloring: list[int]) -> bool:
    return len(coloring) == graph.number_of_nodes() and all(
        coloring[left] != coloring[right] for left, right in graph.edges()
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("result_json")
    args = parser.parse_args()
    result = json.load(open(args.result_json, encoding="utf-8"))
    graph = graph_independent()
    edges = sorted(tuple(sorted(edge)) for edge in graph.edges())
    assert len(edges) == 116
    digest = hashlib.sha256()
    qualifying = 0
    four_colorable = 0
    for index, edge in enumerate(edges, 1):
        vertices = [v for v in graph if v not in edge]
        complement = nx.convert_node_labels_to_integers(
            graph.subgraph(vertices), ordering="sorted"
        )
        feasible, _ = four_colorable_sat(complement)
        ge_five = not feasible
        digest.update(f"{edge[0]},{edge[1]},{int(ge_five)}\n".encode())
        qualifying += ge_five
        four_colorable += feasible
        recorded = result["all_edge_rows"][index - 1]
        assert recorded == {"index": index, "edge": list(edge),
                            "complement_ge_five": ge_five}

    witness = result["first_witness"]
    edge = tuple(witness["edge"])
    assert graph.has_edge(*edge)
    vertices = [v for v in graph if v not in edge]
    complement = nx.convert_node_labels_to_integers(
        graph.subgraph(vertices), ordering="sorted"
    )
    assert replay_coloring(complement, witness["primary"]["five_coloring"])
    assert replay_coloring(complement, witness["independent"]["five_coloring"])
    audit = {
        "status": "PASS",
        "method": "independent Glucose4 CNF four-colorability for every edge complement",
        "partition_evaluations": len(edges),
        "qualifying_edges": qualifying,
        "four_colorable_complements": four_colorable,
        "first_witness_edge": witness["edge"],
        "row_digest_sha256": digest.hexdigest(),
        "both_five_colorings_replayed": True,
    }
    assert qualifying == result["qualifying_edges"] == 115
    assert four_colorable == result["four_colorable_complements"] == 1
    assert audit["row_digest_sha256"] == result["row_digest_sha256"]
    print(json.dumps(audit, sort_keys=True))


if __name__ == "__main__":
    main()
