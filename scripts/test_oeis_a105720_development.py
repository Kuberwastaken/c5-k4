"""Constructor-only tests: no frozen target arm is executed."""
import json, math, pathlib, tempfile, unittest
from unittest import mock

import prepare_oeis_a105720_gate as prep
import search_oeis_a105720 as search
import verify_oeis_a105720_candidate as independent

class FreezeTests(unittest.TestCase):
    def test_constants_and_caps(self):
        self.assertEqual(prep.MANIFEST["shards"],24)
        self.assertEqual(prep.MANIFEST["internal_seconds"],54)
        self.assertEqual(prep.MANIFEST["external_seconds"],60)
        self.assertLessEqual(prep.MANIFEST["child_seconds"],4)

    def test_domains_are_exact_disjoint_and_complete(self):
        cat=[n for s in range(24) for n in search.arm_values("CATALOGUE",s)]
        wall=[n for s in range(24) for n in search.arm_values("WALL_NAVIGATION",s)]
        generic=[n for s in range(24) for n in search.arm_values("GENERIC",s)]
        self.assertEqual(set(cat),set(range(21,20021)))
        self.assertEqual(set(wall),set(range(20021,120021)))
        self.assertEqual(len(generic),96000); self.assertEqual(len(set(generic)),96000)
        self.assertFalse(set(cat)&set(wall)); self.assertFalse(set(cat)&set(generic)); self.assertFalse(set(wall)&set(generic))
        for arm,values in (("CATALOGUE",cat),("WALL_NAVIGATION",wall),("GENERIC",generic)):
            for s in range(24):
                self.assertTrue(all(independent.belongs(arm,s,n) for n in search.arm_values(arm,s)))

    def test_affine_multiplier_is_invertible(self):
        a=prep.MANIFEST["arms"]["GENERIC"]
        self.assertEqual(math.gcd(a["multiplier"],a["width"]),1)

    def test_residue_screen_has_no_false_negative_for_squares(self):
        for r in range(500): self.assertTrue(search.square_residue(r*r))

    def test_prime_constructor_and_source_controls(self):
        primes=prep.sieve(9000)
        for n,value in prep.MANIFEST["controls"].items():
            self.assertEqual(prep.window_sum(primes,int(n)),value)

    def test_ledger_chain_and_fsync(self):
        with tempfile.TemporaryDirectory() as td, mock.patch.object(search.os,"fsync") as fsync:
            path=pathlib.Path(td)/"ledger.jsonl"; ledger=search.Ledger(path)
            first=ledger.append({"x":1}); second=ledger.append({"x":2}); ledger.close()
            rows=[json.loads(x) for x in path.read_text().splitlines()]
            self.assertEqual(rows[0]["previous_row_sha256"],"0"*64); self.assertEqual(rows[0]["row_sha256"],first)
            self.assertEqual(rows[1]["previous_row_sha256"],first); self.assertEqual(rows[1]["row_sha256"],second)
            self.assertEqual(fsync.call_count,2)

    def test_independent_chain_replay_and_mutation_rejection(self):
        commit="1"*40
        with tempfile.TemporaryDirectory() as td:
            path=pathlib.Path(td)/"ledger.jsonl"; ledger=search.Ledger(path)
            ledger.append({"schema":"oeis-a105720-row-v1","campaign_commit":commit,"arm":"CATALOGUE","shard":0,"screen_pass":True}); ledger.close()
            self.assertEqual(independent.verify_chain(path,commit,"CATALOGUE",0)[1:4],(1,1,1))
            text=path.read_text(); path.write_text(text.replace('"screen_pass":true','"screen_pass":false'))
            with self.assertRaisesRegex(ValueError,"ledger chain"): independent.verify_chain(path,commit,"CATALOGUE",0)

    def test_independent_semantic_row_and_completion_rejection(self):
        commit="1"*40; gate_sha="2"*64; primes=prep.sieve(100)
        # Exercise semantics only on the source-published n=3 control.  The
        # temporary one-point arm is synthetic and never touches a frozen lane.
        n=3; value=prep.MANIFEST["controls"][str(n)]; root=math.isqrt(value)
        row={"schema":"oeis-a105720-row-v1","campaign_commit":commit,"source_commit":prep.MANIFEST["formal_conjectures"]["commit"],"gate_attestation_sha256":gate_sha,"arm":"CATALOGUE","shard":0,"n":n,"a_n":value,"screen_pass":True,"exact_square":root*root==value,"nearest_square_distance":min(value-root*root,(root+1)**2-value)}
        with mock.patch.dict(independent.M["arms"]["CATALOGUE"],{"lo":3,"hi":3}), tempfile.TemporaryDirectory() as td:
            path=pathlib.Path(td)/"ledger.jsonl"; ledger=search.Ledger(path); ledger.append(row); ledger.close()
            self.assertEqual(independent.verify_chain(path,commit,"CATALOGUE",0,primes,gate_sha)[2:4],(1,1))
            bad=dict(row); bad["n"]=4; path2=pathlib.Path(td)/"bad.jsonl"; ledger=search.Ledger(path2); ledger.append(bad); ledger.close()
            with self.assertRaisesRegex(ValueError,"domain order"): independent.verify_chain(path2,commit,"CATALOGUE",0,primes,gate_sha)
        with self.assertRaisesRegex(ValueError,"false domain exhaustion"): independent.validate_completion("DOMAIN_EXHAUSTED",1,834,[],False)
        with self.assertRaisesRegex(ValueError,"final exact row"): independent.validate_completion("CERTIFICATE_FOUND",1,834,[{"exact_square":False}],True)

    def test_known_indices_can_never_be_candidate_shape(self):
        for n in prep.MANIFEST["known_square_indices"]: self.assertIn(n,{3,6,4072})
        self.assertFalse(independent.belongs("CATALOGUE",0,3))

if __name__=="__main__": unittest.main()
