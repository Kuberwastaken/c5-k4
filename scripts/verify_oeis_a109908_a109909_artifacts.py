#!/usr/bin/env python3
"""Independent exact replay for A109908/A109909 development artifacts."""
from __future__ import annotations
import argparse, hashlib, json, math, pathlib

ROOT=pathlib.Path(__file__).resolve().parents[1]
HERE=ROOT/"results/expansion/live-search-2026-08-14/oeis-a109908-a109909-development"
MANIFEST=HERE/"manifest.json"; M=json.loads(MANIFEST.read_text()); ZERO="0"*64
STOPS=("PRIME_ESCAPE","COMPOSITE_ESCAPE","FULL_COVER","CAP_PREFIX","WORKER_ERROR")

def canonical(x): return (json.dumps(x,sort_keys=True,separators=(",",":"))+"\n").encode("ascii")
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def exact_commit(x):
    if len(x)!=40 or any(c not in "0123456789abcdef" for c in x): raise ValueError("bad commit")
    return x

def prime(n):
    if type(n)is not int or n<2:return False
    for p in (2,3,5,7,11,13,17,19,23,29,31,37):
        if n%p==0:return n==p
    d,s=n-1,0
    while d%2==0:d//=2;s+=1
    for a in (2,325,9375,28178,450775,9780504,1795265022):
        if a%n==0:continue
        x=pow(a,d,n)
        if x in (1,n-1):continue
        for _ in range(s-1):
            x=x*x%n
            if x==n-1:break
        else:return False
    return True

def roots(q,residue): return tuple(k for k in range(1,q) if (k+pow(k,-1,q))%q==residue)

def _replay_mask_options(q,prefix):
    options=[]
    for residue in range(q):
        rs=roots(q,residue)
        if not rs:continue
        positions=0
        for root in rs:
            for k in range(root,prefix+1,q):positions|=1<<(k-1)
        options.append((residue,rs,positions))
    return options

def _replay_first_open(mask,prefix):
    missing=(~mask)&((1<<prefix)-1)
    return prefix+1 if missing==0 else (missing&-missing).bit_length()

def _replay_crt(a,m,residue,q):
    step=((residue-a)*pow(m,-1,q))%q
    return (a+m*step)%(m*q),m*q

def frozen_profile_stream():
    """Reconstruct the frozen beam without importing discovery code."""
    spec=M["construction"];prefix=spec["construction_prefix_k"]
    beam=[(0,1,(),(),0)];ordinal=0
    for depth,q in enumerate(spec["divisor_primes"],1):
        children=[];options=_replay_mask_options(q,prefix)
        for a,modulus,selected,root_rows,mask in beam:
            for residue,rs,qmask in options:
                na,nm=_replay_crt(a,modulus,residue,q);choice=selected+(residue,);combined=mask|qmask
                rank=(-_replay_first_open(combined,prefix),-combined.bit_count(),na,choice)
                children.append((rank,(na,nm,choice,root_rows+((q,residue,rs),),combined)))
        children.sort(key=lambda item:item[0]);beam=[state for _,state in children[:spec["beam_width"]]]
        if depth>=spec["profile_minimum_depth"]:
            for a,modulus,selected,root_rows,_mask in beam:
                if modulus<=M["candidate_n_maximum"]//2:raise ValueError("selected-profile lcm obstruction")
                profile={"ordinal":ordinal,"depth":depth,"crt_residue":a,"modulus":modulus,
                         "selected_residues":list(selected),
                         "root_classes":[{"q":p,"n_residue":r,"roots":list(rs)} for p,r,rs in root_rows]}
                yield profile;ordinal+=1

