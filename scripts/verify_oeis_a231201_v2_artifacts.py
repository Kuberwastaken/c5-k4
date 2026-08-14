#!/usr/bin/env python3
"""Fail-closed structural verifier for v2 stage artifacts; never runs a model."""
from __future__ import annotations
import argparse, hashlib, json, pathlib
from oeis_a231201_v2_common import M, MANIFEST_PATH, ZERO, assignment_hash, direct_value, sha, validate_assignment
from prepare_oeis_a231201_gate import verify as verify_gate

def chain(path:pathlib.Path)->tuple[int,str]:
    previous=ZERO; count=0
    with path.open(encoding="ascii") as f:
        for line in f:
            row=json.loads(line); digest=row.pop("row_sha256",None)
            if row.get("seq")!=count or row.get("previous_row_sha256")!=previous: raise ValueError("ledger order drift")
            actual=hashlib.sha256(json.dumps(row,sort_keys=True,separators=(",",":")).encode("ascii")).hexdigest()
            if digest!=actual: raise ValueError("ledger hash drift")
            previous=digest; count+=1
    return count,previous

def common(a,doc):
    count,last=chain(a.ledger)
    if (doc.get("ledger_rows"),doc.get("final_row_sha256"),doc.get("ledger_sha256"))!=(count,last,sha(a.ledger)): raise ValueError("terminal/ledger binding drift")
    if (doc.get("campaign_commit"),doc.get("arm"),doc.get("cell"),doc.get("round"))!=(a.campaign_commit,a.arm,a.cell,a.round): raise ValueError("stage identity drift")

def verified_gate(a)->str:
    verify_gate(a.gate,a.campaign_commit); return sha(a.gate/"gate-attestation.json")

def read_assignment(path:pathlib.Path,a)->tuple[dict,dict[int,int]]:
    value=json.loads(path.read_text()); assignment={int(k):int(v) for k,v in value["assignment"].items()}; validate_assignment(assignment,a.cell)
    if value.get("schema")!="oeis-a231201-v2-assignment-v1" or value.get("manifest_sha256")!=sha(MANIFEST_PATH) or value.get("assignment_sha256")!=assignment_hash(assignment): raise ValueError("assignment schema/hash drift")
    if (value.get("campaign_commit"),value.get("arm"),value.get("cell"),value.get("round"),value.get("slot"))!=(a.campaign_commit,a.arm,a.cell,a.round,0): raise ValueError("assignment identity drift")
    return value,assignment

def read_candidate(path:pathlib.Path,a,gate_hash:str)->tuple[dict,dict[int,int]]:
    value=json.loads(path.read_text()); assignment={int(k):int(v) for k,v in value["assignment"].items()}; validate_assignment(assignment,a.cell)
    expected={"schema":"oeis-a231201-v2-cover-pending-v1","campaign_commit":a.campaign_commit,"manifest_sha256":sha(MANIFEST_PATH),"gate_attestation_sha256":gate_hash,"arm":a.arm,"cell":a.cell,"round":a.round,"slot":0,"assignment_sha256":assignment_hash(assignment),"assignment":{str(q):assignment[q] for q in M["primes"]}}
    if value!=expected: raise ValueError("pending candidate exact binding drift")
    return value,assignment

def crt_all(assignment:dict[int,int])->tuple[int,int]:
    n=0; modulus=1
    for q in M["primes"]: n+=modulus*(((assignment[q]-n)*pow(modulus,-1,q))%q); modulus*=q
    return n%modulus,modulus

