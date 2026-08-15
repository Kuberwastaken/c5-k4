#!/usr/bin/env python3
"""Independent semantic and artifact verifier for the parity-packed Catch-Up arm."""

from __future__ import annotations

import argparse
import functools
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

UPSTREAM_COMMIT = "6c0950bec7743f5098c0196c6aee7b22c1ec8005"
UPSTREAM_TREE = "5af0d2a3a319ee2458f8cd061db7c49aeba1b35e"
SOURCE_BLOB = "ce8251a228ea79a6b2f8414e9eb6b5291a640677"
SOURCE_SHA256 = "7e940f2e37a1794e98fc21454096429da13243669a432b9239743aaf46f1d3c0"
N23_STATES = 95_451_689
N23_CALLS = 826_741_149
COMMIT_RE = re.compile(r"[0-9a-f]{40}\Z")


def canonical_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSONL row {number}: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"JSONL row {number} is not an object")
        rows.append(value)
    if not rows:
        raise ValueError("empty JSONL artifact")
    return rows


def independent_absolute_value(n: int) -> int:
    """Reference recurrence with absolute scores, not packed deficit states."""
    full = (1 << n) - 1

    @functools.cache
    def turn(mask: int, current: int, opponent: int) -> int:
        if mask == 0:
            return 0 if current == opponent else (-1 if current < opponent else 1)
        best = -1
        bits = mask
        while bits and best < 1:
            bit = bits & -bits
            bits ^= bit
            x = bit.bit_length()
            next_mask = mask ^ bit
            new_current = current + x
            candidate = (
                turn(next_mask, new_current, opponent)
                if new_current < opponent
                else -turn(next_mask, opponent, new_current)
            )
            best = max(best, candidate)
        return best

    root = -1
    for x in range(1, n + 1):
        root = max(root, -turn(full ^ (1 << (x - 1)), 0, x))
        if root == 1:
            break
    return root


def run_small_reference(solver: Path, maximum: int) -> None:
    if not 1 <= maximum <= 12:
        raise ValueError("small reference maximum must be 1..12")
    compared = []
    for n in range(1, maximum + 1):
        process = subprocess.run(
            [str(solver.resolve()), "--small", str(n)],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
        )
        if process.returncode != 0:
            raise ValueError(f"solver failed for N={n}: {process.stderr.strip()}")
        rows = [json.loads(line) for line in process.stdout.splitlines()]
        result = [row for row in rows if row.get("event") == "result"]
        if len(result) != 1:
            raise ValueError(f"missing unique result for N={n}")
        reference = independent_absolute_value(n)
        if result[0].get("value") != reference:
            raise ValueError(f"absolute-score mismatch at N={n}")
        compared.append({"n": n, "value": reference})
    print(json.dumps({"status": "PASS", "comparison": compared}, sort_keys=True))


def verify_start(start: dict[str, Any], n: int, campaign: str) -> None:
    expected_mode = "n23_performance_gate" if n == 23 else "n24_target"
    expected_deadline = 38.0 if n == 23 else 54.0
    expected = {
        "event": "run_start",
        "n": n,
        "schema": "catchup-parity-packed-v1",
        "upstream_commit": UPSTREAM_COMMIT,
        "upstream_tree": UPSTREAM_TREE,
        "source_blob": SOURCE_BLOB,
        "source_sha256": SOURCE_SHA256,
        "campaign_commit": campaign,
        "mode": expected_mode,
        "move_order": "ascending_set_bits",
        "state": "remaining_mask,current_deficit,remaining_sum",
        "memo": "uint32_per_mask_two_bits_per_parity_slot",
        "deadline_seconds": expected_deadline,
    }
    for key, value in expected.items():
        if start.get(key) != value:
            raise ValueError(f"start-row drift for {key}")


