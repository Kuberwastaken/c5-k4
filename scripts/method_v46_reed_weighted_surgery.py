#!/usr/bin/env python3
"""Frozen v46 Reed-bound trial: Atlas gate and weighted-C5 edge surgery.

This script deliberately has two modes so that the database gate can be
recorded before any prospective-family evaluation.  It uses exact finite
search throughout; the weighted-C5 formulas are only an enumeration prefilter.
"""

from __future__ import annotations

import argparse
import itertools
import json
from dataclasses import dataclass
from typing import Iterable

import networkx as nx


def popcount(value: int) -> int:
    return bin(value).count("1")


@dataclass
class ExactProfile:
    n: int
    m: int
    chi: int
    coloring: list[int]
    coloring_states: dict[str, int]
    omega: int
    clique: list[int]
    clique_states: int
    delta: int
    max_degree_vertex: int | None

    @property
    def slack(self) -> int:
        return self.omega + self.delta + 2 - 2 * self.chi

    def as_dict(self) -> dict:
        return {
            "n": self.n,
            "m": self.m,
            "chi": self.chi,
            "coloring": self.coloring,
            "coloring_states": self.coloring_states,
            "omega": self.omega,
            "clique": self.clique,
            "clique_states": self.clique_states,
            "delta": self.delta,
            "max_degree_vertex": self.max_degree_vertex,
            "slack": self.slack,
        }


def normalized_graph(graph: nx.Graph) -> nx.Graph:
    return nx.convert_node_labels_to_integers(nx.Graph(graph), ordering="sorted")


def adjacency_masks(graph: nx.Graph) -> list[int]:
    graph = normalized_graph(graph)
    masks = [0] * graph.number_of_nodes()
    for u, v in graph.edges():
        masks[u] |= 1 << v
        masks[v] |= 1 << u
    return masks


def greedy_dsatur(adj: list[int]) -> list[int]:
    n = len(adj)
    colors = [-1] * n
    neighbor_colors = [set() for _ in range(n)]
    degrees = [popcount(x) for x in adj]
    for _ in range(n):
        v = max(
            (x for x in range(n) if colors[x] < 0),
            key=lambda x: (len(neighbor_colors[x]), degrees[x], -x),
        )
        forbidden = neighbor_colors[v]
        color = 0
        while color in forbidden:
            color += 1
        colors[v] = color
        for u in range(n):
            if colors[u] < 0 and ((adj[v] >> u) & 1):
                neighbor_colors[u].add(color)
    return colors


def fixed_k_coloring(adj: list[int], k: int) -> tuple[list[int] | None, int]:
    """Exact deterministic DSATUR feasibility search for a k-coloring."""
    n = len(adj)
    colors = [-1] * n
    degrees = [popcount(x) for x in adj]
    states = 0

    def visit(colored: int, used: int) -> bool:
        nonlocal states
        states += 1
        if colored == n:
            return True

        best_v = -1
        best_key = (-1, -1, 0)
        best_forbidden = 0
        for v in range(n):
            if colors[v] >= 0:
                continue
            forbidden = 0
            mask = adj[v]
            while mask:
                bit = mask & -mask
                u = bit.bit_length() - 1
                if colors[u] >= 0:
                    forbidden |= 1 << colors[u]
                mask ^= bit
            key = (popcount(forbidden), degrees[v], -v)
            if key > best_key:
                best_key = key
                best_v = v
                best_forbidden = forbidden

        # Existing colors first; at most one new color breaks color symmetry.
        upper = min(k, used + 1)
        for color in range(upper):
            if (best_forbidden >> color) & 1:
                continue
            colors[best_v] = color
            if visit(colored + 1, max(used, color + 1)):
                return True
            colors[best_v] = -1
        return False

    if visit(0, 0):
        return colors.copy(), states
    return None, states


def maximum_clique(adj: list[int]) -> tuple[list[int], int]:
    """Exact maximum clique by Bron--Kerbosch-style branch and bound."""
    n = len(adj)
    best: list[int] = []
    states = 0

    def expand(current: list[int], candidates: int) -> None:
        nonlocal best, states
        states += 1
        if len(current) + popcount(candidates) <= len(best):
            return
        while candidates:
            if len(current) + popcount(candidates) <= len(best):
                return
            bit = candidates & -candidates
            v = bit.bit_length() - 1
            candidates ^= bit
            current.append(v)
            next_candidates = candidates & adj[v]
            if next_candidates:
                expand(current, next_candidates)
            elif len(current) > len(best):
                best = current.copy()
            current.pop()

    expand([], (1 << n) - 1)
    return best, states


