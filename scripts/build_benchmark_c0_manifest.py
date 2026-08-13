#!/usr/bin/env python3
"""Build the non-self-referential Method v1.1 C0 manifest.

The artifact commit is first published with ``PROTOCOL_DESIGN`` and null
chronology.  A later attestation commit may name that already-public commit
and timestamp while leaving the future beacon and every C1 field unknown.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_COMMIT = "7a38c469ec329d0c97c068e03c58834f61628e7e"
UPSTREAM_TREE = "daa36d0d9e82133dfd83488d89594d92b4940fb7"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def reference(relative: str) -> dict[str, str]:
    path = ROOT / relative
    if not path.is_file():
        raise ValueError(f"missing frozen artifact: {relative}")
    return {"path": relative, "sha256": sha256_file(path)}


def build(
    c0_commit: str | None,
    c0_published_at_utc: str | None,
    c1_commit: str | None = None,
    c1_frozen_at_utc: str | None = None,
) -> dict:
    if (c0_commit is None) != (c0_published_at_utc is None):
        raise ValueError("C0 commit and publication time must be supplied together")
    contamination_path = ROOT / "results/benchmark/contamination-inventory.c0.json"
    contamination = json.loads(contamination_path.read_text(encoding="utf-8"))
    prior_ref = reference("results/benchmark/c0/development-prior.json")
    prior_ref["probabilities"] = json.loads(
        (ROOT / prior_ref["path"]).read_text(encoding="utf-8")
    )["probabilities"]
    if (c1_commit is None) != (c1_frozen_at_utc is None):
        raise ValueError("C1 commit and freeze time must be supplied together")
    if c1_commit is not None and c0_commit is None:
        raise ValueError("a terminal C1 requires an attested C0")
    manifest = {
        "$schema": "../../schemas/benchmark-v1.1.schema.json",
        "schema_version": "c5k4-benchmark-1.1",
        "benchmark_id": "method-v1.1-deepmind-heldout-20260813",
        "phase": "C0_FROZEN" if c0_commit else "PROTOCOL_DESIGN",
        "upstream": {
            "repository": "google-deepmind/formal-conjectures",
            "commit": UPSTREAM_COMMIT,
            "tree": UPSTREAM_TREE,
            "declaration_root": "FormalConjectures",
            "open_inventory": reference("results/benchmark/c0/open-inventory.json"),
        },
        "freeze_artifacts": {
            "pool_manifest": reference("results/benchmark/c0/eligible-cluster-pool.json"),
            "classifier": reference("results/benchmark/c0/five-strata-classifier.json"),
            "development_prior": prior_ref,
            "transformation_library": reference("results/benchmark/c0/transformation-library.json"),
            "scoring_rule": reference("results/benchmark/c0/scoring-rule.json"),
            "stopping_rule": reference("results/benchmark/c0/stopping-rule.json"),
        },
        "contamination": {
            "inventory": reference("results/benchmark/contamination-inventory.c0.json"),
            "excluded_cluster_ids": contamination["excluded_cluster_ids"],
            "excluded_identity_sha256s": contamination["excluded_identity_sha256s"],
            "excluded_declaration_sha256s": contamination["excluded_declaration_sha256s"],
            "identity_ambiguity_means_exclusion": True,
        },
        "randomness": {
            "source": "League of Entropy drand legacy mainnet",
            "round": 6373886,
            "round_closes_at_utc": "2026-08-13T19:00:00Z",
            "chain": {
                "hash": "8990e7a9aaed2ffed73dbd7092123d6f289930540d7651336225dc172e51b2ce",
                "public_key": "868f005eb8e6e4ca0a47c8a77ceaa5309a47978a7c71bc5cce96366b5d7a569937c529eeda66c7293784a9402801af31",
                "scheme_id": "pedersen-bls-chained",
                "genesis_time": 1595431050,
                "period_seconds": 30,
            },
            "relays": ["https://api.drand.sh", "https://api2.drand.sh"],
            "verification": {
                "library": "drand-client",
                "library_version": "1.4.2",
                "require_exact_round": True,
                "require_relay_equality": True,
                "require_bls_signature": True,
                "require_randomness_sha256_signature": True,
                "raw_artifact": None,
            },
            "selection_algorithm": "UNBIASED_DOMAIN_SEPARATED_SHA256_FISHER_YATES_V1",
            "value": None,
            "value_sha256": None,
        },
        "selection": {
            "sampling_unit": "QUESTION_CLUSTER",
            "target_cluster_count": 12,
            "quotas": {
                "GRAPH_SCALAR_INEQUALITY": 3,
                "GRAPH_STRUCTURAL_PROPERTY": 3,
                "FINITE_ALGEBRA_EQUATIONAL": 2,
                "AUTOMATA_GAME_PROCESS": 2,
                "FINITE_COMBINATORIAL": 2,
            },
            "no_backfill": True,
            "relaxed_exclusion": False,
            "backfill_events": [],
            "insufficient_stratum_outcome": "NO_ELIGIBLE_BENCHMARK",
            "evidence": None,
        },
        "budgets": {
            "shared_analysis": {"cpu_budget_seconds": 600, "process_wall_cap_seconds": 60},
            "discovery_arm": {"process_count": 8, "process_wall_cap_seconds": 60, "cpu_budget_seconds": 480},
            "independent_verification": {"process_count": 2, "process_wall_cap_seconds": 60, "cpu_budget_seconds": 120},
        },
        "chronology": {
            "c0_commit": c0_commit,
            "c0_published_at_utc": c0_published_at_utc,
            "randomness_retrieved_at_utc": None,
            "c1_commit": None,
            "c1_frozen_at_utc": None,
            "evaluation_started_at_utc": None,
            "completed_at_utc": None,
        },
        "clusters": [],
        "ledgers": [],
    }
    if c1_commit is not None:
        randomness_artifact = json.loads(
            (ROOT / "results/benchmark/c1/drand-round-6373886.json").read_text(
                encoding="utf-8"
            )
        )
        manifest["phase"] = "NO_ELIGIBLE_BENCHMARK"
        manifest["randomness"]["value"] = randomness_artifact["randomness"]
        manifest["randomness"]["value_sha256"] = randomness_artifact[
            "randomness_sha256"
        ]
        manifest["randomness"]["verification"]["raw_artifact"] = reference(
            "results/benchmark/c1/drand-round-6373886.json"
        )
        manifest["selection"]["evidence"] = reference(
            "results/benchmark/c1/selection-evidence.json"
        )
        manifest["chronology"].update(
            randomness_retrieved_at_utc=randomness_artifact["retrieval"][
                "retrieved_at_utc"
            ],
            c1_commit=c1_commit,
            c1_frozen_at_utc=c1_frozen_at_utc,
            completed_at_utc=c1_frozen_at_utc,
        )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--c0-commit")
    parser.add_argument("--c0-published-at-utc")
    parser.add_argument("--c1-commit")
    parser.add_argument("--c1-frozen-at-utc")
    args = parser.parse_args()
    manifest = build(
        args.c0_commit,
        args.c0_published_at_utc,
        args.c1_commit,
        args.c1_frozen_at_utc,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(sha256_file(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