def construction(a,doc):
    if doc.get("schema")!="oeis-a231201-v2-construction-terminal-v1" or doc.get("status") not in M["terminal_vocabularies"]["construction"]: raise ValueError("construction terminal drift")
    if doc.get("manifest_sha256")!=sha(MANIFEST_PATH): raise ValueError("manifest binding drift")
    present=a.payload.is_file()
    if present!=bool(doc.get("assignment_present")): raise ValueError("assignment presence drift")
    if doc["status"]=="PREREQUISITE_NOT_RUN":
        if present or doc.get("gate_attestation_sha256") is not None or doc.get("exit_status")!=75: raise ValueError("construction prerequisite encoding drift")
    else:
        if doc.get("gate_attestation_sha256")!=verified_gate(a): raise ValueError("construction gate binding drift")
    if present:
        value,assignment=read_assignment(a.payload,a)
        if value.get("gate_attestation_sha256")!=doc.get("gate_attestation_sha256"): raise ValueError("assignment gate drift")
        if assignment_hash(assignment)!=value.get("assignment_sha256") or value.get("assignment_sha256")!=doc.get("assignment_sha256"): raise ValueError("assignment hash drift")
        if doc["status"]!="ASSIGNMENT_EMITTED": raise ValueError("assignment/status drift")
        basis_path=a.work/"basis-final.json"; basis=json.loads(basis_path.read_text())["ordered_exponents"]
        uncovered=sum(not any(direct_value(q,x)==assignment[q] for q in M["primes"]) for x in basis); prefix=None
        for q in M["primes"]:
            if all(any(direct_value(p,x)==assignment[p] for p in M["primes"] if p<=q) for x in basis): prefix=q; break
        expected_rank={"uncovered_rows":uncovered,"least_prime_prefix":prefix,"assignment":[assignment[q] for q in M["primes"]]}
        if value.get("basis_sha256")!=sha(basis_path) or value.get("basis_rows")!=len(basis) or value.get("proposal_rank")!=expected_rank: raise ValueError("assignment basis/rank drift")
    for rel,digest in doc.get("artifacts",{}).items():
        path=a.work/rel if rel.startswith("basis-") else a.payload.parent/rel
        if not path.is_file() or sha(path)!=digest: raise ValueError("construction artifact drift")
    if doc["status"]=="CAP_EXHAUSTED_AFTER_ASSIGNMENTS":
        rows=[json.loads(line) for line in a.ledger.read_text().splitlines()]
        duplicates=[row for row in rows if row.get("status")=="DUPLICATE_ASSIGNMENT_SKIPPED"]
        if not duplicates: raise ValueError("after-assignments lacks duplicate binding")
        for row in duplicates:
            if not all(isinstance(row.get(key),str) and len(row[key])==64 for key in ("assignment_sha256","original_assignment_artifact_sha256","original_adversary_receipt_sha256")) or row.get("original_adversary_status") not in {"COVER_FOUND_PENDING_VERIFY","UNCOVERED_CLASS","ADVERSARY_DEADLINE"}: raise ValueError("duplicate provenance drift")

def adversary(a,doc):
    if doc.get("schema")!="oeis-a231201-v2-adversary-terminal-v1" or doc.get("status") not in M["terminal_vocabularies"]["adversary"]: raise ValueError("adversary terminal drift")
    candidate_present=a.candidate.is_file()
    if doc["status"]=="NOT_RUN":
        if a.payload.is_file() or candidate_present or doc.get("exit_status") is not None or doc.get("result") is not None or doc.get("assignment_sha256") is not None or doc.get("gate_attestation_sha256") is not None or doc.get("candidate_sha256") is not None: raise ValueError("NOT_RUN encoding drift")
        return
    result=doc.get("result") or {}
    if doc.get("manifest_sha256")!=sha(MANIFEST_PATH) or not a.payload.is_file(): raise ValueError("adversary manifest/input drift")
    if doc["status"]=="PREREQUISITE_NOT_RUN":
        if candidate_present or doc.get("exit_status")!=75: raise ValueError("adversary prerequisite encoding drift")
        return
    gate_hash=verified_gate(a); assignment_doc,assignment=read_assignment(a.payload,a)
    if assignment_doc.get("gate_attestation_sha256")!=gate_hash or doc.get("gate_attestation_sha256")!=gate_hash or doc.get("assignment_sha256")!=assignment_hash(assignment) or doc.get("assignment_artifact_sha256")!=sha(a.payload): raise ValueError("adversary input binding drift")
    expected_result={"COVER_FOUND_PENDING_VERIFY":"COMPLETE_COVER","UNCOVERED_CLASS":"UNCOVERED_CLASS","ADVERSARY_DEADLINE":"ADVERSARY_DEADLINE"}
    if doc["status"] in expected_result and result.get("status")!=expected_result[doc["status"]]: raise ValueError("adversary result/status drift")
    if (doc.get("exit_status")==0)!=(doc["status"] in {"COVER_FOUND_PENDING_VERIFY","UNCOVERED_CLASS"}): raise ValueError("adversary exit-status drift")
    if doc["status"]=="UNCOVERED_CLASS":
        x=result.get("x")
        if not isinstance(x,int) or x<1 or any(direct_value(q,x)==assignment[q] for q in M["primes"]): raise ValueError("uncovered class drift")
    if candidate_present!=(doc["status"]=="COVER_FOUND_PENDING_VERIFY") or bool(doc.get("candidate_present"))!=candidate_present: raise ValueError("pending-cover drift")
    if candidate_present:
        candidate,candidate_assignment=read_candidate(a.candidate,a,gate_hash)
        if candidate_assignment!=assignment or candidate["assignment_sha256"]!=doc["assignment_sha256"] or doc.get("candidate_sha256")!=sha(a.candidate): raise ValueError("candidate/assignment drift")
    elif doc.get("candidate_sha256") is not None: raise ValueError("absent candidate has digest")

