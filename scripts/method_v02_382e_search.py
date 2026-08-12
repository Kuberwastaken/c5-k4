#!/usr/bin/env python3
"""Exact bounded search for Method v0.2 Trial F, WOWII 382e.

The conjectured residuals are

    Maxine_best(G) + gamma(G) - gamma_2(G)
    Maxine_det(G)  + gamma(G) - gamma_2(G).

Maxine repeatedly deletes a maximum-degree vertex until the remainder is
discrete.  ``best`` maximizes the number of survivors over all ties;
``det`` deletes the least-labelled maximum-degree vertex at each tie.

This helper deliberately separates the historical-control gate from later
construction stages.  All set parameters are exhaustive and integral.
"""

from __future__ import annotations

import argparse
from functools import lru_cache
from itertools import combinations, product
import json
import random
import sys
import time

import networkx as nx


def popcount(value: int) -> int:
    """Python 3.9-compatible population count."""
    return bin(value).count("1")


def normalized_adjacency(graph: nx.Graph) -> tuple[int, ...]:
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    return tuple(
        sum(1 << other for other in graph.neighbors(vertex))
        for vertex in range(len(graph))
    )


def minimum_subset_parameter(adjacency: tuple[int, ...], kind: str) -> int:
    """Return exact domination or 2-domination number."""
    n = len(adjacency)
    all_vertices = (1 << n) - 1
    for size in range(1, n + 1):
        for chosen_tuple in combinations(range(n), size):
            chosen = sum(1 << vertex for vertex in chosen_tuple)
            valid = True
            for vertex in range(n):
                if (chosen >> vertex) & 1:
                    continue
                neighbors_chosen = popcount(adjacency[vertex] & chosen)
                threshold = 1 if kind == "gamma" else 2
                if neighbors_chosen < threshold:
                    valid = False
                    break
            if valid:
                return size
    raise AssertionError(f"no {kind} set")


def independence_number(adjacency: tuple[int, ...]) -> int:
    n = len(adjacency)
    for size in range(n, -1, -1):
        for chosen_tuple in combinations(range(n), size):
            chosen = sum(1 << vertex for vertex in chosen_tuple)
            if all(adjacency[vertex] & chosen == 0 for vertex in chosen_tuple):
                return size
    raise AssertionError("empty set is independent")


def maxine_values(adjacency: tuple[int, ...]) -> tuple[int, int]:
    """Return (deterministic, best-tie) survivor counts exactly."""
    initial = (1 << len(adjacency)) - 1

    def degrees(state: int) -> list[tuple[int, int]]:
        return [
            (vertex, popcount(adjacency[vertex] & state))
            for vertex in range(len(adjacency))
            if (state >> vertex) & 1
        ]

    state = initial
    while True:
        degree_list = degrees(state)
        maximum = max((degree for _, degree in degree_list), default=0)
        if maximum == 0:
            deterministic = popcount(state)
            break
        vertex = min(vertex for vertex, degree in degree_list if degree == maximum)
        state ^= 1 << vertex

    @lru_cache(maxsize=None)
    def best(state: int) -> int:
        degree_list = degrees(state)
        maximum = max((degree for _, degree in degree_list), default=0)
        if maximum == 0:
            return popcount(state)
        return max(
            best(state ^ (1 << vertex))
            for vertex, degree in degree_list
            if degree == maximum
        )

    return deterministic, best(initial)


def evaluate(graph: nx.Graph) -> dict[str, int | str]:
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    adjacency = normalized_adjacency(graph)
    gamma = minimum_subset_parameter(adjacency, "gamma")
    gamma_2 = minimum_subset_parameter(adjacency, "gamma_2")
    alpha = independence_number(adjacency)
    maxine_det, maxine_best = maxine_values(adjacency)
    return {
        "n": len(graph),
        "m": graph.number_of_edges(),
        "g6": nx.to_graph6_bytes(graph, header=False).decode().strip(),
        "gamma": gamma,
        "gamma_2": gamma_2,
        "alpha": alpha,
        "maxine_det": maxine_det,
        "maxine_best": maxine_best,
        "residual_det": maxine_det + gamma - gamma_2,
        "residual_best": maxine_best + gamma - gamma_2,
    }


