#!/usr/bin/env python3
"""Frozen three-arm development search for Graffiti³ Conjecture 2.

This worker is deliberately self-contained.  It certifies a crossing with an
explicit independent set and an outward dyadic upper bound on every radical
summand; floating point is never used to decide a verdict.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import time
from typing import Iterable, Iterator, Sequence

import networkx as nx


SCHEMA = "c5k4-graffiti3-conjecture2-ledger-1.0"
TERMINAL_SCHEMA = "c5k4-graffiti3-conjecture2-terminal-1.0"
INTERNAL_SECONDS = 54.0
RADICAL_BITS = 96
ARMS = ("CATALOGUE", "GENERIC", "WALL_NAVIGATION")
TERMINAL_REASONS = {
    "DOMAIN_EXHAUSTED", "DEADLINE_PREFIX", "CANDIDATE_FOUND", "DB_GATE_FAILED", "ERROR"
}


class SearchError(RuntimeError):
    """A frozen-contract or exact-evaluation failure."""


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def graph6(graph: nx.Graph) -> str:
    ordered = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    return nx.to_graph6_bytes(ordered, header=False).decode().strip()


def graph_digest(encoded: str) -> str:
    return hashlib.sha256((encoded + "\n").encode()).hexdigest()


class IsomorphismDeduplicator:
    """Exact in-memory isomorphism deduplication behind cheap invariant buckets."""

    def __init__(self) -> None:
        self._buckets: dict[tuple[object, ...], list[nx.Graph]] = {}

    @staticmethod
    def _key(graph: nx.Graph) -> tuple[object, ...]:
        return (
            graph.number_of_nodes(), graph.number_of_edges(),
            tuple(sorted(dict(graph.degree()).values())),
            nx.weisfeiler_lehman_graph_hash(graph),
        )

    def add_if_new(self, graph: nx.Graph) -> bool:
        bucket = self._buckets.setdefault(self._key(graph), [])
        if any(nx.is_isomorphic(graph, prior) for prior in bucket):
            return False
        bucket.append(graph.copy())
        return True


def d2_values(graph: nx.Graph) -> dict[int, int]:
    """Closed distance-two ball sizes; the source phrase includes distance zero."""
    values: dict[int, int] = {}
    for vertex in graph:
        lengths = nx.single_source_shortest_path_length(graph, vertex, cutoff=2)
        values[int(vertex)] = len(lengths)
    return values


def sqrt_dyadic_bounds(value: int, bits: int = RADICAL_BITS) -> tuple[Fraction, Fraction]:
    if value < 0 or bits < 1:
        raise ValueError("sqrt input/bits outside contract")
    scale = 1 << bits
    floor_scaled = math.isqrt(value * scale * scale)
    lower = Fraction(floor_scaled, scale)
    if floor_scaled * floor_scaled == value * scale * scale:
        return lower, lower
    return lower, Fraction(floor_scaled + 1, scale)


def rga2_bounds(graph: nx.Graph, bits: int = RADICAL_BITS) -> tuple[Fraction, Fraction, list[dict[str, object]]]:
    d2 = d2_values(graph)
    lower = Fraction(0)
    upper = Fraction(0)
    terms: list[dict[str, object]] = []
    for raw_u, raw_v in sorted((min(u, v), max(u, v)) for u, v in graph.edges()):
        u, v = int(raw_u), int(raw_v)
        a, b = d2[u], d2[v]
        root_lower, root_upper = sqrt_dyadic_bounds(a * b, bits)
        term_lower = Fraction(2, a + b) * root_lower
        term_upper = Fraction(2, a + b) * root_upper
        lower += term_lower
        upper += term_upper
        terms.append({
            "edge": [u, v], "d2": [a, b],
            "lower": [term_lower.numerator, term_lower.denominator],
            "upper": [term_upper.numerator, term_upper.denominator],
        })
    return lower, upper, terms


def _squarefree_part(value: int) -> tuple[int, int]:
    outside = 1
    remainder = value
    prime = 2
    while prime * prime <= remainder:
        exponent = 0
        while remainder % prime == 0:
            remainder //= prime
            exponent += 1
        outside *= prime ** (exponent // 2)
        if exponent % 2:
            pass
        prime += 1
    squarefree = value // (outside * outside)
    return outside, squarefree


def rga2_radical_normal_form(graph: nx.Graph) -> dict[int, Fraction]:
    d2 = d2_values(graph)
    form: dict[int, Fraction] = {}
    for u, v in graph.edges():
        outside, squarefree = _squarefree_part(d2[int(u)] * d2[int(v)])
        form[squarefree] = form.get(squarefree, Fraction(0)) + Fraction(
            2 * outside, d2[int(u)] + d2[int(v)]
        )
    return {key: value for key, value in form.items() if value}


def is_exact_integer(form: dict[int, Fraction], value: int) -> bool:
    return form.get(1, Fraction(0)) == value and all(
        coefficient == 0 for radicand, coefficient in form.items() if radicand != 1
    )


def exact_independent_set(graph: nx.Graph) -> tuple[int, ...]:
    nodes = tuple(sorted(int(v) for v in graph))
    for size in range(len(nodes), -1, -1):
        for subset in itertools.combinations(nodes, size):
            if all(not graph.has_edge(u, v) for u, v in itertools.combinations(subset, 2)):
                return subset
    raise AssertionError("empty set is always independent")


def greedy_independent_set(graph: nx.Graph) -> tuple[int, ...]:
    nodes = tuple(sorted(int(v) for v in graph))
    orders = [
        nodes,
        tuple(sorted(nodes, key=lambda v: (graph.degree(v), v))),
        tuple(sorted(nodes, key=lambda v: (-graph.degree(v), v))),
    ]
    best: tuple[int, ...] = ()
    for order in orders:
        chosen: list[int] = []
        blocked: set[int] = set()
        for vertex in order:
            if vertex not in blocked:
                chosen.append(vertex)
                blocked.add(vertex)
                blocked.update(int(v) for v in graph.neighbors(vertex))
        candidate = tuple(sorted(chosen))
        if len(candidate) > len(best) or (len(candidate) == len(best) and candidate < best):
            best = candidate
    return best


def star_name(graph: nx.Graph) -> str | None:
    n = graph.number_of_nodes()
    degrees = sorted(dict(graph.degree()).values())
    if n >= 2 and degrees == [1] * (n - 1) + [n - 1]:
        return f"K1,{n - 1}"
    return None


def database_gate() -> dict[str, object]:
    graphs = [
        nx.convert_node_labels_to_integers(g, ordering="sorted")
        for g in nx.graph_atlas_g()
        if 2 <= g.number_of_nodes() <= 7 and nx.is_connected(g)
    ]
    if len(graphs) != 995:
        raise SearchError(f"Atlas gate expected 995 graphs, got {len(graphs)}")
    equalities: list[str] = []
    for graph in graphs:
        independent = exact_independent_set(graph)
        lower, upper, _ = rga2_bounds(graph)
        if upper < len(independent):
            raise SearchError(f"Atlas gate violation at {graph6(graph)}")
        form = rga2_radical_normal_form(graph)
        if is_exact_integer(form, len(independent)):
            name = star_name(graph)
            if name is None:
                raise SearchError(f"unexpected Atlas equality at {graph6(graph)}")
            equalities.append(name)
        elif lower <= len(independent) <= upper:
            raise SearchError(f"Atlas interval cannot decide strict hold at {graph6(graph)}")
    expected = [f"K1,{m}" for m in range(1, 7)]
    if sorted(equalities, key=lambda x: int(x.split(",")[1])) != expected:
        raise SearchError(f"Atlas equality set mismatch: {equalities}")
    return {"graphs": 995, "violations": 0, "equalities": expected}


def catalogue_graphs() -> Iterator[tuple[str, nx.Graph, tuple[int, ...] | None]]:
    for n in range(8, 31):
        yield f"path:{n}", nx.path_graph(n), None
        yield f"cycle:{n}", nx.cycle_graph(n), None
        yield f"star:{n}", nx.star_graph(n - 1), tuple(range(1, n))
        if n >= 5:
            broom = nx.path_graph(n - 2)
            broom.add_edges_from(((0, n - 2), (0, n - 1)))
            yield f"broom:{n}", broom, None
        if n >= 6:
            left = max(1, (n - 2) // 2)
            right = n - 2 - left
            double = nx.Graph([(0, 1)])
            double.add_edges_from((0, 2 + i) for i in range(left))
            double.add_edges_from((1, 2 + left + i) for i in range(right))
            yield f"double-star:{left}:{right}", double, None
        if n % 2 == 0:
            base = nx.path_graph(n // 2)
            yield f"corona-path:{n}", nx.convert_node_labels_to_integers(nx.corona_product(base, nx.empty_graph(1))), None
    for arms in range(3, 11):
        for length in (2, 3):
            n = 1 + arms * length
            if n > 30:
                continue
            spider = nx.Graph()
            spider.add_node(0)
            next_vertex = 1
            for _ in range(arms):
                previous = 0
                for _ in range(length):
                    spider.add_edge(previous, next_vertex)
                    previous = next_vertex
                    next_vertex += 1
            yield f"spider:{arms}:{length}", spider, None
    for multiplicity in range(2, 7):
        clique_blowup = nx.lexicographic_product(nx.cycle_graph(5), nx.complete_graph(multiplicity))
        yield f"c5-clique-blowup:{multiplicity}", nx.convert_node_labels_to_integers(clique_blowup), None
        independent_blowup = nx.lexicographic_product(nx.cycle_graph(5), nx.empty_graph(multiplicity))
        yield f"c5-independent-blowup:{multiplicity}", nx.convert_node_labels_to_integers(independent_blowup), None
    for clique in range(2, 9):
        for independent in range(2, 23):
            if clique + independent > 30:
                continue
            graph = nx.complete_graph(clique)
            graph.add_nodes_from(range(clique, clique + independent))
            graph.add_edges_from((u, v) for u in range(clique) for v in range(clique, clique + independent))
            yield f"split:{clique}:{independent}", graph, tuple(range(clique, clique + independent))


def generic_graphs(seed: int = 320260119, count: int = 6000) -> Iterator[tuple[str, nx.Graph, None]]:
    rng = random.Random(seed)
    probabilities = (0.10, 0.18, 0.30, 0.50, 0.72)
    for index in range(count):
        n = 8 + index % 23
        p = probabilities[(index // 23) % len(probabilities)]
        graph_seed = rng.randrange(1 << 63)
        graph = nx.gnp_random_graph(n, p, seed=graph_seed)
        if not nx.is_connected(graph):
            components = sorted((sorted(c) for c in nx.connected_components(graph)), key=lambda c: c[0])
            for left, right in zip(components, components[1:]):
                graph.add_edge(left[0], right[0])
        yield f"gnp:{index}:{n}:{p}:{graph_seed}", graph, None


def wall_graphs() -> Iterator[tuple[str, nx.Graph, tuple[int, ...] | None]]:
    for leaves in range(2, 30):
        star = nx.star_graph(leaves)
        yield f"wall-star:{leaves}", star, tuple(range(1, leaves + 1))
        for leaf in range(1, min(leaves, 5) + 1):
            subdivided = star.copy()
            subdivided.remove_edge(0, leaf)
            new = leaves + 1
            subdivided.add_edges_from(((0, new), (new, leaf)))
            witness = tuple(v for v in range(1, leaves + 1))
            yield f"wall-subdivide:{leaves}:{leaf}", subdivided, witness
        if leaves >= 3:
            split = nx.Graph()
            split.add_nodes_from(range(leaves + 2))
            split.add_edge(0, 1)
            cut = leaves // 2
            split.add_edges_from((0, 2 + i) for i in range(cut))
            split.add_edges_from((1, 2 + i) for i in range(cut, leaves))
            yield f"wall-hub-split:{leaves}", split, tuple(range(2, leaves + 2))
        cloned = star.copy()
        cloned.add_node(leaves + 1)
        cloned.add_edge(0, leaves + 1)
        yield f"wall-leaf-clone:{leaves}", cloned, tuple(range(1, leaves + 2))
        for u in range(1, min(leaves, 5) + 1):
            for v in range(u + 1, min(leaves, 6) + 1):
                branch = star.copy()
                branch.add_edge(u, v)
                witness = tuple(x for x in range(1, leaves + 1) if x != v)
                yield f"wall-branch-edge:{leaves}:{u}:{v}", branch, witness


def proposal_stream(arm: str) -> Iterable[tuple[str, nx.Graph, tuple[int, ...] | None]]:
    if arm == "CATALOGUE":
        return catalogue_graphs()
    if arm == "GENERIC":
        return generic_graphs()
    if arm == "WALL_NAVIGATION":
        return wall_graphs()
    raise SearchError(f"unsupported arm: {arm}")


@dataclass
class Ledger:
    path: Path
    previous: str = ""
    sequence: int = 0

    def append(self, row: dict[str, object]) -> None:
        payload = {"schema": SCHEMA, "sequence": self.sequence, "previous_row_sha256": self.previous, **row}
        raw_without_hash = canonical_json(payload)
        digest = hashlib.sha256(raw_without_hash).hexdigest()
        payload["row_sha256"] = digest
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("ab") as handle:
            handle.write(canonical_json(payload))
            handle.flush()
            import os
            os.fsync(handle.fileno())
        self.previous = digest
        self.sequence += 1


def validate_witness(graph: nx.Graph, witness: Sequence[int]) -> None:
    if len(set(witness)) != len(witness) or any(v not in graph for v in witness):
        raise SearchError("independent-set witness has invalid vertices")
    if any(graph.has_edge(u, v) for u, v in itertools.combinations(witness, 2)):
        raise SearchError("claimed independent-set witness is not independent")


def write_terminal(path: Path, arm: str, reason: str, proposed: int, unique: int, evaluated: int) -> None:
    if reason not in TERMINAL_REASONS:
        raise SearchError("invalid terminal reason")
    value = {
        "schema": TERMINAL_SCHEMA, "arm": arm, "terminal_reason": reason,
        "proposed": proposed, "canonical_unique": unique, "evaluated": evaluated,
        "domain_exhausted": reason == "DOMAIN_EXHAUSTED",
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json(value))


def run(arm: str, output: Path, terminal: Path, seconds: float = INTERNAL_SECONDS) -> str:
    started = time.monotonic()
    ledger = Ledger(output)
    try:
        gate = database_gate()
    except Exception as exc:
        ledger.append({"kind": "database_gate", "status": "FAIL", "detail": str(exc)})
        write_terminal(terminal, arm, "DB_GATE_FAILED", 0, 0, 0)
        return "DB_GATE_FAILED"
    ledger.append({"kind": "database_gate", "status": "PASS", **gate})
    proposed = unique = evaluated = 0
    deduplicator = IsomorphismDeduplicator()
    reason = "DOMAIN_EXHAUSTED"
    try:
        for name, raw_graph, supplied in proposal_stream(arm):
            if time.monotonic() - started >= seconds:
                reason = "DEADLINE_PREFIX"
                break
            proposed += 1
            graph = nx.convert_node_labels_to_integers(raw_graph, ordering="sorted")
            if graph.number_of_nodes() < 2 or not nx.is_connected(graph) or nx.number_of_selfloops(graph):
                raise SearchError(f"constructor emitted inapplicable graph: {name}")
            encoded = graph6(graph)
            digest = graph_digest(encoded)
            if not deduplicator.add_if_new(graph):
                continue
            unique += 1
            witness = tuple(supplied) if supplied is not None else greedy_independent_set(graph)
            validate_witness(graph, witness)
            lower, upper, terms = rga2_bounds(graph)
            crossing = upper < len(witness)
            row: dict[str, object] = {
                "kind": "evaluated_candidate", "arm": arm, "name": name,
                "representative_graph6": encoded, "representative_sha256": digest,
                "n": graph.number_of_nodes(), "m": graph.number_of_edges(),
                "independent_set": list(witness), "independent_set_size": len(witness),
                "rga2_lower": [lower.numerator, lower.denominator],
                "rga2_upper": [upper.numerator, upper.denominator],
                "residual_upper_minus_independent": [
                    (upper - len(witness)).numerator, (upper - len(witness)).denominator
                ],
                "d2": d2_values(graph), "crossing": crossing,
            }
            if crossing:
                row["radical_term_certificates"] = terms
            ledger.append(row)
            evaluated += 1
            if crossing:
                reason = "CANDIDATE_FOUND"
                break
    except Exception as exc:
        reason = "ERROR"
        ledger.append({
            "kind": "fatal_error", "arm": arm, "detail": str(exc),
            "proposed": proposed, "canonical_unique": unique, "evaluated": evaluated,
        })
    ledger.append({
        "kind": "summary", "arm": arm, "terminal_reason": reason,
        "proposed": proposed, "canonical_unique": unique, "evaluated": evaluated,
    })
    write_terminal(terminal, arm, reason, proposed, unique, evaluated)
    return reason


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=ARMS, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--terminal", type=Path, required=True)
    parser.add_argument("--internal-seconds", type=float, default=INTERNAL_SECONDS)
    args = parser.parse_args(argv)
    if args.output.exists() or args.terminal.exists():
        parser.error("output and terminal paths must not pre-exist")
    if not 1 <= args.internal_seconds <= INTERNAL_SECONDS:
        parser.error(f"internal seconds must be in [1,{INTERNAL_SECONDS}]")
    try:
        run(args.arm, args.output, args.terminal, args.internal_seconds)
    except Exception as exc:
        if not args.output.exists():
            Ledger(args.output).append({"kind": "fatal_error", "detail": str(exc)})
        write_terminal(args.terminal, args.arm, "ERROR", 0, 0, 0)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
