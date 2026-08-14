#!/usr/bin/env python3
"""Frozen DEVELOPMENT search for TxGraffiti Conjecture 3.

No floating-point arithmetic is used.  A crossing certificate contains a
total dominating set of size k in G square H and exhaustive subset checks
showing that G direct H has no dominating set of size k or k-1.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import random
import time
from typing import Iterable, Iterator, Sequence

import networkx as nx


CAMPAIGN_ID = "txgraffiti-product-conjecture-development-v1"
LEDGER_SCHEMA = "c5k4-txgraffiti-product-ledger-1.0"
TERMINAL_SCHEMA = "c5k4-txgraffiti-product-terminal-1.0"
CERTIFICATE_SCHEMA = "c5k4-txgraffiti-product-certificate-1.0"
INTERNAL_STOP_SECONDS = 54.0
ARMS = ("CATALOGUE", "GENERIC", "WALL_NAVIGATION")
TERMINAL_REASONS = {
    "CANDIDATE_FOUND", "DOMAIN_EXHAUSTED", "DEADLINE_PREFIX",
    "DB_SOURCE_GATE_FAILED", "CERTIFICATE_FAILED", "ERROR",
}
ATLAS_COUNTS = {2: 1, 3: 2, 4: 6, 5: 21, 6: 112, 7: 853}
ATLAS_SHA256 = "1cfb1c9688917d79dc59a9e9fc529af2780b9bceaa39f25bb61672c4ad4e72c3"


class SearchError(RuntimeError):
    pass


class DeadlineReached(RuntimeError):
    pass


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def labelled_graph6(graph: nx.Graph) -> str:
    ordered = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    return nx.to_graph6_bytes(ordered, header=False).decode().strip()


def identity(graph: nx.Graph) -> dict[str, object]:
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    edges = [[int(u), int(v)] for u, v in sorted((min(u, v), max(u, v)) for u, v in graph.edges())]
    raw = canonical_json({"n": graph.number_of_nodes(), "edges": edges})
    return {
        "n": graph.number_of_nodes(), "m": graph.number_of_edges(),
        "labelled_graph6": labelled_graph6(graph), "edge_list": edges,
        "labelled_identity_sha256": hashlib.sha256(raw).hexdigest(),
    }


def cartesian_product(left: nx.Graph, right: nx.Graph) -> nx.Graph:
    """Literal source definition: equality in one coordinate, edge in the other."""
    product = nx.Graph()
    product.add_nodes_from((u, v) for u in left for v in right)
    for u, v in product:
        product.add_edges_from(((u, v), (u, w)) for w in right.neighbors(v))
        product.add_edges_from(((u, v), (w, v)) for w in left.neighbors(u))
    return nx.convert_node_labels_to_integers(product, ordering="sorted")


def direct_product(left: nx.Graph, right: nx.Graph) -> nx.Graph:
    """Literal tensor/direct definition: an edge in both coordinates."""
    product = nx.Graph()
    product.add_nodes_from((u, v) for u in left for v in right)
    for u, v in product:
        product.add_edges_from(((u, v), (w, x)) for w in left.neighbors(u) for x in right.neighbors(v))
    return nx.convert_node_labels_to_integers(product, ordering="sorted")


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


def greedy_total_dominating_set(graph: nx.Graph) -> tuple[int, ...]:
    uncovered = set(graph.nodes())
    chosen: list[int] = []
    while uncovered:
        vertex = min(graph, key=lambda v: (-len(uncovered & set(graph.neighbors(v))), int(v)))
        gain = uncovered & set(graph.neighbors(vertex))
        if not gain:
            raise SearchError("Cartesian product unexpectedly has an isolated vertex")
        chosen.append(int(vertex))
        uncovered -= gain
    for vertex in tuple(reversed(chosen)):
        trial = [v for v in chosen if v != vertex]
        if totally_dominates(graph, trial):
            chosen = trial
    witness = tuple(sorted(chosen))
    if not totally_dominates(graph, witness):
        raise AssertionError("internal total-domination witness failure")
    return witness


def first_set_of_size_with_count(
    graph: nx.Graph,
    size: int,
    total: bool,
    deadline: float | None = None,
) -> tuple[tuple[int, ...] | None, int, int]:
    """Return the first witness, combinations examined, and total combinations."""
    if size < 0 or size > graph.number_of_nodes():
        return None, 0, 0
    predicate = totally_dominates if total else dominates
    total_subsets = math.comb(graph.number_of_nodes(), size)
    subsets_examined = 0
    for index, chosen in enumerate(itertools.combinations(sorted(graph), size)):
        if deadline is not None and index % 1024 == 0 and time.monotonic() >= deadline:
            raise DeadlineReached
        subsets_examined += 1
        if predicate(graph, chosen):
            return tuple(int(v) for v in chosen), subsets_examined, total_subsets
    return None, subsets_examined, total_subsets


def first_set_of_size(graph: nx.Graph, size: int, total: bool, deadline: float | None = None) -> tuple[int, ...] | None:
    witness, _, _ = first_set_of_size_with_count(graph, size, total, deadline)
    return witness


def absence_proof(graph: nx.Graph, size: int, deadline: float) -> dict[str, object]:
    witness, subsets_examined, total_subsets = first_set_of_size_with_count(
        graph, size, total=False, deadline=deadline
    )
    return {
        "size": size,
        "subsets_examined": subsets_examined,
        "total_subsets": total_subsets,
        "dominating_set_found": list(witness) if witness is not None else None,
        "complete": witness is None and subsets_examined == total_subsets,
    }


def exact_parameter(graph: nx.Graph, total: bool) -> int:
    for size in range(1, graph.number_of_nodes() + 1):
        if first_set_of_size(graph, size, total=total) is not None:
            return size
    raise SearchError("parameter undefined")


def atlas_graphs(max_order: int = 7) -> list[nx.Graph]:
    return [
        nx.convert_node_labels_to_integers(graph, ordering="sorted")
        for graph in nx.graph_atlas_g()
        if 2 <= graph.number_of_nodes() <= max_order and nx.is_connected(graph)
    ]


def database_source_gate(source_attestation: Path) -> dict[str, object]:
    attestation = json.loads(source_attestation.read_text())
    required = {
        "arxiv_id": "2409.19379v2", "source_revision_date": "2026-05-11",
        "conjecture_number": 3, "public_status": "OPEN_NO_PUBLIC_RESOLUTION_FOUND",
    }
    if any(attestation.get(key) != value for key, value in required.items()):
        raise SearchError("source/status attestation does not match the frozen v2 contract")
    graphs = atlas_graphs()
    counts = {n: sum(g.number_of_nodes() == n for g in graphs) for n in ATLAS_COUNTS}
    digest = hashlib.sha256(("\n".join(labelled_graph6(g) for g in graphs) + "\n").encode()).hexdigest()
    if counts != ATLAS_COUNTS or digest != ATLAS_SHA256:
        raise SearchError(f"Graph Atlas fingerprint mismatch: counts={counts}, sha256={digest}")

    k2, k3 = nx.complete_graph(2), nx.complete_graph(3)
    identities = {
        "K2_square_K2_is_C4": nx.is_isomorphic(cartesian_product(k2, k2), nx.cycle_graph(4)),
        "K2_direct_K2_is_2K2": nx.is_isomorphic(direct_product(k2, k2), nx.disjoint_union(nx.path_graph(2), nx.path_graph(2))),
        "K2_square_K3_is_triangular_prism": nx.is_isomorphic(cartesian_product(k2, k3), nx.circular_ladder_graph(3)),
        "K2_direct_K3_is_C6": nx.is_isomorphic(direct_product(k2, k3), nx.cycle_graph(6)),
    }
    if not all(identities.values()):
        raise SearchError(f"product identity gate failed: {identities}")
    parameters = {}
    for name, left, right in (("K2,K2", k2, k2), ("K2,K3", k2, k3)):
        cart, direct = cartesian_product(left, right), direct_product(left, right)
        parameters[name] = {"gamma_t_cartesian": exact_parameter(cart, True), "gamma_direct": exact_parameter(direct, False)}
    if parameters != {"K2,K2": {"gamma_t_cartesian": 2, "gamma_direct": 2}, "K2,K3": {"gamma_t_cartesian": 2, "gamma_direct": 2}}:
        raise SearchError(f"domination-definition gate failed: {parameters}")
    return {"atlas_counts": counts, "atlas_sha256": digest, "product_identities": identities, "known_parameters": parameters}


def named_graphs() -> list[tuple[str, nx.Graph]]:
    values: list[tuple[str, nx.Graph]] = []
    for n in range(2, 8):
        values.extend(((f"P{n}", nx.path_graph(n)), (f"K{n}", nx.complete_graph(n)), (f"K1,{n-1}", nx.star_graph(n - 1))))
        if n >= 3:
            values.append((f"C{n}", nx.cycle_graph(n)))
    return values


def catalogue_pairs() -> Iterator[tuple[str, nx.Graph, nx.Graph]]:
    small = atlas_graphs(5)
    small.sort(key=labelled_graph6)
    for i, left in enumerate(small):
        for j, right in enumerate(small[i:], start=i):
            if left.number_of_nodes() * right.number_of_nodes() <= 25:
                yield f"atlas:{i}:{j}", left, right
    named = named_graphs()
    for i, (left_name, left) in enumerate(named):
        for right_name, right in named[i:]:
            if left.number_of_nodes() * right.number_of_nodes() <= 36:
                yield f"named:{left_name}:{right_name}", left, right


def random_connected_graph(rng: random.Random, n: int, p: float) -> nx.Graph:
    graph = nx.random_labeled_tree(n, seed=rng.randrange(1 << 63))
    for u, v in itertools.combinations(range(n), 2):
        if not graph.has_edge(u, v) and rng.random() < p:
            graph.add_edge(u, v)
    return graph


def generic_pairs(seed: int = 320240919, count: int = 4000) -> Iterator[tuple[str, nx.Graph, nx.Graph]]:
    rng = random.Random(seed)
    probabilities = (0.0, 0.12, 0.28, 0.50, 0.75)
    for index in range(count):
        left_n = 2 + index % 5
        right_n = 2 + (index // 5) % 5
        left_p = probabilities[(index // 25) % len(probabilities)]
        right_p = probabilities[(index // 125) % len(probabilities)]
        yield (
            f"generic:{index}:{left_n}:{right_n}:{left_p}:{right_p}",
            random_connected_graph(rng, left_n, left_p), random_connected_graph(rng, right_n, right_p),
        )


def fixed_moves(graph: nx.Graph) -> Iterator[tuple[str, nx.Graph]]:
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    anchor = min(graph)
    new = graph.number_of_nodes()
    leaf = graph.copy(); leaf.add_edge(anchor, new)
    yield "leaf", leaf
    false_twin = graph.copy(); false_twin.add_node(new); false_twin.add_edges_from((new, v) for v in graph.neighbors(anchor))
    yield "false-twin", false_twin
    true_twin = false_twin.copy(); true_twin.add_edge(anchor, new)
    yield "true-twin", true_twin
    edge = min((min(u, v), max(u, v)) for u, v in graph.edges())
    subdivided = graph.copy(); subdivided.remove_edge(*edge); subdivided.add_edges_from(((edge[0], new), (new, edge[1])))
    yield "subdivision", subdivided
    parity = graph.copy(); parity.add_edges_from(((anchor, new), (new, new + 1)))
    yield "parity-path-2", parity


def wall_pairs() -> Iterator[tuple[str, nx.Graph, nx.Graph]]:
    seeds = (("K2,K2", nx.complete_graph(2), nx.complete_graph(2)), ("K2,K3", nx.complete_graph(2), nx.complete_graph(3)))
    for seed_name, left, right in seeds:
        yield f"tight:{seed_name}", left, right
        for move, changed in fixed_moves(left):
            yield f"tight:{seed_name}:left:{move}", changed, right
        for move, changed in fixed_moves(right):
            yield f"tight:{seed_name}:right:{move}", left, changed
        for left_move, changed_left in fixed_moves(left):
            for right_move, changed_right in fixed_moves(right):
                yield f"tight:{seed_name}:both:{left_move}:{right_move}", changed_left, changed_right


def proposals(arm: str) -> Iterable[tuple[str, nx.Graph, nx.Graph]]:
    return {"CATALOGUE": catalogue_pairs, "GENERIC": generic_pairs, "WALL_NAVIGATION": wall_pairs}[arm]()


@dataclass
class Ledger:
    path: Path
    previous: str = ""
    sequence: int = 0

    def append(self, row: dict[str, object]) -> None:
        payload = {"schema": LEDGER_SCHEMA, "campaign_id": CAMPAIGN_ID, "sequence": self.sequence, "previous_row_sha256": self.previous, **row}
        digest = hashlib.sha256(canonical_json(payload)).hexdigest()
        payload["row_sha256"] = digest
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("ab") as handle:
            handle.write(canonical_json(payload)); handle.flush(); os.fsync(handle.fileno())
        self.previous, self.sequence = digest, self.sequence + 1


def durable_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(canonical_json(value)); handle.flush(); os.fsync(handle.fileno())


def verify_certificate(value: dict[str, object]) -> bool:
    if value.get("schema") != CERTIFICATE_SCHEMA:
        return False
    left = nx.Graph(); left.add_nodes_from(range(value["left"]["n"])); left.add_edges_from(value["left"]["edge_list"])
    right = nx.Graph(); right.add_nodes_from(range(value["right"]["n"])); right.add_edges_from(value["right"]["edge_list"])
    cart, direct = cartesian_product(left, right), direct_product(left, right)
    witness, k = value["cartesian_total_dominating_set"], value["k"]
    return (
        len(witness) == k and totally_dominates(cart, witness)
        and first_set_of_size(direct, k - 1, total=False) is None
        and first_set_of_size(direct, k, total=False) is None
    )


def evaluate(name: str, left: nx.Graph, right: nx.Graph, deadline: float) -> dict[str, object]:
    left = nx.convert_node_labels_to_integers(left, ordering="sorted")
    right = nx.convert_node_labels_to_integers(right, ordering="sorted")
    if min(left.number_of_nodes(), right.number_of_nodes()) < 2 or not nx.is_connected(left) or not nx.is_connected(right):
        raise SearchError("proposal has an inapplicable factor")
    cart, direct = cartesian_product(left, right), direct_product(left, right)
    witness = greedy_total_dominating_set(cart)
    k = len(witness)
    proof_k = absence_proof(direct, k, deadline)
    row: dict[str, object] = {
        "kind": "evaluated_pair", "name": name, "left": identity(left), "right": identity(right),
        "cartesian": identity(cart), "direct": identity(direct),
        "cartesian_total_dominating_set": list(witness), "k": k,
        "no_direct_dominating_set_size_k": proof_k, "crossing": proof_k["complete"],
    }
    if proof_k["complete"]:
        row["no_direct_dominating_set_size_k_minus_1"] = absence_proof(direct, k - 1, deadline)
    return row


def write_terminal(path: Path, arm: str, reason: str, proposed: int, evaluated: int, ledger: Ledger) -> None:
    if reason not in TERMINAL_REASONS:
        raise SearchError("unsupported terminal reason")
    durable_json(path, {
        "schema": TERMINAL_SCHEMA, "campaign_id": CAMPAIGN_ID, "arm": arm,
        "terminal_reason": reason, "domain_exhausted": reason == "DOMAIN_EXHAUSTED",
        "proposed": proposed, "evaluated": evaluated, "ledger_rows": ledger.sequence,
        "last_row_sha256": ledger.previous,
    })


def run(arm: str, ledger_path: Path, terminal_path: Path, certificate_path: Path, source_attestation: Path, seconds: float) -> str:
    started, deadline = time.monotonic(), time.monotonic() + seconds
    ledger = Ledger(ledger_path)
    proposed = evaluated = 0
    try:
        gate = database_source_gate(source_attestation)
        ledger.append({"kind": "database_source_gate", "status": "PASS", **gate})
    except Exception as exc:
        ledger.append({"kind": "database_source_gate", "status": "FAIL", "detail": str(exc)})
        write_terminal(terminal_path, arm, "DB_SOURCE_GATE_FAILED", 0, 0, ledger)
        return "DB_SOURCE_GATE_FAILED"
    reason = "DOMAIN_EXHAUSTED"
    try:
        for name, left, right in proposals(arm):
            if time.monotonic() >= deadline:
                reason = "DEADLINE_PREFIX"; break
            proposed += 1
            row = evaluate(name, left, right, deadline)
            ledger.append(row); evaluated += 1
            if row["crossing"]:
                certificate = {"schema": CERTIFICATE_SCHEMA, "campaign_id": CAMPAIGN_ID, **row}
                if (
                    not totally_dominates(cartesian_product(left, right), certificate["cartesian_total_dominating_set"])
                    or not certificate["no_direct_dominating_set_size_k"]["complete"]
                    or not certificate["no_direct_dominating_set_size_k_minus_1"]["complete"]
                ):
                    reason = "CERTIFICATE_FAILED"; break
                durable_json(certificate_path, certificate)
                reason = "CANDIDATE_FOUND"; break
    except DeadlineReached:
        reason = "DEADLINE_PREFIX"
    except Exception as exc:
        ledger.append({"kind": "fatal_error", "detail": str(exc)})
        reason = "ERROR"
    ledger.append({"kind": "summary", "arm": arm, "terminal_reason": reason, "proposed": proposed, "evaluated": evaluated, "elapsed_millis": int((time.monotonic() - started) * 1000)})
    write_terminal(terminal_path, arm, reason, proposed, evaluated, ledger)
    return reason


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=ARMS, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--terminal", type=Path, required=True)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--source-attestation", type=Path, required=True)
    parser.add_argument("--internal-seconds", type=float, default=INTERNAL_STOP_SECONDS)
    args = parser.parse_args(argv)
    if any(path.exists() for path in (args.ledger, args.terminal, args.certificate)):
        parser.error("ledger, terminal, and certificate paths must not pre-exist")
    if not 1 <= args.internal_seconds <= INTERNAL_STOP_SECONDS:
        parser.error("internal deadline must be in [1,54]")
    reason = run(args.arm, args.ledger, args.terminal, args.certificate, args.source_attestation, args.internal_seconds)
    return 2 if reason in {"DB_SOURCE_GATE_FAILED", "CERTIFICATE_FAILED", "ERROR"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