def connected_atlas_controls() -> list[tuple[str, nx.Graph]]:
    controls = [
        (f"atlas#{index}", graph)
        for index, graph in enumerate(nx.graph_atlas_g())
        if 3 <= len(graph) <= 7 and nx.is_connected(graph)
    ]
    named = [
        (f"C{order}", nx.cycle_graph(order)) for order in range(5, 10)
    ]
    named.extend(
        [
            ("P7", nx.path_graph(7)),
            ("Petersen", nx.petersen_graph()),
            ("K3,3", nx.complete_bipartite_graph(3, 3)),
            ("K7", nx.complete_graph(7)),
            ("star7", nx.star_graph(6)),
            ("K2,5", nx.complete_bipartite_graph(2, 5)),
        ]
    )
    return controls + named


def graph6_stream(path: str):
    stream = sys.stdin.buffer if path == "-" else open(path, "rb")
    try:
        for line in stream:
            line = line.strip()
            if line and not line.startswith(b">"):
                yield nx.from_graph6_bytes(line)
    finally:
        if path != "-":
            stream.close()


def run_gate() -> dict:
    started = time.monotonic()
    minimum = {"det": None, "best": None}
    tight = {"det": 0, "best": 0}
    violations = []
    checked = 0
    for name, graph in connected_atlas_controls():
        record = evaluate(graph)
        checked += 1
        for reading in ("det", "best"):
            residual = int(record[f"residual_{reading}"])
            old = minimum[reading]
            minimum[reading] = residual if old is None else min(old, residual)
            tight[reading] += residual == 0
            if residual < 0:
                violations.append({"name": name, "reading": reading, **record})
    return {
        "stage": "gate",
        "checked": checked,
        "minimum_residual": minimum,
        "tight": tight,
        "violations": violations,
        "seconds": time.monotonic() - started,
    }


def run_catalogue(path: str, time_cap: float) -> dict:
    started = time.monotonic()
    checked = 0
    minimum = {"det": None, "best": None}
    tight = {"det": 0, "best": 0}
    deficits = 0
    crossings = []
    timed_out = False
    for graph in graph6_stream(path):
        if time.monotonic() - started > time_cap:
            timed_out = True
            break
        if len(graph) <= 2 or not nx.is_connected(graph):
            continue
        record = evaluate(graph)
        checked += 1
        deficits += int(record["maxine_best"]) < int(record["alpha"])
        for reading in ("det", "best"):
            residual = int(record[f"residual_{reading}"])
            old = minimum[reading]
            minimum[reading] = residual if old is None else min(old, residual)
            tight[reading] += residual == 0
            if residual < 0:
                crossings.append({"reading": reading, **record})
    return {
        "stage": "catalogue",
        "path": path,
        "checked": checked,
        "maxine_best_below_alpha": deficits,
        "minimum_residual": minimum,
        "tight": tight,
        "crossings": crossings,
        "timed_out": timed_out,
        "seconds": time.monotonic() - started,
    }


def quotient_set_parameter(
    quotient: nx.Graph, weights: tuple[int, ...], substitution: str, kind: str
) -> int:
    """Compute gamma or gamma_2 on a twin-class substitution exactly."""
    quotient = nx.convert_node_labels_to_integers(quotient, ordering="sorted")
    order = len(quotient)
    if substitution == "clique":
        choices = [tuple(range(min(weight, 2) + 1)) for weight in weights]
    elif kind == "gamma":
        choices = [tuple(sorted({0, 1, weight})) for weight in weights]
    else:
        choices = [tuple(sorted({0, 1, min(2, weight), weight})) for weight in weights]

    best = sum(weights)
    threshold = 1 if kind == "gamma" else 2
    for selected in product(*choices):
        size = sum(selected)
        if size >= best:
            continue
        valid = True
        for vertex in range(order):
            if selected[vertex] == weights[vertex]:
                continue
            neighbor_count = sum(selected[other] for other in quotient.neighbors(vertex))
            if substitution == "clique":
                neighbor_count += selected[vertex]
            if neighbor_count < threshold:
                valid = False
                break
        if valid:
            best = size
    return best


