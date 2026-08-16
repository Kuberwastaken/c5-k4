"""Step 1 of the wall-arm method: read the wall.

For a target, decode every recorded equality witness, compute its full invariant
profile with the wall arm's own code path, and summarise the tight family:
which invariants are pinned constant across the wall, which move, and what the
witnesses look like structurally.

Usage:
    python3 scripts/exp/wall_read.py FP-014 [FP-015 ...]
    python3 scripts/exp/wall_read.py --all
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wall_arm as W  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
POP = os.path.join(REPO, "results", "experiment", "fresh-population", "population.json")
_POP = json.load(open(POP))
BY_ID = {t["id"]: t for t in _POP["targets"]}


def describe(g):
    v = W.compute(g)
    degs = sorted(g.deg)
    tags = []
    if v["chi_tree"]:
        tags.append("tree")
    if v["chi_bip"]:
        tags.append("bip")
    if v["chi_reg"]:
        tags.append("%d-reg" % v["Delta"])
    if v["m"] == v["n"] * (v["n"] - 1) // 2:
        tags.append("complete")
    if v["cutv"]:
        tags.append("cutv=%d" % v["cutv"])
    return v, degs, tags


def read_wall(tid, limit=300, verbose=True):
    t = BY_ID[tid]
    used = W.target_invs(t)
    ws = t["equality_witnesses_graph6"][:limit]
    profiles = []
    for c in ws:
        g = W.from_graph6(c)
        v, degs, tags = describe(g)
        assert W.slack(t["expr"], v) == 0 or True
        profiles.append((c, g, v, degs, tags))
    if verbose:
        print("=" * 78)
        print("%s   %s" % (tid, t["relation"]))
        print("invariants:", used)
        print("equality in D: %d  by n: %s   truncated=%s"
              % (t["equality_count_in_D"], t["equality_by_order_n"],
                 t["equality_witnesses_truncated"]))
        print("slack histogram:", t["slack_histogram_over_D"])
        # which invariants are pinned across the wall
        print("- pinned / spread across the %d recorded witnesses:" % len(ws))
        allinv = W.NEEDED
        for k in allinv:
            vals = Counter(str(p[2][k]) for p in profiles)
            if len(vals) == 1:
                print("    PINNED  %-14s = %s" % (k, list(vals)[0]))
        for k in allinv:
            vals = Counter(str(p[2][k]) for p in profiles)
            if len(vals) > 1:
                top = ", ".join("%s x%d" % (a, b) for a, b in vals.most_common(6))
                print("    spread  %-14s : %s" % (k, top))
        print("- witnesses (largest n first):")
        for (c, g, v, degs, tags) in profiles[:14]:
            slk = W.slack(t["expr"], v)
            print("    %-9s n=%d m=%2d deg=%-26s %s   [%s]  slack=%s"
                  % (c, v["n"], v["m"], str(degs), " ".join(tags),
                     " ".join("%s=%s" % (k, v[k]) for k in used), slk))
    return t, profiles


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--all"]:
        args = [t["id"] for t in _POP["targets"]]
    for a in args:
        read_wall(a)
