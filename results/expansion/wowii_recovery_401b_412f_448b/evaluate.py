"""Driver: per-reading evaluation of 401b / 412f / 448b (published wording,
recovered identical from Wayback) on gate battery + arsenal.
Writes EVALUATION.md incrementally + results.json."""
import sys, json, time
from fractions import Fraction
from itertools import combinations
import networkx as nx

sys.path.insert(0, "/Users/kuber.mehta/Personal-Projects/c5-k4/results/expansion/wowii_recovery_401b_412f_448b")
from invariants import (dist_matrix, tdist, tdist_max, triangles_at, mu,
                        radius, gamma_2, alpha_2, critical_analysis,
                        arsenal, gate_battery, C5Km, all_independent_sets)

OUT = "/Users/kuber.mehta/Personal-Projects/c5-k4/results/expansion/wowii_recovery_401b_412f_448b"
md = open(f"{OUT}/EVALUATION.md", "w")
res = {"401b": {}, "412f": {}, "448b": {}}

def w(s=""):
    md.write(s + "\n"); md.flush()

def path_cover_bruteforce(G):
    """min number of vertex-disjoint paths covering V (general graph, small n).
    Exact backtracking over path decompositions."""
    V = list(G.nodes)
    n = len(V)
    adj = {v: set(G.neighbors(v)) for v in V}
    # lower bound: isolated vertices must be singleton paths
    def feasible(k):
        # can we cover V with <= k vertex-disjoint paths?
        used = set()
        # count vertices of degree 0 in G: each needs its own path
        iso = [v for v in V if not adj[v]]
        if len(iso) > k:
            return False
        remaining = set(V)
        def rec(remaining, paths_left):
            if not remaining:
                return True
            if paths_left == 0:
                return False
            start = min(remaining)
            # try all simple paths starting at 'start' (including singleton)
            def extend(path, visited):
                if rec(remaining - visited, paths_left - 1):
                    return True
                last = path[-1]
                for nxt in adj[last]:
                    if nxt in remaining and nxt not in visited:
                        if extend(path + [nxt], visited | {nxt}):
                            return True
                return False
            return extend([start], {start})
        return rec(remaining, k)
    for k in range(1, n+1):
        if feasible(k):
            return k
    return n

# ================================================================ 401b
w("# EVALUATION — recovered wordings 401b / 412f / 448b")
w()
w("Wording recovered from Wayback is IDENTICAL to the published corpus")
w("(see RECOVERY.md), so what follows evaluates *plausible readings* of the")
w("published statements. All arithmetic exact (integers / Fraction).")
w("Gate = DB-SANITY battery: connected atlas graphs n<=7, C5..C9, P7, Petersen,")
w("K3,3, K4,4, K5,5, K7, stars K_{1,n} (n=2..8). A reading failing any gate graph")
w("is a MIS-TRANSCRIPTION-class artifact and cannot be hunted.")
w()

w("## 401b — `gamma_2 <= FLOOR[3*Tdist_max / freq[T_max(v)]]` (open, Jan 2010)")
w()
w("- gamma_2: 2-domination number (def: every vertex in D or adjacent to >=2 in D).")
w("- Tdist_max: maximum transmission. T(v): triangles at v; T_max=max; freq=count.")
w()

def rhs_401b_tri(G):
    dm = dist_matrix(G)
    tdmax = max(tdist(G, v, dm) for v in G.nodes)
    T = triangles_at(G)
    tmax = max(T.values())
    freq = sum(1 for v in G.nodes if T[v] == tmax)
    val = Fraction(3 * tdmax, freq)
    return val.numerator // val.denominator, {"Tdist_max": tdmax, "T_max": tmax, "freq": freq}

def rhs_401b_tdistfreq(G):
    dm = dist_matrix(G)
    trans = {v: tdist(G, v, dm) for v in G.nodes}
    tdmax = max(trans.values())
    freq = sum(1 for v in G.nodes if trans[v] == tdmax)
    val = Fraction(3 * tdmax, freq)
    return val.numerator // val.denominator, {"Tdist_max": tdmax, "freq_of_Tdist_max": freq}