class MaxineTimeout(RuntimeError):
    pass


def quotient_maxine_det(
    quotient: nx.Graph, weights: tuple[int, ...], substitution: str
) -> int:
    """One exact least-label Maxine performance on twin classes."""
    quotient = nx.convert_node_labels_to_integers(quotient, ordering="sorted")
    offsets = []
    offset = 0
    for weight in weights:
        offsets.append(offset)
        offset += weight

    def degree(state: tuple[int, ...], vertex: int) -> int:
        result = sum(state[other] for other in quotient.neighbors(vertex))
        if substitution == "clique":
            result += state[vertex] - 1
        return result

    state = weights
    while True:
        active = [vertex for vertex in range(len(quotient)) if state[vertex]]
        maximum = max((degree(state, vertex) for vertex in active), default=0)
        if maximum == 0:
            return sum(state)
        maxima = [vertex for vertex in active if degree(state, vertex) == maximum]
        vertex = min(
            maxima,
            key=lambda item: offsets[item] + weights[item] - state[item],
        )
        mutable = list(state)
        mutable[vertex] -= 1
        state = tuple(mutable)


def quotient_maxine_values(
    quotient: nx.Graph,
    weights: tuple[int, ...],
    substitution: str,
    time_cap: float,
) -> tuple[int, int, int]:
    """Return (det, best, states) for a substitution without expansion."""
    quotient = nx.convert_node_labels_to_integers(quotient, ordering="sorted")
    order = len(quotient)
    started = time.monotonic()
    offsets = []
    offset = 0
    for weight in weights:
        offsets.append(offset)
        offset += weight

    def degree(state: tuple[int, ...], vertex: int) -> int:
        result = sum(state[other] for other in quotient.neighbors(vertex))
        if substitution == "clique":
            result += state[vertex] - 1
        return result

    def active_maxima(state: tuple[int, ...]) -> tuple[list[int], int]:
        active = [vertex for vertex in range(order) if state[vertex]]
        maximum = max((degree(state, vertex) for vertex in active), default=0)
        return [vertex for vertex in active if degree(state, vertex) == maximum], maximum

    deterministic = quotient_maxine_det(quotient, weights, substitution)

    states = 0

    @lru_cache(maxsize=None)
    def best(state: tuple[int, ...]) -> int:
        nonlocal states
        states += 1
        if states % 1024 == 0 and time.monotonic() - started > time_cap:
            raise MaxineTimeout
        maxima, maximum = active_maxima(state)
        if maximum == 0:
            return sum(state)
        answers = []
        for vertex in maxima:
            mutable = list(state)
            mutable[vertex] -= 1
            answers.append(best(tuple(mutable)))
        return max(answers)

    return deterministic, best(weights), states


def evaluate_substitution(
    quotient: nx.Graph,
    weights: tuple[int, ...],
    substitution: str,
    maxine_time_cap: float,
) -> dict:
    gamma = quotient_set_parameter(quotient, weights, substitution, "gamma")
    gamma_2 = quotient_set_parameter(quotient, weights, substitution, "gamma_2")
    maxine_det, maxine_best, states = quotient_maxine_values(
        quotient, weights, substitution, maxine_time_cap
    )
    return {
        "quotient_n": len(quotient),
        "quotient_m": quotient.number_of_edges(),
        "quotient_g6": nx.to_graph6_bytes(quotient, header=False).decode().strip(),
        "substitution": substitution,
        "weights": weights,
        "n": sum(weights),
        "gamma": gamma,
        "gamma_2": gamma_2,
        "maxine_det": maxine_det,
        "maxine_best": maxine_best,
        "residual_det": maxine_det + gamma - gamma_2,
        "residual_best": maxine_best + gamma - gamma_2,
        "maxine_states": states,
    }


