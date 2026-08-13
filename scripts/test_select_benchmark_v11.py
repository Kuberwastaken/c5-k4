#!/usr/bin/env python3
"""Regression tests for the frozen Method v1.1 C1 sampler."""

from __future__ import annotations

import copy
import json
import unittest

try:
    from select_benchmark_v11 import POOL_SCHEMA_VERSION, QUOTAS, STRATA, select, shuffle_rows
except ModuleNotFoundError:  # run through ``python -m unittest scripts...``
    from scripts.select_benchmark_v11 import POOL_SCHEMA_VERSION, QUOTAS, STRATA, select, shuffle_rows


H40 = "a" * 40
ENTROPY_A = "01" * 32
ENTROPY_B = "02" * 32


def pool(extra: int = 1) -> dict:
    clusters = []
    counter = 0
    for stratum in STRATA:
        for _ in range(QUOTAS[stratum] + extra):
            counter += 1
            clusters.append(
                {
                    "cluster_id": f"cluster-{counter:03d}",
                    "identity_sha256": f"{counter:064x}",
                    "stratum": stratum,
                    "eligible": True,
                    "opaque_metadata": {"must_not_affect_selection": counter},
                }
            )
    return {
        "schema_version": POOL_SCHEMA_VERSION,
        "upstream": {"commit": H40, "tree": "b" * 40},
        "contamination": {
            "applied": True,
            "inventory_sha256": "c" * 64,
            "identity_ambiguity_means_exclusion": True,
        },
        "clusters": clusters,
    }


def encoded(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


class SelectionTests(unittest.TestCase):
    def test_exact_quotas_and_audit_evidence(self) -> None:
        result = select(encoded(pool()), ENTROPY_A)
        self.assertEqual(result["status"], "SELECTED")
        self.assertEqual(len(result["selected_clusters"]), 12)
        for stratum in STRATA:
            rows = [row for row in result["selected_clusters"] if row["stratum"] == stratum]
            self.assertEqual(len(rows), QUOTAS[stratum])
        self.assertEqual(len(result["evidence_sha256"]), 64)
        self.assertTrue(result["algorithm"]["no_backfill"])

    def test_frozen_entropy_vector(self) -> None:
        result = select(encoded(pool()), ENTROPY_A)
        self.assertEqual(
            [row["cluster_id"] for row in result["selected_clusters"]],
            [
                "cluster-003", "cluster-002", "cluster-001",
                "cluster-008", "cluster-005", "cluster-007",
                "cluster-011", "cluster-010",
                "cluster-014", "cluster-012",
                "cluster-016", "cluster-015",
            ],
        )

    def test_rejection_sampling_discards_out_of_range_u64(self) -> None:
        rows = [
            {"cluster_id": f"c{i}", "identity_sha256": f"{i:064x}"}
            for i in range(3)
        ]
        # For modulus three, 2^64-1 lies outside the largest multiple of three.
        # The following zero word is accepted, forcing this otherwise rare path.
        block = (b"\xff" * 8) + (b"\x00" * 24)
        shuffled, consumption = shuffle_rows(rows, bytes(32), 0, lambda _: block)
        self.assertEqual(len(shuffled), 3)
        self.assertEqual(consumption["u64_words_rejected"], 1)
        self.assertEqual(consumption["u64_words_consumed"], 3)

    def test_input_order_and_irrelevant_metadata_do_not_change_selection(self) -> None:
        first = pool()
        second = copy.deepcopy(first)
        second["clusters"].reverse()
        for row in second["clusters"]:
            row["opaque_metadata"] = "changed"
        a = select(encoded(first), ENTROPY_A)["selected_clusters"]
        b = select(encoded(second), ENTROPY_A)["selected_clusters"]
        self.assertEqual(a, b)

    def test_entropy_changes_ranking(self) -> None:
        raw = encoded(pool(extra=5))
        a = select(raw, ENTROPY_A)["selected_clusters"]
        b = select(raw, ENTROPY_B)["selected_clusters"]
        self.assertNotEqual(a, b)

    def test_ineligible_rows_never_rank(self) -> None:
        value = pool()
        forbidden = value["clusters"][0]
        forbidden["eligible"] = False
        result = select(encoded(value), ENTROPY_A)
        ranked_ids = {
            row["cluster_id"]
            for stratum in result["strata"]
            for row in stratum["shuffled"]
        }
        self.assertNotIn(forbidden["cluster_id"], ranked_ids)

    def test_short_stratum_terminates_without_partial_selection(self) -> None:
        value = pool()
        target = STRATA[0]
        kept = 0
        for row in value["clusters"]:
            if row["stratum"] == target:
                kept += 1
                row["eligible"] = kept < QUOTAS[target]
        result = select(encoded(value), ENTROPY_A)
        self.assertEqual(result["status"], "NO_ELIGIBLE_BENCHMARK")
        self.assertEqual(result["selected_clusters"], [])
        target_evidence = next(row for row in result["strata"] if row["stratum"] == target)
        self.assertFalse(target_evidence["quota_satisfied"])

    def test_duplicate_cluster_or_identity_is_rejected(self) -> None:
        value = pool()
        value["clusters"][1]["cluster_id"] = value["clusters"][0]["cluster_id"]
        with self.assertRaisesRegex(ValueError, "duplicate cluster_id"):
            select(encoded(value), ENTROPY_A)
        value = pool()
        value["clusters"][1]["identity_sha256"] = value["clusters"][0]["identity_sha256"]
        with self.assertRaisesRegex(ValueError, "duplicate identity"):
            select(encoded(value), ENTROPY_A)

    def test_empty_randomness_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "64 lowercase"):
            select(encoded(pool()), "")
        with self.assertRaisesRegex(ValueError, "64 lowercase"):
            select(encoded(pool()), ("ab" * 32).upper())

    def test_precontamination_pool_is_rejected(self) -> None:
        value = pool()
        del value["contamination"]
        with self.assertRaisesRegex(ValueError, "pool.contamination"):
            select(encoded(value), ENTROPY_A)

    def test_ineligible_unclassified_row_is_accepted(self) -> None:
        value = pool()
        value["clusters"][0]["eligible"] = False
        value["clusters"][0]["stratum"] = None
        result = select(encoded(value), ENTROPY_A)
        self.assertEqual(result["status"], "SELECTED")

    def test_exact_pool_bytes_are_recorded(self) -> None:
        raw_a = encoded(pool())
        raw_b = json.dumps(pool(), separators=(",", ":")).encode()
        a = select(raw_a, ENTROPY_A)
        b = select(raw_b, ENTROPY_A)
        self.assertNotEqual(a["pool"]["file_sha256"], b["pool"]["file_sha256"])
        self.assertEqual(a["pool"]["canonical_sha256"], b["pool"]["canonical_sha256"])


if __name__ == "__main__":
    unittest.main()
