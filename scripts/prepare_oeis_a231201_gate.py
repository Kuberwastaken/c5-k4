#!/usr/bin/env python3
"""Prepare and semantically replay the fail-closed A231201 sanity gate."""
from __future__ import annotations
import argparse, concurrent.futures, hashlib, json, os, pathlib, subprocess, sys, time
from collections import Counter
from oeis_a231201_common import FREEZE, M, ZERO, Ledger, atomic_json, exact_commit, sha

GATE_SCHEMA="oeis-a231201-sanity-gate-v1"
MR_BASES=(2,3,5,7,11,13,17,19,23,29,31,37)
MR_LIMIT=318_665_857_834_031_151_167_461

def parse_bfile(path:pathlib.Path)->list[tuple[int,int]]:
    if sha(path)!=M["oeis_bfile"]["sha256"]: raise ValueError("b-file hash drift")
    rows=[]
    for line in path.read_text(encoding="ascii").splitlines():
        if not line.strip(): continue
        fields=line.split()
        if len(fields)!=2: raise ValueError("malformed b-file")
        rows.append((int(fields[0]),int(fields[1])))
    if len(rows)!=M["oeis_bfile"]["rows"] or [n for n,_ in rows]!=list(range(1,10001)): raise ValueError("b-file domain drift")
    return rows

def verify_sources(lean:pathlib.Path,source:pathlib.Path,bfile:pathlib.Path)->list[tuple[int,int]]:
    if sha(lean)!=M["formal_conjectures"]["sha256"]: raise ValueError("Lean source drift")
    lean_bytes=lean.read_bytes(); blob=hashlib.sha1(f"blob {len(lean_bytes)}\0".encode("ascii")+lean_bytes).hexdigest()
    if blob!=M["formal_conjectures"]["blob_sha1"]: raise ValueError("Lean blob identity drift")
    text=lean.read_text()
    for token in ("def A (n : ℕ) : Prop","theorem conjecture (n : ℕ) (hn : 1 < n) : A n","category research open"):
        if token not in text: raise ValueError("Lean declaration/status drift")
    if sha(source)!=M["oeis_source"]["sha256"]: raise ValueError("OEIS record drift")
    record=source.read_text()
    for token in ("%O A231201 1,5","a[n_]:=Sum[If[PrimeQ[2^x+n-x],1,0],{x,1,n-1}]","for n up to 10^7","a(53) = 1","a(64) = 1",M["oeis_source"]["revision"]):
        if token not in record: raise ValueError("OEIS statement/control drift")
    return parse_bfile(bfile)

def prime_test(n:int)->bool:
    if n>=MR_LIMIT: raise ValueError("gate primality outside deterministic Miller-Rabin range")
    if n<2:return False
    for p in MR_BASES:
        if n%p==0:return n==p
    d=n-1; s=0
    while d%2==0:s+=1; d//=2
    for a in MR_BASES:
        z=pow(a,d,n)
        if z in (1,n-1):continue
        for _ in range(s-1):
            z=z*z%n
            if z==n-1:break
        else:return False
    return True

def count_a(n:int,deadline:float)->int:
    count=0
    for x in range(1,n):
        if time.monotonic()>=deadline: raise TimeoutError("internal gate deadline")
        count+=int(prime_test((1<<x)+n-x))
    return count

def chunk(bfile:pathlib.Path,start:int,end:int,ledger_path:pathlib.Path,terminal:pathlib.Path)->int:
    rows=parse_bfile(bfile); ledger=Ledger(ledger_path); deadline=time.monotonic()+M["internal_seconds"]; status="GATE_CHUNK_EXHAUSTED"; checked=0
    try:
        for offset in range(start,end):
            n,expected=rows[offset]
            try: actual=count_a(n,deadline)
            except TimeoutError: status="DEADLINE_PREFIX"; break
            ledger.append({"schema":"oeis-a231201-gate-row-v1","offset":offset,"n":n,"expected":expected,"actual":actual,"match":actual==expected}); checked+=1
            if actual!=expected: status="SANITY_GATE_INCOMPLETE"; break
    finally: ledger.close()
    atomic_json(terminal,{"schema":"oeis-a231201-gate-chunk-terminal-v1","start":start,"end":end,"checked":checked,"status":status,"ledger_rows":ledger.seq,"final_row_sha256":ledger.previous,"ledger_sha256":sha(ledger_path)})
    return 0 if status=="GATE_CHUNK_EXHAUSTED" and checked==end-start else 75

