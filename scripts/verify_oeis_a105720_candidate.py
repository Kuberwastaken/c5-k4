#!/usr/bin/env python3
"""Independent certificate and terminal verifier (imports no discovery code)."""
from __future__ import annotations
import argparse, hashlib, json, math, pathlib, struct

ROOT=pathlib.Path(__file__).resolve().parents[1]
FREEZE=ROOT/"results/expansion/live-search-2026-08-14/oeis-a105720-development"
M=json.loads((FREEZE/"manifest.json").read_text())
ZERO="0"*64

def sha(path):
    h=hashlib.sha256()
    with pathlib.Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def canonical(row): return json.dumps(row,sort_keys=True,separators=(",",":"))

def verify_gate(gate:pathlib.Path, commit:str):
    att=json.loads((gate/"gate-attestation.json").read_text())
    if att.get("campaign_commit")!=commit or att.get("schema")!="oeis-a105720-gate-v1": raise ValueError("gate binding")
    expected_names={"105720.lean","b105720.txt","manifest.json","source-status-attestation.json","primes.u32"}
    if set(att.get("files",{}))!=expected_names: raise ValueError("gate file set")
    for name,digest in att["files"].items():
        if sha(gate/name)!=digest: raise ValueError(f"gate hash {name}")
    if json.loads((gate/"manifest.json").read_text())!=M: raise ValueError("gate manifest")
    if sha(gate/"105720.lean")!=M["formal_conjectures"]["sha256"]: raise ValueError("immutable Lean source")
    if sha(gate/"b105720.txt")!=M["oeis_bfile"]["sha256"]: raise ValueError("immutable OEIS source")
    if (gate/"source-status-attestation.json").read_bytes()!=(FREEZE/"source-status-attestation.json").read_bytes(): raise ValueError("source/status attestation")
    return sha(gate/"gate-attestation.json")

def belongs(arm,shard,n):
    a=M["arms"][arm]
    if arm in ("CATALOGUE","WALL_NAVIGATION"):
        return a["lo"]<=n<=a["hi"] and (n-a["lo"])%M["shards"]==shard
    if not a["lo"]<=n<a["lo"]+a["width"]: return False
    # multiplier is invertible modulo width; recover the frozen global index.
    i=((n-a["lo"]-a["offset"])*pow(a["multiplier"],-1,a["width"]))%a["width"]
    return i<a["count"] and i%M["shards"]==shard

def arm_values(arm,shard):
    a=M["arms"][arm]
    if arm in ("CATALOGUE","WALL_NAVIGATION"):
        yield from range(a["lo"]+shard,a["hi"]+1,M["shards"])
    else:
        for i in range(shard,a["count"],M["shards"]):
            yield a["lo"]+((a["multiplier"]*i+a["offset"])%a["width"])

def square_residue(value):
    for modulus in M["arms"]["WALL_NAVIGATION"]["moduli"]:
        if value%modulus not in {x*x%modulus for x in range(modulus)}: return False
    return True

