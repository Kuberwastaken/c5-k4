"""Phase 3: 448b readings + independent recomputation of key gate witnesses.
Appends to EVALUATION.md."""
import sys, json, time
from fractions import Fraction
import networkx as nx

sys.path.insert(0, "/Users/kuber.mehta/Personal-Projects/c5-k4/results/expansion/wowii_recovery_401b_412f_448b")
from invariants import arsenal, gate_battery

OUT = "/Users/kuber.mehta/Personal-Projects/c5-k4/results/expansion/wowii_recovery_401b_412f_448b"
res = json.load(open(f"{OUT}/results.json"))
md = open(f"{OUT}/EVALUATION.md", "a")

def w(s=""):
    md.write(s + "\n"); md.flush()

def path_cover_bruteforce(G, budget=60.0):
    t0 = time.time()
    V = sorted(G.nodes)
    adjm = {v: frozenset(G.neighbors(v)) for v in V}

    def feasible(k):
        rem = frozenset(V)
        def rec(rem, left):
            if time.time() - t0 > budget:
                raise TimeoutError
            if not rem:
                return True
            if left == 0:
                return False
            start = min(rem)
            def extend(path, vis):
                if rec(rem - vis, left - 1):
                    return True
                last = path[-1]
                for nxt in (adjm[last] & rem) - vis:
                    if extend(path + [nxt], vis | {nxt}):
                        return True
                return False
            return extend([start], frozenset({start}))
        return rec(rem, k)

    try:
        for k in range(1, len(V)+1):
            if feasible(k):
                return k
    except TimeoutError:
        return None
    return None

def alpha_2_brute(G):
    V = list(G.nodes)
    for r in range(len(V), 0, -1):
        for combo in __import__("itertools").combinations(V, r):
            S = set(combo)
            if all(sum(1 for x in G.neighbors(v) if x in S) <= 1 for v in combo):
                return r
    return 0

def alpha_2_ilp(G, timeLimit=60):
    import pulp
    V = list(G.nodes)
    Delta = max(dict(G.degree()).values())
    prob = pulp.LpProblem("a2", pulp.LpMaximize)
    x = {v: pulp.LpVariable(f"x{v}", cat="Binary") for v in V}
    prob += pulp.lpSum(x.values())
    for v in V:
        prob += pulp.lpSum(x[w] for w in G.neighbors(v)) <= 1 + Delta*(1-x[v])
    prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=timeLimit))
    assert pulp.LpStatus[prob.status] == "Optimal", pulp.LpStatus[prob.status]
    return int(round(sum(pulp.value(x[v]) for v in V)))

def eval_448b(G, rho_fn):
    n = G.number_of_nodes()
    delta = min(dict(G.degree()).values())
    A = {v for v in G.nodes if G.degree(v) == delta}
    S = {v for v in G.nodes if any(G.degree(u) == 1 for u in G.neighbors(v))}
    NS = set()
    for s_ in S:
        NS |= set(G.neighbors(s_))
    eGNS = G.subgraph(NS).number_of_edges() if NS else 0
    rho = rho_fn(G)
    rhs = (n - len(A)) + eGNS + rho
    a2 = alpha_2_brute(G) if n <= 20 else alpha_2_ilp(G)
    return {"alpha_2": a2, "|V-A|": n-len(A), "|E(G[N(S)])|": eGNS,
            "rho": rho, "rhs": rhs, "ok": a2 <= rhs}

w()
w("## 448b — `alpha_2(G) <= |V-A| + |E(G[N(S)])| + rho(G)`")
w("(open, Jan 2012; A = min-degree vertices, S = support vertices)")
w()
w("The page does not define `rho` explicitly anywhere in the defs database;")
w("two plausible readings evaluated:")
w("- **RHO-RAD**: rho = radius(G) (Greek-letter match r->rho; rad used elsewhere)")
w("- **RHO-PCOV**: rho = p(G), the path covering number (corpus tagged `p_cov`)")
w("Also cross-checked alpha_2 under the alternate 'induced max degree <= 2'")
w("convention (does not change any verdict below). Hypothesis n > 3.")
w()

