#!/usr/bin/env python3
"""Frozen DEVELOPMENT worker for DOI-qualified Graffiti3 energy Conjecture 3.

The primary reading uses the literal closed distance-at-most-two ball.  The
published table's center-excluding reading is retained as a rejected reading:
K2 and K3 already refute it.  Floating point is used only for guarded screening;
any candidate must carry rational radical bounds and Sturm-isolated adjacency
eigenvalues before it can be written to the ledger as CANDIDATE_FOUND.
"""

from __future__ import annotations

import argparse
import csv
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import random
import time
from typing import Iterable, Iterator

import networkx as nx
import numpy as np


CAMPAIGN = "graffiti3-energy-c3-development-v1"
DOI = "10.21203/rs.3.rs-8493329/v1"
SCHEMA = "c5k4-graffiti3-energy-c3-ledger-1.0"
TERMINAL_SCHEMA = "c5k4-graffiti3-energy-c3-terminal-1.0"
INTERNAL_SECONDS = 54.0
RADICAL_BITS = 96
SOURCE_COMMIT = "e37126da53b84150d142a5d61202b61f78521fcc"
SOURCE_CSV_SHA256 = "4f455fbfe1149c2ca952b429c7ca9d9c1aae192309fbb642be2b12a345526e97"
SOURCE_ROWS = 335
SOURCE_ELIGIBLE_ROWS = 97
SOURCE_EQUALITY_IDS = (19, 33, 52, 65, 75, 159, 172, 174, 263)
ARMS = ("CATALOGUE", "GENERIC", "WALL_NAVIGATION")


class ContractError(RuntimeError):
    """The frozen source, gate, or serialization contract was not met."""


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def frac_pair(value: Fraction) -> list[int]:
    return [value.numerator, value.denominator]


def graph6(graph: nx.Graph) -> str:
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    return nx.to_graph6_bytes(graph, header=False).decode().strip()


def normalized_graph(graph: nx.Graph) -> nx.Graph:
    return nx.convert_node_labels_to_integers(nx.Graph(graph), ordering="sorted")


def edge_list(graph: nx.Graph) -> list[list[int]]:
    return [[int(min(u, v)), int(max(u, v))] for u, v in sorted(
        (min(int(a), int(b)), max(int(a), int(b))) for a, b in graph.edges()
    )]


class ChainedLedger:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = path.open("ab", buffering=0)
        self.previous = "0" * 64
        self.count = 0

    def append(self, payload: dict[str, object]) -> str:
        record = dict(payload)
        record.update({"schema": SCHEMA, "sequence": self.count, "previous_hash": self.previous})
        record_hash = hashlib.sha256(canonical_bytes(record)).hexdigest()
        record["record_hash"] = record_hash
        self.handle.write(canonical_bytes(record))
        self.handle.flush()
        os.fsync(self.handle.fileno())
        self.previous = record_hash
        self.count += 1
        return record_hash

    def close(self) -> None:
        self.handle.close()


def write_fsync_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = canonical_bytes(value)
    with path.open("wb", buffering=0) as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())


def d2_values(graph: nx.Graph, *, include_center: bool) -> dict[int, int]:
    result: dict[int, int] = {}
    for vertex in graph:
        value = len(nx.single_source_shortest_path_length(graph, vertex, cutoff=2))
        if not include_center:
            value -= 1
        if value <= 0:
            raise ContractError("nonpositive 2-degree")
        result[int(vertex)] = value
    return result


def sqrt_dyadic_bounds(value: int, bits: int = RADICAL_BITS) -> tuple[Fraction, Fraction]:
    scale = 1 << bits
    floor_scaled = math.isqrt(value * scale * scale)
    lower = Fraction(floor_scaled, scale)
    if floor_scaled * floor_scaled == value * scale * scale:
        return lower, lower
    return lower, Fraction(floor_scaled + 1, scale)


