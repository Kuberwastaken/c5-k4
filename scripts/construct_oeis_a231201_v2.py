#!/usr/bin/env python3
"""Bounded v2 assignment constructors; never runs the exact target adversary."""
from __future__ import annotations
import argparse, json, pathlib, platform, time, traceback
from oeis_a231201_v2_common import M, MANIFEST_PATH, Ledger, active_rows, assignment_covers, assignment_hash, atomic_json, cell_fixed, direct_value, exact_commit, low_discrepancy_seed, sha, validate_assignment
from prepare_oeis_a231201_gate import verify as verify_gate

def incidence(xs:list[int])->dict[tuple[int,int],int]:
    out:dict[tuple[int,int],int]={}
    for i,x in enumerate(xs):
        bit=1<<i
        for q in M["primes"][2:]: out[q,direct_value(q,x)]=out.get((q,direct_value(q,x)),0)|bit
    return out

def coverage_score(assignment:dict[int,int],inc:dict[tuple[int,int],int],row_count:int,skip:int|None=None,replace:tuple[int,int]|None=None)->tuple[int,int,tuple[int,...]]:
    once=0; multiple=0
    for q in M["primes"][2:]:
        if q==skip: continue
        bits=inc.get((q,assignment[q]),0); new_multiple=multiple|(once&bits); once=(once^bits)&~new_multiple; multiple=new_multiple
    if replace is not None:
        bits=inc.get(replace,0); new_multiple=multiple|(once&bits); once=(once^bits)&~new_multiple
    mask=(1<<row_count)-1
    return ((mask&~(once|multiple)).bit_count(),once.bit_count(),tuple(assignment[q] if replace is None or q!=replace[0] else replace[1] for q in M["primes"]))

def least_prime_prefix(assignment:dict[int,int],inc:dict[tuple[int,int],int],row_count:int)->int|None:
    covered=0; mask=(1<<row_count)-1
    for q in M["primes"]:
        if q>=5: covered|=inc.get((q,assignment[q]),0)
        if covered==mask:return q
    return None

