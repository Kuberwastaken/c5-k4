#!/usr/bin/env python3
"""Target-free constructors and adversarial freeze tests for A108569."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json
import pathlib
import tempfile
import time
import unittest
from types import SimpleNamespace
from unittest import mock

import prepare_oeis_a108569_gate as prep
import search_oeis_a108569 as search
import verify_oeis_a108569_candidate as independent


class A108569FreezeTests(unittest.TestCase):
    def test_caps_arms_and_literal_shape(self):
        self.assertEqual((prep.M["internal_seconds"],prep.M["external_search_seconds"],
                          prep.M["external_verify_seconds"]),(48,54,60))
        self.assertEqual(prep.M["shards"],24)
        self.assertEqual(set(prep.M["arms"]),{"CATALOGUE_LIFT_CONTROL","ODD_CORE_PROFILES","ODD_COLLISION_WALL"})
        card=json.loads((prep.HERE/"resolution-card.json").read_text())
        self.assertEqual(card["logical_class"],"FINITE_UNIVERSAL")
        self.assertIn("R(k)=phi(k+phi(k))-phi(k)",card["exact_residual"])
        self.assertEqual(card["semantic_candidate_without_bridge"],"SEMANTIC_CANDIDATE_ONLY")

    def test_target_free_profile_constructor_pins(self):
        """No phi, translation, ratio matching, residual, equality, or target coordinate."""
        started=time.monotonic()
        with mock.patch.object(search,"totient_factors",side_effect=AssertionError("target evaluation")), \
             mock.patch.object(search,"tuples",side_effect=AssertionError("target tuple")), \
             mock.patch.object(search,"evaluate",side_effect=AssertionError("residual evaluation")), \
             mock.patch.object(search,"ratio_catalogue",side_effect=AssertionError("rho collision")):
            observed={str(s):search.profile_digest(s) for s in (1,2,3)}
            catalogue=search.endpoint_catalogue()
        elapsed=time.monotonic()-started
        spec=prep.M["profile_catalogues"]
        self.assertEqual({k:v[0] for k,v in observed.items()},spec["core_support_counts"])
        self.assertEqual({k:v[1] for k,v in observed.items()},spec["core_stream_sha256"])
        self.assertEqual(len(catalogue),spec["endpoint_entries"])
        self.assertEqual(search.catalogue_digest(catalogue),spec["endpoint_stream_sha256"])
        self.assertLess(elapsed,spec["catalogue_only_benchmark_cap_seconds"])

    def test_constructor_code_has_no_target_operations(self):
        source=inspect.getsource(search._support_rows)+inspect.getsource(search.profile_digest)+inspect.getsource(search.endpoint_catalogue)
        for forbidden in ("totient_factors(","ratio_catalogue(","evaluate(","k + phi","residual"):
            self.assertNotIn(forbidden,source)

    def test_arm_partition_and_canonical_ownership(self):
        core=list(search.profiles("ODD_CORE_PROFILES"))
        wall=list(search.profiles("ODD_COLLISION_WALL"))
        self.assertEqual((len(core),len(wall)),(34066,745665))
        self.assertEqual({row[3]["support_cardinality"] for row in core},{1,2})
        self.assertEqual({row[3]["support_cardinality"] for row in wall},{3})
        self.assertFalse({row[1] for row in core}&{row[1] for row in wall})

    def test_core_rejects_rho_before_residual(self):
        source=inspect.getsource(search.tuples)
        core=source.index('if arm == "ODD_CORE_PROFILES"')
        mismatch=source.index('"SUPPORT_RHO_MISMATCH"',core)
        evaluation=source.index("evaluate(k, k_factors",core)
        self.assertLess(mismatch,evaluation)

    def test_lattice_rejects_before_residual(self):
        source=inspect.getsource(search.tuples)
        self.assertLess(source.index('"EXPONENT_LATTICE_MISMATCH"'),
                        source.index("evaluate(k, k_factors"))

    def live_fixture(self):
        searches={name:{"query":query,"total_count":0,"incomplete_results":False,"items":[]}
                  for name,query in prep.SEARCH_QUERIES.items()}
        return {"schema":"oeis-a108569-live-duplicate-audit-v1",
            "upstream_head":prep.M["formal_conjectures"]["commit"],"upstream_tree":prep.M["formal_conjectures"]["tree"],
            "queries":dict(prep.SEARCH_QUERIES),"searches":searches,
            "known_ingestion_pull":{**prep.INGESTION,"target_file_records":[prep.INGESTION_TARGET_FILE],
                                     "file_page_sizes":[75],"files_scanned":75},
            "open_pull_requests_scanned":prep.OPEN_PULL_COUNT,
            "pulls_requiring_full_file_pagination":sorted(prep.FULL_FILE_PAGE_SIZES),
            "full_file_pagination_page_sizes":{str(k):v for k,v in prep.FULL_FILE_PAGE_SIZES.items()},
            "open_target_path_matches":[],"release_page_sizes":[11],"releases_scanned":11,
            "local_release_matches":[],"upstream_release_page_sizes":[1],"upstream_releases_scanned":1,
            "upstream_release_matches":[]}

    def assert_live_rejected(self,mutator,pattern):
        value=self.live_fixture(); mutator(value)
        with tempfile.TemporaryDirectory() as directory:
            path=pathlib.Path(directory)/"live.json"; path.write_bytes(prep.canonical(value))
            with self.assertRaisesRegex(ValueError,pattern): prep.verify_live_audit(path)

    def test_live_audit_accepts_exact_frozen_surface(self):
        with tempfile.TemporaryDirectory() as directory:
            path=pathlib.Path(directory)/"live.json"; path.write_bytes(prep.canonical(self.live_fixture()))
            self.assertEqual(prep.verify_live_audit(path)["open_pull_requests_scanned"],279)

    def test_live_audit_rejects_pagination_omission_and_zero_forgery(self):
        self.assert_live_rejected(lambda x:x["pulls_requiring_full_file_pagination"].pop(),"pagination")
        self.assert_live_rejected(lambda x:x["full_file_pagination_page_sizes"].__setitem__("3422",[0]),"page-size")
        self.assert_live_rejected(lambda x:x.__setitem__("release_page_sizes",[0]),"release pagination")
        self.assert_live_rejected(lambda x:x.__setitem__("upstream_release_page_sizes",[0]),"upstream release")

    def test_live_audit_rejects_ingestion_and_race_mutations(self):
        self.assert_live_rejected(lambda x:x["known_ingestion_pull"].__setitem__("merge_commit_sha","0"*40),"#4450")
        self.assert_live_rejected(lambda x:x["known_ingestion_pull"].__setitem__("target_file_records",[]),"#4450")
        self.assert_live_rejected(lambda x:x["open_target_path_matches"].append({"number":9999}),"race stop")
        self.assert_live_rejected(lambda x:x["searches"]["upstream_sequence"].update({"total_count":1,"items":[{"number":4450}]}),"duplicate")

    def test_rename_away_is_target_touch(self):
        target=prep.M["formal_conjectures"]["path"]
        self.assertTrue(prep.touches_target([{"filename":"new","previous_filename":target,"status":"renamed"}]))
        self.assertTrue(prep.touches_target([{"path":target,"changeType":"MODIFIED"}]))

    def test_catalogue_control_small_fixture(self):
        rows="1 1\n2 4\n3 8\n"
        with tempfile.TemporaryDirectory() as directory:
            path=pathlib.Path(directory)/"b"; path.write_text(rows)
            digest=hashlib.sha256(path.read_bytes()).hexdigest()
            with mock.patch.dict(prep.M["oeis_bfile"],{"sha256":digest,"rows":3,"first_index":1,
                "first_value":1,"last_index":3,"last_value":8},clear=False), \
                 mock.patch.object(prep,"SOPHIE_GERMAIN_CONTROLS",{}):
                result=prep.verify_catalogue(path)
        self.assertEqual((result["odd_rows"],result["even_rows"]),([[1,1]],2))

    def args(self,root):
        gate=root/"gate"; (gate/"snapshots").mkdir(parents=True)
        (gate/"gate-attestation.json").write_text("{}\n"); (gate/"snapshots/b108569.txt").write_text("1 1\n")
        return SimpleNamespace(arm="ODD_CORE_PROFILES",shard=0,campaign_commit="1"*40,gate_bundle=gate,
            ledger=root/"ledger.jsonl",terminal=root/"terminal.json",certificate=root/"certificate.json")

    def test_checkpoint_pair_and_interval_boundaries(self):
        coordinates=[{"profile_ordinal":i} for i in range(18)]
        outcomes=[{"stop":"NO_TRANSLATED_ENDPOINT_PROFILE"} for _ in coordinates]
        outcomes[0]={"stop":"SUPPORT_RHO_MISMATCH","support_pair_completed":True}
        with tempfile.TemporaryDirectory() as directory:
            args=self.args(pathlib.Path(directory))
            with mock.patch.object(search,"verify",return_value={"table":{"catalogue":{"rows":1}}}), \
                 mock.patch.object(search,"parse_bfile",return_value=[(1,1)]), \
                 mock.patch.object(search,"tuples",return_value=iter(zip(coordinates,outcomes))):
                self.assertEqual(search.run(args),0)
            rows=[json.loads(line) for line in args.ledger.read_text().splitlines()]
        self.assertEqual([(row["visited"],row["checkpoint_reason"]) for row in rows],
                         [(0,"INITIAL"),(1,"SUPPORT_PAIR_COMPLETE"),(17,"EXPONENT_COORDINATE_INTERVAL"),(18,"FINAL_PREFIX")])

    def test_candidate_atomic_commit_precedes_no_ledger_append(self):
        coordinate={"profile_ordinal":0}; outcome={"stop":"SURVIVOR"}
        calls=0; real=search.Ledger.append
        def only_initial(ledger,payload):
            nonlocal calls; calls+=1
            if calls>1: raise AssertionError("post-candidate ledger append")
            return real(ledger,payload)
        with tempfile.TemporaryDirectory() as directory:
            args=self.args(pathlib.Path(directory))
            with mock.patch.object(search,"verify",return_value={"table":{"catalogue":{"rows":1}}}), \
                 mock.patch.object(search,"parse_bfile",return_value=[(1,1)]), \
                 mock.patch.object(search,"tuples",return_value=iter([(coordinate,outcome)])), \
                 mock.patch.object(search,"make_certificate",return_value={"schema":"synthetic"}), \
                 mock.patch.object(search.Ledger,"append",new=only_initial):
                self.assertEqual(search.run(args),0)
            terminal=json.loads(args.terminal.read_text())
        self.assertEqual((terminal["terminal_reason"],terminal["visited"],calls),("CERTIFICATE_FOUND",1,1))

    def test_ledger_mutation_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path=pathlib.Path(directory)/"ledger"; ledger=search.Ledger(path)
            ledger.append(search.progress("1"*40,"ODD_CORE_PROFILES",0,0,None,None,
                          {name:0 for name in search.STOPS},"INITIAL")); ledger.close()
            independent.chain(path,"1"*40,"ODD_CORE_PROFILES",0)
            path.write_text(path.read_text().replace('"checkpoint_reason":"INITIAL"','"checkpoint_reason":"FINAL_PREFIX"'))
            with self.assertRaisesRegex(ValueError,"hash-chain"): independent.chain(path,"1"*40,"ODD_CORE_PROFILES",0)

    def test_ledger_rejects_noncanonical_extra_and_bool_numeric(self):
        with tempfile.TemporaryDirectory() as directory:
            path=pathlib.Path(directory)/"ledger"; ledger=search.Ledger(path)
            ledger.append(search.progress("1"*40,"ODD_CORE_PROFILES",0,0,None,None,
                          {name:0 for name in search.STOPS},"INITIAL")); ledger.close()
            original=path.read_bytes()
            for mutated,pattern in ((original.rstrip(b"\n"),"noncanonical"),
                                    (b" "+original,"noncanonical")):
                path.write_bytes(mutated)
                with self.assertRaisesRegex(ValueError,pattern): independent.chain(path,"1"*40,"ODD_CORE_PROFILES",0)
            row=json.loads(original); row["extra"]=1; path.write_bytes(independent.canonical(row))
            with self.assertRaisesRegex(ValueError,"key/order"): independent.chain(path,"1"*40,"ODD_CORE_PROFILES",0)
            row=json.loads(original); row["seq"]=False
            body=dict(row); body.pop("row_sha256"); row["row_sha256"]=hashlib.sha256(json.dumps(body,sort_keys=True,separators=(",",":")).encode()).hexdigest()
            path.write_bytes(independent.canonical(row))
            with self.assertRaisesRegex(ValueError,"key/order"): independent.chain(path,"1"*40,"ODD_CORE_PROFILES",0)
            row=json.loads(original); row["shard"]=False
            body=dict(row); body.pop("row_sha256"); row["row_sha256"]=hashlib.sha256(json.dumps(body,sort_keys=True,separators=(",",":")).encode()).hexdigest()
            path.write_bytes(independent.canonical(row))
            with self.assertRaisesRegex(ValueError,"identity"): independent.chain(path,"1"*40,"ODD_CORE_PROFILES",0)

    def test_candidate_canonical_expected_rejects_bool_aliases(self):
        expected={"schema":"oeis-a108569-certificate-v1","arm":"ODD_CORE_PROFILES","shard":0,
                  "coordinate":{"profile_ordinal":0},"campaign_commit":"1"*40,"k":9,
                  "residual":0,"odd_counterexample":True,"source_catalogue_excluded":True,
                  "enumeration_bridge":dict(independent.BRIDGE)}
        mutations=[]
        for path,value in ((("residual",),False),(("odd_counterexample",),1),
                           (("source_catalogue_excluded",),1),
                           (("enumeration_bridge","positive_index_predecessor"),True)):
            item=copy.deepcopy(expected); target=item
            for key in path[:-1]: target=target[key]
            target[path[-1]]=value; mutations.append(item)
        with tempfile.TemporaryDirectory() as directory:
            root=pathlib.Path(directory); cert=root/"candidate.json"
            (root/"gate-attestation.json").write_text("{}\n")
            for item in mutations:
                cert.write_bytes(independent.canonical(item))
                with mock.patch.object(independent,"verify",return_value={}), \
                     mock.patch.object(independent,"parse_bfile",return_value=[(1,1)]), \
                     mock.patch.object(independent,"locate",return_value={"stop":"SURVIVOR"}), \
                     mock.patch.object(independent,"expected_certificate",return_value=expected):
                    with self.assertRaisesRegex(ValueError,"payload"): independent.candidate(cert,root,"1"*40)

    def test_replay_rejects_early_survivor_and_omission(self):
        zero=search.progress("1"*40,"ODD_CORE_PROFILES",0,0,None,None,
                             {name:0 for name in search.STOPS},"INITIAL")
        zero.update({"seq":0,"previous_row_sha256":"0"*64,"row_sha256":"x"})
        first=({"profile_ordinal":0},{"stop":"SURVIVOR"})
        later=({"profile_ordinal":24},{"stop":"NO_TRANSLATED_ENDPOINT_PROFILE"})
        counts={name:0 for name in search.STOPS}; counts["SURVIVOR"]=1; counts["NO_TRANSLATED_ENDPOINT_PROFILE"]=1
        terminal={"campaign_commit":"1"*40,"arm":"ODD_CORE_PROFILES","shard":0,"visited":2,
                  "counts":counts,"last_coordinate":later[0],"last_outcome":later[1],
                  "odd_profile_domain_only":True,"terminal_reason":"CERTIFICATE_FOUND"}
        with mock.patch.object(independent,"expected_tuples",return_value=iter([first,later])):
            with self.assertRaisesRegex(ValueError,"first survivor"):
                independent.replay(terminal,[zero],{"coordinate":first[0]},set())
        terminal["terminal_reason"]="CAP_PREFIX"
        final=search.progress("1"*40,"ODD_CORE_PROFILES",0,2,later[0],later[1],counts,"FINAL_PREFIX")
        final.update({"seq":1,"previous_row_sha256":"x","row_sha256":"y"})
        with mock.patch.object(independent,"expected_tuples",return_value=iter([first,later])):
            with self.assertRaisesRegex(ValueError,"candidate omission"):
                independent.replay(terminal,[zero,final],None,set())

    def test_terminal_rejects_extra_and_bool_numeric_fields(self):
        counts={name:0 for name in search.STOPS}
        with tempfile.TemporaryDirectory() as directory:
            root=pathlib.Path(directory); ledger=root/"ledger"; ledger.write_text("x")
            gate=root/"gate"; gate.mkdir(); (gate/"gate-attestation.json").write_text("{}\n")
            base={"schema":"oeis-a108569-terminal-v1","campaign_commit":"1"*40,
                  "source_commit":prep.M["formal_conjectures"]["commit"],
                  "gate_attestation_sha256":prep.sha(gate/"gate-attestation.json"),
                  "arm":"ODD_CORE_PROFILES","shard":0,"odd_profile_domain_only":True,
                  "catalogue_rows":1,"visited":0,"last_coordinate":None,"last_outcome":None,
                  "counts":counts,"terminal_reason":"CAP_PREFIX","certificate_present":False,
                  "worker_error":None,"ledger_rows":1,"final_row_sha256":"0"*64,
                  "ledger_sha256":prep.sha(ledger)}
            mutations=({"extra":1},{"shard":False},{"ledger_rows":True},
                       {"counts":{**counts,"SURVIVOR":False}})
            terminal_path=root/"terminal.json"
            for mutation in mutations:
                terminal_path.write_bytes(independent.canonical({**base,**mutation}))
                with mock.patch.object(independent,"verify",return_value={"table":{"catalogue":{"rows":1}}}), \
                     mock.patch.object(independent,"chain",return_value=([{}],"0"*64)), \
                     mock.patch.object(independent,"replay"):
                    with self.assertRaises(ValueError):
                        independent.terminal(ledger,terminal_path,None,gate,"1"*40,"ODD_CORE_PROFILES",0)

    def test_verifier_is_independent_and_bridge_is_symbolic(self):
        source=inspect.getsource(independent)
        self.assertNotIn("import search_oeis_a108569",source)
        self.assertEqual(independent.BRIDGE["index_definition"],"i := Nat.count A k")
        self.assertIn("not a Lean proof",source)


if __name__=="__main__":
    unittest.main()
