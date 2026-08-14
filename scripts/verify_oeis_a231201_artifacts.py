#!/usr/bin/env python3
"""Fail-closed structural replay of A231201 master artifacts."""
from __future__ import annotations
import argparse, hashlib, json, pathlib
from oeis_a231201_common import M, MANIFEST_PATH, ZERO, combined_period, direct_value, order_table, sha, shard_fixed
from prepare_oeis_a231201_gate import verify as verify_gate

def verify_chain(path:pathlib.Path,commit:str,arm:str,shard:int)->tuple[int,str]:
    previous=ZERO; count=0
    with path.open(encoding="ascii") as f:
        for line in f:
            row=json.loads(line); digest=row.pop("row_sha256",None)
            if row.get("seq")!=count or row.get("previous_row_sha256")!=previous or row.get("campaign_commit")!=commit or row.get("arm")!=arm or row.get("shard")!=shard: raise ValueError("master ledger identity/order drift")
            actual=hashlib.sha256(json.dumps(row,sort_keys=True,separators=(",",":")).encode("ascii")).hexdigest()
            if digest!=actual: raise ValueError("master ledger hash drift")
            previous=digest; count+=1
    return count,previous

def terminal(a)->None:
    verify_gate(a.gate,a.campaign_commit); t=json.loads(a.terminal.read_text()); count,last=verify_chain(a.ledger,a.campaign_commit,a.arm,a.shard)
    allowed={"DEADLINE_PREFIX","SOLVER_INFEASIBLE_UNVERIFIED","COVER_FOUND_PENDING_VERIFY","WORKER_ERROR"}
    if t.get("schema")!="oeis-a231201-master-terminal-v1" or t.get("terminal_reason") not in allowed: raise ValueError("terminal reason/schema drift")
    expected_identity=(a.campaign_commit,M["formal_conjectures"]["commit"],sha(a.gate/"gate-attestation.json"),a.arm,a.shard,shard_fixed(a.arm,a.shard))
    actual=(t.get("campaign_commit"),t.get("source_commit"),t.get("gate_attestation_sha256"),t.get("arm"),t.get("shard"),{int(k):v for k,v in t.get("fixed",{}).items()})
    if actual!=expected_identity: raise ValueError("terminal binding drift")
    if (t.get("ledger_rows"),t.get("final_row_sha256"),t.get("ledger_sha256"))!=(count,last,sha(a.ledger)): raise ValueError("terminal ledger drift")
    if t.get("manifest_sha256")!=sha(MANIFEST_PATH) or t.get("source_sha256")!=M["formal_conjectures"]["sha256"] or t.get("order_table")!=[list(x) for x in order_table()] or t.get("combined_period")!=str(combined_period()) or t.get("ortools")!=M["solver"]["version"]: raise ValueError("terminal environment/frozen arithmetic drift")
    checkpoints=t.get("checkpoint_artifacts",{}); previous=ZERO; checkpoint_values={}
    for index,(relative,digest) in enumerate(sorted(checkpoints.items())):
        path=a.work/relative
        if sha(path)!=digest: raise ValueError("checkpoint artifact drift")
        value=json.loads(path.read_text())
        if value.get("iteration")!=index or value.get("previous_checkpoint_sha256")!=previous or value.get("campaign_commit")!=a.campaign_commit or value.get("arm")!=a.arm or value.get("shard")!=a.shard: raise ValueError("checkpoint chain drift")
        checkpoint_values[index]=value
        previous=digest
    if previous!=t.get("last_checkpoint_sha256"): raise ValueError("last checkpoint binding drift")
    for relative,digest in t.get("adversary_artifacts",{}).items():
        if sha(a.work/relative)!=digest: raise ValueError("adversary artifact drift")
    receipt_paths=sorted(a.work.glob("adversary-*.json"))
    for receipt_path in receipt_paths:
        stem=receipt_path.stem; iteration=int(stem.split("-")[-1]); assignment_path=a.work/f"assignment-{iteration:04d}.json"; ledger_path=a.work/f"adversary-{iteration:04d}.jsonl"
        assignment_doc=json.loads(assignment_path.read_text()); assignment={int(k):int(v) for k,v in assignment_doc["assignment"].items()}
        if (assignment_doc.get("campaign_commit"),assignment_doc.get("arm"),assignment_doc.get("shard"),assignment_doc.get("iteration"))!=(a.campaign_commit,a.arm,a.shard,iteration): raise ValueError("assignment identity drift")
        if list(sorted(assignment))!=M["primes"] or any(not 0<=assignment[q]<q for q in assignment) or any(assignment[q]!=v for q,v in shard_fixed(a.arm,a.shard).items()): raise ValueError("assignment universe/shard drift")
        raw=json.dumps(assignment,sort_keys=True,separators=(",",":"))
        if checkpoint_values.get(iteration,{}).get("assignment_sha256")!=hashlib.sha256(raw.encode("ascii")).hexdigest(): raise ValueError("checkpoint/assignment drift")
        receipt=json.loads(receipt_path.read_text()); raw=json.dumps(assignment,sort_keys=True,separators=(",",":"))
        if receipt.get("assignment_sha256")!=hashlib.sha256(raw.encode("ascii")).hexdigest() or receipt.get("ledger_sha256")!=sha(ledger_path): raise ValueError("adversary assignment/ledger binding drift")
        result=receipt.get("result",{})
        if result.get("status")=="UNCOVERED_CLASS":
            x=result.get("x")
            if not isinstance(x,int) or x<1 or any(direct_value(q,x)==assignment[q] for q in M["primes"]): raise ValueError("fabricated uncovered class")
    candidate_present=a.candidate!="-" and pathlib.Path(a.candidate).is_file()
    if candidate_present!=(t["terminal_reason"]=="COVER_FOUND_PENDING_VERIFY") or bool(t.get("candidate_present"))!=candidate_present: raise ValueError("pending-cover/candidate mismatch")
    if t["terminal_reason"]=="SOLVER_INFEASIBLE_UNVERIFIED" and candidate_present: raise ValueError("unverified infeasible emitted candidate")
    if t.get("constraints",0)<4096 or t.get("cegar_iterations",0)<0 or t.get("last_constraint",0)<1 or t.get("models_solved")!=len(checkpoints) or t.get("adversary_calls")!=len(receipt_paths): raise ValueError("counter drift")

def static_bindings()->None:
    if combined_period()!=int(M["combined_period"]): raise ValueError("combined-period drift")
    if [q for q,_,_ in order_table()]!=M["primes"] or sha(MANIFEST_PATH)=="0"*64: raise ValueError("order/manifest drift")

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("ledger",type=pathlib.Path); p.add_argument("terminal",type=pathlib.Path); p.add_argument("candidate"); p.add_argument("work",type=pathlib.Path); p.add_argument("gate",type=pathlib.Path); p.add_argument("--campaign-commit",required=True); p.add_argument("--arm",required=True); p.add_argument("--shard",type=int,required=True)
    a=p.parse_args(); static_bindings(); terminal(a); print('{"verified":true}'); return 0
if __name__=="__main__": raise SystemExit(main())