def reciprocal_sum_bounds(
    graph: nx.Graph, *, include_center: bool, bits: int = RADICAL_BITS
) -> tuple[Fraction, Fraction, list[dict[str, object]]]:
    d2 = d2_values(graph, include_center=include_center)
    lower, upper = Fraction(0), Fraction(0)
    terms: list[dict[str, object]] = []
    for u, v in sorted((min(int(a), int(b)), max(int(a), int(b))) for a, b in graph.edges()):
        root_lower, root_upper = sqrt_dyadic_bounds(d2[u] * d2[v], bits)
        term_lower = Fraction(1, 1) / root_upper
        term_upper = Fraction(1, 1) / root_lower
        lower += 3 * term_lower
        upper += 3 * term_upper
        terms.append({
            "edge": [u, v], "d2": [d2[u], d2[v]],
            "lower": frac_pair(3 * term_lower), "upper": frac_pair(3 * term_upper),
        })
    return lower, upper, terms


def numerical_energy(graph: nx.Graph) -> float:
    matrix = nx.to_numpy_array(graph, nodelist=sorted(graph), dtype=float)
    return float(np.abs(np.linalg.eigvalsh(matrix)).sum())


def nearest_half_up(value: float) -> int:
    return math.floor(value + 0.5)


def source_calibration(source_csv: Path) -> dict[str, object]:
    if sha256_file(source_csv) != SOURCE_CSV_SHA256:
        raise ContractError("source CSV hash differs from frozen blob")
    with source_csv.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != SOURCE_ROWS:
        raise ContractError(f"source row count {len(rows)} != {SOURCE_ROWS}")
    required = {
        "", "order", "size", "diameter", "graph_energy",
        "reciprocal_randic_index_2_degree",
        "a connected and planar graph with diameter at most 3",
    }
    if not rows or not required.issubset(rows[0]):
        raise ContractError("source CSV lacks frozen columns")
    eligible: list[dict[str, str]] = [
        row for row in rows
        if row["a connected and planar graph with diameter at most 3"] == "True"
    ]
    if len(eligible) != SOURCE_ELIGIBLE_ROWS:
        raise ContractError("source eligible-row count changed")
    violations: list[int] = []
    equalities: list[int] = []
    for row in eligible:
        rounded_energy = Fraction(row["graph_energy"])
        rhs = 3 * Fraction(row["reciprocal_randic_index_2_degree"])
        index = int(row[""])
        # Decimal source columns are calibration evidence, never proof evidence.
        gap = float(rounded_energy - rhs)
        if gap < -1e-9:
            violations.append(index)
        if abs(gap) <= 1e-9:
            equalities.append(index)
    if violations or tuple(equalities) != SOURCE_EQUALITY_IDS:
        raise ContractError(f"source scalar calibration changed: {violations=} {equalities=}")
    return {
        "commit": SOURCE_COMMIT, "csv_sha256": SOURCE_CSV_SHA256,
        "rows": len(rows), "eligible_rows": len(eligible),
        "scalar_violations": violations, "scalar_equality_ids": equalities,
        "equality_semantics": "source-table center-excluding implementation; calibration only",
    }


def atlas_gate() -> dict[str, object]:
    graphs = [normalized_graph(g) for g in nx.graph_atlas_g()
              if 2 <= len(g) <= 7 and nx.is_connected(g)]
    if len(graphs) != 995:
        raise ContractError(f"Atlas count {len(graphs)} != 995")
    literal_min = (float("inf"), "")
    literal_equalities: list[str] = []
    rejected_violations: list[str] = []
    rejected_equalities: list[str] = []
    for graph in graphs:
        energy = numerical_energy(graph)
        rounded = nearest_half_up(energy)
        for include_center, label in ((True, "literal"), (False, "center_excluding")):
            d2 = d2_values(graph, include_center=include_center)
            rhs = 3.0 * sum(1.0 / math.sqrt(d2[u] * d2[v]) for u, v in graph.edges())
            gap = rounded - rhs
            code = graph6(graph)
            if include_center:
                if gap < -1e-6:
                    raise ContractError(f"literal Atlas violation {code}")
                if abs(gap) <= 1e-6:
                    literal_equalities.append(code)
                if gap < literal_min[0]:
                    literal_min = (gap, code)
            else:
                if gap < -1e-6:
                    rejected_violations.append(code)
                if abs(gap) <= 1e-6:
                    rejected_equalities.append(code)
    if literal_equalities:
        raise ContractError(f"unexpected literal Atlas equalities {literal_equalities}")
    if rejected_violations != ["A_", "Bw"]:
        raise ContractError(f"center-excluding control failures changed: {rejected_violations}")
    return {
        "graphs": 995,
        "literal_closed": {
            "violations": 0, "equalities": [],
            "least_gap_graph6": literal_min[1], "least_gap_guarded_float": literal_min[0],
        },
        "center_excluding_rejected": {
            "violations": rejected_violations,
            "violation_names": ["K2", "K3"],
            "equalities": rejected_equalities,
            "disposition": "DB_REJECTED",
        },
        "spectral_guard": "1e-6; smallest literal gap is 0.5",
    }


