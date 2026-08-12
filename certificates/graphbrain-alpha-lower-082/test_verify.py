import unittest

from verify import GUARD, certify, rhs


class CertificateTest(unittest.TestCase):
    def test_complete_graph_gate_through_ten(self):
        for n in range(2, 11):
            bound, raw = rhs(n)
            self.assertGreaterEqual(1 + GUARD, bound, (n, raw, bound))

    def test_k11_and_carrier(self):
        result = certify()
        self.assertEqual([4, 3], [w["rhs"] for w in result["witnesses"]])
        self.assertEqual([1, 2], [w["independence_number"] for w in result["witnesses"]])


if __name__ == "__main__":
    unittest.main()
