#!/usr/bin/env python3
"""WOWII 255 + 256 prospective wall-navigation trials (open_sweep2_20260826).

Protocol: TRIAL_CONTRACT_255.md / TRIAL_CONTRACT_256.md (frozen before any
development-family evaluation). Exact arithmetic (fractions.Fraction).
Engines: A = pulp/CBC ILP; B = pure-python branch-and-bound (independent code).
Usage: trial_255_256.py [fixtures|gate|arsenal|family|all]
"""
import json
import sys
import time
from fractions import Fraction
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
CAP_S = 60.0


# ---------------------------------------------------------------- coordinates
def maxN_incl_A(g):
    """RD-A: max over edges {u,v} of |open union N(u)|U|N(v)| (contains u,v)."""
    best = 0
    for u, v in g.edges():
        s = set(g[u])
        s.update(g[v])
        if len(s) > best:
            best = len(s)
    return best


def maxN_incl_B(g):
    """Independent path: closed neighborhoods; closed-union == open-union."""
    cn = {v: frozenset(g.adj[v]) | {v} for v in g.nodes()}
    best = 0
    for u, v in g.edges():
        val = len(cn[u] | cn[v])
        if val > best:
            best = val
    return best


def maxN_excl_A(g):
    """RD-B compute-hint variant: |(N(u) U N(v)) \\ {u,v}| maximized."""
    best = 0
    for u, v in g.edges():
        s = set(g[u])
        s.update(g[v])
        s.discard(u)
        s.discard(v)
        if len(s) > best:
            best = len(s)
    return best


def maxN_excl_B(g):
    cn = {v: frozenset(g.adj[v]) for v in g.nodes()}
    best = 0
    for u, v in g.edges():
        s = set(cn[u])
        s.update(cn[v])
        s -= {u, v}
        if len(s) > best:
            best = len(s)
    return best


def ecc_B(g):
    """Hand BFS eccentricities (engine-B path)."""
    out = {}
    for s in g.nodes():
        dist = {s: 0}
        queue = [s]
        for v in queue:
            dv = dist[v]
            for w in g[v]:
                if w not in dist:
                    dist[w] = dv + 1
                    queue.append(w)
        out[s] = max(dist.values())
    return out


def center_size_A(g):
    e = nx.eccentricity(g)
    m = min(e.values())
    return sum(1 for v in e if e[v] == m)


def center_size_B(g):
    e = ecc_B(g)
    m = min(e.values())
    return sum(1 for v in e if e[v] == m)


def min_degree_set(g):
    delta = min(dict(g.degree()).values())
    return [v for v in g.nodes() if g.degree(v) == delta]


def open_nbhd_size_of_set(g, S):
    acc = set()
    for s in S:
        acc.update(g[s])
    return len(acc)


# ---------------------------------------------------------------- gamma_t engines
def gamma_t_ilp(g):
    import pulp

    nodes = list(g.nodes())
    x = {v: pulp.LpVariable(f"x_{i}", cat="Binary") for i, v in enumerate(nodes)}
    prob = pulp.LpProblem("total_domination", pulp.LpMinimize)
    prob += pulp.lpSum(x.values())
    for v in nodes:
        nbrs = list(g[v])
        if not nbrs:
            return None  # isolated vertex: no total dominating set exists
        prob += pulp.lpSum(x[u] for u in nbrs) >= 1
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    return int(round(sum((pulp.value(x[v]) or 0) for v in nodes)))


def _greedy_td(adj, n):
    dom = set()
    D = []
    while len(dom) < n:
        v = max(range(n), key=lambda z: len(adj[z] - dom))
        D.append(v)
        dom |= adj[v]
    Dset = set(D)
    extras = set()
    for d in D:
        if not (adj[d] & Dset):
            u = next(iter(adj[d]))
            extras.add(u)
            Dset.add(u)
    return Dset | extras


def gamma_t_bnb(g):
    """Independent engine: branch on an undominated vertex's neighborhood."""
    nodes = list(g.nodes())
    n = len(nodes)
    if any(g.degree(v) == 0 for v in nodes):
        return None
    idx = {v: i for i, v in enumerate(nodes)}
    adj = [{idx[w] for w in g[v]} for v in nodes]

    best = _greedy_td(adj, n)
    best_len = len(best)

    dom_count = [0] * n
    chosen = []

    def rec():
        nonlocal best_len
        if len(chosen) >= best_len:
            return
        target = None
        tdeg = 10 ** 9
        for v in range(n):
            if dom_count[v] == 0 and len(adj[v]) < tdeg:
                tdeg = len(adj[v])
                target = v
                if tdeg <= 1:
                    break
        if target is None:
            best_len = len(chosen)
            return
        for u in sorted(adj[target], key=lambda z: -len(adj[z])):
            chosen.append(u)
            for w in adj[u]:
                dom_count[w] += 1
            rec()
            for w in adj[u]:
                dom_count[w] -= 1
            chosen.pop()
            if len(chosen) >= best_len:
                return

    rec()
    return best_len


