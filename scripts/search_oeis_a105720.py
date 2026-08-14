#!/usr/bin/env python3
"""Exact frozen A105720 worker; emits durable evidence, never a public claim."""
from __future__ import annotations
import argparse, hashlib, json, math, os, pathlib, signal, struct, time, traceback
from prepare_oeis_a105720_gate import MANIFEST, sha, verify

ZERO = "0" * 64

def arm_values(arm: str, shard: int):
    a = MANIFEST["arms"][arm]; shards = MANIFEST["shards"]
    if arm in ("CATALOGUE", "WALL_NAVIGATION"):
        yield from range(a["lo"] + shard, a["hi"] + 1, shards)
    else:
        for i in range(shard, a["count"], shards):
            yield a["lo"] + ((a["multiplier"] * i + a["offset"]) % a["width"])

def square_residue(value: int) -> bool:
    for m in MANIFEST["arms"]["WALL_NAVIGATION"]["moduli"]:
        if value % m not in {x*x % m for x in range(m)}: return False
    return True

class Ledger:
    def __init__(self, path: pathlib.Path):
        self.path=path; self.seq=0; self.previous=ZERO
        path.parent.mkdir(parents=True, exist_ok=True); self.file=path.open("x", encoding="ascii")
    def append(self, payload: dict) -> str:
        row=dict(payload); row["seq"]=self.seq; row["previous_row_sha256"]=self.previous
        canonical=json.dumps(row,sort_keys=True,separators=(",",":"))
        digest=hashlib.sha256(canonical.encode("ascii")).hexdigest(); row["row_sha256"]=digest
        self.file.write(json.dumps(row,sort_keys=True,separators=(",",":"))+"\n"); self.file.flush(); os.fsync(self.file.fileno())
        self.seq += 1; self.previous=digest; return digest
    def close(self): self.file.close()

def atomic_json(path: pathlib.Path, value: dict) -> None:
    tmp=path.with_suffix(path.suffix+".tmp")
    with tmp.open("x",encoding="ascii") as f:
        json.dump(value,f,sort_keys=True,separators=(",",":")); f.write("\n"); f.flush(); os.fsync(f.fileno())
    os.replace(tmp,path)

def load_primes(path: pathlib.Path) -> list[int]:
    raw=path.read_bytes(); return list(struct.unpack(f"<{len(raw)//4}I",raw))

def run(a) -> int:
    gate=verify(a.gate_bundle,a.campaign_commit); primes=load_primes(a.gate_bundle/"primes.u32")
    prefix=[0]
    for p in primes: prefix.append(prefix[-1]+p)
    gate_sha=sha(a.gate_bundle/"gate-attestation.json"); ledger=Ledger(a.ledger)
    deadline=time.monotonic()+MANIFEST["internal_seconds"]
    evaluated=screened=0; reason="DOMAIN_EXHAUSTED"; candidate=None
    try:
        for n in arm_values(a.arm,a.shard):
            if time.monotonic() >= deadline: reason="DEADLINE_PREFIX"; break
            value=prefix[2*n]-prefix[n-1]; screened += 1
            compatible=True if a.arm != "WALL_NAVIGATION" else square_residue(value)
            root=math.isqrt(value); exact=compatible and root*root==value; evaluated += int(compatible)
            residual=min(value-root*root,(root+1)*(root+1)-value)
            row={"schema":"oeis-a105720-row-v1","campaign_commit":a.campaign_commit,"source_commit":MANIFEST["formal_conjectures"]["commit"],"gate_attestation_sha256":gate_sha,"arm":a.arm,"shard":a.shard,"n":n,"a_n":value,"screen_pass":compatible,"exact_square":exact,"nearest_square_distance":residual}
            ledger.append(row)
            if exact and n not in MANIFEST["known_square_indices"]:
                candidate={**row,"schema":"oeis-a105720-certificate-v1","square_root":root,"prime_n":primes[n-1],"prime_2n":primes[2*n-1]}
                atomic_json(a.certificate,candidate); reason="CERTIFICATE_FOUND"; break
    except BaseException:
        reason="WORKER_ERROR"; ledger.append({"schema":"oeis-a105720-error-v1","campaign_commit":a.campaign_commit,"arm":a.arm,"shard":a.shard,"error":traceback.format_exc()}); raise
    finally:
        ledger.close()
        terminal={"schema":"oeis-a105720-terminal-v1","campaign_commit":a.campaign_commit,"source_commit":MANIFEST["formal_conjectures"]["commit"],"gate_attestation_sha256":gate_sha,"arm":a.arm,"shard":a.shard,"terminal_reason":reason,"screened":screened,"exact_evaluated":evaluated,"ledger_rows":ledger.seq,"final_row_sha256":ledger.previous,"ledger_sha256":sha(a.ledger)}
        atomic_json(a.terminal,terminal)
    return 0

def main():
    p=argparse.ArgumentParser(); p.add_argument("--arm",choices=tuple(MANIFEST["arms"]),required=True); p.add_argument("--shard",type=int,choices=range(MANIFEST["shards"]),required=True)
    p.add_argument("--campaign-commit",required=True); p.add_argument("--gate-bundle",type=pathlib.Path,required=True); p.add_argument("--ledger",type=pathlib.Path,required=True); p.add_argument("--terminal",type=pathlib.Path,required=True); p.add_argument("--certificate",type=pathlib.Path,required=True)
    a=p.parse_args()
    if len(a.campaign_commit)!=40 or any(c not in "0123456789abcdef" for c in a.campaign_commit): p.error("campaign commit must be 40 lowercase hex")
    raise SystemExit(run(a))
if __name__=="__main__": main()
