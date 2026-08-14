#!/usr/bin/env python3
"""Frozen three-arm Graffiti³ Conjecture 13 DEVELOPMENT worker."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Iterable, Mapping, Sequence

from prepare_graffiti3_conjecture13_gate import (
    DEFAULT_MANIFEST, GateError, canonical_json, load_manifest, parse_oeis,
    primes_through, segmented_phi, self_hash, sha256_file, verify_bundle,
    write_json_fsync,
)


ARMS = ("CATALOGUE", "GENERIC", "WALL_NAVIGATION")
SHARDS = 24
BOUNDARY = 2_000_000
INTERNAL_SECONDS = 54.0
CHILD_SECONDS = 4.0
LEDGER_SCHEMA = "c5k4-graffiti3-conjecture13-ledger-1.0"
TERMINAL_SCHEMA = "c5k4-graffiti3-conjecture13-terminal-1.0"
CERTIFICATE_SCHEMA = "c5k4-graffiti3-conjecture13-certificate-1.0"
GENERIC_BLOCK_SCHEMA = "c5k4-graffiti3-conjecture13-generic-block-1.0"
ZERO_SHA = "0" * 64
TERMINALS = {"DOMAIN_EXHAUSTED", "DEADLINE_PREFIX", "CERTIFICATE_FOUND", "SANITY_GATE_FAILED", "WORKER_ERROR"}


class SearchError(ValueError):
    pass


def is_prime64(n: int) -> bool:
    if n < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in small:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        s += 1
        d //= 2
    for a in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def factor_with_primes(n: int, primes: Sequence[int], deadline: float | None = None) -> dict[int, int]:
    remaining = n
    factors: dict[int, int] = {}
    for index, p in enumerate(primes):
        if deadline is not None and index % 1024 == 0 and time.monotonic() >= deadline:
            raise TimeoutError("internal deadline during factorization")
        if p * p > remaining:
            break
        while remaining % p == 0:
            factors[p] = factors.get(p, 0) + 1
            remaining //= p
    if remaining > 1:
        if not is_prime64(remaining):
            raise SearchError("prime table did not cover factorization")
        factors[remaining] = factors.get(remaining, 0) + 1
    if math.prod(p ** e for p, e in factors.items()) != n:
        raise SearchError("factorization product mismatch")
    return factors


def phi_from_factors(n: int, factors: Mapping[int, int]) -> int:
    phi = n
    for p in factors:
        phi -= phi // p
    return phi


def is_carmichael(n: int, factors: Mapping[int, int]) -> bool:
    return len(factors) >= 3 and all(e == 1 for e in factors.values()) and all((n - 1) % (p - 1) == 0 for p in factors)


@dataclass(frozen=True)
class Evaluation:
    n: int
    arm: str
    provenance: str
    factors: tuple[tuple[int, int], ...]
    phi: int
    margin_t: int
    modular_residue: int
    composite: bool
    carmichael: bool
    crossing: bool


def evaluate(n: int, arm: str, provenance: str, primes: Sequence[int],
             known_factors: Mapping[int, int] | None = None,
             deadline: float | None = None) -> Evaluation:
    if n <= BOUNDARY:
        raise SearchError("target boundary violated")
    if known_factors is None:
        factors = factor_with_primes(n, primes, deadline)
    else:
        factors = dict(known_factors)
        if (not factors or any(e < 1 or not is_prime64(p) for p, e in factors.items())
                or math.prod(p ** e for p, e in factors.items()) != n):
            raise SearchError("supplied exact factor tuple failed replay")
    phi = phi_from_factors(n, factors)
    composite = not (len(factors) == 1 and next(iter(factors.values())) == 1)
    residue = pow(2, n - 1, n) if composite and n % 2 else -1
    margin = 9 * n - 19 * phi
    carmichael = is_carmichael(n, factors)
    return Evaluation(n, arm, provenance, tuple(sorted(factors.items())), phi, margin,
                      residue, composite, carmichael,
                      composite and n % 2 == 1 and residue == 1 and margin >= 0)


@dataclass
class Counters:
    proposed: int = 0
    exact_evaluated: int = 0
    excluded_overlap: int = 0
    child_timeouts: int = 0
    crossings: int = 0


class Ledger:
    def __init__(self, path: Path, arm: str, shard: int, commit: str):
        self.path, self.arm, self.shard, self.commit = path, arm, shard, commit
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            raise SearchError("ledger exists")
        self.sequence, self.previous = 0, ZERO_SHA
        self.counters = Counters()
        self.started = time.monotonic()
        self.emit("start", {})

    def emit(self, kind: str, payload: Mapping[str, Any]) -> None:
        row: dict[str, Any] = {
            "schema": LEDGER_SCHEMA, "sequence": self.sequence,
            "previous_row_sha256": self.previous, "arm": self.arm,
            "shard": self.shard, "campaign_commit": self.commit,
            "kind": kind, "payload": dict(payload), "counters": asdict(self.counters),
        }
        row["row_sha256"] = hashlib.sha256(canonical_json(row)).hexdigest()
        with self.path.open("ab") as handle:
            handle.write(canonical_json(row)); handle.flush(); os.fsync(handle.fileno())
        self.sequence += 1; self.previous = row["row_sha256"]


def terminal(path: Path, ledger: Ledger, reason: str) -> None:
    if reason not in TERMINALS:
        raise SearchError("bad terminal")
    ledger.emit("terminal", {"terminal_reason": reason})
    write_json_fsync(path, {
        "schema": TERMINAL_SCHEMA, "terminal_reason": reason,
        "arm": ledger.arm, "shard": ledger.shard,
        "campaign_commit": ledger.commit, "ledger_sha256": sha256_file(ledger.path),
        "final_row_sha256": ledger.previous, "final_sequence": ledger.sequence - 1,
        "counters": asdict(ledger.counters),
    })


def snapshot_paths(bundle: Path) -> tuple[Path, Path]:
    return bundle / "snapshots/b001567.txt", bundle / "snapshots/b002997.txt"


def partition(values: Sequence[int], shard: int) -> Sequence[int]:
    q, r = divmod(len(values), SHARDS)
    start = shard * q + min(shard, r)
    size = q + (1 if shard < r else 0)
    return values[start:start + size]


def generic_block(manifest: Mapping[str, Any], shard: int) -> tuple[int, int]:
    spec = manifest["generic"]
    width = int(spec["block_width"])
    first = BOUNDARY + 1
    count = (int(spec["upper_exclusive"]) - first) // width
    if count <= SHARDS:
        raise SearchError("generic domain cannot supply disjoint shard blocks")
    base = int.from_bytes(hashlib.sha256(spec["seed"].encode("ascii")).digest(), "big") % (count - SHARDS + 1)
    index = base + shard
    start = first + index * width
    return start, start + width - 1


def scan_generic_block(start: int, end: int) -> dict[str, Any]:
    phis = segmented_phi(start, end)
    candidates: list[dict[str, int]] = []
    premise_rows = 0
    for n, phi in zip(range(start, end + 1), phis):
        if n % 2 == 0 or phi == n - 1:
            continue
        margin = 9 * n - 19 * phi
        if margin < 0:
            continue
        premise_rows += 1
        residue = pow(2, n - 1, n)
        if residue == 1:
            candidates.append({"n": n, "phi": phi, "margin_t": margin, "modular_residue": residue})
    receipt: dict[str, Any] = {
        "schema": GENERIC_BLOCK_SCHEMA, "start": start, "end": end,
        "evaluated": end - start + 1, "premise_composites": premise_rows,
        "candidates": candidates,
    }
    receipt["receipt_sha256"] = self_hash(receipt, "receipt_sha256")
    return receipt


def validate_generic_block(block: Mapping[str, Any], start: int, end: int) -> None:
    if (set(block) != {"schema", "start", "end", "evaluated",
                       "premise_composites", "candidates", "receipt_sha256"}
            or block.get("schema") != GENERIC_BLOCK_SCHEMA
            or block.get("receipt_sha256") != self_hash(block, "receipt_sha256")
            or block.get("start") != start or block.get("end") != end
            or block.get("evaluated") != end - start + 1
            or not isinstance(block.get("premise_composites"), int)
            or not isinstance(block.get("candidates"), list)
            or not 0 <= block["premise_composites"] <= block["evaluated"]
            or len(block["candidates"]) > block["premise_composites"]):
        raise SearchError("generic block receipt is malformed or partial")
    previous = start - 1
    for row in block["candidates"]:
        if (not isinstance(row, dict)
                or set(row) != {"n", "phi", "margin_t", "modular_residue"}
                or not all(isinstance(row.get(key), int) for key in row)
                or not start <= row["n"] <= end or row["n"] <= previous
                or row["n"] % 2 == 0 or row["modular_residue"] != 1
                or row["margin_t"] != 9 * row["n"] - 19 * row["phi"]
                or row["margin_t"] < 0):
            raise SearchError("generic candidate receipt row failed replay")
        previous = row["n"]


def divisors_from_factors(factors: Mapping[int, int]) -> list[int]:
    values = [1]
    for p, e in factors.items():
        values = [base * p ** power for base in values for power in range(e + 1)]
    return sorted(values)


def korselt_extensions(n: int, factors: Mapping[int, int], primes: Sequence[int],
                       deadline: float | None = None) -> Iterable[tuple[int, dict[int, int]]]:
    modulus = math.lcm(*(p - 1 for p in factors))
    nm1 = factor_with_primes(n - 1, primes, deadline)
    for divisor in divisors_from_factors(nm1):
        if deadline is not None and time.monotonic() >= deadline:
            raise TimeoutError("internal deadline during Korselt expansion")
        q = divisor + 1
        if q in factors or q % modulus != 1 or not is_prime64(q):
            continue
        child_factors = dict(factors); child_factors[q] = 1
        child = n * q
        if is_carmichael(child, child_factors):
            yield child, child_factors


def wall_values(values_2997: Sequence[int], primes: Sequence[int], max_n: int,
                depth: int, deadline: float | None = None
                ) -> tuple[dict[int, tuple[dict[int, int] | None, dict[str, Any]]], bool]:
    identities: dict[int, tuple[dict[int, int] | None, dict[str, Any]]] = {
        n: (None, {"kind": "A002997"}) for n in values_2997 if BOUNDARY < n < max_n
    }
    frontier: list[tuple[int, dict[int, int], int, tuple[int, ...]]] = []
    for n in values_2997:
        if deadline is not None and time.monotonic() >= deadline:
            return identities, False
        if n > BOUNDARY:
            break
        try:
            factors = factor_with_primes(n, primes, deadline)
        except TimeoutError:
            return identities, False
        frontier.append((n, factors, n, ()))
    factor_limit = primes[-1] if primes else 1
    for _depth in range(depth):
        next_frontier: list[tuple[int, dict[int, int], int, tuple[int, ...]]] = []
        for n, factors, seed, extension_primes in frontier:
            if deadline is not None and time.monotonic() >= deadline:
                return identities, False
            try:
                for child, child_factors in korselt_extensions(n, factors, primes, deadline):
                    if child >= max_n:
                        continue
                    child_extensions = extension_primes + (child // n,)
                    if child > BOUNDARY:
                        identities[child] = (
                            child_factors,
                            {"kind": "korselt_chain", "seed": seed,
                             "extension_primes": list(child_extensions)},
                        )
                    # A child may be emitted from its already complete factor tuple,
                    # but may seed the next layer only if child-1 remains exactly
                    # factorable by the snapshot-derived prime table.
                    if math.isqrt(child - 1) <= factor_limit:
                        next_frontier.append((child, child_factors, seed, child_extensions))
            except TimeoutError:
                return identities, False
        frontier = next_frontier
    return identities, True


def candidate_document(evaluation: Evaluation, construction: Mapping[str, Any],
                       manifest_path: Path, campaign_commit: str) -> dict[str, Any]:
    return {
        "schema": CERTIFICATE_SCHEMA,
        "campaign_commit": campaign_commit,
        "manifest_sha256": sha256_file(manifest_path),
        "construction": dict(construction),
        "evaluation": asdict(evaluation),
    }


def run(args: argparse.Namespace) -> int:
    if len(args.campaign_commit) != 40 or any(c not in "0123456789abcdef" for c in args.campaign_commit):
        raise SearchError("exact campaign commit required")
    ledger = Ledger(args.ledger, args.arm, args.shard, args.campaign_commit)
    deadline = ledger.started + INTERNAL_SECONDS
    try:
        manifest = load_manifest(args.manifest)
        if (int(manifest["source"]["snapshot_max_n"]) != BOUNDARY
                or int(manifest["shards_per_arm"]) != SHARDS
                or float(manifest["internal_stop_seconds"]) != INTERNAL_SECONDS
                or float(manifest["external_stop_seconds"]) != 60.0
                or float(manifest["gate"]["child_cap_seconds"]) != CHILD_SECONDS
                or tuple(manifest["arms"]) != ARMS):
            raise SearchError("manifest/code frozen constants disagree")
        attestation = verify_bundle(
            args.manifest, args.gate_bundle, args.campaign_commit,
        )
        ledger.emit("database_sanity_attestation", {"attestation_sha256": attestation["attestation_sha256"], "coverage": attestation["coverage"]})
    except Exception as exc:
        ledger.emit("database_sanity_failure", {"error": type(exc).__name__, "message": str(exc)[:1000]})
        terminal(args.terminal, ledger, "SANITY_GATE_FAILED")
        return 3
    try:
        a1_path, a2_path = snapshot_paths(args.gate_bundle)
        values_1567 = parse_oeis(a1_path, manifest["oeis"]["A001567"])
        values_2997 = parse_oeis(a2_path, manifest["oeis"]["A002997"])
        locked_1567, locked_2997 = set(values_1567), set(values_2997)
        max_value = max(values_1567[-1], values_2997[-1])
        primes = primes_through(math.isqrt(max_value) + 1)
    except Exception as exc:
        ledger.emit("worker_error", {"phase": "snapshot_replay", "error": type(exc).__name__, "message": str(exc)[:1000]})
        terminal(args.terminal, ledger, "WORKER_ERROR")
        return 4

    construction_complete = True
    if args.arm == "CATALOGUE":
        domain = [n for n in values_1567 if n > BOUNDARY][:int(manifest["catalogue_limit"])]
        proposals: Iterable[tuple[int, str, Mapping[int, int] | None, Mapping[str, Any]]] = (
            (n, "locked A001567", None, {"kind": "A001567"})
            for n in partition(domain, args.shard)
        )
    elif args.arm == "WALL_NAVIGATION":
        wall = manifest["wall"]
        try:
            domain, construction_complete = wall_values(
                values_2997, primes, int(wall["max_n_exclusive"]),
                int(wall["extension_depth"]), deadline,
            )
        except Exception as exc:
            ledger.emit("worker_error", {"phase": "wall_construction", "error": type(exc).__name__, "message": str(exc)[:1000]})
            terminal(args.terminal, ledger, "WORKER_ERROR")
            return 4
        proposals = (
            (n, "locked/extended Korselt wall", domain[n][0], domain[n][1])
            for n in sorted(domain)
            if int.from_bytes(hashlib.sha256(str(n).encode("ascii")).digest(), "big") % SHARDS == args.shard
        )
    else:
        start, end = generic_block(manifest, args.shard)
        child_output = args.ledger.parent / "generic-block.json"
        remaining_seconds = deadline - time.monotonic()
        if remaining_seconds <= 0:
            terminal(args.terminal, ledger, "DEADLINE_PREFIX")
            return 0
        try:
            subprocess.run(
                [sys.executable, __file__, "--scan-block", str(start), str(end), str(child_output)],
                check=True, timeout=min(CHILD_SECONDS, remaining_seconds),
                capture_output=True, text=True,
            )
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as exc:
            ledger.counters.child_timeouts += 1
            ledger.emit("generic_block_timeout", {"start": start, "end": end, "cap_seconds": CHILD_SECONDS, "error": type(exc).__name__})
            terminal(args.terminal, ledger, "DEADLINE_PREFIX")
            return 0
        try:
            block = json.loads(child_output.read_text(encoding="utf-8"))
            validate_generic_block(block, start, end)
        except Exception as exc:
            ledger.emit("worker_error", {"phase": "generic_receipt", "error": type(exc).__name__, "message": str(exc)[:1000]})
            terminal(args.terminal, ledger, "WORKER_ERROR")
            return 4
        ledger.counters.proposed += block["evaluated"]
        ledger.counters.exact_evaluated += block["evaluated"]
        ledger.emit("generic_block", {k: v for k, v in block.items() if k != "candidates"} | {"candidate_count": len(block["candidates"])})
        proposals = (
            (row["n"], "deterministic generic block", None,
             {"kind": "generic_block", "start": start, "end": end})
            for row in block["candidates"]
        )

    exhausted = construction_complete
    for n, provenance, known_factors, construction in proposals:
        if time.monotonic() >= deadline:
            exhausted = False; break
        if args.arm != "GENERIC":
            ledger.counters.proposed += 1
        try:
            row = evaluate(n, args.arm, provenance, primes, known_factors, deadline)
        except Exception as exc:
            ledger.emit("evaluation_error", {"n": n, "error": type(exc).__name__, "message": str(exc)[:1000], "mathematical_inference": "NONE"})
            if time.monotonic() >= deadline:
                terminal(args.terminal, ledger, "DEADLINE_PREFIX")
                return 0
            terminal(args.terminal, ledger, "WORKER_ERROR")
            return 4
        if args.arm == "CATALOGUE" and row.carmichael:
            ledger.counters.excluded_overlap += 1; ledger.emit("arm_overlap_excluded", {"n": n, "reason": "Carmichael belongs to wall"}); continue
        if args.arm == "WALL_NAVIGATION" and not row.carmichael:
            ledger.emit("evaluation_error", {"n": n, "reason": "wall identity failed Korselt", "mathematical_inference": "NONE"})
            terminal(args.terminal, ledger, "WORKER_ERROR")
            return 4
        if args.arm == "GENERIC" and (n in locked_1567 or n in locked_2997 or row.carmichael):
            ledger.counters.excluded_overlap += 1; ledger.emit("arm_overlap_excluded", {"n": n}); continue
        if args.arm != "GENERIC":
            ledger.counters.exact_evaluated += 1
        ledger.emit("exact_evaluation", asdict(row))
        if row.crossing:
            ledger.counters.crossings += 1
            write_json_fsync(
                args.certificate,
                candidate_document(row, construction, args.manifest, args.campaign_commit),
            )
            ledger.emit("candidate_certificate", {"n": n, "sha256": sha256_file(args.certificate)})
            terminal(args.terminal, ledger, "CERTIFICATE_FOUND")
            return 0
    terminal(args.terminal, ledger, "DOMAIN_EXHAUSTED" if exhausted else "DEADLINE_PREFIX")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan-block", nargs=3, metavar=("START", "END", "OUTPUT"))
    parser.add_argument("--arm", choices=ARMS)
    parser.add_argument("--shard", type=int, choices=range(SHARDS))
    parser.add_argument("--campaign-commit")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--gate-bundle", type=Path)
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--terminal", type=Path)
    parser.add_argument("--certificate", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.scan_block:
        start, end, output = args.scan_block
        write_json_fsync(Path(output), scan_generic_block(int(start), int(end)))
        raise SystemExit(0)
    required = (args.arm, args.shard, args.campaign_commit, args.gate_bundle, args.ledger, args.terminal, args.certificate)
    if any(value is None for value in required):
        raise SystemExit("missing worker arguments")
    raise SystemExit(run(args))
