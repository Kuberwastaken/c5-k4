#!/usr/bin/env python3
"""Exact bounded Method v0.1 search around the WOWII barbell cluster.

Targets: WOWII 169, 174, 180, and 182.  This script deliberately implements
only the preregistered transformations in the accompanying report: edit-orbit
representatives through two toggled edges around D6/D8/D10, and endpoint
cliques K2..K5 on path lengths 2..10.

All subset optimizations are exact and guarded by a 60-second wall-clock cap.
The script writes no files; its TSV/JSON output can be independently preserved.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from itertools import combinations
import json
import signal
import time
from typing import Iterable, Iterator

import networkx as nx


CAP_SECONDS = 60
TARGETS = (169, 174, 180, 182)


def popcount(value: int) -> int:
    """Python 3.9-compatible population count."""
    return bin(value).count("1")


class OptimizationTimeout(RuntimeError):
    pass


class alarm:
    """POSIX wall-clock cap for one exact optimization call."""

    def __init__(self, seconds: int = CAP_SECONDS):
        self.seconds = seconds
        self.old_handler = None

    def __enter__(self):
        def handle_timeout(_signum, _frame):
            raise OptimizationTimeout(f"exact optimization exceeded {self.seconds}s")

        self.old_handler = signal.signal(signal.SIGALRM, handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, exc_type, exc, tb):
        signal.alarm(0)
        signal.signal(signal.SIGALRM, self.old_handler)
        return False


def endpoint_clique_barbell(length: int, left: int = 3, right: int = 3) -> nx.Graph:
    """K_left and K_right joined at distinguished vertices by an L-edge path."""
    if length < 1 or left < 2 or right < 2:
        raise ValueError("positive path length and endpoint cliques of order >=2 required")
    graph = nx.Graph()
    path = list(range(length + 1))
    graph.add_edges_from(zip(path, path[1:]))
    next_vertex = length + 1
    left_vertices = [path[0], *range(next_vertex, next_vertex + left - 1)]
    next_vertex += left - 1
    right_vertices = [path[-1], *range(next_vertex, next_vertex + right - 1)]
    graph.add_edges_from(combinations(left_vertices, 2))
    graph.add_edges_from(combinations(right_vertices, 2))
    return graph


def adjacency_masks(graph: nx.Graph) -> tuple[list[int], int]:
    nodes = list(graph)
    if nodes != list(range(len(nodes))):
        raise ValueError("graphs must be labelled consecutively from zero")
    masks = [sum(1 << u for u in graph.neighbors(v)) for v in nodes]
    return masks, (1 << len(nodes)) - 1


def mask_connected(mask: int, adjacency: list[int]) -> bool:
    if not mask:
        return False
    seen = 0
    frontier = mask & -mask
    while frontier:
        seen |= frontier
        neighbors = 0
        work = frontier
        while work:
            bit = work & -work
            work ^= bit
            neighbors |= adjacency[bit.bit_length() - 1]
        frontier = neighbors & mask & ~seen
    return seen == mask


def mask_bipartite(mask: int, adjacency: list[int]) -> bool:
    uncolored = mask
    color1 = 0
    while uncolored:
        seed = uncolored & -uncolored
        side0 = seed
        side1 = 0
        frontier = seed
        parity = 0
        colored = seed
        while frontier:
            next_frontier = 0
            work = frontier
            while work:
                bit = work & -work
                work ^= bit
                next_frontier |= adjacency[bit.bit_length() - 1]
            next_frontier &= mask
            same_side = side0 if parity == 0 else side1
            if next_frontier & same_side:
                return False
            new = next_frontier & ~colored
            if parity == 0:
                side1 |= new
            else:
                side0 |= new
            colored |= new
            frontier = new
            parity ^= 1
        uncolored &= ~colored
    return True


def connected_domination_number(graph: nx.Graph) -> int:
    adjacency, full = adjacency_masks(graph)
    closed = [adjacency[v] | (1 << v) for v in range(len(adjacency))]
    vertices = range(len(adjacency))
    with alarm():
        for size in range(1, len(adjacency) + 1):
            for chosen in combinations(vertices, size):
                mask = sum(1 << v for v in chosen)
                dominated = 0
                for v in chosen:
                    dominated |= closed[v]
                if dominated == full and mask_connected(mask, adjacency):
                    return size
    raise AssertionError("connected graph has no connected dominating set")


def bipartite_number(graph: nx.Graph) -> int:
    adjacency, full = adjacency_masks(graph)
    vertices = range(len(adjacency))
    with alarm():
        for removed_size in range(len(adjacency) + 1):
            for removed in combinations(vertices, removed_size):
                removed_mask = sum(1 << v for v in removed)
                if mask_bipartite(full ^ removed_mask, adjacency):
                    return len(adjacency) - removed_size
    raise AssertionError("empty induced graph is bipartite")


def independence_number_mask(mask: int, adjacency: list[int]) -> int:
    best = 0

    def visit(candidates: int, size: int) -> None:
        nonlocal best
        if size + popcount(candidates) <= best:
            return
        if not candidates:
            best = max(best, size)
            return
        bit = candidates & -candidates
        vertex = bit.bit_length() - 1
        visit(candidates & ~bit & ~adjacency[vertex], size + 1)
        visit(candidates & ~bit, size)

    visit(mask, 0)
    return best


def independence_number(graph: nx.Graph) -> int:
    adjacency, full = adjacency_masks(graph)
    with alarm():
        return independence_number_mask(full, adjacency)


def lambda_max(graph: nx.Graph) -> int:
    adjacency, _ = adjacency_masks(graph)
    with alarm():
        return max(independence_number_mask(adjacency[v], adjacency) for v in graph)


def graph_square(graph: nx.Graph) -> nx.Graph:
    square = nx.Graph()
    square.add_nodes_from(graph)
    distances = dict(nx.all_pairs_shortest_path_length(graph, cutoff=2))
    square.add_edges_from(
        (u, v)
        for u, v in combinations(graph, 2)
        if distances[u].get(v, 3) <= 2
    )
    return square


def periphery(graph: nx.Graph) -> set[int]:
    eccentricities = nx.eccentricity(graph)
    maximum = max(eccentricities.values())
    return {v for v, value in eccentricities.items() if value == maximum}


def even_distance_counts(graph: nx.Graph) -> list[int]:
    distances = dict(nx.all_pairs_shortest_path_length(graph))
    return [sum(distance % 2 == 0 for distance in distances[v].values()) for v in graph]


@dataclass(frozen=True)
class Profile:
    name: str
    n: int
    m: int
    graph6: str
    gamma_c: int
    Ls: int
    b: int
    alpha: int
    lambda_max: int
    even_min_self: int
    even_max_self: int
    diameter: int
    square_periphery: tuple[int, ...]
    delta_B_square_in_square: int
    delta_B_square_in_graph: int
    chi_bipartite: int
    T173: int
    R169: int
    R174: int
    R180_self: int
    R180_without_self: int
    R182_square: int
    R182_graph: int


def profile(graph: nx.Graph, name: str) -> Profile:
    if len(graph) < 2 or not nx.is_connected(graph):
        raise ValueError("profile requires a connected graph of order at least two")
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    n = len(graph)
    gamma_c = connected_domination_number(graph)
    leaves = n if n == 2 else n - gamma_c
    bip = bipartite_number(graph)
    alpha = independence_number(graph)
    local_independence = lambda_max(graph)
    evens = even_distance_counts(graph)
    diameter = nx.diameter(graph)
    square = graph_square(graph)
    boundary = periphery(square)
    delta_square = max(square.degree(v) for v in boundary)
    delta_graph = max(graph.degree(v) for v in boundary)
    chi_bip = int(nx.is_bipartite(graph))
    theorem = leaves + bip - (n + 1 + chi_bip)
    values = Profile(
        name=name,
        n=n,
        m=graph.number_of_edges(),
        graph6=nx.to_graph6_bytes(graph, header=False).decode().strip(),
        gamma_c=gamma_c,
        Ls=leaves,
        b=bip,
        alpha=alpha,
        lambda_max=local_independence,
        even_min_self=min(evens),
        even_max_self=max(evens),
        diameter=diameter,
        square_periphery=tuple(sorted(boundary)),
        delta_B_square_in_square=delta_square,
        delta_B_square_in_graph=delta_graph,
        chi_bipartite=chi_bip,
        T173=theorem,
        R169=leaves - (1 + max(evens) - min(evens)),
        R174=leaves + bip - (n + local_independence - 1),
        R180_self=leaves + bip - (1 + alpha + max(evens)),
        R180_without_self=leaves + bip - (1 + alpha + max(evens) - 1),
        R182_square=leaves + bip - (delta_square + diameter),
        R182_graph=leaves + bip - (delta_graph + diameter),
    )
    assert values.T173 >= 0, "proved WOWII 173 baseline failed"
    assert values.R174 == theorem + 2 + chi_bip - local_independence
    assert values.R180_self == theorem + n + chi_bip - alpha - max(evens)
    assert values.R182_square == theorem + n + 1 + chi_bip - delta_square - diameter
    assert values.R182_graph == theorem + n + 1 + chi_bip - delta_graph - diameter
    return values


def controls() -> Iterator[tuple[str, nx.Graph]]:
    for index, graph in enumerate(nx.graph_atlas_g()):
        if 2 <= len(graph) <= 7 and nx.is_connected(graph):
            yield f"atlas_{index}", nx.convert_node_labels_to_integers(graph)
    for n in range(5, 10):
        yield f"C{n}", nx.cycle_graph(n)
    yield "P7", nx.path_graph(7)
    yield "Petersen", nx.petersen_graph()
    yield "K3,3", nx.complete_bipartite_graph(3, 3)
    yield "K7", nx.complete_graph(7)
    for leaves in range(2, 9):
        yield f"K1,{leaves}", nx.star_graph(leaves)
    for left in range(1, 6):
        for right in range(left, 6):
            yield f"K{left},{right}", nx.complete_bipartite_graph(left, right)


READING_FIELDS = (
    "R169", "R174", "R180_self", "R180_without_self",
    "R182_square", "R182_graph",
)


def run_gate() -> list[Profile]:
    seen: set[str] = set()
    checked: list[Profile] = []
    for name, graph in controls():
        graph6 = nx.to_graph6_bytes(graph, header=False).decode().strip()
        if graph6 in seen:
            continue
        seen.add(graph6)
        candidate = profile(graph, name)
        failures = {field: getattr(candidate, field) for field in READING_FIELDS
                    if getattr(candidate, field) < 0}
        if failures:
            raise AssertionError(f"database gate rejected frozen reading on {name}: {failures}")
        checked.append(candidate)
    return checked


def automorphisms(graph: nx.Graph) -> list[dict[int, int]]:
    return list(nx.algorithms.isomorphism.GraphMatcher(graph, graph).isomorphisms_iter())


def edge_image(edge: tuple[int, int], permutation: dict[int, int]) -> tuple[int, int]:
    u, v = permutation[edge[0]], permutation[edge[1]]
    return (u, v) if u < v else (v, u)


def orbit_key(toggles: tuple[tuple[int, int], ...], autos: list[dict[int, int]]) -> tuple[tuple[int, int], ...]:
    return min(tuple(sorted(edge_image(edge, permutation) for edge in toggles))
               for permutation in autos)


def edit_orbit_representatives(base: nx.Graph) -> Iterator[tuple[tuple[tuple[int, int], ...], nx.Graph]]:
    possible = tuple(combinations(range(len(base)), 2))
    autos = automorphisms(base)
    seen: set[tuple[tuple[int, int], ...]] = set()
    for distance in (1, 2):
        for toggles in combinations(possible, distance):
            key = orbit_key(toggles, autos)
            if key in seen:
                continue
            seen.add(key)
            graph = base.copy()
            for u, v in key:
                if graph.has_edge(u, v):
                    graph.remove_edge(u, v)
                else:
                    graph.add_edge(u, v)
            yield key, graph


def edit_kind(base: nx.Graph, toggles: tuple[tuple[int, int], ...]) -> str:
    operations = ["del" if base.has_edge(*edge) else "add" for edge in toggles]
    return "+".join(sorted(operations))


def json_record(profile_value: Profile, **metadata) -> str:
    return json.dumps({**metadata, **asdict(profile_value)}, sort_keys=True)


def command_gate(_args: argparse.Namespace) -> None:
    started = time.monotonic()
    checked = run_gate()
    minima = {field: min(getattr(item, field) for item in checked) for field in READING_FIELDS}
    equality = {field: sum(getattr(item, field) == 0 for item in checked) for field in READING_FIELDS}
    print(json.dumps({"event": "gate", "unique_controls": len(checked),
                      "minima": minima, "equalities": equality,
                      "seconds": round(time.monotonic() - started, 6)}, sort_keys=True))


def command_endpoints(_args: argparse.Namespace) -> None:
    run_gate()
    for length in range(2, 11):
        for left in range(2, 6):
            for right in range(left, 6):
                graph = endpoint_clique_barbell(length, left, right)
                try:
                    item = profile(graph, f"K{left}-P{length}-K{right}")
                except OptimizationTimeout as exc:
                    print(json.dumps({"event": "timeout", "family": "endpoint",
                                      "length": length, "left": left, "right": right,
                                      "error": str(exc)}, sort_keys=True))
                    continue
                print(json_record(item, event="profile", family="endpoint",
                                  length=length, left=left, right=right))


def command_edits(args: argparse.Namespace) -> None:
    run_gate()
    length = args.length
    base = endpoint_clique_barbell(length)
    representatives = edit_orbit_representatives(base)
    for index, (toggles, graph) in enumerate(representatives, start=1):
        if not nx.is_connected(graph):
            print(json.dumps({"event": "not_applicable", "family": "edit",
                              "length": length, "index": index,
                              "toggles": toggles, "reason": "disconnected"}, sort_keys=True))
            continue
        try:
            item = profile(graph, f"D{length}_edit_{index}")
        except OptimizationTimeout as exc:
            print(json.dumps({"event": "timeout", "family": "edit",
                              "length": length, "index": index,
                              "toggles": toggles, "error": str(exc)}, sort_keys=True))
            continue
        print(json_record(item, event="profile", family="edit", length=length,
                          index=index, toggles=toggles,
                          edit_kind=edit_kind(base, toggles)))


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    subparsers = result.add_subparsers(dest="command", required=True)
    gate_parser = subparsers.add_parser("gate")
    gate_parser.set_defaults(function=command_gate)
    endpoint_parser = subparsers.add_parser("endpoints")
    endpoint_parser.set_defaults(function=command_endpoints)
    edit_parser = subparsers.add_parser("edits")
    edit_parser.add_argument("length", type=int, choices=(6, 8, 10))
    edit_parser.set_defaults(function=command_edits)
    return result


def main() -> None:
    args = parser().parse_args()
    args.function(args)


if __name__ == "__main__":
    main()
