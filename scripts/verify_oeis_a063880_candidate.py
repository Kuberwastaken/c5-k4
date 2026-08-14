#!/usr/bin/env python3
"""Independent fail-closed replay for A063880 certificates and terminals."""
from __future__ import annotations
import argparse, hashlib, json, math, pathlib
from fractions import Fraction
from prepare_oeis_a063880_gate import DEFAULT_MANIFEST, M, sha, verify

ZERO="0"*64

def ef(p:int,e:int)->Fraction:
    return Fraction((p**(e+1)-1)//(p-1),1+p**e)

def independent_primitive(factors:list[tuple[int,int]])->bool:
    target=math.prod(p**e for p,e in factors); stack=[(0,1,Fraction(1))]
    while stack:
        i,n,r=stack.pop()
        if i==len(factors):
            if n!=target and r==2: return False
            continue
        p,e=factors[i]
        for j in range(e,-1,-1): stack.append((i+1,n*p**j,r*(Fraction(1) if j==0 else ef(p,j))))
    return True

def replay_candidate(path:pathlib.Path,bundle:pathlib.Path,commit:str)->dict:
    commit=commit.lower(); gate=verify(bundle,commit); document=json.loads(path.read_text())
    if document.get("schema")!="oeis-a063880-certificate-v1" or document.get("campaign_commit")!=commit: raise ValueError("certificate identity drift")
    if document.get("source_commit")!=M["formal_conjectures"]["commit"] or document.get("manifest_sha256")!=sha(DEFAULT_MANIFEST) or document.get("gate_attestation_sha256")!=sha(bundle/"gate-attestation.json"): raise ValueError("certificate source/gate drift")
    arm=document.get("arm"); shard=document.get("shard")
    if arm not in M["arms"] or not isinstance(shard,int) or not 0<=shard<M["shards"]: raise ValueError("certificate arm drift")
    raw=document.get("factors")
    if not isinstance(raw,list) or not raw: raise ValueError("factorization missing")
    factors=[]; seen=set(); spec=M["arms"][arm]
    for item in raw:
        if not isinstance(item,list) or len(item)!=2 or not all(isinstance(x,int) for x in item): raise ValueError("malformed factor")
        p,e=item
        if p in seen or p not in spec["primes"] or e not in spec["exponents"]: raise ValueError("factor outside frozen universe")
        seen.add(p); factors.append((p,e))
    if factors!=sorted(factors): raise ValueError("factors not canonical")
    n=math.prod(p**e for p,e in factors); s=math.prod((p**(e+1)-1)//(p-1) for p,e in factors); u=math.prod(1+p**e for p,e in factors)
    maximum=factors[-1][0]; primitive=independent_primitive(factors); mod_failure=n%216!=108; unique_failure=primitive and n!=108
    expected={"schema":"oeis-a063880-certificate-v1","campaign_commit":commit,"source_commit":M["formal_conjectures"]["commit"],"manifest_sha256":sha(DEFAULT_MANIFEST),"gate_attestation_sha256":sha(bundle/"gate-attestation.json"),"arm":arm,"shard":shard,"n":n,"factors":raw,"sigma":s,"usigma":u,"ratio_numerator":s,"ratio_denominator":u,"primitive":primitive,"mod_216":n%216,"disproves_mod_216_of_a":mod_failure,"disproves_unique_primitive_108":unique_failure,"historical_exclusion_checked":n>=M["historical_exclusion_upper_exclusive"]}
    if document!=expected: raise ValueError("certificate arithmetic drift")
    if not (M["universe"]["minimum_core"]<=n<=M["universe"]["maximum_core"] and len(factors)>=M["universe"]["minimum_factors"] and len(factors)<=spec["maximum_factors"] and spec["maximum_prime_min"]<=maximum<=spec["maximum_prime_max"]): raise ValueError("certificate outside finite arm")
    if s!=2*u or not (mod_failure or unique_failure): raise ValueError("certificate does not refute target")
    bind_candidate_to_shard(arm,tuple(factors),shard)
    return document

def verify_chain(path:pathlib.Path,commit:str,arm:str,shard:int)->tuple[list[dict],str]:
    rows=[]; previous=ZERO
    for seq,line in enumerate(path.read_text(encoding="ascii").splitlines()):
        row=json.loads(line); digest=row.pop("row_sha256",None)
        if row.get("seq")!=seq or row.get("previous_row_sha256")!=previous or row.get("campaign_commit")!=commit or row.get("arm")!=arm or row.get("shard")!=shard: raise ValueError("ledger identity/order drift")
        raw=json.dumps(row,sort_keys=True,separators=(",",":")); actual=hashlib.sha256(raw.encode("ascii")).hexdigest()
        if digest!=actual: raise ValueError("ledger chain drift")
        row["row_sha256"]=digest; previous=digest; rows.append(row)
    return rows,previous

def bind_certificate(certificate:dict,arm:str,shard:int)->None:
    if certificate.get("arm")!=arm or certificate.get("shard")!=shard: raise ValueError("certificate/terminal arm-shard mismatch")

def candidate_coordinates(arm:str,factors:tuple[tuple[int,int],...])->tuple[int,tuple[int,int,tuple[tuple[int,int],...]]]:
    spec=M["arms"][arm]; primes=spec["primes"]; mid=len(primes)//2; left_primes=set(primes[:mid]); right_primes=set(primes[mid:])
    left_factors=tuple(x for x in factors if x[0] in left_primes); right_factors=tuple(x for x in factors if x[0] in right_primes)
    if len(left_factors)+len(right_factors)!=len(factors): raise ValueError("candidate factor outside arm split")
    left=list(independent_states(primes[:mid],spec)); right=list(independent_states(primes[mid:],spec))
    left_hits=[i for i,row in enumerate(left) if row[2]==left_factors]; right_hits=[row for row in right if row[2]==right_factors]
    if len(left_hits)!=1 or len(right_hits)!=1: raise ValueError("candidate MITM coordinate is not unique")
    return left_hits[0],right_hits[0]

def bind_candidate_to_shard(arm:str,factors:tuple[tuple[int,int],...],shard:int)->int:
    ordinal,_=candidate_coordinates(arm,factors)
    if ordinal%M["shards"]!=shard: raise ValueError("candidate does not belong to claimed shard")
    return ordinal

def validate_search_evidence(progress:list[dict],matches:list[dict],t:dict,arm:str,shard:int,certificate:dict|None)->None:
    spec=M["arms"][arm]; primes=spec["primes"]; mid=len(primes)//2
    right=list(independent_states(primes[mid:],spec)); left=list(independent_states(primes[:mid],spec))
    right_count=t.get("right_states"); left_seen=t.get("left_states_seen")
    if not isinstance(right_count,int) or not 0<=right_count<=len(right) or not isinstance(left_seen,int) or not 0<=left_seen<=len(left): raise ValueError("terminal state counter range drift")
    expected_progress=[]
    for count in range(256,right_count+1,256):
        n,r,_=right[count-1]; expected_progress.append(("BUILD_RIGHT",count,n,[r.numerator,r.denominator]))
    final_phase="BUILD_RIGHT_COMPLETE" if right_count==len(right) else "BUILD_RIGHT_FINAL"
    if right_count:
        n,r,_=right[right_count-1]; expected_progress.append((final_phase,right_count,n,[r.numerator,r.denominator]))
    actual_progress=[(r.get("phase"),r.get("right_states"),r.get("last_right_n"),r.get("last_right_ratio")) for r in progress]
    if actual_progress!=expected_progress: raise ValueError("right progress semantic drift")
    if left_seen and right_count!=len(right): raise ValueError("left phase began before right completion")
    expected_ordinals=[i for i in range(left_seen) if i%M["shards"]==shard]
    actual_ordinals=[r.get("left_ordinal") for r in matches]
    if actual_ordinals!=expected_ordinals: raise ValueError("owned left ordinal gap/duplicate/order drift")
    right_by_ratio={}
    for rn,rr,rf in right: right_by_ratio.setdefault(rr,[]).append((rn,rf))
    total_matches=0
    for row,ordinal in zip(matches,expected_ordinals):
        ln,lr,lf=left[ordinal]; complement=Fraction(2,1)/lr; compatible=right_by_ratio.get(complement,[])
        expected=(ln,[lr.numerator,lr.denominator],[complement.numerator,complement.denominator],len(compatible))
        actual=(row.get("left_n"),row.get("left_ratio"),row.get("complement"),row.get("right_matches"))
        if actual!=expected: raise ValueError("left/complement/match semantic drift")
        usable=[(rn,rf) for rn,rf in compatible if ln<=M["universe"]["maximum_core"]//rn]
        if certificate is not None and ordinal==expected_ordinals[-1]:
            factors=tuple(tuple(x) for x in certificate["factors"]); candidate_ordinal,candidate_right=candidate_coordinates(arm,factors)
            if candidate_ordinal!=ordinal: raise ValueError("certificate attached before/after its left state")
            try: position=usable.index((candidate_right[0],candidate_right[2]))+1
            except ValueError as exc: raise ValueError("certificate right match absent from visited row") from exc
            total_matches+=position
        else:
            total_matches+=len(usable)
    if certificate is None:
        if t.get("exact_ratio_matches")!=total_matches: raise ValueError("exact-match counter drift")
    elif (not expected_ordinals or candidate_coordinates(arm,tuple(tuple(x) for x in certificate["factors"]))[0]!=expected_ordinals[-1]
          or t.get("exact_ratio_matches")!=total_matches): raise ValueError("certificate match-prefix counter drift")
    if t.get("left_states_owned")!=len(matches): raise ValueError("owned-left counter drift")
    if t.get("terminal_reason")=="DOMAIN_EXHAUSTED" and (right_count!=len(right) or left_seen!=len(left)): raise ValueError("false domain exhaustion")

def terminal(ledger_path:pathlib.Path,terminal_path:pathlib.Path,certificate_path:pathlib.Path|None,bundle:pathlib.Path,commit:str,arm:str,shard:int)->dict:
    verify(bundle,commit); t=json.loads(terminal_path.read_text()); rows,last=verify_chain(ledger_path,commit,arm,shard)
    if t.get("schema")!="oeis-a063880-terminal-v1" or t.get("campaign_commit")!=commit or t.get("source_commit")!=M["formal_conjectures"]["commit"] or t.get("gate_attestation_sha256")!=sha(bundle/"gate-attestation.json") or t.get("arm")!=arm or t.get("shard")!=shard: raise ValueError("terminal identity drift")
    if t.get("ledger_rows")!=len(rows) or t.get("final_row_sha256")!=last or t.get("ledger_sha256")!=sha(ledger_path): raise ValueError("terminal ledger binding drift")
    reason=t.get("terminal_reason"); present=certificate_path is not None
    if reason not in {"DOMAIN_EXHAUSTED","DEADLINE_PREFIX","CERTIFICATE_FOUND"}: raise ValueError("invalid terminal reason")
    if bool(t.get("certificate_present"))!=present or (reason=="CERTIFICATE_FOUND")!=present: raise ValueError("terminal certificate mismatch")
    certificate=None
    if present:
        certificate=replay_candidate(certificate_path,bundle,commit)
        bind_certificate(certificate,arm,shard)
    progress=[r for r in rows if r.get("schema")=="oeis-a063880-progress-v1"]
    matches=[r for r in rows if r.get("schema")=="oeis-a063880-match-row-v1"]
    if len(progress)+len(matches)!=len(rows): raise ValueError("unknown ledger row schema")
    validate_search_evidence(progress,matches,t,arm,shard,certificate)
    return t

def independent_states(primes:list[int],spec:dict):
    powers={p:sorted([(e,p**e,ef(p,e)) for e in spec["exponents"]],key=lambda x:(-x[2],x[0])) for p in primes}
    cap=M["universe"]["maximum_core"]
    def walk(i,n,r,factors):
        if i==len(primes): yield n,r,factors; return
        yield from walk(i+1,n,r,factors)
        if len(factors)>=spec["maximum_factors"]: return
        for e,pe,q in powers[primes[i]]:
            if n<=cap//pe: yield from walk(i+1,n*pe,r*q,factors+((primes[i],e),))
    yield from walk(0,1,Fraction(1),())

def main()->int:
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="mode",required=True)
    c=sub.add_parser("candidate"); c.add_argument("certificate",type=pathlib.Path); c.add_argument("bundle",type=pathlib.Path); c.add_argument("--campaign-commit",required=True)
    c=sub.add_parser("terminal"); c.add_argument("ledger",type=pathlib.Path); c.add_argument("terminal",type=pathlib.Path); c.add_argument("certificate"); c.add_argument("bundle",type=pathlib.Path); c.add_argument("--campaign-commit",required=True); c.add_argument("--arm",choices=tuple(M["arms"]),required=True); c.add_argument("--shard",type=int,required=True)
    a=p.parse_args()
    if a.mode=="candidate": value=replay_candidate(a.certificate,a.bundle,a.campaign_commit); print(json.dumps({"verified":True,"n":value["n"],"arm":value["arm"]},sort_keys=True,separators=(",",":")))
    else: terminal(a.ledger,a.terminal,None if a.certificate=="-" else pathlib.Path(a.certificate),a.bundle,a.campaign_commit,a.arm,a.shard); print('{"verified":true}')
    return 0
if __name__=="__main__": raise SystemExit(main())
