"""Build the frozen verification database `D2` for the v2 fresh-population generator.

`D2` = every connected graph on `2 <= n <= 9` vertices, up to isomorphism.

    n     connected graphs (OEIS A001349)
    2     1
    3     2
    4     6
    5     21
    6     112
    7     853
    8     11,117
    9     261,080
    total 273,192

This is the harder database edge required by `results/experiment-v2/DESIGN.md`.
v1 stopped at `n <= 8` (12,112 graphs) and 14 of its 30 targets fell to plain
annealing; the v2 population is filtered against 22.6x as many graphs, one
vertex further out.

Source of the graphs
--------------------
`geng` from **nauty 2.8.8** (Brendan McKay / Adolfo Piperno), built from the
source bundled in the `pynauty` 2.8.8.1 sdist.  `geng -c n` emits exactly one
representative of every isomorphism class of connected graph on `n` vertices.

Two checks make the database self-certifying, so nothing depends on trusting
`geng`:

  * **count** -- the number produced for each `n` equals A001349(n) exactly, and
    the file contains no duplicate graph6 string;
  * **completeness, independently** (`--verify`) -- every connected graph on 9
    vertices has a non-cut vertex, so deleting it leaves a *connected* graph on 8
    vertices.  Extending all 11,117 connected 8-vertex graphs by one vertex over
    all 255 non-empty neighbourhoods therefore produces every connected 9-vertex
    graph at least once.  Canonicalising those 2,834,835 extensions (`labelg`)
    and comparing the resulting set to the canonicalised `geng` output must give
    equality.  The n <= 8 part is checked the same way against v1's database file
    `scripts/gen/data/connected_n2_n8.g6`, which was built by a completely
    different route (networkx atlas + VF2 isomorphism rejection).

`K_1` is excluded, exactly as in v1: with no edges and no neighbourhoods,
`deg_avg`, `lambda(v)`, `girth`, `disp` and the domination invariants are 0 or
undefined on it, and Graffiti-lineage databases do not contain it.  Every emitted
statement is quantified over **connected graphs with `n >= 2`** and says so.

Deterministic: the cached file is the sorted list of graph6 strings; `load_codes`
returns them ordered by `(n, graph6)`.

Usage:
    python3 scripts/gen2/graph_db2.py                 # build + cache + counts
    python3 scripts/gen2/graph_db2.py --verify        # independent completeness proof
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from typing import Dict, List, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(HERE, "data")
DB_PATH = os.path.join(CACHE_DIR, "connected_n2_n9.g6")

MAX_N = 9

# Connected graphs on n nodes, OEIS A001349.  Used as a build-time self-check,
# never as a source of graphs.
EXPECTED = {2: 1, 3: 2, 4: 6, 5: 21, 6: 112, 7: 853, 8: 11117, 9: 261080}


# --------------------------------------------------------------------------
# graph6 <-> bitmask adjacency (no networkx: backend A must not share code with
# backend B, and 273k networkx objects do not fit in this box's spare RAM)
# --------------------------------------------------------------------------
def g6_to_adj(code: str) -> Tuple[List[int], int]:
    """Decode a graph6 string (n <= 62) to (adjacency bitmasks, n)."""
    data = [ord(c) - 63 for c in code.strip()]
    n = data[0]
    bits = []
    for byte in data[1:]:
        for k in range(5, -1, -1):
            bits.append(byte >> k & 1)
    adj = [0] * n
    p = 0
    for j in range(1, n):
        for i in range(j):
            if bits[p]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            p += 1
    return adj, n


def adj_to_g6(adj: List[int], n: int) -> str:
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(adj[i] >> j & 1)
    while len(bits) % 6:
        bits.append(0)
    out = [chr(n + 63)]
    for k in range(0, len(bits), 6):
        v = 0
        for b in bits[k:k + 6]:
            v = v * 2 + b
        out.append(chr(v + 63))
    return "".join(out)


def is_connected_adj(adj: List[int], n: int) -> bool:
    seen = 1
    frontier = 1
    while frontier:
        nxt = 0
        for v in range(n):
            if frontier >> v & 1:
                nxt |= adj[v]
        nxt &= ~seen
        if not nxt:
            break
        seen |= nxt
        frontier = nxt
    return seen == (1 << n) - 1


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------
def _geng(n: int) -> List[str]:
    exe = os.environ.get("NAUTY_GENG", "geng")
    out = subprocess.run([exe, "-c", "-q", str(n)], check=True,
                         stdout=subprocess.PIPE).stdout.decode()
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


def build(max_n: int = MAX_N) -> List[str]:
    codes: List[str] = []
    for n in range(2, max_n + 1):
        got = _geng(n)
        assert len(got) == EXPECTED[n], "n=%d: got %d, A001349 says %d" % (
            n, len(got), EXPECTED[n])
        assert len(set(got)) == len(got), "n=%d: duplicate graph6 strings" % n
        codes.extend(got)
    return codes


def load_codes(max_n: int = MAX_N, rebuild: bool = False) -> List[str]:
    """`D2` as graph6 strings, ordered by (n, graph6).  Cached on disk."""
    if rebuild or not os.path.exists(DB_PATH):
        os.makedirs(CACHE_DIR, exist_ok=True)
        codes = build(max_n)
        codes.sort(key=lambda c: (ord(c[0]) - 63, c))
        with open(DB_PATH, "w") as fh:
            fh.write("\n".join(codes) + "\n")
    with open(DB_PATH) as fh:
        codes = [ln.strip() for ln in fh if ln.strip()]
    codes.sort(key=lambda c: (ord(c[0]) - 63, c))
    return codes


def orders(codes: List[str]) -> List[int]:
    return [ord(c[0]) - 63 for c in codes]


def sha256_db() -> str:
    with open(DB_PATH, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


# --------------------------------------------------------------------------
# independent completeness verification
# --------------------------------------------------------------------------
def canonical_list(codes: List[str], chunk: int = 200000) -> List[str]:
    """Canonicalise graph6 strings with nauty `labelg`, preserving input order."""
    exe = os.environ.get("NAUTY_LABELG", "labelg")
    out: List[str] = []
    for k in range(0, len(codes), chunk):
        blob = "\n".join(codes[k:k + chunk]) + "\n"
        res = subprocess.run([exe, "-q"], input=blob.encode(), check=True,
                             stdout=subprocess.PIPE).stdout.decode()
        got = [ln.strip() for ln in res.splitlines() if ln.strip()]
        assert len(got) == len(codes[k:k + chunk]), "labelg dropped lines"
        out.extend(got)
    return out


def _canonical_set(codes: List[str], chunk: int = 200000) -> set:
    """Canonicalise graph6 strings with nauty `labelg` and return the set."""
    return set(canonical_list(codes, chunk))


def _extensions(base_codes: List[str]) -> List[str]:
    """All one-vertex extensions of `base_codes` that are connected.

    Every connected graph on n+1 vertices has a non-cut vertex; deleting it
    leaves a connected graph on n vertices.  So extending every connected
    n-vertex graph by one new vertex over every non-empty neighbourhood produces
    every connected (n+1)-vertex graph at least once.
    """
    out = []
    for code in base_codes:
        adj, n = g6_to_adj(code)
        for mask in range(1, 1 << n):
            ext = list(adj) + [mask]
            for i in range(n):
                if mask >> i & 1:
                    ext[i] |= 1 << n
            out.append(adj_to_g6(ext, n + 1))
    return out


def verify(codes: List[str]) -> int:
    by_n: Dict[int, List[str]] = {}
    for c in codes:
        by_n.setdefault(ord(c[0]) - 63, []).append(c)
    rc = 0

    # (i) counts and uniqueness
    for n in sorted(by_n):
        ok = len(by_n[n]) == EXPECTED[n] and len(set(by_n[n])) == len(by_n[n])
        print("count  n=%d  %7d  %s" % (n, len(by_n[n]), "ok" if ok else "MISMATCH"))
        rc |= 0 if ok else 1

    # (ii) every member connected, right order, graph6 round-trips
    bad = 0
    for c in codes:
        adj, n = g6_to_adj(c)
        if not is_connected_adj(adj, n) or adj_to_g6(adj, n) != c:
            bad += 1
    print("shape  all connected + graph6 round-trip: %s" % ("ok" if bad == 0 else "%d BAD" % bad))
    rc |= 0 if bad == 0 else 1

    # (iii) pairwise non-isomorphic (canonical forms all distinct)
    canon = _canonical_set(codes)
    print("iso    distinct canonical forms: %d / %d  %s"
          % (len(canon), len(codes), "ok" if len(canon) == len(codes) else "MISMATCH"))
    rc |= 0 if len(canon) == len(codes) else 1

    # (iv) completeness by independent one-vertex extension, level by level
    for n in sorted(by_n):
        if n + 1 not in by_n:
            continue
        ext = _extensions(by_n[n])
        got = _canonical_set(ext)
        want = _canonical_set(by_n[n + 1])
        ok = got == want
        print("cover  extensions of n=%d -> %d candidates -> %d classes; n=%d has %d; %s"
              % (n, len(ext), len(got), n + 1, len(want),
                 "EQUAL (complete)" if ok else "DIFFER: +%d -%d"
                 % (len(got - want), len(want - got))))
        rc |= 0 if ok else 1

    # (v) the n <= 8 part against v1's independently built database
    v1 = os.path.join(os.path.dirname(HERE), "gen", "data", "connected_n2_n8.g6")
    if os.path.exists(v1):
        with open(v1) as fh:
            v1codes = [ln.strip() for ln in fh if ln.strip()]
        a = _canonical_set(v1codes)
        b = _canonical_set([c for c in codes if ord(c[0]) - 63 <= 8])
        print("v1     n<=8 agrees with scripts/gen/data/connected_n2_n8.g6 "
              "(%d vs %d): %s" % (len(a), len(b), "ok" if a == b else "MISMATCH"))
        rc |= 0 if a == b else 1
    return rc


def main() -> int:
    codes = load_codes(rebuild="--rebuild" in sys.argv)
    by_n: Dict[int, int] = {}
    for c in codes:
        n = ord(c[0]) - 63
        by_n[n] = by_n.get(n, 0) + 1
    for n in sorted(by_n):
        ok = "ok" if by_n[n] == EXPECTED.get(n) else "MISMATCH exp %s" % EXPECTED.get(n)
        print("n=%d  %7d  %s" % (n, by_n[n], ok))
    print("|D2| = %d" % len(codes))
    print("sha256 = %s" % sha256_db())
    assert all(by_n[n] == EXPECTED[n] for n in by_n), "database count self-check failed"
    if "--verify" in sys.argv:
        return verify(codes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
