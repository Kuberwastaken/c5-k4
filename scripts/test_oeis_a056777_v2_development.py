"""Target-free constructor, algebra, transaction, and mutation tests for v2."""
from __future__ import annotations

import hashlib, itertools, json, pathlib, signal, tempfile, unittest
from types import SimpleNamespace
from unittest import mock

import prepare_oeis_a056777_v2_gate as prep
import search_oeis_a056777_v2 as search
import verify_oeis_a056777_v2_candidate as independent


class V2FreezeTests(unittest.TestCase):
    def test_frozen_caps_ranks_and_orientations(self):
        self.assertEqual((prep.M["internal_seconds"],prep.M["external_search_seconds"],prep.M["external_verify_seconds"]),(48,54,60))
        self.assertEqual((prep.M["r_rank_first"],prep.M["r_rank_last"]),(385,640))
        self.assertEqual((prep.M["block_prime_rank_first"],prep.M["block_prime_rank_last"]),(1,640))
        self.assertEqual(set(prep.M["arms"]),{"REPEATED_LOWER","REPEATED_UPPER"})
        self.assertEqual(prep.M["prior_freeze"]["repeated_power_base_rank_last"],384)

    def test_exact_path_prs_are_classified_without_claiming_path_untouched(self):
        status=json.loads((prep.HERE/"source-status-attestation.json").read_text())
        self.assertEqual(status["audited_at_utc"],"2026-08-14T17:03:05Z")
        maintenance=status["open_exact_path_maintenance_prs"]
        self.assertEqual(maintenance["numbers"],[3691,4025,4356,4428])
        self.assertEqual(maintenance["classification"],"NON_RESOLVING_AUXILIARY_MAINTENANCE")
        self.assertIn("target declaration",maintenance["rationale"])
        self.assertNotIn("path untouched",maintenance["rationale"].lower())
        self.assertEqual((status["observed_upstream_main"],status["formal_conjectures_blob_sha256"]),("05ea0345d09375efac830fac93bf083b654e317e","2539ce34a7417a5b482d3c6f21a8327198e4890df7f67e6458a522293b1d099c"))

    def test_independent_prime_and_semiprime_indexes(self):
        left=search.first_primes(640);right=independent.independently_sieve(640)
        self.assertEqual(left,right)
        blocks,products=search.semiprime_index(left);pairs,other_products=independent.build_pairs(right)
        self.assertEqual(len(blocks),640*639//2);self.assertEqual(products,other_products)
        self.assertEqual([(x.product,x.t_rank,x.u_rank,x.t,x.u) for x in blocks],list(pairs))

    def test_formulas_8_9_10_and_stop_order_are_independent(self):
        primes=search.first_primes(18)
        with mock.patch.dict(search.M,{"value_minimum":1,"value_maximum":10**9}),mock.patch.dict(independent.M,{"value_minimum":1,"value_maximum":10**9}):
            for arm in search.M["arms"]:
                for r in primes[4:10]:
                    for i,j in itertools.combinations(range(12),2):
                        block=search.Block(primes[i]*primes[j],i+1,j+1,primes[i],primes[j])
                        pair=independent.PrimePair(block.product,block.t_rank,block.u_rank,block.t,block.u)
                        self.assertEqual(search.evaluate(arm,r,block),independent.independent_result(arm,r,pair))

    def test_denominator_window_is_complete_on_synthetic_band(self):
        """Flat comparison is intentionally below 10^12, never the target."""
        primes=search.first_primes(24);blocks,_=search.semiprime_index(primes);qmax=max(x.product for x in blocks)
        patch={"value_minimum":10_001,"value_maximum":1_000_000}
        with mock.patch.dict(search.M,patch),mock.patch.dict(independent.M,patch):
            for arm in search.M["arms"]:
                for r in primes[6:18]:
                    low,high=search.denominator_window(arm,r,primes,qmax)
                    self.assertEqual((low,high),independent.window(arm,r,primes,qmax))
                    for block in blocks:
                        outcome=search.evaluate(arm,r,block)
                        if outcome.get("p",0)>0 and outcome.get("n") is not None and patch["value_minimum"]<=outcome["n"]<=patch["value_maximum"]:
                            self.assertLessEqual(low,block.product);self.assertLessEqual(block.product,high)

    def test_window_bound_is_strict_algebraically(self):
        primes=search.first_primes(640);qmax=primes[-1]*primes[-2]
        for arm in search.M["arms"]:
            for rank in range(385,641):
                r=primes[rank-1];low,high=search.denominator_window(arm,r,primes,qmax);center=2*r*r
                self.assertLessEqual(low,center);self.assertGreaterEqual(high,center)
                # width=floor(N_bound/p_min)+1 is deliberately strict.
                self.assertGreater(high-center,0)

    def test_exact_prior_coordinate_skip(self):
        with mock.patch.dict(search.M,{"value_minimum":1}),mock.patch.dict(independent.M,{"value_minimum":1}):
            self.assertTrue(search.prior_squarefree_coordinate(1,2,2,3,5))
            self.assertTrue(independent.is_old_squarefree(independent.PrimePair(6,1,2,2,3),5))
            self.assertFalse(search.prior_squarefree_coordinate(97,98,509,521,523))

    def test_hash_chain_mutation_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path=pathlib.Path(directory)/"ledger.jsonl";ledger=search.Ledger(path)
            ledger.append(search.progress("1"*40,"REPEATED_LOWER",0,0,None,None,{name:0 for name in search.STOP_NAMES}));ledger.close()
            rows,digest=independent.chain(path,"1"*40,"REPEATED_LOWER",0);self.assertEqual(digest,rows[0]["row_sha256"])
            path.write_text(path.read_text().replace('"visited":0','"visited":1'))
            with self.assertRaisesRegex(ValueError,"hash-chain"):independent.chain(path,"1"*40,"REPEATED_LOWER",0)

    def test_ledger_requires_exact_ascii_newline_and_canonical_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            root=pathlib.Path(directory);original=root/"original.jsonl";ledger=search.Ledger(original)
            ledger.append(search.progress("1"*40,"REPEATED_LOWER",0,0,None,None,{name:0 for name in search.STOP_NAMES}));ledger.close();raw=original.read_bytes()
            missing=root/"missing-newline.jsonl";missing.write_bytes(raw[:-1])
            with self.assertRaisesRegex(ValueError,"ending in newline"):independent.chain(missing,"1"*40,"REPEATED_LOWER",0)
            whitespace=root/"leading-whitespace.jsonl";whitespace.write_bytes(b" "+raw)
            with self.assertRaisesRegex(ValueError,"byte-canonical"):independent.chain(whitespace,"1"*40,"REPEATED_LOWER",0)
            partial=root/"partial-row.jsonl";partial.write_bytes(raw[:-8]+b"\n")
            with self.assertRaisesRegex(ValueError,"malformed ledger physical row"):independent.chain(partial,"1"*40,"REPEATED_LOWER",0)
            extra=root/"extra-key.jsonl";row=json.loads(raw);row.pop("row_sha256");row["unexpected"]=True
            body=json.dumps(row,sort_keys=True,separators=(",",":"));row["row_sha256"]=hashlib.sha256(body.encode("ascii")).hexdigest()
            extra.write_text(json.dumps(row,sort_keys=True,separators=(",",":"))+"\n",encoding="ascii")
            with self.assertRaisesRegex(ValueError,"row key drift"):independent.chain(extra,"1"*40,"REPEATED_LOWER",0)

    def test_replay_rejects_early_candidate_followed_by_later_state(self):
        zero_counts={name:0 for name in independent.STOPS};survivor_counts=dict(zero_counts);survivor_counts["SURVIVOR"]=1
        final_counts=dict(survivor_counts);final_counts["K_SIGN"]=1
        early_coordinate={"synthetic":0};later_coordinate={"synthetic":1}
        early={"stop":"SURVIVOR"};later={"stop":"K_SIGN"}
        terminal={"arm":"REPEATED_LOWER","shard":0,"visited":2,"tuple_domain_only":True,
                  "last_coordinate":later_coordinate,"last_outcome":later,"counts":final_counts,"terminal_reason":"CERTIFICATE_FOUND"}
        initial={"schema":"oeis-a056777-v2-progress-v1","campaign_commit":"1"*40,"arm":"REPEATED_LOWER","shard":0,
                 "visited":0,"last_coordinate":None,"last_outcome":None,"counts":zero_counts}
        with mock.patch.object(independent,"independent_tuples",return_value=iter([(early_coordinate,early),(later_coordinate,later)])):
            with self.assertRaisesRegex(ValueError,"candidate final-state/first-survivor drift"):
                independent.replay(terminal,[initial],{"coordinate":early_coordinate})

    def test_sigalrm_deferred_through_atomic_transition(self):
        previous=signal.getsignal(signal.SIGALRM);state=[];signal.signal(signal.SIGALRM,search.alarm_handler)
        try:
            with self.assertRaises(search.Deadline):
                with search.block_alarm():state.append("committed");signal.raise_signal(signal.SIGALRM)
            self.assertEqual(state,["committed"])
        finally:signal.signal(signal.SIGALRM,previous)

    def _args(self,root:pathlib.Path):
        gate=root/"gate";gate.mkdir();(gate/"gate-attestation.json").write_text("{}\n")
        return SimpleNamespace(arm="REPEATED_LOWER",shard=0,campaign_commit="1"*40,gate_bundle=gate,
                               ledger=root/"ledger.jsonl",terminal=root/"terminal.json",certificate=root/"certificate.json")

    def test_worker_error_is_typed_and_hashed(self):
        def broken(_arm,_shard):raise RuntimeError("synthetic worker failure");yield
        with tempfile.TemporaryDirectory() as directory:
            args=self._args(pathlib.Path(directory))
            with mock.patch.object(search,"verify"),mock.patch.object(search,"tuples",broken):self.assertEqual(search.run(args),21)
            terminal=json.loads(args.terminal.read_text());self.assertEqual((terminal["terminal_reason"],terminal["certificate_present"]),("WORKER_ERROR",False))
            independent.validate_error(terminal["terminal_reason"],terminal["worker_error"])

    def test_certificate_rename_failure_leaves_prior_prefix(self):
        coordinate={"r":5,"t":2,"u":3};outcome={"stop":"SURVIVOR","n":1,"p":7,"q":11}
        with tempfile.TemporaryDirectory() as directory:
            args=self._args(pathlib.Path(directory));real=search.atomic_json
            def fail_certificate(path,value):
                if path==args.certificate:raise OSError("synthetic certificate rename failure")
                return real(path,value)
            with mock.patch.object(search,"verify"),mock.patch.object(search,"tuples",return_value=iter([(coordinate,outcome)])),mock.patch.object(search,"make_certificate",return_value={"schema":"synthetic"}),mock.patch.object(search,"atomic_json",side_effect=fail_certificate):
                self.assertEqual(search.run(args),21)
            terminal=json.loads(args.terminal.read_text());self.assertEqual((terminal["terminal_reason"],terminal["visited"],terminal["certificate_present"]),("WORKER_ERROR",0,False));self.assertFalse(args.certificate.exists())

    def test_no_ledger_append_occurs_after_durable_certificate(self):
        coordinate={"r":5,"t":2,"u":3};outcome={"stop":"SURVIVOR","n":1,"p":7,"q":11};calls=0;real_append=search.Ledger.append
        def forbid_second(ledger,payload):
            nonlocal calls;calls+=1
            if calls==2:raise AssertionError("ledger append attempted after durable certificate")
            return real_append(ledger,payload)
        with tempfile.TemporaryDirectory() as directory:
            args=self._args(pathlib.Path(directory))
            with mock.patch.object(search,"verify"),mock.patch.object(search,"tuples",return_value=iter([(coordinate,outcome)])),mock.patch.object(search,"make_certificate",return_value={"schema":"synthetic"}),mock.patch.object(search.Ledger,"append",new=forbid_second):
                self.assertEqual(search.run(args),0)
            terminal=json.loads(args.terminal.read_text());self.assertEqual((terminal["terminal_reason"],terminal["visited"],terminal["certificate_present"]),("CERTIFICATE_FOUND",1,True));self.assertTrue(args.certificate.exists());self.assertEqual(calls,1)
            independent.validate_error(terminal["terminal_reason"],terminal["worker_error"])
            rows,_=independent.chain(args.ledger,args.campaign_commit,args.arm,args.shard);self.assertEqual([x["visited"] for x in rows],[0])
            # The terminal verifier validates the durable candidate and replays
            # the intentionally preceding ledger prefix.
            with mock.patch.object(independent,"verify"),mock.patch.object(independent,"candidate",return_value={"coordinate":coordinate}) as candidate_check,mock.patch.object(independent,"replay") as prefix_replay:
                independent.terminal(args.ledger,args.terminal,args.certificate,args.gate_bundle,args.campaign_commit,args.arm,args.shard)
                candidate_check.assert_called_once();prefix_replay.assert_called_once()
            mutated=pathlib.Path(directory)/"terminal-extra-key.json";document=json.loads(args.terminal.read_text());document["unexpected"]=True;mutated.write_text(json.dumps(document)+"\n")
            with mock.patch.object(independent,"verify"):
                with self.assertRaisesRegex(ValueError,"terminal key drift"):
                    independent.terminal(args.ledger,mutated,args.certificate,args.gate_bundle,args.campaign_commit,args.arm,args.shard)


if __name__=="__main__":unittest.main()
