#!/usr/bin/env python3
"""Independent replay of A056777 v2 algebraic surgery evidence."""
from __future__ import annotations

import argparse, bisect, hashlib, json, math, pathlib
from collections import namedtuple

from prepare_oeis_a056777_v2_gate import MANIFEST, M, sha, verify

ZERO = "0"*64
PrimePair = namedtuple("PrimePair", "product left_rank right_rank left right")
STOPS = ("ZERO_DENOMINATOR","K_SIGN","K_NONINTEGRAL","PARTNER_NONINTEGRAL","PRODUCT_MISMATCH","NONCANONICAL","BAND","NONPRIME","PRIOR_FROZEN","C_IDENTITY","SURVIVOR")
PROGRESS_KEYS = {"schema","campaign_commit","arm","shard","visited","last_coordinate","last_outcome","counts"}
ROW_KEYS = PROGRESS_KEYS | {"seq","previous_row_sha256","row_sha256"}
TERMINAL_KEYS = {"schema","campaign_commit","source_commit","gate_attestation_sha256","arm","shard",
                 "tuple_domain_only","visited","last_coordinate","last_outcome","counts","terminal_reason",
                 "certificate_present","worker_error","ledger_rows","final_row_sha256","ledger_sha256"}


def independently_sieve(count: int) -> list[int]:
    ceiling = 8192
    while True:
        composite = [False]*(ceiling+1)
        for base in range(2, math.isqrt(ceiling)+1):
            if not composite[base]:
                for multiple in range(base*base, ceiling+1, base): composite[multiple] = True
        values = [x for x in range(2, ceiling+1) if not composite[x]]
        if len(values) >= count: return values[:count]
        ceiling *= 2


def deterministic_prime(value: int) -> bool:
    if value < 2: return False
    small = (2,3,5,7,11,13,17,19,23,29,31,37)
    for divisor in small:
        if value % divisor == 0: return value == divisor
    d = value-1; s = 0
    while not d & 1: d >>= 1; s += 1
    for witness in (2,325,9375,28178,450775,9780504,1795265022):
        if witness % value == 0: continue
        residue = pow(witness,d,value)
        if residue == 1 or residue == value-1: continue
        passed = False
        for _ in range(s-1):
            residue = pow(residue,2,value)
            if residue == value-1: passed=True; break
        if not passed: return False
    return True


def ceiling_ratio(a: int, b: int) -> int: return (a+b-1)//b


def build_pairs(primes: list[int]) -> tuple[list[PrimePair],list[int]]:
    answer=[]
    for left_rank,left in enumerate(primes,1):
        for right_rank in range(left_rank+1,len(primes)+1):
            right=primes[right_rank-1]
            answer.append(PrimePair(left*right,left_rank,right_rank,left,right))
    answer.sort(key=lambda x:(x.product,x.left_rank,x.right_rank))
    return answer,[x.product for x in answer]


def window(arm: str, r: int, primes: list[int], largest_product: int) -> tuple[int,int]:
    middle=2*r*r; sums=(primes[0]+primes[1],primes[-2]+primes[-1])
    if arm == "REPEATED_LOWER":
        least=ceiling_ratio(M["value_minimum"],r*r)
        scale=max(abs(2*sums[0]-2*r-1),abs(2*sums[1]-2*r-1))
        bound=24+largest_product*scale
    else:
        least=ceiling_ratio(M["value_minimum"],largest_product)
        bound=max(abs(12+r*r*(2*r+1-2*sums[0])),abs(12+r*r*(2*r+1-2*sums[1])))
    radius=bound//least+1
    return max(1,middle-radius),middle+radius


def is_old_squarefree(pair: PrimePair, terminal: int) -> bool:
    old=M["prior_freeze"]
    if pair.left_rank>old["squarefree_smallest_rank_last"] or pair.right_rank-pair.left_rank>old["squarefree_middle_prime_offsets"] or terminal<=pair.right:
        return False
    cursor=max(pair.right+1,ceiling_ratio(M["value_minimum"],pair.product))
    if cursor>2 and cursor%2==0: cursor+=1
    found=0
    while found<old["squarefree_terminal_prime_offsets"]:
        if deterministic_prime(cursor):
            if cursor==terminal:return True
            if cursor>terminal:return False
            found+=1
        cursor=3 if cursor==2 else cursor+2
    return False


