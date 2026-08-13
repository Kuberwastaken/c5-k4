#!/usr/bin/env python3
"""Exact Phase 1 evaluator for the frozen Cyclic(43) orbit flips."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "results/expansion/phase1_ramsey55_cyclic43_orbit_flip_ledger.jsonl"
ORDER = 43
BASE_RED_DISTANCES = frozenset({1, 2, 7, 10, 12, 13, 14, 16, 18, 20, 21})
FROZEN_DELETIONS = (1, 2, 20, 21)
FIVE_SUBSETS = 962598


def emit(record: dict) -> None:
    with LEDGER.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()


def cyclic_distance(u: int, v: int) -> int:
    delta = (u - v) % ORDER
    return min(delta, ORDER - delta)


def adjacency_masks(red_distances: frozenset[int]) -> list[int]:
    masks = [0] * ORDER
    for u in range(ORDER):
        for v in range(u + 1, ORDER):
            if cyclic_distance(u, v) in red_distances:
                masks[u] |= 1 << v
                masks[v] |= 1 << u
    return masks


def complement_masks(masks: list[int]) -> list[int]:
    full = (1 << ORDER) - 1
    return [(full ^ (1 << v) ^ masks[v]) for v in range(ORDER)]


def edge_list(masks: list[int]) -> list[tuple[int, int]]:
    return [
        (u, v)
        for u in range(ORDER)
        for v in range(u + 1, ORDER)
        if masks[u] & (1 << v)
    ]


def edge_hash(masks: list[int]) -> str:
    payload = "".join(f"{u},{v}\n" for u, v in edge_list(masks)).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def is_clique(vertices: tuple[int, ...], masks: list[int]) -> bool:
    for i, u in enumerate(vertices):
        required = 0
        for v in vertices[i + 1 :]:
            required |= 1 << v
        if masks[u] & required != required:
            return False
    return True


def count_five_cliques(
    red_masks: list[int], blue_masks: list[int]
) -> tuple[int, int, list[int] | None, list[int] | None, list[tuple[int, ...]]]:
    red_count = 0
    blue_count = 0
    first_red = None
    first_blue = None
    all_red = []
    checked = 0
    for vertices in itertools.combinations(range(ORDER), 5):
        checked += 1
        if is_clique(vertices, red_masks):
            red_count += 1
            all_red.append(vertices)
            if first_red is None:
                first_red = list(vertices)
        if is_clique(vertices, blue_masks):
            blue_count += 1
            if first_blue is None:
                first_blue = list(vertices)
    assert checked == FIVE_SUBSETS
    return red_count, blue_count, first_red, first_blue, all_red


def expected_baseline_red_cliques() -> set[tuple[int, ...]]:
    return {
        tuple(sorted(((shift + v) % ORDER for v in (0, 1, 2, 22, 23))))
        for shift in range(ORDER)
    }


def maximum_clique_bron_kerbosch(masks: list[int]) -> tuple[int, list[int]]:
    best: list[int] = []

    def expand(chosen: list[int], candidates: int) -> None:
        nonlocal best
        if len(chosen) + candidates.bit_count() <= len(best):
            return
        if not candidates:
            if len(chosen) > len(best):
                best = chosen.copy()
            return
        while candidates:
            bit = candidates & -candidates
            vertex = bit.bit_length() - 1
            expand(chosen + [vertex], candidates & masks[vertex])
            candidates ^= bit
            if len(chosen) + candidates.bit_count() <= len(best):
                return

    expand([], (1 << ORDER) - 1)
    return len(best), best


def common_record(red_distances: frozenset[int]) -> tuple[list[int], list[int], dict]:
    red_masks = adjacency_masks(red_distances)
    blue_masks = complement_masks(red_masks)
    red_edges = edge_list(red_masks)
    blue_edges = edge_list(blue_masks)
    assert len(red_edges) + len(blue_edges) == ORDER * (ORDER - 1) // 2
    return red_masks, blue_masks, {
        "vertices": ORDER,
        "red_distances": sorted(red_distances),
        "red_edges": len(red_edges),
        "blue_edges": len(blue_edges),
        "red_edge_list_sha256": edge_hash(red_masks),
        "blue_edge_list_sha256": edge_hash(blue_masks),
        "five_subsets_checked": FIVE_SUBSETS,
    }


def run_baseline() -> None:
    started = time.monotonic()
    red_masks, blue_masks, record = common_record(BASE_RED_DISTANCES)
    red_count, blue_count, first_red, first_blue, all_red = count_five_cliques(
        red_masks, blue_masks
    )
    expected = expected_baseline_red_cliques()
    actual = set(all_red)
    record.update(
        {
            "event": "baseline_gate",
            "red_k5_count": red_count,
            "blue_k5_count": blue_count,
            "first_red_k5": first_red,
            "first_blue_k5": first_blue,
            "red_k5_translate_family_sha256": hashlib.sha256(
                "".join(",".join(map(str, clique)) + "\n" for clique in sorted(actual)).encode(
                    "ascii"
                )
            ).hexdigest(),
            "translate_family_exact": actual == expected,
            "elapsed_seconds": round(time.monotonic() - started, 6),
        }
    )
    emit(record)
    if red_count != 43 or blue_count != 0 or actual != expected:
        raise RuntimeError("Cyclic(43) baseline gate mismatch")
    print(json.dumps(record, sort_keys=True))


def run_candidate(deleted_distance: int) -> None:
    if deleted_distance not in FROZEN_DELETIONS:
        raise ValueError("distance is outside the frozen family")
    started = time.monotonic()
    red_distances = BASE_RED_DISTANCES - {deleted_distance}
    red_masks, blue_masks, record = common_record(red_distances)
    red_count, blue_count, first_red, first_blue, _ = count_five_cliques(
        red_masks, blue_masks
    )
    is_candidate = red_count == 0 and blue_count == 0
    record.update(
        {
            "event": "candidate",
            "id": f"cyclic43_delete_distance_{deleted_distance}",
            "deleted_distance": deleted_distance,
            "red_k5_count": red_count,
            "blue_k5_count": blue_count,
            "first_red_k5": first_red,
            "first_blue_k5": first_blue,
            "lower_bound_candidate": is_candidate,
        }
    )
    if is_candidate:
        red_omega, red_witness = maximum_clique_bron_kerbosch(red_masks)
        blue_omega, blue_witness = maximum_clique_bron_kerbosch(blue_masks)
        record.update(
            {
                "independent_oracle": "bron_kerbosch",
                "red_clique_number": red_omega,
                "blue_clique_number": blue_omega,
                "red_max_clique_witness": red_witness,
                "blue_max_clique_witness": blue_witness,
                "oracle_agrees": red_omega <= 4 and blue_omega <= 4,
            }
        )
        if not record["oracle_agrees"]:
            emit(record)
            raise RuntimeError("double-zero/Bron--Kerbosch disagreement")
    record["elapsed_seconds"] = round(time.monotonic() - started, 6)
    emit(record)
    print(json.dumps(record, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--baseline", action="store_true")
    group.add_argument("--candidate", type=int)
    args = parser.parse_args()
    if args.baseline:
        run_baseline()
    else:
        run_candidate(args.candidate)


if __name__ == "__main__":
    main()