def greedy(xs:list[int],cell:str,deadline:float,rotation:int=0)->tuple[dict[int,int],dict]:
    inc=incidence(xs); assignment=cell_fixed(cell); uncovered=(1<<len(xs))-1; moves=0
    for q in M["primes"][2:]:
        a=min(range(q),key=lambda a:(-(inc.get((q,a),0)&uncovered).bit_count(),a))
        assignment[q]=a; uncovered&=~inc.get((q,a),0)
    best=coverage_score(assignment,inc,len(xs)); improved=True
    while time.monotonic()<deadline and moves<M["greedy"]["max_moves"] and uncovered:
        improved=False
        for q in M["primes"][2:]:
            if time.monotonic()>=deadline: break
            choice=min(range(q),key=lambda a:coverage_score(assignment,inc,len(xs),skip=q,replace=(q,a)))
            if choice!=assignment[q]: assignment[q]=choice; moves+=1; improved=True
        covered=0
        for q in M["primes"][2:]: covered|=inc.get((q,assignment[q]),0)
        uncovered=((1<<len(xs))-1)&~covered
        score=coverage_score(assignment,inc,len(xs))
        if score<best: best=score
        if uncovered and not improved:
            row=(uncovered&-uncovered).bit_length()-1; q=M["primes"][2+((row+rotation+moves)//M["greedy"]["perturbation_period"]%53)]
            assignment[q]=direct_value(q,xs[row]); moves+=1
    final_score=coverage_score(assignment,inc,len(xs))
    return assignment,{"moves":moves,"uncovered":final_score[0],"singly_covered":final_score[1],"score_assignment":list(final_score[2]),"best_lexicographic_score":{"uncovered":best[0],"singly_covered":best[1],"assignment":list(best[2])},"least_prime_prefix":least_prime_prefix(assignment,inc,len(xs))}

def compressed_cp(xs:list[int],cell:str,hint:dict[int,int],deadline:float,ledger:Ledger,*,growth_pool:list[int]|None=None,logical_start:int=0,work:pathlib.Path|None=None,artifacts:dict|None=None)->tuple[str,dict[int,int]|None,int]:
    from ortools.sat.python import cp_model
    fixed=cell_fixed(cell); inc=incidence(xs); rounds=0; last="UNKNOWN"
    while rounds<M["cp_slices_per_construction"] and time.monotonic()<deadline:
        logical=logical_start+rounds
        if growth_pool is not None and logical>0 and logical%M["small_basis"]["growth_every_rounds"]==0:
            old=len(xs); wanted=min(len(growth_pool),old+M["small_basis"]["growth_rows"]); delta=[x for x in growth_pool if x not in set(xs)][:wanted-old]
            xs.extend(delta); inc=incidence(xs)
            delta_path=work/f"basis-delta-{logical:04d}.json"; atomic_json(delta_path,{"schema":"oeis-a231201-v2-basis-delta-v1","logical_master_round":logical,"previous_rows":old,"added_exponents":delta,"ordered_basis_rows":len(xs)})
            artifacts[delta_path.name]=sha(delta_path); ledger.append({"schema":"oeis-a231201-v2-basis-growth-v1","logical_master_round":logical,"previous_rows":old,"added_rows":len(delta),"basis_rows":len(xs),"delta_sha256":artifacts[delta_path.name]})
        model=cp_model.CpModel(); choose={}
        ordered=[]
        for q in M["primes"][2:]:
            residues=sorted(a for a in range(q) if inc.get((q,a),0))
            ranked=sorted(residues,key=lambda a:(-inc[q,a].bit_count(),a))
            for a in ranked: choose[q,a]=model.new_bool_var(f"a_{q}_{a}"); ordered.append(choose[q,a])
            model.add(sum(choose[q,a] for a in residues)<=1)
        for i,x in enumerate(xs): model.add_bool_or(choose[q,direct_value(q,x)] for q in M["primes"][2:] if (q,direct_value(q,x)) in choose)
        for (q,a),var in choose.items(): model.add_hint(var,int(hint.get(q)==a))
        model.add_decision_strategy(ordered,cp_model.CHOOSE_FIRST,cp_model.SELECT_MAX_VALUE)
        solver=cp_model.CpSolver(); solver.parameters.max_time_in_seconds=min(M["cp_slice_seconds"],max(.001,deadline-time.monotonic())); solver.parameters.num_search_workers=1; solver.parameters.random_seed=0
        status=solver.solve(model); last=solver.status_name(status); rounds+=1
        ledger.append({"schema":"oeis-a231201-v2-cp-slice-v1","slice":rounds-1,"status":last,"basis_rows":len(xs),"wall_time":solver.wall_time,"branches":solver.num_branches,"conflicts":solver.num_conflicts,"remaining_seconds":max(0,deadline-time.monotonic())})
        if status in (cp_model.FEASIBLE,cp_model.OPTIMAL):
            result=dict(fixed)
            for q in M["primes"][2:]:
                picked=[a for a in range(q) if (q,a) in choose and solver.value(choose[q,a])]
                result[q]=picked[0] if picked else (hint[q] if q in hint else 0)
            return last,result,rounds
        if status==cp_model.INFEASIBLE: return last,None,rounds
    return last,None,rounds

def prior_records(paths:list[pathlib.Path],receipts:list[pathlib.Path],cell:str,arm:str,campaign_commit:str,gate_hash:str)->list[dict]:
    if len(paths)!=len(receipts): raise ValueError("prior assignment/receipt arity drift")
    records=[]
    for path,receipt_path in zip(paths,receipts):
        receipt=json.loads(receipt_path.read_text()) if receipt_path.is_file() else None
        if not path.is_file():
            if receipt is None or receipt.get("status") not in {"NOT_RUN","PREREQUISITE_NOT_RUN"}: raise ValueError("missing assignment lacks honest adversary receipt")
            continue
        doc=json.loads(path.read_text()); value={int(k):int(v) for k,v in doc["assignment"].items()}; validate_assignment(value,cell); digest=assignment_hash(value)
        if doc.get("schema")!="oeis-a231201-v2-assignment-v1" or doc.get("manifest_sha256")!=sha(MANIFEST_PATH) or doc.get("gate_attestation_sha256")!=gate_hash or doc.get("assignment_sha256")!=digest or (doc.get("campaign_commit"),doc.get("arm"),doc.get("cell"),doc.get("slot"))!=(campaign_commit,arm,cell,0): raise ValueError("prior assignment binding drift")
        if receipt is None or receipt.get("assignment_sha256")!=digest or receipt.get("assignment_artifact_sha256")!=sha(path) or receipt.get("gate_attestation_sha256")!=gate_hash or receipt.get("manifest_sha256")!=sha(MANIFEST_PATH): raise ValueError("prior adversary binding drift")
        if receipt.get("status") not in {"COVER_FOUND_PENDING_VERIFY","UNCOVERED_CLASS","ADVERSARY_DEADLINE"}: raise ValueError("prior assignment was not adversary-submitted")
        if (receipt.get("campaign_commit"),receipt.get("arm"),receipt.get("cell"),receipt.get("round"),receipt.get("slot"))!=(campaign_commit,arm,cell,doc.get("round"),0): raise ValueError("prior receipt identity drift")
        records.append({"assignment":value,"assignment_sha256":digest,"assignment_artifact_sha256":sha(path),"adversary_receipt_sha256":sha(receipt_path),"adversary_status":receipt["status"],"round":doc["round"],"feedback_x":receipt.get("result",{}).get("x") if receipt["status"]=="UNCOVERED_CLASS" else None})
    return records

def load_hint(records:list[dict])->tuple[dict[int,int]|None,str]:
    for record in reversed(records):
        value=record["assignment"]
        return value,f"prior-round-{record['round']}:{record['assignment_sha256']}"
    return None,"deterministic-greedy"

def run(a)->int:
    started=time.monotonic(); deadline=started+M["internal_seconds"]-M["finalization_reserve_seconds"]
    ledger=Ledger(a.ledger); artifacts={}; emitted=None; status="PREREQUISITE_NOT_RUN"; rounds=0; fixed={}; gate_hash=None; prerequisite_error=None; stage_ready=False
    try:
        exact_commit(a.campaign_commit); fixed=cell_fixed(a.cell)
        if a.prerequisite_check_exit_code: raise ValueError(f"outer prerequisite check failed: {a.prerequisite_check_exit_code}")
        verify_gate(a.gate,a.campaign_commit); gate_hash=sha(a.gate/"gate-attestation.json"); status="CAP_EXHAUSTED_NO_ASSIGNMENT"
        records=prior_records(a.prior_assignment,a.prior_receipt,a.cell,a.arm,a.campaign_commit,gate_hash)
        stage_ready=True
        feedback=[r["feedback_x"] for r in records if r["feedback_x"] is not None]
        full=active_rows(a.cell,list(range(M["seed"]["lo"],M["seed"]["hi"]+1)))
        hint,hint_source=load_hint(records)
        if a.arm=="SMALL_BASIS_CEGAR":
            perm=active_rows(a.cell,low_discrepancy_seed()); logical=a.round*M["cp_slices_per_construction"]
            size=min(len(perm),M["small_basis"]["initial_rows"]+(logical//M["small_basis"]["growth_every_rounds"])*M["small_basis"]["growth_rows"])
            basis=list(dict.fromkeys(perm[:size]+feedback))
        else: basis=list(dict.fromkeys(full+feedback))
        basis_doc={"schema":"oeis-a231201-v2-basis-v1","campaign_commit":a.campaign_commit,"arm":a.arm,"cell":a.cell,"round":a.round,"fixed":fixed,"ordered_exponents":basis,"feedback_exponents":feedback}
        atomic_json(a.work/"basis-0000.json",basis_doc); artifacts["basis-0000.json"]=sha(a.work/"basis-0000.json")
        ledger.append({"schema":"oeis-a231201-v2-basis-bound-v1","campaign_commit":a.campaign_commit,"arm":a.arm,"cell":a.cell,"round":a.round,"basis_rows":len(basis),"basis_sha256":artifacts["basis-0000.json"],"feedback_rows":len(feedback)})
        if hint is None: hint,_stats=greedy(basis,a.cell,deadline,rotation=a.round); hint_source="deterministic-greedy"
        if a.arm=="DETERMINISTIC_GREEDY_REPAIR": assignment,stats=greedy(basis,a.cell,deadline,rotation=a.round); rounds=1; solver_status="HEURISTIC_COMPLETE" if stats["uncovered"]==0 else "HEURISTIC_PARTIAL"; ledger.append({"schema":"oeis-a231201-v2-greedy-round-v1","campaign_commit":a.campaign_commit,"arm":a.arm,"cell":a.cell,"round":a.round,"basis_rows":len(basis),**stats,"remaining_seconds":max(0,deadline-time.monotonic())})
        else: solver_status,assignment,rounds=compressed_cp(basis,a.cell,hint,deadline,ledger,growth_pool=perm if a.arm=="SMALL_BASIS_CEGAR" else None,logical_start=a.round*M["cp_slices_per_construction"],work=a.work,artifacts=artifacts)
        atomic_json(a.work/"basis-final.json",{"schema":"oeis-a231201-v2-basis-final-v1","campaign_commit":a.campaign_commit,"arm":a.arm,"cell":a.cell,"round":a.round,"ordered_exponents":basis}); artifacts["basis-final.json"]=sha(a.work/"basis-final.json")
        if assignment is not None and assignment_covers(assignment,basis):
            validate_assignment(assignment,a.cell); digest=assignment_hash(assignment)
            basis_inc=incidence(basis); prefix=least_prime_prefix(assignment,basis_inc,len(basis)); proposal_score=coverage_score(assignment,basis_inc,len(basis))
            prior_hashes={r["assignment_sha256"] for r in records}
            if digest not in prior_hashes:
                emitted={"schema":"oeis-a231201-v2-assignment-v1","campaign_commit":a.campaign_commit,"manifest_sha256":sha(MANIFEST_PATH),"gate_attestation_sha256":gate_hash,"arm":a.arm,"cell":a.cell,"round":a.round,"slot":0,"basis_rows":len(basis),"basis_sha256":artifacts["basis-final.json"],"hint_source":hint_source,"proposal_rank":{"uncovered_rows":proposal_score[0],"least_prime_prefix":prefix,"assignment":list(proposal_score[2])},"assignment_sha256":digest,"assignment":{str(q):assignment[q] for q in M["primes"]}}
                atomic_json(a.assignment,emitted); artifacts[a.assignment.name]=sha(a.assignment); status="ASSIGNMENT_EMITTED"
            else:
                original=next(r for r in records if r["assignment_sha256"]==digest)
                ledger.append({"schema":"oeis-a231201-v2-duplicate-assignment-v1","campaign_commit":a.campaign_commit,"arm":a.arm,"cell":a.cell,"round":a.round,"assignment_sha256":digest,"original_round":original["round"],"original_assignment_artifact_sha256":original["assignment_artifact_sha256"],"original_adversary_receipt_sha256":original["adversary_receipt_sha256"],"original_adversary_status":original["adversary_status"],"status":"DUPLICATE_ASSIGNMENT_SKIPPED"}); status="CAP_EXHAUSTED_AFTER_ASSIGNMENTS"
        elif solver_status=="INFEASIBLE": status="BASIS_INFEASIBLE_UNVERIFIED"
    except BaseException:
        prerequisite_error=traceback.format_exc()
        if stage_ready: status="WORKER_ERROR"
        ledger.append({"schema":"oeis-a231201-v2-error-v1","campaign_commit":a.campaign_commit,"arm":a.arm,"cell":a.cell,"round":a.round,"status":status,"traceback":prerequisite_error})
    finally:
        ledger.close(); terminal={"schema":"oeis-a231201-v2-construction-terminal-v1","campaign_commit":a.campaign_commit,"manifest_sha256":sha(MANIFEST_PATH),"gate_attestation_sha256":gate_hash,"python":platform.python_version(),"arm":a.arm,"cell":a.cell,"round":a.round,"fixed":fixed,"status":status,"prerequisite_error":prerequisite_error,"basis_rows":len(basis) if 'basis' in locals() else 0,"construction_rounds":rounds,"assignment_present":emitted is not None,"assignment_sha256":emitted and emitted["assignment_sha256"],"artifacts":artifacts,"ledger_rows":ledger.seq,"final_row_sha256":ledger.previous,"ledger_sha256":sha(a.ledger),"elapsed_seconds":time.monotonic()-started,"exit_status":0 if status in {"ASSIGNMENT_EMITTED","BASIS_INFEASIBLE_UNVERIFIED","CAP_EXHAUSTED_AFTER_ASSIGNMENTS"} else 75}
        atomic_json(a.terminal,terminal)
    return terminal["exit_status"]

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--arm",choices=M["arms"],required=True); p.add_argument("--cell",required=True); p.add_argument("--round",type=int,choices=range(M["construction_rounds"]),required=True); p.add_argument("--campaign-commit",required=True); p.add_argument("--gate",type=pathlib.Path,required=True); p.add_argument("--work",type=pathlib.Path,required=True); p.add_argument("--ledger",type=pathlib.Path,required=True); p.add_argument("--terminal",type=pathlib.Path,required=True); p.add_argument("--assignment",type=pathlib.Path,required=True); p.add_argument("--prerequisite-check-exit-code",type=int,default=0); p.add_argument("--prior-assignment",type=pathlib.Path,action="append",default=[]); p.add_argument("--prior-receipt",type=pathlib.Path,action="append",default=[])
    a=p.parse_args(); a.work.mkdir(parents=True,exist_ok=True); return run(a)
if __name__=="__main__": raise SystemExit(main())
