#!/usr/bin/env python3
"""Independent multiplication-table verifier for Graffiti³ Conjecture 23."""

from __future__ import annotations

import argparse
from array import array
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


CERTIFICATE_SCHEMA = "c5k4-graffiti3-conjecture23-certificate-1.0"


class VerificationError(ValueError):
    pass


def prime_power(n: int) -> tuple[bool, int | None]:
    if n < 2:
        return False, None
    divisor = next((p for p in range(2, n + 1) if n % p == 0), None)
    assert divisor is not None
    for q in range(2, divisor):
        if divisor % q == 0:
            raise VerificationError("least divisor was not prime")
    remaining = n
    while remaining % divisor == 0:
        remaining //= divisor
    return remaining == 1, divisor


def validate_table_shape(raw: Any) -> list[list[int]]:
    if not isinstance(raw, list) or not raw:
        raise VerificationError("multiplication table absent")
    n = len(raw)
    table: list[list[int]] = []
    expected = set(range(n))
    for raw_row in raw:
        if not isinstance(raw_row, list) or len(raw_row) != n:
            raise VerificationError("multiplication table is not square")
        row = [int(value) for value in raw_row]
        if set(row) != expected:
            raise VerificationError("left translation is not a permutation")
        table.append(row)
    return table


def find_identity_and_inverses(table: Sequence[Sequence[int]]) -> tuple[int, list[int]]:
    n = len(table)
    identity_rows = [e for e in range(n) if all(table[e][a] == a and table[a][e] == a for a in range(n))]
    if len(identity_rows) != 1:
        raise VerificationError("table has no unique two-sided identity")
    identity = identity_rows[0]
    inverses: list[int] = []
    for a in range(n):
        candidates = [b for b in range(n) if table[a][b] == identity and table[b][a] == identity]
        if len(candidates) != 1:
            raise VerificationError("element has no unique two-sided inverse")
        inverses.append(candidates[0])
    return identity, inverses


def exact_associativity(table: Sequence[Sequence[int]]) -> None:
    """Check L_a L_b = L_(ab) for every a,b, using compact uint arrays."""
    n = len(table)
    code = "H" if n <= 65535 else "I"
    packed = [array(code, row) for row in table]
    for a, left in enumerate(packed):
        for b, right in enumerate(packed):
            target = packed[left[b]]
            composed = array(code, (left[right[x]] for x in range(n)))
            if composed != target:
                raise VerificationError(f"associativity fails at left translations {a},{b}")


def cocycle(dimension: int, outputs: Sequence[int], left_v: int, right_v: int) -> int:
    value = 0
    for pair, mask in enumerate(outputs):
        if ((left_v >> (2 * pair)) & 1) and ((right_v >> (2 * pair + 1)) & 1):
            value ^= mask
    return value


def verify_wall_table_symbolically(table: Sequence[Sequence[int]], descriptor: Mapping[str, Any]) -> None:
    dimension = int(descriptor.get("dimension", -1))
    outputs = tuple(int(x) for x in descriptor.get("pair_outputs", []))
    if dimension not in {6, 8} or len(outputs) != dimension // 2 or any(x not in {1, 2, 3} for x in outputs):
        raise VerificationError("wall descriptor outside frozen construction")
    n = 1 << (dimension + 2)
    if len(table) != n:
        raise VerificationError("wall table order mismatch")
    # The displayed f is bilinear, so f(x,y)+f(x+y,z)=f(y,z)+f(x,y+z).
    # Check its coefficients on the complete basis-pair domain, then compare
    # every table entry with the resulting associative central extension.
    for i in range(dimension):
        for j in range(dimension):
            for k in range(dimension):
                x, y, z = 1 << i, 1 << j, 1 << k
                if cocycle(dimension, outputs, x, y) ^ cocycle(dimension, outputs, x ^ y, z) != cocycle(dimension, outputs, y, z) ^ cocycle(dimension, outputs, x, y ^ z):
                    raise VerificationError("basis cocycle identity failed")
    for left in range(n):
        lv, lz = left >> 2, left & 3
        for right in range(n):
            rv, rz = right >> 2, right & 3
            expected = ((lv ^ rv) << 2) | (lz ^ rz ^ cocycle(dimension, outputs, lv, rv))
            if table[left][right] != expected:
                raise VerificationError("wall table differs from certified cocycle law")


def subgroup_generated(table: Sequence[Sequence[int]], identity: int, generators: set[int]) -> set[int]:
    subgroup = {identity, *generators}
    changed = True
    while changed:
        changed = False
        current = tuple(subgroup)
        for a in current:
            for b in current:
                value = table[a][b]
                if value not in subgroup:
                    subgroup.add(value)
                    changed = True
    return subgroup


def exact_invariants(table: Sequence[Sequence[int]], identity: int, inverses: Sequence[int]) -> dict[str, int]:
    n = len(table)
    center = [a for a in range(n) if all(table[a][b] == table[b][a] for b in range(n))]
    commutators: set[int] = set()
    for a in range(n):
        ia = inverses[a]
        for b in range(n):
            ib = inverses[b]
            commutators.add(table[table[table[ia][ib]][a]][b])
    derived = subgroup_generated(table, identity, commutators)

    unseen = set(range(n))
    classes = 0
    while unseen:
        a = min(unseen)
        conjugates = {table[table[b][a]][inverses[b]] for b in range(n)}
        if not conjugates <= unseen:
            # A previously completed orbit cannot overlap a new group-action orbit.
            raise VerificationError("conjugacy orbits overlap")
        unseen.difference_update(conjugates)
        classes += 1
    if n % len(derived):
        raise VerificationError("derived subgroup order does not divide group order")
    return {
        "order": n,
        "derived_order": len(derived),
        "abelianization_order": n // len(derived),
        "center_order": len(center),
        "conjugacy_classes": classes,
        "residual_w": 2 * (n // len(derived)) + n + 2 * len(center) - 4 * classes,
    }


def verify_document(document: Mapping[str, Any]) -> dict[str, Any]:
    if document.get("schema") != CERTIFICATE_SCHEMA:
        raise VerificationError("certificate schema mismatch")
    profile = document.get("profile")
    if not isinstance(profile, dict):
        raise VerificationError("profile absent")
    table = validate_table_shape(document.get("multiplication_table"))
    premise, prime = prime_power(len(table))
    if not premise:
        raise VerificationError("table order is not a prime power")
    identity, inverses = find_identity_and_inverses(table)
    descriptor = profile.get("wall_descriptor")
    if isinstance(descriptor, dict):
        verify_wall_table_symbolically(table, descriptor)
    else:
        exact_associativity(table)
    exact = exact_invariants(table, identity, inverses)
    for key, value in exact.items():
        if int(profile.get(key, -1)) != value:
            raise VerificationError(f"profile mismatch: {key}")
    if exact["residual_w"] >= 0:
        raise VerificationError("certificate does not strictly refute Conjecture 23")
    return {"verified": True, "prime": prime, "identity": identity, **exact}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", type=Path)
    args = parser.parse_args()
    document = json.loads(args.certificate.read_text(encoding="utf-8"))
    print(json.dumps(verify_document(document), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
