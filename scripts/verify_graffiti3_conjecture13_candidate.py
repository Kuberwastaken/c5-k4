#!/usr/bin/env python3
"""Independent fail-closed replay for a Graffiti³ Conjecture 13 candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping

from prepare_graffiti3_conjecture13_gate import (
    DEFAULT_MANIFEST, load_manifest, parse_oeis, sha256_file, verify_bundle,
)


SCHEMA = "c5k4-graffiti3-conjecture13-certificate-1.0"
BOUNDARY = 2_000_000
ARMS = {"CATALOGUE", "GENERIC", "WALL_NAVIGATION"}


class ReplayError(ValueError):
    pass


def prime64(n: int) -> bool:
    """Deterministic Miller--Rabin for the complete unsigned 64-bit range."""
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
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


def replay(certificate_path: Path, manifest_path: Path, bundle: Path) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    document = json.loads(certificate_path.read_text(encoding="utf-8"))
    if document.get("schema") != SCHEMA:
        raise ReplayError("candidate schema drift")
    if document.get("manifest_sha256") != sha256_file(manifest_path):
        raise ReplayError("candidate belongs to another manifest")
    commit = document.get("campaign_commit")
    if not isinstance(commit, str) or len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        raise ReplayError("candidate has no exact campaign commit")
    verify_bundle(manifest_path, bundle, commit)
    row = document.get("evaluation")
    construction = document.get("construction")
    if not isinstance(row, dict):
        raise ReplayError("candidate evaluation missing")
    if not isinstance(construction, dict):
        raise ReplayError("candidate construction witness missing")
    n = row.get("n")
    arm = row.get("arm")
    if not isinstance(n, int) or not BOUNDARY < n < 2**64 or arm not in ARMS:
        raise ReplayError("candidate boundary/arm invalid")
    raw_factors = row.get("factors")
    if not isinstance(raw_factors, list) or not raw_factors:
        raise ReplayError("complete factorization missing")
    factors: dict[int, int] = {}
    for item in raw_factors:
        if (not isinstance(item, list) or len(item) != 2
                or not all(isinstance(value, int) for value in item)):
            raise ReplayError("malformed factor tuple")
        p, exponent = item
        if p in factors or exponent < 1 or not prime64(p):
            raise ReplayError("factor tuple is not canonical prime data")
        factors[p] = exponent
    if list(factors) != sorted(factors) or math.prod(p**e for p, e in factors.items()) != n:
        raise ReplayError("factorization does not reconstruct n")
    phi = n
    for p in factors:
        phi -= phi // p
    composite = not (len(factors) == 1 and next(iter(factors.values())) == 1)
    carmichael = (len(factors) >= 3 and all(e == 1 for e in factors.values())
                  and all((n - 1) % (p - 1) == 0 for p in factors))
    residue = pow(2, n - 1, n) if composite and n % 2 else -1
    margin = 9 * n - 19 * phi
    expected = {
        "n": n, "arm": arm, "provenance": row.get("provenance"),
        "factors": raw_factors, "phi": phi, "margin_t": margin,
        "modular_residue": residue, "composite": composite,
        "carmichael": carmichael,
        "crossing": composite and n % 2 == 1 and residue == 1 and margin >= 0,
    }
    if row != expected or not expected["crossing"]:
        raise ReplayError("candidate arithmetic or crossing claim failed")

    a1 = parse_oeis(bundle / "snapshots/b001567.txt", manifest["oeis"]["A001567"])
    a2 = parse_oeis(bundle / "snapshots/b002997.txt", manifest["oeis"]["A002997"])
    catalogue = set([value for value in a1 if value > BOUNDARY][:int(manifest["catalogue_limit"])])
    locked = set(a1) | set(a2)
    if arm == "CATALOGUE":
        if construction != {"kind": "A001567"} or n not in catalogue or carmichael:
            raise ReplayError("candidate is outside the catalogue arm")
    elif arm == "GENERIC":
        spec = manifest["generic"]
        width = int(spec["block_width"])
        first = BOUNDARY + 1
        count = (int(spec["upper_exclusive"]) - first) // width
        base = int.from_bytes(hashlib.sha256(spec["seed"].encode("ascii")).digest(), "big") % (count - 24 + 1)
        blocks = [(first + (base + shard) * width,
                   first + (base + shard + 1) * width - 1) for shard in range(24)]
        if (construction.get("kind") != "generic_block"
                or (construction.get("start"), construction.get("end")) not in blocks
                or not construction["start"] <= n <= construction["end"]
                or n in locked or carmichael):
            raise ReplayError("candidate violates generic-arm construction/exclusions")
    else:
        if not carmichael:
            raise ReplayError("candidate is outside the Carmichael wall")
        kind = construction.get("kind")
        if kind == "A002997":
            if n not in set(a2):
                raise ReplayError("wall snapshot identity is not locked A002997")
        elif kind == "korselt_chain":
            seed = construction.get("seed")
            additions = construction.get("extension_primes")
            if (not isinstance(seed, int) or seed > BOUNDARY or seed not in set(a2)
                    or not isinstance(additions, list) or not additions
                    or len(additions) > int(manifest["wall"]["extension_depth"])
                    or not all(isinstance(q, int) for q in additions)):
                raise ReplayError("malformed Korselt chain")
            seed_factors = dict(factors)
            for q in additions:
                if seed_factors.get(q) != 1:
                    raise ReplayError("extension prime absent/noncanonical in final factors")
                del seed_factors[q]
            if math.prod(p**e for p, e in seed_factors.items()) != seed:
                raise ReplayError("Korselt seed factors do not reconstruct seed")
            parent = seed
            parent_factors = seed_factors
            factor_limit = math.isqrt(max(a1[-1], a2[-1])) + 1
            while not prime64(factor_limit):
                factor_limit -= 1
            for index, q in enumerate(additions):
                modulus = math.lcm(*(p - 1 for p in parent_factors))
                if (not prime64(q) or q in parent_factors or (parent - 1) % (q - 1)
                        or q % modulus != 1):
                    raise ReplayError("Korselt extension condition failed")
                parent *= q
                parent_factors = dict(parent_factors)
                parent_factors[q] = 1
                if not (len(parent_factors) >= 3
                        and all(e == 1 for e in parent_factors.values())
                        and all((parent - 1) % (p - 1) == 0 for p in parent_factors)):
                    raise ReplayError("Korselt chain child is not Carmichael")
                if index + 1 < len(additions) and math.isqrt(parent - 1) > factor_limit:
                    raise ReplayError("Korselt chain leaves frozen factorization envelope")
            if parent != n:
                raise ReplayError("Korselt chain does not reconstruct candidate")
        else:
            raise ReplayError("unknown wall construction witness")
    return expected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", type=Path)
    parser.add_argument("gate_bundle", type=Path)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    result = replay(args.certificate, args.manifest, args.gate_bundle)
    print(json.dumps({"verified": True, "n": result["n"], "arm": result["arm"]},
                     sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