def sieve_to(limit):
    bits=bytearray(b"\x01")*(limit+1); bits[0:2]=b"\x00\x00"
    for p in range(2,math.isqrt(limit)+1):
        if bits[p]: bits[p*p:limit+1:p]=b"\x00"*(((limit-p*p)//p)+1)
    return [i for i,x in enumerate(bits) if x]

def verified_gate_primes(gate:pathlib.Path):
    raw=(gate/"primes.u32").read_bytes()
    if len(raw)%4: raise ValueError("prime table bytes")
    claimed=list(struct.unpack(f"<{len(raw)//4}I",raw))
    if len(claimed)!=M["prime_count"]: raise ValueError("prime table count")
    reconstructed=sieve_to(claimed[-1])
    if reconstructed!=claimed: raise ValueError("prime table content")
    return claimed

def candidate(path:pathlib.Path,gate:pathlib.Path,commit:str):
    gate_sha=verify_gate(gate,commit); c=json.loads(path.read_text())
    required={"schema","campaign_commit","source_commit","gate_attestation_sha256","arm","shard","n","a_n","exact_square","square_root","prime_n","prime_2n"}
    if not required<=c.keys() or c["schema"]!="oeis-a105720-certificate-v1": raise ValueError("certificate shape")
    if c["campaign_commit"]!=commit or c["source_commit"]!=M["formal_conjectures"]["commit"] or c["gate_attestation_sha256"]!=gate_sha: raise ValueError("certificate binding")
    n=int(c["n"]); arm=c["arm"]; shard=int(c["shard"])
    if arm not in M["arms"] or not 0<=shard<M["shards"] or not belongs(arm,shard,n): raise ValueError("domain provenance")
    if n<=0 or n in M["known_square_indices"]: raise ValueError("not an extra index")
    primes=sieve_to(int(c["prime_2n"]))
    if len(primes)!=2*n or primes[n-1]!=c["prime_n"] or primes[-1]!=c["prime_2n"]: raise ValueError("prime boundaries")
    value=sum(primes[n-1:2*n]); root=math.isqrt(value)
    if value!=c["a_n"] or root!=c["square_root"] or root*root!=value or c["exact_square"] is not True: raise ValueError("not an exact counterexample")

def verify_chain(ledger:pathlib.Path,commit:str,arm:str,shard:int,primes=None,gate_sha=None):
    previous=ZERO; count=screened=evaluated=errors=0; rows=[]; last_schema=None
    expected=iter(arm_values(arm,shard)) if primes is not None else None
    prefix=None
    if primes is not None:
        prefix=[0]
        for p in primes: prefix.append(prefix[-1]+p)
    with ledger.open(encoding="ascii") as f:
        for line in f:
            row=json.loads(line); digest=row.pop("row_sha256")
            if row.get("seq")!=count or row.get("previous_row_sha256")!=previous or hashlib.sha256(canonical(row).encode("ascii")).hexdigest()!=digest: raise ValueError("ledger chain")
            if row.get("campaign_commit")!=commit or row.get("arm")!=arm or row.get("shard")!=shard: raise ValueError("ledger binding")
            if row.get("schema")=="oeis-a105720-row-v1":
                if primes is not None:
                    try: n=next(expected)
                    except StopIteration: raise ValueError("ledger beyond frozen domain")
                    if row.get("n")!=n or not belongs(arm,shard,n): raise ValueError("ledger domain order")
                    value=prefix[2*n]-prefix[n-1]; root=math.isqrt(value)
                    compatible=True if arm!="WALL_NAVIGATION" else square_residue(value)
                    exact=compatible and root*root==value
                    residual=min(value-root*root,(root+1)*(root+1)-value)
                    if row.get("source_commit")!=M["formal_conjectures"]["commit"] or row.get("gate_attestation_sha256")!=gate_sha: raise ValueError("row source binding")
                    if row.get("a_n")!=value or row.get("screen_pass") is not compatible or row.get("exact_square") is not exact or row.get("nearest_square_distance")!=residual: raise ValueError("row arithmetic")
                screened+=1; evaluated+=int(row.get("screen_pass") is True); rows.append(dict(row,row_sha256=digest))
            elif row.get("schema")=="oeis-a105720-error-v1": errors+=1
            else: raise ValueError("ledger row schema")
            last_schema=row.get("schema")
            previous=digest; count+=1
    return previous,count,screened,evaluated,rows,errors,last_schema

def validate_completion(reason,screened,domain_size,rows,certificate_present):
    if (reason=="CERTIFICATE_FOUND")!=certificate_present: raise ValueError("terminal/certificate mismatch")
    if reason=="DOMAIN_EXHAUSTED" and screened!=domain_size: raise ValueError("false domain exhaustion")
    if reason=="DEADLINE_PREFIX" and screened>=domain_size: raise ValueError("invalid deadline prefix")
    if reason=="CERTIFICATE_FOUND" and (not rows or rows[-1].get("exact_square") is not True): raise ValueError("certificate is not final exact row")

def terminal(ledger:pathlib.Path,receipt:pathlib.Path,certificate_path:pathlib.Path|None,gate:pathlib.Path,commit:str,arm:str,shard:int):
    gate_sha=verify_gate(gate,commit)
    primes=verified_gate_primes(gate)
    previous,count,screened,evaluated,rows,errors,last_schema=verify_chain(ledger,commit,arm,shard,primes,gate_sha)
    t=json.loads(receipt.read_text()); allowed={"DOMAIN_EXHAUSTED","DEADLINE_PREFIX","CERTIFICATE_FOUND","WORKER_ERROR"}
    if t.get("schema")!="oeis-a105720-terminal-v1" or t.get("terminal_reason") not in allowed: raise ValueError("terminal shape")
    if t.get("campaign_commit")!=commit or t.get("source_commit")!=M["formal_conjectures"]["commit"] or t.get("gate_attestation_sha256")!=gate_sha or t.get("arm")!=arm or t.get("shard")!=shard: raise ValueError("terminal binding")
    if t.get("ledger_rows")!=count or t.get("final_row_sha256")!=previous or t.get("ledger_sha256")!=sha(ledger): raise ValueError("terminal ledger binding")
    if t.get("screened")!=screened or t.get("exact_evaluated")!=evaluated: raise ValueError("terminal counter binding")
    present=certificate_path is not None and certificate_path.is_file()
    domain_size=sum(1 for _ in arm_values(arm,shard))
    validate_completion(t["terminal_reason"],screened,domain_size,rows,present)
    if t["terminal_reason"]=="WORKER_ERROR":
        if errors!=1 or last_schema!="oeis-a105720-error-v1": raise ValueError("worker error receipt mismatch")
    elif errors: raise ValueError("unexpected error row")
    if t["terminal_reason"]=="CERTIFICATE_FOUND":
        c=json.loads(certificate_path.read_text())
        for key in ("campaign_commit","source_commit","gate_attestation_sha256","arm","shard","n","a_n","exact_square"):
            if c.get(key)!=rows[-1].get(key): raise ValueError("certificate/last-row mismatch")
        candidate(certificate_path,gate,commit)

def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="mode",required=True)
    c=sub.add_parser("candidate"); c.add_argument("certificate",type=pathlib.Path); c.add_argument("gate",type=pathlib.Path); c.add_argument("--campaign-commit",required=True)
    t=sub.add_parser("terminal"); t.add_argument("ledger",type=pathlib.Path); t.add_argument("receipt",type=pathlib.Path); t.add_argument("certificate"); t.add_argument("gate",type=pathlib.Path); t.add_argument("--campaign-commit",required=True); t.add_argument("--arm",required=True); t.add_argument("--shard",type=int,required=True)
    a=p.parse_args()
    if a.mode=="candidate": candidate(a.certificate,a.gate,a.campaign_commit)
    else: terminal(a.ledger,a.receipt,None if a.certificate=="-" else pathlib.Path(a.certificate),a.gate,a.campaign_commit,a.arm,a.shard)
if __name__=="__main__": main()