def premise_record(graph: nx.Graph) -> dict[str, object]:
    connected = nx.is_connected(graph)
    planar, embedding = nx.check_planarity(graph, counterexample=False)
    diameter = nx.diameter(graph) if connected else None
    rotation = {
        str(int(v)): [int(w) for w in embedding.neighbors_cw_order(v)]
        for v in sorted(embedding)
    } if planar else {}
    return {
        "nontrivial": graph.number_of_nodes() >= 2,
        "connected": connected, "planar": planar, "diameter": diameter,
        "diameter_at_most_three": diameter is not None and diameter <= 3,
        "rotation": rotation,
    }


def diameter_paths(graph: nx.Graph) -> dict[str, list[int]]:
    paths: dict[str, list[int]] = {}
    for u in sorted(graph):
        all_paths = nx.single_source_shortest_path(graph, u, cutoff=3)
        for v in sorted(graph):
            if u < v:
                paths[f"{u}:{v}"] = [int(x) for x in all_paths[v]]
    return paths


def rational_eigenvalue_intervals(graph: nx.Graph, bits: int = 72) -> dict[str, object]:
    """Return a rational enclosure of graph energy using SymPy Sturm isolation."""
    import sympy as sp

    nodes = sorted(graph)
    matrix = sp.zeros(len(nodes), len(nodes))
    position = {v: i for i, v in enumerate(nodes)}
    for u, v in graph.edges():
        matrix[position[u], position[v]] = 1
        matrix[position[v], position[u]] = 1
    symbol = sp.Symbol("x")
    poly = sp.Poly(matrix.charpoly(symbol).as_expr(), symbol, domain=sp.ZZ)
    isolated = poly.intervals(eps=sp.Rational(1, 1 << bits))
    if sum(mult for _, mult in isolated) != len(nodes):
        raise ContractError("Sturm intervals lost eigenvalue multiplicity")
    energy_lower, energy_upper = Fraction(0), Fraction(0)
    intervals: list[dict[str, object]] = []
    for (left_raw, right_raw), multiplicity in isolated:
        left = Fraction(int(sp.numer(left_raw)), int(sp.denom(left_raw)))
        right = Fraction(int(sp.numer(right_raw)), int(sp.denom(right_raw)))
        if right < 0:
            abs_lower, abs_upper = -right, -left
        elif left > 0:
            abs_lower, abs_upper = left, right
        else:
            abs_lower, abs_upper = Fraction(0), max(-left, right)
        energy_lower += multiplicity * abs_lower
        energy_upper += multiplicity * abs_upper
        intervals.append({
            "left": frac_pair(left), "right": frac_pair(right),
            "multiplicity": multiplicity,
        })
    return {
        "characteristic_coefficients": [int(c) for c in poly.all_coeffs()],
        "root_intervals": intervals,
        "energy_lower": frac_pair(energy_lower), "energy_upper": frac_pair(energy_upper),
    }


