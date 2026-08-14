#!/usr/bin/env python3
"""Prepare/verify the reusable content-addressed Graffiti³ C13 database gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping


MANIFEST_SCHEMA = "c5k4-graffiti3-conjecture13-manifest-1.0"
CHUNK_SCHEMA = "c5k4-graffiti3-conjecture13-gate-chunk-1.0"
ATTESTATION_SCHEMA = "c5k4-graffiti3-conjecture13-gate-attestation-1.0"
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "results/expansion/live-search-2026-08-14/graffiti3-conjecture13-manifest.json"


class GateError(ValueError):
    pass


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json_fsync(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.write(canonical_json(value))
        handle.flush()
        os.fsync(handle.fileno())


def copy_fsync(source: Path, target: Path) -> None:
    with source.open("rb") as incoming, target.open("wb") as outgoing:
        for chunk in iter(lambda: incoming.read(1 << 20), b""):
            outgoing.write(chunk)
        outgoing.flush()
        os.fsync(outgoing.fileno())


def self_hash(value: Mapping[str, Any], field: str) -> str:
    clean = dict(value)
    clean.pop(field, None)
    return hashlib.sha256(canonical_json(clean)).hexdigest()


def load_manifest(path: Path, verify_artifacts: bool = True) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != MANIFEST_SCHEMA:
        raise GateError("manifest schema drift")
    if verify_artifacts:
        for artifact in value.get("artifacts", []):
            target = REPO_ROOT / str(artifact.get("path", ""))
            if not target.is_file() or sha256_file(target) != artifact.get("sha256"):
                raise GateError(f"artifact digest mismatch: {target}")
    return value


def primes_through(limit: int) -> list[int]:
    sieve = bytearray(b"\x01") * (limit + 1)
    if limit >= 0:
        sieve[0] = 0
    if limit >= 1:
        sieve[1] = 0
    for p in range(2, math.isqrt(limit) + 1):
        if sieve[p]:
            sieve[p * p:limit + 1:p] = b"\x00" * (((limit - p * p) // p) + 1)
    return [i for i, flag in enumerate(sieve) if flag]


def segmented_phi(start: int, end: int) -> list[int]:
    if start < 1 or end < start:
        raise GateError("invalid phi interval")
    values = list(range(start, end + 1))
    remaining = values.copy()
    for p in primes_through(math.isqrt(end)):
        first = ((start + p - 1) // p) * p
        for n in range(first, end + 1, p):
            idx = n - start
            values[idx] -= values[idx] // p
            while remaining[idx] % p == 0:
                remaining[idx] //= p
    for idx, rest in enumerate(remaining):
        if rest > 1:
            values[idx] -= values[idx] // rest
    return values


def factor_trial(n: int) -> dict[int, int]:
    if n < 1:
        raise GateError("factorization requires positive n")
    factors: dict[int, int] = {}
    remaining = n
    for p in primes_through(math.isqrt(n)):
        if p * p > remaining:
            break
        while remaining % p == 0:
            factors[p] = factors.get(p, 0) + 1
            remaining //= p
    if remaining > 1:
        factors[remaining] = factors.get(remaining, 0) + 1
    return factors


def phi_from_factors(n: int, factors: Mapping[int, int]) -> int:
    value = n
    for p in factors:
        value -= value // p
    return value


def control_profile(n: int) -> dict[str, Any]:
    factors = factor_trial(n)
    phi = phi_from_factors(n, factors)
    return {
        "n": n,
        "factors": [[p, e] for p, e in sorted(factors.items())],
        "phi": phi,
        "composite": len(factors) > 1 or next(iter(factors.values()), 0) > 1,
        "modular_residue": pow(2, n - 1, n),
        "premise": 19 * phi <= 9 * n,
    }


def make_chunk(start: int, end: int) -> dict[str, Any]:
    phis = segmented_phi(start, end)
    crossings = 0
    premise_rows = 0
    pseudoprimes = 0
    for n, phi in zip(range(start, end + 1), phis):
        composite = phi != n - 1
        premise = 19 * phi <= 9 * n
        if premise:
            premise_rows += 1
        if composite and n % 2 == 1 and pow(2, n - 1, n) == 1:
            pseudoprimes += 1
            if premise:
                crossings += 1
    receipt: dict[str, Any] = {
        "schema": CHUNK_SCHEMA,
        "start": start,
        "end": end,
        "evaluated": end - start + 1,
        "premise_rows": premise_rows,
        "base2_pseudoprimes": pseudoprimes,
        "crossings": crossings,
    }
    receipt["receipt_sha256"] = self_hash(receipt, "receipt_sha256")
    return receipt


def parse_oeis(path: Path, expected: Mapping[str, Any]) -> list[int]:
    if sha256_file(path) != expected.get("sha256"):
        raise GateError(f"OEIS snapshot hash mismatch: {path.name}")
    rows: list[tuple[int, int]] = []
    for line in path.read_text(encoding="ascii").splitlines():
        fields = line.split()
        if not fields:
            continue
        if len(fields) != 2:
            raise GateError("malformed OEIS b-file row")
        rows.append((int(fields[0]), int(fields[1])))
    if len(rows) != expected.get("rows"):
        raise GateError("OEIS row-count drift")
    if [idx for idx, _ in rows] != list(range(1, len(rows) + 1)):
        raise GateError("OEIS indices are not contiguous")
    if rows[-1] != (expected.get("last_index"), expected.get("last_value")):
        raise GateError("OEIS terminal row drift")
    return [value for _, value in rows]


def exact_commit(value: str) -> str:
    if len(value) != 40 or any(character not in "0123456789abcdef" for character in value):
        raise GateError("exact lowercase campaign commit required")
    return value


def prepare_bundle(
    manifest_path: Path, pdf: Path, a001567: Path, a002997: Path,
    output: Path, campaign_commit: str,
) -> dict[str, Any]:
    campaign_commit = exact_commit(campaign_commit)
    manifest = load_manifest(manifest_path)
    if sha256_file(pdf) != manifest["source"]["pdf_sha256"]:
        raise GateError("primary PDF hash mismatch")
    values_1567 = parse_oeis(a001567, manifest["oeis"]["A001567"])
    values_2997 = parse_oeis(a002997, manifest["oeis"]["A002997"])
    output.mkdir(parents=True, exist_ok=False)
    snapshot_dir = output / "snapshots"
    snapshot_dir.mkdir()
    for source, name in ((pdf, "graffiti3-v1.pdf"), (a001567, "b001567.txt"), (a002997, "b002997.txt")):
        copy_fsync(source, snapshot_dir / name)
    chunk_dir = output / "chunks"
    chunk_dir.mkdir()
    gate = manifest["gate"]
    receipts: list[dict[str, Any]] = []
    start = int(gate["min_n"])
    while start <= int(gate["max_n"]):
        end = min(start + int(gate["chunk_size"]) - 1, int(gate["max_n"]))
        path = chunk_dir / f"{start:07d}-{end:07d}.json"
        try:
            subprocess.run(
                [sys.executable, __file__, "--gate-chunk", str(start), str(end), str(path)],
                check=True, timeout=float(gate["child_cap_seconds"]), capture_output=True, text=True,
            )
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as exc:
            raise GateError(f"gate chunk failed or exceeded cap: {start}-{end}") from exc
        receipt = json.loads(path.read_text(encoding="utf-8"))
        if receipt.get("receipt_sha256") != self_hash(receipt, "receipt_sha256"):
            raise GateError("new chunk receipt self-hash failed")
        receipts.append({"path": str(path.relative_to(output)), "sha256": sha256_file(path), **receipt})
        start = end + 1
    controls = [control_profile(n) for n in gate["controls"]]
    if any(row["modular_residue"] != 1 or row["premise"] for row in controls):
        raise GateError("341/561 calibration failed")
    if sum(row["crossings"] for row in receipts) != 0:
        raise GateError("source snapshot contains a literal crossing")
    attestation: dict[str, Any] = {
        "schema": ATTESTATION_SCHEMA,
        "campaign_commit": campaign_commit,
        "manifest_sha256": sha256_file(manifest_path),
        "coverage": {"min_n": gate["min_n"], "max_n": gate["max_n"], "evaluated": int(gate["max_n"]) - int(gate["min_n"]) + 1},
        "crossings": 0,
        "controls": controls,
        "snapshots": {
            "pdf": {"path": "snapshots/graffiti3-v1.pdf", "sha256": sha256_file(snapshot_dir / "graffiti3-v1.pdf")},
            "A001567": {"path": "snapshots/b001567.txt", "sha256": sha256_file(snapshot_dir / "b001567.txt"), "rows": len(values_1567)},
            "A002997": {"path": "snapshots/b002997.txt", "sha256": sha256_file(snapshot_dir / "b002997.txt"), "rows": len(values_2997)},
        },
        "chunks": receipts,
    }
    attestation["attestation_sha256"] = self_hash(attestation, "attestation_sha256")
    write_json_fsync(output / "attestation.json", attestation)
    return attestation


def verify_bundle(manifest_path: Path, bundle: Path, campaign_commit: str) -> dict[str, Any]:
    campaign_commit = exact_commit(campaign_commit)
    manifest = load_manifest(manifest_path)
    attestation_path = bundle / "attestation.json"
    if not attestation_path.is_file():
        raise GateError("gate attestation missing")
    attestation = json.loads(attestation_path.read_text(encoding="utf-8"))
    if attestation.get("schema") != ATTESTATION_SCHEMA or attestation.get("attestation_sha256") != self_hash(attestation, "attestation_sha256"):
        raise GateError("attestation schema/self-hash failed")
    if attestation.get("manifest_sha256") != sha256_file(manifest_path):
        raise GateError("attestation belongs to a different manifest")
    if attestation.get("campaign_commit") != campaign_commit:
        raise GateError("attestation belongs to a different campaign commit")
    gate = manifest["gate"]
    if attestation.get("coverage") != {"min_n": gate["min_n"], "max_n": gate["max_n"], "evaluated": gate["max_n"] - gate["min_n"] + 1} or attestation.get("crossings") != 0:
        raise GateError("attestation coverage/crossing claim failed")
    expected_start = gate["min_n"]
    total = 0
    for descriptor in attestation.get("chunks", []):
        expected_end = min(expected_start + gate["chunk_size"] - 1, gate["max_n"])
        expected_relative = f"chunks/{expected_start:07d}-{expected_end:07d}.json"
        if descriptor.get("path") != expected_relative:
            raise GateError("chunk descriptor path/order drift")
        path = bundle / expected_relative
        if not path.is_file() or sha256_file(path) != descriptor.get("sha256"):
            raise GateError("chunk missing or tampered")
        row = json.loads(path.read_text(encoding="utf-8"))
        if (row.get("receipt_sha256") != self_hash(row, "receipt_sha256")
                or row.get("start") != expected_start or row.get("end") != expected_end
                or row.get("evaluated") != expected_end - expected_start + 1
                or row.get("crossings") != 0):
            raise GateError("chunk chain/receipt failed")
        for key in ("schema", "start", "end", "evaluated", "premise_rows",
                    "base2_pseudoprimes", "crossings", "receipt_sha256"):
            if descriptor.get(key) != row.get(key):
                raise GateError("chunk descriptor/receipt mismatch")
        expected_start = row["end"] + 1
        total += row["evaluated"]
    if expected_start != gate["max_n"] + 1 or total != gate["max_n"] - gate["min_n"] + 1:
        raise GateError("chunk coverage is partial or overlapping")
    snapshots = attestation.get("snapshots")
    expected_snapshots = {
        "pdf": {"path": "snapshots/graffiti3-v1.pdf", "sha256": manifest["source"]["pdf_sha256"]},
        "A001567": {"path": "snapshots/b001567.txt", "sha256": manifest["oeis"]["A001567"]["sha256"]},
        "A002997": {"path": "snapshots/b002997.txt", "sha256": manifest["oeis"]["A002997"]["sha256"]},
    }
    if not isinstance(snapshots, dict) or set(snapshots) != set(expected_snapshots):
        raise GateError("snapshot descriptor set drift")
    for key, expected in expected_snapshots.items():
        spec = snapshots[key]
        if spec.get("path") != expected["path"] or spec.get("sha256") != expected["sha256"]:
            raise GateError(f"snapshot identity drift: {key}")
        path = bundle / spec["path"]
        if not path.is_file() or sha256_file(path) != spec["sha256"]:
            raise GateError(f"snapshot missing/tampered: {key}")
    parse_oeis(bundle / attestation["snapshots"]["A001567"]["path"], manifest["oeis"]["A001567"])
    parse_oeis(bundle / attestation["snapshots"]["A002997"]["path"], manifest["oeis"]["A002997"])
    controls = {row["n"]: row for row in attestation.get("controls", [])}
    if set(controls) != set(gate["controls"]):
        raise GateError("control set mismatch")
    for n in gate["controls"]:
        if controls[n] != control_profile(n) or controls[n]["modular_residue"] != 1 or controls[n]["premise"]:
            raise GateError("control replay mismatch")
    return attestation


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--gate-chunk", nargs=3, metavar=("START", "END", "OUTPUT"))
    parser.add_argument("--prepare", nargs=4, metavar=("PDF", "A001567", "A002997", "OUTPUT"))
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--campaign-commit", required=False)
    args = parser.parse_args()
    if args.gate_chunk:
        start, end, output = args.gate_chunk
        write_json_fsync(Path(output), make_chunk(int(start), int(end)))
    elif args.prepare:
        if args.campaign_commit is None:
            parser.error("--campaign-commit is required with --prepare")
        pdf, a1, a2, output = map(Path, args.prepare)
        prepare_bundle(args.manifest, pdf, a1, a2, output, args.campaign_commit)
    elif args.verify:
        if args.campaign_commit is None:
            parser.error("--campaign-commit is required with --verify")
        verify_bundle(args.manifest, args.verify, args.campaign_commit)
    else:
        parser.error("choose one mode")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
