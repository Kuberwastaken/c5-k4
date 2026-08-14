#!/usr/bin/env python3
"""Prepare or verify the immutable, reusable A105720 source/database gate."""
from __future__ import annotations

import argparse, hashlib, json, math, os, pathlib, shutil, struct, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
FREEZE = ROOT / "results/expansion/live-search-2026-08-14/oeis-a105720-development"
MANIFEST = json.loads((FREEZE / "manifest.json").read_text())
STATEMENT = "∀ n : ℕ, 0 < n → (IsSquare (a n) ↔ (n = 3 ∨ n = 6 ∨ n = 4072))"

def sha(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""): h.update(block)
    return h.hexdigest()

def atomic_json(path: pathlib.Path, value: object) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="ascii") as f:
        json.dump(value, f, sort_keys=True, separators=(",", ":")); f.write("\n"); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)

def sieve(count: int) -> list[int]:
    if count < 1: return []
    n = max(16, math.ceil(count * (math.log(count) + math.log(math.log(count)))) + 64)
    while True:
        bits = bytearray(b"\x01") * (n + 1); bits[0:2] = b"\x00\x00"
        for p in range(2, math.isqrt(n) + 1):
            if bits[p]: bits[p*p:n+1:p] = b"\x00" * (((n-p*p)//p)+1)
        values = [i for i, yes in enumerate(bits) if yes]
        if len(values) >= count: return values[:count]
        n *= 2

def build_child(output: pathlib.Path, count: int) -> None:
    values = sieve(count)
    with output.open("wb") as f:
        for start in range(0, len(values), 65536):
            chunk = values[start:start+65536]
            f.write(struct.pack(f"<{len(chunk)}I", *chunk))
        f.flush(); os.fsync(f.fileno())

def read_primes(path: pathlib.Path) -> list[int]:
    raw = path.read_bytes()
    if len(raw) % 4: raise ValueError("prime table byte length")
    return list(struct.unpack(f"<{len(raw)//4}I", raw))

def parse_bfile(path: pathlib.Path) -> dict[int, int]:
    rows: dict[int, int] = {}
    for line in path.read_text(encoding="ascii").splitlines():
        if not line or line.startswith("#"): continue
        fields = line.split()
        if len(fields) != 2: raise ValueError("malformed b-file row")
        n, value = map(int, fields)
        if n in rows: raise ValueError("duplicate b-file index")
        rows[n] = value
    return rows

def window_sum(primes: list[int], n: int) -> int:
    return sum(primes[n-1:2*n])

def verify_sources(lean: pathlib.Path, bfile: pathlib.Path) -> None:
    fm, bm = MANIFEST["formal_conjectures"], MANIFEST["oeis_bfile"]
    if sha(lean) != fm["sha256"] or sha(bfile) != bm["sha256"]: raise ValueError("source hash mismatch")
    text = lean.read_text(encoding="utf-8")
    compact = " ".join(text.split())
    expected = "theorem conjecture : ∀ n : ℕ, 0 < n → (IsSquare (a n) ↔ (n = 3 ∨ n = 6 ∨ n = 4072)) := by sorry"
    if expected not in compact or "@[category research open, AMS 11]" not in text: raise ValueError("declaration/status shape mismatch")
    rows = parse_bfile(bfile)
    if len(rows) != bm["rows"] or sorted(rows) != list(range(1, bm["rows"] + 1)): raise ValueError("b-file extent mismatch")
    for n, value in MANIFEST["controls"].items():
        if int(n) <= bm["rows"] and rows[int(n)] != value: raise ValueError(f"b-file control {n}")

def prepare(lean: pathlib.Path, bfile: pathlib.Path, out: pathlib.Path, commit: str) -> None:
    if len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit): raise ValueError("campaign commit")
    verify_sources(lean, bfile)
    out.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(lean, out / "105720.lean"); shutil.copyfile(bfile, out / "b105720.txt")
    prime_path = out / "primes.u32"
    subprocess.run([sys.executable, __file__, "--build-primes-child", str(prime_path), str(MANIFEST["prime_count"])], check=True, timeout=MANIFEST["child_seconds"])
    primes = read_primes(prime_path)
    if len(primes) != MANIFEST["prime_count"]: raise ValueError("prime count")
    for n, value in MANIFEST["controls"].items():
        if window_sum(primes, int(n)) != value: raise ValueError(f"prime control {n}")
    shutil.copyfile(FREEZE / "manifest.json", out / "manifest.json")
    shutil.copyfile(FREEZE / "source-status-attestation.json", out / "source-status-attestation.json")
    files = {p.name: sha(p) for p in sorted(out.iterdir()) if p.is_file()}
    atomic_json(out / "gate-attestation.json", {"schema":"oeis-a105720-gate-v1","campaign_commit":commit,"files":files,"prime_count":len(primes),"last_prime":primes[-1]})
    verify(out, commit)

def verify(out: pathlib.Path, commit: str) -> dict:
    att = json.loads((out / "gate-attestation.json").read_text())
    if att.get("schema") != "oeis-a105720-gate-v1" or att.get("campaign_commit") != commit: raise ValueError("gate binding")
    expected = {"105720.lean", "b105720.txt", "manifest.json", "source-status-attestation.json", "primes.u32"}
    if set(att.get("files", {})) != expected: raise ValueError("gate file set")
    for name, digest in att.get("files", {}).items():
        if sha(out / name) != digest: raise ValueError(f"gate file hash {name}")
    if json.loads((out / "manifest.json").read_text()) != MANIFEST: raise ValueError("gate manifest")
    if (out / "source-status-attestation.json").read_bytes() != (FREEZE / "source-status-attestation.json").read_bytes(): raise ValueError("source/status attestation")
    verify_sources(out / "105720.lean", out / "b105720.txt")
    primes = read_primes(out / "primes.u32")
    if len(primes) != MANIFEST["prime_count"] or att.get("prime_count") != len(primes) or primes[-1] != att.get("last_prime"): raise ValueError("prime table extent")
    for n, value in MANIFEST["controls"].items():
        if window_sum(primes, int(n)) != value: raise ValueError(f"gate prime control {n}")
    return att

def main() -> None:
    p = argparse.ArgumentParser(); g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--prepare", nargs=3, metavar=("LEAN","BFILE","OUT")); g.add_argument("--verify", metavar="GATE")
    g.add_argument("--build-primes-child", nargs=2, metavar=("OUT","COUNT")); p.add_argument("--campaign-commit")
    a = p.parse_args()
    if a.build_primes_child: build_child(pathlib.Path(a.build_primes_child[0]), int(a.build_primes_child[1])); return
    if not a.campaign_commit: p.error("--campaign-commit required")
    if a.prepare: prepare(*(pathlib.Path(x) for x in a.prepare), a.campaign_commit)
    else: verify(pathlib.Path(a.verify), a.campaign_commit)

if __name__ == "__main__": main()
