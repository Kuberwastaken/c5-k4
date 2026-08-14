#!/usr/bin/env python3
"""Audit the finite arithmetic data accompanying the A056777 K-theorem report.

This is deliberately not presented as a proof checker for the general theorem;
the report contains that proof.  It independently rebuilds the exact finite
PURE_PRIME_POWER tuple domain and checks useful identities on every tuple.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent


def ceil_root(value: int, exponent: int) -> int:
    low, high = 0, 1
    while high**exponent < value:
        high *= 2
    while low + 1 < high:
        middle = (low + high) // 2
        if middle**exponent < value:
            low = middle
        else:
            high = middle
    return high


def floor_root(value: int, exponent: int) -> int:
    root = ceil_root(value, exponent)
    return root if root**exponent <= value else root - 1


def prime_sieve(limit: int) -> bytearray:
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[:2] = b"\x00\x00"
    for prime in range(2, math.isqrt(limit) + 1):
        if sieve[prime]:
            start = prime * prime
            sieve[start : limit + 1 : prime] = b"\x00" * (
                (limit - start) // prime + 1
            )
    return sieve


def prime_power_values(prime: int, exponent: int) -> tuple[int, int, int]:
    n = prime**exponent
    sigma = (prime ** (exponent + 1) - 1) // (prime - 1)
    phi = (prime - 1) * prime ** (exponent - 1)
    k_value = sigma + phi - 2 * n
    expected_k = sum(prime**j for j in range(exponent - 1))
    if k_value != expected_k:
        raise ValueError("prime-power K identity failed")
    return n, phi, sigma


def main() -> int:
    certificate = json.loads((HERE / "certificate.json").read_text())
    if certificate.get("schema") != "oeis-a056777-theorem-shadow-v1":
        raise ValueError("certificate schema drift")

    lower = certificate["value_minimum"]
    upper = certificate["value_maximum"]
    grid = certificate["pure_prime_power_grid"]
    first_e = grid["exponent_minimum_computed"]
    last_e = grid["exponent_maximum_computed"]
    if first_e != 3 or last_e != 46 or 2**47 <= upper:
        raise ValueError("exponent boundary drift")

    sieve = prime_sieve(math.isqrt(upper))
    rows: list[tuple[int, int, int]] = []
    actual_counts: dict[str, int] = {}
    owners = [0] * certificate["shards"]
    for exponent in range(first_e, last_e + 1):
        low = max(2, ceil_root(lower, exponent))
        high = floor_root(upper, exponent)
        count = 0
        for prime in range(low, high + 1):
            if not sieve[prime]:
                continue
            n, _phi, _sigma = prime_power_values(prime, exponent)
            if not lower <= n <= upper:
                raise ValueError("tuple escaped the declared value band")
            owners[len(rows) % certificate["shards"]] += 1
            rows.append((exponent, prime, n))
            count += 1
        actual_counts[str(exponent)] = count

    if actual_counts != grid["counts_by_exponent"]:
        raise ValueError("per-exponent count drift")
    if len(rows) != grid["tuple_count"]:
        raise ValueError("tuple-count drift")
    stream = "".join(f"{e},{p},{n}\n" for e, p, n in rows).encode("ascii")
    if hashlib.sha256(stream).hexdigest() != grid["tuple_stream_sha256"]:
        raise ValueError("canonical tuple stream drift")
    if max(owners) - min(owners) > 1:
        raise ValueError("ordinal shard assignment is unbalanced")

    # Exhaust the elementary p^2 difference-of-squares reduction.
    factor_pairs = [
        (a, 12 // a)
        for a in range(1, math.isqrt(12) + 1)
        if 12 % a == 0 and a % 2 == (12 // a) % 2
    ]
    if factor_pairs != [(2, 6)]:
        raise ValueError("difference-of-squares factor-pair audit failed")
    p, q = (factor_pairs[0][1] - factor_pairs[0][0]) // 2, (
        factor_pairs[0][1] + factor_pairs[0][0]
    ) // 2
    if (p, q) != (2, 4):
        raise ValueError("prime-square reduction drift")

    print(
        json.dumps(
            {
                "verified": True,
                "tuple_count": len(rows),
                "tuple_stream_sha256": hashlib.sha256(stream).hexdigest(),
                "shard_minimum": min(owners),
                "shard_maximum": max(owners),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
