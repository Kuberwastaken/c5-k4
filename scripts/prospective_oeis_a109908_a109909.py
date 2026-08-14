#!/usr/bin/env python3
"""Frozen finite-prefix residue-cover development lane for A109908/A109909."""
from __future__ import annotations

import argparse, hashlib, json, math, os, pathlib, random, shutil, signal, subprocess
import urllib.parse, urllib.request
from contextlib import contextmanager

ROOT = pathlib.Path(__file__).resolve().parents[1]
HERE = ROOT / "results/expansion/live-search-2026-08-14/oeis-a109908-a109909-development"
MANIFEST = HERE / "manifest.json"
M = json.loads(MANIFEST.read_text())
ZERO = "0" * 64
STOPS = ("PRIME_ESCAPE", "COMPOSITE_ESCAPE", "FULL_COVER", "CAP_PREFIX", "WORKER_ERROR")


class Deadline(Exception): pass
def _alarm(_signum, _frame): raise Deadline()


@contextmanager
def blocked_alarm():
    old = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGALRM})
    try: yield
    finally: signal.pthread_sigmask(signal.SIG_SETMASK, old)


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def sha(path: pathlib.Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_commit(value: str) -> str:
    if len(value) != 40 or any(c not in "0123456789abcdef" for c in value):
        raise ValueError("exact lowercase 40-hex campaign commit required")
    return value


def atomic_json(path: pathlib.Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("xb") as stream:
        stream.write(canonical(value)); stream.flush(); os.fsync(stream.fileno())
    os.replace(tmp, path)
    fd = os.open(path.parent, os.O_RDONLY)
    try: os.fsync(fd)
    finally: os.close(fd)


def prime(n: int) -> bool:
    if type(n) is not int or n < 2: return False
    for p in (2,3,5,7,11,13,17,19,23,29,31,37):
        if n % p == 0: return n == p
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    for a in (2,325,9375,28178,450775,9780504,1795265022):
        if a % n == 0: continue
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True


def _rho(n: int, salt: int) -> int:
    if n % 2 == 0: return 2
    rng = random.Random((n << 17) ^ salt); c = rng.randrange(1, n); x = rng.randrange(2, n); y = x; d = 1
    while d == 1:
        x = (x*x+c) % n; y = (y*y+c) % n; y = (y*y+c) % n; d = math.gcd(abs(x-y), n)
    return d


def factorint(n: int) -> list[list[int]]:
    if n < 1: raise ValueError("positive factor target required")
    raw: list[int] = []
    def rec(x: int) -> None:
        if x == 1: return
        if prime(x): raw.append(x); return
        for salt in range(1, 65):
            d = _rho(x, salt)
            if d not in (1, x): rec(d); rec(x // d); return
        raise RuntimeError("deterministic factor budget exhausted")
    rec(n); raw.sort(); answer=[]
    for p in raw:
        if answer and answer[-1][0] == p: answer[-1][1] += 1
        else: answer.append([p,1])
    if math.prod(p**e for p,e in answer) != n or any(not prime(p) for p,_ in answer):
        raise RuntimeError("incomplete factorization")
    return answer


def sieve(limit: int) -> bytearray:
    values = bytearray(b"\x01") * (limit + 1); values[:2] = b"\x00\x00"
    for p in range(2, math.isqrt(limit) + 1):
        if values[p]: values[p*p:limit+1:p] = b"\x00" * (((limit-p*p)//p)+1)
    return values


def values(n: int, primality) -> tuple[int,int,set[int]]:
    half = {k*(n-k)-1 for k in range(1, n//2 + 1)}
    full = {k*(n-k)-1 for k in range(1, n)}
    if half != full: raise ValueError(f"Nat-safe symmetry failure at n={n}")
    ps = {x for x in half if primality(x)}
    return (max(ps, default=0), len(ps), ps)


def parse_bfile(path: pathlib.Path, spec: dict) -> list[tuple[int,int]]:
    if sha(path) != spec["sha256"]: raise ValueError(f"{spec['sequence']} b-file hash drift")
    rows=[]
    for line in path.read_text(encoding="ascii").splitlines():
        if not line or line.startswith("#"): continue
        a,b=line.split(); rows.append((int(a),int(b)))
    if len(rows)!=spec["rows"] or [n for n,_ in rows] != list(range(1,spec["last_index"]+1)):
        raise ValueError(f"{spec['sequence']} b-file coverage drift")
    return rows


def api(url: str, token: str) -> object:
    req=urllib.request.Request(url,headers={"Accept":"application/vnd.github+json","Authorization":f"Bearer {token}","User-Agent":"c5-k4-a1099-gate"})
    with urllib.request.urlopen(req,timeout=30) as response: return json.load(response)

def api_post(url: str, token: str, value: dict) -> object:
    req=urllib.request.Request(url,data=json.dumps(value).encode(),headers={"Accept":"application/vnd.github+json","Authorization":f"Bearer {token}","User-Agent":"c5-k4-a1099-gate","Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=30) as response:return json.load(response)


def live_audit(path: pathlib.Path, token: str) -> None:
    commit=api("https://api.github.com/repos/google-deepmind/formal-conjectures/commits/main",token)
    oeis_commit=api("https://api.github.com/repos/oeis/oeisdata/commits/main",token)
    searches={}
    for owner in ("google-deepmind/formal-conjectures","Kuberwastaken/c5-k4"):
        for seq in ("A109908","OeisA109908","A109909","OeisA109909"):
            q=f"repo:{owner} {seq}"; result=api("https://api.github.com/search/issues?"+urllib.parse.urlencode({"q":q,"per_page":100}),token)
            if result["incomplete_results"] or result["total_count"] != len(result["items"]): raise ValueError("search incomplete/truncated")
            searches[q]=result["total_count"]
    pulls=[]; touches=[]
    targets={x["path"] for x in M["formal_conjectures"]["targets"]}
    query='''query($cursor:String){repository(owner:"google-deepmind",name:"formal-conjectures"){pullRequests(states:OPEN,first:100,after:$cursor){nodes{number url files(first:100){nodes{path changeType} pageInfo{hasNextPage}}}pageInfo{hasNextPage endCursor}}}}'''
    cursor=None
    while True:
        response=api_post("https://api.github.com/graphql",token,{"query":query,"variables":{"cursor":cursor}})
        if response.get("errors"):raise ValueError("GraphQL race audit failed")
        page=response["data"]["repository"]["pullRequests"];pulls.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:break
        cursor=page["pageInfo"]["endCursor"]
    for pull in pulls:
        files=pull["files"]["nodes"]
        if pull["files"]["pageInfo"]["hasNextPage"] or any(x.get("changeType")=="RENAMED" for x in files):
            files=[];pageno=1
            while True:
                batch=api(f"https://api.github.com/repos/google-deepmind/formal-conjectures/pulls/{pull['number']}/files?per_page=100&page={pageno}",token);files.extend(batch)
                if len(batch)<100:break
                pageno+=1
        if any(x.get("path") in targets or x.get("filename") in targets or x.get("previous_filename") in targets for x in files):
            touches.append({"number":pull["number"],"url":pull["url"]})
    ingestion=api("https://api.github.com/repos/google-deepmind/formal-conjectures/pulls/4450",token)
    ingestion_identity={"number":ingestion["number"],"state":"MERGED" if ingestion["merged_at"] else ingestion["state"].upper(),"merged_at":ingestion["merged_at"],
                        "merge_commit":ingestion["merge_commit_sha"],"head_commit":ingestion["head"]["sha"]}
    releases=[];page_number=1
    while True:
        batch=api(f"https://api.github.com/repos/Kuberwastaken/c5-k4/releases?per_page=100&page={page_number}",token);releases.extend(batch)
        if len(batch)<100:break
        page_number+=1
    release_matches=[]
    for release in releases:
        text="\n".join(str(release.get(key) or "") for key in ("name","tag_name","body"))
        if "A109908" in text or "A109909" in text:release_matches.append({"tag":release["tag_name"],"url":release["html_url"]})
    value={"schema":"oeis-a109908-a109909-live-audit-v1","head":commit["sha"],"tree":commit["commit"]["tree"]["sha"],
           "oeis_head":oeis_commit["sha"],"oeis_tree":oeis_commit["commit"]["tree"]["sha"],
           "open_pull_requests_scanned":len(pulls),"searches":searches,"open_target_path_touches":touches,
           "known_ingestion":ingestion_identity,"local_releases_scanned":len(releases),"local_release_matches":release_matches}
    atomic_json(path,value)


def prepare_gate(input_dir: pathlib.Path, output: pathlib.Path, commit: str) -> None:
    exact_commit(commit)
    if output.exists(): raise FileExistsError(output)
    audit=json.loads((input_dir/"live-audit.json").read_text())
    formal=M["formal_conjectures"]
    if (audit.get("head"),audit.get("tree"))!=(formal["commit"],formal["tree"]) or audit.get("open_target_path_touches"):
        raise ValueError("live source/race drift")
    oeis=M["oeis_source"]
    if (audit.get("oeis_head"),audit.get("oeis_tree"))!=(oeis["commit"],oeis["tree"]):
        raise ValueError("live OEIS source drift")
    source_status=json.loads((HERE/"source-status-attestation.json").read_text())
    if audit.get("searches") != source_status["exact_searches"]:
        raise ValueError("live duplicate-search drift")
    if audit.get("known_ingestion") != source_status["known_ingestion"] or audit.get("local_release_matches"):
        raise ValueError("ingestion/release race drift")
    for target in formal["targets"]:
        for suffix in ("", "-live"):
            path=input_dir/f"{target['sequence'][1:]}{suffix}.lean"
            if sha(path)!=target["sha256"] or "@[category research open" not in path.read_text() or "sorry" not in path.read_text():
                raise ValueError("formal source/status drift")
    for source in M["oeis_source"]["targets"]:
        for suffix in ("", "-live"):
            if sha(input_dir/f"{source['sequence']}{suffix}.seq") != source["sha256"]: raise ValueError("OEIS source drift")
    specs={x["sequence"]:x for x in M["oeis_source"]["bfiles"]}
    rows908=parse_bfile(input_dir/"b109908.txt",specs["A109908"]); rows909=parse_bfile(input_dir/"b109909.txt",specs["A109909"])
    ps=sieve(25_000_000)
    for n,expected in rows908:
        if values(n,lambda x: x>=0 and x<len(ps) and bool(ps[x]))[0] != expected: raise ValueError(f"A109908 row drift at {n}")
    for n,expected in rows909:
        if values(n,lambda x: x>=0 and x<len(ps) and bool(ps[x]))[1] != expected: raise ValueError(f"A109909 row drift at {n}")
    controls=json.loads((HERE/"controls.json").read_text())
    for i,n in enumerate(controls["n"]):
        maximum,count,_=values(n,prime)
        if (maximum,count)!=(controls["A109908"][i],controls["A109909"][i]): raise ValueError("independent control drift")
    output.mkdir(parents=True); snapshots=output/"snapshots"; snapshots.mkdir()
    for name in ("109908.lean","109909.lean","109908-live.lean","109909-live.lean",
                 "A109908.seq","A109909.seq","A109908-live.seq","A109909-live.seq",
                 "b109908.txt","b109909.txt","live-audit.json"):
        shutil.copy2(input_dir/name,snapshots/name)
    att={"schema":"oeis-a109908-a109909-gate-v1","campaign_commit":commit,"manifest_sha256":sha(MANIFEST),
         "audit_sha256":sha(snapshots/"live-audit.json"),"rows":{"A109908":len(rows908),"A109909":len(rows909)},
         "controls":20,"status":"VERIFIED"}
    atomic_json(output/"gate-attestation.json",att)


def verify_gate(bundle: pathlib.Path, commit: str) -> dict:
    exact_commit(commit); doc=json.loads((bundle/"gate-attestation.json").read_text())
    expected={"schema":"oeis-a109908-a109909-gate-v1","campaign_commit":commit,"manifest_sha256":sha(MANIFEST),
              "audit_sha256":sha(bundle/"snapshots/live-audit.json"),"rows":{"A109908":10000,"A109909":93},"controls":20,"status":"VERIFIED"}
    if canonical(doc)!=canonical(expected): raise ValueError("gate attestation drift")
    return doc


def roots(q: int, residue: int) -> tuple[int,...]:
    found=tuple(k for k in range(1,q) if (k + pow(k,-1,q))%q==residue)
    if any(pow(k,-1,q) not in found for k in found): raise RuntimeError("inverse-pair drift")
    return found


def residue_masks(q: int, prefix: int) -> list[tuple[int,tuple[int,...],int]]:
    answer=[]
    for residue in range(q):
        rs=roots(q,residue)
        if not rs: continue
        mask=0
        for root in rs:
            start=root if root else q
            for k in range(start,prefix+1,q): mask |= 1 << (k-1)
        answer.append((residue,rs,mask))
    return answer


def crt(a: int, m: int, residue: int, q: int) -> tuple[int,int]:
    t=((residue-a)*pow(m,-1,q))%q; modulus=m*q
    return (a+m*t)%modulus,modulus


def first_uncovered(mask: int, prefix: int) -> int:
    missing=(~mask)&((1<<prefix)-1)
    return prefix+1 if not missing else (missing & -missing).bit_length()


def frozen_profiles():
    spec=M["construction"]; prefix=spec["construction_prefix_k"]
    beam=[(0,1,tuple(),tuple(),0)] # residue, modulus, selected residues, root rows, mask
    ordinal=0
    for depth,q in enumerate(spec["divisor_primes"],1):
        expanded=[]; options=residue_masks(q,prefix)
        for a,m,selected,root_rows,mask in beam:
            for residue,rs,qmask in options:
                na,nm=crt(a,m,residue,q); nmask=mask|qmask
                score=(-first_uncovered(nmask,prefix),-nmask.bit_count(),na,selected+(residue,))
                expanded.append((score,(na,nm,selected+(residue,),root_rows+((q,residue,rs),),nmask)))
        expanded.sort(key=lambda x:x[0]); beam=[state for _,state in expanded[:spec["beam_width"]]]
        if depth>=spec["profile_minimum_depth"]:
            for state in beam:
                if state[1] <= M["candidate_n_maximum"]//2:
                    raise RuntimeError("selected-profile lcm obstruction")
                yield ordinal,depth,state; ordinal+=1


def representatives(a: int, modulus: int):
    lo,hi=M["candidate_n_minimum"],M["candidate_n_maximum"]
    first=a if a>=lo else a+((lo-a+modulus-1)//modulus)*modulus
    for n in range(first,hi+1,modulus): yield n


def coverage(n: int, root_rows: tuple, deadline_check=True) -> dict:
    end=n//2; block=M["construction"]["coverage_block_size"]; digest=hashlib.sha256(); covered=0
    for lo in range(1,end+1,block):
        hi=min(end,lo+block-1); labels=bytearray(hi-lo+1)
        for index,(q,residue,rs) in enumerate(root_rows,1):
            if n%q!=residue: raise ValueError("CRT/profile drift")
            for root in rs:
                first=lo+((root-lo)%q); count=(hi-first)//q+1 if first<=hi else 0
                if count: labels[first-lo::q]=bytes([index])*count
        try: offset=labels.index(0)
        except ValueError: digest.update(labels); covered+=len(labels)
        else:
            digest.update(labels[:offset]); k=lo+offset; value=k*(n-k)-1; factors=factorint(value)
            return {"complete":False,"covered":covered+offset,"first_uncovered_k":k,"value":value,
                    "factors":factors,"escape_is_prime":len(factors)==1 and factors[0]==[value,1],"coverage_sha256":digest.hexdigest()}
    return {"complete":True,"covered":end,"coverage_sha256":digest.hexdigest(),"blocks":math.ceil(end/block)}


class Ledger:
    def __init__(self,path:pathlib.Path): self.path=path; self.stream=path.open("x",encoding="ascii"); self.seq=0; self.tail=ZERO
    def append(self,payload:dict):
        row={**payload,"seq":self.seq,"previous_row_sha256":self.tail}; body=json.dumps(row,sort_keys=True,separators=(",",":")); row["row_sha256"]=hashlib.sha256(body.encode()).hexdigest()
        self.stream.write(json.dumps(row,sort_keys=True,separators=(",",":"))+"\n"); self.stream.flush(); os.fsync(self.stream.fileno()); self.tail=row["row_sha256"]; self.seq+=1
    def close(self): self.stream.close()


def run_search(args) -> int:
    commit=exact_commit(args.campaign_commit)
    if subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()!=commit: raise ValueError("campaign checkout mismatch")
    gate=verify_gate(args.gate_bundle,commit); args.output.mkdir(parents=True,exist_ok=False); ledger=Ledger(args.output/"ledger.jsonl")
    counts={x:0 for x in STOPS}; visited=0; terminal_reason="DOMAIN_EXHAUSTED"; candidate=None; error=None
    signal.signal(signal.SIGALRM,_alarm); signal.alarm(M["internal_seconds"])
    try:
        for ordinal,depth,(a,modulus,residues,root_rows,mask) in frozen_profiles():
            if ordinal%M["shards"]!=args.shard: continue
            for n in representatives(a,modulus):
                if visited>=M["construction"]["maximum_trials_per_shard"]: terminal_reason="FROZEN_TRIAL_LIMIT"; raise StopIteration
                result=coverage(n,root_rows); stop="FULL_COVER" if result["complete"] else "PRIME_ESCAPE" if result["escape_is_prime"] else "COMPOSITE_ESCAPE"
                profile={"ordinal":ordinal,"depth":depth,"crt_residue":a,"modulus":modulus,"selected_residues":list(residues),
                         "root_classes":[{"q":q,"n_residue":r,"roots":list(rs)} for q,r,rs in root_rows]}
                row={"schema":"oeis-a109908-a109909-trial-v1","campaign_commit":commit,"shard":args.shard,"profile":profile,"n":n,"outcome":stop,"coverage":result}
                with blocked_alarm():
                    ledger.append(row); counts[stop]+=1; visited+=1
                if stop=="FULL_COVER":
                    candidate={"schema":"oeis-a109908-a109909-candidate-v1","campaign_commit":commit,"manifest_sha256":sha(MANIFEST),
                               "gate_attestation_sha256":sha(args.gate_bundle/"gate-attestation.json"),"n":n,"half_end":n//2,
                               "profile":profile,"coverage":result,"properness_bound":{"largest_q":max(x[0] for x in root_rows),"n_minus_two":n-2},
                               "status":"LITERAL_SHARED_COUNTEREXAMPLE_PENDING_LEAN"}
                    signal.alarm(0)
                    with blocked_alarm():
                        atomic_json(args.output/"candidate.json",candidate)
                        terminal_reason="CANDIDATE_FOUND"
                    raise StopIteration
    except Deadline: terminal_reason="CAP_PREFIX"; counts["CAP_PREFIX"]+=1
    except StopIteration: pass
    except BaseException as exc: terminal_reason="WORKER_ERROR"; counts["WORKER_ERROR"]+=1; error={"type":type(exc).__name__,"message":str(exc)[:1000]}
    finally:
        signal.alarm(0); ledger.close()
        candidate_path=args.output/"candidate.json"
        terminal={"schema":"oeis-a109908-a109909-terminal-v1","campaign_commit":commit,"gate_attestation_sha256":sha(args.gate_bundle/"gate-attestation.json"),
                  "shard":args.shard,"visited":visited,"counts":counts,"terminal_reason":terminal_reason,"candidate_present":candidate is not None,
                  "candidate_sha256":sha(candidate_path) if candidate_path.exists() else None,
                  "coverage_sha256":candidate["coverage"]["coverage_sha256"] if candidate is not None else None,
                  "worker_error":error,"ledger_rows":ledger.seq,"final_row_sha256":ledger.tail,"ledger_sha256":sha(args.output/"ledger.jsonl")}
        atomic_json(args.output/"terminal.json",terminal)
    return 21 if error else 0


def main() -> int:
    parser=argparse.ArgumentParser(); sub=parser.add_subparsers(dest="command",required=True)
    p=sub.add_parser("live-audit"); p.add_argument("output",type=pathlib.Path)
    p=sub.add_parser("prepare-gate"); p.add_argument("input",type=pathlib.Path); p.add_argument("output",type=pathlib.Path); p.add_argument("--campaign-commit",required=True)
    p=sub.add_parser("verify-gate"); p.add_argument("bundle",type=pathlib.Path); p.add_argument("--campaign-commit",required=True)
    p=sub.add_parser("search"); p.add_argument("--campaign-commit",required=True); p.add_argument("--gate-bundle",type=pathlib.Path,required=True); p.add_argument("--shard",type=int,choices=range(M["shards"]),required=True); p.add_argument("--output",type=pathlib.Path,required=True)
    args=parser.parse_args()
    if args.command=="live-audit": live_audit(args.output,os.environ["GITHUB_TOKEN"]); return 0
    if args.command=="prepare-gate": prepare_gate(args.input,args.output,args.campaign_commit); return 0
    if args.command=="verify-gate": verify_gate(args.bundle,args.campaign_commit); return 0
    return run_search(args)


if __name__=="__main__": raise SystemExit(main())