def verify_prior_certificate(path:pathlib.Path)->None:
    if sha(path)!=M["contamination_controls"]["breakthrough_certificate_sha256"]: raise ValueError("prior certificate hash drift")
    c=json.loads(path.read_text()); claim=c.get("claim",{}); maximum=c.get("maximum_cases",[])
    if (claim.get("upper_n"),claim.get("maximum_least_x"),claim.get("first_n_above_threshold"),claim.get("maximum_before_first_above_threshold"))!=(327,72,327,59): raise ValueError("prior L(327) control drift")
    if maximum!=[{"n":327,"prime":4722366482869645213951,"x":72,"y":255}] or not prime_test(maximum[0]["prime"]): raise ValueError("prior sharp prime control failed")
    histogram=Counter(); records=[]; maximum_value=0; maximum_cases=[]; first_above=None; maximum_before=0; stream=hashlib.sha256()
    for n in range(2,328):
        witness=None
        for x in range(1,min(n,73)):
            p=(1<<x)+n-x
            if prime_test(p):witness=(x,p); break
        if witness is None: raise ValueError("prior certificate witness replay failed")
        x,p=witness; row={"n":n,"x":x,"y":n-x,"prime":p}; histogram[x]+=1; stream.update(f"{n},{x},{p}\n".encode("ascii"))
        if x>63 and first_above is None:first_above=n
        if first_above is None:maximum_before=max(maximum_before,x)
        if x>maximum_value:maximum_value=x; maximum_cases=[row]; records.append(row)
        elif x==maximum_value:maximum_cases.append(row)
    if c.get("least_x_histogram")!={str(x):histogram[x] for x in sorted(histogram)} or c.get("record_holders")!=records or c.get("maximum_cases")!=maximum_cases or c.get("canonical_stream",{}).get("sha256")!=stream.hexdigest() or (first_above,maximum_before,maximum_value)!=(327,59,72): raise ValueError("prior certificate full semantic replay failed")

def verify_prior_covering(path:pathlib.Path)->None:
    if sha(path)!=M["contamination_controls"]["covering_results_sha256"]: raise ValueError("prior covering hash drift")
    actual=[[r.get("prime_bound"),r.get("period"),r.get("status")] for r in json.loads(path.read_text()).get("results",[])]
    if actual!=M["contamination_controls"]["covering_expected"]: raise ValueError("prior covering controls drift")

def copy_snapshot(src:pathlib.Path,dst:pathlib.Path)->None:
    with src.open("rb") as incoming,dst.open("xb") as outgoing:
        for block in iter(lambda:incoming.read(1<<20),b""): outgoing.write(block)
        outgoing.flush(); os.fsync(outgoing.fileno())

def expected_snapshot_hashes()->dict[str,str]:
    return {"231201.lean":M["formal_conjectures"]["sha256"],"A231201.seq":M["oeis_source"]["sha256"],"b231201.txt":M["oeis_bfile"]["sha256"],"prior-certificate.json":M["contamination_controls"]["breakthrough_certificate_sha256"],"prior-covering.json":M["contamination_controls"]["covering_results_sha256"],"manifest.json":sha(FREEZE/"manifest.json"),"source-status-attestation.json":sha(FREEZE/"source-status-attestation.json")}

