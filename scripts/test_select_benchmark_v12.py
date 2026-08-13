#!/usr/bin/env python3
"""Regression and exact-vector tests for the Method v1.2 C1 selector."""

from __future__ import annotations

import copy
import hashlib
import json
import unittest

try:
    import select_benchmark_v12 as selector
except ModuleNotFoundError:  # run through ``python -m unittest scripts...``
    from scripts import select_benchmark_v12 as selector


ENTROPY_SIGNATURE = "11" * 96
ENTROPY = hashlib.sha256(bytes.fromhex(ENTROPY_SIGNATURE)).hexdigest()


def encoded(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def fixtures(extra: int = 1):
    artifacts = {
        key: encoded({"schema_version": f"fixture-{key}-1.2", "payload": key})
        for key in selector.ARTIFACT_KEYS
    }
    clusters = []
    counter = 0
    for stratum in selector.STRATA:
        for _ in range(selector.QUOTAS[stratum] + extra):
            counter += 1
            clusters.append(
                {
                    "cluster_id": f"cluster-{counter:03d}",
                    "identity_sha256": f"{counter:064x}",
                    "stratum": stratum,
                    "eligible": True,
                    "opaque_metadata": {"not_a_selection_input": counter},
                }
            )
    pool = {
        "schema_version": selector.POOL_SCHEMA_VERSION,
        "artifact_status": "CONTAMINATION_APPLIED",
        "upstream": {
            "repository": "google-deepmind/formal-conjectures",
            "commit": "a" * 40,
            "tree": "b" * 40,
        },
        "digests": {
            f"{key}_sha256": selector.sha256(raw) for key, raw in artifacts.items()
        },
        "clusters": clusters,
    }
    pool_raw = encoded(pool)
    strata = []
    for stratum in selector.STRATA:
        count = sum(row["eligible"] and row["stratum"] == stratum for row in clusters)
        quota = selector.QUOTAS[stratum]
        strata.append(
            {
                "stratum": stratum,
                "quota": quota,
                "eligible_count": count,
                "deficit": max(0, quota - count),
                "surplus": max(0, count - quota),
            }
        )
    certificate = {
        "schema_version": selector.FEASIBILITY_SCHEMA_VERSION,
        "phase": "PRE_C0_FEASIBILITY",
        "status": "PASS",
        "upstream": pool["upstream"],
        "chronology": {
            "p0_artifact_commit": "1" * 40,
            "p0_attestation_commit": "2" * 40,
            "p0_published_at_utc": "2026-08-13T18:00:00Z",
            "s0_acquired_at_utc": "2026-08-13T18:10:00Z",
            "feasibility_checked_at_utc": "2026-08-13T18:15:00Z",
        },
        "digests": {
            "eligible_pool_file_sha256": selector.sha256(pool_raw),
            "eligible_pool_canonical_sha256": selector.sha256(selector.canonical_json(pool)),
            **{
                f"{key}_sha256": selector.sha256(raw)
                for key, raw in artifacts.items()
            },
        },
        "quotas": dict(selector.QUOTAS),
        "strata": strata,
        "entropy_used": False,
        "selected_clusters": [],
    }
    certificate["certificate_sha256"] = selector.object_digest(
        certificate, "certificate_sha256"
    )
    certificate_raw = encoded(certificate)
    c0 = {
        "schema_version": selector.C0_SCHEMA_VERSION,
        "phase": "C0_FROZEN",
        "chronology": {
            "p0_artifact_commit": "1" * 40,
            "p0_attestation_commit": "2" * 40,
            "p0_published_at_utc": "2026-08-13T18:00:00Z",
            "s0_acquired_at_utc": "2026-08-13T18:10:00Z",
            "c0_artifact_commit": "3" * 40,
            "c0_attestation_commit": None,
            "c0_published_at_utc": "2026-08-13T18:20:00Z",
        },
        "published_at_utc": "2026-08-13T18:20:00Z",
        "pool_file_sha256": selector.sha256(pool_raw),
        "quota_feasibility_sha256": certificate["certificate_sha256"],
        "randomness": {
            "source": "League of Entropy drand",
            "chain_hash": selector.DRAND_CHAIN_HASH,
            "round": 42,
            "round_closes_at_utc": "2026-08-13T19:00:00Z",
            "value": None,
        },
    }
    c0_raw = encoded(c0)
    receipt = {
        "schema_version": "c5k4-c0-validation-receipt-1.2",
        "c0t": {"path": "results/c0t.json", "file_sha256": selector.sha256(c0_raw)},
        "c0_artifact_commit": "3" * 40, "c0_attestation_commit": "4" * 40,
        "direct_nonmerge_parent_verified": True, "changed_paths": ["results/c0t.json"],
        "committed_bytes_verified": True, "publication_observation": None,
        "c0_published_at_utc": "2026-08-13T18:20:00Z",
        "future_round_close_at_utc": "2026-08-13T19:00:00Z",
    }
    receipt["receipt_sha256"] = selector.object_digest(receipt, "receipt_sha256")
    receipt_raw = encoded(receipt)
    randomness = {
        "schema_version": selector.RANDOMNESS_SCHEMA_VERSION,
        "c0_binding": {"artifact_commit": "3" * 40, "attestation_commit": "4" * 40, "published_at_utc": "2026-08-13T18:20:00Z"},
        "retrieval": {"retrieved_at_utc": "2026-08-13T19:00:01Z"},
        "chain": {"hash": selector.DRAND_CHAIN_HASH},
        "round": 42,
        "round_closes_at_utc": "2026-08-13T19:00:00Z",
        "beacon": {
            "round": 42,
            "randomness": ENTROPY,
            "signature": ENTROPY_SIGNATURE,
        },
        "randomness": ENTROPY,
        "randomness_sha256": selector.sha256(ENTROPY.encode("ascii")),
        "verification": {
            "exact_round": True,
            "official_relay_equality": True,
            "frozen_chain_info": True,
            "bls_signature": True,
            "randomness_equals_sha256_signature": True,
        },
    }
    return pool, pool_raw, artifacts, certificate, certificate_raw, c0, c0_raw, receipt, receipt_raw, randomness, encoded(randomness)


def run(parts):
    _, pool_raw, artifacts, _, certificate_raw, _, c0_raw, _, receipt_raw, _, randomness_raw = parts
    return selector.select(pool_raw, certificate_raw, artifacts, c0_raw, receipt_raw, randomness_raw)


class SelectionV12Tests(unittest.TestCase):
    def test_exact_frozen_vector_and_complete_evidence(self) -> None:
        result = run(fixtures())
        self.assertEqual(result["status"], "SELECTED")
        self.assertEqual(result["algorithm"]["domain_hex"], selector.DOMAIN.hex())
        self.assertEqual(result["c1_artifact_commit"], None)
        self.assertEqual(result["c1_attestation_commit"], None)
        self.assertEqual(
            [row["cluster_id"] for row in result["selected_clusters"]],
            [
                "cluster-004", "cluster-001", "cluster-002",
                "cluster-005", "cluster-006", "cluster-008",
                "cluster-010", "cluster-011",
                "cluster-012", "cluster-014",
                "cluster-016", "cluster-017",
            ],
        )
        self.assertEqual(
            [row["entropy_consumption"] for row in result["strata"]],
            [
                {"sha256_blocks_consumed": 1, "u64_words_consumed": 3, "u64_words_rejected": 0},
                {"sha256_blocks_consumed": 1, "u64_words_consumed": 3, "u64_words_rejected": 0},
                {"sha256_blocks_consumed": 1, "u64_words_consumed": 2, "u64_words_rejected": 0},
                {"sha256_blocks_consumed": 1, "u64_words_consumed": 2, "u64_words_rejected": 0},
                {"sha256_blocks_consumed": 1, "u64_words_consumed": 2, "u64_words_rejected": 0},
            ],
        )
        self.assertEqual(
            result["evidence_sha256"],
            "c953b9f2dc331b350049859a95cde169e16ec4f63b124760791a9aee0e69d060",
        )

    def test_rejection_sampling_discards_out_of_range_u64(self) -> None:
        rows = [
            {"cluster_id": f"c{i}", "identity_sha256": f"{i:064x}"}
            for i in range(3)
        ]
        block = (b"\xff" * 8) + (b"\x00" * 24)
        shuffled, consumption = selector.shuffle_rows(
            rows, bytes(32), 0, lambda _: block
        )
        self.assertEqual(len(shuffled), 3)
        self.assertEqual(consumption["u64_words_rejected"], 1)
        self.assertEqual(consumption["u64_words_consumed"], 3)

    def test_fail_certificate_is_rejected_before_entropy_is_parsed(self) -> None:
        parts = list(fixtures())
        certificate = parts[3]
        certificate["status"] = "FAIL"
        certificate["phase"] = "NO_ELIGIBLE_BENCHMARK_PRE_C0"
        certificate["certificate_sha256"] = selector.object_digest(
            certificate, "certificate_sha256"
        )
        parts[4] = encoded(certificate)
        parts[10] = b"this is deliberately not entropy JSON"
        with self.assertRaisesRegex(ValueError, "PRE_C0 failure is terminal"):
            run(parts)

    def test_false_pass_count_and_deficit_are_rejected(self) -> None:
        parts = list(fixtures())
        certificate = parts[3]
        certificate["strata"][0]["eligible_count"] += 1
        certificate["certificate_sha256"] = selector.object_digest(
            certificate, "certificate_sha256"
        )
        parts[4] = encoded(certificate)
        parts[5]["quota_feasibility_sha256"] = certificate["certificate_sha256"]
        parts[6] = encoded(parts[5])
        with self.assertRaisesRegex(ValueError, "counts or deficits"):
            run(parts)

    def test_short_pool_cannot_replay_pass(self) -> None:
        parts = list(fixtures())
        target = selector.STRATA[0]
        eligible = [row for row in parts[0]["clusters"] if row["stratum"] == target]
        for row in eligible[selector.QUOTAS[target] - 1 :]:
            row["eligible"] = False
        parts[1] = encoded(parts[0])
        with self.assertRaisesRegex(ValueError, "digests do not match|pool digest"):
            run(parts)

    def test_all_frozen_artifact_hashes_are_replayed(self) -> None:
        parts = list(fixtures())
        parts[2][selector.ARTIFACT_KEYS[-1]] += b" "
        with self.assertRaisesRegex(ValueError, "digest does not match"):
            run(parts)

    def test_certificate_self_digest_is_replayed(self) -> None:
        parts = list(fixtures())
        certificate = parts[3]
        certificate["certificate_sha256"] = "0" * 64
        parts[4] = encoded(certificate)
        with self.assertRaisesRegex(ValueError, "certificate_sha256 does not replay"):
            run(parts)

    def test_nonfuture_round_is_rejected(self) -> None:
        parts = list(fixtures())
        parts[5]["randomness"]["round_closes_at_utc"] = "2026-08-13T18:20:00Z"
        parts[6] = encoded(parts[5])
        parts[7]["c0t"]["file_sha256"] = selector.sha256(parts[6])
        parts[7]["future_round_close_at_utc"] = "2026-08-13T18:20:00Z"
        parts[7]["receipt_sha256"] = selector.object_digest(parts[7], "receipt_sha256")
        parts[8] = encoded(parts[7])
        with self.assertRaisesRegex(ValueError, "not future"):
            run(parts)

    def test_unverified_or_early_randomness_is_rejected(self) -> None:
        parts = list(fixtures())
        parts[9]["verification"]["bls_signature"] = False
        parts[10] = encoded(parts[9])
        with self.assertRaisesRegex(ValueError, "verification passes"):
            run(parts)
        parts = list(fixtures())
        parts[9]["retrieval"]["retrieved_at_utc"] = "2026-08-13T18:59:59Z"
        parts[10] = encoded(parts[9])
        with self.assertRaisesRegex(ValueError, "before the frozen round closed"):
            run(parts)

    def test_input_order_and_irrelevant_metadata_do_not_change_selection(self) -> None:
        first = fixtures()
        second = list(copy.deepcopy(first))
        second[0]["clusters"].reverse()
        for row in second[0]["clusters"]:
            row["opaque_metadata"] = "changed"
        second[1] = encoded(second[0])
        # Content addressing intentionally notices the byte change; update the
        # pass certificate and C0 exactly as a legitimately frozen alternative.
        second[3]["digests"]["eligible_pool_file_sha256"] = selector.sha256(second[1])
        second[3]["digests"]["eligible_pool_canonical_sha256"] = selector.sha256(
            selector.canonical_json(second[0])
        )
        second[3]["certificate_sha256"] = selector.object_digest(
            second[3], "certificate_sha256"
        )
        second[4] = encoded(second[3])
        second[5]["pool_file_sha256"] = selector.sha256(second[1])
        second[5]["quota_feasibility_sha256"] = second[3]["certificate_sha256"]
        second[6] = encoded(second[5])
        second[7]["c0t"]["file_sha256"] = selector.sha256(second[6])
        second[7]["receipt_sha256"] = selector.object_digest(second[7], "receipt_sha256")
        second[8] = encoded(second[7])
        self.assertEqual(
            [row["cluster_id"] for row in run(first)["selected_clusters"]],
            [row["cluster_id"] for row in run(second)["selected_clusters"]],
        )


if __name__ == "__main__":
    unittest.main()
