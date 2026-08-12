import unittest

from verify import GUARD, certify, rhs


class CertificateTest(unittest.TestCase):
    def test_database_matching_numbers(self):
        # Any graph of order at most ten has matching number at most five.
        # The posted bound is at most one for every integer mu in [0,5], so
        # every nonempty connected graph in that database passes.
        for matching in range(6):
            bound, raw = rhs(matching)
            self.assertGreaterEqual(1 + GUARD, bound, (matching, raw, bound))

    def test_k28_and_carrier(self):
        result = certify()
        self.assertEqual([12, 12], [w["rhs"] for w in result["witnesses"]])
        self.assertEqual([1, 3], [w["independence_number"] for w in result["witnesses"]])


if __name__ == "__main__":
    unittest.main()
