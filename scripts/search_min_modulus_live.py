#!/usr/bin/env python3
"""Exact three-arm DEVELOPMENT search for the minimum-modulus conjecture."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import random
import time
from typing import Any, Iterator, Mapping, Sequence


ARMS = ("CATALOGUE", "GENERIC", "WALL_NAVIGATION")
SHARDS_PER_ARM = 8
INTERNAL_STOP_SECONDS = 54.0
GENERIC_PROPOSAL_LIMIT = 200_000
GENERIC_BASE_SEED = 0x4D494E4D4F44
WALL_BEAM_WIDTH = 128
WALL_MAX_DEPTH = 6
UPSTREAM_COMMIT = "942fb149e782a56c2719c543ab58e093f733acb4"
LEDGER_SCHEMA = "c5k4-min-modulus-live-jsonl-1.0"
TERMINAL_SCHEMA = "c5k4-min-modulus-live-terminal-1.0"
MANIFEST_SCHEMA = "c5k4-min-modulus-live-manifest-1.0"
TERMINAL_REASONS = {
    "DOMAIN_EXHAUSTED",
    "PROPOSAL_LIMIT",
    "SEARCH_EXHAUSTED",
    "DEADLINE_PREFIX",
    "CROSSING_VERIFIED",
    "WORKER_ERROR",
}
ZERO_SHA256 = "0" * 64
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = (
    REPO_ROOT
    / "results"
    / "expansion"
    / "live-search-2026-08-14"
    / "min-modulus-manifest.json"
)


class SearchError(ValueError):
    """Raised when frozen input or exact evaluation fails closed."""


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode(
        "ascii"
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_and_verify_manifest(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != MANIFEST_SCHEMA:
        raise SearchError("wrong minimum-modulus manifest schema")
    upstream = value.get("upstream")
    if not isinstance(upstream, dict) or upstream.get("commit") != UPSTREAM_COMMIT:
        raise SearchError("manifest is not pinned to the frozen upstream commit")
    if value.get("arms") != list(ARMS) or value.get("shards_per_arm") != SHARDS_PER_ARM:
        raise SearchError("manifest arm/shard geometry changed")
    contract = value.get("contract")
    if not isinstance(contract, dict):
        raise SearchError("manifest contract record is absent")
    contract_path = REPO_ROOT / str(contract.get("path", ""))
    if not contract_path.is_file() or sha256_file(contract_path) != contract.get("sha256"):
        raise SearchError("frozen contract digest mismatch")
    artifacts = value.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise SearchError("manifest implementation artifact lock is absent")
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            raise SearchError("malformed manifest artifact lock")
        artifact_path = REPO_ROOT / str(artifact.get("path", ""))
        if not artifact_path.is_file() or sha256_file(artifact_path) != artifact.get("sha256"):
            raise SearchError(f"frozen artifact digest mismatch: {artifact_path}")
    return value


def min_modulus(n: int) -> int:
    if n < 1:
        raise SearchError("min_modulus is used only for positive n")
    return (1 << n) - (1 << (n.bit_length() - 1))


def weak_compositions(total: int, parts: int) -> Iterator[tuple[int, ...]]:
    """Stars-and-bars generator used only by independent candidate replay."""

    if total < 0 or parts <= 0:
        raise SearchError("invalid weak-composition parameters")
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for tail in weak_compositions(total - first, parts - 1):
            yield (first, *tail)


def validate_residue_set(n: int, modulus: int, residues: Sequence[int]) -> tuple[int, ...]:
    if n < 2 or modulus <= 0:
        raise SearchError("target hypotheses require n >= 2 and positive modulus")
    normalized = tuple(sorted(int(value) % modulus for value in residues))
    if len(normalized) != n or len(set(normalized)) != n:
        raise SearchError("residue representative is not a size-n set")
    return normalized


def units_mod(modulus: int) -> tuple[int, ...]:
    return tuple(value for value in range(1, modulus) if math.gcd(value, modulus) == 1)


def canonical_residue_set(n: int, modulus: int, residues: Sequence[int]) -> tuple[int, ...]:
    """Exact affine canonicalization under translations and multiplication by units."""

    normalized = validate_residue_set(n, modulus, residues)
    candidates: list[tuple[int, ...]] = []
    for origin in normalized:
        translated = tuple((value - origin) % modulus for value in normalized)
        for unit in units_mod(modulus):
            candidates.append(tuple(sorted((unit * value) % modulus for value in translated)))
    if not candidates:
        raise SearchError("positive modulus unexpectedly has no units")
    return min(candidates)


def identity_sha256(n: int, modulus: int, residues: Sequence[int]) -> str:
    canonical = canonical_residue_set(n, modulus, residues)
    raw = canonical_json({"n": n, "modulus": modulus, "residues": list(canonical)})
    return hashlib.sha256(b"c5k4-min-modulus-identity-v1\0" + raw).hexdigest()


def exact_collision_profile(n: int, modulus: int, residues: Sequence[int]) -> dict[str, int]:
    """Count colliding weak compositions by an exact generating-function DP."""

    values = validate_residue_set(n, modulus, residues)
    dp = [[0] * modulus for _ in range(n + 1)]
    dp[0][0] = 1
    for value in values:
        next_dp = [[0] * modulus for _ in range(n + 1)]
        for mass in range(n + 1):
            for residue_class, count in enumerate(dp[mass]):
                if count == 0:
                    continue
                for multiplicity in range(n - mass + 1):
                    target = (residue_class + multiplicity * value) % modulus
                    next_dp[mass + multiplicity][target] += count
        dp = next_dp
    target_sum = sum(values) % modulus
    all_matching = dp[n][target_sum]
    if all_matching < 1:
        raise SearchError("all-ones multiplicity vector disappeared from exact DP")
    compositions = math.comb(2 * n - 1, n - 1)
    if sum(dp[n]) != compositions:
        raise SearchError("exact DP did not count every weak composition")
    return {
        "collision_count": all_matching - 1,
        "matching_composition_count": all_matching,
        "composition_count": compositions,
        "target_sum_modulus": target_sum,
    }


def replay_collision_count(n: int, modulus: int, residues: Sequence[int]) -> int:
    """Independent recursive replay used only after a proposed crossing."""

    values = validate_residue_set(n, modulus, residues)
    target = sum(values) % modulus
    all_ones = (1,) * n
    collisions = 0
    checked = 0
    for composition in weak_compositions(n, n):
        checked += 1
        if composition == all_ones:
            continue
        weighted = sum(count * value for count, value in zip(composition, values)) % modulus
        if weighted == target:
            collisions += 1
    if checked != math.comb(2 * n - 1, n - 1):
        raise SearchError("candidate replay did not exhaust weak compositions")
    return collisions


def database_sanity_gate() -> dict[str, Any]:
    controls = [
        (2, 2, (0, 1), 0, "boundary_n2_valid"),
        (3, 6, (0, 1, 3), 0, "boundary_n3_valid"),
        (3, 6, (0, 1, 2), 1, "documented_collision"),
    ]
    rows: list[dict[str, Any]] = []
    for n, modulus, residues, minimum_collisions, name in controls:
        profile = exact_collision_profile(n, modulus, residues)
        collisions = profile["collision_count"]
        if (minimum_collisions == 0 and collisions != 0) or (
            minimum_collisions > 0 and collisions < minimum_collisions
        ):
            raise SearchError(f"database-sanity control failed: {name}")
        rows.append({"name": name, "n": n, "modulus": modulus, **profile})
    try:
        validate_residue_set(2, 1, (0, 1))
    except SearchError:
        rejected_impossible_set = True
    else:  # pragma: no cover - protects against weakening the gate
        rejected_impossible_set = False
    if not rejected_impossible_set:
        raise SearchError("modulus-one cardinality control was accepted")
    return {"controls": rows, "modulus_one_size_two_rejected": True}


@dataclass
class Counters:
    proposed: int = 0
    canonical_unique: int = 0
    hypothesis_survivor: int = 0
    exact_evaluated: int = 0
    objective_scored: int = 0


class DurableLedger:
    def __init__(self, path: Path, arm: str, shard: int):
        if arm not in ARMS or not 0 <= shard < SHARDS_PER_ARM:
            raise SearchError("arm/shard is outside the frozen manifest")
        if path.exists() and path.stat().st_size:
            raise SearchError("ledger must be a fresh file")
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.arm = arm
        self.shard = shard
        self.started = time.monotonic()
        self.sequence = 0
        self.previous = ZERO_SHA256
        self.counters = Counters()
        self.emit("checkpoint", {"label": "started"})

    def emit(self, kind: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        row: dict[str, Any] = {
            "schema": LEDGER_SCHEMA,
            "kind": kind,
            "arm": self.arm,
            "shard": self.shard,
            "sequence": self.sequence,
            "elapsed_milliseconds": int((time.monotonic() - self.started) * 1000),
            "counters": asdict(self.counters),
            "previous_row_sha256": self.previous,
            **dict(payload),
        }
        row["row_sha256"] = hashlib.sha256(canonical_json(row)).hexdigest()
        raw = canonical_json(row)
        descriptor = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        try:
            view = memoryview(raw)
            while view:
                written = os.write(descriptor, view)
                if written <= 0:  # pragma: no cover
                    raise OSError("short durable ledger write")
                view = view[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        self.previous = row["row_sha256"]
        self.sequence += 1
        return row


def write_terminal(
    path: Path,
    ledger: DurableLedger,
    reason: str,
    cursor: Mapping[str, Any],
    crossing_verified: bool,
) -> dict[str, Any]:
    if reason not in TERMINAL_REASONS:
        raise SearchError("unknown terminal reason")
    terminal_row = ledger.emit(
        "terminal",
        {
            "terminal_reason": reason,
            "cursor": dict(cursor),
            "crossing_verified": crossing_verified,
        },
    )
    receipt = {
        "schema": TERMINAL_SCHEMA,
        "arm": ledger.arm,
        "shard": ledger.shard,
        "terminal_reason": reason,
        "cursor": dict(cursor),
        "crossing_verified": crossing_verified,
        "counters": asdict(ledger.counters),
        "final_row_sha256": terminal_row["row_sha256"],
    }
    raw = canonical_json(receipt)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.write(descriptor, raw)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    return receipt


class SearchRecorder:
    def __init__(self, ledger: DurableLedger):
        self.ledger = ledger
        self.seen: set[str] = set()

    def evaluate(
        self,
        n: int,
        modulus: int,
        residues: Sequence[int],
        provenance: Mapping[str, Any],
    ) -> tuple[dict[str, Any] | None, bool]:
        self.ledger.counters.proposed += 1
        canonical = canonical_residue_set(n, modulus, residues)
        identity = identity_sha256(n, modulus, canonical)
        if identity in self.seen:
            return None, False
        self.seen.add(identity)
        self.ledger.counters.canonical_unique += 1
        if not (2 <= n and 0 < modulus < min_modulus(n) and len(canonical) == n):
            return None, False
        self.ledger.counters.hypothesis_survivor += 1
        profile = exact_collision_profile(n, modulus, canonical)
        self.ledger.counters.exact_evaluated += 1
        self.ledger.counters.objective_scored += 1
        crossing = profile["collision_count"] == 0
        payload: dict[str, Any] = {
            "n": n,
            "modulus": modulus,
            "min_modulus": min_modulus(n),
            "modulus_gap": min_modulus(n) - modulus,
            "canonical_residues": list(canonical),
            "identity_sha256": identity,
            "objective": profile["collision_count"],
            "crossing": crossing,
            **profile,
            "provenance": dict(provenance),
        }
        if crossing:
            replay = replay_collision_count(n, modulus, canonical)
            payload["independent_replay_collision_count"] = replay
            if replay != 0:
                raise SearchError("candidate failed independent composition replay")
        self.ledger.emit("evaluated_candidate", payload)
        return payload, crossing


def deadline_reached(deadline: float) -> bool:
    return time.monotonic() >= deadline


def run_catalogue(recorder: SearchRecorder, shard: int, deadline: float) -> tuple[str, dict[str, Any]]:
    cursor: dict[str, Any] = {"n": 2, "modulus": 2, "combination_index": 0}
    for n in range(2, 7):
        for modulus in range(n, min_modulus(n)):
            for combination_index, tail in enumerate(itertools.combinations(range(1, modulus), n - 1)):
                cursor = {"n": n, "modulus": modulus, "combination_index": combination_index}
                if deadline_reached(deadline):
                    return "DEADLINE_PREFIX", cursor
                residues = (0, *tail)
                canonical = canonical_residue_set(n, modulus, residues)
                identity = identity_sha256(n, modulus, canonical)
                if int(identity, 16) % SHARDS_PER_ARM != shard:
                    continue
                _, crossing = recorder.evaluate(
                    n,
                    modulus,
                    residues,
                    {"generator": "catalogue", **cursor},
                )
                if crossing:
                    return "CROSSING_VERIFIED", cursor
    return "DOMAIN_EXHAUSTED", {"n": 7, "modulus": 0, "combination_index": 0}


def random_generic_proposal(rng: random.Random) -> tuple[int, int, tuple[int, ...]]:
    n = rng.randint(6, 11)
    ceiling = min_modulus(n)
    maximum_gap = ceiling - n
    gap = 1 + int(math.exp(rng.random() * math.log(maximum_gap))) if maximum_gap > 1 else 1
    modulus = ceiling - min(gap, maximum_gap)
    residues = (0, *sorted(rng.sample(range(1, modulus), n - 1)))
    return n, modulus, residues


def run_generic(recorder: SearchRecorder, shard: int, deadline: float) -> tuple[str, dict[str, Any]]:
    rng = random.Random(GENERIC_BASE_SEED + shard)
    for proposal_index in range(GENERIC_PROPOSAL_LIMIT):
        cursor = {"proposal_index": proposal_index, "seed": GENERIC_BASE_SEED + shard}
        if deadline_reached(deadline):
            return "DEADLINE_PREFIX", cursor
        n, modulus, residues = random_generic_proposal(rng)
        _, crossing = recorder.evaluate(
            n,
            modulus,
            residues,
            {"generator": "generic", **cursor},
        )
        if crossing:
            return "CROSSING_VERIFIED", cursor
    return "PROPOSAL_LIMIT", {
        "proposal_index": GENERIC_PROPOSAL_LIMIT,
        "seed": GENERIC_BASE_SEED + shard,
    }


def wall_children(n: int, modulus: int, residues: Sequence[int]) -> Iterator[tuple[int, tuple[int, ...], str]]:
    values = tuple(sorted(residues))
    if modulus - 1 >= n:
        reduced = tuple(sorted({value % (modulus - 1) for value in values}))
        if len(reduced) == n:
            yield modulus - 1, reduced, "decrement_modulus"
    for index in range(1, n):
        for delta in (-1, 1):
            changed = list(values)
            changed[index] = (changed[index] + delta) % modulus
            if len(set(changed)) == n:
                yield modulus, tuple(sorted(changed)), f"one_substitution:{index}:{delta}"
    for left, right in itertools.combinations(range(1, n), 2):
        for delta_left, delta_right in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
            changed = list(values)
            changed[left] = (changed[left] + delta_left) % modulus
            changed[right] = (changed[right] + delta_right) % modulus
            if len(set(changed)) == n:
                yield (
                    modulus,
                    tuple(sorted(changed)),
                    f"two_substitution:{left}:{delta_left}:{right}:{delta_right}",
                )


def run_wall_navigation(
    recorder: SearchRecorder, shard: int, deadline: float
) -> tuple[str, dict[str, Any]]:
    assigned_n = [n for n in range(3, 13) if (n - 3) % SHARDS_PER_ARM == shard]
    for n in assigned_n:
        threshold = min_modulus(n)
        root = (threshold, tuple((1 << exponent) - 1 for exponent in range(n)))
        frontier = [root]
        generated_seen = {(threshold, canonical_residue_set(n, threshold, root[1]))}
        for depth in range(1, WALL_MAX_DEPTH + 1):
            cursor = {"n": n, "depth": depth}
            candidates: list[tuple[tuple[Any, ...], int, tuple[int, ...], str]] = []
            for modulus, residues in frontier:
                for child_modulus, child_residues, operation in wall_children(n, modulus, residues):
                    if deadline_reached(deadline):
                        return "DEADLINE_PREFIX", cursor
                    canonical = canonical_residue_set(n, child_modulus, child_residues)
                    state = (child_modulus, canonical)
                    if state in generated_seen:
                        continue
                    generated_seen.add(state)
                    result, crossing = recorder.evaluate(
                        n,
                        child_modulus,
                        canonical,
                        {
                            "generator": "wall_navigation",
                            "n": n,
                            "depth": depth,
                            "operation": operation,
                            "parent_modulus": modulus,
                            "parent_residues": list(residues),
                        },
                    )
                    if crossing:
                        return "CROSSING_VERIFIED", cursor
                    if result is None:
                        continue
                    score = (
                        int(result["collision_count"]),
                        -int(result["modulus_gap"]),
                        tuple(int(value) for value in result["canonical_residues"]),
                    )
                    candidates.append((score, child_modulus, canonical, operation))
            candidates.sort(key=lambda row: row[0])
            frontier = [(modulus, residues) for _, modulus, residues, _ in candidates[:WALL_BEAM_WIDTH]]
            if not frontier:
                break
    return "SEARCH_EXHAUSTED", {"assigned_n": assigned_n, "max_depth": WALL_MAX_DEPTH}


def run_worker(
    arm: str,
    shard: int,
    ledger_path: Path,
    terminal_path: Path,
    manifest_path: Path,
) -> None:
    manifest = load_and_verify_manifest(manifest_path)
    if manifest["internal_stop_seconds"] != int(INTERNAL_STOP_SECONDS):
        raise SearchError("manifest internal deadline changed")
    ledger = DurableLedger(ledger_path, arm, shard)
    gate = database_sanity_gate()
    ledger.emit("database_sanity_gate", gate)
    recorder = SearchRecorder(ledger)
    deadline = ledger.started + INTERNAL_STOP_SECONDS
    crossing = False
    cursor: dict[str, Any] = {}
    try:
        if arm == "CATALOGUE":
            reason, cursor = run_catalogue(recorder, shard, deadline)
        elif arm == "GENERIC":
            reason, cursor = run_generic(recorder, shard, deadline)
        else:
            reason, cursor = run_wall_navigation(recorder, shard, deadline)
        crossing = reason == "CROSSING_VERIFIED"
    except Exception as exc:
        reason = "WORKER_ERROR"
        cursor = {"exception_type": type(exc).__name__, "message": str(exc)}
        write_terminal(terminal_path, ledger, reason, cursor, False)
        raise
    write_terminal(terminal_path, ledger, reason, cursor, crossing)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=ARMS, required=True)
    parser.add_argument("--shard", type=int, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--terminal", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args(argv)
    if not 0 <= args.shard < SHARDS_PER_ARM:
        parser.error(f"--shard must be in 0..{SHARDS_PER_ARM - 1}")
    try:
        run_worker(args.arm, args.shard, args.ledger, args.terminal, args.manifest)
    except (OSError, SearchError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