def independent_result(arm: str,r: int,pair: PrimePair) -> dict:
    total=pair.left+pair.right
    if arm=="REPEATED_LOWER": d=pair.product-2*r*r; numerator=24+pair.product*(2*total-2*r-1)
    else: d=2*r*r-pair.product; numerator=12+r*r*(2*r+1-2*total)
    initial={"denominator":d,"numerator":numerator}
    if d==0:return {**initial,"stop":"ZERO_DENOMINATOR"}
    if numerator*d<=0:return {**initial,"stop":"K_SIGN"}
    quotient,remainder=divmod(numerator,d)
    if remainder:return {**initial,"stop":"K_NONINTEGRAL"}
    p=quotient
    if arm=="REPEATED_LOWER":
        partner=p+2*r+1-2*total
        if partner%2:return {**initial,"p":p,"stop":"PARTNER_NONINTEGRAL"}
        q=partner//2; n=r*r*p; m=pair.product*q; canonical=r<p and pair.left<pair.right<q
    else:
        q=2*p+2*total-2*r-1; n=pair.product*p; m=r*r*q; canonical=pair.left<pair.right<p and r<q
    values={**initial,"p":p,"q":q,"n":n,"m":m}
    if m!=n+12:return {**values,"stop":"PRODUCT_MISMATCH"}
    if not canonical:return {**values,"stop":"NONCANONICAL"}
    if n<M["value_minimum"] or n>M["value_maximum"]:return {**values,"stop":"BAND"}
    if not deterministic_prime(p) or not deterministic_prime(q):return {**values,"stop":"NONPRIME"}
    if arm=="REPEATED_UPPER" and is_old_squarefree(pair,p):return {**values,"stop":"PRIOR_FROZEN"}
    if arm=="REPEATED_LOWER": identity=r*p+r*(r-1)==(total-1)*q+(pair.product-total+1)
    else: identity=(total-1)*p+(pair.product-total+1)==r*q+r*(r-1)
    return {**values,"stop":"SURVIVOR" if identity else "C_IDENTITY"}


def independent_tuples(arm: str,shard: int):
    primes=independently_sieve(M["block_prime_rank_last"]); pairs,products=build_pairs(primes)
    for rank in range(M["r_rank_first"]+shard,M["r_rank_last"]+1,M["shards"]):
        r=primes[rank-1]; low,high=window(arm,r,primes,products[-1])
        begin=bisect.bisect_left(products,low); end=bisect.bisect_right(products,high)
        for pair in pairs[begin:end]:
            coordinate={"orientation":arm,"lower_signature":[2,1] if arm=="REPEATED_LOWER" else [1,1,1],
                        "upper_signature":[1,1,1] if arm=="REPEATED_LOWER" else [2,1],"r_rank":rank,"r":r,
                        "t_rank":pair.left_rank,"t":pair.left,"u_rank":pair.right_rank,"u":pair.right,"Q":pair.product,
                        "window_low":low,"window_high":high}
            yield coordinate,independent_result(arm,r,pair)


def number_theory(factors: list[list[int]]) -> tuple[int,int,int]:
    product=phi=sigma=1; prior=1
    for prime,exponent in factors:
        if not isinstance(prime,int) or not deterministic_prime(prime) or prime<=prior or not isinstance(exponent,int) or exponent<1: raise ValueError("invalid factor certificate")
        product*=prime**exponent; phi*=prime**(exponent-1)*(prime-1); sigma*=(prime**(exponent+1)-1)//(prime-1); prior=prime
    return product,phi,sigma


def expected_certificate(arm:str,shard:int,commit:str,gate_digest:str,coordinate:dict,outcome:dict)->dict:
    r,t,u,p,q,n=coordinate["r"],coordinate["t"],coordinate["u"],outcome["p"],outcome["q"],outcome["n"]
    fn=[[r,2],[p,1]] if arm=="REPEATED_LOWER" else [[t,1],[u,1],[p,1]]
    fm=[[t,1],[u,1],[q,1]] if arm=="REPEATED_LOWER" else [[r,2],[q,1]]
    fn.sort();fm.sort();pn,phi,sigma=number_theory(fn);pm,phim,sigmam=number_theory(fm)
    if pn!=n or pm!=n+12 or phim!=phi+12 or sigmam!=sigma+12:raise ValueError("candidate arithmetic drift")
    return {"schema":"oeis-a056777-v2-certificate-v1","campaign_commit":commit,"source_commit":M["formal_conjectures"]["commit"],
            "manifest_sha256":sha(MANIFEST),"gate_attestation_sha256":gate_digest,"declaration":M["formal_conjectures"]["declaration"],
            "arm":arm,"shard":shard,"coordinate":coordinate,"n":n,"factors_n":fn,"factors_n_plus_12":fm,
            "phi_n":phi,"phi_n_plus_12":phim,"sigma_n":sigma,"sigma_n_plus_12":sigmam,"composite_n":True,"comes_from_prime_quadruple":False}


