#!/usr/bin/env python3
"""Prepare/verify the content-locked A063880 historical-table gate."""
from __future__ import annotations
import argparse, hashlib, json, math, os, pathlib, subprocess, sys
from typing import Any

ROOT=pathlib.Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST=ROOT/"results/expansion/live-search-2026-08-14/oeis-a063880-development/manifest.json"
M=json.loads(DEFAULT_MANIFEST.read_text())
ATTESTATION_SCHEMA="oeis-a063880-gate-attestation-v1"
CHUNK_SCHEMA="oeis-a063880-gate-chunk-v1"

def sha(path:pathlib.Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""): h.update(block)
    return h.hexdigest()

def canonical(value:Any)->bytes:
    return (json.dumps(value,sort_keys=True,separators=(",",":"))+"\n").encode("ascii")

def self_hash(value:dict)->str:
    copy=dict(value); copy.pop("receipt_sha256",None); copy.pop("attestation_sha256",None)
    return hashlib.sha256(canonical(copy)).hexdigest()

def atomic_json(path:pathlib.Path,value:dict)->None:
    temp=path.with_suffix(path.suffix+".tmp")
    with temp.open("xb") as f: f.write(canonical(value)); f.flush(); os.fsync(f.fileno())
    os.replace(temp,path)

def copy_fsync(source:pathlib.Path,target:pathlib.Path)->None:
    with source.open("rb") as incoming,target.open("xb") as outgoing:
        for block in iter(lambda:incoming.read(1<<20),b""): outgoing.write(block)
        outgoing.flush(); os.fsync(outgoing.fileno())

def exact_commit(value:str)->str:
    if len(value)!=40 or any(c not in "0123456789abcdef" for c in value): raise ValueError("exact lowercase campaign commit required")
    return value

def factor(n:int)->dict[int,int]:
    out={}; d=2
    while d*d<=n:
        while n%d==0: out[d]=out.get(d,0)+1; n//=d
        d=3 if d==2 else d+2
    if n>1: out[n]=out.get(n,0)+1
    return out

def sigma_usigma(factors:dict[int,int])->tuple[int,int]:
    sigma=unitary=1
    for p,e in factors.items():
        sigma*=sum(p**j for j in range(e+1)); unitary*=1+p**e
    return sigma,unitary

def primitive_core(factors:dict[int,int])->int:
    return math.prod(p**e for p,e in factors.items() if e>=2)

def parse_bfile(path:pathlib.Path)->list[tuple[int,int]]:
    if sha(path)!=M["oeis_bfile"]["sha256"]: raise ValueError("b-file hash drift")
    rows=[]
    for line in path.read_text(encoding="ascii").splitlines():
        fields=line.split()
        if len(fields)!=2: raise ValueError("malformed b-file")
        rows.append((int(fields[0]),int(fields[1])))
    spec=M["oeis_bfile"]
    if len(rows)!=spec["rows"] or [i for i,_ in rows]!=list(range(1,len(rows)+1)) or rows[-1]!=(spec["last_index"],spec["last_value"]):
        raise ValueError("b-file coverage drift")
    return rows

def verify_sources(lean:pathlib.Path,source:pathlib.Path,bfile:pathlib.Path)->list[tuple[int,int]]:
    if sha(lean)!=M["formal_conjectures"]["sha256"]: raise ValueError("Lean source hash drift")
    text=lean.read_text()
    for token in ("theorem mod_216_of_a", "theorem unique_primitive_108", "category research open"):
        if token not in text: raise ValueError("Lean declaration/status drift")
    if sha(source)!=M["oeis_source"]["sha256"]: raise ValueError("OEIS source hash drift")
    record=source.read_text()
    for token in ("The only primitive term below 10^18 is 108.", "Confirmed up to 10^7", "#39 Aug 31 2024 04:33:09"):
        if token not in record: raise ValueError("OEIS historical statement drift")
    return parse_bfile(bfile)

def check_chunk(rows:list[tuple[int,int]],start:int,end:int)->dict:
    bad=[]
    for index,value in rows[start:end]:
        factors=factor(value); s,u=sigma_usigma(factors)
        if s!=2*u or value%216!=108 or primitive_core(factors)!=108: bad.append(index)
    receipt={"schema":CHUNK_SCHEMA,"start_offset":start,"end_offset":end,"rows":end-start,"bad_indices":bad}
    receipt["receipt_sha256"]=self_hash(receipt); return receipt