def gamma_t_bruteforce(g):
    """Third check (only invoked on candidate hits): iterative-deepening combos."""
    nodes = list(g.nodes())
    n = len(nodes)
    adjsets = [set(g[v]) for v in nodes]
    for k in range(2, n + 1):
        for combo in __import__("itertools").combinations(range(n), k):
            s = set(combo)
            ok = True
            cov = set()
            for i in combo:
                if not (adjsets[i] & s):
                    ok = False
                    break
                cov |= adjsets[i]
            if ok and len(cov) == n:
                return k
    return None


# ---------------------------------------------------------------- evaluation
def residual(gamma_t, num, den):
    if den == 0:
        return None  # UNDEFINED reading
    return Fraction(gamma_t) - Fraction(2 * num, den)


def evaluate(g, name, origin, brute_on_hit=True):
    t0 = time.time()
    gtA = gamma_t_ilp(g)
    gtB = gamma_t_bnb(g)
    csA = center_size_A(g)
    csB = center_size_B(g)
    A = min_degree_set(g)
    na = open_nbhd_size_of_set(g, A)
    miA, miB = maxN_incl_A(g), maxN_incl_B(g)
    meA, meB = maxN_excl_A(g), maxN_excl_B(g)
    elapsed = time.time() - t0

    agree = (
        gtA == gtB
        and csA == csB
        and miA == miB
        and meA == meB
    )
    row = {
        "name": name,
        "origin": origin,
        "n": g.number_of_nodes(),
        "gamma_t": gtA,
        "absC": csA,
        "absNA": na,
        "maxN_incl": miA,
        "maxN_excl": meA,
        "engines_agree": bool(agree),
        "seconds": round(elapsed, 3),
        "within_cap": bool(elapsed <= CAP_S),
    }
    for tag, den, num in (
        ("r255_RD-A", miA, csA),
        ("r255_RD-B", meA, csA),
        ("r256_RD-A", miA, na),
        ("r256_RD-B", meA, na),
    ):
        val = residual(gtA, num, den)
        row[tag] = str(val) if val is not None else "UNDEFINED"
    row["_viol_any"] = any(
        Fraction(row[t]) < 0
        for t in ("r255_RD-A", "r256_RD-A")
        if row[t] != "UNDEFINED"
    )
    if brute_on_hit and row["_viol_any"]:
        row["brute_gamma_t"] = gamma_t_bruteforce(g)
    return row, g


# ---------------------------------------------------------------- graph builders
def blowup_c5(weights):
    """Blow-up of the cycle C_len(weights): blob i = clique of size weights[i],
    complete joins between consecutive blobs (mod len)."""
    k = len(weights)
    g = nx.Graph()
    offs = []
    cur = 0
    for w in weights:
        offs.append(list(range(cur, cur + w)))
        cur += w
    for blob in offs:
        for i in range(len(blob)):
            for j in range(i + 1, len(blob)):
                g.add_edge(blob[i], blob[j])
    for i in range(k):
        for u in offs[i]:
            for v in offs[(i + 1) % k]:
                g.add_edge(u, v)
    return g


def subdivide_first_edge(g):
    h = g.copy()
    u, v = sorted(h.edges())[0]
    h.remove_edge(u, v)
    w = max(h.nodes()) + 1
    h.add_edge(u, w)
    h.add_edge(w, v)
    return h


def delete_first_edge(g):
    h = g.copy()
    u, v = sorted(h.edges())[0]
    h.remove_edge(u, v)
    return h


def add_pendant(g, v):
    h = g.copy()
    w = max(h.nodes()) + 1
    h.add_edge(v, w)
    return h


def relabel_int(g):
    return nx.convert_node_labels_to_integers(g)


# ---------------------------------------------------------------- steps
def named_controls():
    ctrls = []
    ctrls.append(("C5", nx.cycle_graph(5)))
    ctrls.append(("C6", nx.cycle_graph(6)))
    ctrls.append(("C7", nx.cycle_graph(7)))
    ctrls.append(("C8", nx.cycle_graph(8)))
    ctrls.append(("C9", nx.cycle_graph(9)))
    ctrls.append(("P7", nx.path_graph(7)))
    ctrls.append(("Petersen", nx.petersen_graph()))
    ctrls.append(("K3,3", nx.complete_bipartite_graph(3, 3)))
    ctrls.append(("K7", nx.complete_graph(7)))
    for k in range(3, 9):
        ctrls.append((f"K1,{k}", nx.star_graph(k)))
    for k in range(2, 7):
        ctrls.append((f"K{k},{k}", nx.complete_bipartite_graph(k, k)))
    return ctrls


