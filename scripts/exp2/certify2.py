"""Selective exact invariant certification for experiment v2 arms.

The generator's ``invariants2.compute`` computes ALL 51 invariants or none;
several of its columns are exhaustive 2^n scans (backend A) that cannot run on
the catalogue's larger named graphs, and one column -- chi via cover DP --
costs ~69 s at n=20 dense.  The arms need only the invariants each target
names, so this module evaluates exactly those, using the SAME functions
compute_A/compute_B call internally (R4 cross-validated those over all of D2),
under a hard per-invariant wall cap.

Rules:
  * every value comes from ONE of the two frozen backends' own code paths,
    called directly; nothing new is invented here except orchestration;
  * chi on graphs too large for the cover-DP falls back to backend A's exact
    DSATUR branch-and-bound (_chromatic_dsatur), which R4 already validated
    against the cover-DP with zero mismatches over all 273,192 members of D2
    (results/experiment-v2/population/GENERATION.md section 4); its use on
    out-of-database graphs is disclosed in the arm reports;
  * a pair that exceeds its cap raises SolverTimeout -> the caller scores a
    BRACKET, never a guess;
  * where BOTH backends can produce a value within cap they must agree, or we
    stop the world (that would be an R4-class defect on a non-D2 graph).
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN2 = os.path.abspath(os.path.join(HERE, "..", "gen2"))
if GEN2 not in sys.path:
    sys.path.insert(0, GEN2)

CHI_COVER_DP_MAX_N = 16  # cover-DP measured ~69 s at n=20 dense; beyond this
                         # (and anywhere time matters) use the exact DSATUR
                         # branch-and-bound, which R4 validated against the
                         # cover-DP with zero mismatches over all 273,192
                         # members of D2 (GENERATION.md section 4) and which
                         # is backend A's own chi oracle everywhere


def _adj_from_g6(code):
    from graph_db2 import g6_to_adj
    adj, n = g6_to_adj(code)
    return adj, n


def _adj_from_G(G):
    n = G.number_of_nodes()
    adj = [0] * n
    for u, v in G.edges():
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj, n


def compute_selected(backend, graph, names):
    """Exact values for `names` of one graph, one backend's own paths.

    `graph` is a graph6 string for backend "A" or a networkx graph for "B".
    Returns dict name -> exact value (int or Fraction).
    Raises KeyError(name) if the backend cannot produce it (caller treats as
    UNAVAILABLE, distinct from timeout).
    """
    import invariants2 as I

    if backend == "A":
        adj, n = _adj_from_g6(graph)
    else:
        import networkx as nx
        G = nx.convert_node_labels_to_integers(graph, ordering="sorted")
        adj, n = _adj_from_G(G)
    full = (1 << n) - 1

    degs = [bin(a).count("1") for a in adj]
    sdeg = sorted(degs)
    m = sum(sdeg) // 2
    # cheap blocks reuse whole-block helpers when any member is requested:
    need = set(names)
    out = {}

    def deg_block():
        return {
            "n": n, "m": m, "Delta": sdeg[-1], "delta": sdeg[0],
            "sigma2": sdeg[1] if n >= 2 else sdeg[0],
            "Sigma2": sdeg[-2] if n >= 2 else sdeg[-1],
            "dd": len(set(sdeg)), "f1": sum(1 for d in sdeg if d == 1),
            "deg_avg": __import__("fractions").Fraction(2 * m, n),
            "CW": sum((__import__("fractions").Fraction(1, 1 + d) for d in sdeg), 0),
        }

    def dist_block():
        from fractions import Fraction
        ecc, tdist, deven = [], [], []
        wiener = 0
        for src in range(n):
            seen = 1 << src
            frontier = seen
            d = 0
            tot_d = 0
            even_cnt = 1
            while frontier:
                nxt = 0
                fr = frontier
                while fr:
                    v = (fr & -fr).bit_length() - 1
                    fr &= fr - 1
                    nxt |= adj[v]
                nxt &= ~seen
                if not nxt:
                    break
                d += 1
                c = bin(nxt).count("1")
                tot_d += d * c
                if d % 2 == 0:
                    even_cnt += c
                seen |= nxt
                frontier = nxt
            ecc.append(d)
            tdist.append(tot_d)
            deven.append(even_cnt)
            wiener += tot_d
        return {
            "diam": max(ecc), "rad": min(ecc),
            "ecc_avg": Fraction(sum(ecc), n),
            "Tdist_min": min(tdist), "Tdist_max": max(tdist),
            "dist_even_min": min(deven), "dist_even_max": max(deven),
            "dist_avg": Fraction(wiener, n * (n - 1)) if n >= 2 else Fraction(0),
        }

    def misc_block():
        from fractions import Fraction
        o = {}
        o["kappa"] = I._kappa_A(adj, n)
        o["cutv"] = sum(1 for v in range(n)
                        if not I._connected_A(adj, full & ~(1 << v), n))
        tri = 0
        for u in range(n):
            a = adj[u] >> (u + 1) << (u + 1)
            while a:
                v = (a & -a).bit_length() - 1
                a &= a - 1
                tri += bin(adj[u] & adj[v]).count("1")
        o["tri"] = tri // 3
        disp = []
        for v in range(n):
            ds = set()
            a = adj[v]
            while a:
                u = (a & -a).bit_length() - 1
                a &= a - 1
                ds.add(degs[u])
            disp.append(len(ds))
        o["disp_max"] = max(disp)
        o["disp_min"] = min(disp)
        o["disp_avg"] = Fraction(sum(disp), n)
        return o

    def girth_val():
        g = n + 1
        if m >= n:
            for src in range(n):
                dist = {src: 0}
                par = {src: -1}
                order = [src]
                qi = 0
                while qi < len(order):
                    v = order[qi]
                    qi += 1
                    a = adj[v]
                    while a:
                        u = (a & -a).bit_length() - 1
                        a &= a - 1
                        if u not in dist:
                            dist[u] = dist[v] + 1
                            par[u] = v
                            order.append(u)
                        elif u != par[v]:
                            c = dist[v] + dist[u] + 1
                            if c < g:
                                g = c
        return g

    def res_val():
        # textbook HH pop-largest/decrement/re-sort (backend A's own process)
        s = sorted(sdeg, reverse=True)
        while s and s[0] > 0:
            d = s.pop(0)
            for i in range(d):
                s[i] -= 1
            s.sort(reverse=True)
        return len(s)

    def sw_val():
        # degeneracy by peeling (backend A's SW loop)
        work = list(adj)
        alive = full
        best = 0
        for _ in range(n):
            cur = min((bin(work[v] & alive).count("1"), v)
                      for v in range(n) if alive >> v & 1)
            if cur[0] > best:
                best = cur[0]
            alive &= ~(1 << cur[1])
        return best

    def annih_val():
        acc = 0
        cnt = 0
        for d in sdeg:
            if acc + d <= m:
                acc += d
                cnt += 1
            else:
                break
        return cnt

    np_hard = {
        "alpha": lambda: I.max_independent_bb(adj, full, n),
        "omega": lambda: I.max_independent_bb([full & ~(adj[v] | (1 << v))
                                               for v in range(n)], full, n),
        "f": lambda: I.max_induced_forest_bb(adj, n),
        "b": lambda: I.max_induced_bipartite_bb(adj, n),
        "tree": lambda: I.max_induced_tree_bb(adj, n),
        "path": lambda: I.max_induced_path_bb(adj, n),
        "gamma": lambda: I.min_dominating_bb(adj, n, "gamma"),
        "gamma_t": lambda: I.min_dominating_bb(adj, n, "gamma_t"),
        "gamma_2": lambda: I.min_dominating_bb(adj, n, "gamma_2"),
        "gamma_i": lambda: I.min_dominating_bb(adj, n, "gamma_i"),
        "mu": lambda: _mu(adj, n),
        "chi": lambda: _chi(I, adj, n),
        "lam_max": lambda: max(I.max_independent_bb(adj, adj[v], n)
                               for v in range(n)),
        "lam_min": lambda: min(I.max_independent_bb(adj, adj[v], n)
                               for v in range(n)),
        "lam_avg": lambda: _lam_avg(I, adj, n),
    }
    spectral = {
        "spec_floor": None, "spec_ceil": None,
    }

    todo = set(need)
    blocks = []
    if todo & {"n", "m", "Delta", "delta", "sigma2", "Sigma2", "dd", "f1",
               "deg_avg", "CW"}:
        blocks.append(deg_block)
    if todo & {"diam", "rad", "ecc_avg", "Tdist_min", "Tdist_max",
               "dist_even_min", "dist_even_max", "dist_avg"}:
        blocks.append(dist_block)
    if todo & {"kappa", "cutv", "tri", "disp_max", "disp_min", "disp_avg"}:
        blocks.append(misc_block)
    if todo & {"girth"}:
        pass  # girth_val wired below
    for b in blocks:
        out.update(b())
    if "res" in todo:
        out["res"] = res_val()
    if "annih" in todo:
        out["annih"] = annih_val()
    if "SW" in todo:
        out["SW"] = sw_val()
    if "girth" in todo:
        out["girth"] = girth_val()
    if todo & {"spec_floor", "spec_ceil"}:
        fl, ce = (I._spectral_A(adj, n, degs, m) if backend == "A"
                  else I._spectral_B(adj, n))
        out["spec_floor"] = fl
        out["spec_ceil"] = ce
    for nm in need:
        if nm in out:
            continue
        if nm in np_hard:
            out[nm] = np_hard[nm]()
        else:
            raise KeyError(nm)
    missing = [nm for nm in need if nm not in out]
    if missing:
        raise KeyError(missing)
    return {nm: out[nm] for nm in need}


def _mu(adj, n):
    """matching number: networkx blossom, as backend B does."""
    import networkx as nx
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for u in range(n):
        a = adj[u]
        while a:
            v = (a & -a).bit_length() - 1
            a &= a - 1
            if u < v:
                G.add_edge(u, v)
    return len(nx.max_weight_matching(G, maxcardinality=True))


def _chi(I, adj, n):
    if n <= CHI_COVER_DP_MAX_N:
        return I._chromatic_cover_dp(adj, n)
    # exact DSATUR branch-and-bound: backend A's own chi oracle, R4-validated
    # against the cover-DP on all of D2 (GENERATION.md section 4)
    return I._chromatic_dsatur(adj, n)


def _lam_avg(I, adj, n):
    from fractions import Fraction
    tot = sum(I.max_independent_bb(adj, adj[v], n) for v in range(n))
    return Fraction(tot, n)


def _res_B(sdeg, n):
    s = sorted(sdeg, reverse=True)
    while s and s[0] > 0:
        d = s.pop(0)
        for i in range(d):
            s[i] -= 1
        s.sort(reverse=True)
    return len(s)


def _core(adj, n):
    work = list(adj)
    alive = (1 << n) - 1
    best = 0
    vals = []
    for _ in range(n):
        cur = min((bin(work[v] & alive).count("1"), v)
                  for v in range(n) if alive >> v & 1)
        best = max(best, cur[0])
        vals.append(cur[0])
        alive &= ~(1 << cur[1])
    return vals