def prepare(lean:pathlib.Path,source:pathlib.Path,bfile:pathlib.Path,out:pathlib.Path,commit:str)->dict:
    commit=exact_commit(commit); rows=verify_sources(lean,source,bfile)
    out.mkdir(parents=True,exist_ok=False); snapshots=out/"snapshots"; snapshots.mkdir(); chunks=out/"chunks"; chunks.mkdir()
    for src,name in ((lean,"63880.lean"),(source,"A063880.seq"),(bfile,"b063880.txt")): copy_fsync(src,snapshots/name)
    receipts=[]; chunk_size=250
    for start in range(0,len(rows),chunk_size):
        end=min(start+chunk_size,len(rows)); path=chunks/f"{start:05d}-{end:05d}.json"
        subprocess.run([sys.executable,__file__,"chunk",str(bfile),str(start),str(end),str(path)],check=True,timeout=M["child_seconds"])
        row=json.loads(path.read_text());
        if row.get("receipt_sha256")!=self_hash(row) or row.get("bad_indices"): raise ValueError("historical gate chunk failed")
        receipts.append({"path":str(path.relative_to(out)),"sha256":sha(path),**row})
    att={"schema":ATTESTATION_SCHEMA,"campaign_commit":commit,"manifest_sha256":sha(DEFAULT_MANIFEST),
         "historical_exclusion":{"primitive_unique_below":M["historical_exclusion_upper_exclusive"],"source_statement":True},
         "table":{"rows":len(rows),"first":rows[0],"last":rows[-1],"all_equation":True,"all_mod_216":108,"all_primitive_core":108},
         "snapshots":{name:sha(snapshots/name) for name in ("63880.lean","A063880.seq","b063880.txt")},"chunks":receipts}
    att["attestation_sha256"]=self_hash(att); atomic_json(out/"gate-attestation.json",att); return att

def verify_chunk_set(rows:list[tuple[int,int]],chunks:list[dict],bundle:pathlib.Path)->None:
    expected_bounds=[(start,min(start+250,len(rows))) for start in range(0,len(rows),250)]
    if not isinstance(chunks,list) or len(chunks)!=len(expected_bounds): raise ValueError("chunk coverage cardinality drift")
    for row,(start,end) in zip(chunks,expected_bounds):
        expected_path=f"chunks/{start:05d}-{end:05d}.json"
        if row.get("path")!=expected_path or row.get("start_offset")!=start or row.get("end_offset")!=end: raise ValueError("chunk coverage order/gap drift")
        path=bundle/expected_path
        if not path.is_file() or sha(path)!=row.get("sha256"): raise ValueError("chunk digest drift")
        value=json.loads(path.read_text())
        expected=check_chunk(rows,start,end)
        if value!=expected or row!={"path":expected_path,"sha256":sha(path),**expected}: raise ValueError("chunk semantic receipt drift")

def verify(bundle:pathlib.Path,commit:str)->dict:
    commit=exact_commit(commit); att=json.loads((bundle/"gate-attestation.json").read_text())
    if att.get("schema")!=ATTESTATION_SCHEMA or att.get("attestation_sha256")!=self_hash(att): raise ValueError("gate attestation drift")
    if set(att)!={"schema","campaign_commit","manifest_sha256","historical_exclusion","table","snapshots","chunks","attestation_sha256"}: raise ValueError("gate attestation key drift")
    if att.get("campaign_commit")!=commit or att.get("manifest_sha256")!=sha(DEFAULT_MANIFEST): raise ValueError("gate binding drift")
    snapshots=bundle/"snapshots"; rows=verify_sources(snapshots/"63880.lean",snapshots/"A063880.seq",snapshots/"b063880.txt")
    expected_table={"rows":len(rows),"first":list(rows[0]),"last":list(rows[-1]),"all_equation":True,"all_mod_216":108,"all_primitive_core":108}
    expected_snapshots={name:sha(snapshots/name) for name in ("63880.lean","A063880.seq","b063880.txt")}
    if att.get("table")!=expected_table or att.get("snapshots")!=expected_snapshots or att.get("historical_exclusion")!={"primitive_unique_below":10**18,"source_statement":True}: raise ValueError("gate coverage drift")
    verify_chunk_set(rows,att.get("chunks"),bundle)
    return att

def main()->int:
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="mode",required=True)
    a=sub.add_parser("prepare"); a.add_argument("lean",type=pathlib.Path); a.add_argument("source",type=pathlib.Path); a.add_argument("bfile",type=pathlib.Path); a.add_argument("output",type=pathlib.Path); a.add_argument("--campaign-commit",required=True)
    a=sub.add_parser("verify"); a.add_argument("bundle",type=pathlib.Path); a.add_argument("--campaign-commit",required=True)
    a=sub.add_parser("chunk"); a.add_argument("bfile",type=pathlib.Path); a.add_argument("start",type=int); a.add_argument("end",type=int); a.add_argument("output",type=pathlib.Path)
    args=p.parse_args()
    if args.mode=="prepare": prepare(args.lean,args.source,args.bfile,args.output,args.campaign_commit)
    elif args.mode=="verify": verify(args.bundle,args.campaign_commit)
    else:
        rows=parse_bfile(args.bfile); receipt=check_chunk(rows,args.start,args.end); atomic_json(args.output,receipt)
    return 0
if __name__=="__main__": raise SystemExit(main())
