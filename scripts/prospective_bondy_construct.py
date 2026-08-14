#!/usr/bin/env python3
"""Target-free frozen constructor for the Bondy longest-cycles DEVELOPMENT arm.

This module deliberately contains no circumference or path-cover evaluator.
It constructs labelled peripheral graphs H around S(4,4), checks only source,
premise, theorem-domain, integrity, and duplicate gates, and emits canonical
JSON records in a deterministic order.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Iterable, Iterator, Sequence

import networkx as nx

K = 4
T = 4
BLOCKS = 5
H_ORDER = 20
G_ORDER = 24
LARGE_GRAPH_CUTOFF = 108
ROW_LIMIT = 96

PERFECT_MATCHINGS: tuple[tuple[tuple[int, int], ...], ...] = (
    ((0, 1), (2, 3)),
    ((0, 2), (1, 3)),
    ((0, 3), (1, 2)),
)

# Each catalogue entry is a loopless quotient 2-factor: every block occurs
# exactly four times. Occurrence number is its port before PORT_PERMUTATIONS.
QUOTIENT_CATALOGUE: tuple[tuple[tuple[int, ...], ...], ...] = (
    ((0, 1, 2, 3), (1, 2, 3, 4), (2, 3, 4, 0), (3, 4, 0, 1), (4, 0, 1, 2)),
    ((0, 1, 3, 2), (1, 2, 4, 3), (2, 3, 0, 4), (3, 4, 1, 0), (4, 0, 2, 1)),
    ((0, 2, 1, 3), (1, 3, 2, 4), (2, 4, 3, 0), (3, 0, 4, 1), (4, 1, 0, 2)),
    ((0, 2, 4, 1), (1, 3, 0, 2), (2, 4, 1, 3), (3, 0, 2, 4), (4, 1, 3, 0)),
)

PORT_PERMUTATIONS: tuple[tuple[int, int, int, int], ...] = (
    (0, 1, 2, 3),
    (1, 0, 3, 2),
    (1, 2, 3, 0),
)


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def vertex(block: int, port: int) -> int:
    if not (0 <= block < BLOCKS and 0 <= port < T):
        raise ValueError("invalid block/port")
    return T * block + port


def role_map() -> list[dict[str, int]]:
    return [{"vertex": vertex(i, j), "block": i, "port": j} for i in range(BLOCKS) for j in range(T)]


def edge_list(graph: nx.Graph) -> list[list[int]]:
    return [[u, v] for u, v in sorted(tuple(sorted(e)) for e in graph.edges())]


def graph_from_edges(order: int, edges: Sequence[Sequence[int]]) -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(range(order))
    graph.add_edges_from((int(u), int(v)) for u, v in edges)
    return graph


def source_seed() -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(range(H_ORDER))
    for block in range(BLOCKS):
        graph.add_edges_from(
            (vertex(block, a), vertex(block, b))
            for a in range(T) for b in range(a + 1, T)
        )
    return graph


def join_separator(peripheral: nx.Graph) -> nx.Graph:
    if set(peripheral) != set(range(H_ORDER)):
        raise ValueError("peripheral labels drifted")
    graph = nx.Graph()
    graph.add_nodes_from(range(G_ORDER))
    graph.add_edges_from(peripheral.edges())
    separator = range(H_ORDER, G_ORDER)
    graph.add_edges_from(itertools.combinations(separator, 2))
    graph.add_edges_from((s, h) for s in separator for h in range(H_ORDER))
    return graph


def source_control() -> dict[str, object]:
    peripheral = source_seed()
    graph = join_separator(peripheral)
    delta_h = min(dict(peripheral.degree()).values())
    delta_g = min(dict(graph.degree()).values())
    numerator = G_ORDER + K * (K - 1)
    denominator = K + 1
    integer_threshold = math.ceil(numerator / denominator)
    scaled_residual = denominator * delta_g - numerator
    if (delta_h, delta_g, integer_threshold, scaled_residual) != (3, 7, 8, -1):
        raise AssertionError("S(4,4) minus-one source control failed")
    return {
        "kind": "source_seed_control",
        "k": K,
        "t": T,
        "h": H_ORDER,
        "n": G_ORDER,
        "delta_h": delta_h,
        "delta_g": delta_g,
        "threshold": {"numerator": numerator, "denominator": denominator, "ceiling": integer_threshold},
        "scaled_degree_residual": scaled_residual,
        "source_seed_edge_sha256": sha256_bytes(canonical_bytes(edge_list(peripheral))),
    }


def cross_factor(quotient_index: int, permutation_index: int) -> nx.Graph:
    quotient = QUOTIENT_CATALOGUE[quotient_index]
    permutation = PORT_PERMUTATIONS[permutation_index]
    seen = [0] * BLOCKS
    cycles: list[list[int]] = []
    for quotient_cycle in quotient:
        cycle: list[int] = []
        for block in quotient_cycle:
            occurrence = seen[block]
            if occurrence >= T:
                raise AssertionError("quotient catalogue overuses a block")
            cycle.append(vertex(block, permutation[occurrence]))
            seen[block] += 1
        cycles.append(cycle)
    if seen != [T] * BLOCKS:
        raise AssertionError("quotient catalogue does not cover every port")
    factor = nx.Graph()
    factor.add_nodes_from(range(H_ORDER))
    for cycle in cycles:
        factor.add_edges_from((cycle[i], cycle[(i + 1) % len(cycle)]) for i in range(len(cycle)))
    if nx.number_of_selfloops(factor) or factor.number_of_edges() != H_ORDER:
        raise AssertionError("cross factor is not loopless 2-regular")
    if set(dict(factor.degree()).values()) != {2}:
        raise AssertionError("cross factor degree drift")
    if any(u // T == v // T for u, v in factor.edges()):
        raise AssertionError("cross factor contains an undeclared within-block edge")
    return factor


def construct_row(
    matching_choices: tuple[int, int, int, int, int],
    quotient_index: int,
    permutation_index: int,
) -> tuple[nx.Graph, dict[str, object]]:
    seed = source_seed()
    graph = seed.copy()
    deleted: list[tuple[int, int]] = []
    for block, choice in enumerate(matching_choices):
        for a, b in PERFECT_MATCHINGS[choice]:
            edge = tuple(sorted((vertex(block, a), vertex(block, b))))
            graph.remove_edge(*edge)
            deleted.append(edge)
    factor = cross_factor(quotient_index, permutation_index)
    added = sorted(tuple(sorted(e)) for e in factor.edges())
    graph.add_edges_from(added)
    metadata = {
        "matching_choices": list(matching_choices),
        "quotient_index": quotient_index,
        "port_permutation_index": permutation_index,
        "deleted_edges": [list(e) for e in sorted(deleted)],
        "added_edges": [list(e) for e in added],
        "quotient_cycles": [list(c) for c in QUOTIENT_CATALOGUE[quotient_index]],
        "port_permutation": list(PORT_PERMUTATIONS[permutation_index]),
    }
    return graph, metadata


def induced_claw(graph: nx.Graph) -> list[int] | None:
    for center in sorted(graph):
        neighbors = sorted(graph.neighbors(center))
        for leaves in itertools.combinations(neighbors, 3):
            if all(not graph.has_edge(a, b) for a, b in itertools.combinations(leaves, 2)):
                return [center, *leaves]
    return None


def universal_join_connectivity_audit() -> dict[str, object]:
    checked = 0
    separator = set(range(H_ORDER, G_ORDER))
    for size in range(K):
        for removed_tuple in itertools.combinations(range(G_ORDER), size):
            removed = set(removed_tuple)
            surviving_separator = sorted(separator - removed)
            if not surviving_separator:
                raise AssertionError("fewer than four deletions removed the separator")
            checked += 1
    return {
        "method": "enumerate_all_deleted_sets_and_exhibit_surviving_universal_separator_vertex",
        "sets_checked": checked,
        "expected_sets": sum(math.comb(G_ORDER, r) for r in range(K)),
    }


def validate_labelled_roundtrip(graph: nx.Graph) -> str:
    edges = edge_list(graph)
    rebuilt = graph_from_edges(H_ORDER, edges)
    if edge_list(rebuilt) != edges or set(rebuilt) != set(range(H_ORDER)):
        raise AssertionError("labelled edge round-trip failed")
    roles = role_map()
    if len(roles) != H_ORDER or len({(r["block"], r["port"]) for r in roles}) != H_ORDER:
        raise AssertionError("role-map round-trip failed")
    return sha256_bytes(canonical_bytes({"edges": edges, "roles": roles}))


def constructor_gate(graph: nx.Graph, metadata: dict[str, object]) -> tuple[str, dict[str, object]]:
    seed = source_seed()
    declared_deleted = {tuple(e) for e in metadata["deleted_edges"]}
    declared_added = {tuple(e) for e in metadata["added_edges"]}
    actual_deleted = set(map(tuple, edge_list(seed))) - set(map(tuple, edge_list(graph)))
    actual_added = set(map(tuple, edge_list(graph))) - set(map(tuple, edge_list(seed)))
    if actual_deleted != declared_deleted or actual_added != declared_added:
        return "GATE_FAIL", {"reason": "undeclared_edge_change"}
    if nx.number_of_selfloops(graph) or graph.number_of_edges() != 40:
        return "GATE_FAIL", {"reason": "simple_or_edge_count_drift"}
    digest = validate_labelled_roundtrip(graph)
    degrees_h = sorted(dict(graph.degree()).values())
    joined = join_separator(graph)
    degrees_g = sorted(dict(joined.degree()).values())
    threshold_numerator = G_ORDER + K * (K - 1)
    threshold = math.ceil(threshold_numerator / (K + 1))
    if K != 4 or T != 4 or G_ORDER >= LARGE_GRAPH_CUTOFF:
        return "GATE_FAIL", {"reason": "order_or_theorem_boundary_drift"}
    if degrees_h != [4] * H_ORDER or min(degrees_g) != 8 or threshold != 8:
        return "GATE_FAIL", {"reason": "degree_wall_drift"}
    if not actual_deleted:
        return "KNOWN_PROOF_DOMAIN", {"reason": "no_op_or_monotone_supergraph"}
    # A cross factor with <= k components already gives a spanning <=k-path
    # cover before any target optimization and is a frozen neutral rejection.
    factor = graph_from_edges(H_ORDER, metadata["added_edges"])
    factor_components = nx.number_connected_components(factor)
    if factor_components <= K:
        return "KNOWN_PROOF_DOMAIN", {"reason": "naive_cross_factor_path_cover", "components": factor_components}
    claw = induced_claw(joined)
    if claw is None:
        return "KNOWN_PROOF_DOMAIN", {"reason": "claw_free"}
    return "APPLICABLE", {
        "labelled_sha256": digest,
        "graph6": nx.to_graph6_bytes(graph, header=False).decode("ascii").strip(),
        "delta_h": min(degrees_h),
        "delta_g": min(degrees_g),
        "threshold": threshold,
        "induced_claw": claw,
        "cross_factor_components": factor_components,
    }


def frozen_parameter_rows() -> Iterator[tuple[tuple[int, int, int, int, int], int, int]]:
    emitted = 0
    for choices in itertools.product(range(len(PERFECT_MATCHINGS)), repeat=BLOCKS):
        typed_choices = tuple(int(x) for x in choices)
        for quotient_index in range(len(QUOTIENT_CATALOGUE)):
            for permutation_index in range(len(PORT_PERMUTATIONS)):
                if emitted >= ROW_LIMIT:
                    return
                yield typed_choices, quotient_index, permutation_index
                emitted += 1


class IsoStore:
    def __init__(self) -> None:
        self.labelled: set[str] = set()
        self.buckets: dict[str, list[nx.Graph]] = {}

    def classify(self, graph: nx.Graph, labelled_sha256: str) -> str:
        if labelled_sha256 in self.labelled:
            return "DUPLICATE_LABELLED"
        self.labelled.add(labelled_sha256)
        triangle_profile = tuple(sorted(nx.triangles(graph).values()))
        neighborhood_edges = tuple(sorted(graph.subgraph(graph.neighbors(v)).number_of_edges() for v in graph))
        common_neighbor_profile = tuple(sorted(len(set(graph[a]) & set(graph[b])) for a, b in itertools.combinations(graph, 2)))
        key = "|".join((
            nx.weisfeiler_lehman_graph_hash(graph, iterations=4),
            repr(triangle_profile),
            repr(neighborhood_edges),
            repr(common_neighbor_profile),
        ))
        bucket = self.buckets.setdefault(key, [])
        if any(nx.vf2pp_is_isomorphic(graph, old) for old in bucket):
            return "DUPLICATE_ISOMORPHIC"
        bucket.append(graph.copy())
        return "NEW"


def generate(limit: int = ROW_LIMIT) -> Iterator[dict[str, object]]:
    if not 0 <= limit <= ROW_LIMIT:
        raise ValueError("limit exceeds frozen row limit")
    seed_digest = sha256_bytes(canonical_bytes(edge_list(source_seed())))
    isos = IsoStore()
    connectivity = universal_join_connectivity_audit()
    for row_index, params in enumerate(itertools.islice(frozen_parameter_rows(), limit)):
        graph, metadata = construct_row(*params)
        verdict, gate = constructor_gate(graph, metadata)
        record: dict[str, object] = {
            "kind": "constructor_row",
            "row_index": row_index,
            "parameters": metadata,
            "constructor_verdict": verdict,
            "gate": gate,
            "source_seed_edge_sha256": seed_digest,
            "connectivity_audit": connectivity,
        }
        if verdict == "APPLICABLE":
            duplicate = isos.classify(graph, str(gate["labelled_sha256"]))
            if duplicate != "NEW":
                record["constructor_verdict"] = duplicate
            else:
                record["edges_h"] = edge_list(graph)
                record["roles"] = role_map()
        yield record


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
        directory_fd = os.open(path.parent, os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-control", action="store_true")
    parser.add_argument("--construct", action="store_true")
    parser.add_argument("--limit", type=int, default=ROW_LIMIT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.source_control == args.construct:
        parser.error("choose exactly one of --source-control or --construct")
    if args.source_control:
        payload = canonical_bytes(source_control())
    else:
        payload = b"".join(canonical_bytes(row) for row in generate(args.limit))
    if args.output:
        atomic_write(args.output, payload)
    else:
        os.write(1, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
