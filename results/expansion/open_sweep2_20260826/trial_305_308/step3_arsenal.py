#!/usr/bin/env python3
"""STEP 3 — tightness map on the 13-graph campaign arsenal (+T(7..9) analytic
arsenal) for the sole gate-surviving entry/reading: WOWII 305 / RDG-B.
Two engines per member where feasible inside caps; brackets otherwise."""
import sys, json, time, signal
sys.path.insert(0, "/Users/kuber.mehta/Personal-Projects/c5-k4/results/expansion/open_sweep2_20260826/trial_305_308")
from fractions import Fraction
import networkx as nx
from trial_common import *

class Timeout(Exception): pass
def _alarm(s, f): raise Timeout()
signal.signal(signal.SIGALRM, _alarm)

def g6(g): return nx.to_graph6_bytes(g, header=False).decode().strip()

def arsenal():
    A = {}
    for m in range(2, 9): A[f"C5[K{m}]"] = c5_blowup([m]*5)
    for k in (2, 3, 4):   A[f"C7[K{k}]"] = c5_blowup([k]*7)
    A["C9[K3]"] = c5_blowup([3]*9)
    A["B(4,4,3,4,3)"] = c5_blowup([4,4,3,4,3])
    A["B(4,2,4,2,4)"] = c5_blowup([4,2,4,2,4])
    A["B(4,1,4,1,4)"] = c5_blowup([4,1,4,1,4])
    A["comp(C5[K4])"] = nx.complement(c5_blowup([4]*5))
    for t in (7, 8, 9):   A[f"T({t})"] = line_T(t)
    return A

rows = []
t0 = time.monotonic()
for name, g in arsenal().items():
    assert nx.is_connected(g) and g.number_of_nodes() > 2
    row = {"member": name, "n": g.number_of_nodes(), "graph6_sha_note": len(g6(g))}
    # engine A under its own cap
    try:
        signal.setitimer(signal.ITIMER_REAL, 30)
        ta = time.monotonic()
        gtA, wit = gamma_t_enum(g)
        signal.setitimer(signal.ITIMER_REAL, 0)
        row.update(gamma_t_A=gtA, witness=sorted(wit),
                   engine_A_seconds=round(time.monotonic()-ta, 2))
    except Timeout:
        signal.setitimer(signal.ITIMER_REAL, 0)
        row.update(gamma_t_A=None, engine_A="BRACKET>30s")
    # engine B always (CBC time-limited)
    tb = time.monotonic()
    gtB, witB, st = gamma_t_ilp(g, time_limit=55)
    row.update(gamma_t_B=gtB, ilp_status=st,
               engine_B_seconds=round(time.monotonic()-tb, 2))
    row["engines_agree"] = (row.get("gamma_t_A") == gtB)
    gt_certified = gtB if st == "Optimal" else None
    row["gamma_t"] = gt_certified
    rdgs = nbar_readings(g)
    mxset = maxine_reachable(g)
    row["maxmin"], row["maxmax"] = min(mxset), max(mxset)
    for r, vals in rdgs.items():
        if not vals:
            continue
        row[f"max_{r}"] = max(vals); row[f"min_{r}"] = min(vals)
        row[f"R305_{r}"] = (residual_305(vals, gt_certified)
                            if gt_certified is not None else "INCOMPLETE")
    rows.append(row)
    print(f"{name:16s} n={row['n']:3d} gamma_t(A={row.get('gamma_t_A')},"
          f"B={gtB},{st}) agree={row['engines_agree']} "
          f"RDG-B: max={row.get('max_B')} R={row.get('R305_B')}")

with open("/Users/kuber.mehta/Personal-Projects/c5-k4/results/expansion/open_sweep2_20260826/trial_305_308/arsenal_rows.json", "w") as f:
    json.dump(rows, f, indent=1, default=str)
print(f"total {time.monotonic()-t0:.1f}s")
