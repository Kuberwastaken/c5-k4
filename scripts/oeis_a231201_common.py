#!/usr/bin/env python3
"""Shared frozen constants and artifact primitives; no target scan on import."""
from __future__ import annotations
import hashlib, json, math, os, pathlib
from typing import Any, Iterable

ROOT=pathlib.Path(__file__).resolve().parents[1]
FREEZE=ROOT/"results/expansion/live-search-2026-08-14/oeis-a231201-development"
MANIFEST_PATH=FREEZE/"manifest.json"
M=json.loads(MANIFEST_PATH.read_text())
ZERO="0"*64

def canonical(value:Any)->bytes:
    return (json.dumps(value,sort_keys=True,separators=(",",":"))+"\n").encode("ascii")

def sha(path:pathlib.Path)->str:
    h=hashlib.sha256()
    with pathlib.Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""): h.update(block)
    return h.hexdigest()

def exact_commit(value:str)->str:
    if len(value)!=40 or any(c not in "0123456789abcdef" for c in value): raise ValueError("exact lowercase campaign commit required")
    return value

def atomic_json(path:pathlib.Path,value:dict)->None:
    path.parent.mkdir(parents=True,exist_ok=True); temp=path.with_suffix(path.suffix+".tmp")
    with temp.open("xb") as f: f.write(canonical(value)); f.flush(); os.fsync(f.fileno())
    os.replace(temp,path)

class Ledger:
    def __init__(self,path:pathlib.Path):
        path.parent.mkdir(parents=True,exist_ok=True); self.path=path; self.file=path.open("x",encoding="ascii"); self.seq=0; self.previous=ZERO
    def append(self,payload:dict)->str:
        row=dict(payload); row["seq"]=self.seq; row["previous_row_sha256"]=self.previous
        raw=json.dumps(row,sort_keys=True,separators=(",",":")); digest=hashlib.sha256(raw.encode("ascii")).hexdigest(); row["row_sha256"]=digest
        self.file.write(json.dumps(row,sort_keys=True,separators=(",",":"))+"\n"); self.file.flush(); os.fsync(self.file.fileno()); self.seq+=1; self.previous=digest; return digest
    def close(self)->None: self.file.close()

def is_prime_trial(n:int)->bool:
    if n<2:return False
    if n%2==0:return n==2
    d=3
    while d*d<=n:
        if n%d==0:return False
        d+=2
    return True

def order_two(q:int)->int:
    if q==2:return 1
    x=2%q
    for order in range(1,q):
        if x==1:return order
        x=x*2%q
    raise ValueError(f"no order for {q}")

def order_table()->list[tuple[int,int,int]]:
    return [(q,order_two(q),q*order_two(q)) for q in M["primes"]]

def combined_period()->int:
    return math.lcm(*(modulus for _,_,modulus in order_table()))

def positive_representative(residue:int,modulus:int)->int:
    residue%=modulus
    return residue if residue else modulus

def periodic_value(q:int,residue:int)->int:
    modulus=q*order_two(q); x=positive_representative(residue,modulus)
    return (x-pow(2,x,q))%q

def direct_value(q:int,x:int)->int:
    if x<0: raise ValueError("exponents are nonnegative")
    return (x-pow(2,x,q))%q

def signature(x:int)->tuple[tuple[int,int],...]:
    return tuple((q,direct_value(q,x)) for q in M["primes"])

def periodic_signature(residue:int)->tuple[tuple[int,int],...]:
    return tuple((q,periodic_value(q,residue)) for q in M["primes"])

def shard_fixed(arm:str,shard:int)->dict[int,int]:
    arms=M["partition"]["arms"]
    if arm not in arms or shard not in M["partition"]["shards"]: raise ValueError("unknown assignment shard")
    return {2:int(arms[arm]),3:int(shard)}

def crt_pair(r:int,m:int,s:int,n:int)->tuple[int,int]|None:
    g=math.gcd(m,n)
    if (s-r)%g:return None
    mm=m//g; nn=n//g
    k=((s-r)//g*pow(mm,-1,nn))%nn
    modulus=m*nn
    return (r+m*k)%modulus,modulus

def queue_hash(states:Iterable[tuple[int,int]])->str:
    h=hashlib.sha256()
    for r,m in states:h.update(f"{r},{m}\n".encode("ascii"))
    return h.hexdigest()
