#!/usr/bin/env python3
"""Frozen Petersen 3-edge-splice trial for current DeepMind WOWII #133."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import os
import subprocess
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "results/expansion/prospective_wowii133_petersen_splice_ledger.jsonl"
UPSTREAM = Path("/Users/kuber.mehta/Projects/formal-conjectures")
EXPECTED_COMMIT = "d16e05aded22b8c467a0a27c14b2311f53185006"
EXPECTED_BLOB = "9a8dca984e87efc2fb1ffd68f5d4185e4645a8e8"

SPEC = importlib.util.spec_from_file_location(
    "wow133_splice_core", ROOT / "scripts/prospective_wowii133_alt_geometry.py"
)
assert SPEC and SPEC.loader
CORE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CORE)


def append(row: dict) -> None:
    with LEDGER.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def graph6(G: nx.Graph) -> str:
    H = nx.convert_node_labels_to_integers(G, ordering="sorted")
    return nx.to_graph6_bytes(H, header=False).decode().strip()


def live_source_gate() -> dict:
    remote_line = subprocess.run(
        ["git", "ls-remote", "upstream", "refs/heads/main"], cwd=UPSTREAM,
        check=True, capture_output=True, text=True, timeout=15,
    ).stdout.strip()
    remote_commit = remote_line.split()[0]
    source = subprocess.run(
        ["git", "show", f"{remote_commit}:FormalConjectures/WrittenOnTheWallII/GraphConjecture133.lean"],
        cwd=UPSTREAM, check=True, capture_output=True, text=True, timeout=10,
    ).stdout
    blob = subprocess.run(
        ["git", "hash-object", "--stdin"], input=source, check=True,
        capture_output=True, text=True, timeout=10,
    ).stdout.strip()
    required = {
        "open_tag": "@[category research open, AMS 5]\ntheorem conjecture133" in source,
        "induced_path_text": "largest induced path" in source,
        "c4_subgraph_quantifier": "let hasC4 := ∃ a b c d" in source,
        "floor_local_independence": "(⌊l G⌋ : ℝ) ^ cC4" in source,
    }
    return {
        "remote_commit": remote_commit,
        "source_blob": blob,
        "required_checks": required,
        "pass": remote_commit == EXPECTED_COMMIT and blob == EXPECTED_BLOB and all(required.values()),
    }


def run_gate() -> dict:
    source = live_source_gate()
    rows = []
    for name, G in CORE.gate_controls():
        row = CORE.evaluate(G, name, "splice_gate", solve_cap=8.0, independently_verify=False)
        rows.append(row)
    crossings = [row for row in rows if row.get("residual", 0) < 0]
    timeouts = [row for row in rows if row.get("kind") == "solve_timeout"]
    petersen = next(row for row in rows if row["name"] == "Petersen")
    pgraph = nx.petersen_graph()
    ppath = petersen.get("path_witness", [])
    p_replay = CORE.subset_is_path(pgraph, tuple(ppath)) and len(ppath) == 5
    status = "PASS" if source["pass"] and not crossings and not timeouts and petersen.get("residual") == 0 and p_replay else "FAIL"
    result = {
        "event": "DB_GATE",
        "status": status,
        "source": source,
        "controls": len(rows),
        "crossings": len(crossings),
        "timeouts": len(timeouts),
        "petersen": {
            key: petersen[key] for key in ("graph6", "path", "radius", "floor_l", "residual", "path_witness")
        },
        "petersen_path_replay": p_replay,
        "candidate_evaluations": 0,
        "public_action": False,
    }
    append(result)
    return result


def gate_passed() -> bool:
    rows = [json.loads(line) for line in LEDGER.read_text().splitlines() if line.strip()]
    gates = [row for row in rows if row.get("event") == "DB_GATE"]
    return bool(gates and gates[-1].get("status") == "PASS" and gates[-1]["source"].get("pass"))


def splices():
    P = nx.convert_node_labels_to_integers(nx.petersen_graph(), ordering="sorted")
    portals_left = sorted(P[0])
    portals_right = [v + 10 for v in portals_left]
    left = P.copy()
    right = nx.relabel_nodes(P, {v: v + 10 for v in P})
    left.remove_node(0)
    right.remove_node(10)
    base = nx.compose(left, right)
    for permutation in itertools.permutations(portals_right):
        G = base.copy()
        matching = list(zip(portals_left, permutation))
        G.add_edges_from(matching)
        yield portals_left, portals_right, matching, nx.convert_node_labels_to_integers(G, ordering="sorted")


def run_development() -> dict:
    if not gate_passed():
        result = {"event": "VERDICT", "status": "DB_SANITY_REJECT", "public_action": False}
        append(result)
        return result

    seen = set()
    rows = []
    raw = 0
    for portals_left, portals_right, matching, G in splices():
        raw += 1
        g6 = graph6(G)
        if g6 in seen:
            continue
        seen.add(g6)
        degrees = sorted(dict(G.degree()).values())
        triangle_free = sum(nx.triangles(G).values()) == 0
        c4 = CORE.c4_witness(G)
        construction_ok = nx.is_connected(G) and degrees == [3] * 18 and triangle_free and c4 is None
        row = CORE.evaluate(G, f"splice:{raw - 1}", "development", solve_cap=50.0, independently_verify=True)
        row.update({
            "event": "GRAPH_EVALUATED",
            "matching_index": raw - 1,
            "matching": matching,
            "left_portals_before_relabel": portals_left,
            "right_portals_before_relabel": portals_right,
            "graph6_sha256": hashlib.sha256(g6.encode()).hexdigest(),
            "degree_sequence": degrees,
            "triangle_free": triangle_free,
            "construction_c4_witness": c4,
            "construction_gate": construction_ok,
            "candidate": row.get("residual", 0) < 0,
            "public_action": False,
        })
        append(row)
        rows.append(row)
        if not construction_ok:
            break

    bad_gate = [row for row in rows if not row["construction_gate"]]
    timeouts = [row for row in rows if row.get("kind") == "solve_timeout"]
    candidates = [row for row in rows if row.get("candidate")]
    if bad_gate or timeouts:
        status = "INCONCLUSIVE"
    elif candidates:
        status = "CANDIDATE_ADVERSARIAL"
    else:
        status = "HOLD_BOUNDED"
    result = {
        "event": "VERDICT",
        "status": status,
        "raw_matchings": raw,
        "unique_labelled_graphs": len(rows),
        "construction_gate_failures": len(bad_gate),
        "timeouts": len(timeouts),
        "candidate_count": len(candidates),
        "residuals": [row.get("residual") for row in rows],
        "independent_audit_required": True,
        "public_action": False,
    }
    append(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("gate", "development"), required=True)
    args = parser.parse_args()
    result = run_gate() if args.phase == "gate" else run_development()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
