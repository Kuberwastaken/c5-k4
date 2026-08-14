#!/usr/bin/env python3
"""Exact finite certificate for the A231201 finite-prime lift invariant.

This script does not search for an A231201 counterexample.  It checks the
finite arithmetic hypotheses used by the accompanying mathematical proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
MANIFEST = (
    ROOT
    / "results/expansion/live-search-2026-08-14"
    / "oeis-a231201-development/manifest.json"
)
CERTIFICATE = HERE / "divisibility-certificate.json"


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "ascii"
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def order_two(q: int) -> int:
    if q == 2:
        return 1
    value = 1
    for order in range(1, q):
        value = value * 2 % q
        if value == 1:
            return order
    raise AssertionError(f"2 has no multiplicative order modulo {q}")


def build_certificate() -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="ascii"))
    primes = manifest["primes"]
    assert len(primes) == 55
    assert primes == sorted(primes) and len(set(primes)) == len(primes)

    modulus = 1
    survivor_count = 1
    rows = []
    simple_failures = []

    for q in primes:
        assert is_prime(q)
        order = order_two(q)
        if q == 2:
            # Frozen convention: 2^x is constantly 0 modulo 2 for positive x,
            # so its positive-exponent period is represented by o_2=1.
            assert order == 1
        else:
            assert order < q and (q - 1) % order == 0
            assert pow(2, order, q) == 1

        old_modulus = modulus
        simple_condition = old_modulus % order == 0
        if not simple_condition:
            simple_failures.append(q)

        gcd_old_order = math.gcd(old_modulus, order)
        exponent_fibers = order // gcd_old_order
        lift_count = q * exponent_fibers
        new_modulus = math.lcm(old_modulus, q * order)

        # q is a fresh coordinate.  In each exponent fiber, t=t0+k*d,
        # k=0,...,q-1, and d*M is invertible modulo q.  The exhaustive residue
        # check below is independent of the old-class translation r.
        assert old_modulus % q != 0
        assert new_modulus // old_modulus == lift_count
        assert math.gcd(exponent_fibers * old_modulus, q) == 1
        groups: dict[int, list[int]] = {}
        for t in range(lift_count):
            exponent_residue = (t * old_modulus) % order if order > 1 else 0
            groups.setdefault(exponent_residue, []).append(
                (t * old_modulus) % q
            )
        assert len(groups) == exponent_fibers
        assert all(len(values) == q for values in groups.values())
        assert all(sorted(values) == list(range(q)) for values in groups.values())

        survivors_per_old_class = exponent_fibers * (q - 1)
        survivor_count *= survivors_per_old_class
        rows.append(
            {
                "prime": q,
                "order_two": order,
                "old_modulus": str(old_modulus),
                "gcd_old_modulus_order": gcd_old_order,
                "exponent_fibers": exponent_fibers,
                "lifts_per_old_class": lift_count,
                "survivors_per_old_class_for_every_assigned_residue": survivors_per_old_class,
                "simple_order_divides_old_modulus": simple_condition,
                "new_modulus": str(new_modulus),
            }
        )
        modulus = new_modulus

    assert str(modulus) == manifest["combined_period"]
    return {
        "schema": "c5-k4.a231201-periodic-lift-certificate.v1",
        "scope": "exact frozen 55-prime universe; no target candidate search",
        "source_manifest": str(MANIFEST.relative_to(ROOT)),
        "source_manifest_sha256": sha256(MANIFEST),
        "prime_count": len(primes),
        "first_prime": primes[0],
        "last_prime": primes[-1],
        "combined_period": str(modulus),
        "surviving_residue_classes_for_every_assignment": str(survivor_count),
        "proposed_simple_condition_holds": not simple_failures,
        "proposed_simple_condition_failures": simple_failures,
        "rows": rows,
    }


def verify_certificate(certificate: dict) -> None:
    expected = build_certificate()
    assert certificate == expected, "certificate does not match exact recomputation"

    # Exercise the deterministic least-lift construction on fixed all-zero and
    # affine assignments.  These are implementation checks, not the universal
    # proof, which is the lift-count argument in result.md.
    for mode in ("zero", "affine"):
        residue = 0
        modulus = 1
        assignments: dict[int, int] = {}
        for row in expected["rows"]:
            q = row["prime"]
            order = row["order_two"]
            new_modulus = int(row["new_modulus"])
            lifts = row["lifts_per_old_class"]
            assigned = 0 if mode == "zero" else (17 * q + 11) % q
            assignments[q] = assigned
            for t in range(lifts):
                candidate = residue + t * modulus
                candidate_residue = candidate % new_modulus
                positive_candidate = (
                    candidate_residue if candidate_residue > 0 else new_modulus
                )
                if (
                    positive_candidate - pow(2, positive_candidate, q)
                ) % q != assigned:
                    residue = candidate_residue
                    modulus = new_modulus
                    break
            else:
                raise AssertionError(f"no surviving lift at q={q}")
        positive = residue if residue > 0 else modulus
        assert positive > 0
        assert all(
            (positive - pow(2, positive, q)) % q != assigned
            for q, assigned in assignments.items()
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    expected = build_certificate()
    if args.write:
        CERTIFICATE.write_bytes(canonical(expected))
    certificate = json.loads(CERTIFICATE.read_text(encoding="ascii"))
    verify_certificate(certificate)
    print(
        "A231201 periodic-lift certificate verified: "
        f"{certificate['prime_count']} primes; "
        f"simple-condition failures={certificate['proposed_simple_condition_failures']}; "
        "every assignment leaves positive periodic escape classes"
    )


if __name__ == "__main__":
    main()