def exact_candidate_certificate(graph: nx.Graph, rounded_hint: int) -> dict[str, object] | None:
    spectral = rational_eigenvalue_intervals(graph)
    energy_lower = Fraction(*spectral["energy_lower"])
    energy_upper = Fraction(*spectral["energy_upper"])
    shelf_lower = Fraction(2 * rounded_hint - 1, 2)
    shelf_upper = Fraction(2 * rounded_hint + 1, 2)
    if not (shelf_lower < energy_lower <= energy_upper < shelf_upper):
        return None
    rhs_lower, rhs_upper, terms = reciprocal_sum_bounds(graph, include_center=True)
    if not rhs_lower > rounded_hint:
        return None
    open_lower, open_upper, open_terms = reciprocal_sum_bounds(graph, include_center=False)
    premises = premise_record(graph)
    if not all(premises[key] for key in ("nontrivial", "connected", "planar", "diameter_at_most_three")):
        return None
    return {
        "schema": "c5k4-graffiti3-energy-c3-candidate-certificate-1.0",
        "doi": DOI, "reading": "LITERAL_CLOSED_D2",
        "graph6": graph6(graph), "edges": edge_list(graph),
        "order": graph.number_of_nodes(), "size": graph.number_of_edges(),
        "premises": premises, "diameter_paths": diameter_paths(graph),
        "d2_closed": [[v, x] for v, x in sorted(d2_values(graph, include_center=True).items())],
        "d2_center_excluding": [[v, x] for v, x in sorted(d2_values(graph, include_center=False).items())],
        "spectral": spectral, "rounded_energy": rounded_hint,
        "rounding": {
            "shelf_lower": frac_pair(shelf_lower), "shelf_upper": frac_pair(shelf_upper),
            "half_up": rounded_hint, "ties_to_even": rounded_hint,
            "tie_boundary_excluded": True,
        },
        "literal_rhs_lower": frac_pair(rhs_lower), "literal_rhs_upper": frac_pair(rhs_upper),
        "literal_terms": terms,
        "center_excluding_rhs_lower": frac_pair(open_lower),
        "center_excluding_rhs_upper": frac_pair(open_upper),
        "center_excluding_terms": open_terms,
        "strict_certificate": f"{rhs_lower} > {rounded_hint}",
    }


def book_graph(pages: int) -> nx.Graph:
    graph = nx.Graph([(0, 1)])
    graph.add_edges_from((hub, 2 + i) for i in range(pages) for hub in (0, 1))
    return normalized_graph(graph)


def book_chain(left_pages: int, right_pages: int) -> nx.Graph:
    graph = nx.Graph([(0, 1), (1, 2), (2, 3)])
    graph.add_edges_from((hub, 4 + i) for i in range(left_pages) for hub in (0, 1))
    offset = 4 + left_pages
    graph.add_edges_from((hub, offset + i) for i in range(right_pages) for hub in (2, 3))
    return normalized_graph(graph)


def double_star(left: int, right: int) -> nx.Graph:
    graph = nx.Graph([(0, 1)])
    graph.add_edges_from((0, 2 + i) for i in range(left))
    graph.add_edges_from((1, 2 + left + i) for i in range(right))
    return normalized_graph(graph)


