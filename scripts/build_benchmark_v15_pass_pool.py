#!/usr/bin/env python3
"""Publish the complete Method v1.5 eligible identity pool before entropy.

This builder is deliberately downstream of the separately published
``QUOTA_PASS_U2`` receipt.  It authenticates that receipt against the frozen
P1 closure, the byte-identical private-registry replay, and the public Git
checkpoint chain.  Its output contains only the complete eligible identity
pool and replayable counts: no declaration path, statement, semantic payload,
outcome, ranking, entropy, or selected target is admitted.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator, FormatChecker

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_benchmark_v15_aggregate_certificate as aggregate  # noqa: E402
import build_benchmark_v15_future_cohort as future_registry  # noqa: E402
import verify_benchmark_v15_public_checkpoint_chain as public_chain  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas/benchmark-pass-pool-v1.5.schema.json"
REGISTRY_SCHEMA_PATH = ROOT / "schemas/benchmark-future-registry-output-v1.5.schema.json"
PUBLIC_CHAIN_SCHEMA_PATH = ROOT / "schemas/benchmark-public-checkpoint-chain-proof-v1.5.schema.json"
SCHEMA = "c5k4-method-v1.5-pass-pool-1.0"
STRATA = aggregate.STRATA
QUOTAS = aggregate.QUOTAS
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
PASS_RECEIPT_KEYS = {
    "schema", "artifact_kind", "protocol_version", "chronology_rule",
    "checkpoint_ordinal", "scheduled_for_utc", "basis", "capture",
    "quota_certificate", "replay_attestation", "terminal_horizon", "u2",
    "status",
}


class PassPoolError(ValueError):
    """The first-pass or target-blind pool contract is not satisfied."""


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode()


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PassPoolError(f"{label} is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise PassPoolError(f"{label} must be one JSON object")
    return value


def validate_schema(value: dict[str, Any], schema_path: Path, label: str) -> None:
    schema = load_json(schema_path, f"{label} schema")
    try:
        Draft7Validator(schema, format_checker=FormatChecker()).validate(value)
    except Exception as exc:
        raise PassPoolError(f"{label} fails its strict JSON schema: {exc}") from exc


def pool_digest(pool: dict[str, Any]) -> str:
    unsigned = copy.deepcopy(pool)
    unsigned.pop("pool_sha256", None)
    return sha256_bytes(canonical_json(unsigned))


def _exact_dict(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise PassPoolError(f"{label} does not have its exact frozen field set")
    return value


def _validate_proof_digest(proof: dict[str, Any], label: str) -> None:
    validate_schema(proof, PUBLIC_CHAIN_SCHEMA_PATH, label)
    if proof.get("proof_sha256") != public_chain.proof_digest(proof):
        raise PassPoolError(f"{label} self-digest is invalid")


def validate_public_chain_pair(
    prior: dict[str, Any], final: dict[str, Any], receipt: dict[str, Any],
    certificate: dict[str, Any], repository: Path, *, prior_proof_file_sha256: str,
    receipt_file_sha256: str,
) -> None:
    """Authenticate the pre-U2 proof and its unique PASS extension."""
    _validate_proof_digest(prior, "pre-pass public-chain proof")
    _validate_proof_digest(final, "pass public-chain proof")
    p1t_commit = certificate["p1_binding"]["p1t_commit"]
    for label, proof in (("pre-pass", prior), ("pass", final)):
        if proof["p1t_commit"] != p1t_commit:
            raise PassPoolError(f"{label} public-chain proof is not anchored at exact P1T")
    try:
        replayed = public_chain.verify_chain(
            repository.resolve(), public_chain.PUBLICATION_REF, p1t_commit,
        )
    except public_chain.PublicChainError as exc:
        raise PassPoolError(f"public checkpoint-chain replay failed: {exc}") from exc
    if canonical_json(replayed) != canonical_json(final):
        raise PassPoolError("pass public-chain proof differs from replay of the public ref")

    ordinal = certificate["checkpoint"]["ordinal"]
    scheduled = certificate["checkpoint"]["scheduled_for_utc"]
    prior_rows = prior["checkpoints"]
    if (
        prior["terminal"] is not False
        or prior["checkpoint_count"] != ordinal - 1
        or len(prior_rows) != ordinal - 1
        or any(row["status"] != "QUOTA_FAIL" for row in prior_rows)
        or prior["next_checkpoint"] != {
            "ordinal": ordinal,
            "scheduled_for_utc": scheduled,
            "required_parent_commit": prior["public_tip_commit"],
        }
        or prior["previous_checkpoint"] != (prior_rows[-1] if prior_rows else None)
    ):
        raise PassPoolError("pre-pass proof does not establish the exact next first-pass position")
    basis_proof = receipt["basis"].get("public_chain_proof")
    if basis_proof != {
        "sha256": receipt["basis"]["public_chain_proof"].get("sha256"),
        "proof_sha256": prior["proof_sha256"],
        "public_tip_commit": prior["public_tip_commit"],
    }:
        raise PassPoolError("PASS receipt is not bound to the pre-pass public-chain proof")
    if basis_proof["sha256"] != prior_proof_file_sha256:
        raise PassPoolError("PASS receipt binds different pre-pass proof bytes")
    if certificate["chronology"]["prior_checkpoint_chain_sha256"] != prior["proof_sha256"]:
        raise PassPoolError("aggregate certificate binds a different prior public-chain proof")

    final_rows = final["checkpoints"]
    if (
        final["terminal"] is not True
        or final["next_checkpoint"] is not None
        or final["checkpoint_count"] != ordinal
        or len(final_rows) != ordinal
        or final["genesis"] != prior["genesis"]
        or final_rows[:-1] != prior_rows
    ):
        raise PassPoolError("pass proof is not the unique one-checkpoint extension of the prior proof")
    last = final_rows[-1]
    expected_path = "checkpoints/" + scheduled.replace(":", "-") + "/receipt.json"
    if (
        last["ordinal"] != ordinal
        or last["scheduled_for_utc"] != scheduled
        or last["status"] != "QUOTA_PASS_U2"
        or last["parent_commit"] != prior["public_tip_commit"]
        or last["commit"] != final["public_tip_commit"]
        or last["receipt_path"] != expected_path
        or last["receipt_blob_sha256"] != receipt_file_sha256
        or final["previous_checkpoint"] != last
        or final["normal_push_must_use_lease_tip"] != final["public_tip_commit"]
    ):
        raise PassPoolError("pass proof does not authenticate the exact QUOTA_PASS_U2 receipt")


def validate_pass_receipt(
    receipt: dict[str, Any], certificate: dict[str, Any], attestation: dict[str, Any],
    registry: dict[str, Any], certificate_path: Path, attestation_path: Path,
) -> None:
    _exact_dict(receipt, PASS_RECEIPT_KEYS, "PASS receipt")
    if (
        receipt.get("schema") != "c5k4-method-v1.5-chronology-receipt-1.0"
        or receipt.get("artifact_kind") != "CHECKPOINT_RECEIPT"
        or receipt.get("protocol_version") != "1.5"
        or receipt.get("status") != "QUOTA_PASS_U2"
    ):
        raise PassPoolError("receipt is not a Method v1.5 QUOTA_PASS_U2 receipt")
    if (
        receipt["checkpoint_ordinal"] != certificate["checkpoint"]["ordinal"]
        or receipt["scheduled_for_utc"] != certificate["checkpoint"]["scheduled_for_utc"]
        or receipt["terminal_horizon"] is not certificate["checkpoint"]["terminal_horizon"]
    ):
        raise PassPoolError("PASS receipt identifies a different scheduled checkpoint")
    basis = _exact_dict(
        receipt.get("basis"), {"u1_receipt", "previous_checkpoint", "public_chain_proof"},
        "PASS receipt basis",
    )
    u1 = _exact_dict(
        basis.get("u1_receipt"), {"path", "sha256", "commit", "publication_commit"},
        "PASS receipt U1 binding",
    )
    if u1["commit"] != registry["upstream"]["u1_commit"]:
        raise PassPoolError("PASS receipt and private registry bind different U1 commits")
    _exact_dict(
        basis.get("public_chain_proof"), {"sha256", "proof_sha256", "public_tip_commit"},
        "PASS receipt public-chain binding",
    )
    certificate_ref = _exact_dict(
        receipt.get("quota_certificate"), {"path", "sha256", "certificate_sha256", "aggregates"},
        "PASS receipt aggregate binding",
    )
    if (
        certificate_ref["sha256"] != sha256_file(certificate_path)
        or certificate_ref["certificate_sha256"] != certificate["certificate_sha256"]
        or certificate_ref["aggregates"] != certificate["aggregates"]
    ):
        raise PassPoolError("PASS receipt authenticates a different aggregate certificate")
    replay_ref = _exact_dict(
        receipt.get("replay_attestation"), {"path", "sha256", "attestation_sha256"},
        "PASS receipt replay binding",
    )
    if (
        replay_ref["sha256"] != sha256_file(attestation_path)
        or replay_ref["attestation_sha256"] != attestation["attestation_sha256"]
    ):
        raise PassPoolError("PASS receipt authenticates a different replay attestation")
    capture = _exact_dict(
        receipt.get("capture"), {"path", "sha256", "commit", "root_tree", "formal_conjectures_tree"},
        "PASS receipt capture",
    )
    upstream = certificate["upstream"]
    if (
        capture["path"] != certificate["chronology"]["receipt"]["path"]
        or capture["sha256"] != certificate["chronology"]["receipt"]["sha256"]
        or any(capture[key] != upstream[key] for key in ("commit", "root_tree", "formal_conjectures_tree"))
    ):
        raise PassPoolError("PASS receipt capture differs from the aggregate chronology binding")
    u2 = _exact_dict(
        receipt.get("u2"), {"commit", "root_tree", "formal_conjectures_tree", "u1_is_ancestor", "membership_interval"},
        "PASS receipt U2",
    )
    if (
        u2["commit"] != upstream["commit"]
        or u2["root_tree"] != upstream["root_tree"]
        or u2["formal_conjectures_tree"] != upstream["formal_conjectures_tree"]
        or u2["u1_is_ancestor"] is not True
        or u2["membership_interval"] != registry["upstream"]["ancestry_interval"]
    ):
        raise PassPoolError("PASS receipt U2 differs from the authenticated future cohort")


def _eligible_clusters(registry: dict[str, Any]) -> list[dict[str, Any]]:
    records = registry.get("records")
    if not isinstance(records, list):
        raise PassPoolError("private registry record set is absent")
    clusters = [
        {
            "cluster_id": row["cluster_id"],
            "identity_sha256": row["identity_sha256"],
            "stratum": row["machine_stratum"],
            "eligible": True,
        }
        for row in records
        if isinstance(row, dict) and row.get("membership_status") == "INCLUDE"
    ]
    if len(clusters) != sum(
        isinstance(row, dict) and row.get("membership_status") == "INCLUDE"
        for row in records
    ):
        raise PassPoolError("an included private-registry row is malformed")
    cluster_ids = [row["cluster_id"] for row in clusters]
    identities = [row["identity_sha256"] for row in clusters]
    if len(cluster_ids) != len(set(cluster_ids)) or len(identities) != len(set(identities)):
        raise PassPoolError("eligible pool contains duplicate cluster or identity keys")
    order = {stratum: index for index, stratum in enumerate(STRATA)}
    return sorted(
        clusters,
        key=lambda row: (
            order[row["stratum"]], row["identity_sha256"].lower(),
            row["cluster_id"].encode("utf-8"),
        ),
    )


def validate_pool(pool: dict[str, Any]) -> None:
    validate_schema(pool, SCHEMA_PATH, "PASS pool")
    if pool.get("pool_sha256") != pool_digest(pool):
        raise PassPoolError("PASS pool self-digest is invalid")
    clusters = pool["clusters"]
    order = {stratum: index for index, stratum in enumerate(STRATA)}
    expected_order = sorted(
        clusters,
        key=lambda row: (
            order[row["stratum"]], row["identity_sha256"].lower(),
            row["cluster_id"].encode("utf-8"),
        ),
    )
    if clusters != expected_order:
        raise PassPoolError("PASS pool identities are not in canonical stratum/digest/ID order")
    if len({row["cluster_id"] for row in clusters}) != len(clusters):
        raise PassPoolError("PASS pool repeats a cluster ID")
    if len({row["identity_sha256"] for row in clusters}) != len(clusters):
        raise PassPoolError("PASS pool repeats an identity digest")
    counts = {stratum: 0 for stratum in STRATA}
    for row in clusters:
        counts[row["stratum"]] += 1
    replay = pool["replay"]
    if (
        replay["eligible_by_stratum"] != counts
        or replay["included_record_count"] != len(clusters)
        or replay["candidate_count"] != len(clusters)
        or replay["pool_cluster_count"] != len(clusters)
        or replay["source_record_count"]
        != replay["included_record_count"] + replay["excluded_record_count"]
        or any(counts[stratum] < QUOTAS[stratum] for stratum in STRATA)
    ):
        raise PassPoolError("PASS pool counts do not replay from its complete identity rows")


def build_pool(
    private_registry_path: Path, certificate_path: Path, attestation_path: Path,
    pass_receipt_path: Path, prior_proof_path: Path, pass_proof_path: Path,
    p1a_path: Path, p1t_path: Path, public_repository: Path,
) -> dict[str, Any]:
    registry = load_json(private_registry_path, "private registry")
    certificate = load_json(certificate_path, "aggregate certificate")
    attestation = load_json(attestation_path, "replay attestation")
    receipt = load_json(pass_receipt_path, "PASS receipt")
    prior_proof = load_json(prior_proof_path, "pre-pass public-chain proof")
    pass_proof = load_json(pass_proof_path, "pass public-chain proof")

    try:
        aggregate.validate_certificate(certificate)
        aggregate.validate_schema(registry, REGISTRY_SCHEMA_PATH, "private registry")
        aggregate.validate_schema(
            attestation, aggregate.ATTESTATION_SCHEMA_PATH, "replay attestation",
        )
    except aggregate.CertificateError as exc:
        raise PassPoolError(str(exc)) from exc
    if certificate["aggregates"]["status"] != "PASS":
        raise PassPoolError("a PASS pool may only follow an aggregate quota PASS")
    if certificate["sealed_replay"]["pass_pool_publication"] != "SEPARATE_PRE_ENTROPY_ARTIFACT":
        raise PassPoolError("aggregate certificate does not authorize the separate PASS-pool phase")
    registry_digest = future_registry.registry_digest(registry)
    if (
        registry.get("registry_sha256") != registry_digest
        or registry.get("quota_certificate", {}).get("registry_sha256") != registry_digest
    ):
        raise PassPoolError("private registry unsigned projection digest is invalid")
    if sha256_file(private_registry_path) != certificate["sealed_replay"]["private_registry_sha256"]:
        raise PassPoolError("private registry bytes differ from the aggregate sealed replay")
    derived = aggregate.derive_aggregates(registry)
    if derived != certificate["aggregates"] or derived["quotas"] != QUOTAS:
        raise PassPoolError("private-registry counts differ from the aggregate certificate")
    if derived["status"] != "PASS" or any(derived["deficits"].values()):
        raise PassPoolError("private registry does not satisfy every frozen stratum quota")
    quota = registry["quota_certificate"]
    if (
        quota.get("first_passing_checkpoint") is not True
        or quota.get("all_prior_valid_checkpoints_failed") is not True
        or quota.get("prior_checkpoint_chain_sha256")
        != certificate["chronology"]["prior_checkpoint_chain_sha256"]
    ):
        raise PassPoolError("private registry does not claim the authenticated first pass")

    if (
        attestation.get("attestation_sha256") != aggregate.attestation_digest(attestation)
        or attestation.get("status") != "INDEPENDENT_EXACT_REPLAY_PASS"
        or attestation.get("certificate_sha256") != certificate["certificate_sha256"]
        or attestation.get("private_registry_sha256") != sha256_file(private_registry_path)
        or attestation.get("registry_unsigned_projection_sha256") != registry_digest
        or attestation.get("upstream") != {
            key: certificate["upstream"][key]
            for key in ("commit", "root_tree", "formal_conjectures_tree")
        }
        or attestation.get("chronology_receipt_sha256")
        != certificate["chronology"]["receipt"]["sha256"]
    ):
        raise PassPoolError("replay attestation does not bind this exact registry/certificate/U2")
    try:
        _p1a, _p1t, p1_binding = aggregate.authenticate_p1(
            p1a_path, p1t_path, certificate["p1_binding"]["p1t_commit"],
        )
    except aggregate.CertificateError as exc:
        raise PassPoolError(f"P1 authentication failed: {exc}") from exc
    if p1_binding != certificate["p1_binding"]:
        raise PassPoolError("aggregate certificate does not bind the supplied exact P1A/P1T")

    validate_pass_receipt(
        receipt, certificate, attestation, registry, certificate_path, attestation_path,
    )
    validate_public_chain_pair(
        prior_proof, pass_proof, receipt, certificate, public_repository,
        prior_proof_file_sha256=sha256_file(prior_proof_path),
        receipt_file_sha256=sha256_file(pass_receipt_path),
    )

    clusters = _eligible_clusters(registry)
    records = registry["records"]
    included = sum(row["membership_status"] == "INCLUDE" for row in records)
    excluded = sum(row["membership_status"] == "EXCLUDE" for row in records)
    if included != len(clusters) or included != registry["counts"]["included"]:
        raise PassPoolError("complete eligible-pool cardinality differs from the private registry")
    if excluded != registry["counts"]["excluded"] or included + excluded != len(records):
        raise PassPoolError("private registry membership partition does not replay")
    upstream = registry["upstream"]
    last = pass_proof["checkpoints"][-1]
    pool = {
        "schema": SCHEMA,
        "artifact_kind": "FIRST_PASS_PRE_ENTROPY_ELIGIBLE_IDENTITY_POOL",
        "protocol_version": "1.5",
        "authority": "FIRST_SCHEDULED_QUOTA_PASS_U2_ONLY",
        "publication_boundary": {
            "eligible_identities_present": True,
            "excluded_identities_present": False,
            "statement_text_present": False,
            "target_semantics_present": False,
            "outcomes_present": False,
            "ranking_present": False,
            "entropy_present": False,
            "selection_present": False,
            "standalone_publication_claimed": False,
            "c0a_embedding_required": True,
            "canonical_embedding_bytes_required": True,
        },
        "checkpoint": {
            "ordinal": certificate["checkpoint"]["ordinal"],
            "scheduled_for_utc": certificate["checkpoint"]["scheduled_for_utc"],
            "status": "QUOTA_PASS_U2",
            "first_passing_checkpoint": True,
        },
        "upstream": {
            "repository": upstream["repository"],
            "u1_commit": upstream["u1_commit"],
            "u1_tree": upstream["u1_tree"],
            "u2_commit": upstream["u2_commit"],
            "u2_tree": upstream["u2_tree"],
            "u2_formal_conjectures_tree": certificate["upstream"]["formal_conjectures_tree"],
            "ancestry_interval": upstream["ancestry_interval"],
        },
        "p1_binding": copy.deepcopy(certificate["p1_binding"]),
        "public_chain": {
            "prior_proof_role": "PRE_U2_PUBLIC_CHECKPOINT_CHAIN_PROOF",
            "prior_proof_file_sha256": sha256_file(prior_proof_path),
            "prior_proof_sha256": prior_proof["proof_sha256"],
            "prior_public_tip_commit": prior_proof["public_tip_commit"],
            "pass_proof_role": "POST_PASS_PUBLIC_CHECKPOINT_CHAIN_PROOF",
            "pass_proof_file_sha256": sha256_file(pass_proof_path),
            "pass_proof_sha256": pass_proof["proof_sha256"],
            "pass_public_tip_commit": pass_proof["public_tip_commit"],
            "pass_publication_commit": last["commit"],
            "checkpoint_count": pass_proof["checkpoint_count"],
            "earlier_checkpoint_status": "ALL_QUOTA_FAIL",
            "proof_status": "FIRST_SCHEDULED_QUOTA_PASS_AUTHENTICATED",
        },
        "source_bindings": {
            "private_registry": {
                "role": "PRIVATE_FIRST_PASS_REGISTRY",
                "file_sha256": sha256_file(private_registry_path),
                "registry_sha256": registry_digest,
            },
            "aggregate_certificate": {
                "role": "PUBLIC_FIRST_PASS_AGGREGATE_CERTIFICATE",
                "file_sha256": sha256_file(certificate_path),
                "certificate_sha256": certificate["certificate_sha256"],
            },
            "replay_attestation": {
                "role": "PRIVATE_INDEPENDENT_REPLAY_ATTESTATION",
                "file_sha256": sha256_file(attestation_path),
                "attestation_sha256": attestation["attestation_sha256"],
            },
            "pass_receipt": {
                "role": "PUBLIC_QUOTA_PASS_U2_RECEIPT",
                "committed_public_path": last["receipt_path"],
                "publication_commit": last["commit"],
                "file_sha256": sha256_file(pass_receipt_path),
            },
        },
        "replay": {
            "source_record_count": len(records),
            "included_record_count": included,
            "excluded_record_count": excluded,
            "eligible_by_stratum": copy.deepcopy(derived["eligible_by_stratum"]),
            "quotas": dict(QUOTAS),
            "deficits": copy.deepcopy(derived["deficits"]),
            "candidate_count": derived["candidate_count"],
            "pool_cluster_count": len(clusters),
            "complete_pool_match": True,
            "aggregate_match": True,
            "private_registry_exact_byte_bound": True,
            "independent_replay_attested": True,
        },
        "selection_contract": {
            "sampling_unit": "QUESTION_CLUSTER",
            "target_cluster_count": 12,
            "quotas": dict(QUOTAS),
            "no_backfill": True,
            "relaxed_exclusion": False,
            "entropy_required_after_public_pool_commit": True,
            "selection_permitted": False,
        },
        "clusters": clusters,
    }
    pool["pool_sha256"] = pool_digest(pool)
    validate_pool(pool)
    return pool


def write_json(path: Path, value: dict[str, Any]) -> None:
    if path.exists():
        raise PassPoolError("PASS-pool output already exists; overwrite is forbidden")
    path.parent.mkdir(parents=True, exist_ok=True)
    # The future one-path C0A compiler embeds this exact canonical object.  A
    # pretty-printer is intentionally not used: byte stability is part of the
    # handoff contract and this helper claims no standalone publication event.
    path.write_bytes(canonical_json(value))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build")
    build.add_argument("--private-registry", type=Path, required=True)
    build.add_argument("--aggregate-certificate", type=Path, required=True)
    build.add_argument("--replay-attestation", type=Path, required=True)
    build.add_argument("--pass-receipt", type=Path, required=True)
    build.add_argument("--prior-public-chain-proof", type=Path, required=True)
    build.add_argument("--pass-public-chain-proof", type=Path, required=True)
    build.add_argument("--p1a", type=Path, required=True)
    build.add_argument("--p1t", type=Path, required=True)
    build.add_argument("--public-repository", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)
    check = sub.add_parser("validate")
    check.add_argument("--pool", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "build":
            pool = build_pool(
                args.private_registry.resolve(), args.aggregate_certificate.resolve(),
                args.replay_attestation.resolve(), args.pass_receipt.resolve(),
                args.prior_public_chain_proof.resolve(),
                args.pass_public_chain_proof.resolve(), args.p1a.resolve(),
                args.p1t.resolve(), args.public_repository.resolve(),
            )
            write_json(args.output.resolve(), pool)
        else:
            validate_pool(load_json(args.pool.resolve(), "PASS pool"))
    except (OSError, PassPoolError) as exc:
        print(f"INVALID_PASS_POOL: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
