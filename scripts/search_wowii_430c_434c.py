#!/usr/bin/env python3
"""Method-v0.1 bounded search for WOWII 430c and 434c.

The discovery path uses quotient formulas for positive clique blow-ups.  Any
candidate is replayed on its expanded NetworkX graph by separate routines.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import time
from dataclasses import asdict, dataclass
from itertools import combinations
from pathlib import Path
from typing import Iterable

import networkx as nx


DEFAULT_SEED = 430434
DEFAULT_LIMIT = 250_000


def path_clique_blowup(quotient: nx.Graph, weights: tuple[int, ...]) -> nx.Graph:
    """Expand each quotient vertex to a clique and each quotient edge to a join."""
    graph = nx.Graph()
    blobs: list[tuple[int, ...]] = []
    start = 0
    for weight in weights:
        blob = tuple(range(start, start + weight))
        start += weight
        blobs.append(blob)
        graph.add_nodes_from(blob)
        graph.add_edges_from(combinations(blob, 2))
    for u, v in quotient.edges():
        graph.add_edges_from((a, b) for a in blobs[u] for b in blobs[v])
    graph.graph["blobs"] = blobs
    return graph


def independent_domination_number(graph: nx.Graph) -> int:
    """Minimum maximal-independent-set cardinality, via complement cliques."""
    return min(map(len, nx.find_cliques(nx.complement(graph))))


def independence_number(graph: nx.Graph) -> int:
    if len(graph) == 0:
        return 0
    return max(map(len, nx.find_cliques(nx.complement(graph))))


def local_independence_max(graph: nx.Graph) -> int:
    return max(independence_number(graph.subgraph(graph.neighbors(v))) for v in graph)


def havel_hakimi_residue_degrees(degrees: Iterable[int]) -> int:
    seq = sorted(degrees, reverse=True)
    while seq and seq[0] > 0:
        degree = seq.pop(0)
        if degree > len(seq):
            raise ValueError("nongraphical degree sequence encountered")
        seq = sorted((value - 1 if i < degree else value for i, value in enumerate(seq)),
                     reverse=True)
        if seq and seq[-1] < 0:
            raise ValueError("nongraphical degree sequence encountered")
    return len(seq)


def graph_square(graph: nx.Graph) -> nx.Graph:
    square = nx.Graph()
    square.add_nodes_from(graph)
    for source, lengths in nx.all_pairs_shortest_path_length(graph, cutoff=2):
        square.add_edges_from((source, target) for target, distance in lengths.items()
                              if source < target and distance <= 2)
    return square


def residue(graph: nx.Graph) -> int:
    return havel_hakimi_residue_degrees(dict(graph.degree()).values())


def max_degree_vertices(graph: nx.Graph) -> set[int]:
    maximum = max(dict(graph.degree()).values())
    return {v for v in graph if graph.degree(v) == maximum}


def centers(graph: nx.Graph) -> set[int]:
    eccentricity = nx.eccentricity(graph)
    radius = min(eccentricity.values())
    return {v for v, value in eccentricity.items() if value == radius}


def induced_max_degree(graph: nx.Graph, vertices: set[int]) -> int:
    return max((degree for _, degree in graph.subgraph(vertices).degree()), default=0)


def induced_min_degree(graph: nx.Graph, vertices: set[int]) -> int:
    return min((degree for _, degree in graph.subgraph(vertices).degree()), default=0)


def sw(graph: nx.Graph) -> int:
    """Szekeres--Wilf as defined by source: maximum subgraph minimum degree."""
    return max(nx.core_number(graph).values(), default=0)


@dataclass(frozen=True)
class Terms:
    n: int
    m: int
    independent_domination: int
    lambda_local_max: int
    square_residue: int
    delta_maxset: int
    delta_center: int
    delta_nonmax: int
    min_degree: int
    sw_complement: int
    residual_430c_maxset: int
    residual_430c_center: int
    residual_434c_general: int
    residual_434c_leaf: int | None


def expanded_terms(graph: nx.Graph) -> Terms:
    indep_dom = independent_domination_number(graph)
    lambda_max = local_independence_max(graph)
    square_residue = residue(graph_square(graph))
    maxset = max_degree_vertices(graph)
    center = centers(graph)
    nonmax = set(graph) - maxset
    d_maxset = induced_max_degree(graph, maxset)
    d_center = induced_max_degree(graph, center)
    d_nonmax = induced_min_degree(graph, nonmax)
    min_degree = min(dict(graph.degree()).values())
    sw_complement = sw(nx.complement(graph))
    return Terms(
        n=len(graph), m=graph.number_of_edges(), independent_domination=indep_dom,
        lambda_local_max=lambda_max, square_residue=square_residue,
        delta_maxset=d_maxset, delta_center=d_center, delta_nonmax=d_nonmax,
        min_degree=min_degree, sw_complement=sw_complement,
        residual_430c_maxset=lambda_max * square_residue + d_maxset - indep_dom,
        residual_430c_center=lambda_max * square_residue + d_center - indep_dom,
        residual_434c_general=d_nonmax + 1 + sw_complement - indep_dom,
        residual_434c_leaf=(d_nonmax + sw_complement - indep_dom
                            if min_degree == 1 else None),
    )


def quotient_independent_domination(quotient: nx.Graph) -> int:
    return independent_domination_number(quotient)


def quotient_local_independence_max(quotient: nx.Graph) -> int:
    return local_independence_max(quotient)


def weighted_degrees(quotient: nx.Graph, weights: tuple[int, ...]) -> list[int]:
    return [weights[v] - 1 + sum(weights[u] for u in quotient.neighbors(v))
            for v in quotient]


def weighted_square_degrees(quotient: nx.Graph, weights: tuple[int, ...]) -> list[int]:
    distances = dict(nx.all_pairs_shortest_path_length(quotient, cutoff=2))
    return [weights[v] - 1 + sum(weights[u] for u, d in distances[v].items()
                                 if u != v and d <= 2)
            for v in quotient]


def expanded_degree_sequence(values: list[int], weights: tuple[int, ...]) -> list[int]:
    return [degree for degree, weight in zip(values, weights) for _ in range(weight)]


def quotient_fast_terms(quotient: nx.Graph, weights: tuple[int, ...]) -> dict[str, int | None]:
    """Discovery formulas. Candidate acceptance always uses expanded_terms."""
    i_value = quotient_independent_domination(quotient)
    lambda_max = quotient_local_independence_max(quotient)
    degrees = weighted_degrees(quotient, weights)
    maximum = max(degrees)
    max_blobs = {v for v, value in enumerate(degrees) if value == maximum}
    maxset_degrees = [weights[v] - 1 + sum(weights[u] for u in quotient.neighbors(v)
                                           if u in max_blobs) for v in max_blobs]
    d_maxset = max(maxset_degrees, default=0)
    center_blobs = set(nx.center(quotient))
    center_degrees = [weights[v] - 1 + sum(weights[u] for u in quotient.neighbors(v)
                                            if u in center_blobs) for v in center_blobs]
    d_center = max(center_degrees, default=0)
    square_degrees = weighted_square_degrees(quotient, weights)
    square_residue = havel_hakimi_residue_degrees(
        expanded_degree_sequence(square_degrees, weights))
    return {
        "i": i_value,
        "lambda": lambda_max,
        "square_residue": square_residue,
        "delta_maxset": d_maxset,
        "delta_center": d_center,
        "r430c": lambda_max * square_residue + d_maxset - i_value,
        "r430c_center": lambda_max * square_residue + d_center - i_value,
    }


def named_controls() -> list[tuple[str, nx.Graph]]:
    controls = [(f"C{n}", nx.cycle_graph(n)) for n in range(5, 10)]
    controls += [("P7", nx.path_graph(7)), ("Petersen", nx.petersen_graph()),
                 ("K3,3", nx.complete_bipartite_graph(3, 3)),
                 ("K7", nx.complete_graph(7))]
    controls += [(f"K1,{r}", nx.star_graph(r)) for r in range(2, 8)]
    controls += [(f"K{a},{b}", nx.complete_bipartite_graph(a, b))
                 for a in range(2, 5) for b in range(a, 6)]
    p7 = nx.path_graph(7)
    controls.append(("430a-P7-blowup", path_clique_blowup(p7, (1, 4, 12, 19, 12, 4, 1))))
    return controls


def run_gate() -> dict[str, object]:
    atlas = [(f"atlas-{nx.to_graph6_bytes(g, header=False).decode().strip()}", g)
             for g in nx.graph_atlas_g() if 4 <= len(g) <= 7 and nx.is_connected(g)]
    rows: list[dict[str, object]] = []
    for name, graph in atlas + named_controls():
        terms = expanded_terms(graph)
        rows.append({"name": name, "graph6": nx.to_graph6_bytes(graph, header=False).decode().strip(),
                     "terms": asdict(terms)})
    return {
        "atlas_count": len(atlas), "named_count": len(named_controls()),
        "violations": {
            "430c-MAXDEG": [row for row in rows if row["terms"]["residual_430c_maxset"] < 0],
            "430c-CENTER": [row for row in rows if row["terms"]["residual_430c_center"] < 0],
            "434c-general": [row for row in rows if row["terms"]["residual_434c_general"] < 0],
            "434c-leaf": [row for row in rows
                           if row["terms"]["residual_434c_leaf"] is not None
                           and row["terms"]["residual_434c_leaf"] < 0],
        },
        "minimum_residuals": {
            key: min(row["terms"][key] for row in rows
                     if row["terms"][key] is not None)
            for key in ("residual_430c_maxset", "residual_430c_center",
                        "residual_434c_general", "residual_434c_leaf")
        },
    }


def positive_composition(total: int, parts: int, rng: random.Random) -> tuple[int, ...]:
    cuts = sorted(rng.sample(range(1, total), parts - 1))
    return tuple(b - a for a, b in zip((0, *cuts), (*cuts, total)))


def candidate_weights(order: int, rng: random.Random, trials: int) -> Iterable[tuple[int, ...]]:
    yielded: set[tuple[int, ...]] = set()
    seeds = [tuple(1 for _ in range(order))]
    for vertex in range(order):
        for value in (2, 4, 8):
            row = [1] * order
            row[vertex] = value
            seeds.append(tuple(row))
    if order == 7:
        seeds.append((1, 4, 12, 19, 12, 4, 1))
    for weights in seeds:
        if sum(weights) <= 100 and weights not in yielded:
            yielded.add(weights)
            yield weights
    for _ in range(trials):
        total = rng.randint(order, 100)
        weights = positive_composition(total, order, rng)
        if weights not in yielded:
            yielded.add(weights)
            yield weights


def quotient_pool(rng: random.Random) -> list[nx.Graph]:
    graphs: dict[str, nx.Graph] = {}
    for graph in nx.graph_atlas_g():
        if 2 <= len(graph) <= 7 and nx.is_connected(graph):
            graph = nx.convert_node_labels_to_integers(graph)
            key = nx.to_graph6_bytes(graph, header=False).decode().strip()
            graphs[key] = graph
    for order in (8, 9):
        structured = [nx.path_graph(order), nx.cycle_graph(order), nx.star_graph(order - 1),
                      nx.complete_graph(order), nx.wheel_graph(order)]
        for graph in structured:
            key = nx.to_graph6_bytes(graph, header=False).decode().strip()
            graphs[key] = graph
        for _ in range(1200):
            probability = rng.choice((0.18, 0.25, 0.33, 0.5, 0.67, 0.8))
            graph = nx.gnp_random_graph(order, probability, seed=rng.randrange(2**32))
            if nx.is_connected(graph):
                key = nx.to_graph6_bytes(graph, header=False).decode().strip()
                graphs[key] = graph
    return list(graphs.values())


def run_search(limit: int, seed: int) -> dict[str, object]:
    rng = random.Random(seed)
    all_quotients = quotient_pool(rng)
    # Since residue >= 1 and Delta(G[M]) >= 0, a crossing is impossible unless
    # i(Q) > lambda_max(Q).  This exact obstruction filter is weight-independent.
    pool = [quotient for quotient in all_quotients
            if quotient_independent_domination(quotient)
            > quotient_local_independence_max(quotient)]
    started = time.monotonic()
    evaluations = 0
    hits_430c: list[dict[str, object]] = []
    best_430c: list[dict[str, object]] = []
    hits_430c_center: list[dict[str, object]] = []
    best_430c_center: list[dict[str, object]] = []
    # Method v0.1 prunes 434c here: its source-faithful leaf clause fails the
    # pre-search database gate (already on P4).  Searching a rejected reading
    # would turn a likely source error into a manufactured "discovery".
    per_q = max(10, min(250, limit // max(1, len(pool))))
    for quotient in pool:
        q6 = nx.to_graph6_bytes(quotient, header=False).decode().strip()
        for weights in candidate_weights(len(quotient), rng, per_q):
            if evaluations >= limit:
                break
            evaluations += 1
            fast = quotient_fast_terms(quotient, weights)
            record = {"quotient_graph6": q6, "weights": weights, **fast}
            best_430c.append(record)
            best_430c = sorted(best_430c, key=lambda row: row["r430c"])[:20]
            best_430c_center.append(record)
            best_430c_center = sorted(
                best_430c_center, key=lambda row: row["r430c_center"])[:20]
            if fast["r430c"] < 0:
                graph = path_clique_blowup(quotient, weights)
                exact = expanded_terms(graph)
                if exact.residual_430c_maxset < 0:
                    hits_430c.append({**record, "expanded_graph6": nx.to_graph6_bytes(
                        graph, header=False).decode().strip(), "expanded": asdict(exact)})
            if fast["r430c_center"] < 0:
                graph = path_clique_blowup(quotient, weights)
                exact = expanded_terms(graph)
                if exact.residual_430c_center < 0:
                    hits_430c_center.append({**record, "expanded_graph6":
                        nx.to_graph6_bytes(graph, header=False).decode().strip(),
                        "expanded": asdict(exact)})
        if evaluations >= limit:
            break
    return {
        "seed": seed, "quotients_generated": len(all_quotients),
        "quotients_after_obstruction_filter": len(pool), "evaluations": evaluations,
        "elapsed_seconds": time.monotonic() - started,
        "hits_430c": hits_430c[:50], "best_430c": best_430c,
        "hits_430c_center": hits_430c_center[:50],
        "best_430c_center": best_430c_center,
        "434c_search": "PRUNED_BY_DATABASE_GATE",
    }


def run_self_test(seed: int, trials: int = 500) -> dict[str, object]:
    """Cross-check quotient discovery formulas against expanded graph routines."""
    rng = random.Random(seed)
    quotients = [nx.convert_node_labels_to_integers(graph)
                 for graph in nx.graph_atlas_g()
                 if 2 <= len(graph) <= 7 and nx.is_connected(graph)]
    checked = 0
    for _ in range(trials):
        quotient = rng.choice(quotients)
        total = rng.randint(len(quotient), min(100, len(quotient) + 30))
        weights = positive_composition(total, len(quotient), rng)
        graph = path_clique_blowup(quotient, weights)
        fast = quotient_fast_terms(quotient, weights)
        exact = expanded_terms(graph)
        assert fast["i"] == exact.independent_domination
        assert fast["lambda"] == exact.lambda_local_max
        assert fast["square_residue"] == exact.square_residue
        assert fast["delta_maxset"] == exact.delta_maxset
        assert fast["delta_center"] == exact.delta_center
        assert fast["r430c"] == exact.residual_430c_maxset
        assert fast["r430c_center"] == exact.residual_430c_center
        encoded = nx.to_graph6_bytes(graph, header=False).strip()
        decoded = nx.from_graph6_bytes(encoded)
        assert set(graph) == set(decoded)
        assert {frozenset(edge) for edge in graph.edges()} == {
            frozenset(edge) for edge in decoded.edges()
        }
        checked += 1
    return {"seed": seed, "expanded_formula_cross_checks": checked, "status": "PASS"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("gate", "search", "selftest"))
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.mode == "gate":
        result = run_gate()
    elif args.mode == "selftest":
        result = run_self_test(args.seed)
    else:
        result = run_search(args.limit, args.seed)
    payload = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