def prepare(a)->int:
    a.output.mkdir(parents=True,exist_ok=True); diagnostic=a.output/"diagnostic-attestation.json"
    atomic_json(diagnostic,{"schema":"oeis-a231201-gate-diagnostic-v1","campaign_commit":a.campaign_commit,"status":"INITIALIZED","stage":"BEFORE_SOURCE_VERIFICATION"})
    try:
        commit=exact_commit(a.campaign_commit); rows=verify_sources(a.lean,a.source,a.bfile); verify_prior_certificate(a.prior_certificate); verify_prior_covering(a.prior_covering)
        snapshots=a.output/"snapshots"; snapshots.mkdir(); chunks=a.output/"chunks"; chunks.mkdir()
        inputs=((a.lean,"231201.lean"),(a.source,"A231201.seq"),(a.bfile,"b231201.txt"),(a.prior_certificate,"prior-certificate.json"),(a.prior_covering,"prior-covering.json"),(FREEZE/"manifest.json","manifest.json"),(FREEZE/"source-status-attestation.json","source-status-attestation.json"))
        for src,name in inputs: copy_snapshot(src,snapshots/name)
        commands=[]; chunk_size=M["gate_exact_prefix"]//M["gate_chunks"]
        for index in range(M["gate_chunks"]):
            start=index*chunk_size; end=start+chunk_size; base=chunks/f"{start:05d}-{end:05d}"
            commands.append((index,[sys.executable,__file__,"chunk",str(a.bfile),str(start),str(end),str(base.with_suffix('.jsonl')),str(base.with_suffix('.terminal.json'))]))
        def run_one(item):
            index,cmd=item
            try:return index,subprocess.run(cmd,timeout=M["external_seconds"],check=False).returncode
            except subprocess.TimeoutExpired:return index,124
        statuses={}
        with concurrent.futures.ThreadPoolExecutor(max_workers=M["gate_chunks"]) as pool:
            for index,code in pool.map(run_one,commands):statuses[index]=code
        chunk_files={}; complete=True
        for index in range(M["gate_chunks"]):
            start=index*chunk_size; end=start+chunk_size; base=chunks/f"{start:05d}-{end:05d}"; terminal=base.with_suffix('.terminal.json'); ledger=base.with_suffix('.jsonl')
            if statuses[index]!=0 or not terminal.is_file() or not ledger.is_file():complete=False; continue
            t=json.loads(terminal.read_text()); complete &= t.get("status")=="GATE_CHUNK_EXHAUSTED" and t.get("checked")==chunk_size
            chunk_files[str(ledger.relative_to(a.output))]=sha(ledger); chunk_files[str(terminal.relative_to(a.output))]=sha(terminal)
        controls={str(n):count_a(n,time.monotonic()+M["internal_seconds"]) for n in (2,3,4,5,8,53,64)}; expected={"2":1,"3":1,"4":1,"5":2,"8":1,"53":1,"64":1}; complete &= controls==expected
        status="PASS" if complete else "SANITY_GATE_INCOMPLETE"
        att={"schema":GATE_SCHEMA,"campaign_commit":commit,"status":status,"source_hashes":{name:sha(snapshots/name) for _,name in inputs},"controls":controls,"chunk_exit_codes":statuses,"chunk_files":chunk_files,"bfile_rows":len(rows)}
        atomic_json(a.output/"gate-attestation.json",att); atomic_json(diagnostic,{"schema":"oeis-a231201-gate-diagnostic-v1","campaign_commit":commit,"status":status,"stage":"COMPLETE","gate_attestation_sha256":sha(a.output/"gate-attestation.json")})
        return 0 if complete else 75
    except BaseException as exc:
        atomic_json(diagnostic,{"schema":"oeis-a231201-gate-diagnostic-v1","campaign_commit":a.campaign_commit,"status":"SANITY_GATE_INCOMPLETE","stage":"PREPARATION_FAILURE","error_type":type(exc).__name__,"error":str(exc)})
        raise

def replay_chunk(bundle:pathlib.Path,rows:list[tuple[int,int]],start:int,end:int)->tuple[str,str]:
    base=bundle/"chunks"/f"{start:05d}-{end:05d}"; ledger_path=base.with_suffix(".jsonl"); terminal_path=base.with_suffix(".terminal.json"); previous=ZERO; count=0
    with ledger_path.open(encoding="ascii") as f:
        for line in f:
            row=json.loads(line); digest=row.pop("row_sha256",None); raw=json.dumps(row,sort_keys=True,separators=(",",":")); actual_digest=hashlib.sha256(raw.encode("ascii")).hexdigest(); offset=start+count; n,expected=rows[offset]; actual=count_a(n,time.monotonic()+M["internal_seconds"])
            expected_row={"schema":"oeis-a231201-gate-row-v1","offset":offset,"n":n,"expected":expected,"actual":actual,"match":actual==expected,"seq":count,"previous_row_sha256":previous}
            if row!=expected_row or digest!=actual_digest or actual!=expected: raise ValueError("gate chunk row arithmetic/chain drift")
            previous=digest; count+=1
    if count!=end-start: raise ValueError("gate chunk row coverage drift")
    terminal=json.loads(terminal_path.read_text()); expected_terminal={"schema":"oeis-a231201-gate-chunk-terminal-v1","start":start,"end":end,"checked":count,"status":"GATE_CHUNK_EXHAUSTED","ledger_rows":count,"final_row_sha256":previous,"ledger_sha256":sha(ledger_path)}
    if terminal!=expected_terminal: raise ValueError("gate chunk terminal drift")
    return sha(ledger_path),sha(terminal_path)

