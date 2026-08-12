#!/usr/bin/env python3
"""Bounded exact quotient search for the WOWII 422b residual wall.

For a positive clique blow-up of a connected quotient Q with blob sizes s_v,

  i(G) = i(Q),
  alpha(G[M]) = alpha(Q[M]), and
  gamma(G[V-M]) = gamma(Q[V-M]),

where M consists of quotient vertices maximizing

  s_v + sum_{u adjacent to v} s_u.

The quotient residual is therefore

  R(Q, M) = alpha(Q[M]) + gamma(Q[V-M])^2 - i(Q).

This program exhausts connected, unlabelled quotients emitted by nauty geng.
It first checks R for every structurally possible partition.  Only a negative
quotient residual is sent to the bounded integer max-set realization step.
Consequently a run with zero negative quotient residuals is exact and does not
depend on the numerical MILP prefilter.
"""

from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
from pathlib import Path
import subprocess
import time
from typing import Iterable

import networkx as nx
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp


def popcount(mask: int) -> int:
    """Python 3.9-compatible population count."""
    return bin(mask).count("1")


def mask_data(graph: nx.Graph) -> tuple[list[int], list[int], list[int], int]:
    """Return adjacency masks, closed masks, alpha table, and exact i(G)."""
    graph = nx.convert_node_labels_to_integers(graph)
    n = len(graph)
    adjacency = [sum(1 << u for u in graph.neighbors(v)) for v in range(n)]
    closed = [adjacency[v] | (1 << v) for v in range(n)]
    all_vertices = (1 << n) - 1
    independent = [False] * (1 << n)
    cover = [0] * (1 << n)
    alpha = [0] * (1 << n)
    independent[0] = True

    for subset in range(1, 1 << n):
        bit = subset & -subset
        vertex = bit.bit_length() - 1
        rest = subset ^ bit
        independent[subset] = independent[rest] and not (
            adjacency[vertex] & rest
        )
        cover[subset] = cover[rest] | closed[vertex]
        alpha[subset] = max(
            alpha[rest], 1 + alpha[rest & ~adjacency[vertex]]
        )

    independent_domination = min(
        popcount(subset)
        for subset in range(1, 1 << n)
        if independent[subset] and cover[subset] == all_vertices
    )
    return adjacency, closed, alpha, independent_domination


def domination_number(closed: list[int], target: int) -> int:
    """Exact domination number of the subgraph induced by target."""
    if target == 0:
        return 0
    best = popcount(target)
    subset = target
    while subset:
        size = popcount(subset)
        if size < best:
            covered = 0
            chosen = subset
            while chosen:
                bit = chosen & -chosen
                covered |= closed[bit.bit_length() - 1]
                chosen ^= bit
            if target & ~covered == 0:
                best = size
        subset = (subset - 1) & target
    return best


def negative_residual_partitions(
    adjacency: list[int], closed: list[int], alpha: list[int], i_value: int
) -> list[tuple[int, int, int]]:
    """Return (M, alpha(Q[M]), gamma(Q-M)) for every exact R < 0 partition."""
    n = len(adjacency)
    all_vertices = (1 << n) - 1
    if i_value <= 2:
        return []

    results: dict[int, tuple[int, int, int]] = {}
    if i_value <= 4:
        # Since M and its complement are nonempty, alpha(M) >= 1.  If
        # gamma(Q-M) >= 2, then R >= 1 + 4 - i(Q) >= 0.  Hence every
        # crossing at these i-values has gamma(Q-M)=1.  Enumerate its possible
        # universal dominator w exactly, without scanning all set partitions.
        for witness in range(n):
            mandatory_m = all_vertices ^ closed[witness]
            optional_m = adjacency[witness]
            subset = optional_m
            while True:
                maximum_set = mandatory_m | subset
                if maximum_set and maximum_set != all_vertices:
                    alpha_m = alpha[maximum_set]
                    if alpha_m + 1 < i_value:
                        results[maximum_set] = (maximum_set, alpha_m, 1)
                if subset == 0:
                    break
                subset = (subset - 1) & optional_m
        return list(results.values())

    # This branch is not reached in the <=9 run, but keeps the helper exact
    # if the bound is raised later.
    for maximum_set in range(1, all_vertices):
        complement = all_vertices ^ maximum_set
        gamma_complement = domination_number(closed, complement)
        if alpha[maximum_set] + gamma_complement**2 < i_value:
            results[maximum_set] = (
                maximum_set,
                alpha[maximum_set],
                gamma_complement,
            )
    return list(results.values())


