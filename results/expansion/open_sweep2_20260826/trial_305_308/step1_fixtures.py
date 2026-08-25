#!/usr/bin/env python3
"""STEP 1 — semantic microfixtures, hand-frozen expected values (both engines)."""
import sys, time
sys.path.insert(0, "/Users/kuber.mehta/Personal-Projects/c5-k4/results/expansion/open_sweep2_20260826/trial_305_308")
from fractions import Fraction
import networkx as nx
from trial_common import *

def fixture(name, g, exp):
    t0 = time.monotonic()
    row = evaluate(g, engines=("enum", "ilp"))
    dt = time.monotonic() - t0
    assert dt < 60.0, f"{name} exceeded cap"
    got = {
        "gamma_t": row["gamma_t"], "ilp": row["gamma_t_ilp"],
        "maxmin": row["maxmin"], "maxmax": row["maxmax"], "maxdet": row["maxdet"],
        "R305_B": row.get("R305_B"), "R308min_B": row.get("R308min_B"),
        "R308max_B": row.get("R308max_B"),
        "R305_C": row.get("R305_C"), "R305_A": row.get("R305_A"), "R305_D": row.get("R305_D"),
        "appB": row.get("applicable_B", False),
    }
    for key, val in exp.items():
        assert got[key] == val, (name, key, got[key], val)
    print(f"OK {name}: {got}  ({dt:.2f}s)")
    return row

# hand-frozen expectations (see TRIAL_LOG STEP 1 table)
fixture("K3", nx.complete_graph(3), dict(gamma_t=2, ilp=2, maxmin=1, maxmax=1,
    appB=False))  # complete: RDG-B undefined
fixture("C5", nx.cycle_graph(5), dict(gamma_t=3, ilp=2+1, maxmin=2, maxmax=2,
    R305_B=Fraction(0), R308min_B=Fraction(0), R308max_B=Fraction(0)))
fixture("Diamond", diamond(), dict(gamma_t=2, ilp=2, maxmin=1, maxmax=1,
    R305_B=Fraction(0), R308min_B=Fraction(-1,2), R308max_B=Fraction(-1,2)))
fixture("K1,3", nx.star_graph(3), dict(gamma_t=2, ilp=2, maxmin=1, maxmax=1,
    R305_B=Fraction(0), R308min_B=Fraction(0), R308max_B=Fraction(0)))
fixture("P4", nx.path_graph(4), dict(gamma_t=2, ilp=2, maxmin=2, maxmax=2,
    R305_B=Fraction(1), R308min_B=Fraction(1,2), R308max_B=Fraction(1,2)))
fixture("C5[K2]", c5_blowup([2]*5), dict(gamma_t=3, ilp=3, maxmin=2, maxmax=2,
    R305_B=Fraction(3), R308min_B=Fraction(2), R308max_B=Fraction(2)))
print("ALL FIXTURES PASS")
