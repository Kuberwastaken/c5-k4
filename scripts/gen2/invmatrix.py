"""Compute the exact invariant matrix over `D2`, once per backend.

Both backends produce, for every member of `D2`, all 51 invariants as exact
`int`/`Fraction` values; each value is multiplied by `SCALE = 2520` and asserted
to be an integer, so the cached `int64` matrices are an exact representation and
comparing them element by element (``crossval.py``) is an exact comparison.

Deterministic: `D2` is enumerated in a fixed order and `multiprocessing.Pool.imap`
preserves it, so the cached matrices are byte-identical between runs.

Usage:
    python3 scripts/gen2/invmatrix.py A          # backend A (exhaustive bit-mask)
    python3 scripts/gen2/invmatrix.py B          # backend B (networkx + BB)
"""
from __future__ import annotations

import multiprocessing as mp
import os
import sys
import time
from fractions import Fraction
from typing import List, Tuple

import numpy as np

import graph_db2 as DB
import invariants2 as I
from expressions2 import SCALE

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(HERE, "data")
WORKERS = int(os.environ.get("GEN2_WORKERS", "6"))
CHUNK = 200


def cache_path(backend: str) -> str:
    return os.path.join(CACHE_DIR, "invariants_n2_n9_%s.npz" % backend)


def _row(args: Tuple[str, str]) -> List[int]:
    code, backend = args
    vals = I.compute(code, backend)
    row = []
    for k in I.VOCAB:
        v = Fraction(vals[k]) * SCALE
        if v.denominator != 1:
            raise AssertionError("SCALE=%d does not clear %s on %s" % (SCALE, k, code))
        row.append(int(v))
    return row


def build(backend: str, codes: List[str]) -> np.ndarray:
    t0 = time.time()
    rows: List[List[int]] = []
    with mp.Pool(WORKERS) as pool:
        for i, row in enumerate(pool.imap(_row, ((c, backend) for c in codes), CHUNK)):
            rows.append(row)
            if (i + 1) % 20000 == 0:
                print("    %s %d/%d  %.0fs" % (backend, i + 1, len(codes),
                                               time.time() - t0), flush=True)
    return np.array(rows, dtype=np.int64)


def load(backend: str, codes: List[str] = None, rebuild: bool = False) -> np.ndarray:
    path = cache_path(backend)
    if not rebuild and os.path.exists(path):
        z = np.load(path, allow_pickle=False)
        if list(z["names"]) == I.VOCAB:
            return z["M"]
    if codes is None:
        codes = DB.load_codes()
    M = build(backend, codes)
    os.makedirs(CACHE_DIR, exist_ok=True)
    np.savez_compressed(path, names=np.array(I.VOCAB), M=M)
    return M


def main() -> int:
    backend = sys.argv[1] if len(sys.argv) > 1 else "A"
    codes = DB.load_codes()
    print("|D2| = %d, backend %s, %d workers" % (len(codes), backend, WORKERS), flush=True)
    t0 = time.time()
    M = load(backend, codes, rebuild="--rebuild" in sys.argv)
    print("matrix %s shape=%s  %.0fs  -> %s (%.1f MB)"
          % (backend, M.shape, time.time() - t0, cache_path(backend),
             os.path.getsize(cache_path(backend)) / 1e6))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