def substitution_alpha(
    quotient: nx.Graph, weights: tuple[int, ...], substitution: str
) -> int:
    adjacency = normalized_adjacency(quotient)
    order = len(quotient)
    best = 0
    for subset in range(1 << order):
        if any(
            ((subset >> vertex) & 1) and adjacency[vertex] & subset
            for vertex in range(order)
        ):
            continue
        if substitution == "clique":
            value = popcount(subset)
        else:
            value = sum(weights[vertex] for vertex in range(order) if (subset >> vertex) & 1)
        best = max(best, value)
    return best


def single_bundle_templates(order: int, max_order: int) -> list[tuple[int, ...]]:
    templates = {tuple([1] * order)}
    for uniform in range(2, max_order // order + 1):
        templates.add(tuple([uniform] * order))
    for vertex in range(order):
        for weight in range(2, max_order - order + 2):
            values = [1] * order
            values[vertex] = weight
            templates.add(tuple(values))
    return sorted(templates, key=lambda item: (sum(item), item))


def run_wall_substitutions(path: str, max_order: int, solve_cap: float) -> dict:
    """Search single bundles over quotients lying on the unweighted wall."""
    started = time.monotonic()
    quotients = list(graph6_stream(path))
    wall_quotients = []
    for quotient in quotients:
        if len(quotient) <= 2 or not nx.is_connected(quotient):
            continue
        direct = evaluate(quotient)
        if direct["residual_best"] == 0 or direct["maxine_best"] < direct["alpha"]:
            wall_quotients.append(quotient)

    templates_checked = 0
    theorem_pruned = 0
    exact_checked = 0
    timeouts = []
    crossings = []
    minimum = {"det": None, "best": None}
    for quotient in wall_quotients:
        for weights in single_bundle_templates(len(quotient), max_order):
            for substitution in ("false", "clique"):
                templates_checked += 1
                alpha = substitution_alpha(quotient, weights, substitution)
                maxine_det = quotient_maxine_det(quotient, weights, substitution)
                if maxine_det >= alpha:
                    theorem_pruned += 1
                    continue
                try:
                    _, maxine_best, states = quotient_maxine_values(
                        quotient, weights, substitution, solve_cap
                    )
                except MaxineTimeout:
                    timeouts.append(
                        {
                            "quotient_g6": nx.to_graph6_bytes(quotient, header=False).decode().strip(),
                            "substitution": substitution,
                            "weights": weights,
                        }
                    )
                    continue
                if maxine_best >= alpha:
                    theorem_pruned += 1
                    continue
                gamma = quotient_set_parameter(quotient, weights, substitution, "gamma")
                gamma_2 = quotient_set_parameter(quotient, weights, substitution, "gamma_2")
                exact_checked += 1
                record = {
                    "quotient_n": len(quotient),
                    "quotient_m": quotient.number_of_edges(),
                    "quotient_g6": nx.to_graph6_bytes(quotient, header=False).decode().strip(),
                    "substitution": substitution,
                    "weights": weights,
                    "n": sum(weights),
                    "alpha": alpha,
                    "gamma": gamma,
                    "gamma_2": gamma_2,
                    "maxine_det": maxine_det,
                    "maxine_best": maxine_best,
                    "residual_det": maxine_det + gamma - gamma_2,
                    "residual_best": maxine_best + gamma - gamma_2,
                    "maxine_states": states,
                }
                for reading in ("det", "best"):
                    residual = int(record[f"residual_{reading}"])
                    old = minimum[reading]
                    minimum[reading] = residual if old is None else min(old, residual)
                if record["residual_det"] < 0 or record["residual_best"] < 0:
                    crossings.append(record)
    return {
        "stage": "wall_substitutions",
        "path": path,
        "quotients": len(quotients),
        "wall_or_deficit_quotients": len(wall_quotients),
        "max_order": max_order,
        "solve_cap": solve_cap,
        "templates_checked": templates_checked,
        "theorem_pruned": theorem_pruned,
        "exact_checked_after_prune": exact_checked,
        "minimum_residual_after_prune": minimum,
        "timeouts": timeouts,
        "crossings": crossings,
        "seconds": time.monotonic() - started,
    }


def random_positive_composition(total: int, parts: int, rng: random.Random) -> tuple[int, ...]:
    if parts == 1:
        return (total,)
    cuts = sorted(rng.sample(range(1, total), parts - 1))
    points = (0, *cuts, total)
    return tuple(points[index + 1] - points[index] for index in range(parts))


def run_sample_substitutions(
    path: str, max_order: int, trials: int, seed: int, solve_cap: float
) -> dict:
    """Seeded coverage of unrestricted positive weight vectors."""
    started = time.monotonic()
    rng = random.Random(seed)
    quotients = [
        graph for graph in graph6_stream(path)
        if 3 <= len(graph) <= 8 and nx.is_connected(graph)
    ]
    theorem_pruned = 0
    exact_checked = 0
    timeouts = []
    crossings = []
    minimum = {"det": None, "best": None}
    for trial in range(trials):
        quotient = quotients[rng.randrange(len(quotients))]
        total = rng.randint(len(quotient), max_order)
        weights = random_positive_composition(total, len(quotient), rng)
        substitution = ("false", "clique")[rng.randrange(2)]
        alpha = substitution_alpha(quotient, weights, substitution)
        maxine_det = quotient_maxine_det(quotient, weights, substitution)
        if maxine_det >= alpha:
            theorem_pruned += 1
            continue
        try:
            _, maxine_best, states = quotient_maxine_values(
                quotient, weights, substitution, solve_cap
            )
        except MaxineTimeout:
            timeouts.append(
                {
                    "trial": trial,
                    "quotient_g6": nx.to_graph6_bytes(quotient, header=False).decode().strip(),
                    "substitution": substitution,
                    "weights": weights,
                }
            )
            continue
        if maxine_best >= alpha:
            theorem_pruned += 1
            continue
        gamma = quotient_set_parameter(quotient, weights, substitution, "gamma")
        gamma_2 = quotient_set_parameter(quotient, weights, substitution, "gamma_2")
        exact_checked += 1
        record = {
            "trial": trial,
            "quotient_g6": nx.to_graph6_bytes(quotient, header=False).decode().strip(),
            "substitution": substitution,
            "weights": weights,
            "n": sum(weights),
            "alpha": alpha,
            "gamma": gamma,
            "gamma_2": gamma_2,
            "maxine_det": maxine_det,
            "maxine_best": maxine_best,
            "residual_det": maxine_det + gamma - gamma_2,
            "residual_best": maxine_best + gamma - gamma_2,
            "maxine_states": states,
        }
        for reading in ("det", "best"):
            residual = int(record[f"residual_{reading}"])
            old = minimum[reading]
            minimum[reading] = residual if old is None else min(old, residual)
        if record["residual_det"] < 0 or record["residual_best"] < 0:
            crossings.append(record)
    return {
        "stage": "sample_substitutions",
        "path": path,
        "quotients": len(quotients),
        "max_order": max_order,
        "trials": trials,
        "seed": seed,
        "solve_cap": solve_cap,
        "theorem_pruned": theorem_pruned,
        "exact_checked_after_prune": exact_checked,
        "minimum_residual_after_prune": minimum,
        "timeouts": timeouts,
        "crossings": crossings,
        "seconds": time.monotonic() - started,
    }


def structured_quotients() -> list[tuple[str, nx.Graph]]:
    records: list[tuple[str, nx.Graph]] = []
    for leaves in range(2, 7):
        graph = nx.complete_bipartite_graph(2, leaves)
        records.append((f"double_hub_{leaves}", graph))
        graph_with_edge = graph.copy()
        graph_with_edge.add_edge(0, 1)
        records.append((f"double_hub_edge_{leaves}", graph_with_edge))
    for order in range(3, 9):
        records.append((f"path_{order}", nx.path_graph(order)))
    # Three internally disjoint u-v paths, each of length 2 or 3.
    for lengths in product((2, 3), repeat=3):
        graph = nx.Graph()
        graph.add_nodes_from((0, 1))
        next_vertex = 2
        for length in lengths:
            path = [0]
            for _ in range(length - 1):
                path.append(next_vertex)
                next_vertex += 1
            path.append(1)
            nx.add_path(graph, path)
        if len(graph) <= 8:
            records.append((f"theta_{''.join(map(str, lengths))}", graph))
    unique = {}
    for name, graph in records:
        key = nx.weisfeiler_lehman_graph_hash(graph)
        unique.setdefault(key, (name, nx.convert_node_labels_to_integers(graph)))
    return list(unique.values())


def weight_templates(order: int, max_order: int, two_bundle_cap: int) -> list[tuple[int, ...]]:
    templates = {tuple([1] * order)}
    for uniform in range(2, max_order // order + 1):
        templates.add(tuple([uniform] * order))
    for vertex in range(order):
        for weight in range(2, max_order - order + 2):
            values = [1] * order
            values[vertex] = weight
            templates.add(tuple(values))
    for first, second in combinations(range(order), 2):
        for a in range(2, two_bundle_cap + 1):
            for b in range(2, two_bundle_cap + 1):
                if a + b + order - 2 > max_order:
                    continue
                values = [1] * order
                values[first] = a
                values[second] = b
                templates.add(tuple(values))
    return sorted(templates, key=lambda item: (sum(item), item))


def run_structured(max_order: int, two_bundle_cap: int, solve_cap: float) -> dict:
    started = time.monotonic()
    checked = 0
    timeouts = []
    crossings = []
    minimum = {"det": None, "best": None}
    tight = {"det": 0, "best": 0}
    family_counts = {}
    for name, quotient in structured_quotients():
        family_counts[name] = 0
        for weights in weight_templates(len(quotient), max_order, two_bundle_cap):
            for substitution in ("false", "clique"):
                try:
                    record = evaluate_substitution(
                        quotient, weights, substitution, solve_cap
                    )
                except MaxineTimeout:
                    timeouts.append(
                        {"name": name, "substitution": substitution, "weights": weights}
                    )
                    continue
                checked += 1
                family_counts[name] += 1
                for reading in ("det", "best"):
                    residual = int(record[f"residual_{reading}"])
                    old = minimum[reading]
                    minimum[reading] = residual if old is None else min(old, residual)
                    tight[reading] += residual == 0
                if record["residual_det"] < 0 or record["residual_best"] < 0:
                    crossings.append({"name": name, **record})
    return {
        "stage": "structured",
        "max_order": max_order,
        "two_bundle_cap": two_bundle_cap,
        "solve_cap": solve_cap,
        "checked": checked,
        "family_counts": family_counts,
        "minimum_residual": minimum,
        "tight": tight,
        "timeouts": timeouts,
        "crossings": crossings,
        "seconds": time.monotonic() - started,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="stage", required=True)
    subparsers.add_parser("gate")
    catalogue = subparsers.add_parser("catalogue")
    catalogue.add_argument("--graph6", required=True)
    catalogue.add_argument("--time-cap", type=float, default=60.0)
    structured = subparsers.add_parser("structured")
    structured.add_argument("--max-order", type=int, default=60)
    structured.add_argument("--two-bundle-cap", type=int, default=12)
    structured.add_argument("--solve-cap", type=float, default=60.0)
    wall = subparsers.add_parser("wall-substitutions")
    wall.add_argument("--graph6", required=True)
    wall.add_argument("--max-order", type=int, default=60)
    wall.add_argument("--solve-cap", type=float, default=60.0)
    sample = subparsers.add_parser("sample-substitutions")
    sample.add_argument("--graph6", required=True)
    sample.add_argument("--max-order", type=int, default=60)
    sample.add_argument("--trials", type=int, default=10000)
    sample.add_argument("--seed", type=int, default=382)
    sample.add_argument("--solve-cap", type=float, default=60.0)
    args = parser.parse_args()
    if args.stage == "gate":
        result = run_gate()
    elif args.stage == "catalogue":
        result = run_catalogue(args.graph6, args.time_cap)
    elif args.stage == "structured":
        result = run_structured(args.max_order, args.two_bundle_cap, args.solve_cap)
    elif args.stage == "wall-substitutions":
        result = run_wall_substitutions(args.graph6, args.max_order, args.solve_cap)
    else:
        result = run_sample_substitutions(
            args.graph6, args.max_order, args.trials, args.seed, args.solve_cap
        )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
