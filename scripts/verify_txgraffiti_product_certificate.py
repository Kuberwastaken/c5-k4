#!/usr/bin/env python3
"""Independently replay a TxGraffiti product crossing certificate."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Sequence

import networkx as nx


CAMPAIGN_ID = "txgraffiti-product-conjecture-development-v1"
CERTIFICATE_SCHEMA = "c5k4-txgraffiti-product-certificate-1.0"


class CertificateError(RuntimeError):
    pass


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def labelled_graph6(graph: nx.Graph) -> str:
    ordered = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    return nx.to_graph6_bytes(ordered, header=False).decode().strip()


def graph_identity(graph: nx.Graph) -> dict[str, object]:
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    edges = [[int(u), int(v)] for u, v in sorted((min(u, v), max(u, v)) for u, v in graph.edges())]
    raw = canonical_json({"n": graph.number_of_nodes(), "edges": edges})
    return {
        "n": graph.number_of_nodes(),
        "m": graph.number_of_edges(),
        "labelled_graph6": labelled_graph6(graph),
        "edge_list": edges,
        "labelled_identity_sha256": hashlib.sha256(raw).hexdigest(),
    }


def graph_from_identity(value: object, require_connected: bool = False) -> nx.Graph:
    if not isinstance(value, dict):
        raise CertificateError("graph identity is not an object")
    n = value.get("n")
    edges = value.get("edge_list")
    if not isinstance(n, int) or isinstance(n, bool) or n < 0 or not isinstance(edges, list):
        raise CertificateError("invalid graph order or edge list")
    graph = nx.Graph()
    graph.add_nodes_from(range(n))
    normalized: list[list[int]] = []
    for edge in edges:
        if not isinstance(edge, list) or len(edge) != 2:
            raise CertificateError("invalid edge record")
        u, v = edge
        if (
            not isinstance(u, int) or isinstance(u, bool)
            or not isinstance(v, int) or isinstance(v, bool)
            or not 0 <= u < v < n
        ):
            raise CertificateError("edge is not a sorted in-range simple edge")
        normalized.append([u, v])
        graph.add_edge(u, v)
    if normalized != sorted(normalized) or len(normalized) != len({tuple(edge) for edge in normalized}):
        raise CertificateError("edge list is not strictly sorted and unique")
    if graph_identity(graph) != value:
        raise CertificateError("graph identity fields do not replay")
    if require_connected and (n < 2 or not nx.is_connected(graph)):
        raise CertificateError("factor is not a connected graph of order at least two")
    return graph


def cartesian_product(left: nx.Graph, right: nx.Graph) -> nx.Graph:
    graph = nx.Graph()
    vertices = [(u, v) for u in left for v in right]
    graph.add_nodes_from(vertices)
    for u, v in vertices:
        for x in right.neighbors(v):
            graph.add_edge((u, v), (u, x))
        for w in left.neighbors(u):
            graph.add_edge((u, v), (w, v))
    return nx.convert_node_labels_to_integers(graph, ordering="sorted")


def direct_product(left: nx.Graph, right: nx.Graph) -> nx.Graph:
    graph = nx.Graph()
    vertices = [(u, v) for u in left for v in right]
    graph.add_nodes_from(vertices)
    for u, v in vertices:
        for w in left.neighbors(u):
            for x in right.neighbors(v):
                graph.add_edge((u, v), (w, x))
    return nx.convert_node_labels_to_integers(graph, ordering="sorted")


def dominates(graph: nx.Graph, chosen: Sequence[int]) -> bool:
    covered = set(chosen)
    for vertex in chosen:
        covered.update(graph.neighbors(vertex))
    return len(covered) == graph.number_of_nodes()


def totally_dominates(graph: nx.Graph, chosen: Sequence[int]) -> bool:
    covered: set[int] = set()
    for vertex in chosen:
        covered.update(graph.neighbors(vertex))
    return len(covered) == graph.number_of_nodes()


def has_dominating_set_of_size(graph: nx.Graph, size: int) -> bool:
    if size < 0 or size > graph.number_of_nodes():
        return False
    return any(dominates(graph, chosen) for chosen in itertools.combinations(sorted(graph), size))


def validate_absence_record(value: object, size: int, order: int) -> None:
    total = math.comb(order, size) if 0 <= size <= order else 0
    expected = {
        "size": size,
        "subsets_examined": total,
        "total_subsets": total,
        "dominating_set_found": None,
        "complete": True,
    }
    if value != expected:
        raise CertificateError("stored exhaustive-absence receipt is not exact")


def verify_certificate(value: object) -> bool:
    try:
        if not isinstance(value, dict):
            raise CertificateError("certificate is not an object")
        if value.get("schema") != CERTIFICATE_SCHEMA or value.get("campaign_id") != CAMPAIGN_ID:
            raise CertificateError("certificate schema or campaign differs")
        if value.get("kind") != "evaluated_pair" or value.get("crossing") is not True:
            raise CertificateError("certificate is not a crossing evaluation")
        left = graph_from_identity(value.get("left"), require_connected=True)
        right = graph_from_identity(value.get("right"), require_connected=True)
        cartesian = cartesian_product(left, right)
        direct = direct_product(left, right)
        if graph_identity(cartesian) != value.get("cartesian"):
            raise CertificateError("Cartesian-product identity does not replay")
        if graph_identity(direct) != value.get("direct"):
            raise CertificateError("direct-product identity does not replay")

        k = value.get("k")
        witness = value.get("cartesian_total_dominating_set")
        if not isinstance(k, int) or isinstance(k, bool) or not 1 <= k <= cartesian.number_of_nodes():
            raise CertificateError("invalid witness size")
        if (
            not isinstance(witness, list)
            or len(witness) != k
            or len(set(witness)) != k
            or any(not isinstance(v, int) or isinstance(v, bool) or not 0 <= v < cartesian.number_of_nodes() for v in witness)
        ):
            raise CertificateError("invalid Cartesian total-dominating witness")
        if witness != sorted(witness) or not totally_dominates(cartesian, witness):
            raise CertificateError("Cartesian total-dominating witness does not replay")

        validate_absence_record(value.get("no_direct_dominating_set_size_k"), k, direct.number_of_nodes())
        validate_absence_record(value.get("no_direct_dominating_set_size_k_minus_1"), k - 1, direct.number_of_nodes())
        if has_dominating_set_of_size(direct, k) or has_dominating_set_of_size(direct, k - 1):
            raise CertificateError("direct-product exhaustive absence does not replay")
        return True
    except (CertificateError, KeyError, TypeError, ValueError, nx.NetworkXException):
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path)
    args = parser.parse_args()
    try:
        value = json.loads(args.certificate.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"CERTIFICATE_INVALID detail={exc}")
        return 1
    if not verify_certificate(value):
        print("CERTIFICATE_INVALID")
        return 1
    print(f"CERTIFICATE_OK name={value['name']} k={value['k']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