def step_fixtures():
    F = [
        ("K2", lambda: nx.complete_graph(2), 2, 2, 2, 2, "0", "0"),
        ("K3", lambda: nx.complete_graph(3), 2, 3, 3, 3, "0", "0"),
        ("K4", lambda: nx.complete_graph(4), 2, 4, 4, 4, "0", "0"),
        ("C4", lambda: nx.cycle_graph(4), 2, 4, 4, 4, "0", "0"),
        ("C5", lambda: nx.cycle_graph(5), 3, 5, 5, 4, "1/2", "1/2"),
        ("C6", lambda: nx.cycle_graph(6), 4, 6, 6, 4, "1", "1"),
        ("C7", lambda: nx.cycle_graph(7), 4, 7, 7, 4, "1/2", "1/2"),
        ("P7", lambda: nx.path_graph(7), 4, 1, 2, 4, "7/2", "3"),
        ("K1,3", lambda: nx.star_graph(3), 2, 1, 1, 4, "3/2", "3/2"),
        ("K1,4", lambda: nx.star_graph(4), 2, 1, 1, 5, "8/5", "8/5"),
        ("K3,3", lambda: nx.complete_bipartite_graph(3, 3), 2, 6, 6, 6, "0", "0"),
        ("Q3", lambda: relabel_int(nx.hypercube_graph(3)), 4, 8, 8, 6, "4/3", "4/3"),
        ("Petersen", lambda: nx.petersen_graph(), 4, 10, 10, 6, "2/3", "2/3"),
    ]
    rows = []
    all_ok = True
    for name, fn, gt, c_, na_, mx, r255, r256 in F:
        row, _ = evaluate(fn(), f"fixture:{name}", "fixture", brute_on_hit=False)
        got = (row["r255_RD-A"], row["r256_RD-A"])
        exp = (r255, r256)
        ok = (
            got == exp
            and row["gamma_t"] == gt
            and row["absC"] == c_
            and row["absNA"] == na_
            and row["maxN_incl"] == mx
            and row["engines_agree"]
        )
        all_ok &= ok
        rows.append({"name": name, "ok": bool(ok), "expected": exp, "row": row})
        print(f"{'PASS' if ok else 'FAIL'} {name}: got {got} expected {exp}")
    (HERE / "fixtures.json").write_text(json.dumps(rows, indent=2))
    print("FIXTURES:", "ALL PASS" if all_ok else "FAILURE")
    return 0 if all_ok else 1


def step_gate():
    rows = []
    violations = {"r255_RD-A": [], "r255_RD-B": [], "r256_RD-A": [], "r256_RD-B": []}
    undefined = {"r255_RD-B": [], "r256_RD-B": []}
    atlas = [
        g
        for g in nx.graph_atlas_g()
        if 2 <= g.number_of_nodes() <= 7 and nx.is_connected(g)
    ]
    ctrls = [("atlas:%d" % i, g) for i, g in enumerate(atlas)] + named_controls()
    for name, g in ctrls:
        row, _ = evaluate(g, name, "gate", brute_on_hit=False)
        rows.append(row)
        for tag in violations:
            v = row[tag]
            if v == "UNDEFINED":
                undefined[tag].append(name)
            elif Fraction(v) < 0:
                violations[tag].append(name)
        if not row["engines_agree"]:
            print("ENGINE DISAGREEMENT AT GATE ROW", name, row)
    n_conn = len(atlas)
    summary = {
        "atlas_connected_rows": n_conn,
        "named_rows": len(rows) - n_conn,
        "total_rows": len(rows),
        "violations": {k: v[:25] + (["..."] * (len(v) > 25)) for k, v in violations.items()},
        "violation_counts": {k: len(v) for k, v in violations.items()},
        "undefined_counts": {k: len(v) for k, v in undefined.items()},
        "undefined_examples": {k: v[:10] for k, v in undefined.items()},
    }
    (HERE / "gate_rows.json").write_text(
        json.dumps({"summary": summary, "rows": rows}, indent=2)
    )
    print(json.dumps(summary, indent=2))
    return 0


def arsenal_graphs():
    ars = []
    for m in range(2, 9):
        ars.append((f"C5[K{m}]", blowup_c5([m] * 5)))
    for t in (7, 8, 9):
        ars.append((f"T({t})=L(K{t})", relabel_int(nx.line_graph(nx.complete_graph(t)))))
    ars.append(("comp(C5[K4])", nx.complement(blowup_c5([4] * 5))))
    ars.append(("C7[K3]", blowup_c5([3] * 7)))
    ars.append(("C9[K3]", blowup_c5([3] * 9)))
    ars.append(("Petersen", nx.petersen_graph()))
    return ars


