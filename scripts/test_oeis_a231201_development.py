"""Constructor/control tests only; no A231201 candidate or frozen arm runs."""
import json, math, pathlib, tempfile, time, unittest
from unittest import mock
import oeis_a231201_common as common
import prepare_oeis_a231201_gate as gate
import search_oeis_a231201 as search
import verify_oeis_a231201_coverage as independent

class FreezeTests(unittest.TestCase):
    def test_exact_prime_universe_orders_and_period(self):
        self.assertEqual(len(common.M["primes"]),55)
        self.assertEqual(common.M["primes"],[n for n in range(2,258) if common.is_prime_trial(n)])
        table=common.order_table(); self.assertEqual(table[0],(2,1,2))
        for q,o,m in table[1:]:
            self.assertEqual(pow(2,o,q),1); self.assertTrue(all(pow(2,k,q)!=1 for k in range(1,o))); self.assertEqual(m,q*o)
        self.assertEqual(common.combined_period(),int(common.M["combined_period"]))

    def test_positive_class_equivalence_including_q2(self):
        for q,o,m in common.order_table():
            for r in range(m):
                expected=common.periodic_value(q,r)
                for k in (1,2,7):
                    x=common.positive_representative(r,m)+k*m
                    self.assertEqual(common.direct_value(q,x),expected)
        self.assertEqual(common.periodic_value(2,0),0)
        self.assertNotEqual(common.direct_value(2,0),common.periodic_value(2,0))

    def test_seed_and_assignment_partition(self):
        seed=range(common.M["initial_exponents"]["lo"],common.M["initial_exponents"]["hi"]+1)
        self.assertEqual((seed.start,seed.stop,len(seed)),(1,4097,4096)); self.assertNotIn(0,seed)
        cells=[tuple(sorted(common.shard_fixed(arm,shard).items())) for arm in common.M["partition"]["arms"] for shard in common.M["partition"]["shards"]]
        self.assertEqual(len(cells),len(set(cells)),6)
        self.assertEqual(set(cells),{((2,a2),(3,a3)) for a2 in range(2) for a3 in range(3)})

    def test_gate_primality_is_guarded_and_vocabulary_separate(self):
        self.assertTrue(gate.prime_test(4722366482869645213951))
        with self.assertRaisesRegex(ValueError,"outside deterministic"):
            gate.prime_test(gate.MR_LIMIT)
        source=pathlib.Path(gate.__file__).read_text()
        self.assertIn('"GATE_CHUNK_EXHAUSTED"',source)
        self.assertNotIn('status="DOMAIN_EXHAUSTED"',source)

    def test_generalized_crt_constructor(self):
        self.assertEqual(common.crt_pair(1,2,2,3),(5,6))
        self.assertIsNone(common.crt_pair(0,2,1,2))

    def test_ledger_hash_chain_and_fsync(self):
        with tempfile.TemporaryDirectory() as td, mock.patch.object(common.os,"fsync") as fsync:
            path=pathlib.Path(td)/"ledger.jsonl"; ledger=common.Ledger(path); first=ledger.append({"x":1}); ledger.append({"x":2}); ledger.close()
            rows=[json.loads(x) for x in path.read_text().splitlines()]
            self.assertEqual(rows[0]["previous_row_sha256"],common.ZERO); self.assertEqual(rows[1]["previous_row_sha256"],first); self.assertEqual(fsync.call_count,2)

    def test_two_coverage_implementations_on_synthetic_prefix(self):
        assignment={q:0 for q in common.M["primes"]}
        synthetic=[(2,1,2),(3,2,6)]
        with mock.patch.object(independent,"order_table",return_value=synthetic), tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td)
            one=common.Ledger(p/"a.jsonl"); a=independent.refine(assignment,time.monotonic()+2,one); one.close()
            two=common.Ledger(p/"b.jsonl"); b=independent.independent_coverage(assignment,time.monotonic()+2,two); two.close()
            self.assertEqual(a["status"],b["status"])

    def test_terminal_vocabulary_is_fail_closed(self):
        source=pathlib.Path(search.__file__).read_text()
        self.assertIn('"SOLVER_INFEASIBLE_UNVERIFIED"',source)
        self.assertNotIn('"NO_COMPLETE_COVER"',source)
        verifier=pathlib.Path(independent.__file__).read_text()
        self.assertIn('"VERIFICATION_FAILED_UNCOVERED_CLASS"',verifier)

if __name__=="__main__": unittest.main()
