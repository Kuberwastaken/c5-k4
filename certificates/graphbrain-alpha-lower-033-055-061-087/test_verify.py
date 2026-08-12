import unittest
import verify


class CertificateTests(unittest.TestCase):
    def test_database_gate(self):
        self.assertEqual(verify.verify_gate()[0], 995)

    def test_witnesses(self):
        results = verify.verify_witnesses()
        self.assertEqual(set(results), {33, 55, 61, 87})


if __name__ == "__main__":
    unittest.main()

