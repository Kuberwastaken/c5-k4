#!/usr/bin/env python3
"""Independent bounded replay of a TxGraffiti product v2 certificate."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import time
from typing import Sequence

import networkx as nx


CAMPAIGN_ID = "txgraffiti-product-conjecture-development-v2"
CERTIFICATE_SCHEMA = "c5k4-txgraffiti-product-v2-certificate-1.0"
SUBPROBLEM_SECONDS = 4.0


class CertificateError(RuntimeError):
    pass


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def graph_identity(graph: nx.Graph) -> dict[str, object]:
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    edges = [[int(u), int(v)] for u, v in sorted((min(u, v), max(u, v)) for u, v in graph.edges())]
    raw = canonical_json({"n": graph.number_of_nodes(), "edges": edges})
    return {
        "n": graph.number_of_nodes(), "m": graph.number_of_edges(),
        "labelled_graph6": nx.to_graph6_bytes(graph, header=False).decode().strip(),
        "edge_list": edges, "labelled_identity_sha256": hashlib.sha256(raw).hexdigest(),
    }


def graph_from_identity(value: object, connected: bool = False) -> nx.Graph:
    if not isinstance(value, dict):
        raise CertificateError("graph identity is not an object")
    n, edges = value.get("n"), value.get("edge_list")
    if not isinstance(n, int) or isinstance(n, bool) or n < 0 or not isinstance(edges, list):
        raise CertificateError("invalid order or edge list")
    graph = nx.Graph(); graph.add_nodes_from(range(n))
    normalized: list[list[int]] = []
    for edge in edges:
        if not isinstance(edge, list) or len(edge) != 2:
            raise CertificateError("invalid edge record")
        u, v = edge
        if (not isinstance(u, int) or isinstance(u, bool) or not isinstance(v, int)
                or isinstance(v, bool) or not 0 <= u < v < n):
            raise CertificateError("edge is not a sorted in-range simple edge")
        normalized.append([u, v]); graph.add_edge(u, v)
    if normalized != sorted(normalized) or len(normalized) != len({tuple(e) for e in normalized}):
        raise CertificateError("edge list is not sorted and unique")
    if graph_identity(graph) != value:
        raise CertificateError("identity fields do not replay")
    if connected and (n < 2 or not nx.is_connected(graph)):
        raise CertificateError("factor is not connected of order at least two")
    return graph


def cartesian_product(left: nx.Graph, right: nx.Graph) -> nx.Graph:
    graph = nx.Graph(); vertices = [(u, v) for u in left for v in right]
    graph.add_nodes_from(vertices)
    for u, v in vertices:
        graph.add_edges_from(((u, v), (u, x)) for x in right.neighbors(v))
        graph.add_edges_from(((u, v), (x, v)) for x in left.neighbors(u))
    return nx.convert_node_labels_to_integers(graph, ordering="sorted")


def direct_product(left: nx.Graph, right: nx.Graph) -> nx.Graph:
    graph = nx.Graph(); vertices = [(u, v) for u in left for v in right]
    graph.add_nodes_from(vertices)
    for u, v in vertices:
        for x in left.neighbors(u):
            for y in right.neighbors(v):
                graph.add_edge((u, v), (x, y))
    return nx.convert_node_labels_to_integers(graph, ordering="sorted")


def masks(graph: nx.Graph, total: bool) -> tuple[list[int], int]:
    if sorted(graph) != list(range(len(graph))):
        raise CertificateError("nonconsecutive product labels")
    values: list[int] = []
    for vertex in range(len(graph)):
        mask = 0 if total else 1 << vertex
        for neighbor in graph.neighbors(vertex):
            mask |= 1 << int(neighbor)
        values.append(mask)
    return values, (1 << len(graph)) - 1


def covers(values: Sequence[int], full: int, chosen: Sequence[int]) -> bool:
    covered = 0
    for vertex in chosen:
        covered |= values[vertex]
    return covered == full


def validate_witness(graph: nx.Graph, witness: object, size: int, total: bool) -> None:
    if (not isinstance(witness, list) or len(witness) != size
            or witness != sorted(witness) or len(set(witness)) != size
            or any(not isinstance(v, int) or isinstance(v, bool) or not 0 <= v < len(graph) for v in witness)):
        raise CertificateError("invalid witness coordinates")
    values, full = masks(graph, total)
    if not covers(values, full, witness):
        raise CertificateError("stored witness does not cover")


def lower_bound(graph: nx.Graph, total: bool) -> int:
    maximum = max(dict(graph.degree()).values())
    denominator = maximum if total else maximum + 1
    if denominator <= 0:
        raise CertificateError("undefined neighborhood lower bound")
    return max(1, math.ceil(len(graph) / denominator))


def prove_absent(graph: nx.Graph, size: int, total: bool) -> None:
    values, full = masks(graph, total)
    deadline = time.monotonic() + SUBPROBLEM_SECONDS
    for index, chosen in enumerate(itertools.combinations(range(len(graph)), size)):
        if index % 256 == 0 and time.monotonic() >= deadline:
            raise CertificateError("independent exact replay exceeded four-second subproblem cap")
        if covers(values, full, chosen):
            raise CertificateError("claimed absent cardinality has a witness")


def verify(value: object) -> bool:
    try:
        if not isinstance(value, dict):
            raise CertificateError("certificate is not an object")
        if value.get("schema") != CERTIFICATE_SCHEMA or value.get("campaign_id") != CAMPAIGN_ID:
            raise CertificateError("schema or campaign mismatch")
        if value.get("kind") != "evaluated_pair" or value.get("crossing") is not True:
            raise CertificateError("record is not a crossing")
        left = graph_from_identity(value.get("left"), connected=True)
        right = graph_from_identity(value.get("right"), connected=True)
        cartesian, direct = cartesian_product(left, right), direct_product(left, right)
        if graph_identity(cartesian) != value.get("cartesian"):
            raise CertificateError("Cartesian product differs")
        if graph_identity(direct) != value.get("direct"):
            raise CertificateError("direct product differs")

        cart, direct_record = value.get("cartesian_total_domination"), value.get("direct_domination")
        if not isinstance(cart, dict) or not isinstance(direct_record, dict):
            raise CertificateError("missing parameter records")
        k = cart.get("upper_bound")
        gamma = direct_record.get("value")
        if (not isinstance(k, int) or isinstance(k, bool) or not isinstance(gamma, int)
                or isinstance(gamma, bool) or not 1 <= k < gamma <= len(direct)):
            raise CertificateError("strict comparison is invalid")
        if cart.get("lower_bound") != lower_bound(cartesian, total=True):
            raise CertificateError("Cartesian lower bound differs")
        validate_witness(cartesian, cart.get("witness"), k, total=True)
        if direct_record.get("exact") is not True:
            raise CertificateError("direct value is not marked exact")
        if direct_record.get("lower_bound") != lower_bound(direct, total=False):
            raise CertificateError("direct lower bound differs")
        validate_witness(direct, direct_record.get("witness"), gamma, total=False)
        if gamma > direct_record["lower_bound"]:
            prove_absent(direct, gamma - 1, total=False)

        if cart.get("exact") is True and k > cart["lower_bound"]:
            prove_absent(cartesian, k - 1, total=True)
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
    if not verify(value):
        print("CERTIFICATE_INVALID")
        return 1
    print(f"CERTIFICATE_OK name={value['name']} cartesian_upper={value['cartesian_total_domination']['upper_bound']} direct_gamma={value['direct_domination']['value']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