def verify_ledger(path: Path, n: int, campaign: str, certificate: Path | None) -> None:
    if not COMMIT_RE.fullmatch(campaign):
        raise ValueError("campaign commit is not 40 lowercase hex")
    rows = canonical_rows(path)
    allowed_events = {"run_start", "memo_progress", "result", "controlled_timeout", "controlled_signal"}
    if any(row.get("event") not in allowed_events for row in rows):
        raise ValueError("ledger contains an unknown event")
    if rows[0].get("event") != "run_start" or rows[-1].get("event") not in {
        "result", "controlled_timeout", "controlled_signal"
    }:
        raise ValueError("ledger start/terminal ordering drift")
    starts = [row for row in rows if row.get("event") == "run_start"]
    if len(starts) != 1:
        raise ValueError("ledger must have exactly one start row")
    verify_start(starts[0], n, campaign)

    progress = [row for row in rows if row.get("event") == "memo_progress"]
    last_states = 0
    last_calls = 0
    last_seconds = 0.0
    for row in progress:
        states = row.get("memo_states")
        calls = row.get("calls")
        if type(states) is not int or type(calls) is not int:
            raise ValueError("malformed progress row")
        seconds = row.get("seconds")
        if row.get("n") != n or not isinstance(seconds, (int, float)):
            raise ValueError("progress identity/time drift")
        if states != last_states + 1_000_000 or calls <= last_calls or seconds < last_seconds:
            raise ValueError("non-monotone incremental evidence")
        if row.get("memo_bytes") != (1 << n) * 4:
            raise ValueError("packed-table byte count drift")
        last_states, last_calls, last_seconds = states, calls, float(seconds)

    terminal = [
        row for row in rows if row.get("event") in {"result", "controlled_timeout", "controlled_signal"}
    ]
    if len(terminal) != 1:
        raise ValueError("ledger must have exactly one mathematical/resource terminal")
    end = terminal[0]
    if end.get("n") != n or end.get("memo_bytes") != (1 << n) * 4:
        raise ValueError("terminal identity or packed allocation drift")
    expected_mode = "n23_performance_gate" if n == 23 else "n24_target"
    if end.get("mode") != expected_mode:
        raise ValueError("terminal mode drift")
    if (
        type(end.get("memo_states")) is not int
        or type(end.get("calls")) is not int
        or not isinstance(end.get("seconds"), (int, float))
        or end["memo_states"] < last_states
        or end["calls"] < last_calls
        or end["seconds"] < last_seconds
    ):
        raise ValueError("terminal counters/time do not exhaust the progress prefix")
    if end["event"] in {"controlled_timeout", "controlled_signal"}:
        if end["event"] == "controlled_timeout" and end["seconds"] < (38.0 if n == 23 else 54.0):
            raise ValueError("controlled timeout precedes its frozen deadline")
        if end["event"] == "controlled_signal" and end.get("signal") not in {2, 15}:
            raise ValueError("controlled signal identity drift")
        if certificate is not None and certificate.exists():
            raise ValueError("timeout must not emit a strategy certificate")
        status = "PASS_TIMEOUT_BRACKET" if end["event"] == "controlled_timeout" else "PASS_SIGNAL_BRACKET"
        print(json.dumps({"status": status, "n": n}, sort_keys=True))
        return

    if type(end.get("value")) is not int or end["value"] not in {-1, 0, 1}:
        raise ValueError("invalid exact outcome")
    if end["seconds"] > (38.0 if n == 23 else 54.0):
        raise ValueError("exact result exceeded its frozen internal deadline")
    if n == 23:
        if (
            end.get("value") != 0
            or end.get("memo_states") != N23_STATES
            or end.get("calls") != N23_CALLS
            or end.get("matches_frozen_gate") is not True
            or not isinstance(end.get("seconds"), (int, float))
            or end["seconds"] > 38.0
        ):
            raise ValueError("N=23 exact-count/performance gate failed")
    if end["value"] == 0:
        if end.get("certificate_emitted") is not False:
            raise ValueError("draw row claims an unnecessary certificate")
        if certificate is not None and certificate.exists() and certificate.stat().st_size:
            raise ValueError("draw must not emit strategy DAG bytes")
        status = "PASS_N23_GATE" if n == 23 else "PASS_EXACT_DRAW"
        print(json.dumps({"status": status, "n": n}, sort_keys=True))
        return
    if certificate is None or not certificate.is_file():
        raise ValueError("non-draw is quarantined without a strategy DAG")
    if end.get("certificate_emitted") is not True:
        raise ValueError("non-draw result did not bind certificate emission")
    verify_strategy_dag(certificate, n, campaign, end["value"])
    print(json.dumps({"status": "PASS_NON_DRAW_DAG", "n": n}, sort_keys=True))


