#!/usr/bin/env python3
"""Fixed-catalogue checks for Method v0.3 Lane P1 (WOWII 183).

This script does not generate graphs.  By default it checks the connected
Graph Atlas graphs of orders 2 through 7.  With ``--graph6`` it reads the
already-frozen connected order-8 catalogue used by
``verify_wowii_183_extremal.py``.

The checks distinguish failed proof devices from the remaining proposition:

* endpoint_avoidance: for each extremal centre x and its unique distance-three
  vertex z, some minimum connected dominating set avoids both x and z;
* cds_plus_two: some minimum connected dominating set can be enlarged by two
  outside vertices to an induced bipartite set;
* gamma_at_most_four: the claw-free core always has connected domination
  number at most four;
* sharpened_dichotomy: in the claw-free core, either gamma_c <= 4 or deletion
  of one vertex makes the graph bipartite.

The first three are deliberately expected to fail.  The last check is only a
bounded audit and is not asserted as a theorem.
"""

from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path
from typing import Iterable

import networkx as nx


def graph_square(graph: nx.Graph) -> nx.Graph:
    square = nx.Graph()
    square.add_nodes_from(graph)
    lengths = dict(nx.all_pairs_shortest_path_length(graph, cutoff=2))
    square.add_edges_from(
        (u, v)
        for u, v in combinations(graph.nodes, 2)
        if lengths[u].get(v, 3) <= 2
    )
    return square


def independent(graph: nx.Graph, chosen: Iterable[int]) -> bool:
    return all(not graph.has_edge(u, v) for u, v in combinations(chosen, 2))


def local_independence(graph: nx.Graph) -> int:
    answer = 0
    for vertex in graph:
        neighbors = tuple(graph.neighbors(vertex))
        for size in range(len(neighbors), answer, -1):
            if any(independent(graph, chosen) for chosen in combinations(neighbors, size)):
                answer = size
                break
    return answer


def connected_dominating_sets(graph: nx.Graph) -> list[frozenset[int]]:
    vertices = tuple(graph)
    for size in range(1, len(vertices) + 1):
        answers = []
        for chosen in combinations(vertices, size):
            selected = frozenset(chosen)
            if size > 1 and not nx.is_connected(graph.subgraph(selected)):
                continue
            if all(
                vertex in selected
                or any(neighbor in selected for neighbor in graph.neighbors(vertex))
                for vertex in vertices
            ):
                answers.append(selected)
        if answers:
            return answers
    raise AssertionError("connected graph has no connected dominating set")


def bipartite_number(graph: nx.Graph) -> int:
    vertices = tuple(graph)
    for size in range(len(vertices), 0, -1):
        if any(nx.is_bipartite(graph.subgraph(chosen)) for chosen in combinations(vertices, size)):
            return size
    raise AssertionError("nonempty graph has no induced bipartite subgraph")


def odd_cycle_transversal_at_most_one(graph: nx.Graph) -> bool:
    return any(
        nx.is_bipartite(graph.subgraph(set(graph) - {vertex}))
        for vertex in graph
    )


def extremal_centres(graph: nx.Graph, square: nx.Graph) -> list[tuple[int, int]]:
    maximum_degree = max(dict(square.degree()).values())
    answers = []
    for centre, degree in square.degree():
        if degree != maximum_degree:
            continue
        distances = nx.single_source_shortest_path_length(graph, centre)
        far = [vertex for vertex, distance in distances.items() if distance == 3]
        if max(distances.values()) == 3 and len(far) == 1:
            answers.append((centre, far[0]))
    return answers


def graph_record(
    graph: nx.Graph,
    *,
    source: str,
    gamma_c: int,
    b: int,
    mu: int,
    extra: dict | None = None,
) -> dict:
    record = {
        "source": source,
        "graph6": nx.to_graph6_bytes(graph, header=False).decode().strip(),
        "n": graph.number_of_nodes(),
        "m": graph.number_of_edges(),
        "edges": [list(sorted(edge)) for edge in sorted(tuple(sorted(edge)) for edge in graph.edges())],
        "gamma_c": gamma_c,
        "b": b,
        "mu": mu,
    }
    if extra:
        record.update(extra)
    return record


def read_graph6(path: str) -> Iterable[nx.Graph]:
    stream = sys.stdin.buffer if path == "-" else open(path, "rb")
    try:
        for line in stream:
            if line.strip() and not line.startswith(b">"):
                yield nx.from_graph6_bytes(line.strip())
    finally:
        if path != "-":
            stream.close()


def audit(graphs: Iterable[nx.Graph], source: str) -> dict:
    counts = {
        "connected": 0,
        "critical_nonbipartite": 0,
        "mu_3": 0,
        "claw_free": 0,
    }
    failures: dict[str, list[dict]] = {
        "endpoint_avoidance": [],
        "cds_plus_two": [],
        "gamma_at_most_four": [],
        "sharpened_dichotomy": [],
    }

    for graph in graphs:
        if not nx.is_connected(graph):
            continue
        counts["connected"] += 1
        square = graph_square(graph)
        radius = nx.radius(square)
        q = graph.number_of_nodes() - 1 - max(dict(square.degree()).values())
        if q != 2 * radius - 3 or nx.is_bipartite(graph):
            continue
        centres = extremal_centres(graph, square)
        assert centres
        counts["critical_nonbipartite"] += 1

        mu = local_independence(graph)
        minimum_sets = connected_dominating_sets(graph)
        gamma_c = len(minimum_sets[0])
        b = bipartite_number(graph)
        assert b >= gamma_c + 2
        base = dict(source=source, gamma_c=gamma_c, b=b, mu=mu)

        for centre, far in centres:
            if not any(centre not in chosen and far not in chosen for chosen in minimum_sets):
                failures["endpoint_avoidance"].append(
                    graph_record(
                        graph,
                        **base,
                        extra={
                            "centre": centre,
                            "far": far,
                            "minimum_cds": [sorted(chosen) for chosen in minimum_sets],
                        },
                    )
                )

        extendable = False
        for chosen in minimum_sets:
            outside = set(graph) - chosen
            if any(
                nx.is_bipartite(graph.subgraph(chosen | set(pair)))
                for pair in combinations(outside, 2)
            ):
                extendable = True
                break
        if not extendable:
            failures["cds_plus_two"].append(
                graph_record(
                    graph,
                    **base,
                    extra={"minimum_cds": [sorted(chosen) for chosen in minimum_sets]},
                )
            )

        if mu == 3:
            counts["mu_3"] += 1
            continue
        assert mu <= 2
        counts["claw_free"] += 1
        if gamma_c > 4:
            failures["gamma_at_most_four"].append(graph_record(graph, **base))
            if not odd_cycle_transversal_at_most_one(graph):
                failures["sharpened_dichotomy"].append(graph_record(graph, **base))

    smallest = {}
    for name, records in failures.items():
        records.sort(key=lambda item: (item["n"], item["m"], item["graph6"]))
        smallest[name] = records[0] if records else None
    return {
        "catalogue": source,
        "counts": counts,
        "failure_counts": {name: len(records) for name, records in failures.items()},
        "smallest_countermodels": smallest,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph6", help="fixed graph6 catalogue; use - for stdin")
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()

    if args.graph6:
        graphs = read_graph6(args.graph6)
        source = "connected order-8 graph6 catalogue"
    else:
        graphs = (
            graph
            for graph in nx.graph_atlas_g()
            if 2 <= graph.number_of_nodes() <= 7
        )
        source = "Graph Atlas orders 2..7"

    result = audit(graphs, source)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    print(rendered)
    if args.json_output:
        args.json_output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
