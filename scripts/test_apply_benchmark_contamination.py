#!/usr/bin/env python3
"""Regression tests for contamination application to the C0 pool."""

from __future__ import annotations

import unittest

import apply_benchmark_contamination as overlay


UPSTREAM = {"commit": "a" * 40, "tree": "b" * 40}


def pool_row(cluster_id: str, eligible: bool = True) -> dict:
    return {
        "cluster_id": cluster_id,
        "identity_sha256": "c" * 64,
        "path": "FormalConjectures/Test.lean",
        "module_blob_sha256": "e" * 64,
        "declarations": [{"name": "test"}],
        "eligible": eligible,
        "stratum": "FINITE_COMBINATORIAL" if eligible else None,
    }


def contamination_row(cluster_id: str, status: str) -> dict:
    return {
        "cluster_id": cluster_id,
        "identity_sha256": "f" * 64,
        "path": "FormalConjectures/Test.lean",
        "source_blob_sha256": "e" * 64,
        "declarations": [{"name": "test"}],
        "exposure_status": status,
        "exposure_basis": "test",
    }


class OverlayTests(unittest.TestCase):
    def test_eligibility_is_conjunction(self) -> None:
        pool = {"upstream": dict(UPSTREAM), "clusters": [pool_row("x")]}
        inventory = {
            "upstream": dict(UPSTREAM),
            "inventory_sha256": "d" * 64,
            "clusters": [contamination_row("x", "EXPOSED")],
        }
        result = overlay.apply_contamination(pool, inventory)
        self.assertFalse(result["clusters"][0]["eligible"])
        self.assertIsNone(result["clusters"][0]["stratum"])
        self.assertTrue(result["contamination"]["applied"])

    def test_cluster_set_mismatch_fails_closed(self) -> None:
        pool = {"upstream": dict(UPSTREAM), "clusters": [pool_row("x")]}
        inventory = {
            "upstream": dict(UPSTREAM),
            "inventory_sha256": "d" * 64,
            "clusters": [contamination_row("y", "UNEXPOSED")],
        }
        with self.assertRaisesRegex(ValueError, "cluster sets differ"):
            overlay.apply_contamination(pool, inventory)


if __name__ == "__main__":
    unittest.main()