def representative_stream(profile):
    lo,hi=M["candidate_n_minimum"],M["candidate_n_maximum"]
    residue,modulus=profile["crt_residue"],profile["modulus"]
    first=residue if residue>=lo else residue+((lo-residue+modulus-1)//modulus)*modulus
    yield from range(first,hi+1,modulus)

def frozen_trial_stream(shard):
    for profile in frozen_profile_stream():
        if profile["ordinal"]%M["shards"]==shard:
            for n in representative_stream(profile):yield profile,n

def factor_ok(value,factors):
    if not isinstance(factors,list) or not factors:return False
    prior=1; product=1
    for item in factors:
        if not isinstance(item,list) or len(item)!=2:return False
        p,e=item
        if type(e)is not int or e<1 or p<=prior or not prime(p):return False
        product*=p**e;prior=p
    return product==value

def profile_ok(profile,n):
    rows=profile["root_classes"]; selected=profile["selected_residues"]
    if len(rows)!=profile["depth"] or len(rows)!=len(selected):raise ValueError("profile length drift")
    modulus=1; crt_residue=n%profile["modulus"]
    for index,row in enumerate(rows):
        q,r,rs=row["q"],row["n_residue"],tuple(row["roots"])
        if q!=M["construction"]["divisor_primes"][index] or r!=selected[index] or rs!=roots(q,r):raise ValueError("root-class drift")
        if any(pow(k,-1,q) not in rs for k in rs):raise ValueError("roots not inverse-paired")
        if n%q!=r:raise ValueError("candidate CRT drift")
        modulus*=q
    if modulus!=profile["modulus"] or crt_residue!=profile["crt_residue"]:raise ValueError("modulus/residue drift")

def cover_replay(n,profile,stop_at=None):
    end=n//2 if stop_at is None else stop_at
    block=M["construction"]["coverage_block_size"]; digest=hashlib.sha256(); covered=0
    for lo in range(1,end+1,block):
        hi=min(end,lo+block-1); labels=bytearray(hi-lo+1)
        for index,row in enumerate(profile["root_classes"],1):
            q=row["q"]
            for root in row["roots"]:
                first=lo+((root-lo)%q); count=(hi-first)//q+1 if first<=hi else 0
                if count:labels[first-lo::q]=bytes([index])*count
        try:offset=labels.index(0)
        except ValueError:digest.update(labels);covered+=len(labels)
        else:digest.update(labels[:offset]);return False,covered+offset,lo+offset,digest.hexdigest()
    return True,covered,None,digest.hexdigest()

def verify_trial(row,commit,shard,expected_profile,expected_n):
    if row.get("schema")!="oeis-a109908-a109909-trial-v1" or row.get("campaign_commit")!=commit or row.get("shard")!=shard:raise ValueError("trial identity drift")
    profile=row["profile"]; n=row["n"]
    if profile!=expected_profile or n!=expected_n:raise ValueError("frozen profile/order drift")
    if not M["candidate_n_minimum"]<=n<=M["candidate_n_maximum"] or profile["ordinal"]%M["shards"]!=shard:raise ValueError("trial ownership/range drift")
    profile_ok(profile,n); coverage=row["coverage"]
    complete,covered,uncovered,digest=cover_replay(n,profile,None if coverage["complete"] else coverage["first_uncovered_k"])
    if coverage["complete"]:
        if not complete or covered!=n//2 or digest!=coverage["coverage_sha256"] or row["outcome"]!="FULL_COVER":raise ValueError("full-cover drift")
    else:
        if complete or uncovered!=coverage["first_uncovered_k"] or covered!=coverage["covered"] or digest!=coverage["coverage_sha256"]:raise ValueError("escape-prefix drift")
        k=uncovered; value=k*(n-k)-1
        if value!=coverage["value"] or not factor_ok(value,coverage["factors"]):raise ValueError("escape factorization drift")
        isprime=len(coverage["factors"])==1 and coverage["factors"][0]==[value,1]
        expected="PRIME_ESCAPE" if isprime else "COMPOSITE_ESCAPE"
        if coverage["escape_is_prime"]!=isprime or row["outcome"]!=expected:raise ValueError("escape classification drift")

def read_chain(path,commit,shard):
    rows=[];tail=ZERO;expected=iter(frozen_trial_stream(shard))
    for seq,raw in enumerate(path.read_bytes().splitlines(keepends=True)):
        row=json.loads(raw)
        if raw!=canonical(row):raise ValueError("noncanonical ledger")
        digest=row.get("row_sha256");body=dict(row);body.pop("row_sha256",None)
        if body.pop("seq")!=seq or body.pop("previous_row_sha256")!=tail:raise ValueError("chain sequence drift")
        if hashlib.sha256(json.dumps({**body,"seq":seq,"previous_row_sha256":tail},sort_keys=True,separators=(",",":")).encode()).hexdigest()!=digest:raise ValueError("chain hash drift")
        try:expected_profile,expected_n=next(expected)
        except StopIteration:raise ValueError("ledger exceeds frozen trial domain")
        verify_trial(body,commit,shard,expected_profile,expected_n);rows.append(body);tail=digest
    return rows,tail,expected

def verify_all(directory,gate,commit,shard):
    exact_commit(commit); terminal_path=directory/"terminal.json"; ledger=directory/"ledger.jsonl"
    doc=json.loads(terminal_path.read_text()); rows,tail,expected=read_chain(ledger,commit,shard)
    gate_doc=json.loads((gate/"gate-attestation.json").read_text())
    if (gate_doc.get("schema"),gate_doc.get("campaign_commit"),gate_doc.get("manifest_sha256"),gate_doc.get("status")) != ("oeis-a109908-a109909-gate-v1",commit,sha(MANIFEST),"VERIFIED"):raise ValueError("gate identity drift")
    if gate_doc.get("rows")!={"A109908":10000,"A109909":93} or gate_doc.get("controls")!=20:raise ValueError("gate coverage drift")
    if doc.get("schema")!="oeis-a109908-a109909-terminal-v1" or doc.get("campaign_commit")!=commit or doc.get("shard")!=shard or doc.get("gate_attestation_sha256")!=sha(gate/"gate-attestation.json"):raise ValueError("terminal identity drift")
    counts={x:0 for x in STOPS}
    for row in rows:counts[row["outcome"]]+=1
    if doc["terminal_reason"]=="CAP_PREFIX":counts["CAP_PREFIX"]+=1
    if doc["terminal_reason"]=="WORKER_ERROR":counts["WORKER_ERROR"]+=1
    if doc["visited"]!=len(rows) or doc["counts"]!=counts or doc["ledger_rows"]!=len(rows) or doc["final_row_sha256"]!=tail or doc["ledger_sha256"]!=sha(ledger):raise ValueError("terminal ledger drift")
    reason=doc.get("terminal_reason");candidate_path=directory/"candidate.json"
    if reason not in {"DOMAIN_EXHAUSTED","FROZEN_TRIAL_LIMIT","CANDIDATE_FOUND","CAP_PREFIX","WORKER_ERROR"}:raise ValueError("terminal reason drift")
    if candidate_path.exists():
        candidate=json.loads(candidate_path.read_text())
        expected_keys={"schema","campaign_commit","manifest_sha256","gate_attestation_sha256","n","half_end","profile","coverage","properness_bound","status"}
        if set(candidate)!=expected_keys or candidate_path.read_bytes()!=canonical(candidate) or not rows or rows[-1]["outcome"]!="FULL_COVER":raise ValueError("candidate transaction drift")
        if candidate["schema"]!="oeis-a109908-a109909-candidate-v1" or candidate["status"]!="LITERAL_SHARED_COUNTEREXAMPLE_PENDING_LEAN":raise ValueError("candidate schema/status drift")
        if candidate["campaign_commit"]!=commit or candidate["manifest_sha256"]!=sha(MANIFEST) or candidate["gate_attestation_sha256"]!=sha(gate/"gate-attestation.json"):raise ValueError("candidate identity drift")
        if candidate["n"]!=rows[-1]["n"] or candidate["half_end"]!=candidate["n"]//2 or candidate["profile"]!=rows[-1]["profile"] or candidate["coverage"]!=rows[-1]["coverage"]:raise ValueError("candidate payload drift")
        proper={"largest_q":max(row["q"] for row in candidate["profile"]["root_classes"]),"n_minus_two":candidate["n"]-2}
        if candidate["properness_bound"]!=proper or proper["largest_q"]>=proper["n_minus_two"]:raise ValueError("proper divisor bound drift")
        if reason!="CANDIDATE_FOUND" or len([row for row in rows if row["outcome"]=="FULL_COVER"])!=1:raise ValueError("terminal reason drift")
        if doc.get("candidate_sha256")!=sha(candidate_path) or doc.get("coverage_sha256")!=candidate["coverage"]["coverage_sha256"]:raise ValueError("candidate hash drift")
    else:
        if doc.get("candidate_sha256") is not None or doc.get("coverage_sha256") is not None or any(row["outcome"]=="FULL_COVER" for row in rows):raise ValueError("candidate hash drift")
    if doc["candidate_present"]!=candidate_path.exists():raise ValueError("candidate presence drift")
    if reason!="WORKER_ERROR" and doc.get("worker_error") is not None:raise ValueError("terminal reason drift")
    if reason=="DOMAIN_EXHAUSTED":
        try:next(expected)
        except StopIteration:pass
        else:raise ValueError("terminal reason drift")
    elif reason=="FROZEN_TRIAL_LIMIT":
        if len(rows)!=M["construction"]["maximum_trials_per_shard"]:raise ValueError("terminal reason drift")
        try:next(expected)
        except StopIteration:raise ValueError("terminal reason drift")
    elif reason=="CAP_PREFIX":
        if candidate_path.exists() or doc.get("worker_error") is not None:raise ValueError("terminal reason drift")
    elif reason=="WORKER_ERROR":
        if candidate_path.exists() or not isinstance(doc.get("worker_error"),dict):raise ValueError("terminal reason drift")
    elif reason=="CANDIDATE_FOUND" and not candidate_path.exists():raise ValueError("terminal reason drift")
    return doc

def main():
    p=argparse.ArgumentParser();p.add_argument("directory",type=pathlib.Path);p.add_argument("gate",type=pathlib.Path);p.add_argument("--campaign-commit",required=True);p.add_argument("--shard",type=int,required=True)
    a=p.parse_args();verify_all(a.directory,a.gate,a.campaign_commit,a.shard);print("artifact replay verified");return 0
if __name__=="__main__":raise SystemExit(main())
