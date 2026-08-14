#!/usr/bin/env python3
"""Frozen DEVELOPMENT v2 search for TxGraffiti Conjecture 3.

The v1 greedy Cartesian witness is replaced by monotone exact-size descent.
Every hard fixed-cardinality decision has its own four-second cap.  The direct
product parameter is admitted only when its exact value has been certified.
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
from typing import Callable, Iterable, Iterator, Sequence

import networkx as nx


CAMPAIGN_ID = "txgraffiti-product-conjecture-development-v2"
LEDGER_SCHEMA = "c5k4-txgraffiti-product-v2-ledger-1.0"
TERMINAL_SCHEMA = "c5k4-txgraffiti-product-v2-terminal-1.0"
CERTIFICATE_SCHEMA = "c5k4-txgraffiti-product-v2-certificate-1.0"
INTERNAL_STOP_SECONDS = 54.0
SUBPROBLEM_SECONDS = 4.0
ARMS = ("CATALOGUE", "GENERIC", "WALL_NAVIGATION")
TERMINAL_REASONS = {
    "CANDIDATE_FOUND", "DOMAIN_EXHAUSTED", "DEADLINE_PREFIX",
    "DB_SOURCE_GATE_FAILED", "CERTIFICATE_FAILED", "ERROR",
}
ATLAS_COUNTS = {2: 1, 3: 2, 4: 6, 5: 21, 6: 112, 7: 853}
ATLAS_SHA256 = "1cfb1c9688917d79dc59a9e9fc529af2780b9bceaa39f25bb61672c4ad4e72c3"


class SearchError(RuntimeError):
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
    product = nx.Graph()
    product.add_nodes_from((u, v) for u in left for v in right)
    for u, v in tuple(product):
        product.add_edges_from(((u, v), (u, x)) for x in right.neighbors(v))
        product.add_edges_from(((u, v), (x, v)) for x in left.neighbors(u))
    return nx.convert_node_labels_to_integers(product, ordering="sorted")


def direct_product(left: nx.Graph, right: nx.Graph) -> nx.Graph:
    product = nx.Graph()
    product.add_nodes_from((u, v) for u in left for v in right)
    for u, v in tuple(product):
        product.add_edges_from(
            ((x, y), (u, v)) for x in left.neighbors(u) for y in right.neighbors(v)
        )
    return nx.convert_node_labels_to_integers(product, ordering="sorted")


def coverage_masks(graph: nx.Graph, total: bool) -> tuple[list[int], int]:
    vertices = sorted(graph)
    if vertices != list(range(len(vertices))):
        raise SearchError("coverage masks require consecutive integer labels")
    masks: list[int] = []
    for vertex in vertices:
        mask = 0 if total else 1 << vertex
        for neighbor in graph.neighbors(vertex):
            mask |= 1 << int(neighbor)
        masks.append(mask)
    return masks, (1 << len(vertices)) - 1


def covers(masks: Sequence[int], full: int, chosen: Sequence[int]) -> bool:
    covered = 0
    for vertex in chosen:
        covered |= masks[vertex]
    return covered == full


def greedy_total_dominating_set(graph: nx.Graph) -> tuple[int, ...]:
    masks, full = coverage_masks(graph, total=True)
    covered = 0
    chosen: list[int] = []
    while covered != full:
        vertex = min(
            range(len(masks)),
            key=lambda v: (-(bin(masks[v] & ~covered).count("1")), v),
        )
        if masks[vertex] & ~covered == 0:
            raise SearchError("Cartesian product unexpectedly has an isolated vertex")
        chosen.append(vertex)
        covered |= masks[vertex]
    for vertex in tuple(reversed(chosen)):
        trial = [v for v in chosen if v != vertex]
        if covers(masks, full, trial):
            chosen = trial
    return tuple(sorted(chosen))


def cardinality_lower_bound(graph: nx.Graph, total: bool) -> int:
    maximum = max(dict(graph.degree()).values())
    denominator = maximum if total else maximum + 1
    if denominator <= 0:
        raise SearchError("parameter undefined on graph with no covering neighborhood")
    return max(1, math.ceil(graph.number_of_nodes() / denominator))


def fixed_size_decision(
    graph: nx.Graph,
    size: int,
    total: bool,
    global_deadline: float,
    subproblem_seconds: float = SUBPROBLEM_SECONDS,
) -> dict[str, object]:
    """Decide one cardinality by literal exhaustive enumeration or time out."""
    if not 0 < subproblem_seconds <= SUBPROBLEM_SECONDS:
        raise SearchError("hard-subproblem cap must be in (0,4]")
    masks, full = coverage_masks(graph, total=total)
    order = len(masks)
    total_subsets = math.comb(order, size) if 0 <= size <= order else 0
    local_deadline = min(global_deadline, time.monotonic() + subproblem_seconds)
    examined = 0
    for index, chosen in enumerate(itertools.combinations(range(order), size)):
        if index % 256 == 0 and time.monotonic() >= local_deadline:
            return {
                "status": "TIMEOUT", "size": size, "total": total,
                "subsets_examined": examined, "total_subsets": total_subsets,
                "witness": None, "complete": False,
            }
        examined += 1
        if covers(masks, full, chosen):
            return {
                "status": "WITNESS", "size": size, "total": total,
                "subsets_examined": examined, "total_subsets": total_subsets,
                "witness": list(chosen), "complete": False,
            }
    return {
        "status": "ABSENT", "size": size, "total": total,
        "subsets_examined": examined, "total_subsets": total_subsets,
        "witness": None, "complete": examined == total_subsets,
    }


SubproblemSink = Callable[[dict[str, object]], None]


def descend_cartesian_upper_bound(
    graph: nx.Graph,
    deadline: float,
    sink: SubproblemSink,
) -> dict[str, object]:
    witness = greedy_total_dominating_set(graph)
    upper = len(witness)
    lower = cardinality_lower_bound(graph, total=True)
    steps: list[dict[str, object]] = []
    exact = upper == lower
    while not exact and upper > lower:
        receipt = fixed_size_decision(graph, upper - 1, True, deadline)
        steps.append(receipt)
        sink({"kind": "cartesian_descent_subproblem", **receipt})
        if receipt["status"] == "WITNESS":
            witness = tuple(receipt["witness"])
            upper -= 1
        elif receipt["status"] == "ABSENT":
            exact = True
        else:
            break
    return {
        "upper_bound": upper, "witness": list(witness), "lower_bound": lower,
        "exact": exact, "steps": steps,
    }


def exact_direct_domination(
    graph: nx.Graph,
    deadline: float,
    sink: SubproblemSink,
) -> dict[str, object]:
    lower = cardinality_lower_bound(graph, total=False)
    steps: list[dict[str, object]] = []
    for size in range(lower, graph.number_of_nodes() + 1):
        receipt = fixed_size_decision(graph, size, False, deadline)
        steps.append(receipt)
        sink({"kind": "direct_exact_subproblem", **receipt})
        if receipt["status"] == "WITNESS":
            return {
                "lower_bound": lower, "exact": True, "value": size,
                "witness": receipt["witness"], "steps": steps,
            }
        if receipt["status"] == "TIMEOUT":
            return {
                "lower_bound": lower, "exact": False, "value": None,
                "witness": None, "steps": steps,
            }
    raise SearchError("direct-product domination parameter was not found")


def exact_parameter_tiny(graph: nx.Graph, total: bool) -> int:
    masks, full = coverage_masks(graph, total=total)
    for size in range(1, len(masks) + 1):
        if any(covers(masks, full, chosen) for chosen in itertools.combinations(range(len(masks)), size)):
            return size
    raise SearchError("tiny exact parameter undefined")


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
        raise SearchError("source/status attestation differs from frozen source")
    graphs = atlas_graphs()
    counts = {n: sum(g.number_of_nodes() == n for g in graphs) for n in ATLAS_COUNTS}
    digest = hashlib.sha256(("\n".join(labelled_graph6(g) for g in graphs) + "\n").encode()).hexdigest()
    if counts != ATLAS_COUNTS or digest != ATLAS_SHA256:
        raise SearchError(f"Graph Atlas gate failed: counts={counts}, sha256={digest}")
    k2, k3 = nx.complete_graph(2), nx.complete_graph(3)
    product_checks = {
        "K2_square_K2_is_C4": nx.is_isomorphic(cartesian_product(k2, k2), nx.cycle_graph(4)),
        "K2_direct_K2_is_2K2": nx.is_isomorphic(
            direct_product(k2, k2), nx.disjoint_union(nx.path_graph(2), nx.path_graph(2))
        ),
        "K2_square_K3_is_triangular_prism": nx.is_isomorphic(
            cartesian_product(k2, k3), nx.circular_ladder_graph(3)
        ),
        "K2_direct_K3_is_C6": nx.is_isomorphic(direct_product(k2, k3), nx.cycle_graph(6)),
    }
    if not all(product_checks.values()):
        raise SearchError(f"product-definition gate failed: {product_checks}")
    parameters: dict[str, object] = {}
    for name, left, right in (("K2,K2", k2, k2), ("K2,K3", k2, k3)):
        parameters[name] = {
            "gamma_t_cartesian": exact_parameter_tiny(cartesian_product(left, right), True),
            "gamma_direct": exact_parameter_tiny(direct_product(left, right), False),
        }
    expected = {
        "K2,K2": {"gamma_t_cartesian": 2, "gamma_direct": 2},
        "K2,K3": {"gamma_t_cartesian": 2, "gamma_direct": 2},
    }
    if parameters != expected:
        raise SearchError(f"parameter-definition gate failed: {parameters}")
    return {
        "atlas_counts": counts, "atlas_sha256": digest,
        "product_identities": product_checks, "known_parameters": parameters,
    }


def named_graph(name: str) -> nx.Graph:
    kind, order_text = name[0], name[1:]
    order = int(order_text)
    if kind == "P":
        return nx.path_graph(order)
    if kind == "C":
        return nx.cycle_graph(order)
    if kind == "K":
        return nx.complete_graph(order)
    if kind == "S":
        return nx.star_graph(order - 1)
    raise SearchError(f"unknown named graph {name}")


CURATED_NAMED_PAIRS = (
    ("K2", "P5"), ("K2", "P6"), ("K2", "C4"), ("K2", "C5"),
    ("K2", "C6"), ("K2", "S5"), ("K2", "S6"), ("K2", "K4"),
    ("K2", "K5"), ("K3", "P3"), ("K3", "P4"), ("K3", "C4"),
    ("K3", "C5"), ("K3", "S4"), ("K3", "S5"), ("P3", "P3"),
    ("P3", "P4"), ("P3", "C4"), ("P4", "P4"), ("P4", "C4"),
    ("C4", "C4"), ("C4", "S4"), ("S4", "S4"), ("S4", "S5"),
)


def catalogue_pairs() -> Iterator[tuple[str, nx.Graph, nx.Graph]]:
    small = atlas_graphs(4)
    small.sort(key=labelled_graph6)
    for i, left in enumerate(small):
        for j, right in enumerate(small[i:], start=i):
            yield f"atlas-small:{i}:{j}", left, right
    for left_name, right_name in CURATED_NAMED_PAIRS:
        yield f"named:{left_name}:{right_name}", named_graph(left_name), named_graph(right_name)


def random_connected_graph(rng: random.Random, order: int, probability: float) -> nx.Graph:
    graph = nx.random_labeled_tree(order, seed=rng.randrange(1 << 63))
    for u, v in itertools.combinations(range(order), 2):
        if not graph.has_edge(u, v) and rng.random() < probability:
            graph.add_edge(u, v)
    return graph


def generic_pairs(seed: int = 820240919, count: int = 192) -> Iterator[tuple[str, nx.Graph, nx.Graph]]:
    rng = random.Random(seed)
    probabilities = (0.0, 0.18, 0.42, 0.68)
    for index in range(count):
        left_n = 2 + index % 4
        right_n = 2 + (index // 4) % 4
        left_p = probabilities[(index // 16) % 4]
        right_p = probabilities[(index // 64) % 4]
        yield (
            f"generic-v2:{index}:{left_n}:{right_n}:{left_p}:{right_p}",
            random_connected_graph(rng, left_n, left_p),
            random_connected_graph(rng, right_n, right_p),
        )


def fixed_moves(graph: nx.Graph) -> Iterator[tuple[str, nx.Graph]]:
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    anchor, new = min(graph), graph.number_of_nodes()
    leaf = graph.copy(); leaf.add_edge(anchor, new)
    yield "leaf", leaf
    false_twin = graph.copy(); false_twin.add_node(new)
    false_twin.add_edges_from((new, v) for v in graph.neighbors(anchor))
    yield "false-twin", false_twin
    true_twin = false_twin.copy(); true_twin.add_edge(anchor, new)
    yield "true-twin", true_twin
    edge = min((min(u, v), max(u, v)) for u, v in graph.edges())
    subdivision = graph.copy(); subdivision.remove_edge(*edge)
    subdivision.add_edges_from(((edge[0], new), (new, edge[1])))
    yield "subdivision", subdivision
    parity = graph.copy(); parity.add_edges_from(((anchor, new), (new, new + 1)))
    yield "parity-path-2", parity


def wall_pairs() -> Iterator[tuple[str, nx.Graph, nx.Graph]]:
    seeds = (("K2,K2", nx.complete_graph(2), nx.complete_graph(2)),
             ("K2,K3", nx.complete_graph(2), nx.complete_graph(3)))
    for seed_name, left, right in seeds:
        yield f"wall-v2:{seed_name}", left, right
        left_moves, right_moves = list(fixed_moves(left)), list(fixed_moves(right))
        for move, changed in left_moves:
            yield f"wall-v2:{seed_name}:left:{move}", changed, right
        for move, changed in right_moves:
            yield f"wall-v2:{seed_name}:right:{move}", left, changed
        for (move, changed_left), (_, changed_right) in zip(left_moves, right_moves):
            yield f"wall-v2:{seed_name}:matched:{move}", changed_left, changed_right


def proposals(arm: str) -> Iterable[tuple[str, nx.Graph, nx.Graph]]:
    return {"CATALOGUE": catalogue_pairs, "GENERIC": generic_pairs,
            "WALL_NAVIGATION": wall_pairs}[arm]()


@dataclass
class Ledger:
    path: Path
    previous: str = ""
    sequence: int = 0

    def append(self, row: dict[str, object]) -> None:
        payload = {
            "schema": LEDGER_SCHEMA, "campaign_id": CAMPAIGN_ID,
            "sequence": self.sequence, "previous_row_sha256": self.previous, **row,
        }
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


def evaluate(name: str, left: nx.Graph, right: nx.Graph, deadline: float, ledger: Ledger) -> dict[str, object]:
    left = nx.convert_node_labels_to_integers(left, ordering="sorted")
    right = nx.convert_node_labels_to_integers(right, ordering="sorted")
    if min(len(left), len(right)) < 2 or not nx.is_connected(left) or not nx.is_connected(right):
        raise SearchError("proposal factors must be connected and have order at least two")
    cartesian, direct = cartesian_product(left, right), direct_product(left, right)
    ledger.append({
        "kind": "pair_start", "pair_name": name,
        "left": identity(left), "right": identity(right),
        "cartesian": identity(cartesian), "direct": identity(direct),
    })
    context = {"pair_name": name}
    cart = descend_cartesian_upper_bound(
        cartesian, deadline, lambda row: ledger.append({**context, **row})
    )
    direct_exact = exact_direct_domination(
        direct, deadline, lambda row: ledger.append({**context, **row})
    )
    crossing = bool(direct_exact["exact"] and direct_exact["value"] > cart["upper_bound"])
    return {
        "kind": "evaluated_pair", "name": name,
        "left": identity(left), "right": identity(right),
        "cartesian": identity(cartesian), "direct": identity(direct),
        "cartesian_total_domination": cart,
        "direct_domination": direct_exact,
        "crossing": crossing,
    }


def verify_candidate_shape(value: dict[str, object]) -> bool:
    cart = value["cartesian_total_domination"]
    direct = value["direct_domination"]
    return bool(
        value.get("crossing") is True
        and direct.get("exact") is True
        and isinstance(direct.get("value"), int)
        and direct["value"] > cart["upper_bound"]
        and len(cart["witness"]) == cart["upper_bound"]
    )


def write_terminal(path: Path, arm: str, reason: str, proposed: int, evaluated: int, ledger: Ledger) -> None:
    if reason not in TERMINAL_REASONS:
        raise SearchError("unsupported terminal reason")
    durable_json(path, {
        "schema": TERMINAL_SCHEMA, "campaign_id": CAMPAIGN_ID, "arm": arm,
        "terminal_reason": reason, "domain_exhausted": reason == "DOMAIN_EXHAUSTED",
        "proposed": proposed, "evaluated": evaluated, "ledger_rows": ledger.sequence,
        "last_row_sha256": ledger.previous,
    })


def run(
    arm: str, ledger_path: Path, terminal_path: Path, certificate_path: Path,
    source_attestation: Path, seconds: float,
) -> str:
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
            row = evaluate(name, left, right, deadline, ledger)
            ledger.append(row); evaluated += 1
            if row["crossing"]:
                certificate = {"schema": CERTIFICATE_SCHEMA, "campaign_id": CAMPAIGN_ID, **row}
                if not verify_candidate_shape(certificate):
                    reason = "CERTIFICATE_FAILED"; break
                durable_json(certificate_path, certificate)
                reason = "CANDIDATE_FOUND"; break
            if time.monotonic() >= deadline:
                reason = "DEADLINE_PREFIX"; break
    except Exception as exc:
        ledger.append({"kind": "fatal_error", "detail": str(exc)})
        reason = "ERROR"
    ledger.append({
        "kind": "summary", "arm": arm, "terminal_reason": reason,
        "proposed": proposed, "evaluated": evaluated,
        "elapsed_millis": int((time.monotonic() - started) * 1000),
    })
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
    reason = run(
        args.arm, args.ledger, args.terminal, args.certificate,
        args.source_attestation, args.internal_seconds,
    )
    return 2 if reason in {"DB_SOURCE_GATE_FAILED", "CERTIFICATE_FAILED", "ERROR"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
