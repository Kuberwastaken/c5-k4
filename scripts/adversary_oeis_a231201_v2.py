#!/usr/bin/env python3
"""Exact v2 generalized-CRT adversary for one durably emitted assignment."""
from __future__ import annotations
import argparse, json, math, pathlib, time, traceback
from oeis_a231201_v2_common import M, MANIFEST_PATH, Ledger, assignment_hash, atomic_json, exact_commit, order_table, periodic_value, queue_hash, sha, validate_assignment
from prepare_oeis_a231201_gate import verify as verify_gate

def refine(assignment:dict[int,int],deadline:float,ledger:Ledger)->dict:
    states=[(0,1)]
    for level,(q,order,modulus) in enumerate(order_table()):
        following=[]; processed=0
        for input_index,(r,current) in enumerate(states):
            limit=math.lcm(current,modulus)
            for split_index,value in enumerate(range(r,limit,current)):
                if time.monotonic()>=deadline:
                    cursor={"input_index":input_index,"input_residue":r,"input_modulus":current,"split_index":split_index,"split_value":value}
                    ledger.append({"schema":"oeis-a231201-v2-adversary-level-v1","level":level,"q":q,"status":"ADVERSARY_DEADLINE","input_states":len(states),"input_processed":processed,"cursor":cursor,"partial_output_states":len(following),"partial_queue_sha256":queue_hash(following)})
                    return {"status":"ADVERSARY_DEADLINE","level":level,"cursor":cursor,"partial_states":len(following),"partial_queue_sha256":queue_hash(following)}
                if periodic_value(q,value)!=assignment[q]: following.append((value,limit))
            processed+=1
        following.sort(); ledger.append({"schema":"oeis-a231201-v2-adversary-level-v1","level":level,"q":q,"order":order,"modulus":modulus,"status":"DOMAIN_EXHAUSTED","input_states":len(states),"input_processed":processed,"output_states":len(following),"queue_sha256":queue_hash(following)})
        states=following
        if not states:return {"status":"COMPLETE_COVER","level":level,"states":[]}
    r,modulus=min(states,key=lambda z:(z[0] if z[0]>0 else z[1],z[1]))
    return {"status":"UNCOVERED_CLASS","x":r if r>0 else modulus,"residue":r,"modulus":modulus,"final_states":len(states),"queue_sha256":queue_hash(states)}

def run(a)->int:
    started=time.monotonic(); ledger=Ledger(a.ledger); candidate=None; gate_hash=None; assignment_digest=None; assignment_artifact_digest=None
    if not a.assignment.is_file():
        ledger.append({"schema":"oeis-a231201-v2-adversary-not-run-v1","campaign_commit":a.campaign_commit,"arm":a.arm,"cell":a.cell,"round":a.round,"slot":a.slot,"status":"NOT_RUN","reason":"ABSENT_ASSIGNMENT"}); ledger.close()
        atomic_json(a.output,{"schema":"oeis-a231201-v2-adversary-terminal-v1","campaign_commit":a.campaign_commit,"manifest_sha256":sha(MANIFEST_PATH),"gate_attestation_sha256":None,"arm":a.arm,"cell":a.cell,"round":a.round,"slot":a.slot,"assignment_sha256":None,"assignment_artifact_sha256":None,"status":"NOT_RUN","result":None,"candidate_present":False,"candidate_sha256":None,"exit_status":None,"ledger_rows":ledger.seq,"final_row_sha256":ledger.previous,"ledger_sha256":sha(a.ledger),"elapsed_seconds":time.monotonic()-started})
        return 78
    status="PREREQUISITE_NOT_RUN"; result={"status":"PREREQUISITE_NOT_RUN"}
    try:
        if a.prerequisite_check_exit_code: raise ValueError(f"outer prerequisite check failed: {a.prerequisite_check_exit_code}")
        exact_commit(a.campaign_commit); verify_gate(a.gate,a.campaign_commit); gate_hash=sha(a.gate/"gate-attestation.json")
        doc=json.loads(a.assignment.read_text()); assignment={int(k):int(v) for k,v in doc["assignment"].items()}; validate_assignment(assignment,a.cell)
        assignment_digest=assignment_hash(assignment); assignment_artifact_digest=sha(a.assignment)
        if doc.get("schema")!="oeis-a231201-v2-assignment-v1" or doc.get("assignment_sha256")!=assignment_digest or doc.get("manifest_sha256")!=sha(MANIFEST_PATH) or doc.get("gate_attestation_sha256")!=gate_hash: raise ValueError("assignment schema/hash/source drift")
        if (doc.get("campaign_commit"),doc.get("arm"),doc.get("cell"),doc.get("round"),doc.get("slot"))!=(a.campaign_commit,a.arm,a.cell,a.round,a.slot): raise ValueError("assignment identity drift")
        result=refine(assignment,started+M["internal_seconds"],ledger); status="COVER_FOUND_PENDING_VERIFY" if result["status"]=="COMPLETE_COVER" else result["status"]
        if status=="COVER_FOUND_PENDING_VERIFY":
            candidate={"schema":"oeis-a231201-v2-cover-pending-v1","campaign_commit":a.campaign_commit,"manifest_sha256":sha(MANIFEST_PATH),"gate_attestation_sha256":doc["gate_attestation_sha256"],"arm":a.arm,"cell":a.cell,"round":a.round,"slot":a.slot,"assignment_sha256":doc["assignment_sha256"],"assignment":doc["assignment"]}
            atomic_json(a.candidate,candidate)
    except BaseException:
        if gate_hash is not None: status="WORKER_ERROR"; result={"status":"WORKER_ERROR"}
        ledger.append({"schema":"oeis-a231201-v2-adversary-error-v1","campaign_commit":a.campaign_commit,"arm":a.arm,"cell":a.cell,"round":a.round,"slot":a.slot,"status":status,"traceback":traceback.format_exc()})
    finally:
        ledger.close(); receipt={"schema":"oeis-a231201-v2-adversary-terminal-v1","campaign_commit":a.campaign_commit,"manifest_sha256":sha(MANIFEST_PATH),"gate_attestation_sha256":gate_hash,"arm":a.arm,"cell":a.cell,"round":a.round,"slot":a.slot,"assignment_sha256":assignment_digest,"assignment_artifact_sha256":assignment_artifact_digest,"status":status,"result":result,"candidate_present":candidate is not None,"candidate_sha256":sha(a.candidate) if candidate is not None else None,"ledger_rows":ledger.seq,"final_row_sha256":ledger.previous,"ledger_sha256":sha(a.ledger),"elapsed_seconds":time.monotonic()-started,"exit_status":0 if status in {"COVER_FOUND_PENDING_VERIFY","UNCOVERED_CLASS"} else 75}
        atomic_json(a.output,receipt)
    return receipt["exit_status"]

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--assignment",type=pathlib.Path,required=True); p.add_argument("--ledger",type=pathlib.Path,required=True); p.add_argument("--output",type=pathlib.Path,required=True); p.add_argument("--candidate",type=pathlib.Path,required=True); p.add_argument("--gate",type=pathlib.Path,required=True); p.add_argument("--prerequisite-check-exit-code",type=int,default=0); p.add_argument("--campaign-commit",required=True); p.add_argument("--arm",choices=M["arms"],required=True); p.add_argument("--cell",required=True); p.add_argument("--round",type=int,required=True); p.add_argument("--slot",type=int,choices=[0],required=True)
    return run(p.parse_args())
if __name__=="__main__": raise SystemExit(main())