def locate(coordinate:dict,arm:str,shard:int):
    for expected,outcome in independent_tuples(arm,shard):
        if expected==coordinate:return outcome
    raise ValueError("coordinate outside frozen indexed domain")


def candidate(path:pathlib.Path,bundle:pathlib.Path,commit:str)->dict:
    verify(bundle,commit); document=json.loads(path.read_text()); arm=document.get("arm"); shard=document.get("shard"); coordinate=document.get("coordinate")
    if document.get("schema")!="oeis-a056777-v2-certificate-v1" or document.get("campaign_commit")!=commit or arm not in M["arms"] or not isinstance(shard,int) or not 0<=shard<M["shards"] or not isinstance(coordinate,dict):raise ValueError("certificate identity drift")
    outcome=locate(coordinate,arm,shard)
    if outcome.get("stop")!="SURVIVOR":raise ValueError("certificate is not an exact survivor")
    expected=expected_certificate(arm,shard,commit,sha(bundle/"gate-attestation.json"),coordinate,outcome)
    if document!=expected:raise ValueError("certificate payload drift")
    return document


def chain(path:pathlib.Path,commit:str,arm:str,shard:int)->tuple[list[dict],str]:
    raw=path.read_bytes()
    if not raw or not raw.endswith(b"\n"):raise ValueError("ledger must be nonempty ASCII ending in newline")
    try: text=raw.decode("ascii")
    except UnicodeDecodeError as exc:raise ValueError("ledger is not ASCII") from exc
    physical=text.splitlines(keepends=True);rows=[];previous=ZERO
    for sequence,line in enumerate(physical):
        if not line.endswith("\n") or line.endswith("\r\n"):raise ValueError("ledger physical-row framing drift")
        encoded=line[:-1].encode("ascii")
        try: full=json.loads(encoded)
        except json.JSONDecodeError as exc:raise ValueError("malformed ledger physical row") from exc
        if not isinstance(full,dict) or set(full)!=ROW_KEYS:raise ValueError("ledger row key drift")
        canonical=json.dumps(full,sort_keys=True,separators=(",",":")).encode("ascii")
        if encoded!=canonical:raise ValueError("ledger row is not byte-canonical")
        row=dict(full);digest=row.pop("row_sha256")
        if row.get("schema")!="oeis-a056777-v2-progress-v1" or row.get("seq")!=sequence or row.get("previous_row_sha256")!=previous or row.get("campaign_commit")!=commit or row.get("arm")!=arm or row.get("shard")!=shard:raise ValueError("ledger identity/order drift")
        actual=hashlib.sha256(json.dumps(row,sort_keys=True,separators=(",",":")).encode("ascii")).hexdigest()
        if digest!=actual:raise ValueError("ledger hash-chain drift")
        row["row_sha256"]=digest;rows.append(row);previous=digest
    return rows,previous


def validate_error(reason:str,error)->None:
    if reason=="WORKER_ERROR":
        if not isinstance(error,dict) or set(error)!={"type","message","message_sha256"}:raise ValueError("worker error receipt drift")
        if not error["type"] or not isinstance(error["message"],str) or len(error["message"])>1000:raise ValueError("worker error fields drift")
        if hashlib.sha256(error["message"].encode()).hexdigest()!=error["message_sha256"]:raise ValueError("worker error digest drift")
    elif error is not None:raise ValueError("spurious worker error")


