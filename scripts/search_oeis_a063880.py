#!/usr/bin/env python3
"""Frozen exact MITM search for A063880 primitive cores; never a claim."""
from __future__ import annotations
import argparse, hashlib, json, math, os, pathlib, time, traceback
from fractions import Fraction
from prepare_oeis_a063880_gate import DEFAULT_MANIFEST, M, sha, verify

ZERO="0"*64

class Ledger:
    def __init__(self,path:pathlib.Path):
        path.parent.mkdir(parents=True,exist_ok=True); self.path=path; self.file=path.open("x",encoding="ascii"); self.seq=0; self.previous=ZERO
    def append(self,payload:dict)->str:
        row=dict(payload); row["seq"]=self.seq; row["previous_row_sha256"]=self.previous
        raw=json.dumps(row,sort_keys=True,separators=(",",":")); digest=hashlib.sha256(raw.encode("ascii")).hexdigest(); row["row_sha256"]=digest
        self.file.write(json.dumps(row,sort_keys=True,separators=(",",":"))+"\n"); self.file.flush(); os.fsync(self.file.fileno()); self.seq+=1; self.previous=digest; return digest
    def close(self): self.file.close()

def atomic_json(path:pathlib.Path,value:dict)->None:
    temp=path.with_suffix(path.suffix+".tmp")
    with temp.open("x",encoding="ascii") as f: json.dump(value,f,sort_keys=True,separators=(",",":")); f.write("\n"); f.flush(); os.fsync(f.fileno())
    os.replace(temp,path)

def euler_factor(p:int,e:int)->Fraction:
    return Fraction(sum(p**j for j in range(e+1)),1+p**e)

def ordered_powers(p:int,exponents:list[int])->list[tuple[int,int,Fraction]]:
    values=[(e,p**e,euler_factor(p,e)) for e in exponents]
    return sorted(values,key=lambda x:(-x[2],x[0]))

def states(primes:list[int],exponents:list[int],maximum_factors:int,maximum_core:int):
    """Canonical DFS: omit first, then exact-factor-descending prime powers."""
    powers={p:ordered_powers(p,exponents) for p in primes}
    def walk(index:int,n:int,ratio:Fraction,factors:tuple[tuple[int,int],...]):
        if index==len(primes): yield n,ratio,factors; return
        yield from walk(index+1,n,ratio,factors)
        if len(factors)>=maximum_factors: return
        p=primes[index]
        for e,pe,r in powers[p]:
            if n<=maximum_core//pe: yield from walk(index+1,n*pe,ratio*r,factors+((p,e),))
    yield from walk(0,1,Fraction(1),())

def sigma_usigma(factors:tuple[tuple[int,int],...])->tuple[int,int]:
    s=u=1
    for p,e in factors: s*=sum(p**j for j in range(e+1)); u*=1+p**e
    return s,u

def is_primitive(factors:tuple[tuple[int,int],...])->bool:
    """Exact proper-divisor replay, including exponent-one neutral factors."""
    target=math.prod(p**e for p,e in factors)
    def walk(i:int,n:int,ratio:Fraction)->bool:
        if i==len(factors): return n!=target and ratio==2
        p,e=factors[i]
        for j in range(e+1):
            r=Fraction(1) if j==0 else euler_factor(p,j)
            if walk(i+1,n*p**j,ratio*r): return True
        return False
    return not walk(0,1,Fraction(1))

def arm_accepts(arm:str,factors:tuple[tuple[int,int],...],n:int)->bool:
    if not factors or not M["universe"]["minimum_core"]<=n<=M["universe"]["maximum_core"]: return False
    spec=M["arms"][arm]; maximum=factors[-1][0]
    return (len(factors)>=M["universe"]["minimum_factors"] and len(factors)<=spec["maximum_factors"]
            and spec["maximum_prime_min"]<=maximum<=spec["maximum_prime_max"])

def candidate_document(arm:str,shard:int,commit:str,gate_sha:str,factors:tuple[tuple[int,int],...])->dict|None:
    n=math.prod(p**e for p,e in factors); s,u=sigma_usigma(factors)
    if s!=2*u or not arm_accepts(arm,factors,n): return None
    primitive=is_primitive(factors); mod_failure=n%216!=108; unique_failure=primitive and n!=108
    if not (mod_failure or unique_failure): return None
    return {"schema":"oeis-a063880-certificate-v1","campaign_commit":commit,"source_commit":M["formal_conjectures"]["commit"],"manifest_sha256":sha(DEFAULT_MANIFEST),"gate_attestation_sha256":gate_sha,
            "arm":arm,"shard":shard,"n":n,"factors":[list(x) for x in factors],"sigma":s,"usigma":u,"ratio_numerator":s,"ratio_denominator":u,
            "primitive":primitive,"mod_216":n%216,"disproves_mod_216_of_a":mod_failure,"disproves_unique_primitive_108":unique_failure,"historical_exclusion_checked":n>=M["historical_exclusion_upper_exclusive"]}

