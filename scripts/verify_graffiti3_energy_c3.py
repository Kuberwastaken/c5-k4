#!/usr/bin/env python3
"""Independent freeze, ledger, and candidate verifier for Graffiti3 energy C3."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

import networkx as nx


LEDGER_SCHEMA = "c5k4-graffiti3-energy-c3-ledger-1.0"
TERMINAL_SCHEMA = "c5k4-graffiti3-energy-c3-terminal-1.0"
CANDIDATE_SCHEMA = "c5k4-graffiti3-energy-c3-candidate-certificate-1.0"
DOI = "10.21203/rs.3.rs-8493329/v1"


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pair(value: list[int]) -> Fraction:
    return Fraction(value[0], value[1])


def replay_ledger(path: Path) -> tuple[int, str]:
    previous = "0" * 64
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row.get("schema") != LEDGER_SCHEMA or row.get("sequence") != count:
            raise ValueError(f"ledger schema/sequence failure at {count}")
        if row.get("previous_hash") != previous:
            raise ValueError(f"ledger predecessor failure at {count}")
        claimed = row.pop("record_hash")
        actual = hashlib.sha256(canonical_bytes(row)).hexdigest()
        if claimed != actual:
            raise ValueError(f"ledger hash failure at {count}")
        previous = claimed
        count += 1
    return count, previous


def verify_terminal(ledger: Path, terminal_path: Path) -> dict[str, object]:
    terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
    if terminal.get("schema") != TERMINAL_SCHEMA:
        raise ValueError("terminal schema mismatch")
    count, final_hash = replay_ledger(ledger)
    if terminal.get("ledger_records") != count or terminal.get("final_record_hash") != final_hash:
        raise ValueError("terminal does not bind ledger chain")
    if terminal.get("ledger_sha256") != file_sha(ledger):
        raise ValueError("terminal ledger SHA mismatch")
    claimed = terminal.pop("terminal_hash")
    if hashlib.sha256(canonical_bytes(terminal)).hexdigest() != claimed:
        raise ValueError("terminal hash mismatch")
    terminal["terminal_hash"] = claimed
    return terminal


def reconstruct_graph(certificate: dict[str, object]) -> nx.Graph:
    order = int(certificate["order"])
    graph = nx.Graph()
    graph.add_nodes_from(range(order))
    graph.add_edges_from(tuple(edge) for edge in certificate["edges"])
    if set(graph) != set(range(order)):
        raise ValueError("edge endpoint outside declared vertex set")
    if graph.number_of_edges() != int(certificate["size"]):
        raise ValueError("edge count mismatch")
    return graph


def independent_graph6(graph: nx.Graph) -> str:
    normalized = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    return nx.to_graph6_bytes(normalized, header=False).decode().strip()


def independent_d2(graph: nx.Graph, include_center: bool) -> list[list[int]]:
    output: list[list[int]] = []
    for vertex in sorted(graph):
        count = len(nx.single_source_shortest_path_length(graph, vertex, cutoff=2))
        output.append([vertex, count if include_center else count - 1])
    return output


def frac_pair(value: Fraction) -> list[int]:
    return [value.numerator, value.denominator]


def independent_rhs_certificate(
    graph: nx.Graph, include_center: bool, bits: int = 96
) -> tuple[Fraction, Fraction, list[dict[str, object]]]:
    d2 = dict((row[0], row[1]) for row in independent_d2(graph, include_center))
    scale = 1 << bits
    lower = upper = Fraction(0)
    terms: list[dict[str, object]] = []
    for u, v in sorted((min(int(a), int(b)), max(int(a), int(b))) for a, b in graph.edges()):
        value = d2[u] * d2[v]
        floor_scaled = math.isqrt(value * scale * scale)
        root_lower = Fraction(floor_scaled, scale)
        root_upper = root_lower if floor_scaled * floor_scaled == value * scale * scale else Fraction(floor_scaled + 1, scale)
        lower += Fraction(3, 1) / root_upper
        upper += Fraction(3, 1) / root_lower
        terms.append({
            "edge": [u, v],
            "d2": [d2[u], d2[v]],
            "lower": frac_pair(Fraction(3, 1) / root_upper),
            "upper": frac_pair(Fraction(3, 1) / root_lower),
        })
    return lower, upper, terms


def independent_spectral_certificate(graph: nx.Graph) -> dict[str, object]:
    import sympy as sp

    matrix = sp.zeros(len(graph), len(graph))
    for u, v in graph.edges():
        matrix[u, v] = matrix[v, u] = 1
    x = sp.Symbol("x")
    polynomial = sp.Poly(matrix.charpoly(x).as_expr(), x, domain=sp.ZZ)
    intervals = polynomial.intervals(eps=sp.Rational(1, 1 << 72))
    if sum(multiplicity for _, multiplicity in intervals) != len(graph):
        raise ValueError("independent Sturm isolation lost eigenvalue multiplicity")
    energy_lower = energy_upper = Fraction(0)
    encoded_intervals: list[dict[str, object]] = []
    for (left_raw, right_raw), multiplicity in intervals:
        left = Fraction(int(sp.numer(left_raw)), int(sp.denom(left_raw)))
        right = Fraction(int(sp.numer(right_raw)), int(sp.denom(right_raw)))
        if right < 0:
            lo, hi = -right, -left
        elif left > 0:
            lo, hi = left, right
        else:
            lo, hi = Fraction(0), max(-left, right)
        energy_lower += multiplicity * lo
        energy_upper += multiplicity * hi
        encoded_intervals.append({
            "left": frac_pair(left),
            "right": frac_pair(right),
            "multiplicity": multiplicity,
        })
    return {
        "characteristic_coefficients": [int(c) for c in polynomial.all_coeffs()],
        "root_intervals": encoded_intervals,
        "energy_lower": frac_pair(energy_lower),
        "energy_upper": frac_pair(energy_upper),
    }


def verify_rotation_certificate(graph: nx.Graph, raw_rotation: dict[str, list[int]]) -> None:
    rotation = {int(vertex): [int(neighbor) for neighbor in neighbors]
                for vertex, neighbors in raw_rotation.items()}
    if set(rotation) != set(graph):
        raise ValueError("rotation vertex set mismatch")
    embedding = nx.PlanarEmbedding()
    embedding.set_data(rotation)
    embedding.check_structure()
    embedded_edges = {frozenset((int(u), int(v))) for u, v in embedding.edges()}
    graph_edges = {frozenset((int(u), int(v))) for u, v in graph.edges()}
    if embedded_edges != graph_edges:
        raise ValueError("rotation edge set mismatch")
    marked: set[tuple[int, int]] = set()
    faces = 0
    for u, v in embedding.edges():
        directed = (int(u), int(v))
        if directed in marked:
            continue
        face = embedding.traverse_face(u, v, mark_half_edges=marked)
        if len(face) < 2:
            raise ValueError("degenerate face in rotation certificate")
        faces += 1
    if graph.number_of_nodes() - graph.number_of_edges() + faces != 2:
        raise ValueError("rotation certificate fails Euler formula")


def verify_candidate_integrity(
    certificate: dict[str, object],
) -> tuple[nx.Graph, Fraction, Fraction, Fraction]:
    if certificate.get("schema") != CANDIDATE_SCHEMA:
        raise ValueError("candidate schema mismatch")
    if certificate.get("doi") != DOI or certificate.get("reading") != "LITERAL_CLOSED_D2":
        raise ValueError("candidate source/reading mismatch")
    graph = reconstruct_graph(certificate)
    if certificate.get("graph6") != independent_graph6(graph):
        raise ValueError("graph6 checksum mismatch")
    if not nx.is_connected(graph) or not nx.check_planarity(graph)[0] or nx.diameter(graph) > 3:
        raise ValueError("candidate premise failure")
    expected_premises = {
        "nontrivial": len(graph) >= 2,
        "connected": nx.is_connected(graph),
        "planar": nx.check_planarity(graph)[0],
        "diameter": nx.diameter(graph),
        "diameter_at_most_three": nx.diameter(graph) <= 3,
    }
    for key, expected in expected_premises.items():
        if certificate["premises"].get(key) != expected:
            raise ValueError(f"candidate premise field mismatch: {key}")
    verify_rotation_certificate(graph, certificate["premises"]["rotation"])
    if certificate["d2_closed"] != independent_d2(graph, True):
        raise ValueError("closed d2 mismatch")
    if certificate["d2_center_excluding"] != independent_d2(graph, False):
        raise ValueError("center-excluding d2 mismatch")
    expected_path_keys = {f"{u}:{v}" for u in sorted(graph) for v in sorted(graph) if u < v}
    if set(certificate["diameter_paths"]) != expected_path_keys:
        raise ValueError("diameter path coverage mismatch")
    for key, path_vertices in certificate["diameter_paths"].items():
        u, v = map(int, key.split(":"))
        if path_vertices[0] != u or path_vertices[-1] != v or len(path_vertices) > 4:
            raise ValueError(f"invalid diameter path {key}")
        if any(not graph.has_edge(a, b) for a, b in zip(path_vertices, path_vertices[1:])):
            raise ValueError(f"nonedge in diameter path {key}")
    spectral = independent_spectral_certificate(graph)
    if certificate.get("spectral") != spectral:
        raise ValueError("stored spectral certificate mismatch")
    energy_lower = pair(spectral["energy_lower"])
    energy_upper = pair(spectral["energy_upper"])
    rounded = int(certificate["rounded_energy"])
    shelf_lower = Fraction(2 * rounded - 1, 2)
    shelf_upper = Fraction(2 * rounded + 1, 2)
    expected_rounding = {
        "shelf_lower": frac_pair(shelf_lower),
        "shelf_upper": frac_pair(shelf_upper),
        "half_up": rounded,
        "ties_to_even": rounded,
        "tie_boundary_excluded": True,
    }
    if certificate.get("rounding") != expected_rounding:
        raise ValueError("stored rounding certificate mismatch")
    if not (shelf_lower < energy_lower <= energy_upper < shelf_upper):
        raise ValueError("energy is not isolated inside claimed rounding shelf")
    rhs_lower, rhs_upper, literal_terms = independent_rhs_certificate(graph, True)
    if certificate.get("literal_rhs_lower") != frac_pair(rhs_lower):
        raise ValueError("stored literal RHS lower bound mismatch")
    if certificate.get("literal_rhs_upper") != frac_pair(rhs_upper):
        raise ValueError("stored literal RHS upper bound mismatch")
    if certificate.get("literal_terms") != literal_terms:
        raise ValueError("stored literal radical terms mismatch")
    open_lower, open_upper, open_terms = independent_rhs_certificate(graph, False)
    if certificate.get("center_excluding_rhs_lower") != frac_pair(open_lower):
        raise ValueError("stored center-excluding RHS lower bound mismatch")
    if certificate.get("center_excluding_rhs_upper") != frac_pair(open_upper):
        raise ValueError("stored center-excluding RHS upper bound mismatch")
    if certificate.get("center_excluding_terms") != open_terms:
        raise ValueError("stored center-excluding radical terms mismatch")
    if certificate.get("strict_certificate") != f"{rhs_lower} > {rounded}":
        raise ValueError("stored strict-certificate text mismatch")
    return graph, energy_lower, energy_upper, rhs_lower


def verify_candidate(path: Path) -> None:
    certificate = json.loads(path.read_text(encoding="utf-8"))
    _, _, _, rhs_lower = verify_candidate_integrity(certificate)
    rounded = int(certificate["rounded_energy"])
    if rhs_lower <= rounded:
        raise ValueError("literal closed-d2 strict crossing not certified")


def verify_candidate_binding(ledger: Path, terminal_path: Path, candidate: Path) -> None:
    terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
    if terminal.get("reason") != "CANDIDATE_FOUND" or not terminal.get("candidate_path"):
        raise ValueError("terminal does not declare the supplied candidate")
    candidate_sha256 = file_sha(candidate)
    candidate_rows: list[dict[str, object]] = []
    for line in ledger.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if "certificate_sha256" in row:
            candidate_rows.append(row)
    if len(candidate_rows) != 1:
        raise ValueError("ledger must contain exactly one candidate-binding row")
    row = candidate_rows[0]
    if row.get("verdict") != "CANDIDATE_ONLY":
        raise ValueError("candidate-binding row has wrong verdict")
    if row.get("certificate_sha256") != candidate_sha256:
        raise ValueError("candidate bytes do not match ledger certificate_sha256")


def verify_freeze(root: Path) -> None:
    manifest_path = root / "results/expansion/live-search-2026-08-14/graffiti3-energy-c3-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "FROZEN_UNRUN_DEVELOPMENT":
        raise ValueError("manifest status is not frozen-unrun")
    for relative, expected in manifest["frozen_files"].items():
        actual = file_sha(root / relative)
        if actual != expected:
            raise ValueError(f"frozen file hash mismatch: {relative}")
    workflow = (root / ".github/workflows/graffiti3-energy-c3-development.yml").read_text()
    for needle in ("permissions:\n  contents: read", "timeout --signal=TERM --kill-after=5s 60s", "--internal-seconds 54"):
        if needle not in workflow:
            raise ValueError(f"workflow guard missing: {needle}")
    test_text = (root / "scripts/test_graffiti3_energy_c3.py").read_text()
    if "evaluate_graph(" in test_text:
        raise ValueError("constructor-only test file invokes target evaluator")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path)
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--terminal", type=Path)
    parser.add_argument("--candidate", type=Path)
    args = parser.parse_args()
    if args.root:
        verify_freeze(args.root)
    terminal: dict[str, object] | None = None
    if args.ledger or args.terminal:
        if not (args.ledger and args.terminal):
            parser.error("ledger and terminal must be supplied together")
        terminal = verify_terminal(args.ledger, args.terminal)
    if args.candidate:
        verify_candidate(args.candidate)
        if args.ledger and args.terminal:
            verify_candidate_binding(args.ledger, args.terminal, args.candidate)
    elif terminal is not None and terminal.get("reason") == "CANDIDATE_FOUND":
        parser.error("candidate artifact is required for a CANDIDATE_FOUND terminal")
    if not any((args.root, args.ledger, args.terminal, args.candidate)):
        parser.error("choose a verification mode")
    print("graffiti3-energy-c3 verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
