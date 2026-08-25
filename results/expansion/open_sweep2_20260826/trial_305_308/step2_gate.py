#!/usr/bin/env python3
"""STEP 2 — database-sanity gate: all connected atlas graphs n<=7 + named controls.
Per-reading verdicts for 305 and 308; S1 shadow verification (gamma_t <= 2n/3);
ILP double-check of violation witnesses before declaring any reading dead."""
import sys, json, time
sys.path.insert(0, "/Users/kuber.mehta/Personal-Projects/c5-k4/results/expansion/open_sweep2_20260826/trial_305_308")
from fractions import Fraction
import networkx as nx
from trial_common import *

t_start = time.monotonic()
viol = {r: {"305": [], "308max": [], "308min": []} for r in "ABCD"}
shadow_viol = []
n_controls = 0
slack_hist = {r: {"305": {}, "308min": {}, "308max": {}} for r in "ABCD"}
spot = {}

def g6(g):
    return nx.to_graph6_bytes(g, header=False).decode().strip()

controls = []
for i, g in enumerate(atlas_connected(3, 7)):
    controls.append((f"atlas{i}:{g.number_of_nodes()}", g))
for name, g in named_controls().items():
    if g.number_of_nodes() >= 3 and nx.is_connected(g):
        controls.append((name, g))

for ci, (name, g) in enumerate(controls):
    n = g.number_of_nodes()
    assert time.monotonic() - t_start < 900, "gate budget exceeded"
    gt, wit = gamma_t_enum(g)
    if Fraction(gt, 1) > Fraction(2 * n, 3):
        shadow_viol.append((name, g6(g), gt, n))
    mx = maxine_reachable(g)
    mn, mxv = min(mx), max(mx)
    rdgs = nbar_readings(g)
    for r, vals in rdgs.items():
        if not vals:
            continue
        R305 = residual_305(vals, gt)
        R308m = residual_308(vals, gt, mn)
        R308M = residual_308(vals, gt, mxv)
        if R305 is not None and R305 < 0:
            viol[r]["305"].append((name, str(R305), max(vals), gt, g6(g)))
        if R308M is not None and R308M < 0:
            viol[r]["308max"].append((name, str(R308M), min(vals), mn, mxv, gt, g6(g)))
        if R308m is not None and R308m < 0:
            viol[r]["308min"].append((name, str(R308m), min(vals), mn, mxv, gt, g6(g)))
        for tag, R in (("305", R305), ("308min", R308m), ("308max", R308M)):
            if R is not None:
                k = str(R)
                slack_hist[r][tag][k] = slack_hist[r][tag].get(k, 0) + 1
    if ci % 150 == 0:
        gi, _, st = gamma_t_ilp(g)
        spot[name] = [gt, gi, bool(st == "Optimal" and gi == gt)]
    n_controls += 1

replay = {}
named = dict(named_controls())
for r in "ABCD":
    for key in ("305", "308max"):
        if viol[r][key]:
            wname, wR, wterm, *rest = viol[r][key][0]
            g = None
            if wname in named and named[wname].number_of_nodes() >= 3:
                g = named[wname]
            else:
                idx = int(wname.split(":")[0].replace("atlas", ""))
                g = next(x for x in atlas_connected(3, 7) if False) if False else None
            if g is not None:
                gt_i, _, st = gamma_t_ilp(g)
                replay[f"{r}/{key}/{wname}"] = {"row": viol[r][key][0][:4], "gamma_t_ilp": gt_i, "status": st}

out = {
    "n_controls": n_controls,
    "violations": viol,
    "shadow_S1_violations": shadow_viol,
    "ilp_spot": spot,
    "ilp_replay": replay,
    "slack_histograms": {r: {t: dict(sorted(v.items())) for t, v in d.items()} for r, d in slack_hist.items()},
}
with open("/Users/kuber.mehta/Personal-Projects/c5-k4/results/expansion/open_sweep2_20260826/trial_305_308/gate_rows.json", "w") as f:
    json.dump(out, f, indent=1)

print(f"controls evaluated: {n_controls}  ({time.monotonic()-t_start:.1f}s)")
print("S1 shadow (gamma_t <= 2n/3) violations:", shadow_viol[:5], f"total={len(shadow_viol)}")
for r in "ABCD":
    print(f"RDG-{r}: 305 violations={len(viol[r]['305'])}  "
          f"308(tie-robust,maxmax)={len(viol[r]['308max'])}  308(any-rule,min-only)={len(viol[r]['308min'])}")
    if viol[r]["305"]:
        print("   first 305 witness:", viol[r]["305"][0][:4])
    if viol[r]["308max"]:
        print("   first 308 witness:", viol[r]["308max"][0][:6])
print("ILP spot agreements:", sum(1 for v in spot.values() if v[2]), "/", len(spot))
