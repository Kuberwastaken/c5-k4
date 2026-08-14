#!/usr/bin/env python3
"""Frozen CEGAR coordinator for one disjoint A231201 assignment shard."""
from __future__ import annotations
import argparse, hashlib, importlib.metadata, json, os, pathlib, platform, subprocess, sys, time, traceback
from typing import Optional
from oeis_a231201_common import M, MANIFEST_PATH, Ledger, atomic_json, combined_period, exact_commit, order_table, sha, shard_fixed, signature
from prepare_oeis_a231201_gate import verify as verify_gate

def assignment_hash(value:dict[int,int])->str:
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":")).encode("ascii")).hexdigest()

def solve_once(constraints:list[int],fixed:dict[int,int],seconds:float)->tuple[str,Optional[dict[int,int]],dict]:
    from ortools.sat.python import cp_model
    model=cp_model.CpModel(); choose={}
    for q in M["primes"]:
        for a in range(q): choose[q,a]=model.new_bool_var(f"a_{q}_{a}")
        model.add_exactly_one(choose[q,a] for a in range(q))
    for q,a in sorted(fixed.items()):model.add(choose[q,a]==1)
    for x in constraints:model.add_bool_or(choose[q,a] for q,a in signature(x))
    solver=cp_model.CpSolver(); solver.parameters.max_time_in_seconds=max(.001,seconds); solver.parameters.num_search_workers=1; solver.parameters.random_seed=0
    status=solver.solve(model); name=solver.status_name(status)
    assignment=None
    if status in (cp_model.FEASIBLE,cp_model.OPTIMAL): assignment={q:next(a for a in range(q) if solver.value(choose[q,a])) for q in M["primes"]}
    stats={"status":name,"wall_time":solver.wall_time,"branches":solver.num_branches,"conflicts":solver.num_conflicts}
    return name,assignment,stats

