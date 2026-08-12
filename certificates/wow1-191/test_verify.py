#!/usr/bin/env python3
"""Regression tests for the WoW-I #191 executable certificate."""

from fractions import Fraction
import unittest

import verify


class CertificateTests(unittest.TestCase):
    def test_t7_counterexample(self) -> None:
        result = verify.evaluate(7)
        self.assertEqual(result["order"], 21)
        self.assertEqual(result["size"], 105)
        self.assertEqual(result["clique_number"], 6)
        self.assertEqual(result["minimum_deficiency"], 20)
        self.assertEqual(result["sum_odd"], 210)
        self.assertEqual(result["sum_even"], 231)
        self.assertTrue(result["hypothesis_sum_odd_le_sum_even"])
        self.assertFalse(result["conjecture_holds"])
        self.assertGreater(20, Fraction(105, 6))

    def test_closed_forms_by_construction(self) -> None:
        for q in range(3, 11):
            result = verify.evaluate(q)
            for key, value in verify.expected(q).items():
                self.assertEqual(result[key], value, (q, key))

    def test_threshold_is_exact(self) -> None:
        for q in range(3, 7):
            result = verify.evaluate(q)
            self.assertFalse(
                result["hypothesis_sum_odd_le_sum_even"]
                and not result["conjecture_holds"]
            )
        for q in range(7, 11):
            result = verify.evaluate(q)
            self.assertTrue(result["hypothesis_sum_odd_le_sum_even"])
            self.assertFalse(result["conjecture_holds"])


if __name__ == "__main__":
    unittest.main()
