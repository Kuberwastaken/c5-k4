from fractions import Fraction
import unittest
from verify import database_gate, verify, simple_witness, windmill


class TestCertificate(unittest.TestCase):
    def test_carrier(self):
        result=verify(4); self.assertEqual(result['order'],20)
        self.assertEqual(result['rhs'],str(Fraction(4,3)))
        self.assertEqual(result['margin'],str(Fraction(2,3)))
    def test_family_threshold(self):
        for m in range(4,20): verify(m)
    def test_simple_witness(self):
        result=simple_witness(); self.assertEqual(result['graph6'],'H~}CKMF')
        self.assertEqual(result['margin'],str(Fraction(2,3)))
    def test_windmill_family(self):
        for s in range(4,12):
            for t in range(2,8):
                if Fraction(t)>Fraction(4,s-2): windmill(s,t)
    def test_database_gate(self):
        gate=database_gate()
        self.assertEqual(gate['connected_atlas_total'],995)
        self.assertEqual(gate['applicable_nonzero_denominator'],58)
        self.assertEqual(gate['zero_denominator_vacuous_holds'],937)
        self.assertEqual(gate['violations'],0)

if __name__=='__main__': unittest.main()