def state_key(mask: int, deficit: int) -> tuple[int, int]:
    return mask, deficit


def expected_transition(mask: int, deficit: int, remaining_sum: int, move: int) -> dict[str, Any]:
    bit = 1 << (move - 1)
    if not mask & bit:
        raise ValueError("certificate move is absent from mask")
    swapped = move >= deficit
    return {
        "move": move,
        "swapped": swapped,
        "child_mask": mask ^ bit,
        "child_deficit": move - deficit if swapped else deficit - move,
        "child_sum": remaining_sum - move,
    }


def verify_edge(edge: dict[str, Any], base: dict[str, Any], nodes: dict[tuple[int, int], dict[str, Any]]) -> int:
    if set(edge) != {
        "move", "swapped", "child_mask", "child_deficit", "child_sum", "child_value", "move_value"
    }:
        raise ValueError("non-canonical strategy edge payload")
    move = edge.get("move")
    if type(move) is not int or move < 1 or type(edge.get("swapped")) is not bool:
        raise ValueError("invalid certificate move")
    expected = expected_transition(base["mask"], base["deficit"], base["remaining_sum"], move)
    for key, value in expected.items():
        if edge.get(key) != value:
            raise ValueError(f"strategy transition drift for {key}")
    if bin(edge["child_mask"]).count("1") != bin(base["mask"]).count("1") - 1:
        raise ValueError("strategy edge does not strictly reduce mask cardinality")
    child = nodes.get(state_key(edge["child_mask"], edge["child_deficit"]))
    if child is None:
        raise ValueError("strategy edge references a missing node")
    if child["remaining_sum"] != edge["child_sum"] or child["value"] != edge.get("child_value"):
        raise ValueError("strategy child payload mismatch")
    move_value = -child["value"] if edge["swapped"] else child["value"]
    if edge.get("move_value") != move_value:
        raise ValueError("strategy sign-change mismatch")
    return move_value


