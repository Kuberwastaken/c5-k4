#!/usr/bin/env python3
"""Exact premise gate for the single frozen Erdős 628 Phase 1 graph."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass

import networkx as nx
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix


def mycielski(graph: nx.Graph) -> nx.Graph:
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    n = graph.number_of_nodes()
    result = nx.Graph()
    result.add_nodes_from(range(2 * n + 1))
    result.add_edges_from(graph.edges())
    for left, right in graph.edges():
        result.add_edge(n + left, right)
        result.add_edge(n + right, left)
    result.add_edges_from((2 * n, n + vertex) for vertex in range(n))
    return result


def frozen_graph() -> tuple[nx.Graph, dict]:
    c5 = nx.cycle_graph(5)
    h4 = mycielski(c5)
    h5 = mycielski(h4)
    assert h5.number_of_nodes() == 23
    latest_apex = 22
    x, y = 23, 24
    graph = h5.copy()
    graph.add_nodes_from((x, y))
    graph.add_edge(x, y)
    graph.add_edges_from((x, vertex) for vertex in h5 if vertex != latest_apex)
    graph.add_edges_from((y, vertex) for vertex in h5)
    if not graph.has_edge(1, 2):
        raise RuntimeError("frozen embedded C5 edge missing")
    graph.remove_edge(1, 2)
    return graph, {"u": latest_apex, "x": x, "y": y, "deleted": [1, 2]}


def replay_coloring(graph: nx.Graph, coloring: list[int]) -> bool:
    return len(coloring) == graph.number_of_nodes() and all(
        coloring[left] != coloring[right] for left, right in graph.edges()
    )


def replay_clique(graph: nx.Graph, clique: list[int]) -> bool:
    return all(graph.has_edge(left, right) for i, left in enumerate(clique)
               for right in clique[i + 1:])


def dsatur_feasible(graph: nx.Graph, colors: int) -> list[int] | None:
    n = graph.number_of_nodes()
    adjacency = [set(graph.neighbors(vertex)) for vertex in range(n)]
    assignment = [-1] * n
    neighbor_colors = [set() for _ in range(n)]

    def search(colored: int) -> bool:
        if colored == n:
            return True
        vertex = max(
            (v for v in range(n) if assignment[v] < 0),
            key=lambda v: (len(neighbor_colors[v]), len(adjacency[v]), -v),
        )
        forbidden = neighbor_colors[vertex]
        for color in range(colors):
            if color in forbidden:
                continue
            assignment[vertex] = color
            changed = []
            for neighbor in adjacency[vertex]:
                if assignment[neighbor] < 0 and color not in neighbor_colors[neighbor]:
                    neighbor_colors[neighbor].add(color)
                    changed.append(neighbor)
            if search(colored + 1):
                return True
            for neighbor in changed:
                neighbor_colors[neighbor].remove(color)
            assignment[vertex] = -1
        return False

    return assignment.copy() if search(0) else None


def combinatorial_oracle(graph: nx.Graph) -> dict:
    cliques = list(nx.find_cliques(graph))
    clique = min(
        (sorted(c) for c in cliques if len(c) == max(map(len, cliques))),
        key=lambda c: c,
    )
    if not replay_clique(graph, clique):
        raise RuntimeError("Bron-Kerbosch clique replay failed")
    infeasible = []
    coloring = None
    chromatic = None
    for colors in range(len(clique), graph.number_of_nodes() + 1):
        coloring = dsatur_feasible(graph, colors)
        if coloring is not None:
            chromatic = colors
            break
        infeasible.append(colors)
    if chromatic is None or coloring is None or not replay_coloring(graph, coloring):
        raise RuntimeError("DSATUR coloring replay failed")
    return {
        "name": "DSATUR+BronKerbosch",
        "chi": chromatic,
        "coloring": coloring,
        "infeasible_color_counts": infeasible,
        "omega": len(clique),
        "maximum_clique": clique,
        "coloring_replay": True,
        "clique_replay": True,
    }


def milp_maximum_clique(graph: nx.Graph) -> tuple[list[int], float, int]:
    n = graph.number_of_nodes()
    nonedges = [(left, right) for left in range(n) for right in range(left + 1, n)
                if not graph.has_edge(left, right)]
    matrix = lil_matrix((len(nonedges), n), dtype=float)
    for row, (left, right) in enumerate(nonedges):
        matrix[row, left] = 1
        matrix[row, right] = 1
    result = milp(
        c=-np.ones(n), integrality=np.ones(n),
        bounds=Bounds(np.zeros(n), np.ones(n)),
        constraints=LinearConstraint(matrix.tocsr(),
                                     np.full(len(nonedges), -np.inf),
                                     np.ones(len(nonedges))),
        options={"time_limit": 55.0},
    )
    if not result.success or result.mip_gap != 0:
        raise RuntimeError(f"clique MILP not exact: {result.message}")
    clique = [vertex for vertex, value in enumerate(result.x) if value > 0.5]
    if not replay_clique(graph, clique):
        raise RuntimeError("MILP clique replay failed")
    return clique, float(result.mip_gap), int(result.mip_node_count)


def milp_coloring(graph: nx.Graph, colors: int) -> dict | None:
    n = graph.number_of_nodes()
    variables = n * colors
    rows = n + graph.number_of_edges() * colors
    matrix = lil_matrix((rows, variables), dtype=float)
    lower = np.full(rows, -np.inf)
    upper = np.ones(rows)
    row = 0
    for vertex in range(n):
        for color in range(colors):
            matrix[row, vertex * colors + color] = 1
        lower[row] = 1
        row += 1
    for left, right in graph.edges():
        for color in range(colors):
            matrix[row, left * colors + color] = 1
            matrix[row, right * colors + color] = 1
            row += 1
    result = milp(
        c=np.zeros(variables), integrality=np.ones(variables),
        bounds=Bounds(np.zeros(variables), np.ones(variables)),
        constraints=LinearConstraint(matrix.tocsr(), lower, upper),
        options={"time_limit": 55.0},
    )
    if result.status == 2:
        return None
    if not result.success or result.mip_gap != 0:
        raise RuntimeError(f"coloring MILP not exact for {colors}: {result.message}")
    coloring = [max(range(colors), key=lambda color: result.x[v * colors + color])
                for v in range(n)]
    if not replay_coloring(graph, coloring):
        raise RuntimeError("MILP coloring replay failed")
    return {"coloring": coloring, "mip_gap": float(result.mip_gap),
            "mip_node_count": int(result.mip_node_count)}


def milp_oracle(graph: nx.Graph) -> dict:
    clique, clique_gap, clique_nodes = milp_maximum_clique(graph)
    infeasible = []
    certificate = None
    chromatic = None
    for colors in range(len(clique), graph.number_of_nodes() + 1):
        certificate = milp_coloring(graph, colors)
        if certificate is not None:
            chromatic = colors
            break
        infeasible.append(colors)
    if chromatic is None or certificate is None:
        raise RuntimeError("MILP chromatic search failed")
    return {
        "name": "binary-MILP",
        "chi": chromatic,
        "coloring": certificate["coloring"],
        "coloring_mip_gap": certificate["mip_gap"],
        "coloring_mip_node_count": certificate["mip_node_count"],
        "infeasible_color_counts": infeasible,
        "omega": len(clique),
        "maximum_clique": clique,
        "clique_mip_gap": clique_gap,
        "clique_mip_node_count": clique_nodes,
        "coloring_replay": True,
        "clique_replay": True,
    }


def split_search(graph: nx.Graph) -> dict:
    digest = hashlib.sha256()
    rows = []
    first_witness = None
    for index, edge in enumerate(sorted(tuple(sorted(e)) for e in graph.edges()), 1):
        complement_vertices = [v for v in graph.nodes() if v not in edge]
        complement = nx.convert_node_labels_to_integers(
            graph.subgraph(complement_vertices), ordering="sorted"
        )
        primary_four = dsatur_feasible(complement, 4)
        independent_four = milp_coloring(complement, 4)
        if (primary_four is None) != (independent_four is None):
            raise RuntimeError(f"split oracle disagreement at {edge}")
        complement_ge_five = primary_four is None
        digest.update(f"{edge[0]},{edge[1]},{int(complement_ge_five)}\n".encode())
        row = {"index": index, "edge": list(edge),
               "complement_ge_five": complement_ge_five}
        rows.append(row)
        if complement_ge_five and first_witness is None:
            primary_five = dsatur_feasible(complement, 5)
            independent_five = milp_coloring(complement, 5)
            if primary_five is None or independent_five is None:
                raise RuntimeError("first witness has no replayable 5-coloring")
            first_witness = {
                **row,
                "left_chi": 2,
                "left_edge_replay": graph.has_edge(*edge),
                "complement_vertices": complement_vertices,
                "primary": {"four_colorable": False, "five_coloring": primary_five,
                            "five_coloring_replay": replay_coloring(complement, primary_five)},
                "independent": {"four_colorable": False,
                                "five_coloring": independent_five["coloring"],
                                "five_coloring_replay": replay_coloring(
                                    complement, independent_five["coloring"]),
                                "five_color_mip_gap": independent_five["mip_gap"],
                                "five_color_mip_node_count": independent_five["mip_node_count"]},
            }
    return {
        "event": "PHASE1_SPLIT_RESULT",
        "trial": "ERDOS628_TIHANY_MYC_EDGE_PHASE1",
        "status": "HOLD_EXPLICIT_SPLIT" if first_witness else "CANDIDATE_NO_SPLIT",
        "partition_evaluations": len(rows),
        "candidate_evaluations": 1,
        "four_colorable_complements": sum(not row["complement_ge_five"] for row in rows),
        "qualifying_edges": sum(row["complement_ge_five"] for row in rows),
        "first_witness": first_witness,
        "row_digest_sha256": digest.hexdigest(),
        "all_edge_rows": rows,
        "independent_recomputation": "binary four-colorability MILP on every edge complement",
        "public_action": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("premise", "split"), nargs="?", default="premise")
    args = parser.parse_args()
    graph, labels = frozen_graph()
    if args.mode == "split":
        print(json.dumps(split_search(graph), sort_keys=True))
        return
    graph6 = nx.to_graph6_bytes(graph, header=False).strip()
    combinatorial = combinatorial_oracle(graph)
    integer_programming = milp_oracle(graph)
    if ((combinatorial["chi"], combinatorial["omega"])
            != (integer_programming["chi"], integer_programming["omega"])):
        raise RuntimeError("independent oracle disagreement")
    premise = combinatorial["chi"] == 6 and combinatorial["omega"] < 6
    result = {
        "event": "PHASE1_PREMISE_GATE",
        "trial": "ERDOS628_TIHANY_MYC_EDGE_PHASE1",
        "status": "PASS_TO_SPLIT_SEARCH" if premise else "STOP_PREMISE_FAILURE",
        "n": graph.number_of_nodes(),
        "m": graph.number_of_edges(),
        "graph6": graph6.decode(),
        "graph6_sha256": hashlib.sha256(graph6).hexdigest(),
        "labels": labels,
        "oracles": [combinatorial, integer_programming],
        "expected_premise": {"chi": 6, "omega_lt": 6},
        "premise_survives": premise,
        "tihany_partition_evaluations": 0,
        "candidate_evaluations": 1,
        "public_action": False,
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
