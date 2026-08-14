#!/usr/bin/env python3
"""Independent v2 final coverage replay; does not call the construction adversary."""
from __future__ import annotations
import argparse, json, math, pathlib, time, traceback
from oeis_a231201_v2_common import M, MANIFEST_PATH, Ledger, assignment_hash, atomic_json, crt_pair, exact_commit, order_table, periodic_value, queue_hash, sha, validate_assignment
from prepare_oeis_a231201_gate import verify as verify_gate

def independent_coverage(assignment:dict[int,int],deadline:float,ledger:Ledger)->dict:
    frontier={(0,1)}
    for level,(q,order,modulus) in enumerate(order_table()):
        allowed=[s for s in range(modulus) if periodic_value(q,s)!=assignment[q]]; following=set()
        for input_index,(r,current) in enumerate(sorted(frontier)):
            for residue_index,s in enumerate(allowed):
                if time.monotonic()>=deadline:
                    cursor={"input_index":input_index,"input_residue":r,"input_modulus":current,"allowed_residue_index":residue_index,"allowed_residue":s}
                    ledger.append({"schema":"oeis-a231201-v2-independent-level-v1","level":level,"q":q,"status":"FINAL_VERIFIER_DEADLINE","cursor":cursor,"partial_output_states":len(following),"partial_queue_sha256":queue_hash(sorted(following))})
                    return {"status":"FINAL_VERIFIER_DEADLINE","level":level,"cursor":cursor}
                merged=crt_pair(r,current,s,modulus)
                if merged is not None: following.add(merged)
        frontier=following; ledger.append({"schema":"oeis-a231201-v2-independent-level-v1","level":level,"q":q,"order":order,"modulus":modulus,"status":"DOMAIN_EXHAUSTED","output_states":len(frontier),"queue_sha256":queue_hash(sorted(frontier))})
        if not frontier:return {"status":"COMPLETE_COVER","level":level}
    r,modulus=min(frontier,key=lambda z:(z[0] if z[0] else z[1],z[1])); return {"status":"UNCOVERED_CLASS","x":r if r else modulus,"residue":r,"modulus":modulus,"final_states":len(frontier),"queue_sha256":queue_hash(sorted(frontier))}

def crt_all(assignment:dict[int,int])->tuple[int,int]:
    n=0; modulus=1
    for q in M["primes"]: n+=modulus*(((assignment[q]-n)*pow(modulus,-1,q))%q); modulus*=q
    return n%modulus,modulus

def run(a)->int:
    started=time.monotonic(); ledger=Ledger(a.ledger); gate_hash=None
    if not a.candidate.is_file():
        ledger.append({"schema":"oeis-a231201-v2-final-not-run-v1","campaign_commit":a.campaign_commit,"arm":a.arm,"cell":a.cell,"round":a.round,"slot":a.slot,"status":"NOT_RUN","reason":"ABSENT_PENDING_COVER"}); ledger.close()
        atomic_json(a.output,{"schema":"oeis-a231201-v2-final-terminal-v1","campaign_commit":a.campaign_commit,"manifest_sha256":sha(MANIFEST_PATH),"gate_attestation_sha256":None,"candidate_sha256":None,"assignment_sha256":None,"arm":a.arm,"cell":a.cell,"round":a.round,"slot":a.slot,"status":"NOT_RUN","result":None,"exit_status":None,"ledger_rows":ledger.seq,"final_row_sha256":ledger.previous,"ledger_sha256":sha(a.ledger),"elapsed_seconds":time.monotonic()-started}); return 78
    status="PREREQUISITE_NOT_RUN"; result={"status":"PREREQUISITE_NOT_RUN"}; extra={}
    try:
        if a.prerequisite_check_exit_code: raise ValueError(f"outer prerequisite check failed: {a.prerequisite_check_exit_code}")
        exact_commit(a.campaign_commit); verify_gate(a.gate,a.campaign_commit); gate_hash=sha(a.gate/"gate-attestation.json"); doc=json.loads(a.candidate.read_text()); assignment={int(k):int(v) for k,v in doc["assignment"].items()}; validate_assignment(assignment,a.cell)
        if doc.get("schema")!="oeis-a231201-v2-cover-pending-v1" or doc.get("manifest_sha256")!=sha(MANIFEST_PATH) or doc.get("gate_attestation_sha256")!=gate_hash or doc.get("assignment_sha256")!=assignment_hash(assignment) or (doc.get("campaign_commit"),doc.get("arm"),doc.get("cell"),doc.get("round"),doc.get("slot"))!=(a.campaign_commit,a.arm,a.cell,a.round,a.slot): raise ValueError("pending candidate identity drift")
        result=independent_coverage(assignment,started+M["internal_seconds"],ledger)
        if result["status"]=="COMPLETE_COVER":
            n0,Q=crt_all(assignment); boundary=10_000_000; n=n0 if n0>boundary else n0+((boundary-n0)//Q+1)*Q
            if not (n>boundary and n>max(M["primes"]) and all(n%q==assignment[q] for q in M["primes"])): raise ValueError("CRT/proper-divisor replay failed")
            status="VERIFIED_COUNTEREXAMPLE"; extra={"n":n,"least_nonnegative_crt":n0,"Q":Q}
        elif result["status"]=="UNCOVERED_CLASS": status="VERIFICATION_FAILED_UNCOVERED_CLASS"
        else: status="FINAL_VERIFIER_DEADLINE"
    except BaseException:
        if gate_hash is not None: status="WORKER_ERROR"; result={"status":"WORKER_ERROR"}
        ledger.append({"schema":"oeis-a231201-v2-final-error-v1","campaign_commit":a.campaign_commit,"arm":a.arm,"cell":a.cell,"round":a.round,"slot":a.slot,"status":status,"traceback":traceback.format_exc()})
    finally:
        ledger.close(); receipt={"schema":"oeis-a231201-v2-final-terminal-v1","campaign_commit":a.campaign_commit,"manifest_sha256":sha(MANIFEST_PATH),"gate_attestation_sha256":gate_hash,"candidate_sha256":sha(a.candidate),"assignment_sha256":assignment_hash(assignment) if 'assignment' in locals() else None,"arm":a.arm,"cell":a.cell,"round":a.round,"slot":a.slot,"status":status,"result":result,**extra,"ledger_rows":ledger.seq,"final_row_sha256":ledger.previous,"ledger_sha256":sha(a.ledger),"elapsed_seconds":time.monotonic()-started,"exit_status":0 if status=="VERIFIED_COUNTEREXAMPLE" else 75}; atomic_json(a.output,receipt)
    return receipt["exit_status"]

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--candidate",type=pathlib.Path,required=True); p.add_argument("--ledger",type=pathlib.Path,required=True); p.add_argument("--output",type=pathlib.Path,required=True); p.add_argument("--gate",type=pathlib.Path,required=True); p.add_argument("--prerequisite-check-exit-code",type=int,default=0); p.add_argument("--campaign-commit",required=True); p.add_argument("--arm",choices=M["arms"],required=True); p.add_argument("--cell",required=True); p.add_argument("--round",type=int,required=True); p.add_argument("--slot",type=int,choices=[0],required=True); return run(p.parse_args())
if __name__=="__main__": raise SystemExit(main())