def verify_strategy_dag(path: Path, n: int, campaign: str, root_value: int) -> None:
    rows = canonical_rows(path)
    if rows[0] != {
        "event": "certificate_start",
        "schema": "catchup-parity-packed-v1-strategy-dag",
        "n": n,
        "campaign_commit": campaign,
        "root_value": root_value,
    }:
        raise ValueError("certificate header drift")
    if rows[-1].get("event") != "certificate_end" or set(rows[-1]) != {"event", "nodes"}:
        raise ValueError("certificate missing end row")
    events = [row.get("event") for row in rows]
    if (
        len(rows) < 4
        or events[0] != "certificate_start"
        or events[-2] != "root"
        or events[-1] != "certificate_end"
        or any(event != "node" for event in events[1:-2])
    ):
        raise ValueError("certificate event ordering/schema drift")
    node_rows = [row for row in rows if row.get("event") == "node"]
    roots = [row for row in rows if row.get("event") == "root"]
    if len(roots) != 1 or root_value not in {-1, 1}:
        raise ValueError("certificate requires one non-draw root")
    nodes: dict[tuple[int, int], dict[str, Any]] = {}
    full = (1 << n) - 1
    for node in node_rows:
        if set(node) != {"event", "mask", "deficit", "remaining_sum", "value", "edges"}:
            raise ValueError("non-canonical node payload")
        mask = node.get("mask")
        deficit = node.get("deficit")
        remaining_sum = node.get("remaining_sum")
        value = node.get("value")
        if not all(type(x) is int for x in (mask, deficit, remaining_sum, value)):
            raise ValueError("malformed node scalar")
        if mask < 0 or mask > full or deficit < 0 or deficit > n or value not in {-1, 1}:
            raise ValueError("node scalar outside frozen bounds")
        true_sum = sum(i + 1 for i in range(n) if mask & (1 << i))
        if remaining_sum != true_sum or (remaining_sum + deficit - n * (n + 1) // 2) % 2:
            raise ValueError("node sum/parity invariant failed")
        key = state_key(mask, deficit)
        if key in nodes:
            raise ValueError("duplicate strategy node")
        nodes[key] = node
    if rows[-1].get("nodes") != len(nodes):
        raise ValueError("certificate node count drift")

    for node in nodes.values():
        edges = node.get("edges")
        if not isinstance(edges, list):
            raise ValueError("node edges are not a list")
        terminal_loss = node["remaining_sum"] < node["deficit"]
        if node["mask"] == 0 or terminal_loss:
            expected = 0 if node["mask"] == 0 and node["deficit"] == 0 else -1
            if node["value"] != expected or edges:
                raise ValueError("terminal/pruned node semantics failed")
            continue
        values = [verify_edge(edge, node, nodes) for edge in edges]
        moves = [edge["move"] for edge in edges]
        legal = [i + 1 for i in range(n) if node["mask"] & (1 << i)]
        if node["value"] == 1:
            if len(values) != 1 or values[0] != 1:
                raise ValueError("winning node lacks one winning move")
        else:
            if moves != legal or any(value != -1 for value in values):
                raise ValueError("losing node does not certify every legal move")

    root = roots[0]
    if set(root) != {"event", "value", "edges"}:
        raise ValueError("non-canonical root payload")
    if root.get("value") != root_value or not isinstance(root.get("edges"), list):
        raise ValueError("root payload drift")
    root_base = {"mask": full, "deficit": 0, "remaining_sum": n * (n + 1) // 2}
    root_values = []
    root_moves = []
    reachable: set[tuple[int, int]] = set()
    for edge in root["edges"]:
        move = edge.get("move")
        if type(move) is not int or not 1 <= move <= n:
            raise ValueError("invalid opening move")
        expected = {
            "move": move,
            "swapped": True,
            "child_mask": full ^ (1 << (move - 1)),
            "child_deficit": move,
            "child_sum": n * (n + 1) // 2 - move,
        }
        for key, value in expected.items():
            if edge.get(key) != value:
                raise ValueError(f"root transition drift for {key}")
        child = nodes.get(state_key(edge["child_mask"], edge["child_deficit"]))
        if child is None or child["value"] != edge.get("child_value"):
            raise ValueError("root references missing/mismatched child")
        move_value = -child["value"]
        if edge.get("move_value") != move_value:
            raise ValueError("root sign-change mismatch")
        root_values.append(move_value)
        root_moves.append(move)
        reachable.add(state_key(edge["child_mask"], edge["child_deficit"]))
    if root_value == 1:
        if len(root_values) != 1 or root_values[0] != 1:
            raise ValueError("winning root lacks one winning opening")
    elif root_moves != list(range(1, n + 1)) or any(value != -1 for value in root_values):
        raise ValueError("losing root does not certify every opening")

    stack = list(reachable)
    while stack:
        key = stack.pop()
        node = nodes[key]
        for edge in node["edges"]:
            child_key = state_key(edge["child_mask"], edge["child_deficit"])
            if child_key not in reachable:
                reachable.add(child_key)
                stack.append(child_key)
    if reachable != set(nodes):
        raise ValueError("strategy DAG contains unreachable nodes")


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    small = sub.add_parser("small-reference")
    small.add_argument("solver", type=Path)
    small.add_argument("--maximum", type=int, default=12)
    ledger = sub.add_parser("ledger")
    ledger.add_argument("path", type=Path)
    ledger.add_argument("--n", type=int, choices=(23, 24), required=True)
    ledger.add_argument("--campaign-commit", required=True)
    ledger.add_argument("--certificate", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "small-reference":
            run_small_reference(args.solver, args.maximum)
        else:
            verify_ledger(args.path, args.n, args.campaign_commit, args.certificate)
    except (AssertionError, OSError, subprocess.SubprocessError, ValueError) as exc:
        print(f"verification failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
    if end.get("value_name") != {-1: "loss", 0: "draw", 1: "win"}[end["value"]]:
        raise ValueError("exact outcome name drift")
    if end.get("matches_frozen_gate") is not True:
        raise ValueError("exact result did not pass its frozen gate")
