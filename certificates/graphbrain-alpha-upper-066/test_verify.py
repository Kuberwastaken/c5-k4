import math
import unittest
from verify import verify, simple_witness


class TestCertificate(unittest.TestCase):
    def test_campaign_witness(self):
        result=verify(); self.assertEqual(result['alpha'],2)
        self.assertLess(result['rhs'],0.397); self.assertGreater(result['margin'],1.60)
    def test_simple_witness(self):
        result=simple_witness(); self.assertEqual(result['average_distance'],37/36)
        self.assertLess(result['rhs'],-2.40)
    def test_named_controls(self):
        # Closed-form values: Petersen (a=4, avg=5/3,sigma2=6), K3,3
        # (a=3,avg=7/5,sigma2=6), cube (a=4,avg=12/7,sigma2=6),
        # Heawood (a=7,avg=25/13,sigma2=6).
        for alpha,avg,sigma in [(4,5/3,6),(3,7/5,6),(4,12/7,6),(7,25/13,6)]:
            rhs=math.exp(math.cosh(avg))-math.tan(sigma)
            self.assertLessEqual(alpha,rhs+1e-6)

if __name__=='__main__': unittest.main()
