#!/usr/bin/env python3
"""Replay the Method v1.2 feasibility gate and select C1 from verified entropy.

This executable is deliberately offline.  It does not fetch randomness and it
does not inspect conjecture statements.  It accepts only content-addressed
machine artifacts, proves that the frozen 3/3/2/2/2 gate passed, proves that a
verified beacon matches a future round frozen at C0, and only then shuffles
opaque cluster identities.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Callable, Mapping


SCHEMA_VERSION = "c5k4-benchmark-selection-1.2"
POOL_SCHEMA_VERSION = "c5k4-eligible-cluster-pool-1.2"
FEASIBILITY_SCHEMA_VERSION = "c5k4-quota-feasibility-1.2"
C0_SCHEMA_VERSION = "c5k4-c0-randomness-contract-1.2"
RANDOMNESS_SCHEMA_VERSION = "c5k4-drand-randomness-artifact-1"
DRAND_CHAIN_HASH = "8990e7a9aaed2ffed73dbd7092123d6f289930540d7651336225dc172e51b2ce"
DOMAIN = b"c5-k4/method-v1.2/C1\x00"
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
ARTIFACT_KEYS = (
    "open_inventory",
    "classifier",
    "provenance_policy",
    "provenance_inventory",
    "contamination_inventory",
    "source_snapshots",
)


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def object_digest(value: Mapping[str, Any], digest_key: str) -> str:
    """Digest a self-identifying object with its digest member omitted."""

    return sha256(canonical_json({key: item for key, item in value.items() if key != digest_key}))


def _load_object(raw: bytes, where: str) -> dict[str, Any]:
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{where} is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{where} must be a JSON object")
    return value


def _hex(value: Any, length: int, where: str) -> str:
    if not isinstance(value, str) or len(value) != length or value.lower() != value:
        raise ValueError(f"{where} must be exactly {length} lowercase hexadecimal characters")
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise ValueError(
            f"{where} must be exactly {length} lowercase hexadecimal characters"
        ) from exc
    return value


def _timestamp(value: Any, where: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"{where} must be an RFC 3339 UTC timestamp ending in Z")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError(f"{where} is not a valid timestamp") from exc
    return parsed


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
            row["identity_sha256"].lower(),
            row["cluster_id"].encode("utf-8"),
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
                DOMAIN
                + seed
                + stratum_index.to_bytes(4, "big")
                + counter.to_bytes(8, "big")
            )
            if len(block) != 32:
                raise ValueError("block digest must return exactly 32 bytes")
            counter += 1
            words.extend(
                int.from_bytes(block[index : index + 8], "big")
                for index in range(0, 32, 8)
            )
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


def validate_pool(pool: dict[str, Any]) -> list[dict[str, Any]]:
    if pool.get("schema_version") != POOL_SCHEMA_VERSION:
        raise ValueError(f"pool.schema_version must be {POOL_SCHEMA_VERSION!r}")
    if pool.get("artifact_status") != "CONTAMINATION_APPLIED":
        raise ValueError("pool.artifact_status must be CONTAMINATION_APPLIED")
    upstream = pool.get("upstream")
    if not isinstance(upstream, dict):
        raise ValueError("pool.upstream must be an object")
    if upstream.get("repository") != "google-deepmind/formal-conjectures":
        raise ValueError("pool.upstream.repository is not the frozen registry")
    for key in ("commit", "tree"):
        _hex(upstream.get(key), 40, f"pool.upstream.{key}")
    digests = pool.get("digests")
    if not isinstance(digests, dict) or set(digests) != {
        f"{key}_sha256" for key in ARTIFACT_KEYS
    }:
        raise ValueError("pool.digests must contain exactly the six frozen artifact hashes")
    for key in ARTIFACT_KEYS:
        _hex(digests[f"{key}_sha256"], 64, f"pool.digests.{key}_sha256")

    clusters = pool.get("clusters")
    if not isinstance(clusters, list):
        raise ValueError("pool.clusters must be an array")
    ids: set[str] = set()
    identities: set[str] = set()
    for index, row in enumerate(clusters):
        where = f"pool.clusters[{index}]"
        if not isinstance(row, dict):
            raise ValueError(f"{where} must be an object")
        missing = {"cluster_id", "identity_sha256", "stratum", "eligible"} - set(row)
        if missing:
            raise ValueError(f"{where} is missing {sorted(missing)}")
        cluster_id = row["cluster_id"]
        if not isinstance(cluster_id, str) or not cluster_id:
            raise ValueError(f"{where}.cluster_id must be a nonempty string")
        if cluster_id in ids:
            raise ValueError(f"duplicate cluster_id: {cluster_id}")
        ids.add(cluster_id)
        identity = _hex(row["identity_sha256"], 64, f"{where}.identity_sha256")
        if identity in identities:
            raise ValueError(f"duplicate identity_sha256: {identity}")
        identities.add(identity)
        if type(row["eligible"]) is not bool:
            raise ValueError(f"{where}.eligible must be a JSON boolean")
        if row["eligible"] and row["stratum"] not in STRATA:
            raise ValueError(f"{where}.stratum is not a frozen Method v1.2 stratum")
        if not row["eligible"] and row["stratum"] is not None and row["stratum"] not in STRATA:
            raise ValueError(f"{where}.stratum must be null or a frozen Method v1.2 stratum")
    return clusters


def replay_feasibility(
    pool: dict[str, Any],
    pool_bytes: bytes,
    clusters: list[dict[str, Any]],
    certificate: dict[str, Any],
    artifact_bytes: Mapping[str, bytes],
) -> None:
    """Fail closed unless the frozen PASS certificate replays exactly."""

    if certificate.get("schema_version") != FEASIBILITY_SCHEMA_VERSION:
        raise ValueError(
            f"quota_feasibility.schema_version must be {FEASIBILITY_SCHEMA_VERSION!r}"
        )
    # Check the terminal branch before accepting or inspecting entropy.
    if certificate.get("status") != "PASS":
        raise ValueError("quota-feasibility certificate is not PASS; PRE_C0 failure is terminal")
    if certificate.get("phase") != "PRE_C0_FEASIBILITY":
        raise ValueError("quota-feasibility certificate phase must be PRE_C0_FEASIBILITY")
    if certificate.get("entropy_used") is not False:
        raise ValueError("quota-feasibility certificate entropy_used must be false")
    if certificate.get("selected_clusters") != []:
        raise ValueError("quota-feasibility certificate selected_clusters must be empty")
    if certificate.get("upstream") != pool["upstream"]:
        raise ValueError("quota-feasibility upstream does not match pool")
    if certificate.get("quotas") != QUOTAS:
        raise ValueError("quota-feasibility quotas do not match frozen 3/3/2/2/2 quotas")
    chronology = certificate.get("chronology")
    expected_chronology = {
        "p0_artifact_commit",
        "p0_attestation_commit",
        "p0_published_at_utc",
        "s0_acquired_at_utc",
        "feasibility_checked_at_utc",
    }
    if not isinstance(chronology, dict) or set(chronology) != expected_chronology:
        raise ValueError("quota-feasibility chronology must contain exactly P0/S0/gate fields")
    for key in ("p0_artifact_commit", "p0_attestation_commit"):
        _hex(chronology[key], 40, f"quota_feasibility.chronology.{key}")
    if chronology["p0_artifact_commit"] == chronology["p0_attestation_commit"]:
        raise ValueError("P0A and P0T commit identities must be distinct")
    p0_published = _timestamp(
        chronology["p0_published_at_utc"],
        "quota_feasibility.chronology.p0_published_at_utc",
    )
    s0_acquired = _timestamp(
        chronology["s0_acquired_at_utc"],
        "quota_feasibility.chronology.s0_acquired_at_utc",
    )
    feasibility_checked = _timestamp(
        chronology["feasibility_checked_at_utc"],
        "quota_feasibility.chronology.feasibility_checked_at_utc",
    )
    if not p0_published < s0_acquired <= feasibility_checked:
        raise ValueError("quota-feasibility chronology must satisfy P0T publication < S0 <= gate")

    supplied_digest = _hex(
        certificate.get("certificate_sha256"), 64, "quota_feasibility.certificate_sha256"
    )
    if supplied_digest != object_digest(certificate, "certificate_sha256"):
        raise ValueError("quota-feasibility certificate_sha256 does not replay")

    digests = certificate.get("digests")
    expected_keys = {
        "eligible_pool_file_sha256",
        "eligible_pool_canonical_sha256",
        *(f"{key}_sha256" for key in ARTIFACT_KEYS),
    }
    if not isinstance(digests, dict) or set(digests) != expected_keys:
        raise ValueError("quota-feasibility digests are incomplete or contain unknown keys")
    expected = {
        "eligible_pool_file_sha256": sha256(pool_bytes),
        "eligible_pool_canonical_sha256": sha256(canonical_json(pool)),
    }
    if set(artifact_bytes) != set(ARTIFACT_KEYS):
        raise ValueError("exactly six frozen artifact byte streams are required")
    for key in ARTIFACT_KEYS:
        _load_object(artifact_bytes[key], key)
        expected[f"{key}_sha256"] = sha256(artifact_bytes[key])
        if pool["digests"][f"{key}_sha256"] != expected[f"{key}_sha256"]:
            raise ValueError(f"pool {key} digest does not match supplied artifact")
    if digests != expected:
        raise ValueError("quota-feasibility digests do not match pool and frozen artifacts")

    strata = certificate.get("strata")
    if not isinstance(strata, list) or len(strata) != len(STRATA):
        raise ValueError("quota-feasibility strata must contain exactly five rows")
    replayed = []
    for stratum in STRATA:
        count = sum(
            row["eligible"] and row["stratum"] == stratum for row in clusters
        )
        quota = QUOTAS[stratum]
        replayed.append(
            {
                "stratum": stratum,
                "quota": quota,
                "eligible_count": count,
                "deficit": max(0, quota - count),
            }
        )
    if strata != replayed:
        raise ValueError("quota-feasibility counts or deficits do not replay from pool rows")
    if any(row["deficit"] for row in replayed):
        raise ValueError("quota-feasibility PASS is false: at least one stratum has a deficit")


def validate_future_entropy(
    pool_bytes: bytes,
    certificate: dict[str, Any],
    c0_bytes: bytes,
    randomness_bytes: bytes,
) -> tuple[dict[str, Any], dict[str, Any], bytes]:
    c0 = _load_object(c0_bytes, "C0 randomness contract")
    if c0.get("schema_version") != C0_SCHEMA_VERSION:
        raise ValueError(f"C0 schema_version must be {C0_SCHEMA_VERSION!r}")
    if c0.get("phase") != "C0_FROZEN":
        raise ValueError("C0 phase must be C0_FROZEN")
    chronology = c0.get("chronology")
    expected_chronology = {
        "p0_artifact_commit",
        "p0_attestation_commit",
        "p0_published_at_utc",
        "s0_acquired_at_utc",
        "c0_artifact_commit",
        "c0_attestation_commit",
        "c0_published_at_utc",
    }
    if not isinstance(chronology, dict) or set(chronology) != expected_chronology:
        raise ValueError("C0 chronology must contain exactly the P0/S0/C0 freeze fields")
    for key in (
        "p0_artifact_commit",
        "p0_attestation_commit",
        "c0_artifact_commit",
        "c0_attestation_commit",
    ):
        _hex(chronology[key], 40, f"C0 chronology.{key}")
    if len({chronology[key] for key in (
        "p0_artifact_commit", "p0_attestation_commit",
        "c0_artifact_commit", "c0_attestation_commit",
    )}) != 4:
        raise ValueError("P0A/P0T/C0A/C0T commit identities must be distinct")
    p0_published = _timestamp(
        chronology["p0_published_at_utc"], "C0 chronology.p0_published_at_utc"
    )
    s0_acquired = _timestamp(
        chronology["s0_acquired_at_utc"], "C0 chronology.s0_acquired_at_utc"
    )
    c0_published = _timestamp(
        chronology["c0_published_at_utc"], "C0 chronology.c0_published_at_utc"
    )
    if not p0_published < s0_acquired < c0_published:
        raise ValueError("C0 chronology must satisfy P0T publication < S0 < C0T publication")
    feasibility_chronology = certificate["chronology"]
    for key in (
        "p0_artifact_commit",
        "p0_attestation_commit",
        "p0_published_at_utc",
        "s0_acquired_at_utc",
    ):
        if chronology[key] != feasibility_chronology[key]:
            raise ValueError(f"C0 chronology.{key} does not match passing feasibility certificate")
    feasibility_checked = _timestamp(
        feasibility_chronology["feasibility_checked_at_utc"],
        "quota_feasibility.chronology.feasibility_checked_at_utc",
    )
    if feasibility_checked >= c0_published:
        raise ValueError("passing quota-feasibility gate must precede C0 publication")
    if c0.get("pool_file_sha256") != sha256(pool_bytes):
        raise ValueError("C0 pool digest does not match supplied pool")
    if c0.get("quota_feasibility_sha256") != certificate["certificate_sha256"]:
        raise ValueError("C0 quota-feasibility digest does not match passing certificate")
    contract = c0.get("randomness")
    if not isinstance(contract, dict):
        raise ValueError("C0 randomness must be an object")
    if set(contract) != {"source", "chain_hash", "round", "round_closes_at_utc", "value"}:
        raise ValueError("C0 randomness contract has missing or unknown fields")
    if contract["source"] != "League of Entropy drand":
        raise ValueError("C0 randomness source must be League of Entropy drand")
    if contract["chain_hash"] != DRAND_CHAIN_HASH:
        raise ValueError("C0 randomness.chain_hash must be the frozen legacy mainnet chain")
    if type(contract["round"]) is not int or contract["round"] < 1:
        raise ValueError("C0 randomness.round must be a positive integer")
    if contract["value"] is not None:
        raise ValueError("C0 randomness.value must be null before unlock")
    if c0.get("published_at_utc") != chronology["c0_published_at_utc"]:
        raise ValueError("C0 top-level publication time must match chronology")
    published = c0_published
    closes = _timestamp(contract["round_closes_at_utc"], "C0 round_closes_at_utc")
    if closes <= published:
        raise ValueError("randomness round is not future relative to C0 publication")

    randomness = _load_object(randomness_bytes, "verified randomness artifact")
    if randomness.get("schema_version") != RANDOMNESS_SCHEMA_VERSION:
        raise ValueError(
            f"randomness schema_version must be {RANDOMNESS_SCHEMA_VERSION!r}"
        )
    if randomness.get("round") != contract["round"]:
        raise ValueError("verified randomness round does not match C0")
    if randomness.get("round_closes_at_utc") != contract["round_closes_at_utc"]:
        raise ValueError("verified randomness close time does not match C0")
    chain = randomness.get("chain")
    if not isinstance(chain, dict) or chain.get("hash") != contract["chain_hash"]:
        raise ValueError("verified randomness chain does not match C0")
    retrieval = randomness.get("retrieval")
    if not isinstance(retrieval, dict):
        raise ValueError("verified randomness retrieval must be an object")
    retrieved = _timestamp(retrieval.get("retrieved_at_utc"), "randomness retrieved_at_utc")
    if retrieved < closes:
        raise ValueError("randomness was retrieved before the frozen round closed")
    verification = randomness.get("verification")
    required = (
        "exact_round",
        "official_relay_equality",
        "frozen_chain_info",
        "bls_signature",
        "randomness_equals_sha256_signature",
    )
    if not isinstance(verification, dict) or any(
        verification.get(key) is not True for key in required
    ):
        raise ValueError("randomness artifact does not record all required verification passes")
    value = _hex(randomness.get("randomness"), 64, "randomness")
    if randomness.get("randomness_sha256") != sha256(value.encode("ascii")):
        raise ValueError("randomness_sha256 does not match the encoded randomness")
    beacon = randomness.get("beacon")
    if not isinstance(beacon, dict) or beacon.get("round") != contract["round"]:
        raise ValueError("verified beacon round does not match C0")
    if beacon.get("randomness") != value:
        raise ValueError("verified beacon randomness does not match artifact randomness")
    signature = _hex(beacon.get("signature"), 192, "beacon.signature")
    if sha256(bytes.fromhex(signature)) != value:
        raise ValueError("beacon randomness is not SHA256(signature)")
    return c0, randomness, bytes.fromhex(value)


def select(
    pool_bytes: bytes,
    feasibility_bytes: bytes,
    artifact_bytes: Mapping[str, bytes],
    c0_bytes: bytes,
    randomness_bytes: bytes,
) -> dict[str, Any]:
    """Return full replay evidence after every pre-entropy check succeeds."""

    pool = _load_object(pool_bytes, "pool")
    clusters = validate_pool(pool)
    certificate = _load_object(feasibility_bytes, "quota-feasibility certificate")
    replay_feasibility(pool, pool_bytes, clusters, certificate, artifact_bytes)

    # No identity is ranked and shuffle_rows is never called before this full
    # verified-future-entropy gate returns successfully.
    c0, randomness, seed = validate_future_entropy(
        pool_bytes, certificate, c0_bytes, randomness_bytes
    )

    strata_evidence: list[dict[str, Any]] = []
    selected: list[dict[str, Any]] = []
    for stratum_index, stratum in enumerate(STRATA):
        candidates = [
            {
                "cluster_id": row["cluster_id"],
                "identity_sha256": row["identity_sha256"],
            }
            for row in clusters
            if row["eligible"] and row["stratum"] == stratum
        ]
        shuffled, consumption = shuffle_rows(candidates, seed, stratum_index)
        quota = QUOTAS[stratum]
        for position, row in enumerate(shuffled, start=1):
            row["shuffle_position"] = position
            row["selected"] = position <= quota
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
                "entropy_consumption": consumption,
                "shuffled": shuffled,
            }
        )

    if len(selected) != 12 or len({row["cluster_id"] for row in selected}) != 12:
        raise AssertionError("replayed PASS gate did not produce twelve unique selections")
    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "SELECTED",
        "algorithm": {
            "name": "UNBIASED_DOMAIN_SEPARATED_SHA256_FISHER_YATES",
            "domain_hex": DOMAIN.hex(),
            "seed": "VERIFIED_DRAND_RANDOMNESS_LOWERCASE_HEX_DECODED_32_BYTES",
            "initial_order": "identity_sha256_lower_ascending_then_cluster_id_utf8_bytes_ascending",
            "block": "SHA256(domain || seed || uint32_be(stratum_index) || uint64_be(counter))",
            "shuffle": "FULL_DESCENDING_FISHER_YATES",
            "bounded_integer": "U64_BIG_ENDIAN_REJECTION_BELOW_FLOOR_2^64_OVER_M_TIMES_M",
            "within_stratum_only": True,
            "no_backfill": True,
        },
        "inputs": {
            "pool_file_sha256": sha256(pool_bytes),
            "pool_canonical_sha256": sha256(canonical_json(pool)),
            "quota_feasibility_file_sha256": sha256(feasibility_bytes),
            "quota_feasibility_certificate_sha256": certificate["certificate_sha256"],
            "c0_contract_file_sha256": sha256(c0_bytes),
            "randomness_artifact_file_sha256": sha256(randomness_bytes),
            **{f"{key}_file_sha256": sha256(artifact_bytes[key]) for key in ARTIFACT_KEYS},
        },
        "upstream": pool["upstream"],
        "c0": {
            "published_at_utc": c0["published_at_utc"],
            "p0_artifact_commit": c0["chronology"]["p0_artifact_commit"],
            "p0_attestation_commit": c0["chronology"]["p0_attestation_commit"],
            "c0_artifact_commit": c0["chronology"]["c0_artifact_commit"],
            "c0_attestation_commit": c0["chronology"]["c0_attestation_commit"],
            "round": c0["randomness"]["round"],
            "round_closes_at_utc": c0["randomness"]["round_closes_at_utc"],
        },
        "c1_artifact_commit": None,
        "c1_attestation_commit": None,
        "randomness": {
            "value": randomness["randomness"],
            "value_sha256": randomness["randomness_sha256"],
            "retrieved_at_utc": randomness["retrieval"]["retrieved_at_utc"],
            "verification": {
                key: randomness["verification"][key]
                for key in (
                    "exact_round",
                    "official_relay_equality",
                    "frozen_chain_info",
                    "bls_signature",
                    "randomness_equals_sha256_signature",
                )
            },
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
    parser.add_argument("--feasibility", type=Path, required=True)
    parser.add_argument("--open-inventory", type=Path, required=True)
    parser.add_argument("--classifier", type=Path, required=True)
    parser.add_argument("--provenance-policy", type=Path, required=True)
    parser.add_argument("--provenance-inventory", type=Path, required=True)
    parser.add_argument("--contamination-inventory", type=Path, required=True)
    parser.add_argument("--source-snapshots", type=Path, required=True)
    parser.add_argument("--c0-contract", type=Path, required=True)
    parser.add_argument("--verified-randomness", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = select(
            args.pool.read_bytes(),
            args.feasibility.read_bytes(),
            {
                "open_inventory": args.open_inventory.read_bytes(),
                "classifier": args.classifier.read_bytes(),
                "provenance_policy": args.provenance_policy.read_bytes(),
                "provenance_inventory": args.provenance_inventory.read_bytes(),
                "contamination_inventory": args.contamination_inventory.read_bytes(),
                "source_snapshots": args.source_snapshots.read_bytes(),
            },
            args.c0_contract.read_bytes(),
            args.verified_randomness.read_bytes(),
        )
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
