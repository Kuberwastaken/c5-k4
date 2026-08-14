#!/usr/bin/env python3
"""Independent generalized-CRT adversary and final certificate replay."""
from __future__ import annotations
import argparse, hashlib, importlib.metadata, json, math, pathlib, platform, time
from oeis_a231201_common import M, MANIFEST_PATH, Ledger, atomic_json, combined_period, crt_pair, order_table, periodic_value, queue_hash, sha
from prepare_oeis_a231201_gate import verify as verify_gate

def binding(assignment:dict[int,int])->dict:
    raw=json.dumps(assignment,sort_keys=True,separators=(",",":"))
    try: ortools_version=importlib.metadata.version("ortools")
    except importlib.metadata.PackageNotFoundError: ortools_version="absent"
    return {"assignment_sha256":hashlib.sha256(raw.encode("ascii")).hexdigest(),"manifest_sha256":sha(MANIFEST_PATH),"source_commit":M["formal_conjectures"]["commit"],"source_sha256":M["formal_conjectures"]["sha256"],"python":platform.python_version(),"ortools":ortools_version,"order_table":[list(x) for x in order_table()],"combined_period":str(combined_period())}

def refine(assignment:dict[int,int],deadline:float,ledger:Ledger)->dict:
    states=[(0,1)]
    for level,(q,order,modulus) in enumerate(order_table()):
        next_states=[]; processed=0
        for input_index,(r,current) in enumerate(states):
            step=current; limit=math.lcm(current,modulus)
            for split_index,value in enumerate(range(r,limit,step)):
                if time.monotonic()>=deadline:
                    cursor={"input_index":input_index,"input_residue":r,"input_modulus":current,"split_index":split_index,"split_value":value}
                    ledger.append({"schema":"oeis-a231201-adversary-level-v1","level":level,"q":q,"status":"DEADLINE_PREFIX","input_states":len(states),"input_processed":processed,"cursor":cursor,"partial_output_states":len(next_states),"partial_queue_sha256":queue_hash(next_states)})
                    return {"status":"DEADLINE_PREFIX","level":level,"cursor":cursor,"partial_states":len(next_states),"partial_queue_sha256":queue_hash(next_states)}
                if periodic_value(q,value)!=assignment[q]: next_states.append((value,limit))
            processed+=1
        next_states.sort()
        ledger.append({"schema":"oeis-a231201-adversary-level-v1","level":level,"q":q,"order":order,"modulus":modulus,"status":"DOMAIN_EXHAUSTED","input_states":len(states),"input_processed":processed,"output_states":len(next_states),"queue_sha256":queue_hash(next_states)})
        states=next_states
        if not states:return {"status":"COMPLETE_COVER","level":level,"states":[]}
    r,modulus=min(states,key=lambda z:(z[0] if z[0]>0 else z[1],z[1]))
    return {"status":"UNCOVERED_CLASS","x":r if r>0 else modulus,"residue":r,"modulus":modulus,"final_states":len(states),"queue_sha256":queue_hash(states)}

def coverage(args)->int:
    assignment={int(k):int(v) for k,v in json.loads(args.assignment.read_text())["assignment"].items()}
    if list(sorted(assignment))!=M["primes"] or any(not 0<=assignment[q]<q for q in assignment): raise ValueError("assignment universe drift")
    ledger=Ledger(args.ledger); started=time.monotonic()
    try: result=refine(assignment,started+M["internal_seconds"],ledger)
    finally: ledger.close()
    receipt={"schema":"oeis-a231201-adversary-terminal-v1","status":result["status"],"result":result,**binding(assignment),"ledger_rows":ledger.seq,"final_row_sha256":ledger.previous,"ledger_sha256":sha(args.ledger),"elapsed_seconds":time.monotonic()-started,"exit_status":0 if result["status"]!="DEADLINE_PREFIX" else 75}
    atomic_json(args.output,receipt)
    return 0 if result["status"]!="DEADLINE_PREFIX" else 75

def crt_all(assignment:dict[int,int])->tuple[int,int]:
    n=0; modulus=1
    for q in M["primes"]:
        k=((assignment[q]-n)*pow(modulus,-1,q))%q; n+=modulus*k; modulus*=q
    return n%modulus,modulus

