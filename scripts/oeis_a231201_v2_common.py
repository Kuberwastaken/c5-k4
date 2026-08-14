#!/usr/bin/env python3
"""V2 frozen primitives. Importing this module evaluates no target assignment."""
from __future__ import annotations
import hashlib, json, os, pathlib
from typing import Any
import oeis_a231201_common as v1

ROOT=pathlib.Path(__file__).resolve().parents[1]
FREEZE=ROOT/"results/expansion/live-search-2026-08-14/oeis-a231201-v2-development"
MANIFEST_PATH=FREEZE/"manifest.json"
M=json.loads(MANIFEST_PATH.read_text())
ZERO="0"*64

canonical=v1.canonical; sha=v1.sha; exact_commit=v1.exact_commit
order_table=v1.order_table; combined_period=v1.combined_period
positive_representative=v1.positive_representative; periodic_value=v1.periodic_value
direct_value=v1.direct_value; signature=v1.signature; crt_pair=v1.crt_pair
queue_hash=v1.queue_hash; is_prime_trial=v1.is_prime_trial

def atomic_json(path:pathlib.Path,value:dict)->None:
    path.parent.mkdir(parents=True,exist_ok=True); temp=path.with_suffix(path.suffix+".tmp")
    with temp.open("xb") as f: f.write(canonical(value)); f.flush(); os.fsync(f.fileno())
    os.replace(temp,path)
    descriptor=os.open(path.parent,os.O_RDONLY)
    try: os.fsync(descriptor)
    finally: os.close(descriptor)

class Ledger(v1.Ledger):
    pass

def cell_fixed(cell:str)->dict[int,int]:
    try: a2,a3=(int(x) for x in cell.split("_"))
    except Exception as exc: raise ValueError("cell must be A2_A3") from exc
    if (a2,a3) not in {(x["a2"],x["a3"]) for x in M["partition_cells"]}: raise ValueError("unknown partition cell")
    return {2:a2,3:a3}

def assignment_hash(assignment:dict[int,int])->str:
    raw=json.dumps({str(q):assignment[q] for q in M["primes"]},sort_keys=True,separators=(",",":"))
    return hashlib.sha256(raw.encode("ascii")).hexdigest()

def bit_reverse_12(n:int)->int:
    return int(f"{n:012b}"[::-1],2)

def low_discrepancy_seed()->list[int]:
    lo,hi=M["seed"]["lo"],M["seed"]["hi"]
    return sorted(range(lo,hi+1),key=lambda x:(bit_reverse_12(x-lo),x))

def active_rows(cell:str, xs:list[int])->list[int]:
    fixed=cell_fixed(cell)
    return [x for x in xs if all(direct_value(q,x)!=a for q,a in fixed.items())]

def assignment_covers(assignment:dict[int,int],xs:list[int])->bool:
    return all(any(direct_value(q,x)==assignment[q] for q in M["primes"]) for x in xs)

def validate_assignment(value:dict[int,int],cell:str)->None:
    if sorted(value)!=M["primes"] or any(not 0<=value[q]<q for q in value): raise ValueError("assignment universe drift")
    if any(value[q]!=a for q,a in cell_fixed(cell).items()): raise ValueError("assignment cell drift")

def prior_feedback(path:pathlib.Path|None)->list[int]:
    if path is None or not path.is_file(): return []
    doc=json.loads(path.read_text())
    if doc.get("status")!="UNCOVERED_CLASS": return []
    x=doc.get("result",{}).get("x")
    return [x] if isinstance(x,int) and x>0 else []