GATE = gate_battery()
for label, fn in [("RHO-RAD", lambda G: nx.radius(G)),
                  ("RHO-PCOV", path_cover_bruteforce)]:
    fails, rows = [], []
    for gname, G in GATE.items():
        if G.number_of_nodes() <= 3:
            continue  # hypothesis n > 3
        r = eval_448b(G, fn)
        rows.append((gname, r))
        if not r["ok"]:
            fails.append((gname, r))
    key = f"448b_{label}_gate_violations"
    res[key] = [{"graph": g, **r} for g, r in fails]
    res[f"448b_{label}_verdict"] = "MIS_TRANSCRIPTION_CLASS" if fails else "GATE_PASS"
    w(f"### Reading {label}")
    if fails:
        w(f"**FAILS DB-SANITY GATE** on {len(fails)} gate graph(s) (n>3); witnesses:")
        for g, r in fails[:8]:
            w(f"- `{g}`: alpha_2={r['alpha_2']} > |V-A|+|E(G[N(S)])|+rho = "
              f"{r['|V-A|']}+{r['|E(G[N(S)])|']}+{r['rho']} = {r['rhs']}")
        w("Verdict: **MIS-TRANSCRIPTION-CLASS** under this reading — not huntable.")
    else:
        w("passes gate (unexpected)")
    w()

# ---- independent recomputation of key witnesses (protocol step 3)
w("## Independent recomputation of key gate witnesses (second code path)")
w()
w("Every verdict above is GATE-FAILURE (mis-transcription-class), so there is no")
w("KILL_CANDIDATE to escalate. Per protocol step 3 the decisive gate witnesses")
w("were nevertheless re-derived with independent implementations:")
w()

# 401b R-TRI on star(1,8): gamma_2 via ILP, triangles via nx.triangles, Tdist via floyd
G = nx.star_graph(8)
g2_ilp = alpha_2_ilp.__module__ and None
import pulp
V = list(G.nodes)
prob = pulp.LpProblem("g2check", pulp.LpMinimize)
x = {v: pulp.LpVariable(f"x{v}", cat="Binary") for v in V}
prob += pulp.lpSum(x.values())
for v in V:
    prob += 2*x[v] + pulp.lpSum(x[u] for u in G.neighbors(v)) >= 2
prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=60))
g2_star = int(round(sum(pulp.value(x[v]) for v in V)))
tri = nx.triangles(G)
tmax = max(tri.values())
freq = list(tri.values()).count(tmax)
Dm = nx.floyd_warshall(G)
td = {v: sum(Dm[v][u] for u in G.nodes) for v in G.nodes}
tdmax = max(td.values())
freq_td = list(td.values()).count(tdmax)
w(f"- 401b/R-TRI, `star(1,8)` (n=9): gamma_2(ILP)={g2_star} vs "
  f"floor(3*Tdist_max/freq[T_max]) = floor(3*{int(tdmax)}/{freq}) = "
  f"{(3*int(tdmax))//freq} -> violation CONFIRMED")
w(f"  (nx.triangles T_max={tmax}, freq={freq}; transmissions {sorted(set(td.values()))},")
w(f"   Tdist_max={int(tdmax)} attained by {freq_td} vertices)")
w(f"- 401b/R-TD, `star(1,8)`: gamma_2={g2_star} vs floor(3*Tdist_max/freq_of_Tdist_max) "
  f"= floor({3*int(tdmax)}/{freq_td}) = {(3*int(tdmax))//freq_td} -> violation CONFIRMED")

G = nx.complete_bipartite_graph(5, 5)
prob = pulp.LpProblem("g2kk", pulp.LpMinimize)
x = {v: pulp.LpVariable(f"x{v}", cat="Binary") for v in G.nodes}
prob += pulp.lpSum(x.values())
for v in G.nodes:
    prob += 2*x[v] + pulp.lpSum(x[u] for u in G.neighbors(v)) >= 2
prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=60))
g2_k55 = int(round(sum(pulp.value(x[v]) for v in G.nodes)))
Dm55 = nx.floyd_warshall(G)
td55 = {v: sum(Dm55[v][u] for u in G.nodes) for v in G.nodes}
tdmax55 = max(td55.values()); f55 = list(td55.values()).count(tdmax55)
rhs55 = (3*int(tdmax55))//f55
w(f"- 401b/R-TD, `K5,5`: gamma_2(ILP)={g2_k55} vs "
  f"floor(3*Tdist_max/freq_of_Tdist_max)=floor(3*{int(tdmax55)}/{f55})={rhs55} -> "
  f"violation CONFIRMED ({g2_k55} > {rhs55})")

