#!/usr/bin/env python3
"""Exact bounded search for Method v0.2 Trial H2 (WOWII 133).

The invariant `path` is longest induced path order.  The discovery solver
enumerates endpoint extensions of induced paths; every induced path can be
constructed in this way.  Individual calls enforce a 60-second deadline.
"""

from __future__ import annotations

import argparse
import itertools
import json
import subprocess
import time
from fractions import Fraction
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/expansion/method_v02_133_search.jsonl"
GENG = Path("/Users/kuber.mehta/Projects/breakthroughmaxxing/07-marlin/total-coloring-n12-d6-regular/tools/geng")


class SolveTimeout(RuntimeError):
    pass


def graph6(G: nx.Graph) -> str:
    return nx.to_graph6_bytes(nx.convert_node_labels_to_integers(G), header=False).decode().strip()


def has_c4(G: nx.Graph) -> bool:
    # Two vertices have two common neighbors iff they are opposite vertices
    # of a (not necessarily induced) C4.
    ns = {v: set(G[v]) for v in G}
    return any(len(ns[u] & ns[v]) >= 2 for u, v in itertools.combinations(G, 2))


def local_independence(G: nx.Graph, v: int) -> int:
    H = G.subgraph(list(G[v]))
    verts = list(H)
    for k in range(len(verts), -1, -1):
        for S in itertools.combinations(verts, k):
            if H.subgraph(S).number_of_edges() == 0:
                return k
    raise AssertionError


def floor_average_local_independence(G: nx.Graph) -> tuple[int, Fraction]:
    vals = [local_independence(G, v) for v in G]
    avg = Fraction(sum(vals), len(vals))
    return avg.numerator // avg.denominator, avg


def radius(G: nx.Graph) -> int:
    return min(max(nx.single_source_shortest_path_length(G, v).values()) for v in G)


def longest_induced_path(G: nx.Graph, timeout: float = 60.0) -> tuple[int, list[int], int]:
    """Return exact maximum order, one path, and states visited."""
    deadline = time.monotonic() + timeout
    adj = {v: set(G[v]) for v in G}
    best: list[int] = []
    states = 0

    def extend(path: list[int], used: set[int]) -> None:
        nonlocal best, states
        states += 1
        if states & 8191 == 0 and time.monotonic() > deadline:
            raise SolveTimeout
        if len(path) > len(best):
            best = path.copy()
        end = path[-1]
        forbidden_chord = used - {end}
        for w in adj[end] - used:
            if adj[w].isdisjoint(forbidden_chord):
                path.append(w)
                used.add(w)
                extend(path, used)
                used.remove(w)
                path.pop()

    for v in G:
        extend([v], {v})
    return len(best), best, states


def evaluate(G: nx.Graph, name: str, stratum: str, timeout: float = 60.0) -> dict:
    if len(G) < 2 or not nx.is_connected(G):
        return {"kind": "skip", "name": name, "reason": "not_applicable"}
    c4 = has_c4(G)
    fl, avg = floor_average_local_independence(G)
    rad = radius(G)
    t0 = time.monotonic()
    try:
        path, witness, states = longest_induced_path(G, timeout)
    except SolveTimeout:
        return {
            "kind": "solve_timeout", "name": name, "stratum": stratum,
            "n": len(G), "m": G.number_of_edges(), "graph6": graph6(G),
            "radius": rad, "floor_l": fl, "avg_l": str(avg),
            "has_c4": c4, "seconds": round(time.monotonic() - t0, 6),
        }
    correction = 1 if c4 else fl
    residual = path - rad - correction
    return {
        "kind": "graph", "name": name, "stratum": stratum,
        "n": len(G), "m": G.number_of_edges(), "graph6": graph6(G),
        "connected": True, "has_c4": c4, "radius": rad,
        "floor_l": fl, "avg_l": str(avg), "path": path,
        "path_witness": witness, "residual": residual, "states": states,
        "seconds": round(time.monotonic() - t0, 6),
    }


def emit(row: dict, out=OUT) -> None:
    line = json.dumps(row, sort_keys=True)
    print(line, flush=True)
    with out.open("a") as f:
        f.write(line + "\n")


def controls() -> list[tuple[str, nx.Graph]]:
    ans: list[tuple[str, nx.Graph]] = []
    for G in nx.graph_atlas_g():
        if 2 <= len(G) <= 7 and nx.is_connected(G):
            ans.append((f"atlas:{graph6(G)}", G))
    ans += [(f"C{n}", nx.cycle_graph(n)) for n in range(5, 10)]
    ans += [("P7", nx.path_graph(7)), ("Petersen", nx.petersen_graph()),
            ("K3,3", nx.complete_bipartite_graph(3, 3)), ("K7", nx.complete_graph(7))]
    ans += [(f"K1,{n}", nx.star_graph(n)) for n in range(2, 8)]
    ans += [(f"K{a},{b}", nx.complete_bipartite_graph(a, b))
            for a, b in [(2, 3), (2, 4), (3, 4), (4, 4)]]
    return ans


def named_calibrators() -> list[tuple[str, nx.Graph]]:
    mcgee = nx.LCF_graph(24, [12, 7, -7], 8)
    kneser = nx.Graph()
    triples = list(itertools.combinations(range(7), 3))
    kneser.add_nodes_from(range(len(triples)))
    kneser.add_edges_from((i, j) for i, a in enumerate(triples)
                          for j, b in enumerate(triples[i + 1:], i + 1)
                          if set(a).isdisjoint(b))
    return [
        ("McGee", mcgee), ("Pappus", nx.pappus_graph()),
        ("Desargues", nx.desargues_graph()), ("Dodecahedron", nx.dodecahedral_graph()),
        ("Kneser(7,3)", kneser), ("Hoffman-Singleton", nx.hoffman_singleton_graph()),
    ]


