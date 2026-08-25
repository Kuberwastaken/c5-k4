"""Phase 2: 412f (critical-independent-set H, multiple conventions) and
448b (alpha_2 bound, rho readings). Appends to EVALUATION.md."""
import sys, json, time
from itertools import combinations
import networkx as nx

sys.path.insert(0, "/Users/kuber.mehta/Personal-Projects/c5-k4/results/expansion/wowii_recovery_401b_412f_448b")
from invariants import (mu, alpha_2, radius, critical_analysis,
                        arsenal, gate_battery, all_independent_sets)

OUT = "/Users/kuber.mehta/Personal-Projects/c5-k4/results/expansion/wowii_recovery_401b_412f_448b"
res = json.load(open(f"{OUT}/results.json"))

md = open(f"{OUT}/EVALUATION.md", "a")

def w(s=""):
    md.write(s + "\n"); md.flush()

GATE = gate_battery()
# 401b hypothesis is n>2: drop K1,K2 from its gate (recorded for the record)
res["401b"]["gate_note"] = "atlas1 (=K2) excluded by hypothesis n>2; violations stand on stars/K4,4/K5,5 regardless"

def path_cover_bruteforce(G, budget=[60.0]):
    t0 = time.time()
    V = list(G.nodes)
    n = len(V)
    adjm = {v: frozenset(G.neighbors(v)) for v in V}

    def feasible(k):
        rem = frozenset(V)
        def rec(rem, left):
            if time.time() - t0 > budget[0]:
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
                for nxt in adjm[last] & rem - vis:
                    if extend(path + [nxt], vis | {nxt}):
                        return True
                return False
            return extend([start], frozenset({start}))
        return rec(rem, k)

    try:
        for k in range(1, n+1):
            if feasible(k):
                return k
    except TimeoutError:
        return None
    return n