def final(a,doc):
    if doc.get("schema")!="oeis-a231201-v2-final-terminal-v1" or doc.get("status") not in M["terminal_vocabularies"]["final"]: raise ValueError("final terminal drift")
    candidate_present=a.payload.is_file()
    if doc["status"]=="NOT_RUN":
        if candidate_present or doc.get("exit_status") is not None or doc.get("result") is not None or doc.get("gate_attestation_sha256") is not None or doc.get("candidate_sha256") is not None or doc.get("assignment_sha256") is not None: raise ValueError("NOT_RUN encoding drift")
        return
    if doc.get("manifest_sha256")!=sha(MANIFEST_PATH) or not candidate_present: raise ValueError("final manifest/input drift")
    if doc["status"]=="PREREQUISITE_NOT_RUN":
        if doc.get("exit_status")!=75: raise ValueError("final prerequisite encoding drift")
        return
    gate_hash=verified_gate(a); _candidate,assignment=read_candidate(a.payload,a,gate_hash)
    if doc.get("gate_attestation_sha256")!=gate_hash or doc.get("candidate_sha256")!=sha(a.payload) or doc.get("assignment_sha256")!=assignment_hash(assignment): raise ValueError("final gate/candidate binding drift")
    result=doc.get("result") or {}; expected={"VERIFIED_COUNTEREXAMPLE":"COMPLETE_COVER","VERIFICATION_FAILED_UNCOVERED_CLASS":"UNCOVERED_CLASS","FINAL_VERIFIER_DEADLINE":"FINAL_VERIFIER_DEADLINE"}
    if doc["status"] in expected and result.get("status")!=expected[doc["status"]]: raise ValueError("final result/status drift")
    if (doc.get("exit_status")==0)!=(doc["status"]=="VERIFIED_COUNTEREXAMPLE"): raise ValueError("final exit-status drift")
    if doc["status"]=="VERIFIED_COUNTEREXAMPLE":
        n0,Q=crt_all(assignment); boundary=10_000_000; n=n0 if n0>boundary else n0+((boundary-n0)//Q+1)*Q
        if (doc.get("n"),doc.get("least_nonnegative_crt"),doc.get("Q"))!=(n,n0,Q) or not (n>boundary and n>max(M["primes"]) and all(n%q==assignment[q] for q in M["primes"])): raise ValueError("forged final CRT/result")
    elif doc["status"]=="VERIFICATION_FAILED_UNCOVERED_CLASS":
        x=result.get("x")
        if not isinstance(x,int) or x<1 or any(direct_value(q,x)==assignment[q] for q in M["primes"]): raise ValueError("final uncovered class drift")

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("stage",choices=["construction","adversary","final"]); p.add_argument("ledger",type=pathlib.Path); p.add_argument("terminal",type=pathlib.Path); p.add_argument("payload",type=pathlib.Path); p.add_argument("work",type=pathlib.Path); p.add_argument("--gate",type=pathlib.Path,required=True); p.add_argument("--candidate",type=pathlib.Path,required=True); p.add_argument("--campaign-commit",required=True); p.add_argument("--arm",choices=M["arms"],required=True); p.add_argument("--cell",required=True); p.add_argument("--round",type=int,required=True)
    a=p.parse_args(); doc=json.loads(a.terminal.read_text()); common(a,doc); globals()[a.stage](a,doc); print('{"verified":true}'); return 0
if __name__=="__main__": raise SystemExit(main())
