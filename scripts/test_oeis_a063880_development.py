"""Constructor and mutation tests; no frozen A063880 arm is executed."""
import hashlib, json, pathlib, tempfile, unittest
from fractions import Fraction
from unittest import mock

import prepare_oeis_a063880_gate as prep
import search_oeis_a063880 as search
import verify_oeis_a063880_candidate as independent

class FreezeTests(unittest.TestCase):
    def test_caps_and_historical_exclusion(self):
        self.assertEqual((prep.M["shards"],prep.M["internal_seconds"],prep.M["external_seconds"],prep.M["child_seconds"]),(24,54,60,4))
        self.assertEqual(prep.M["historical_exclusion_upper_exclusive"],10**18)
        self.assertEqual(prep.M["universe"]["minimum_core"],10**18)

    def test_arms_are_disjoint_by_maximum_prime(self):
        intervals=[]
        for name,spec in prep.M["arms"].items():
            lo,hi=spec["maximum_prime_min"],spec["maximum_prime_max"]
            primes=spec["primes"]
            self.assertEqual(primes,sorted(set(primes)))
            self.assertTrue(all(p>=2 and all(p%d for d in range(2,int(p**0.5)+1)) for p in primes))
            in_band=[p for p in primes if lo<=p<=hi]
            self.assertEqual((min(in_band),max(in_band)),(lo,hi))
            intervals.append((lo,hi))
        for i,a in enumerate(intervals):
            for b in intervals[i+1:]: self.assertTrue(a[1]<b[0] or b[1]<a[0])

    def test_exact_euler_identity_and_primitive_core_control(self):
        factors=((2,2),(3,3))
        self.assertEqual(search.euler_factor(2,2)*search.euler_factor(3,3),2)
        self.assertEqual(search.sigma_usigma(factors),(280,140))
        self.assertTrue(search.is_primitive(factors))
        self.assertEqual(prep.primitive_core({2:2,3:3,5:1}),108)

    def test_synthetic_mitm_constructor_order(self):
        states=list(search.states([2,3],[2],2,1000))
        self.assertEqual(states[0],(1,Fraction(1),()))
        self.assertEqual([row[2] for row in states],[(),((3,2),),((2,2),),((2,2),(3,2))])

    def test_historical_values_cannot_be_candidate(self):
        factors=((2,2),(3,3))
        self.assertIsNone(search.candidate_document("CATALOGUE",0,"1"*40,"2"*64,factors))

    def test_ledger_fsync_and_chain_mutation(self):
        with tempfile.TemporaryDirectory() as td, mock.patch.object(search.os,"fsync") as fsync:
            path=pathlib.Path(td)/"ledger.jsonl"; ledger=search.Ledger(path)
            ledger.append({"schema":"oeis-a063880-match-row-v1","campaign_commit":"1"*40,"arm":"CATALOGUE","shard":0,"left_ordinal":0}); ledger.close()
            self.assertEqual(fsync.call_count,1)
            rows,last=independent.verify_chain(path,"1"*40,"CATALOGUE",0); self.assertEqual(len(rows),1); self.assertEqual(last,rows[0]["row_sha256"])
            path.write_text(path.read_text().replace('"left_ordinal":0','"left_ordinal":1'))
            with self.assertRaisesRegex(ValueError,"ledger chain"): independent.verify_chain(path,"1"*40,"CATALOGUE",0)

    def test_gate_chunk_detects_mutated_value(self):
        good=prep.check_chunk([(1,108)],0,1); self.assertEqual(good["bad_indices"],[])
        bad=prep.check_chunk([(1,109)],0,1); self.assertEqual(bad["bad_indices"],[1])

    def test_gate_rejects_repeated_or_semantically_fabricated_chunks(self):
        rows=[(i+1,108) for i in range(251)]
        with tempfile.TemporaryDirectory() as td:
            bundle=pathlib.Path(td); (bundle/"chunks").mkdir(); receipts=[]
            for start,end in ((0,250),(250,251)):
                value=prep.check_chunk(rows,start,end); path=bundle/f"chunks/{start:05d}-{end:05d}.json"
                prep.atomic_json(path,value); receipts.append({"path":str(path.relative_to(bundle)),"sha256":prep.sha(path),**value})
            prep.verify_chunk_set(rows,receipts,bundle)
            with self.assertRaisesRegex(ValueError,"coverage order/gap"):
                prep.verify_chunk_set(rows,[receipts[0],receipts[0]],bundle)
            fabricated=[dict(x) for x in receipts]; fabricated[1]["rows"]=2
            with self.assertRaisesRegex(ValueError,"semantic receipt"):
                prep.verify_chunk_set(rows,fabricated,bundle)

    def test_terminal_semantic_replay_rejects_duplicate_and_mutated_rows(self):
        synthetic={"primes":[2,3],"exponents":[2],"maximum_factors":2,"maximum_prime_min":2,"maximum_prime_max":3}
        progress=[{"phase":"BUILD_RIGHT_COMPLETE","right_states":2,"last_right_n":9,"last_right_ratio":[13,10]}]
        match={"left_ordinal":0,"left_n":1,"left_ratio":[1,1],"complement":[2,1],"right_matches":0}
        terminal={"right_states":2,"left_states_seen":2,"left_states_owned":1,"exact_ratio_matches":0,"terminal_reason":"DOMAIN_EXHAUSTED"}
        with mock.patch.dict(independent.M["arms"],{"CATALOGUE":synthetic}):
            independent.validate_search_evidence(progress,[match],terminal,"CATALOGUE",0,None)
            with self.assertRaisesRegex(ValueError,"gap/duplicate/order"):
                independent.validate_search_evidence(progress,[match,match],terminal,"CATALOGUE",0,None)
            bad=dict(match); bad["complement"]=[3,1]
            with self.assertRaisesRegex(ValueError,"semantic drift"):
                independent.validate_search_evidence(progress,[bad],terminal,"CATALOGUE",0,None)
            incomplete=dict(terminal); incomplete["left_states_seen"]=1
            with self.assertRaisesRegex(ValueError,"false domain exhaustion"):
                independent.validate_search_evidence(progress,[match],incomplete,"CATALOGUE",0,None)

    def test_certificate_must_bind_terminal_arm_and_shard(self):
        independent.bind_certificate({"arm":"CATALOGUE","shard":3},"CATALOGUE",3)
        with self.assertRaisesRegex(ValueError,"arm-shard"):
            independent.bind_certificate({"arm":"GENERIC","shard":3},"CATALOGUE",3)
        with self.assertRaisesRegex(ValueError,"arm-shard"):
            independent.bind_certificate({"arm":"CATALOGUE","shard":4},"CATALOGUE",3)

    def test_candidate_coordinate_rejects_wrong_shard_and_early_attachment(self):
        synthetic={"primes":[2,3],"exponents":[2,3],"maximum_factors":2,"maximum_prime_min":2,"maximum_prime_max":3}
        factors=((2,2),(3,3)); certificate={"factors":[[2,2],[3,3]]}
        progress=[{"phase":"BUILD_RIGHT_COMPLETE","right_states":3,"last_right_n":9,"last_right_ratio":[13,10]}]
        match={"left_ordinal":2,"left_n":4,"left_ratio":[7,5],"complement":[10,7],"right_matches":1}
        terminal={"right_states":3,"left_states_seen":3,"left_states_owned":1,"exact_ratio_matches":1,"terminal_reason":"CERTIFICATE_FOUND"}
        with mock.patch.dict(independent.M["arms"],{"CATALOGUE":synthetic}):
            self.assertEqual(independent.bind_candidate_to_shard("CATALOGUE",factors,2),2)
            with self.assertRaisesRegex(ValueError,"claimed shard"):
                independent.bind_candidate_to_shard("CATALOGUE",factors,3)
            independent.validate_search_evidence(progress,[match],terminal,"CATALOGUE",2,certificate)
            early=dict(terminal); early["left_states_seen"]=2; early["left_states_owned"]=0
            with self.assertRaisesRegex(ValueError,"match-prefix|owned left ordinal"):
                independent.validate_search_evidence(progress,[],early,"CATALOGUE",2,certificate)

    def test_source_status_tokens_are_current(self):
        source=(pathlib.Path(__file__).parents[1]/"results/expansion/live-search-2026-08-14/oeis-a063880-development/source-status-attestation.json")
        value=json.loads(source.read_text()); self.assertEqual(value["formal_conjectures_status"],"research open")
        self.assertIn("10^18",value["prior_result"])

if __name__=="__main__": unittest.main()
