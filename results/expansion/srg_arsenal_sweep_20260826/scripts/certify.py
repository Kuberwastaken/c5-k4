"""Certify the extended invariant battery for every arsenal graph.

Resumable: results saved to cache/cert/<graph>.json after each graph.
NP-hard invariants carry {"value", "certified"} records; BracketTimeout ->
{"bracket": true, "lower": best_found} (maximization) or incumbent note.
"""
import json
import pickle
import sys
import time
from fractions import Fraction
from pathlib import Path

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import invlib as iv

CACHE = HERE.parent / "cache"
CERT = CACHE / "cert"
CERT.mkdir(exist_ok=True, parents=True)

CAP = 60.0


def F(x):
    return float(x)


def certify(name, G):
    rec = {}
    n = G.number_of_nodes()
    nodes = sorted(G.nodes())
    deg = dict(G.degree())
    degseq = sorted(deg.values())
    rec["n"] = n
    rec["m_edges"] = G.number_of_edges()
    rec["delta"] = degseq[0]
    rec["Delta"] = degseq[-1]
    rec["sigma_2nd_smallest"] = degseq[1] if n >= 2 else None
    rec["Sigma_2nd_largest"] = degseq[-2] if n >= 2 else None
    rec["deg_avg"] = Fraction(2 * G.number_of_edges(), n)
    rec["dd"] = len(set(degseq))
    ms = iv.mode_stats(G)
    rec.update({f"mode_{k}": v for k, v in ms.items()})
    md = iv.median_stats(G)
    rec.update({"median_" + k: v for k, v in md.items()})
    rec["q1_ceil"] = iv.q1_quartile(G, "ceil")
    rec["q1_floor"] = iv.q1_quartile(G, "floor")
    rec["annihilation"] = iv.annihilation(G)
    rec["CW"] = iv.caro_wei(G)
    rec["CW_float"] = F(rec["CW"])
    rec["maxine"] = iv.maxine(G)
    rec["WP_complement"] = iv.welsh_powell(nx.complement(G))
    rec["SW_G"] = iv.sw_degeneracy(G)
    rec["SW_comp"] = iv.sw_degeneracy(nx.complement(G))
    rec["length_sq"] = iv.length_sq(G)
    rec["residue"] = iv.residue(G)
    rec["HH_steps"] = iv.havel_hakimi_steps(G)
    rec["chi_residue2"] = int(rec["residue"] == 2)
    rec["bipartite"] = int(nx.is_bipartite(G))
    # connectivity family
    rec["kappa_vertex"] = nx.node_connectivity(G)
    rec["kappa_edge"] = nx.edge_connectivity(G)
    rec["components"] = nx.number_connected_components(G)
    rec["isolates"] = sum(1 for v in nodes if deg[v] == 0)
    rec["cut_vertices"] = len(list(nx.articulation_points(G)))
    # distances
    ecc = {}
    for v in nodes:
        _, layers = iv.bfs_layers(G, v)
        ecc[v] = max(layers.keys())
    rec["ecc"] = ecc
    rec["diam"] = max(ecc.values())
    rec["rad"] = min(ecc.values())
    ev, od = iv.dist_even_odd(G)
    rec["dist_even"] = ev
    rec["dist_odd"] = od
    tr, dm = iv.transmissions(G)
    rec["Tdist"] = tr
    eh, oh = iv.horizontal_counts(G)
    rec["even_horizontal"] = eh
    rec["odd_horizontal"] = oh
    Bset = [v for v in nodes if ecc[v] == rec["diam"]]
    Cset = [v for v in nodes if ecc[v] == rec["rad"]]
    Mset = [v for v in nodes if deg[v] == rec["Delta"]]
    Aset = [v for v in nodes if deg[v] == rec["delta"]]
    rec["periphery_B"] = Bset
    rec["center_C"] = Cset
    rec["M_set"] = Mset
    rec["A_set"] = Aset
    # dist between max/min-degree vertices
    dMM = [dm[a][b] for a, b in __import__("itertools").combinations(Mset, 2)]
    dAA = [dm[a][b] for a, b in __import__("itertools").combinations(Aset, 2)]
    rec["dist_max_M"] = max(dMM) if dMM else 0
    rec["dist_min_M"] = min(dMM) if dMM else 0
    rec["dist_max_A"] = max(dAA) if dAA else 0
    rec["dist_min_A"] = min(dAA) if dAA else 0
    # radial circles (centers)
    rc_orders = []
    for c in Cset[:1]:
        _, layers = iv.bfs_layers(G, c)
        rc_orders = sorted(layers[k] for k in layers if k == rec["rad"])
    rec["radial_circle_orders_at_center"] = {
        c: sorted(l for k, l in iv.bfs_layers(G, c)[1].items() if k == rec["rad"])
        for c in Cset}
    # triangles / K4 / disparity
    tv = iv.triangles_per_vertex(G)
    rec["triangles_total"] = sum(tv.values()) // 3
    rec["T_v"] = tv
    tvals = sorted(tv.values())
    rec["T_min"] = tvals[0]
    rec["T_max"] = tvals[-1]
    rec["freq_T_max"] = tvals.count(tvals[-1])
    kv = iv.k4_per_vertex(G)
    rec["K4_v"] = kv
    kval = sorted(kv.values())
    rec["K4_min"] = kval[0]
    rec["K4_max"] = kval[-1]
    rec["freq_K4_max"] = kval.count(kval[-1])
    rec["dd_K4_seq"] = len(set(kv.values()))
    disp = iv.disparity(G)
    rec["disp"] = disp
    dv = sorted(disp.values())
    rec["disp_min"], rec["disp_max"] = dv[0], dv[-1]
    rec["disp_sum"] = sum(dv)
    rec["disp_avg"] = Fraction(sum(dv), n)
    # edge neighborhoods
    en = iv.edge_neighborhood_sizes(G)
    rec["N_edge_max"] = max(en.values())
    rec["N_edge_min"] = min(en.values())
    Hc = nx.complement(G)
    enc = iv.edge_neighborhood_sizes(Hc)
    rec["Nbar_edge_max"] = max(enc.values()) if enc else None
    rec["Nbar_edge_min"] = min(enc.values()) if enc else None
    # named-set quantities
    def nsz(S):
        return S if isinstance(S, int) else len(set(S))

    NM = set().union(*[set(G[v]) for v in Mset]) if Mset else set()
    NA = set().union(*[set(G[v]) for v in Aset]) if Aset else set()
    rec["card_N_M"] = len(NM)
    rec["card_NM_minus_M"] = len(NM - set(Mset))
    rec["card_N_A"] = len(NA)
    rec["card_NA_minus_A"] = len(NA - set(Aset))
    NB = set().union(*[set(G[v]) for v in Bset]) if Bset else set()
    rec["card_NB_minus_B"] = len(NB - set(Bset))
    D2 = [v for v in nodes if deg[v] == 2]
    rec["D2_set"] = D2
    ND2 = set().union(*[set(G[v]) for v in D2]) if D2 else set()
    rec["card_N_D2"] = len(ND2)
    rec["card_ND2_minus_D2"] = len(ND2 - set(D2))
    P_pend = [v for v in nodes if deg[v] == 1]
    rec["pendant_P"] = P_pend
    Supp = [v for v in nodes if any(deg[u] == 1 for u in G[v])]
    rec["support_S"] = Supp
    rec["f1_deg1_freq"] = len(P_pend)
    rec["E_in_A"] = G.subgraph(Aset).number_of_edges()
    rec["E_in_M"] = G.subgraph(Mset).number_of_edges()
    rec["E_in_D2"] = G.subgraph(D2).number_of_edges()
    rec["E_between_AB_cross"] = sum(1 for u, v in G.edges()
                                    if (u in Aset) != (v in Aset))
    # C4-free indicator (subgraph, not induced)
    has_c4 = False
    for a, b in itertools_comb_pairs(nodes):
        cab = set(G[a]) & set(G[b])
        if len(cab) >= 2:
            has_c4 = True
            break
    rec["chi_C4free"] = int(not has_c4)
    # dp(G): number of pairs at distance = diam ; 2-B: boundary pairs at dist 2
    cnt_dp = 0
    cnt_2B = 0
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            if dm[a][b] == rec["diam"]:
                cnt_dp += 1
            if a in Bset and b in Bset and dm[a][b] == 2:
                cnt_2B += 1
    rec["dp_diametral_pairs"] = cnt_dp
    rec["two_B_pairs"] = cnt_2B
    # NP-hard battery
    t0 = time.time()
    try:
        val, wit, proved = iv.independence_number(G, CAP)
        rec["alpha"] = {"value": val, "certified": proved,
                        "secs": round(time.time() - t0, 1)}
    except iv.BracketTimeout:
        rec["alpha"] = {"bracket": True}
    rec["v_cover"] = n - rec["alpha"]["value"]
    # local independence
    t0 = time.time()
    try:
        lams = []
        for v in nodes:
            lams.append(iv.local_independence(G, v, CAP))
        rec["lambda_stats"] = {"min": min(lams), "max": max(lams),
                               "avg": Fraction(sum(lams), n),
                               "certified": True}
    except iv.BracketTimeout:
        rec["lambda_stats"] = {"bracket": True,
                               "note": f"completed {len(locals().get('lams', []))}/{n} vertices"}
    rec["lambda_secs"] = round(time.time() - t0, 1)
    # matching
    mm = nx.max_weight_matching(G, maxcardinality=True)
    rec["mu"] = len(mm)
    # clique
    tl = iv._TLimit(CAP)
    nd, idx_, masks = iv._adj_masks(G)
    try:
        w, _, proved = iv.max_clique_bnb(masks, tl)
        rec["omega"] = {"value": w, "certified": proved}
    except iv.BracketTimeout:
        rec["omega"] = {"bracket": True}
    # domination battery
    for key, fn in (("gamma", iv.gamma), ("gamma_t", iv.gamma_t),
                    ("gamma_2", iv.gamma_2), ("i", iv.indep_domination_number)):
        t0 = time.time()
        try:
            r = fn(G, CAP)
            r["secs"] = round(time.time() - t0, 1)
            rec[key] = r
        except Exception as e:
            rec[key] = {"error": str(e)}
    # critical independence
    t0 = time.time()
    try:
        r = iv.critical_independence(G, 2 * CAP)
        r["secs"] = round(time.time() - t0, 1)
        rec["alpha_crit"] = r
    except iv.BracketTimeout:
        rec["alpha_crit"] = {"bracket": True}
    # alpha_2 (2-independence, dissociation)
    t0 = time.time()
    try:
        v2, proved2 = iv.dissociation_number(G, 2, CAP)
        rec["alpha_2"] = {"value": v2, "certified": proved2,
                          "secs": round(time.time() - t0, 1)}
    except iv.BracketTimeout:
        rec["alpha_2"] = {"bracket": True}
    # hereditary battery
    for key, fn in (("f", lambda: iv.largest_induced_forest(G, False, CAP)),
                    ("tree", lambda: iv.largest_induced_forest(G, True, CAP)),
                    ("b", lambda: iv.max_induced_bipartite(G, CAP)),
                    ("path_induced", lambda: iv.largest_induced_path(G, CAP))):
        t0 = time.time()
        try:
            vv, proved = fn()
            rec[key] = {"value": vv, "certified": proved,
                        "secs": round(time.time() - t0, 1)}
        except iv.BracketTimeout:
            rec[key] = {"bracket": True}
    # path cover (Hamiltonian witness => 1)
    t0 = time.time()
    hp = iv.ham_path_search(G)
    rec["p_cov"] = ({"value": 1, "certified": True, "witness": "ham path"}
                    if hp == 1 else {"bracket": True, "note": "no ham path found"})
    rec["ham_path"] = int(hp == 1)
    rec["traceable"] = int(hp == 1)
    # L_s
    t0 = time.time()
    try:
        r = iv.spanning_tree_max_leaves(G, CAP)
        r["secs"] = round(time.time() - t0, 1)
        rec["L_s"] = r
    except iv.BracketTimeout:
        rec["L_s"] = {"bracket": True}
    # well-total-dominated search
    try:
        rec["wtd_search"] = iv.well_total_dominated_search(G, samples=25, cap=25.0)
    except Exception as e:
        rec["wtd_search"] = {"error": str(e)}
    # spectra
    A = nx.to_numpy_array(G, dtype=float)
    adj_eigs = np.sort(np.linalg.eigvalsh(A))[::-1]
    rec["lambda1_numeric"] = F(adj_eigs[0])
    rec["lambda2_numeric"] = F(adj_eigs[1]) if n >= 2 else None
    L = np.diag([deg[v] for v in nodes]) - A
    lap_eigs = np.sort(np.linalg.eigvalsh(L))
    rec["algebraic_connectivity_numeric"] = F(lap_eigs[1])
    Q = np.diag([deg[v] for v in nodes]) + A
    q_eigs = np.sort(np.linalg.eigvalsh(Q))
    rec["q1_signless"] = F(q_eigs[-1])
    rec["qn_signless"] = F(q_eigs[0])
    rec["mu1_laplacian_largest"] = F(lap_eigs[-1])
    # proximity / remoteness (AGX defs: avg distance to others)
    trv = [Fraction(tr[v], n - 1) for v in nodes]
    rec["proximity"] = F(min(trv))
    rec["remoteness"] = F(max(trv))
    # average distance
    tot = sum(tr.values())
    rec["avg_distance"] = F(Fraction(tot, n * (n - 1)))
    rec["avg_distance_exact_num"] = tot
    rec["avg_distance_exact_den"] = n * (n - 1)
    # Randic index
    Ra = sum(Fraction(1, 1) for _ in ())  # placeholder replaced below
    import math as _m
    Ra = sum(1 / _m.sqrt(deg[u] * deg[v]) for u, v in G.edges())
    rec["randic_index"] = F(Ra)
    return rec


def itertools_comb_pairs(xs):
    import itertools
    a = list(xs)
    return itertools.combinations(a, 2)


def main():
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    with (CACHE / "arsenal.gpickle").open("rb") as f:
        graphs = pickle.load(f)
    for name in graphs:
        if only and name not in only:
            continue
        out = CERT / (name.replace("/", "_").replace("(", "_")
                      .replace(")", "").replace(",", "_").replace("[", "_")
                      .replace("]", "") + ".json")
        if out.exists():
            print(f"skip {name}", flush=True)
            continue
        t0 = time.time()
        rec = certify(name, graphs[name])
        out.write_text(json.dumps(rec, indent=1, default=str))
        print(f"done {name} in {time.time()-t0:.1f}s -> {out.name}", flush=True)


if __name__ == "__main__":
    main()
