#!/usr/bin/env python3
"""Select the Method v1.1 C1 question clusters from frozen public entropy.

The sampler deliberately knows nothing about conjecture statements.  It
uniformly shuffles eligible cluster identities independently inside each fixed
stratum, then takes the fixed quota.  It never backfills between strata.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Callable


SCHEMA_VERSION = "c5k4-benchmark-selection-1.1"
POOL_SCHEMA_VERSION = "c5k4-eligible-cluster-pool-1.1"
DOMAIN = b"c5-k4/method-v1.1/C1\x00"
STRATA = (
    "GRAPH_SCALAR_INEQUALITY",
    "GRAPH_STRUCTURAL_PROPERTY",
    "FINITE_ALGEBRA_EQUATIONAL",
    "AUTOMATA_GAME_PROCESS",
    "FINITE_COMBINATORIAL",
)
QUOTAS = {
    "GRAPH_SCALAR_INEQUALITY": 3,
    "GRAPH_STRUCTURAL_PROPERTY": 3,
    "FINITE_ALGEBRA_EQUATIONAL": 2,
    "AUTOMATA_GAME_PROCESS": 2,
    "FINITE_COMBINATORIAL": 2,
}


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def shuffle_rows(
    rows: list[dict[str, Any]],
    seed: bytes,
    stratum_index: int,
    block_digest: Callable[[bytes], bytes] = lambda payload: hashlib.sha256(payload).digest(),
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Unbiased Fisher--Yates using rejection-sampled SHA-256 u64 words."""

    shuffled = sorted(
        rows,
        key=lambda row: (
            row["identity_sha256"].lower(), row["cluster_id"].encode("utf-8")
        ),
    )
    counter = 0
    words: list[int] = []
    words_consumed = 0
    rejected_words = 0

    def next_word() -> int:
        nonlocal counter, words_consumed
        if not words:
            block = block_digest(
                DOMAIN + seed + stratum_index.to_bytes(4, "big") + counter.to_bytes(8, "big")
            )
            if len(block) != 32:
                raise ValueError("block digest must return exactly 32 bytes")
            counter += 1
            words.extend(int.from_bytes(block[i : i + 8], "big") for i in range(0, 32, 8))
        words_consumed += 1
        return words.pop(0)

    for index in range(len(shuffled) - 1, 0, -1):
        modulus = index + 1
        limit = ((1 << 64) // modulus) * modulus
        while True:
            word = next_word()
            if word < limit:
                break
            rejected_words += 1
        position = word % modulus
        shuffled[index], shuffled[position] = shuffled[position], shuffled[index]
    return shuffled, {
        "sha256_blocks_consumed": counter,
        "u64_words_consumed": words_consumed,
        "u64_words_rejected": rejected_words,
    }


def validate_pool(pool: Any) -> list[dict[str, Any]]:
    if not isinstance(pool, dict):
        raise ValueError("pool must be a JSON object")
    if pool.get("schema_version") != POOL_SCHEMA_VERSION:
        raise ValueError(f"pool schema_version must be {POOL_SCHEMA_VERSION!r}")
    upstream = pool.get("upstream")
    if not isinstance(upstream, dict) or set(upstream) != {"commit", "tree"}:
        raise ValueError("pool.upstream must contain exactly commit and tree")
    for key in ("commit", "tree"):
        value = upstream[key]
        if not isinstance(value, str) or len(value) not in (40, 64):
            raise ValueError(f"pool.upstream.{key} must be a 40- or 64-hex OID")
        try:
            bytes.fromhex(value)
        except ValueError as exc:
            raise ValueError(f"pool.upstream.{key} is not hexadecimal") from exc
    contamination = pool.get("contamination")
    expected_contamination_keys = {
        "applied", "inventory_sha256", "identity_ambiguity_means_exclusion"
    }
    if not isinstance(contamination, dict) or set(contamination) != expected_contamination_keys:
        raise ValueError(
            "pool.contamination must contain exactly applied, inventory_sha256, "
            "and identity_ambiguity_means_exclusion"
        )
    if contamination["applied"] is not True:
        raise ValueError("pool.contamination.applied must be true")
    if contamination["identity_ambiguity_means_exclusion"] is not True:
        raise ValueError("pool contamination must fail closed on identity ambiguity")
    inventory_sha = contamination["inventory_sha256"]
    if not isinstance(inventory_sha, str) or len(inventory_sha) != 64:
        raise ValueError("pool.contamination.inventory_sha256 must be 64 hex characters")
    try:
        bytes.fromhex(inventory_sha)
    except ValueError as exc:
        raise ValueError("pool.contamination.inventory_sha256 is not hexadecimal") from exc

    clusters = pool.get("clusters")
    if not isinstance(clusters, list):
        raise ValueError("pool.clusters must be an array")
    ids: set[str] = set()
    identities: set[str] = set()
    for index, row in enumerate(clusters):
        where = f"pool.clusters[{index}]"
        if not isinstance(row, dict):
            raise ValueError(f"{where} must be an object")
        required = {"cluster_id", "identity_sha256", "stratum", "eligible"}
        missing = required - set(row)
        if missing:
            raise ValueError(f"{where} is missing {sorted(missing)}")
        cluster_id = row["cluster_id"]
        identity = row["identity_sha256"]
        if not isinstance(cluster_id, str) or not cluster_id:
            raise ValueError(f"{where}.cluster_id must be a nonempty string")
        if cluster_id in ids:
            raise ValueError(f"duplicate cluster_id: {cluster_id}")
        ids.add(cluster_id)
        if not isinstance(identity, str) or len(identity) != 64:
            raise ValueError(f"{where}.identity_sha256 must be 64 hex characters")
        try:
            bytes.fromhex(identity)
        except ValueError as exc:
            raise ValueError(f"{where}.identity_sha256 is not hexadecimal") from exc
        identity = identity.lower()
        if identity in identities:
            raise ValueError(f"duplicate identity_sha256: {identity}")
        identities.add(identity)
        if type(row["eligible"]) is not bool:
            raise ValueError(f"{where}.eligible must be a JSON boolean")
        if row["eligible"] and row["stratum"] not in STRATA:
            raise ValueError(f"{where}.stratum is not a frozen Method v1.1 stratum")
        if not row["eligible"] and row["stratum"] is not None and row["stratum"] not in STRATA:
            raise ValueError(f"{where}.stratum must be null or a frozen Method v1.1 stratum")
    return clusters


def select(pool_bytes: bytes, randomness: str) -> dict[str, Any]:
    if len(randomness) != 64 or randomness.lower() != randomness:
        raise ValueError("randomness must be exactly 64 lowercase hexadecimal characters")
    try:
        seed = bytes.fromhex(randomness)
    except ValueError as exc:
        raise ValueError("randomness must be exactly 64 lowercase hexadecimal characters") from exc
    try:
        pool = json.loads(pool_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"pool is not valid UTF-8 JSON: {exc}") from exc
    clusters = validate_pool(pool)

    strata_evidence: list[dict[str, Any]] = []
    selected: list[dict[str, str]] = []
    shortage = False
    for stratum_index, stratum in enumerate(STRATA):
        quota = QUOTAS[stratum]
        eligible = [
            row for row in clusters if row["eligible"] and row["stratum"] == stratum
        ]
        candidates = [
            {
                "cluster_id": row["cluster_id"],
                "identity_sha256": row["identity_sha256"].lower(),
            }
            for row in eligible
        ]
        shuffled, consumption = shuffle_rows(candidates, seed, stratum_index)
        enough = len(shuffled) >= quota
        shortage |= not enough
        for index, row in enumerate(shuffled, start=1):
            row["shuffle_position"] = index
            row["selected"] = enough and index <= quota
        if enough:
            selected.extend(
                {
                    "cluster_id": row["cluster_id"],
                    "identity_sha256": row["identity_sha256"],
                    "stratum": stratum,
                    "shuffle_position": row["shuffle_position"],
                }
                for row in shuffled[:quota]
            )
        strata_evidence.append(
            {
                "stratum": stratum,
                "quota": quota,
                "eligible_count": len(shuffled),
                "quota_satisfied": enough,
                "entropy_consumption": consumption,
                "shuffled": shuffled,
            }
        )

    # No partial selection is emitted when any fixed stratum is short.  This
    # prevents downstream code from silently treating an incomplete C1 as a
    # usable benchmark or inventing a backfill policy.
    status = "NO_ELIGIBLE_BENCHMARK" if shortage else "SELECTED"
    if shortage:
        selected = []
    result = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "algorithm": {
            "name": "UNBIASED_DOMAIN_SEPARATED_SHA256_FISHER_YATES",
            "domain_hex": DOMAIN.hex(),
            "seed": "LOWERCASE_HEX_DECODED_32_BYTES",
            "initial_order": "identity_sha256_lower_ascending_then_cluster_id_utf8_bytes_ascending",
            "block": "SHA256(domain || seed || uint32_be(stratum_index) || uint64_be(counter))",
            "shuffle": "FULL_DESCENDING_FISHER_YATES",
            "bounded_integer": "U64_BIG_ENDIAN_REJECTION_BELOW_FLOOR_2^64_OVER_M_TIMES_M",
            "within_stratum_only": True,
            "no_backfill": True,
        },
        "pool": {
            "file_sha256": sha256(pool_bytes),
            "canonical_sha256": sha256(canonical_json(pool)),
            "schema_version": pool["schema_version"],
            "upstream": pool["upstream"],
            "contamination": pool["contamination"],
            "cluster_count": len(clusters),
            "eligible_cluster_count": sum(bool(row["eligible"]) for row in clusters),
        },
        "randomness": {
            "encoding": "UTF-8_EXACT_NO_NORMALIZATION",
            "value": randomness,
            "value_sha256": sha256(randomness.encode("ascii")),
        },
        "quotas": dict(QUOTAS),
        "strata": strata_evidence,
        "selected_clusters": selected,
    }
    result["evidence_sha256"] = sha256(canonical_json(result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pool", type=Path, required=True)
    parser.add_argument(
        "--randomness",
        required=True,
        help="exact verified public-randomness value as 64 lowercase hexadecimal characters",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = select(args.pool.read_bytes(), args.randomness)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    encoded = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        sys.stdout.write(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
