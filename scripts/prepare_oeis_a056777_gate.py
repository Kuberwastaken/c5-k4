#!/usr/bin/env python3
"""Prepare and verify the immutable source/table gate for A056777."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[1]
HERE = ROOT / "results/expansion/live-search-2026-08-14/oeis-a056777-development"
MANIFEST = HERE / "manifest.json"
M = json.loads(MANIFEST.read_text())
SCHEMA = "oeis-a056777-gate-v1"


def sha(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def canonical(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def self_hash(value: dict) -> str:
    copy = dict(value)
    copy.pop("attestation_sha256", None)
    return hashlib.sha256(canonical(copy)).hexdigest()


def atomic_json(path: pathlib.Path, value: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("xb") as stream:
        stream.write(canonical(value)); stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)


def exact_commit(value: str) -> str:
    if len(value) != 40 or any(c not in "0123456789abcdef" for c in value):
        raise ValueError("exact lowercase campaign commit required")
    return value


def primes_through(limit: int) -> list[int]:
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[:2] = b"\x00\x00"
    for p in range(2, math.isqrt(limit) + 1):
        if sieve[p]:
            sieve[p * p : limit + 1 : p] = b"\x00" * (((limit - p * p) // p) + 1)
    return [i for i, flag in enumerate(sieve) if flag]


def factor(n: int, primes: list[int]) -> list[tuple[int, int]]:
    result = []
    for p in primes:
        if p * p > n:
            break
        if n % p:
            continue
        exponent = 0
        while n % p == 0:
            exponent += 1; n //= p
        result.append((p, exponent))
    if n > 1:
        result.append((n, 1))
    return result


def arithmetic(factors: list[tuple[int, int]]) -> tuple[int, int]:
    phi = sigma = 1
    for p, e in factors:
        phi *= (p - 1) * p ** (e - 1)
        sigma *= (p ** (e + 1) - 1) // (p - 1)
    return phi, sigma


def prime_quadruple_witness(n: int, factors: list[tuple[int, int]]) -> int | None:
    if len(factors) != 2 or any(e != 1 for _, e in factors):
        return None
    p, q = factors[0][0], factors[1][0]
    return p if q == p + 8 else None


def parse_bfile(path: pathlib.Path) -> list[tuple[int, int]]:
    if sha(path) != M["oeis_bfile"]["sha256"]:
        raise ValueError("b-file hash drift")
    rows = []
    for line in path.read_text(encoding="ascii").splitlines():
        fields = line.split()
        if len(fields) != 2:
            raise ValueError("malformed b-file row")
        rows.append((int(fields[0]), int(fields[1])))
    spec = M["oeis_bfile"]
    if (len(rows) != spec["rows"] or [i for i, _ in rows] != list(range(1, len(rows) + 1))
            or list(rows[-1]) != [spec["last_index"], spec["last_value"]]):
        raise ValueError("b-file coverage drift")
    return rows


def verify_sources(lean: pathlib.Path, source: pathlib.Path, bfile: pathlib.Path) -> dict:
    if sha(lean) != M["formal_conjectures"]["sha256"]:
        raise ValueError("Lean source hash drift")
    lean_text = lean.read_text(encoding="utf-8")
    for token in ("def A (n : ℕ) : Prop", "def ComesFromPrimeQuadruple", "@[category research open, AMS 11]", "theorem comesFromPrimeQuadruple_of_a"):
        if token not in lean_text:
            raise ValueError("Lean declaration/status drift")
    if sha(source) != M["oeis_source"]["sha256"]:
        raise ValueError("OEIS source hash drift")
    source_text = source.read_text(encoding="utf-8")
    for token in ("%I A056777 #28 Jun 13 2026 17:40:34", "verified up to 10^12", "n = 1..166"):
        if token not in source_text:
            raise ValueError("OEIS statement drift")
    rows = parse_bfile(bfile)
    primes = primes_through(math.isqrt(rows[-1][1] + 12))
    previous = 0
    stream = hashlib.sha256()
    for index, n in rows:
        if n <= previous:
            raise ValueError("b-file values not strictly increasing")
        fn, fn12 = factor(n, primes), factor(n + 12, primes)
        phi, sigma = arithmetic(fn); phi12, sigma12 = arithmetic(fn12)
        p = prime_quadruple_witness(n, fn)
        if p is None or [q for q, e in fn12 if e == 1] != [p + 2, p + 6] or any(e != 1 for _, e in fn12):
            raise ValueError(f"b-file row {index} is not a prime-quadruple value")
        if phi12 != phi + 12 or sigma12 != sigma + 12:
            raise ValueError(f"b-file row {index} fails defining equations")
        stream.update(f"{index},{n},{p},{phi},{phi12},{sigma},{sigma12}\n".encode("ascii"))
        previous = n
    return {"rows": len(rows), "first": list(rows[0]), "last": list(rows[-1]), "verified_row_stream_sha256": stream.hexdigest()}


def prepare(lean: pathlib.Path, source: pathlib.Path, bfile: pathlib.Path, output: pathlib.Path, commit: str) -> None:
    commit = exact_commit(commit)
    table = verify_sources(lean, source, bfile)
    output.mkdir(parents=True, exist_ok=False)
    snapshots = output / "snapshots"; snapshots.mkdir()
    for incoming, name in ((lean, "56777.lean"), (source, "A056777.seq"), (bfile, "b056777.txt")):
        with incoming.open("rb") as src, (snapshots / name).open("xb") as dst:
            shutil.copyfileobj(src, dst); dst.flush(); os.fsync(dst.fileno())
    value = {
        "schema": SCHEMA,
        "campaign_commit": commit,
        "manifest_sha256": sha(MANIFEST),
        "source_commit": M["formal_conjectures"]["commit"],
        "historical_exclusion_upper_inclusive": M["historical_exclusion_upper_inclusive"],
        "table": table,
        "snapshots": {name: sha(snapshots / name) for name in ("56777.lean", "A056777.seq", "b056777.txt")},
    }
    value["attestation_sha256"] = self_hash(value)
    atomic_json(output / "gate-attestation.json", value)


def verify(bundle: pathlib.Path, commit: str) -> dict:
    commit = exact_commit(commit)
    value = json.loads((bundle / "gate-attestation.json").read_text())
    if set(value) != {"schema", "campaign_commit", "manifest_sha256", "source_commit", "historical_exclusion_upper_inclusive", "table", "snapshots", "attestation_sha256"}:
        raise ValueError("gate key drift")
    if value["schema"] != SCHEMA or value["attestation_sha256"] != self_hash(value):
        raise ValueError("gate self-hash drift")
    if value["campaign_commit"] != commit or value["manifest_sha256"] != sha(MANIFEST) or value["source_commit"] != M["formal_conjectures"]["commit"]:
        raise ValueError("gate binding drift")
    snapshots = bundle / "snapshots"
    actual = verify_sources(snapshots / "56777.lean", snapshots / "A056777.seq", snapshots / "b056777.txt")
    expected_snapshots = {name: sha(snapshots / name) for name in ("56777.lean", "A056777.seq", "b056777.txt")}
    if value["table"] != actual or value["snapshots"] != expected_snapshots or value["historical_exclusion_upper_inclusive"] != 10**12:
        raise ValueError("gate semantic drift")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(); sub = parser.add_subparsers(dest="mode", required=True)
    p = sub.add_parser("prepare"); p.add_argument("lean", type=pathlib.Path); p.add_argument("source", type=pathlib.Path); p.add_argument("bfile", type=pathlib.Path); p.add_argument("output", type=pathlib.Path); p.add_argument("--campaign-commit", required=True)
    p = sub.add_parser("verify"); p.add_argument("bundle", type=pathlib.Path); p.add_argument("--campaign-commit", required=True)
    args = parser.parse_args()
    if args.mode == "prepare": prepare(args.lean, args.source, args.bfile, args.output, args.campaign_commit)
    else: verify(args.bundle, args.campaign_commit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