def run(a)->int:
    exact_commit(a.campaign_commit); gate=verify_gate(a.gate_bundle,a.campaign_commit); fixed=shard_fixed(a.arm,a.shard)
    started=time.monotonic(); deadline=started+M["internal_seconds"]; ledger=Ledger(a.ledger); constraints=list(range(M["initial_exponents"]["lo"],M["initial_exponents"]["hi"]+1)); previous_checkpoint="0"*64; iteration=0; models_solved=0; adversary_calls=0; reason="DEADLINE_PREFIX"; candidate=None; adversary_hashes={}; checkpoint_hashes={}
    try:
        while time.monotonic()<deadline:
            name,assignment,stats=solve_once(constraints,fixed,deadline-time.monotonic())
            models_solved+=1
            ledger.append({"schema":"oeis-a231201-master-model-v1","campaign_commit":a.campaign_commit,"arm":a.arm,"shard":a.shard,"iteration":iteration,"constraints":len(constraints),"last_constraint":constraints[-1],"solver":stats})
            checkpoint={"schema":"oeis-a231201-checkpoint-v1","campaign_commit":a.campaign_commit,"arm":a.arm,"shard":a.shard,"iteration":iteration,"constraints":constraints,"solver":stats,"previous_checkpoint_sha256":previous_checkpoint}
            if assignment is None:
                reason="SOLVER_INFEASIBLE_UNVERIFIED" if name=="INFEASIBLE" else "DEADLINE_PREFIX"
                checkpoint_path=a.work/f"checkpoint-{iteration:04d}.json"; atomic_json(checkpoint_path,checkpoint); previous_checkpoint=sha(checkpoint_path); checkpoint_hashes[checkpoint_path.name]=previous_checkpoint; break
            checkpoint["assignment_sha256"]=assignment_hash(assignment); checkpoint_path=a.work/f"checkpoint-{iteration:04d}.json"; atomic_json(checkpoint_path,checkpoint); previous_checkpoint=sha(checkpoint_path); checkpoint_hashes[checkpoint_path.name]=previous_checkpoint
            assignment_path=a.work/f"assignment-{iteration:04d}.json"; atomic_json(assignment_path,{"schema":"oeis-a231201-assignment-v1","campaign_commit":a.campaign_commit,"arm":a.arm,"shard":a.shard,"iteration":iteration,"assignment":{str(q):assignment[q] for q in M["primes"]}})
            adversary_hashes[assignment_path.name]=sha(assignment_path)
            adv_ledger=a.work/f"adversary-{iteration:04d}.jsonl"; adv_receipt=a.work/f"adversary-{iteration:04d}.json"
            remaining=max(.001,deadline-time.monotonic())
            try: code=subprocess.run([sys.executable,str(pathlib.Path(__file__).with_name("verify_oeis_a231201_coverage.py")),"coverage",str(assignment_path),str(adv_ledger),str(adv_receipt)],timeout=remaining,check=False,start_new_session=True).returncode
            except subprocess.TimeoutExpired: code=124
            adversary_calls+=1
            if not adv_receipt.is_file(): reason="DEADLINE_PREFIX"; break
            receipt=json.loads(adv_receipt.read_text()); adversary_hashes[str(adv_ledger.name)]=sha(adv_ledger); adversary_hashes[str(adv_receipt.name)]=sha(adv_receipt)
            ledger.append({"schema":"oeis-a231201-adversary-response-v1","campaign_commit":a.campaign_commit,"arm":a.arm,"shard":a.shard,"iteration":iteration,"exit_code":code,"status":receipt.get("status"),"receipt_sha256":sha(adv_receipt)})
            result=receipt["result"]
            if result["status"]=="COMPLETE_COVER":
                candidate={"schema":"oeis-a231201-cover-pending-v1","campaign_commit":a.campaign_commit,"source_commit":M["formal_conjectures"]["commit"],"manifest_sha256":sha(MANIFEST_PATH),"gate_attestation_sha256":sha(a.gate_bundle/"gate-attestation.json"),"arm":a.arm,"shard":a.shard,"assignment":{str(q):assignment[q] for q in M["primes"]},"order_table":[list(row) for row in order_table()],"combined_period":str(combined_period()),"cegar_iterations":iteration+1}
                atomic_json(a.candidate,candidate); reason="COVER_FOUND_PENDING_VERIFY"; break
            if result["status"]!="UNCOVERED_CLASS": reason="DEADLINE_PREFIX"; break
            x=int(result["x"])
            if x in constraints: raise ValueError("adversary repeated existing constraint")
            constraints.append(x); iteration+=1
    except BaseException:
        reason="WORKER_ERROR"; ledger.append({"schema":"oeis-a231201-error-v1","campaign_commit":a.campaign_commit,"arm":a.arm,"shard":a.shard,"error":traceback.format_exc()})
    finally:
        ledger.close(); terminal={"schema":"oeis-a231201-master-terminal-v1","campaign_commit":a.campaign_commit,"source_commit":M["formal_conjectures"]["commit"],"source_sha256":M["formal_conjectures"]["sha256"],"manifest_sha256":sha(MANIFEST_PATH),"gate_attestation_sha256":sha(a.gate_bundle/"gate-attestation.json"),"python":platform.python_version(),"ortools":importlib.metadata.version("ortools"),"order_table":[list(x) for x in order_table()],"combined_period":str(combined_period()),"arm":a.arm,"shard":a.shard,"fixed":fixed,"terminal_reason":reason,"cegar_iterations":iteration,"models_solved":models_solved,"adversary_calls":adversary_calls,"constraints":len(constraints),"last_constraint":constraints[-1],"last_checkpoint_sha256":previous_checkpoint,"checkpoint_artifacts":checkpoint_hashes,"adversary_artifacts":adversary_hashes,"ledger_rows":ledger.seq,"final_row_sha256":ledger.previous,"ledger_sha256":sha(a.ledger),"elapsed_seconds":time.monotonic()-started,"candidate_present":candidate is not None,"exit_status":0 if reason in {"COVER_FOUND_PENDING_VERIFY","SOLVER_INFEASIBLE_UNVERIFIED"} else 75}
        atomic_json(a.terminal,terminal)
    return 0 if reason in {"COVER_FOUND_PENDING_VERIFY","SOLVER_INFEASIBLE_UNVERIFIED"} else 75

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--arm",choices=tuple(M["partition"]["arms"]),required=True); p.add_argument("--shard",type=int,choices=M["partition"]["shards"],required=True); p.add_argument("--campaign-commit",required=True); p.add_argument("--gate-bundle",type=pathlib.Path,required=True); p.add_argument("--work",type=pathlib.Path,required=True); p.add_argument("--ledger",type=pathlib.Path,required=True); p.add_argument("--terminal",type=pathlib.Path,required=True); p.add_argument("--candidate",type=pathlib.Path,required=True)
    a=p.parse_args(); a.work.mkdir(parents=True,exist_ok=True); return run(a)
if __name__=="__main__": raise SystemExit(main())
