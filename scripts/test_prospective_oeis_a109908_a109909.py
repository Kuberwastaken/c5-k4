#!/usr/bin/env python3
"""Target-free and microfixture tests for the frozen A109908/A109909 lane."""
import inspect,json,math,pathlib,tempfile,unittest
import prospective_oeis_a109908_a109909 as search
import verify_oeis_a109908_a109909_artifacts as replay

class FreezeTests(unittest.TestCase):
    def test_caps_and_locked_target(self):
        self.assertEqual((search.M["internal_seconds"],search.M["external_search_seconds"],search.M["external_verify_seconds"]),(48,54,60))
        self.assertTrue(search.M["target_evaluation_requires_exact_campaign_commit"])
        with self.assertRaises(ValueError):search.exact_commit("main")

    def test_nat_safe_full_half_microfixtures(self):
        for n in range(1,21):
            half={k*(n-k)-1 for k in range(1,n//2+1)}
            full={k*(n-k)-1 for k in range(1,n)}
            self.assertEqual(half,full)
            for k in range(1,n):
                j=min(k,n-k);self.assertGreaterEqual(j,1);self.assertLessEqual(j,n//2)
                self.assertEqual(k*(n-k)-1,j*(n-j)-1)

    def test_congruence_hypotheses_root_pairing_and_properness(self):
        for q in search.M["construction"]["divisor_primes"]:
            self.assertGreater(q,1)
            for residue in range(q):
                rs=search.roots(q,residue)
                for k in rs:
                    self.assertEqual(math.gcd(k,q),1);self.assertIn(pow(k,-1,q),rs)
                    n=residue+5*q;self.assertEqual((k*(n-k)-1)%q,0)
        self.assertLess(max(search.M["construction"]["divisor_primes"]),search.M["candidate_n_minimum"]-2)

    def test_lcm_obstruction(self):
        primes=search.M["construction"]["divisor_primes"];q=math.lcm(*primes)
        self.assertEqual(q,search.M["construction"]["divisor_lcm"])
        self.assertGreater(q,search.M["candidate_n_maximum"]//2)
        depth=search.M["construction"]["profile_minimum_depth"]
        self.assertEqual(primes,[2,3,5,7,11,13,17,19,23,29,31,37,41,43])
        self.assertEqual(depth,10)
        self.assertGreater(math.prod(primes[:depth]),search.M["candidate_n_maximum"]//2)
        self.assertLessEqual(math.prod(primes[:depth-1]),search.M["candidate_n_maximum"]//2)
        for p in primes:self.assertEqual((q*(2*q-q)-1)%p,p-1)

    def test_modulus_two_even_arm(self):
        options=search.residue_masks(2,32)
        self.assertEqual([(residue,roots) for residue,roots,_ in options],[(0,(1,))])
        residue,roots,mask=options[0]
        self.assertEqual(residue,0);self.assertEqual(roots,(1,))
        self.assertTrue(all(bool(mask&(1<<(k-1)))==(k%2==1) for k in range(1,33)))

    def test_target_free_constructor_boundary(self):
        source=inspect.getsource(search.residue_masks)+inspect.getsource(search.frozen_profiles)
        for forbidden in ("coverage(","factorint(","candidate_n_minimum","representatives("):
            self.assertNotIn(forbidden,source)
        verifier_source=inspect.getsource(replay.frozen_profile_stream)
        self.assertNotIn("prospective_oeis",verifier_source)
        self.assertIn("selected-profile lcm obstruction",verifier_source)

    def test_compact_cover_and_escape_replay_microfixtures(self):
        profile={"ordinal":0,"depth":1,"crt_residue":2,"modulus":3,"selected_residues":[2],"root_classes":[{"q":3,"n_residue":2,"roots":[1]}]}
        old_search=search.M["construction"]["coverage_block_size"];old_replay=replay.M["construction"]["coverage_block_size"]
        try:
            search.M["construction"]["coverage_block_size"]=8;replay.M["construction"]["coverage_block_size"]=8
            complete,covered,k,digest=replay.cover_replay(8,profile,4)
            self.assertFalse(complete);self.assertEqual((covered,k),(1,2));self.assertEqual(len(digest),64)
        finally:
            search.M["construction"]["coverage_block_size"]=old_search;replay.M["construction"]["coverage_block_size"]=old_replay

    def test_exact_factor_replay(self):
        for n in (2,3,4,91,8051,99991):
            factors=search.factorint(n);self.assertTrue(replay.factor_ok(n,factors))

if __name__=="__main__":unittest.main()