def run_reading_401b(name, rhsfn, graphs, label):
    fails, rows = [], []
    for gname, G in graphs.items():
        if G.number_of_nodes() <= 2:
            continue  # hypothesis n > 2
        g2 = gamma_2(G)
        rhs, info = rhsfn(G)
        ok = g2 <= rhs
        if not ok:
            fails.append((gname, g2, rhs, info))
        rows.append((gname, g2, rhs, ok))
    print(f"[401b/{name}] gate+arsenal done; violations={len(fails)}")
    return fails, rows

GATE = gate_battery()
ARS = arsenal()

t0 = time.time()
fails_tri, rows_tri = run_reading_401b("TRI", rhs_401b_tri, GATE, "gate")
res["401b"]["TRI_gate_violations"] = [
    {"graph": g, "gamma_2": a, "rhs": b, "info": i} for g, a, b, i in fails_tri]

w("### Reading R-TRI (literal page semantics: T(v)=#triangles at v; freq[T_max] = #vertices attaining it)")
w()
if fails_tri:
    w(f"**FAILS DB-SANITY GATE** on {len(fails_tri)} graph(s); first witnesses:")
    for g, a, b, i in fails_tri[:6]:
        w(f"- `{g}`: gamma_2={a} > floor(3*Tdist_max/freq)= {b}   [{i}]")
    w()
    w("Stars are inside Graffiti.pc's own database => under its own definitions this")
    w("reading cannot be what was tested. Verdict: **MIS-TRANSCRIPTION-CLASS**")
    w("(typo as published; e.g. plausibly intended freq of a distance quantity or an")
    w("inverted fraction) — NOT huntable. No reading of this shape survives.")
else:
    w("passes gate (unexpected)")
w()

fails_td, rows_td_gate = run_reading_401b("TD", rhs_401b_tdistfreq, GATE, "gate")
res["401b"]["TD_gate_violations"] = [
    {"graph": g, "gamma_2": a, "rhs": b, "info": i} for g, a, b, i in fails_td]
w("### Reading R-TD (repair hypothesis: `freq[T_max(v)]` re-read as frequency of the")
w("maximum TRANSMISSION value, i.e. #vertices attaining Tdist_max — motivated by")
w("sibling 401a using Tdist_max/disp_avg)")
w()
if fails_td:
    w(f"**FAILS DB-SANITY GATE** on {len(fails_td)} graph(s):")
    for g, a, b, i in fails_td[:10]:
        w(f"- `{g}`: gamma_2={a} > {b}   [{i}]")
    res["401b"]["TD_verdict"] = "MIS_TRANSCRIPTION_CLASS"
else:
    w("PASSES full DB-sanity gate (all connected atlas n<=7, cycles C5-C9, P7,")
    w("Petersen, K3,3/K4,4/K5,5, K7, stars, K3). Hunting on arsenal:")
    ars_fails, rows_td_ars = run_reading_401b("TD", rhs_401b_tdistfreq, {k: v[0] for k, v in ARS.items()}, "arsenal")
    res["401b"]["TD_arsenal_violations"] = [
        {"graph": g, "gamma_2": a, "rhs": b, "info": i} for g, a, b, i in ars_fails]
    if ars_fails:
        w("")
        w("**ARSENAL VIOLATIONS FOUND:**")
        for g, a, b, i in ars_fails:
            w(f"- `{g}`: gamma_2={a} > RHS={b}   [{i}]")
        res["401b"]["TD_verdict"] = "KILL_CANDIDATE_PENDING_RECOMPUTE"
        w("")
        w("Verdict: **KILL_CANDIDATE** pending independent recomputation (below).")
    else:
        tight = [r for r in rows_td_ars if r[1] == r[2]]
        w(f"Holds on entire arsenal ({len(rows_td_ars)} graphs; equality on "
          f"{len(tight)}: {[r[0] for r in tight][:8]}...). Verdict: **HOLD**.")
        res["401b"]["TD_verdict"] = "HOLD"
        res["401b"]["TD_arsenal_rows"] = [
            {"graph": g, "gamma_2": a, "rhs": b, "holds": ok} for g, a, b, ok in rows_td_ars]
w()

json.dump(res, open(f"{OUT}/results.json", "w"), indent=1, default=str)
print("phase1 done", time.time()-t0)