def exact_profile(graph: nx.Graph) -> ExactProfile:
    graph = normalized_graph(graph)
    adj = adjacency_masks(graph)
    clique, clique_states = maximum_clique(adj)
    greedy = greedy_dsatur(adj) if adj else []
    upper = max(greedy, default=-1) + 1
    coloring_states: dict[str, int] = {}
    coloring = greedy
    chi = upper
    for k in range(len(clique), upper + 1):
        candidate, states = fixed_k_coloring(adj, k)
        coloring_states[str(k)] = states
        if candidate is not None:
            chi = k
            coloring = candidate
            break
    degrees = [degree for _, degree in graph.degree()]
    delta = max(degrees, default=0)
    max_vertex = degrees.index(delta) if degrees else None
    return ExactProfile(
        n=graph.number_of_nodes(),
        m=graph.number_of_edges(),
        chi=chi,
        coloring=coloring,
        coloring_states=coloring_states,
        omega=len(clique),
        clique=clique,
        clique_states=clique_states,
        delta=delta,
        max_degree_vertex=max_vertex,
    )


def valid_profile(graph: nx.Graph, profile: ExactProfile) -> bool:
    graph = normalized_graph(graph)
    if len(profile.coloring) != profile.n:
        return False
    if any(profile.coloring[u] == profile.coloring[v] for u, v in graph.edges()):
        return False
    if len(set(profile.coloring)) != profile.chi:
        return False
    if any(not graph.has_edge(u, v) for u, v in itertools.combinations(profile.clique, 2)):
        return False
    if len(profile.clique) != profile.omega:
        return False
    if profile.max_degree_vertex is not None and graph.degree(profile.max_degree_vertex) != profile.delta:
        return False
    return True


def induced_claw(graph: nx.Graph) -> list[int] | None:
    graph = normalized_graph(graph)
    for center in graph.nodes():
        neighbors = sorted(graph.neighbors(center))
        for leaves in itertools.combinations(neighbors, 3):
            if all(not graph.has_edge(a, b) for a, b in itertools.combinations(leaves, 2)):
                return [center, *leaves]
    return None


def weighted_c5(weights: tuple[int, ...]) -> tuple[nx.Graph, list[list[int]]]:
    graph = nx.Graph()
    bags: list[list[int]] = []
    cursor = 0
    for weight in weights:
        bag = list(range(cursor, cursor + weight))
        cursor += weight
        bags.append(bag)
        graph.add_nodes_from(bag)
        graph.add_edges_from(itertools.combinations(bag, 2))
    for i in range(5):
        graph.add_edges_from(itertools.product(bags[i], bags[(i + 1) % 5]))
    return graph, bags


def canonical_weights(weights: tuple[int, ...]) -> tuple[int, ...]:
    rotations = [weights[i:] + weights[:i] for i in range(5)]
    reverse = tuple(reversed(weights))
    rotations += [reverse[i:] + reverse[:i] for i in range(5)]
    return min(rotations)