def catalogue_graphs() -> Iterator[tuple[str, nx.Graph]]:
    for n in range(8, 33):
        yield f"path:{n}", nx.path_graph(n)
        yield f"cycle:{n}", nx.cycle_graph(n)
        yield f"star:{n}", nx.star_graph(n - 1)
        yield f"wheel:{n}", nx.wheel_graph(n)
        yield f"ladder:{n}", nx.ladder_graph(n // 2) if n % 2 == 0 else nx.path_graph(n)
        for left in range(1, n - 2):
            right = n - 2 - left
            yield f"double-star:{left}:{right}", double_star(left, right)
        yield f"book:{n - 2}", book_graph(n - 2)
        if n >= 8:
            for left in range(1, n - 4):
                right = n - 4 - left
                yield f"book-chain:{left}:{right}", book_chain(left, right)


def apollonian_graph(n: int, rng: random.Random) -> nx.Graph:
    graph = nx.complete_graph(3)
    faces: list[tuple[int, int, int]] = [(0, 1, 2)]
    for vertex in range(3, n):
        face_index = rng.randrange(len(faces))
        a, b, c = faces.pop(face_index)
        graph.add_edges_from(((vertex, a), (vertex, b), (vertex, c)))
        faces.extend(((a, b, vertex), (b, c, vertex), (c, a, vertex)))
    return normalized_graph(graph)


def generic_graphs(seed: int = 320260313, proposals: int = 1800) -> Iterator[tuple[str, nx.Graph]]:
    rng = random.Random(seed)
    for index in range(proposals):
        n = 8 + index % 25
        graph_seed = rng.randrange(1 << 63)
        local = random.Random(graph_seed)
        graph = apollonian_graph(n, local)
        removable = list(graph.edges())
        local.shuffle(removable)
        delete_quota = (index // 25) % max(1, n // 3)
        deleted = 0
        for edge in removable:
            if deleted >= delete_quota:
                break
            graph.remove_edge(*edge)
            if nx.is_connected(graph):
                deleted += 1
            else:
                graph.add_edge(*edge)
        yield f"apollonian-delete:{index}:{n}:{graph_seed}:{deleted}", normalized_graph(graph)


def wall_graphs() -> Iterator[tuple[str, nx.Graph]]:
    # Fixed diameter-three false-twin quotient family, motivated by the closed-d2 wall.
    for total in range(4, 33):
        for left in range(1, total):
            right = total - left
            if 8 <= 4 + left + right <= 36:
                yield f"book-chain:{left}:{right}", book_chain(left, right)
    # Source-table equality shapes, extended without using their target values.
    for pages in range(6, 35):
        yield f"book-pages:{pages}", book_graph(pages)
    for total in range(6, 35):
        for left in range(1, total):
            yield f"double-star:{left}:{total-left}", double_star(left, total - left)


def arm_graphs(arm: str) -> Iterable[tuple[str, nx.Graph]]:
    if arm == "CATALOGUE":
        return catalogue_graphs()
    if arm == "GENERIC":
        return generic_graphs()
    if arm == "WALL_NAVIGATION":
        return wall_graphs()
    raise ContractError(f"unknown arm {arm}")


def evaluate_graph(name: str, graph: nx.Graph) -> tuple[dict[str, object], dict[str, object] | None]:
    graph = normalized_graph(graph)
    premises = premise_record(graph)
    row: dict[str, object] = {
        "kind": "evaluation", "name": name, "graph6": graph6(graph),
        "order": graph.number_of_nodes(), "size": graph.number_of_edges(),
        "premises": {k: premises[k] for k in ("nontrivial", "connected", "planar", "diameter", "diameter_at_most_three")},
    }
    if not all(premises[key] for key in ("nontrivial", "connected", "planar", "diameter_at_most_three")):
        row["verdict"] = "NOT_APPLICABLE"
        return row, None
    energy = numerical_energy(graph)
    rounded = nearest_half_up(energy)
    d2_closed = d2_values(graph, include_center=True)
    d2_open = d2_values(graph, include_center=False)
    rhs_closed = 3.0 * sum(1.0 / math.sqrt(d2_closed[u] * d2_closed[v]) for u, v in graph.edges())
    rhs_open = 3.0 * sum(1.0 / math.sqrt(d2_open[u] * d2_open[v]) for u, v in graph.edges())
    row.update({
        "energy_guarded_float": format(energy, ".17g"), "rounded_energy_hint": rounded,
        "literal_rhs_guarded_float": format(rhs_closed, ".17g"),
        "literal_residual_guarded_float": format(rounded - rhs_closed, ".17g"),
        "center_excluding_rhs_guarded_float": format(rhs_open, ".17g"),
        "center_excluding_disposition": "DB_REJECTED_READING",
        "d2_closed": [[v, x] for v, x in sorted(d2_closed.items())],
    })
    certificate = None
    if rhs_closed > rounded + 1e-7:
        certificate = exact_candidate_certificate(graph, rounded)
    row["verdict"] = "CANDIDATE_ONLY" if certificate else "NO_CERTIFIED_CROSSING"
    if certificate:
        encoded = canonical_bytes(certificate)
        row["certificate_sha256"] = hashlib.sha256(encoded).hexdigest()
    return row, certificate


def run(args: argparse.Namespace) -> int:
    started = time.monotonic()
    ledger = ChainedLedger(args.output)
    try:
        source = source_calibration(args.source_csv)
        atlas = atlas_gate()
    except Exception as exc:
        ledger.append({
            "kind": "gate_failure", "campaign": CAMPAIGN, "doi": DOI,
            "arm": args.arm, "campaign_commit": args.campaign_commit,
            "error_type": type(exc).__name__, "message": str(exc),
        })
        terminal = {
            "schema": TERMINAL_SCHEMA, "campaign": CAMPAIGN, "doi": DOI,
            "arm": args.arm, "campaign_commit": args.campaign_commit,
            "reason": "DB_GATE_FAILED", "proposed": 0, "canonical_unique": 0,
            "evaluated": 0, "applicable": 0,
            "ledger_records": ledger.count, "final_record_hash": ledger.previous,
            "ledger_sha256": None, "candidate_path": None,
            "internal_seconds": args.internal_seconds,
            "elapsed_seconds": time.monotonic() - started,
        }
        ledger.close()
        terminal["ledger_sha256"] = sha256_file(args.output)
        terminal["terminal_hash"] = hashlib.sha256(canonical_bytes(terminal)).hexdigest()
        write_fsync_json(args.terminal, terminal)
        print(json.dumps(terminal, sort_keys=True))
        return 2
    ledger.append({
        "kind": "gate", "campaign": CAMPAIGN, "doi": DOI, "arm": args.arm,
        "source_calibration": source, "atlas_gate": atlas,
        "campaign_commit": args.campaign_commit,
    })
    seen: set[str] = set()
    proposed = evaluated = applicable = 0
    reason = "DOMAIN_EXHAUSTED"
    candidate_path: str | None = None
    try:
        for name, raw_graph in arm_graphs(args.arm):
            if time.monotonic() - started >= args.internal_seconds:
                reason = "DEADLINE_PREFIX"
                break
            proposed += 1
            graph = normalized_graph(raw_graph)
            code = graph6(graph)
            if code in seen:
                continue
            seen.add(code)
            row, certificate = evaluate_graph(name, graph)
            evaluated += 1
            if row["premises"]["diameter_at_most_three"] and row["premises"]["planar"]:
                applicable += 1
            ledger.append(row)
            if certificate is not None:
                candidate_path = str(args.candidate)
                write_fsync_json(args.candidate, certificate)
                reason = "CANDIDATE_FOUND"
                break
    except Exception as exc:
        ledger.append({"kind": "error", "error_type": type(exc).__name__, "message": str(exc)})
        reason = "ERROR"
    terminal = {
        "schema": TERMINAL_SCHEMA, "campaign": CAMPAIGN, "doi": DOI,
        "arm": args.arm, "campaign_commit": args.campaign_commit,
        "reason": reason, "proposed": proposed, "canonical_unique": len(seen),
        "evaluated": evaluated, "applicable": applicable,
        "ledger_records": ledger.count, "final_record_hash": ledger.previous,
        "ledger_sha256": None, "candidate_path": candidate_path,
        "internal_seconds": args.internal_seconds,
        "elapsed_seconds": time.monotonic() - started,
    }
    ledger.close()
    terminal["ledger_sha256"] = sha256_file(args.output)
    terminal_without_hash = dict(terminal)
    terminal["terminal_hash"] = hashlib.sha256(canonical_bytes(terminal_without_hash)).hexdigest()
    write_fsync_json(args.terminal, terminal)
    print(json.dumps(terminal, sort_keys=True))
    return 0 if reason != "ERROR" else 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", required=True, choices=ARMS)
    parser.add_argument("--source-csv", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--terminal", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--campaign-commit", required=True)
    parser.add_argument("--internal-seconds", type=float, default=INTERNAL_SECONDS)
    args = parser.parse_args()
    if not (0 < args.internal_seconds <= INTERNAL_SECONDS):
        parser.error("internal cap must be in (0,54]")
    if len(args.campaign_commit) != 40 or any(c not in "0123456789abcdef" for c in args.campaign_commit):
        parser.error("campaign commit must be exactly 40 lowercase hex characters")
    return args


if __name__ == "__main__":
    raise SystemExit(run(parse_args()))
