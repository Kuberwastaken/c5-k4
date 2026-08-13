#!/usr/bin/env python3
"""Replay the frozen six-row Černý C13 two-cycle development trial."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from collections import deque
from pathlib import Path


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def image(mask: int, transition: tuple[int, ...]) -> int:
    result = 0
    while mask:
        bit = mask & -mask
        state = bit.bit_length() - 1
        result |= 1 << transition[state]
        mask -= bit
    return result


def replay(n: int, transitions: dict[str, tuple[int, ...]], word: str) -> int:
    mask = (1 << n) - 1
    for letter in word:
        mask = image(mask, transitions[letter])
    return mask


def shortest_reset(
    n: int, transitions: dict[str, tuple[int, ...]]
) -> tuple[int, str, int]:
    start = (1 << n) - 1
    queue = deque([start])
    parent: dict[int, tuple[int, str] | None] = {start: None}
    target = None
    while queue:
        mask = queue.popleft()
        if mask & (mask - 1) == 0:
            target = mask
            break
        for letter in ("a", "b"):
            child = image(mask, transitions[letter])
            if child not in parent:
                parent[child] = (mask, letter)
                queue.append(child)
    if target is None:
        raise AssertionError("automaton is not synchronizing")
    letters = []
    cursor = target
    while parent[cursor] is not None:
        cursor, letter = parent[cursor]  # type: ignore[misc]
        letters.append(letter)
    word = "".join(reversed(letters))
    assert replay(n, transitions, word) == target
    return len(word), word, target.bit_length() - 1


def cerny(n: int) -> dict[str, tuple[int, ...]]:
    a = tuple((i + 1) % n for i in range(n))
    b = tuple(0 if i == n - 1 else i for i in range(n))
    return {"a": a, "b": b}


def frozen_row(d: int) -> dict[str, tuple[int, ...]]:
    transitions = cerny(13)
    a = list(transitions["a"])
    a[d], a[12] = a[12], a[d]
    b = list(transitions["b"])
    b[1] = 0
    return {"a": tuple(a), "b": tuple(b)}


def serializable(transitions: dict[str, tuple[int, ...]]) -> dict[str, list[int]]:
    return {letter: list(transitions[letter]) for letter in ("a", "b")}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jsonl", type=Path)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--resolution-card-sha256")
    args = parser.parse_args()
    if bool(args.contract_sha256) != bool(args.resolution_card_sha256):
        parser.error("provide both integrity hashes or neither")

    started = time.monotonic()
    rows: list[dict[str, object]] = []
    for n in range(3, 13):
        length, word, target = shortest_reset(n, cerny(n))
        assert length == (n - 1) ** 2
        rows.append(
            {
                "kind": "calibration_row",
                "n": n,
                "shortest_reset_length": length,
                "expected": (n - 1) ** 2,
                "word": word,
                "target": target,
                "artifact_sha256": digest(serializable(cerny(n))),
                "evidence_split": "CALIBRATION",
            }
        )

    manifest = [serializable(frozen_row(d)) for d in range(1, 7)]
    manifest_sha = digest(manifest)
    for d, transitions in zip(range(1, 7), map(frozen_row, range(1, 7))):
        row_started = time.monotonic()
        length, word, target = shortest_reset(13, transitions)
        elapsed = time.monotonic() - row_started
        assert length == 23 - 2 * d
        rows.append(
            {
                "kind": "candidate_evaluated",
                "d": d,
                "cycle_lengths": [d + 1, 12 - d],
                "shortest_reset_length": length,
                "residual_144_minus_length": 144 - length,
                "word": word,
                "target": target,
                "carrier_sha256": digest(serializable(transitions)),
                "family_manifest_sha256": manifest_sha,
                "evidence_split": "DEVELOPMENT",
                "wall_seconds": elapsed,
            }
        )
    total = time.monotonic() - started
    if total > 60:
        raise TimeoutError(f"trial exceeded 60-second cap: {total:.6f}")

    if args.contract_sha256:
        for row in rows:
            row["contract_sha256"] = args.contract_sha256
            row["resolution_card_sha256"] = args.resolution_card_sha256

    output = "".join(canonical(row).decode() for row in rows)
    if args.jsonl:
        args.jsonl.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    print(
        json.dumps(
            {
                "calibration_rows": 10,
                "development_rows": 6,
                "family_manifest_sha256": manifest_sha,
                "total_wall_seconds": total,
                "verdict": "HOLD_BOUNDED",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