def spanning_tree_lift(base: nx.Graph, bits: tuple[int, ...]) -> nx.Graph:
    T = nx.minimum_spanning_tree(base)
    tree_edges = {tuple(sorted(e)) for e in T.edges()}
    cotree = [e for e in base.edges() if tuple(sorted(e)) not in tree_edges]
    signs = {tuple(sorted(e)): 0 for e in T.edges()}
    signs.update({tuple(sorted(e)): bit for e, bit in zip(cotree, bits)})
    H = nx.Graph()
    H.add_nodes_from(range(2 * len(base)))
    for u, v in base.edges():
        s = signs[tuple(sorted((u, v)))]
        for sheet in (0, 1):
            H.add_edge(2 * u + sheet, 2 * v + (sheet ^ s))
    return H


def nonisomorphic_lifts(base: nx.Graph) -> list[nx.Graph]:
    cycle_rank = base.number_of_edges() - len(base) + 1
    reps: list[nx.Graph] = []
    # All-zero voltage is disconnected.  Spanning-tree gauge fixing gives
    # exactly one representative of each vertex-switching class.
    for bits in itertools.product((0, 1), repeat=cycle_rank):
        if not any(bits):
            continue
        H = spanning_tree_lift(base, bits)
        if not nx.is_connected(H):
            continue
        if not any(nx.is_isomorphic(H, K) for K in reps):
            reps.append(H)
    return reps


def run_gate() -> None:
    start = time.monotonic()
    bad = timeouts = 0
    for name, G in controls():
        row = evaluate(G, name, "gate")
        emit(row)
        bad += row.get("residual", 0) < 0
        timeouts += row["kind"] == "solve_timeout"
    emit({"kind": "summary", "phase": "gate", "bad": bad, "timeouts": timeouts,
          "seconds": round(time.monotonic() - start, 6)})


def run_lifts() -> None:
    start = time.monotonic()
    total = bad = 0
    for bname, base in [("C5", nx.cycle_graph(5)), ("Petersen", nx.petersen_graph())]:
        lifts = nonisomorphic_lifts(base)
        emit({"kind": "lift_classes", "base": bname, "count": len(lifts)})
        for i, G in enumerate(lifts):
            row = evaluate(G, f"2lift:{bname}:{i}", "lift")
            emit(row)
            total += 1
            bad += row.get("residual", 0) < 0
    emit({"kind": "summary", "phase": "lifts", "graphs": total, "bad": bad,
          "seconds": round(time.monotonic() - start, 6)})


def run_named() -> None:
    start = time.monotonic()
    bad = timeouts = 0
    for name, G in named_calibrators():
        row = evaluate(G, name, "named")
        emit(row)
        bad += row.get("residual", 0) < 0
        timeouts += row["kind"] == "solve_timeout"
    emit({"kind": "summary", "phase": "named", "bad": bad, "timeouts": timeouts,
          "seconds": round(time.monotonic() - start, 6)})


def run_cubic(n: int, generator_timeout: float) -> None:
    start = time.monotonic()
    cmd = [str(GENG), "-q", "-cf", "-d3D3", str(n), f"{3*n//2}:{3*n//2}"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    total = bad = timeouts = 0
    min_r = None
    min_rows: list[dict] = []
    deadline = start + generator_timeout
    assert proc.stdout is not None
    try:
        for line in proc.stdout:
            if time.monotonic() > deadline:
                raise TimeoutError
            G = nx.from_graph6_bytes(line.strip().encode())
            row = evaluate(G, f"cubic-c4free-{n}:{total}", f"cubic:{n}")
            total += 1
            if row["kind"] == "solve_timeout":
                timeouts += 1
                emit(row)
                continue
            r = row["residual"]
            bad += r < 0
            if min_r is None or r < min_r:
                min_r, min_rows = r, [row]
            elif r == min_r and len(min_rows) < 10:
                min_rows.append(row)
            if r < 0:
                emit(row)
            if total % 1000 == 0:
                emit({"kind": "progress", "phase": "cubic", "n": n, "graphs": total,
                      "min_residual": min_r, "timeouts": timeouts,
                      "seconds": round(time.monotonic() - start, 6)})
        rc = proc.wait(timeout=5)
        complete = rc == 0
    except TimeoutError:
        proc.kill()
        proc.wait()
        complete = False
    for row in min_rows:
        emit({**row, "kind": "minimum"})
    emit({"kind": "summary", "phase": "cubic", "n": n, "graphs": total,
          "complete": complete, "bad": bad, "min_residual": min_r,
          "solve_timeouts": timeouts, "generator_cap_seconds": generator_timeout,
          "seconds": round(time.monotonic() - start, 6)})


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("phase", choices=["gate", "lifts", "named", "cubic"])
    p.add_argument("--n", type=int)
    p.add_argument("--generator-timeout", type=float, default=60.0)
    p.add_argument("--fresh", action="store_true")
    args = p.parse_args()
    if args.fresh and OUT.exists():
        OUT.unlink()
    if args.phase == "gate": run_gate()
    elif args.phase == "lifts": run_lifts()
    elif args.phase == "named": run_named()
    else:
        if args.n is None or args.n % 2 or args.n < 4:
            p.error("cubic requires even --n >= 4")
        run_cubic(args.n, args.generator_timeout)


if __name__ == "__main__":
    main()
