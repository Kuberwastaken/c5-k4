#!/usr/bin/env python3
"""STEP 4 — frozen families F1-F4 + F6 for 305/RDG-B (sole surviving entry/reading).
F1 unequal C5-blow-ups w_i in {1,2,3}^5 (243 members, closed-form prediction)
F2 T(k)=L(K_k) k in {5,6} (7..9 already scored in STEP 3)
F3 cocktail party CP(k) k in {2..7}
F4 complete multipartite (10 frozen part vectors)
F6 subdivided-C5 control arm l in {1,2,3}
Engine A on every member; ILP spot-agreement sample; 60s cap per member."""
import sys, json, time, itertools
sys.path.insert(0, "/Users/kuber.mehta/Personal-Projects/c5-k4/results/expansion/open_sweep2_20260826/trial_305_308")
from fractions import Fraction
from math import ceil
import networkx as nx
from trial_common import *

t0 = time.monotonic()
rows = {"F1": [], "F2": [], "F3": [], "F4": [], "F6": []}
violations = []

def score(family, name, g, closed_form=None):
    assert time.monotonic() - t0 < 600, "arm budget exceeded"
    gtA, wit = gamma_t_enum(g)
    vals = nbar_readings(g)["B"]
    R = residual_305(vals, gtA)
    row = {"member": name, "n": g.number_of_nodes(), "gamma_t_A": gtA,
           "max_B": max(vals), "min_B": min(vals), "R_B": str(R)}
    if closed_form is not None:
        row["closed_form"] = str(closed_form)
        assert R == closed_form, (name, R, closed_form)
    if R < 0:
        violations.append((family, name, str(R), nx.to_graph6_bytes(g, header=False).decode().strip()))
    rows[family].append(row)
    return R

# F1: all 243 weight vectors; gamma_t must be 3; closed form ceil(2/3*(n-w_min))-3
f1_R = []
for w in itertools.product((1, 2, 3), repeat=5):
    g = c5_blowup(list(w))
    n = g.number_of_nodes()
    cf = Fraction(ceil(Fraction(2, 3) * Fraction(n - min(w), 1)) - 3, 1)
    R = score("F1", f"B{list(w)}", g, cf)
    f1_R.append(R)
# ILP spot agreement: every 25th member alphabetically stable order
spot_ok = 0
for i, w in enumerate(itertools.product((1, 2, 3), repeat=5)):
    if i % 25 == 0:
        gi, _, st = gamma_t_ilp(c5_blowup(list(w)))
        assert st == "Optimal" and gi == 3, (w, gi, st)
        spot_ok += 1
print(f"F1: 243 members, closed-form EXACT match on all, ILP spot {spot_ok}/10 agree, "
      f"R range {min(f1_R)}..{max(f1_R)}")

# F2: T(5), T(6)
for k in (5, 6):
    score("F2", f"T({k})", line_T(k))
print("F2:", rows["F2"])

# F3: CP(k) k=2..7 — predicted equality wall R=0 throughout
for k in range(2, 8):
    R = score("F3", f"CP({k})", cocktail_party(k),
              Fraction(0) )  # placeholder replaced below
    # real check below
rows["F3"] = []
for k in range(2, 8):
    g = cocktail_party(k)
    gtA, _ = gamma_t_enum(g)
    vals = nbar_readings(g)["B"]
    R = residual_305(vals, gtA)
    rows["F3"].append({"member": f"CP({k})", "n": g.number_of_nodes(),
                       "gamma_t_A": gtA, "max_B": max(vals), "R_B": str(R)})
    print(f"F3 CP({k}): n={g.number_of_nodes()} gamma_t={gtA} M={max(vals)} R={R}")

# F4: complete multipartite
parts_list = [(2,1,1),(2,2,1),(3,1,1),(2,2,2),(3,2,1),(3,3,1),(4,2,1),(3,3,2),(4,3,1),(5,2,1)]
for p in parts_list:
    g = nx.complete_multipartite_graph(*p)
    gtA, _ = gamma_t_enum(g)
    vals = nbar_readings(g)["B"]
    R = residual_305(vals, gtA)
    rows["F4"].append({"member": f"K({','.join(map(str,p))})",
                       "n": g.number_of_nodes(), "gamma_t_A": gtA,
                       "max_B": max(vals), "R_B": str(R)})
    print(f"F4 K{p}: n={g.number_of_nodes()} gamma_t={gtA} M={max(vals)} R={R}")

# F6: subdivided C5 control arm (=C5, C6, C7 by construction)
for extra in (0, 1, 2):
    g = subdivided_c5(extra)
    gtA, _ = gamma_t_enum(g)
    vals = nbar_readings(g)["B"]
    R = residual_305(vals, gtA)
    rows["F6"].append({"member": f"D_l{extra+1}", "n": g.number_of_nodes(),
                       "gamma_t_A": gtA, "max_B": max(vals), "R_B": str(R)})
    print(f"F6 l={extra+1}: n={g.number_of_nodes()} gamma_t={gtA} M={max(vals)} R={R}")

with open("/Users/kuber.mehta/Personal-Projects/c5-k4/results/expansion/open_sweep2_20260826/trial_305_308/family_rows.json", "w") as f:
    json.dump(rows, f, indent=1)
print("violations so far:", violations)
print(f"total {time.monotonic()-t0:.1f}s")