def weighted_c5_formula(weights: tuple[int, ...]) -> tuple[int, int, int, int]:
    omega = max(weights[i] + weights[(i + 1) % 5] for i in range(5))
    delta = max(
        weights[i] - 1 + weights[(i - 1) % 5] + weights[(i + 1) % 5]
        for i in range(5)
    )
    chi = max(omega, (sum(weights) + 1) // 2)
    return chi, omega, delta, omega + delta + 2 - 2 * chi


def atlas_gate() -> dict:
    connected = [
        graph
        for graph in nx.graph_atlas_g()
        if 2 <= graph.number_of_nodes() <= 7 and nx.is_connected(graph)
    ]
    rows = []
    violations = []
    for index, graph in enumerate(connected):
        profile = exact_profile(graph)
        if not valid_profile(graph, profile):
            raise RuntimeError(f"invalid certificate on Atlas row {index}")
        row = {"atlas_index": index, **profile.as_dict()}
        rows.append(row)
        if profile.slack < 0:
            violations.append(row)

    controls: dict[str, dict] = {}
    named = {
        "K5": nx.complete_graph(5),
        "C5": nx.cycle_graph(5),
        "C7": nx.cycle_graph(7),
        "Petersen": nx.petersen_graph(),
        "C5[K2]": weighted_c5((2,) * 5)[0],
        "C5[K3]": weighted_c5((3,) * 5)[0],
        "C5[K4]": weighted_c5((4,) * 5)[0],
    }
    expected = {
        "K5": (5, 5, 4, 1),
        "C5": (3, 2, 2, 0),
        "C7": (3, 2, 2, 0),
        "Petersen": (3, 2, 3, 1),
        "C5[K2]": (5, 4, 5, 1),
        "C5[K3]": (8, 6, 8, 0),
        "C5[K4]": (10, 8, 11, 1),
    }
    for name, graph in named.items():
        profile = exact_profile(graph)
        if not valid_profile(graph, profile):
            raise RuntimeError(f"invalid control certificate for {name}")
        actual = (profile.chi, profile.omega, profile.delta, profile.slack)
        if actual != expected[name]:
            raise RuntimeError(f"control mismatch for {name}: {actual} != {expected[name]}")
        controls[name] = profile.as_dict()

    if len(connected) != 995:
        raise RuntimeError(f"expected 995 connected Atlas graphs, got {len(connected)}")
    return {
        "mode": "atlas",
        "graphs": len(rows),
        "violations": violations,
        "controls": controls,
        "certificate_totals": {
            "coloring_states": sum(sum(x["coloring_states"].values()) for x in rows),
            "clique_states": sum(x["clique_states"] for x in rows),
        },
    }


def family_trial() -> dict:
    canonical = sorted(
        {
            weights
            for weights in itertools.product(range(1, 7), repeat=5)
            if sum(weights) <= 24 and canonical_weights(weights) == weights
        }
    )
    equality_prefilter = [w for w in canonical if weighted_c5_formula(w)[3] == 0][:2000]
    bases: list[tuple[tuple[int, ...], ExactProfile]] = []
    for weights in equality_prefilter:
        graph, _ = weighted_c5(weights)
        profile = exact_profile(graph)
        formula = weighted_c5_formula(weights)
        if (profile.chi, profile.omega, profile.delta, profile.slack) != formula:
            raise RuntimeError(f"weighted-C5 formula mismatch at {weights}")
        if not valid_profile(graph, profile):
            raise RuntimeError(f"invalid base certificate at {weights}")
        bases.append((weights, profile))

    base_summaries = [
        {"weights": list(weights), "profile": profile.as_dict()}
        for weights, profile in bases
    ]

    generated = 0
    known_domain_stops = 0
    claw_profiles = 0
    crossings: list[dict] = []
    best: dict | None = None
    slack_histogram: dict[str, int] = {}
    compensation: dict[str, int] = {}
    distance_pairs = [(i, (i + 2) % 5) for i in range(5)]

    for weights, base_profile in bases:
        base, bags = weighted_c5(weights)
        for left, right in distance_pairs:
            if generated >= 10000 or claw_profiles >= 4000:
                break
            graph = base.copy()
            added_edge = (bags[left][0], bags[right][0])
            graph.add_edge(*added_edge)
            generated += 1
            claw = induced_claw(graph)
            if claw is None:
                known_domain_stops += 1
                continue
            profile = exact_profile(graph)
            claw_profiles += 1
            if not valid_profile(graph, profile):
                raise RuntimeError(f"invalid surgery certificate at {weights}/{left}-{right}")
            delta_chi = profile.chi - base_profile.chi
            delta_omega = profile.omega - base_profile.omega
            delta_delta = profile.delta - base_profile.delta
            pattern = f"dchi={delta_chi},domega={delta_omega},dDelta={delta_delta}"
            compensation[pattern] = compensation.get(pattern, 0) + 1
            slack_histogram[str(profile.slack)] = slack_histogram.get(str(profile.slack), 0) + 1
            row = {
                "weights": list(weights),
                "blob_pair": [left, right],
                "added_edge": list(added_edge),
                "claw": claw,
                "base": base_profile.as_dict(),
                "profile": profile.as_dict(),
                "coordinate_change": {
                    "chi": delta_chi,
                    "omega": delta_omega,
                    "delta": delta_delta,
                },
            }
            if best is None or (profile.slack, profile.n, weights, left) < (
                best["profile"]["slack"],
                best["profile"]["n"],
                tuple(best["weights"]),
                best["blob_pair"][0],
            ):
                best = row
            if profile.slack < 0:
                crossings.append(row)
                # A crossing contradicts a major open conjecture: stop immediately.
                return {
                    "mode": "family",
                    "status": "HALTED_NUMERICAL_CROSSING",
                    "canonical_weight_tuples": len(canonical),
                    "equality_bases": len(bases),
                    "base_summaries": base_summaries,
                    "generated": generated,
                    "known_domain_stops": known_domain_stops,
                    "claw_profiles": claw_profiles,
                    "crossings": crossings,
                    "best": best,
                    "slack_histogram": slack_histogram,
                    "compensation": compensation,
                }
        if generated >= 10000 or claw_profiles >= 4000:
            break

    return {
        "mode": "family",
        "status": "COMPLETE_NO_CROSSING",
        "canonical_weight_tuples": len(canonical),
        "equality_prefilter": len(equality_prefilter),
        "equality_bases": len(bases),
        "base_summaries": base_summaries,
        "generated": generated,
        "known_domain_stops": known_domain_stops,
        "claw_profiles": claw_profiles,
        "crossings": crossings,
        "best": best,
        "slack_histogram": slack_histogram,
        "compensation": compensation,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("atlas", "family"))
    parser.add_argument("--output")
    args = parser.parse_args()
    result = atlas_gate() if args.mode == "atlas" else family_trial()
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as stream:
            stream.write(rendered + "\n")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