def verify(bundle:pathlib.Path,commit:str)->dict:
    att=json.loads((bundle/"gate-attestation.json").read_text()); commit=exact_commit(commit)
    if set(att)!={"schema","campaign_commit","status","source_hashes","controls","chunk_exit_codes","chunk_files","bfile_rows"} or att.get("schema")!=GATE_SCHEMA or att.get("campaign_commit")!=commit or att.get("status")!="PASS" or att.get("bfile_rows")!=10000: raise ValueError("gate incomplete or unbound")
    expected_hashes=expected_snapshot_hashes(); snapshots=bundle/"snapshots"
    if att.get("source_hashes")!=expected_hashes or {p.name for p in snapshots.iterdir()}!=set(expected_hashes): raise ValueError("gate snapshot identity set drift")
    for name,digest in expected_hashes.items():
        if sha(snapshots/name)!=digest: raise ValueError("gate source snapshot drift")
    rows=verify_sources(snapshots/"231201.lean",snapshots/"A231201.seq",snapshots/"b231201.txt"); verify_prior_certificate(snapshots/"prior-certificate.json"); verify_prior_covering(snapshots/"prior-covering.json")
    expected_controls={"2":1,"3":1,"4":1,"5":2,"8":1,"53":1,"64":1}; actual_controls={str(n):count_a(n,time.monotonic()+M["internal_seconds"]) for n in (2,3,4,5,8,53,64)}
    if att.get("controls")!=expected_controls or actual_controls!=expected_controls: raise ValueError("gate named controls drift")
    chunk_size=M["gate_exact_prefix"]//M["gate_chunks"]; expected_files={}
    for index in range(M["gate_chunks"]):
        start=index*chunk_size; end=start+chunk_size; ledger_digest,terminal_digest=replay_chunk(bundle,rows,start,end); expected_files[f"chunks/{start:05d}-{end:05d}.jsonl"]=ledger_digest; expected_files[f"chunks/{start:05d}-{end:05d}.terminal.json"]=terminal_digest
    actual_chunk_paths={str(p.relative_to(bundle)) for p in (bundle/"chunks").iterdir() if p.is_file()}
    if att.get("chunk_files")!=expected_files or actual_chunk_paths!=set(expected_files) or att.get("chunk_exit_codes")!={str(i):0 for i in range(M["gate_chunks"])}: raise ValueError("gate chunk identities/coverage drift")
    diagnostic=json.loads((bundle/"diagnostic-attestation.json").read_text()); expected_diagnostic={"schema":"oeis-a231201-gate-diagnostic-v1","campaign_commit":commit,"status":"PASS","stage":"COMPLETE","gate_attestation_sha256":sha(bundle/"gate-attestation.json")}
    if diagnostic!=expected_diagnostic: raise ValueError("gate diagnostic drift")
    return att

def main()->int:
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="mode",required=True)
    q=sub.add_parser("prepare")
    for name in ("lean","source","bfile","prior_certificate","prior_covering","output"):q.add_argument(name,type=pathlib.Path)
    q.add_argument("--campaign-commit",required=True)
    q=sub.add_parser("verify"); q.add_argument("bundle",type=pathlib.Path); q.add_argument("--campaign-commit",required=True)
    q=sub.add_parser("chunk"); q.add_argument("bfile",type=pathlib.Path); q.add_argument("start",type=int); q.add_argument("end",type=int); q.add_argument("ledger",type=pathlib.Path); q.add_argument("terminal",type=pathlib.Path)
    a=p.parse_args()
    if a.mode=="prepare":return prepare(a)
    if a.mode=="verify":verify(a.bundle,a.campaign_commit); return 0
    return chunk(a.bfile,a.start,a.end,a.ledger,a.terminal)
if __name__=="__main__":raise SystemExit(main())