def step_arsenal():
    rows = []
    for name, g in arsenal_graphs():
        row, _ = evaluate(g, name, "arsenal")
        rows.append(row)
        print(
            f"{name}: n={row['n']} gt={row['gamma_t']} "
            f"255A={row['r255_RD-A']} 256A={row['r256_RD-A']} "
            f"({row['seconds']}s)"
        )
    (HERE / "arsenal_rows.json").write_text(json.dumps(rows, indent=2))
    return 0


def family_graphs():
    fam = []

    q3 = relabel_int(nx.hypercube_graph(3))
    fam.append(("W_Q3_base", q3))
    fam.append(("W_Q3_delete_e0", delete_first_edge(q3)))
    fam.append(("W_Q3_subdiv_e0", subdivide_first_edge(q3)))
    fam.append(("W_Q3_pendant@0", add_pendant(q3, 0)))
    fq3 = q3.copy()
    fq3.add_edge(0, 7)
    fam.append(("W_Q3_chord_antipodal", fq3))

    c6 = nx.cycle_graph(6)
    fam.append(("W_C6_base", c6))
    fam.append(("W_C6_delete_e0", delete_first_edge(c6)))
    fam.append(("W_C6_subdiv_e0", subdivide_first_edge(c6)))
    fc6 = add_pendant(c6, 0)
    fam.append(("W_C6_pendant@0", fc6))
    fc6b = c6.copy()
    fc6b.add_edge(0, 3)
    fam.append(("W_C6_chord_03", fc6b))

    k33 = nx.complete_bipartite_graph(3, 3)
    fam.append(("W_K33_base", k33))
    fam.append(("W_K33_delete_a0b0", delete_first_edge(k33)))
    fam.append(("W_K33_subdiv_a0b0", subdivide_first_edge(k33)))
    fam.append(("W_K33_pendant@a0", add_pendant(k33, 0)))
    fk33 = k33.copy()
    fk33.add_edge(0, 1)
    fam.append(("W_K33_partedge_a0a1", fk33))

    for k in range(3, 9):
        fam.append((f"P_prism_C{k}xK2", relabel_int(nx.circular_ladder_graph(k))))
    for k in (9, 10, 11, 12):
        fam.append((f"C_circ{k}_12", nx.circulant_graph(k, [1, 2])))
    fam.append(("C_circ10_13", nx.circulant_graph(10, [1, 3])))

    for w in [
        (3, 1, 1, 1, 1),
        (4, 1, 1, 1, 1),
        (3, 2, 1, 1, 1),
        (5, 1, 2, 1, 1),
        (2, 3, 2, 3, 2),
        (6, 1, 1, 1, 1),
    ]:
        fam.append((f"B_w{w}", blowup_c5(w)))

    for t in (5, 6, 7):
        fam.append((f"L_T({t})", relabel_int(nx.line_graph(nx.complete_graph(t)))))
    fam.append(("L_Q3", relabel_int(nx.line_graph(nx.hypercube_graph(3)))))
    fam.append(("L_Petersen", relabel_int(nx.line_graph(nx.petersen_graph()))))
    return fam


def step_family():
    rows = []
    hits = []
    for name, g in family_graphs():
        row, _ = evaluate(g, name, "family")
        rows.append(row)
        neg = {
            t: row[t]
            for t in ("r255_RD-A", "r256_RD-A")  # RD-B is gate-dead (STOP_CORRUPT_READING)
            if row[t] != "UNDEFINED" and Fraction(row[t]) < 0
        }
        flag = " HIT " if neg else ""
        print(
            f"{flag}{name}: n={row['n']} gt={row['gamma_t']} |C|={row['absC']} "
            f"|N(A)|={row['absNA']} maxN={row['maxN_incl']} "
            f"255A={row['r255_RD-A']} 256A={row['r256_RD-A']} ({row['seconds']}s)"
        )
        if neg:
            hits.append({"name": name, "negatives": neg, "row": row})
    (HERE / "family_rows.json").write_text(json.dumps(rows, indent=2))
    if hits:
        (HERE / "HITS.json").write_text(json.dumps(hits, indent=2))
        for name, g in family_graphs():
            if any(h["name"] == name for h in hits):
                nx.write_adjlist(g, str(HERE / f"witness_{name}.adjlist"))
    print(f"FAMILY: {len(rows)} rows, {len(hits)} negative-residual candidates")
    return 0


def main():
    step = sys.argv[1] if len(sys.argv) > 1 else "all"
    rc = 0
    if step in ("fixtures", "all"):
        rc = step_fixtures()
        if rc != 0:
            return rc
    if step in ("gate", "all"):
        step_gate()
    if step in ("arsenal", "all"):
        step_arsenal()
    if step in ("family", "all"):
        step_family()
    return rc


if __name__ == "__main__":
    sys.exit(main())