def replay(terminal:dict,rows:list[dict],certificate_doc:dict|None)->None:
    visited=terminal["visited"]
    expected_visits=[0]+list(range(M["checkpoint_interval"],visited+1,M["checkpoint_interval"]))
    if visited%M["checkpoint_interval"]:expected_visits.append(visited)
    # A certificate is the atomic final state commit.  Its tuple is replayed
    # below, while the ledger intentionally ends at the preceding checkpoint.
    if certificate_doc is not None and expected_visits[-1]==visited:
        expected_visits=expected_visits[:-1]
    if [row.get("visited") for row in rows]!=expected_visits:raise ValueError("incremental checkpoint gap/duplicate drift")
    counts={name:0 for name in STOPS}; checkpoints={row["visited"]:row for row in rows}; iterator=independent_tuples(terminal["arm"],terminal["shard"])
    last_coordinate=last_outcome=first_survivor=None
    for ordinal in range(visited):
        try:coordinate,outcome=next(iterator)
        except StopIteration as exc:raise ValueError("visited prefix exceeds domain") from exc
        counts[outcome["stop"]]+=1;last_coordinate,last_outcome=coordinate,outcome
        if first_survivor is None and outcome["stop"]=="SURVIVOR":first_survivor=(ordinal,coordinate,outcome)
        count=ordinal+1
        if count in checkpoints:
            row=checkpoints[count]
            if row.get("schema")!="oeis-a056777-v2-progress-v1" or row.get("last_coordinate")!=coordinate or row.get("last_outcome")!=outcome or row.get("counts")!=counts:raise ValueError("checkpoint semantic drift")
    zero=checkpoints[0]
    if zero.get("schema")!="oeis-a056777-v2-progress-v1" or zero.get("last_coordinate") is not None or zero.get("last_outcome") is not None or zero.get("counts")!={name:0 for name in STOPS}:raise ValueError("initial checkpoint drift")
    if terminal.get("tuple_domain_only") is not True or terminal.get("last_coordinate")!=last_coordinate or terminal.get("last_outcome")!=last_outcome or terminal.get("counts")!=counts:raise ValueError("terminal prefix drift")
    if certificate_doc is not None:
        if (first_survivor is None or first_survivor[0]!=visited-1 or certificate_doc["coordinate"]!=first_survivor[1]
                or certificate_doc["coordinate"]!=terminal.get("last_coordinate")
                or not isinstance(terminal.get("last_outcome"),dict) or terminal["last_outcome"].get("stop")!="SURVIVOR"):
            raise ValueError("candidate final-state/first-survivor drift")
    elif first_survivor is not None:raise ValueError("candidate omission")
    if terminal["terminal_reason"]=="DOMAIN_EXHAUSTED":
        try:next(iterator)
        except StopIteration:pass
        else:raise ValueError("false indexed-domain exhaustion")


def terminal(ledger_path:pathlib.Path,terminal_path:pathlib.Path,certificate_path:pathlib.Path|None,bundle:pathlib.Path,commit:str,arm:str,shard:int)->dict:
    verify(bundle,commit); doc=json.loads(terminal_path.read_text());rows,final=chain(ledger_path,commit,arm,shard)
    if not isinstance(doc,dict) or set(doc)!=TERMINAL_KEYS:raise ValueError("terminal key drift")
    if doc.get("schema")!="oeis-a056777-v2-terminal-v1" or doc.get("campaign_commit")!=commit or doc.get("source_commit")!=M["formal_conjectures"]["commit"] or doc.get("gate_attestation_sha256")!=sha(bundle/"gate-attestation.json") or (doc.get("arm"),doc.get("shard"))!=(arm,shard):raise ValueError("terminal identity drift")
    if doc.get("ledger_rows")!=len(rows) or doc.get("final_row_sha256")!=final or doc.get("ledger_sha256")!=sha(ledger_path):raise ValueError("terminal ledger binding drift")
    if doc.get("terminal_reason") not in {"DEADLINE_PREFIX","DOMAIN_EXHAUSTED","CERTIFICATE_FOUND","WORKER_ERROR"}:raise ValueError("terminal reason drift")
    validate_error(doc["terminal_reason"],doc.get("worker_error"));present=certificate_path is not None
    if bool(doc.get("certificate_present"))!=present or (doc["terminal_reason"]=="CERTIFICATE_FOUND")!=present:raise ValueError("certificate/terminal mismatch")
    cert=candidate(certificate_path,bundle,commit) if present else None
    replay(doc,rows,cert);return doc


def main()->int:
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest="mode",required=True)
    p=sub.add_parser("candidate");p.add_argument("certificate",type=pathlib.Path);p.add_argument("bundle",type=pathlib.Path);p.add_argument("--campaign-commit",required=True)
    p=sub.add_parser("terminal");p.add_argument("ledger",type=pathlib.Path);p.add_argument("terminal",type=pathlib.Path);p.add_argument("certificate");p.add_argument("bundle",type=pathlib.Path);p.add_argument("--campaign-commit",required=True);p.add_argument("--arm",choices=M["arms"],required=True);p.add_argument("--shard",type=int,required=True)
    args=parser.parse_args()
    if args.mode=="candidate": result=candidate(args.certificate,args.bundle,args.campaign_commit);print(json.dumps({"verified":True,"n":result["n"]},separators=(",",":")))
    else:terminal(args.ledger,args.terminal,None if args.certificate=="-" else pathlib.Path(args.certificate),args.bundle,args.campaign_commit,args.arm,args.shard);print('{"verified":true}')
    return 0


if __name__=="__main__":raise SystemExit(main())
