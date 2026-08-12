#!/usr/bin/env python3
"""Regression tests for the WoW I #724 executable certificate."""

import unittest

import verify


class CertificateTests(unittest.TestCase):
    def test_closed_family(self):
        verify.check_family()

    def test_database_gate(self):
        self.assertEqual(verify.check_gate(), (996, 21))

    def test_carrier_complement(self):
        lhs, alpha, _, nonnegative = verify.value(verify.h_graph(4))
        self.assertAlmostEqual(lhs, 10.0, places=6)
        self.assertEqual(alpha, 8)
        self.assertEqual(nonnegative, 18)
        self.assertGreater(lhs, alpha + verify.EPS)


if __name__ == "__main__":
    unittest.main()
