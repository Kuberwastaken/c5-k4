#!/usr/bin/env python3
"""Produce decision-level hold witnesses for exact-max timeouts in the #133 trial.

This is deliberately separate from the frozen evaluator.  It does not turn an
exact-longest-path timeout into an exact invariant value; it only checks the
logically sufficient condition that an induced path of length
``radius + floor_l`` exists.
"""

from __future__ import annotations

import json
import signal
import time
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "results/expansion/prospective_wowii133_alt_geometry_ledger.jsonl"


class SearchTimeout(RuntimeError):
    pass


def find_induced_path(G: nx.Graph, target: int, cap: float = 0.5) -> tuple[list, int]:
    deadline = time.monotonic() + cap
    adjacency = {v: set(G[v]) for v in G}
    states = 0

    def extend(path: list, used: set) -> list | None:
        nonlocal states
        states += 1
        if states & 4095 == 0 and time.monotonic() > deadline:
            raise SearchTimeout
        if len(path) >= target:
            return path.copy()
        endpoint = path[-1]
        forbidden = used - {endpoint}
        for nxt in sorted(adjacency[endpoint] - used):
            if adjacency[nxt].isdisjoint(forbidden):
                result = extend(path + [nxt], used | {nxt})
                if result is not None:
                    return result
        return None

    for start in sorted(G):
        result = extend([start], {start})
        if result is not None:
            return result, states
    raise AssertionError("no target-length induced path found")


def is_induced_path(G: nx.Graph, vertices: list) -> bool:
    H = G.subgraph(vertices)
    if len(H) == 1:
        return True
    degrees = dict(H.degree())
    return (nx.is_connected(H) and H.number_of_edges() == len(H) - 1
            and sum(value == 1 for value in degrees.values()) == 2
            and max(degrees.values()) <= 2)


def main() -> None:
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError()))
    signal.alarm(59)
    latest: dict[str, dict] = {}
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row.get("kind") == "solve_timeout" and row.get("stratum") != "gate":
            latest[row["name"]] = row
    certified = 0
    for name, row in sorted(latest.items()):
        G = nx.from_graph6_bytes(row["graph6"].encode("ascii"))
        target = row["radius"] + row["floor_l"]
        witness, states = find_induced_path(G, target)
        valid = len(witness) >= target and is_induced_path(G, witness)
        certified += int(valid)
        print(json.dumps({"name": name, "target": target, "witness": witness,
                          "states": states, "valid": valid}, sort_keys=True))
    print(json.dumps({"kind": "summary", "timeouts": len(latest),
                      "decision_hold_witnesses": certified}, sort_keys=True))


if __name__ == "__main__":
    main()
