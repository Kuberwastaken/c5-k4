#!/usr/bin/env python3
"""Verify that one checksum-bound predecessor ended in an honest usable state."""
import argparse,json,pathlib

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("status",type=pathlib.Path); p.add_argument("--terminal",type=pathlib.Path,required=True); p.add_argument("--stage",choices=["construction","adversary"],required=True); p.add_argument("--campaign-commit",required=True); p.add_argument("--arm",required=True); p.add_argument("--cell",required=True); p.add_argument("--round",type=int,required=True)
    a=p.parse_args(); value=json.loads(a.status.read_text()); terminal=json.loads(a.terminal.read_text())
    expected_identity=("oeis-a231201-v2-execution-status-v1",a.campaign_commit,a.stage,a.arm,a.cell,a.round)
    actual_identity=(value.get("schema"),value.get("campaign_commit"),value.get("stage"),value.get("arm"),value.get("cell"),value.get("round"))
    if actual_identity!=expected_identity: raise SystemExit("predecessor execution identity drift")
    prerequisite,stage_code,artifact,job=(value.get("prerequisite_check_exit_code"),value.get("stage_exit_code"),value.get("artifact_verifier_exit_code"),value.get("job_exit_code"))
    if prerequisite!=0 or artifact!=0 or job!=stage_code or stage_code not in {0,75,78}: raise SystemExit(f"predecessor execution was not structurally successful: {(prerequisite,stage_code,artifact,job)}")
    schemas={"construction":"oeis-a231201-v2-construction-terminal-v1","adversary":"oeis-a231201-v2-adversary-terminal-v1"}
    allowed={"construction":{"ASSIGNMENT_EMITTED","BASIS_INFEASIBLE_UNVERIFIED","CAP_EXHAUSTED_AFTER_ASSIGNMENTS","CAP_EXHAUSTED_NO_ASSIGNMENT"},"adversary":{"NOT_RUN","COVER_FOUND_PENDING_VERIFY","UNCOVERED_CLASS","ADVERSARY_DEADLINE"}}
    rejected={"PREREQUISITE_NOT_RUN","WORKER_ERROR"}
    terminal_identity=(terminal.get("campaign_commit"),terminal.get("arm"),terminal.get("cell"),terminal.get("round"))
    if terminal.get("status") in rejected or terminal.get("schema")!=schemas[a.stage] or terminal_identity!=(a.campaign_commit,a.arm,a.cell,a.round) or terminal.get("status") not in allowed[a.stage]: raise SystemExit("predecessor terminal identity/status drift")
    terminal_exit=terminal.get("exit_status")
    if (terminal_exit is None and stage_code!=78) or (terminal_exit is not None and terminal_exit!=stage_code): raise SystemExit("predecessor terminal/execution exit drift")
    print('{"predecessor_execution_verified":true}')
    return 0
if __name__=="__main__": raise SystemExit(main())