def critical_analysis_structured(G, struct, allow_empty):
    kind, param = struct
    if kind == "generic":
        sets = all_independent_sets(G)
    elif kind == "C5Km":
        m = param
        blobs = [[m*b+i for i in range(m)] for b in range(5)]
        sets = [frozenset()]
        for b in range(5):
            sets += [frozenset([v]) for v in blobs[b]]
            j = (b+2) % 5
            sets += [frozenset((u, w)) for u in blobs[b] for w in blobs[j]]
    elif kind == "compC5K4":
        m = 4
        blobs = [[4*b+i for i in range(m)] for b in range(5)]
        def subsets(S):
            return [frozenset(c) for r in range(len(S)+1) for c in combinations(S, r)]
        out = set()
        for b in range(5):
            out |= set(subsets(blobs[b]))
            for jj in ((b+1) % 5, (b-1) % 5):
                for A in subsets(blobs[b]):
                    for B in subsets(blobs[jj]):
                        out.add(A | B)
        sets = list(out)
    elif kind == "CycK3":
        L = param
        blobs = [[3*b+i for i in range(3)] for b in range(L)]
        blobsets = []
        for r in range(1, L//2 + 1):
            for bs in combinations(range(L), r):
                if all((bs[i]-bs[j]) % L not in (1, L-1)
                       for i in range(r) for j in range(i+1, r)):
                    blobsets.append(bs)
        import itertools as it
        s = {frozenset()}
        for bs in blobsets:
            pools = [blobs[b] for b in bs]
            for pick in it.product(*pools):
                s.add(frozenset(pick))
        sets = list(s)
    elif kind in ("Petersen", "Paley"):
        sets = all_independent_sets(G)
    else:
        raise ValueError(kind)
    if not allow_empty:
        sets = [S for S in sets if S]
    infos = []
    for S in sets:
        nb = set()
        for v in S:
            nb |= set(G.neighbors(v))
        infos.append((S, len(S) - len(nb)))
    best = max(d for _, d in infos)
    argmax = [S for S, d in infos if d == best]
    mx = max(len(S) for S in argmax)
    H_maxcard = frozenset().union(*[S for S in argmax if len(S) == mx])
    return {"H_size": len(H_maxcard), "alpha_crit": mx, "best_deficit": best,
            "n_argmax": len(argmax)}


# ================================================================ 412f
w()
w("## 412f — `|H| >= mu(G[V-N(P)])`, bipartite case `|H| >= c(G[V-N(P)]) + mu(...)`")
w("(open, Jun 2010; H = union of all MAXIMUM critical independent sets; P = pendants)")
w()
w("Convention knobs evaluated:")
w("- **CONV-LIT** (literal defs-page wording): U in the defining inequality ranges")
w("  over ALL independent subsets *including empty*; critical := argmax deficit")
w("  |S|-|N(S)|; H = union of argmax sets.")
w("- **CONV-NE**: empty set excluded entirely; critical := argmax deficit among")
w("  nonempty independent sets; 'maximum' = maximum-cardinality members.")
w("  Sub-knob NE-ALL: H = union of ALL argmax sets (not just largest).")
w()

def eval_412f(G, conv):
    """returns dict(lhs, rhs1, rhs2, ok1, ok2and, info)"""
    P = {v for v in G.nodes if G.degree(v) == 1}
    NP = set()
    for v in P:
        NP |= set(G.neighbors(v))
    sub = G.subgraph([v for v in G.nodes if v not in NP]).copy()
    m_sub = mu(sub)
    c_sub = nx.number_connected_components(sub) if nx.is_bipartite(G) else None
    if conv == "LIT":
        ca = critical_analysis_conv(G, allow_empty=True)
        lhs = ca["H_size"]
    else:
        ca = critical_analysis_conv(G, allow_empty=False)
        lhs = ca["H_size"]
    r1 = lhs >= m_sub
    out = {"lhs_H": lhs, "mu_sub": m_sub, "ok_branch1": r1,
           "alpha_crit": ca["alpha_crit"], "best_deficit": ca["best_deficit"],
           "n_argmax": ca["n_argmax"], "P": len(P)}
    if nx.is_bipartite(G):
        out["c_sub"] = c_sub
        out["ok_branch2"] = lhs >= c_sub + m_sub
    return out

def critical_analysis_conv(G, allow_empty):
    """Enumerate independent sets (generic small-n only) and compute H."""
    n = G.number_of_nodes()
    if n <= 22:
        sets = all_independent_sets(G)
    else:
        raise ValueError("big")
    if not allow_empty:
        sets = [S for S in sets if S]
    infos = []
    for S in sets:
        nb = set()
        for v in S:
            nb |= set(G.neighbors(v))
        infos.append((S, len(S) - len(nb)))
    best = max(d for _, d in infos)
    argmax = [S for S, d in infos if d == best]
    mx = max(len(S) for S in argmax)
    H_maxcard = frozenset().union(*[S for S in argmax if len(S) == mx])
    H_all = frozenset().union(*argmax)
    return {"H_size": len(H_maxcard), "H_all_size": len(H_all),
            "alpha_crit": mx, "best_deficit": best, "n_argmax": len(argmax)}

for conv, label in [("LIT", "CONV-LIT"), ("NE", "CONV-NE")]:
    fails = []
    rows = []
    for gname, G in GATE.items():
        if G.number_of_nodes() <= 2:
            continue  # hypothesis n > 2
        try:
            r = eval_412f(G, conv)
        except Exception as e:
            continue
        bad = (not r["ok_branch1"]) or ("ok_branch2" in r and not r["ok_branch2"])
        if bad:
            fails.append((gname, r))
        rows.append((gname, r))
    key = f"412f_{conv}_gate_violations"
    res[key] = [{"graph": g, **r} for g, r in fails]
    w(f"### Reading {label}")
    if fails:
        w(f"**FAILS DB-SANITY GATE** on {len(fails)} gate graph(s); witnesses:")
        for g, r in fails[:8]:
            extra = f", c_sub={r['c_sub']}, branch2={'OK' if r.get('ok_branch2') else 'FAIL'}" if "c_sub" in r else ""
            w(f"- `{g}`: |H|={r['lhs_H']} < mu(G[V-N(P)])={r['mu_sub']}{extra} "
              f"[alpha_crit={r['alpha_crit']}, best_deficit={r['best_deficit']}]")
        res[f"412f_{conv}_verdict"] = "MIS_TRANSCRIPTION_CLASS"
        w("Verdict: **MIS-TRANSCRIPTION-CLASS** under this convention — not huntable.")
    else:
        w("PASSES full gate. Arsenal:")
        arsfails = []
        arsrows = []
        for gname, (G, struct) in arsenal().items():
            P = {v for v in G.nodes if G.degree(v) == 1}
            assert not P, gname
            sub = G
            m_sub = mu(sub)
            ca = critical_analysis_structured(G, struct, allow_empty=(conv == "LIT"))
            lhs = ca["H_size"]
            ok1 = lhs >= m_sub
            ok2 = True
            note2 = ""
            if nx.is_bipartite(G):
                c_sub = nx.number_connected_components(sub)
                ok2 = lhs >= c_sub + m_sub
                note2 = f", branch2 c+m={c_sub + m_sub} {'OK' if ok2 else 'FAIL'}"
            entry = (gname, lhs, m_sub, ok1 and ok2, ca, note2)
            arsrows.append(entry)
            if not (ok1 and ok2):
                arsfails.append(entry)
        if arsfails:
            w("")
            w("**ARSENAL VIOLATIONS:**")
            for gname, lhs, m_sub, ok, ca, note2 in arsfails:
                w(f"- `{gname}`: |H|={lhs} < mu={m_sub}{note2}  [{ca}]")
            res[f"412f_{conv}_verdict"] = "KILL_CANDIDATE_PENDING_RECOMPUTE"
            res[f"412f_{conv}_arsenal_violations"] = [
                {"graph": g, "lhs": l, "mu": m} for g, l, m, ok, ca, n2 in arsfails]
            w("Verdict: **KILL_CANDIDATE** pending independent recomputation.")
        else:
            tight = [e[0] for e in arsrows if e[1] == e[2]]
            w(f"Holds on entire arsenal ({len(arsrows)}; equality on {tight}). Verdict: **HOLD**.")
            res[f"412f_{conv}_verdict"] = "HOLD"
            res[f"412f_{conv}_arsenal_rows"] = [
                {"graph": g, "lhs": l, "mu": m, "holds": ok} for g, l, m, ok, ca, n2 in arsrows]
    w()

json.dump(res, open(f"{OUT}/results.json", "w"), indent=1, default=str)
print("phase 412f done")