def independent_coverage(assignment:dict[int,int],deadline:float,ledger:Ledger)->dict:
    """Separate CRT-intersection implementation; does not call refine()."""
    frontier={(0,1)}
    for level,(q,order,modulus) in enumerate(order_table()):
        allowed=[s for s in range(modulus) if periodic_value(q,s)!=assignment[q]]
        following=set(); processed=0
        for input_index,(r,current) in enumerate(sorted(frontier)):
            for residue_index,s in enumerate(allowed):
                if time.monotonic()>=deadline:
                    cursor={"input_index":input_index,"input_residue":r,"input_modulus":current,"allowed_residue_index":residue_index,"allowed_residue":s}
                    ledger.append({"schema":"oeis-a231201-independent-level-v1","level":level,"q":q,"status":"DEADLINE_PREFIX","cursor":cursor,"input_states":len(frontier),"partial_output_states":len(following),"partial_queue_sha256":queue_hash(sorted(following))})
                    return {"status":"DEADLINE_PREFIX","level":level,"cursor":cursor}
                merged=crt_pair(r,current,s,modulus)
                if merged is not None: following.add(merged)
            processed+=1
        frontier=following
        ledger.append({"schema":"oeis-a231201-independent-level-v1","level":level,"q":q,"order":order,"modulus":modulus,"status":"DOMAIN_EXHAUSTED","input_processed":processed,"output_states":len(frontier),"queue_sha256":queue_hash(sorted(frontier))})
        if not frontier:return {"status":"COMPLETE_COVER","level":level}
    r,modulus=min(frontier,key=lambda z:(z[0] if z[0] else z[1],z[1]))
    return {"status":"UNCOVERED_CLASS","x":r if r else modulus,"residue":r,"modulus":modulus,"final_states":len(frontier),"queue_sha256":queue_hash(sorted(frontier))}

def final(args)->int:
    candidate=json.loads(args.candidate.read_text()); assignment={int(k):int(v) for k,v in candidate["assignment"].items()}
    verify_gate(args.gate,args.campaign_commit)
    if candidate.get("schema")!="oeis-a231201-cover-pending-v1" or candidate.get("campaign_commit")!=args.campaign_commit or candidate.get("source_commit")!=M["formal_conjectures"]["commit"] or candidate.get("manifest_sha256")!=sha(MANIFEST_PATH) or candidate.get("gate_attestation_sha256")!=sha(args.gate/"gate-attestation.json"): raise ValueError("candidate identity/source drift")
    if list(sorted(assignment))!=M["primes"] or any(not 0<=assignment[q]<q for q in assignment): raise ValueError("candidate assignment universe drift")
    arm=candidate.get("arm"); shard=candidate.get("shard")
    from oeis_a231201_common import shard_fixed
    if any(assignment[q]!=a for q,a in shard_fixed(arm,shard).items()): raise ValueError("candidate shard drift")
    if order_table()!=[tuple(row) for row in candidate["order_table"]] or combined_period()!=int(M["combined_period"]) or candidate.get("combined_period")!=M["combined_period"]: raise ValueError("frozen arithmetic drift")
    ledger=Ledger(args.ledger); started=time.monotonic()
    try: result=independent_coverage(assignment,started+M["internal_seconds"],ledger)
    finally: ledger.close()
    status="DEADLINE_PREFIX"
    if result["status"]=="COMPLETE_COVER":
        n0,Q=crt_all(assignment); n=n0
        if n<=M["oeis_bfile"]["prior_boundary"]: n+=((M["oeis_bfile"]["prior_boundary"]-n)//Q+1)*Q
        if not (n>M["oeis_bfile"]["prior_boundary"] and all(n%q==assignment[q] for q in M["primes"])): raise ValueError("CRT replay failed")
        # For every positive x, coverage gives q | 2^x+n-x.  These generic
        # bounds prove each selected q is proper without evaluating target rows.
        if not (n>max(M["primes"]) and all(1<q<n+2-x for q in M["primes"] for x in (1,))): raise ValueError("proper divisor bound failed")
        status="VERIFIED_COUNTEREXAMPLE"
    elif result["status"]=="UNCOVERED_CLASS": status="VERIFICATION_FAILED_UNCOVERED_CLASS"
    receipt={"schema":"oeis-a231201-final-verification-v1","status":status,"coverage":result,**binding(assignment),"ledger_rows":ledger.seq,"final_row_sha256":ledger.previous,"ledger_sha256":sha(args.ledger),"elapsed_seconds":time.monotonic()-started,"exit_status":0 if status=="VERIFIED_COUNTEREXAMPLE" else 75}
    if status=="VERIFIED_COUNTEREXAMPLE": receipt.update({"n":n,"least_nonnegative_crt":n0,"Q":Q})
    atomic_json(args.output,receipt); return 0 if status=="VERIFIED_COUNTEREXAMPLE" else 75

def main()->int:
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="mode",required=True)
    c=sub.add_parser("coverage"); c.add_argument("assignment",type=pathlib.Path); c.add_argument("ledger",type=pathlib.Path); c.add_argument("output",type=pathlib.Path)
    f=sub.add_parser("final"); f.add_argument("candidate",type=pathlib.Path); f.add_argument("ledger",type=pathlib.Path); f.add_argument("output",type=pathlib.Path); f.add_argument("gate",type=pathlib.Path); f.add_argument("--campaign-commit",required=True)
    a=p.parse_args(); return coverage(a) if a.mode=="coverage" else final(a)
if __name__=="__main__": raise SystemExit(main())