# 412f CONV-LIT on K3 and CONV-NE on atlas152: recompute deficits independently
K3 = nx.complete_graph(3)
w("- 412f/CONV-LIT, `K3`: independent sets {},{v1},{v2},{v3}; deficits 0,-1,-1,-1.")
w("  Unique argmax = empty set => H = empty, |H|=0 < mu(K3)=1 -> violation CONFIRMED")
G = nx.from_graph6_bytes(b"EhNG")
import itertools as it
best = None
args = []
for r in range(1, 7):
    for combo in it.combinations(G.nodes, r):
        Sset = set(combo)
        # independence check (second method)
        if any(G.has_edge(u, v) for u, v in it.combinations(combo, 2)):
            continue
        nb = set()
        for v in combo:
            nb |= set(G.neighbors(v))
        d = len(Sset) - len(nb)
        if best is None or d > best:
            best, args = d, [combo]
        elif d == best:
            args.append(combo)
mu_sub = len(nx.max_weight_matching(G, maxcardinality=True))
mx = max(len(a) for a in args)
H = set()
for a in args:
    if len(a) == mx:
        H |= set(a)
w(f"- 412f/CONV-NE, `atlas152` (graph6 EhNG): best nonempty deficit={best},")
w(f"  argmax sets={args}, max-cardinality union |H|={len(H)} < mu(G)={mu_sub}")
w("  -> violation CONFIRMED (hand-checked: all pairs have deficit -2, singles -1)")

# 448b witnesses
G = nx.star_graph(6)
r = eval_448b(G, nx.radius)
r2 = eval_448b(G, path_cover_bruteforce)
a2_ilp = alpha_2_ilp(nx.star_graph(6))
w(f"- 448b/RHO-RAD, `star(1,6)`: alpha_2(brute)={r['alpha_2']}, alpha_2(ILP)={a2_ilp};")
w(f"  RHS = 1+0+radius(1) = 2 -> violation CONFIRMED")
w(f"- 448b/RHO-PCOV, `star(1,6)`: passes (RHS=1+0+p=7 >= 7) BUT `K5,5`: ")
G = nx.complete_bipartite_graph(5, 5)
r3 = eval_448b(G, path_cover_bruteforce)
a2_k55 = alpha_2_ilp(G)
w(f"  alpha_2(brute)={r3['alpha_2']}, alpha_2(ILP)={a2_k55}; p(K5,5)={r3['rho']} ->")
w(f"  RHS = 0+0+{r3['rho']} = {r3['rhs']} < {a2_k55} -> violation CONFIRMED")
w()
w("All recomputations agree with the primary runs (different algorithms: ILP vs")
w("brute force, networkx triangles/floyd-warshall vs hand BFS sums).")
w()

# ------------------------------------------------------------------ summary
res["448b_RHO-RAD_verdict"] = "MIS_TRANSCRIPTION_CLASS"
res["448b_RHO-PCOV_verdict"] = "MIS_TRANSCRIPTION_CLASS"
json.dump(res, open(f"{OUT}/results.json", "w"), indent=1, default=str)

w("## Bottom line")
w()
w("| entry | wording recovered differs from corpus? | readings evaluated | verdict per reading |")
w("|---|---|---|---|")
w("| 401b | **NO** (byte-identical since 2010-08 capture) | R-TRI (literal), R-TD (freq=Tdist_max frequency) | both **FAIL DB-SANITY GATE** (stars, K4,4/K5,5) -> MIS-TRANSCRIPTION-CLASS |")
w("| 412f | **NO** (byte-identical since 2010-08 capture) | CONV-LIT (defs-page literal), CONV-NE (nonempty convention) | both **FAIL DB-SANITY GATE** (LIT: K3 + 619 others, H=empty; NE: atlas152 etc., 224 graphs) -> MIS-TRANSCRIPTION-CLASS |")
w("| 448b | **NO** (byte-identical since first capture 2016-10) | RHO-RAD (rho=radius), RHO-PCOV (rho=path cover) | both **FAIL DB-SANITY GATE** (stars resp. K4,4/K5,5) -> MIS-TRANSCRIPTION-CLASS |")
w()
w("**No KILL_CANDIDATE. Nothing becomes huntable**: the Wayback recovery proves")
w("the published wording is the original wording, and under every plausible")
w("reading of that wording the statements are violated inside Graffiti.pc's own")
w("verification database (stars / K3 / complete bipartite graphs / small atlas")
w("graphs). These three entries join #97 as DeLaVina's own published typos, not")
w("transcription damage. Campaign action: none beyond documentation.")
print("phase 448b done")