def realize_maximum_set(
    adjacency: list[int], maximum_set: int, max_order: int, time_limit: float
) -> tuple[int, ...] | None:
    """Find positive integer blob sizes realizing exactly M, then verify exactly.

    HiGHS is only a candidate generator.  A returned vector is accepted after
    integer re-evaluation of every weighted closed degree.  An infeasible
    return is not used as an exact mathematical certificate.
    """
    n = len(adjacency)
    matrix = np.zeros((n + 1, n + 1))
    lower: list[float] = []
    upper: list[float] = []
    for vertex in range(n):
        for other in range(n):
            if other == vertex or ((adjacency[vertex] >> other) & 1):
                matrix[vertex, other] = 1
        matrix[vertex, n] = -1
        if (maximum_set >> vertex) & 1:
            lower.append(0)
            upper.append(0)
        else:
            lower.append(-np.inf)
            upper.append(-1)
    matrix[n, :n] = 1
    lower.append(-np.inf)
    upper.append(max_order)

    result = milp(
        np.r_[np.ones(n), 0],
        integrality=np.ones(n + 1),
        bounds=Bounds(
            np.r_[np.ones(n), 1],
            np.r_[np.full(n, max_order), max_order],
        ),
        constraints=LinearConstraint(matrix, lower, upper),
        options={"time_limit": time_limit, "mip_rel_gap": 0},
    )
    if not result.success:
        return None
    weights = tuple(int(round(value)) for value in result.x[:n])
    weighted_closed_degrees = [
        sum(
            weights[other]
            for other in range(n)
            if other == vertex or ((adjacency[vertex] >> other) & 1)
        )
        for vertex in range(n)
    ]
    realized = {
        vertex
        for vertex, value in enumerate(weighted_closed_degrees)
        if value == max(weighted_closed_degrees)
    }
    requested = {
        vertex for vertex in range(n) if (maximum_set >> vertex) & 1
    }
    if realized != requested or sum(weights) > max_order or min(weights) < 1:
        return None
    return weights


def graph_records(
    geng: str, order: int, residue: int | None, modulus: int | None
) -> Iterable[tuple[str, nx.Graph]]:
    command = [geng, "-cq", str(order)]
    if residue is not None and modulus is not None:
        command.append(f"{residue}/{modulus}")
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    assert process.stdout is not None
    try:
        for line in process.stdout:
            graph6 = line.strip()
            if graph6:
                yield graph6, nx.from_graph6_bytes(graph6.encode("ascii"))
    finally:
        process.stdout.close()
        process.wait()
    if process.returncode != 0:
        raise RuntimeError(f"geng exited with status {process.returncode}")


def search_shard(task: tuple[str, int, int | None, int | None, int]) -> dict:
    geng, order, residue, modulus, max_expanded_order = task
    started = time.monotonic()
    graphs = 0
    i_above_two = 0
    maximum_i = 0
    negative_partitions = 0
    ilp_calls = 0
    witnesses: list[dict] = []

    for graph6, graph in graph_records(geng, order, residue, modulus):
        graphs += 1
        adjacency, closed, alpha, i_value = mask_data(graph)
        maximum_i = max(maximum_i, i_value)
        if i_value <= 2:
            continue
        i_above_two += 1
        partitions = negative_residual_partitions(
            adjacency, closed, alpha, i_value
        )
        negative_partitions += len(partitions)
        for maximum_set, alpha_m, gamma_complement in partitions:
            ilp_calls += 1
            weights = realize_maximum_set(
                adjacency,
                maximum_set,
                max_expanded_order,
                time_limit=1.0,
            )
            if weights is not None:
                witnesses.append(
                    {
                        "quotient_graph6": graph6,
                        "quotient_order": order,
                        "weights": weights,
                        "expanded_order": sum(weights),
                        "maximum_set_mask": maximum_set,
                        "i": i_value,
                        "alpha_M": alpha_m,
                        "gamma_complement": gamma_complement,
                        "rhs": alpha_m + gamma_complement**2,
                    }
                )

    return {
        "kind": "search_shard",
        "order": order,
        "residue": residue,
        "modulus": modulus,
        "graphs": graphs,
        "i_above_two": i_above_two,
        "maximum_i": maximum_i,
        "negative_partitions": negative_partitions,
        "ilp_calls": ilp_calls,
        "witnesses": witnesses,
        "seconds": time.monotonic() - started,
    }


def exact_terms(graph: nx.Graph) -> tuple[int, int, int, int]:
    graph = nx.convert_node_labels_to_integers(graph)
    degrees = dict(graph.degree())
    maximum_degree = max(degrees.values())
    maximum_vertices = {v for v, degree in degrees.items() if degree == maximum_degree}
    maximum_mask = sum(1 << v for v in maximum_vertices)
    all_vertices = (1 << len(graph)) - 1
    _, closed, alpha, i_value = mask_data(graph)
    gamma_complement = domination_number(closed, all_vertices ^ maximum_mask)
    alpha_m = alpha[maximum_mask]
    return i_value, alpha_m, gamma_complement, alpha_m + gamma_complement**2 - i_value


