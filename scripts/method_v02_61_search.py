#!/usr/bin/env python3
"""Exact bounded two-switch trial for WOWII 61.

Writes an append-only JSONL checkpoint after the database gate and after every
completed degree-sequence component.  No claim is made beyond the frozen
bounds in results/expansion/method_v02_upstream_selection.md.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import signal
import subprocess
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Iterable

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "results/expansion/method_v02_61_search.jsonl"


class SolveTimeout(RuntimeError):
    pass


def _alarm_handler(_signum: int, _frame: object) -> None:
    raise SolveTimeout("60-second exact-solve cap reached")


def residue_from_degrees(degrees: Iterable[int]) -> int:
    sequence = sorted((int(d) for d in degrees), reverse=True)
    while sequence and sequence[0] > 0:
        d = sequence.pop(0)
        if d > len(sequence):
            raise ValueError("nongraphical degree sequence during HH reduction")
        for i in range(d):
            sequence[i] -= 1
            if sequence[i] < 0:
                raise ValueError("negative HH term")
        sequence.sort(reverse=True)
    return len(sequence)


def residue(graph: nx.Graph) -> int:
    return residue_from_degrees(d for _, d in graph.degree())


def is_forest(graph: nx.Graph) -> bool:
    return graph.number_of_edges() == graph.number_of_nodes() - nx.number_connected_components(graph)


def largest_induced_forest(graph: nx.Graph, cap_seconds: int = 60) -> tuple[int, tuple[int, ...]]:
    nodes = tuple(sorted(graph.nodes()))
    old_handler = signal.signal(signal.SIGALRM, _alarm_handler)
    signal.alarm(cap_seconds)
    try:
        for size in range(len(nodes), 0, -1):
            for subset in itertools.combinations(nodes, size):
                if is_forest(graph.subgraph(subset)):
                    return size, subset
        return 0, ()
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


def exact_record(graph: nx.Graph) -> dict[str, object]:
    if graph.number_of_nodes() > 1 and not nx.is_connected(graph):
        raise ValueError("WOWII 61 requires connected graph")
    start = time.monotonic()
    forest, witness = largest_induced_forest(graph)
    elapsed = time.monotonic() - start
    diam = nx.diameter(graph) if graph.number_of_nodes() > 1 else 0
    res = residue(graph)
    residual = forest - res - math.ceil(diam / 3)
    return {
        "n": graph.number_of_nodes(),
        "m": graph.number_of_edges(),
        "degree_sequence": sorted((d for _, d in graph.degree()), reverse=True),
        "forest": forest,
        "forest_witness": list(witness),
        "residue": res,
        "diameter": diam,
        "ceil_diameter_over_3": math.ceil(diam / 3),
        "residual": residual,
        "solve_seconds": elapsed,
        "graph6": nx.to_graph6_bytes(nx.convert_node_labels_to_integers(graph), header=False).decode().strip(),
    }


def c5_clique_blowup(size: int) -> nx.Graph:
    graph = nx.Graph()
    for i in range(5):
        for a in range(size):
            graph.add_node(i * size + a)
    for i in range(5):
        blob = [i * size + a for a in range(size)]
        graph.add_edges_from(itertools.combinations(blob, 2))
        nxt = [((i + 1) % 5) * size + a for a in range(size)]
        graph.add_edges_from(itertools.product(blob, nxt))
    return graph


def named_controls() -> list[tuple[str, nx.Graph]]:
    controls: list[tuple[str, nx.Graph]] = []
    for n in range(5, 10):
        controls.append((f"C{n}", nx.cycle_graph(n)))
    controls.extend([
        ("P7", nx.path_graph(7)),
        ("Petersen", nx.petersen_graph()),
        ("K3,3", nx.complete_bipartite_graph(3, 3)),
        ("K7", nx.complete_graph(7)),
        ("C5[K2]", c5_clique_blowup(2)),
    ])
    for n in range(2, 13):
        controls.append((f"K1,{n-1}", nx.star_graph(n - 1)))
    for a in range(2, 7):
        for b in range(a, 13 - a):
            controls.append((f"K{a},{b}", nx.complete_bipartite_graph(a, b)))
    return controls


def wl_key(graph: nx.Graph) -> tuple[int, tuple[int, ...], str]:
    return (
        graph.number_of_nodes(),
        tuple(sorted((d for _, d in graph.degree()), reverse=True)),
        nx.weisfeiler_lehman_graph_hash(graph, iterations=max(3, graph.number_of_nodes())),
    )


class IsoStore:
    def __init__(self) -> None:
        self.buckets: dict[tuple[int, tuple[int, ...], str], list[nx.Graph]] = defaultdict(list)

    def add(self, graph: nx.Graph) -> bool:
        graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
        key = wl_key(graph)
        if any(nx.is_isomorphic(graph, old) for old in self.buckets[key]):
            return False
        self.buckets[key].append(graph.copy())
        return True


def distinct_controls() -> list[tuple[str, nx.Graph]]:
    result: list[tuple[str, nx.Graph]] = []
    store = IsoStore()
    for i, graph in enumerate(nx.graph_atlas_g()):
        if 2 <= graph.number_of_nodes() <= 7 and nx.is_connected(graph):
            if store.add(graph):
                result.append((f"atlas:{i}", nx.convert_node_labels_to_integers(graph)))
    for name, graph in named_controls():
        if store.add(graph):
            result.append((name, nx.convert_node_labels_to_integers(graph)))
    return result


def two_switch_neighbors(graph: nx.Graph) -> Iterable[nx.Graph]:
    edges = sorted(tuple(sorted(edge)) for edge in graph.edges())
    for i, (a, b) in enumerate(edges):
        for c, d in edges[i + 1:]:
            if len({a, b, c, d}) < 4:
                continue
            for added in (((a, c), (b, d)), ((a, d), (b, c))):
                if graph.has_edge(*added[0]) or graph.has_edge(*added[1]):
                    continue
                candidate = graph.copy()
                candidate.remove_edges_from(((a, b), (c, d)))
                candidate.add_edges_from(added)
                if nx.is_connected(candidate):
                    yield candidate


def append_jsonl(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, sort_keys=True) + "\n")
        handle.flush()


def database_gate(controls: list[tuple[str, nx.Graph]]) -> tuple[list[dict[str, object]], list[tuple[str, nx.Graph, dict[str, object]]]]:
    rows: list[dict[str, object]] = []
    bases: list[tuple[str, nx.Graph, dict[str, object]]] = []
    for name, graph in controls:
        record = exact_record(graph)
        row = {"name": name, **record}
        rows.append(row)
        if 1 <= int(record["residual"]) <= 2 and graph.number_of_nodes() <= 12:
            bases.append((name, graph, record))
    return rows, bases


def switch_component(base_name: str, base: nx.Graph, base_record: dict[str, object], max_depth: int) -> dict[str, object]:
    store = IsoStore()
    store.add(base)
    queue: deque[tuple[nx.Graph, int]] = deque([(base.copy(), 0)])
    layers: dict[int, int] = defaultdict(int)
    residual_hist: dict[int, int] = defaultdict(int)
    diameter_hist: dict[int, int] = defaultdict(int)
    best: list[dict[str, object]] = []
    timeouts = 0
    evaluated = 0
    nontrivial_equality = False
    while queue:
        graph, depth = queue.popleft()
        try:
            record = exact_record(graph)
        except SolveTimeout:
            timeouts += 1
            continue
        evaluated += 1
        layers[depth] += 1
        residual_hist[int(record["residual"])] += 1
        diameter_hist[int(record["diameter"])] += 1
        if depth > 0 and int(record["residual"]) == 0:
            nontrivial_equality = True
        item = {"depth": depth, **record}
        best.append(item)
        best.sort(key=lambda x: (int(x["residual"]), -int(x["diameter"]), int(x["forest"]), str(x["graph6"])))
        del best[10:]
        if depth == max_depth:
            continue
        for neighbor in two_switch_neighbors(graph):
            if store.add(neighbor):
                queue.append((neighbor, depth + 1))
    return {
        "kind": "switch_component",
        "base": base_name,
        "base_graph6": base_record["graph6"],
        "n": base.number_of_nodes(),
        "degree_sequence": base_record["degree_sequence"],
        "residue": base_record["residue"],
        "max_depth": max_depth,
        "evaluated": evaluated,
        "timeouts": timeouts,
        "layers": dict(sorted(layers.items())),
        "residual_histogram": dict(sorted(residual_hist.items())),
        "diameter_histogram": dict(sorted(diameter_hist.items())),
        "minimum_residual": min((int(x["residual"]) for x in best), default=None),
        "maximum_diameter": max(diameter_hist, default=None),
        "nontrivial_equality": nontrivial_equality,
        "best": best,
    }


def geng_regular_component(
    geng: Path, labelg: Path, base_name: str, base: nx.Graph,
    base_record: dict[str, object], max_depth: int
) -> dict[str, object]:
    """Use nauty representatives to avoid labelled duplicate explosion.

    This path is used for the principal 5-regular order-10 component.  We build
    the exact quotient switch graph on all connected unlabelled realizations,
    then retain precisely the vertices at distance at most ``max_depth``.
    """
    n = base.number_of_nodes()
    degrees = {d for _, d in base.degree()}
    if len(degrees) != 1:
        raise ValueError("geng regular path requires a regular base")
    degree = next(iter(degrees))
    process = subprocess.run(
        [str(geng), "-cq", f"-d{degree}", f"-D{degree}", str(n)],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    raw_lines = [line for line in process.stdout.splitlines() if line and not line.startswith(">")]
    graphs = [nx.convert_node_labels_to_integers(nx.from_graph6_bytes(line.encode())) for line in raw_lines]

    def canonicalize(lines: list[str]) -> list[str]:
        labelled = subprocess.run(
            [str(labelg), "-q"], input="\n".join(lines) + "\n", check=True,
            text=True, stdout=subprocess.PIPE,
        )
        return [line for line in labelled.stdout.splitlines() if line and not line.startswith(">")]

    representative_canons = canonicalize(raw_lines)
    canon_to_index = {canon: i for i, canon in enumerate(representative_canons)}
    base_line = nx.to_graph6_bytes(nx.convert_node_labels_to_integers(base), header=False).decode().strip()
    start_index = canon_to_index[canonicalize([base_line])[0]]
    adjacency: list[set[int]] = [set() for _ in graphs]
    owners: list[int] = []
    neighbor_lines: list[str] = []
    for i, graph in enumerate(graphs):
        for neighbor in two_switch_neighbors(graph):
            owners.append(i)
            neighbor_lines.append(
                nx.to_graph6_bytes(nx.convert_node_labels_to_integers(neighbor), header=False).decode().strip()
            )
    for i, canon in zip(owners, canonicalize(neighbor_lines)):
        if canon not in canon_to_index:
            raise AssertionError("geng did not contain a connected regular switch neighbor")
        j = canon_to_index[canon]
        adjacency[i].add(j)
        adjacency[j].add(i)
    distances = {start_index: 0}
    queue: deque[int] = deque([start_index])
    while queue:
        i = queue.popleft()
        if distances[i] == max_depth:
            continue
        for j in adjacency[i]:
            if j not in distances:
                distances[j] = distances[i] + 1
                queue.append(j)

    layers: dict[int, int] = defaultdict(int)
    residual_hist: dict[int, int] = defaultdict(int)
    diameter_hist: dict[int, int] = defaultdict(int)
    best: list[dict[str, object]] = []
    timeouts = 0
    nontrivial_equality = False
    for i, depth in sorted(distances.items(), key=lambda item: (item[1], item[0])):
        try:
            record = exact_record(graphs[i])
        except SolveTimeout:
            timeouts += 1
            continue
        layers[depth] += 1
        residual_hist[int(record["residual"])] += 1
        diameter_hist[int(record["diameter"])] += 1
        if depth > 0 and int(record["residual"]) == 0:
            nontrivial_equality = True
        item = {"depth": depth, **record}
        best.append(item)
        best.sort(key=lambda x: (int(x["residual"]), -int(x["diameter"]), int(x["forest"]), str(x["graph6"])))
        del best[10:]
    return {
        "kind": "switch_component",
        "enumerator": "nauty geng exact unlabelled regular class",
        "base": base_name,
        "base_graph6": base_record["graph6"],
        "n": n,
        "degree_sequence": base_record["degree_sequence"],
        "residue": base_record["residue"],
        "max_depth": max_depth,
        "full_connected_regular_class": len(graphs),
        "evaluated": sum(layers.values()),
        "timeouts": timeouts,
        "layers": dict(sorted(layers.items())),
        "residual_histogram": dict(sorted(residual_hist.items())),
        "diameter_histogram": dict(sorted(diameter_hist.items())),
        "minimum_residual": min((int(x["residual"]) for x in best), default=None),
        "maximum_diameter": max(diameter_hist, default=None),
        "nontrivial_equality": nontrivial_equality,
        "best": best,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--max-depth", type=int, default=4)
    parser.add_argument("--geng", type=Path, required=True, help="path to nauty geng")
    parser.add_argument("--labelg", type=Path, required=True, help="path to nauty labelg")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.output.exists() and not args.force:
        raise SystemExit(f"refusing to overwrite {args.output}; pass --force")
    if args.output.exists():
        args.output.unlink()
    if not args.geng.is_file():
        raise SystemExit(f"geng not found: {args.geng}")
    if not args.labelg.is_file():
        raise SystemExit(f"labelg not found: {args.labelg}")

    started = time.monotonic()
    controls = distinct_controls()
    gate_rows, raw_bases = database_gate(controls)
    violations = [row for row in gate_rows if int(row["residual"]) < 0]
    append_jsonl(args.output, {
        "kind": "database_gate",
        "controls": len(gate_rows),
        "violations": violations,
        "minimum_residual": min(int(row["residual"]) for row in gate_rows),
        "residual_histogram": dict(sorted((r, sum(int(row["residual"]) == r for row in gate_rows)) for r in set(int(row["residual"]) for row in gate_rows))),
        "rows": gate_rows,
    })
    if violations:
        append_jsonl(args.output, {"kind": "stopped", "reason": "database gate failed"})
        return

    # One representative per degree sequence: every 2-switch component has a
    # fixed sequence, and the complete BFS from any representative discovers
    # the same connected realization component when it is connected under
    # switches.  Preserve all names that selected the component.
    grouped: dict[tuple[int, ...], list[tuple[str, nx.Graph, dict[str, object]]]] = defaultdict(list)
    for entry in raw_bases:
        grouped[tuple(entry[2]["degree_sequence"])].append(entry)
    bases: list[tuple[str, nx.Graph, dict[str, object], list[str]]] = []
    for degree_sequence, entries in sorted(grouped.items(), key=lambda x: (len(x[0]), x[0])):
        name, graph, record = entries[0]
        bases.append((name, graph, record, [item[0] for item in entries]))
    append_jsonl(args.output, {
        "kind": "base_manifest",
        "raw_base_controls": len(raw_bases),
        "degree_sequence_components": len(bases),
        "bases": [{"representative": name, "aliases": names, **record} for name, _, record, names in bases],
    })

    components: list[dict[str, object]] = []
    for index, (name, graph, record, aliases) in enumerate(bases, 1):
        if graph.number_of_nodes() == 10 and set(record["degree_sequence"]) == {5}:
            component = geng_regular_component(
                args.geng, args.labelg, name, graph, record, args.max_depth
            )
        else:
            component = switch_component(name, graph, record, args.max_depth)
        component["base_aliases"] = aliases
        component["component_index"] = index
        component["component_count"] = len(bases)
        append_jsonl(args.output, component)
        components.append(component)
    append_jsonl(args.output, {
        "kind": "summary",
        "controls": len(gate_rows),
        "degree_sequence_components": len(components),
        "evaluated_sum": sum(int(c["evaluated"]) for c in components),
        "timeouts": sum(int(c["timeouts"]) for c in components),
        "minimum_residual": min(int(c["minimum_residual"]) for c in components if c["minimum_residual"] is not None),
        "maximum_diameter": max(int(c["maximum_diameter"]) for c in components if c["maximum_diameter"] is not None),
        "negative_components": [c["base"] for c in components if int(c["minimum_residual"]) < 0],
        "nontrivial_equality_components": [c["base"] for c in components if bool(c["nontrivial_equality"])],
        "extension_stratum_triggered": any(bool(c["nontrivial_equality"]) and int(c["n"]) <= 12 for c in components),
        "seconds": time.monotonic() - started,
    })


if __name__ == "__main__":
    main()
