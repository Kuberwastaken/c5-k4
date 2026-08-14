#!/usr/bin/env python3
"""Write a canonical, fsynced v2 execution-status record with fail-closed precedence."""
import argparse, pathlib
from oeis_a231201_v2_common import atomic_json

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("output",type=pathlib.Path); p.add_argument("--stage",required=True); p.add_argument("--campaign-commit",required=True); p.add_argument("--arm",required=True); p.add_argument("--cell",required=True); p.add_argument("--round",type=int,required=True); p.add_argument("--prerequisite-check-exit-code",type=int,required=True); p.add_argument("--stage-exit-code",type=int,required=True); p.add_argument("--artifact-verifier-exit-code",type=int,required=True)
    a=p.parse_args()
    # Structural verifier failure has precedence even if the bounded stage also
    # failed; no failure is hidden by first-error aggregation.
    result=a.artifact_verifier_exit_code or a.prerequisite_check_exit_code or a.stage_exit_code
    atomic_json(a.output,{"schema":"oeis-a231201-v2-execution-status-v1","campaign_commit":a.campaign_commit,"stage":a.stage,"arm":a.arm,"cell":a.cell,"round":a.round,"prerequisite_check_exit_code":a.prerequisite_check_exit_code,"stage_exit_code":a.stage_exit_code,"artifact_verifier_exit_code":a.artifact_verifier_exit_code,"job_exit_code":result})
    return result
if __name__=="__main__": raise SystemExit(main())