def database_gate() -> dict:
    atlas = [
        nx.convert_node_labels_to_integers(graph)
        for graph in nx.graph_atlas_g()
        if 4 <= len(graph) <= 7 and nx.is_connected(graph)
    ]
    named: list[tuple[str, nx.Graph]] = [
        *[(f"C{order}", nx.cycle_graph(order)) for order in range(5, 10)],
        ("P7", nx.path_graph(7)),
        ("Petersen", nx.petersen_graph()),
        ("K3,3", nx.complete_bipartite_graph(3, 3)),
        ("K7", nx.complete_graph(7)),
        *[(f"K1,{leaves}", nx.star_graph(leaves)) for leaves in range(2, 8)],
        *[
            (f"K{left},{right}", nx.complete_bipartite_graph(left, right))
            for left in range(2, 5)
            for right in range(left, 6)
        ],
    ]
    atlas_terms = [exact_terms(graph) for graph in atlas]
    named_terms = [(name, exact_terms(graph)) for name, graph in named]
    violations = [terms for terms in atlas_terms if terms[-1] < 0]
    violations += [terms for _, terms in named_terms if terms[-1] < 0]
    if violations:
        raise AssertionError(f"database gate failed: {violations[:5]}")
    return {
        "kind": "database_gate",
        "atlas_graphs": len(atlas),
        "named_graphs": len(named),
        "violations": 0,
        "atlas_equalities": sum(terms[-1] == 0 for terms in atlas_terms),
        "named_terms": [
            {
                "name": name,
                "i": terms[0],
                "alpha_M": terms[1],
                "gamma_complement": terms[2],
                "residual": terms[3],
            }
            for name, terms in named_terms
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--geng", required=True, help="path to nauty geng")
    parser.add_argument("--max-order", type=int, default=9)
    parser.add_argument("--max-expanded-order", type=int, default=100)
    parser.add_argument("--seconds", type=float, default=60.0)
    parser.add_argument("--jobs", type=int, default=min(8, mp.cpu_count()))
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not 4 <= args.max_order <= 9:
        raise SystemExit("this audited run supports max-order from 4 through 9")
    if args.seconds > 60:
        raise SystemExit("the method caps this search at 60 seconds")
    if not Path(args.geng).is_file():
        raise SystemExit(f"geng not found: {args.geng}")

    output = args.output.open("w", encoding="utf-8") if args.output else None

    def emit(record: dict) -> None:
        line = json.dumps(record, sort_keys=True)
        print(line, flush=True)
        if output:
            output.write(line + "\n")
            output.flush()

    started = time.monotonic()
    emit(database_gate())

    tasks: list[tuple[str, int, int | None, int | None, int]] = []
    for order in range(4, min(args.max_order, 8) + 1):
        tasks.append((args.geng, order, None, None, args.max_expanded_order))
    if args.max_order == 9:
        shards = max(8, args.jobs * 8)
        tasks.extend(
            (args.geng, 9, residue, shards, args.max_expanded_order)
            for residue in range(shards)
        )

    records: list[dict] = []
    pool = mp.Pool(processes=args.jobs)
    timed_out = False
    try:
        iterator = pool.imap_unordered(search_shard, tasks)
        for _ in tasks:
            remaining = args.seconds - (time.monotonic() - started)
            if remaining <= 0:
                raise mp.TimeoutError
            record = iterator.next(timeout=remaining)
            records.append(record)
            emit(record)
    except mp.TimeoutError:
        timed_out = True
        pool.terminate()
    else:
        pool.close()
    finally:
        pool.join()

    summary = {
        "kind": "summary",
        "complete": not timed_out and len(records) == len(tasks),
        "wall_seconds": time.monotonic() - started,
        "cap_seconds": args.seconds,
        "tasks_completed": len(records),
        "tasks_total": len(tasks),
        "graphs": sum(record["graphs"] for record in records),
        "i_above_two": sum(record["i_above_two"] for record in records),
        "maximum_i": max((record["maximum_i"] for record in records), default=0),
        "negative_partitions": sum(
            record["negative_partitions"] for record in records
        ),
        "ilp_calls": sum(record["ilp_calls"] for record in records),
        "witnesses": [
            witness for record in records for witness in record["witnesses"]
        ],
    }
    emit(summary)
    if output:
        output.close()
    if timed_out:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
