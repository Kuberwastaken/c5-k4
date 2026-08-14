"""Constructor-only v2 tests. No target assignment, solver model, or adversary is evaluated."""
import json, pathlib, subprocess, sys, tempfile, unittest
from unittest import mock
import oeis_a231201_v2_common as common

class V2ConstructorTests(unittest.TestCase):
    def test_inherited_universe_semantics_and_cells(self):
        self.assertEqual(len(common.M["primes"]),55)
        self.assertEqual(common.M["primes"],[n for n in range(2,258) if common.is_prime_trial(n)])
        self.assertEqual(common.combined_period(),int(common.M["combined_period"]))
        cells=[f'{a2}_{a3}' for a2 in range(2) for a3 in range(3)]
        self.assertEqual([common.cell_fixed(x) for x in cells],[{2:a2,3:a3} for a2 in range(2) for a3 in range(3)])

    def test_exact_active_row_counts(self):
        seed=list(range(1,4097)); counts={cell:len(common.active_rows(cell,seed)) for cell in [f'{a}_{b}' for a in range(2) for b in range(3)]}
        self.assertEqual(counts,{"0_0":1366,"0_1":1365,"0_2":1365,"1_0":1365,"1_1":1365,"1_2":1366})

    def test_low_discrepancy_permutation_is_frozen(self):
        values=common.low_discrepancy_seed(); self.assertEqual(len(values),4096); self.assertEqual(set(values),set(range(1,4097)))
        self.assertEqual(values[:8],[1,2049,1025,3073,513,2561,1537,3585])

    def test_caps_and_static_limits(self):
        self.assertEqual((common.M["internal_seconds"],common.M["external_seconds"],common.M["external_kill_after_seconds"]),(54,60,6))
        self.assertLessEqual(common.M["cp_slice_seconds"],15); self.assertEqual(common.M["cp_slices_per_construction"],3); self.assertEqual(common.M["construction_rounds"],3); self.assertEqual(common.M["assignment_slots_per_round"],1)

    def test_atomic_and_hash_chained_artifacts(self):
        with tempfile.TemporaryDirectory() as td, mock.patch.object(common.os,"fsync") as fsync:
            root=pathlib.Path(td); common.atomic_json(root/"x.json",{"x":1}); ledger=common.Ledger(root/"x.jsonl"); first=ledger.append({"x":1}); ledger.append({"x":2}); ledger.close()
            rows=[json.loads(x) for x in (root/"x.jsonl").read_text().splitlines()]
            self.assertEqual(rows[0]["previous_row_sha256"],common.ZERO); self.assertEqual(rows[1]["previous_row_sha256"],first); self.assertGreaterEqual(fsync.call_count,4)

    def test_terminal_vocabularies_and_no_upgrade(self):
        self.assertIn("NOT_RUN",common.M["terminal_vocabularies"]["adversary"]); self.assertIn("NOT_RUN",common.M["terminal_vocabularies"]["final"])
        for stage in ("construction","adversary","final"): self.assertIn("PREREQUISITE_NOT_RUN",common.M["terminal_vocabularies"][stage])
        self.assertEqual(common.M["forbidden_statuses"],["NO_COMPLETE_COVER"])
        for name in ("construct_oeis_a231201_v2.py","adversary_oeis_a231201_v2.py","verify_oeis_a231201_v2_final.py"):
            source=(common.ROOT/"scripts"/name).read_text(); self.assertNotIn('"NO_COMPLETE_COVER"',source)

    def test_audit_guards_are_frozen_without_importing_evaluators(self):
        constructor=(common.ROOT/"scripts/construct_oeis_a231201_v2.py").read_text()
        for token in ("singly_covered","least_prime_prefix","original_assignment_artifact_sha256","original_adversary_receipt_sha256","--prior-receipt"):
            self.assertIn(token,constructor)
        verifier=(common.ROOT/"scripts/verify_oeis_a231201_v2_artifacts.py").read_text()
        for token in ("verified_gate(a)","read_candidate","COMPLETE_COVER","crt_all(assignment)","forged final CRT/result","candidate_sha256"):
            self.assertIn(token,verifier)
        workflow=(common.ROOT/".github/workflows/oeis-a231201-v2-development.yml").read_text()
        self.assertGreaterEqual(workflow.count("continue-on-error: true"),13)
        self.assertEqual(workflow.count("record_oeis_a231201_v2_execution.py"),7)
        self.assertEqual(workflow.count("--prerequisite-check-exit-code"),14)  # stage input plus execution record
        self.assertIn("stage-diagnostic-terminal.json",workflow)
        self.assertEqual(workflow.count("Finalize stage diagnostic and checksums"),1)  # one YAML anchor, reused six times
        self.assertIn("STAGE_TERMINAL_UNAVAILABLE",workflow)
        self.assertRegex(workflow,r"construct-r0:\n(?:.*\n){1,4}    if: always\(\)")
        self.assertEqual(workflow.count("verify_oeis_a231201_v2_execution.py"),10)

    def test_predecessor_execution_status_accepts_honest_nonzero_only(self):
        script=common.ROOT/"scripts/verify_oeis_a231201_v2_execution.py"; commit="a"*40
        base={"schema":"oeis-a231201-v2-execution-status-v1","campaign_commit":commit,"stage":"construction","arm":"COMPRESSED_SET_COVER_CP","cell":"0_0","round":0,"prerequisite_check_exit_code":0,"stage_exit_code":75,"artifact_verifier_exit_code":0,"job_exit_code":75}
        terminal={"schema":"oeis-a231201-v2-construction-terminal-v1","campaign_commit":commit,"arm":base["arm"],"cell":"0_0","round":0,"status":"CAP_EXHAUSTED_NO_ASSIGNMENT","exit_status":75}
        with tempfile.TemporaryDirectory() as td:
            path=pathlib.Path(td)/"status.json"; term=pathlib.Path(td)/"terminal.json"; path.write_text(json.dumps(base)); term.write_text(json.dumps(terminal))
            args=[sys.executable,str(script),str(path),"--terminal",str(term),"--stage","construction","--campaign-commit",commit,"--arm",base["arm"],"--cell","0_0","--round","0"]
            self.assertEqual(subprocess.run(args,capture_output=True).returncode,0)
            notrun=dict(base,stage="adversary",stage_exit_code=78,job_exit_code=78); path.write_text(json.dumps(notrun)); term.write_text(json.dumps({"schema":"oeis-a231201-v2-adversary-terminal-v1","campaign_commit":commit,"arm":base["arm"],"cell":"0_0","round":0,"status":"NOT_RUN","exit_status":None})); adversary_args=[x if x!="construction" else "adversary" for x in args]
            self.assertEqual(subprocess.run(adversary_args,capture_output=True).returncode,0)
            path.write_text(json.dumps(dict(base,artifact_verifier_exit_code=1,job_exit_code=1))); term.write_text(json.dumps(terminal))
            self.assertNotEqual(subprocess.run(args,capture_output=True).returncode,0)
            path.write_text(json.dumps(base)); term.write_text(json.dumps(dict(terminal,status="WORKER_ERROR")))
            self.assertNotEqual(subprocess.run(args,capture_output=True).returncode,0)

if __name__=="__main__": unittest.main()