def run(args)->int:
    gate=verify(args.gate_bundle,args.campaign_commit); gate_sha=sha(args.gate_bundle/"gate-attestation.json"); spec=M["arms"][args.arm]
    primes=spec["primes"]; midpoint=len(primes)//2; left_primes=primes[:midpoint]; right_primes=primes[midpoint:]
    deadline=time.monotonic()+M["internal_seconds"]; ledger=Ledger(args.ledger); right_by_ratio={}; right_count=left_seen=left_owned=matched=0; reason="DOMAIN_EXHAUSTED"; candidate=None; last_right=None
    try:
        for n,ratio,factors in states(right_primes,spec["exponents"],spec["maximum_factors"],M["universe"]["maximum_core"]):
            if time.monotonic()>=deadline: reason="DEADLINE_PREFIX"; break
            right_by_ratio.setdefault(ratio,[]).append((n,factors)); right_count+=1; last_right=(n,ratio)
            if right_count%256==0: ledger.append({"schema":"oeis-a063880-progress-v1","campaign_commit":args.campaign_commit,"arm":args.arm,"shard":args.shard,"phase":"BUILD_RIGHT","right_states":right_count,"last_right_n":n,"last_right_ratio":[ratio.numerator,ratio.denominator]})
        if last_right is not None:
            n,ratio=last_right; ledger.append({"schema":"oeis-a063880-progress-v1","campaign_commit":args.campaign_commit,"arm":args.arm,"shard":args.shard,"phase":"BUILD_RIGHT_FINAL" if reason=="DEADLINE_PREFIX" else "BUILD_RIGHT_COMPLETE","right_states":right_count,"last_right_n":n,"last_right_ratio":[ratio.numerator,ratio.denominator]})
        if reason!="DEADLINE_PREFIX":
            for ln,lr,lf in states(left_primes,spec["exponents"],spec["maximum_factors"],M["universe"]["maximum_core"]):
                if time.monotonic()>=deadline: reason="DEADLINE_PREFIX"; break
                ordinal=left_seen; left_seen+=1
                if ordinal%M["shards"]!=args.shard: continue
                left_owned+=1; complement=Fraction(2,1)/lr
                rows=right_by_ratio.get(complement,())
                ledger.append({"schema":"oeis-a063880-match-row-v1","campaign_commit":args.campaign_commit,"source_commit":M["formal_conjectures"]["commit"],"gate_attestation_sha256":gate_sha,"arm":args.arm,"shard":args.shard,"left_ordinal":ordinal,"left_n":ln,"left_ratio":[lr.numerator,lr.denominator],"complement":[complement.numerator,complement.denominator],"right_matches":len(rows)})
                for rn,rf in rows:
                    if ln>M["universe"]["maximum_core"]//rn: continue
                    factors=tuple(sorted(lf+rf)); matched+=1
                    candidate=candidate_document(args.arm,args.shard,args.campaign_commit,gate_sha,factors)
                    if candidate:
                        atomic_json(args.certificate,candidate); reason="CERTIFICATE_FOUND"; break
                if candidate: break
    except BaseException:
        reason="WORKER_ERROR"; ledger.append({"schema":"oeis-a063880-error-v1","campaign_commit":args.campaign_commit,"arm":args.arm,"shard":args.shard,"error":traceback.format_exc()}); raise
    finally:
        ledger.close(); terminal={"schema":"oeis-a063880-terminal-v1","campaign_commit":args.campaign_commit,"source_commit":M["formal_conjectures"]["commit"],"gate_attestation_sha256":gate_sha,"arm":args.arm,"shard":args.shard,"terminal_reason":reason,"right_states":right_count,"left_states_seen":left_seen,"left_states_owned":left_owned,"exact_ratio_matches":matched,"ledger_rows":ledger.seq,"final_row_sha256":ledger.previous,"ledger_sha256":sha(args.ledger),"certificate_present":candidate is not None}
        atomic_json(args.terminal,terminal)
    return 0

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--arm",choices=tuple(M["arms"]),required=True); p.add_argument("--shard",type=int,choices=range(M["shards"]),required=True); p.add_argument("--campaign-commit",required=True); p.add_argument("--gate-bundle",type=pathlib.Path,required=True); p.add_argument("--ledger",type=pathlib.Path,required=True); p.add_argument("--terminal",type=pathlib.Path,required=True); p.add_argument("--certificate",type=pathlib.Path,required=True)
    args=p.parse_args();
    if len(args.campaign_commit)!=40 or any(c not in "0123456789abcdef" for c in args.campaign_commit): p.error("exact lowercase campaign commit required")
    return run(args)
if __name__=="__main__": raise SystemExit(main())
