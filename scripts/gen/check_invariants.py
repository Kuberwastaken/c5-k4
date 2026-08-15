"""Correctness and runtime checks for the invariant vocabulary.

Two jobs:

1. **Cross-check** the ``brute`` and ``scal`` backends on a deterministic sample
   of `D`.  They share only the polynomial part; every NP-hard invariant is
   computed twice by unrelated algorithms.

2. **Runtime budget.** Measure the ``scal`` backend on 20--40 vertex graphs so
   that "every conjecture is checkable on a 20--40 vertex graph in well under
   60 s" is a measurement, not an assumption.

CONTAMINATION NOTE.  This script prints **timings only** for graphs outside `D`.
It never evaluates, compares, or reports an inequality on them, and it never
prints an invariant *value* for one -- there is no code path by which a candidate
conjecture could be tested here.  Its stress graphs are generic structures
(paths, cycles, grids, hypercubes, circulants, complete multipartite, seeded
random graphs) chosen for algorithmic difficulty, not for any target.

Usage:
    python3 scripts/gen/check_invariants.py
"""
from __future__ import annotations

import random
import signal
import sys
import time

import networkx as nx

import graph_db as DB
import invariants as I

SEED = 20260815


def cross_check(k: int = 400) -> int:
    D = DB.load()
    rng = random.Random(SEED)
    idx = sorted(rng.sample(range(len(D)), k))
    bad = 0
    t0 = time.time()
    for i in idx:
        G = D[i]
        a = I.compute(G, "brute")
        b = I.compute(G, "scal")
        diff = {n: (str(a[n]), str(b[n])) for n in a if a[n] != b[n]}
        if diff:
            bad += 1
            print("  DISAGREE %s %s" % (DB.g6(G), diff))
    print("cross-check: %d graphs, %d disagreements, %.1fs" % (k, bad, time.time() - t0))
    return bad


def stress_graphs():
    rng = random.Random(SEED)
    out = [
        ("path_40", nx.path_graph(40)),
        ("cycle_40", nx.cycle_graph(40)),
        ("grid_5x8", nx.convert_node_labels_to_integers(nx.grid_2d_graph(5, 8))),
        ("hypercube_Q5_32", nx.convert_node_labels_to_integers(nx.hypercube_graph(5))),
        ("circulant_30_1_3", nx.circulant_graph(30, [1, 3])),
        ("circulant_36_1_5_9", nx.circulant_graph(36, [1, 5, 9])),
        ("complete_multipartite_5x6", nx.complete_multipartite_graph(6, 6, 6, 6, 6)),
        ("complete_bipartite_20_20", nx.complete_bipartite_graph(20, 20)),
        ("wheel_31", nx.wheel_graph(31)),
        ("binary_tree_31", nx.balanced_tree(2, 4)),
        ("complete_30", nx.complete_graph(30)),
        ("complete_40", nx.complete_graph(40)),
    ]
    for n, p in [(20, 0.3), (25, 0.5), (30, 0.2), (30, 0.5), (35, 0.35), (40, 0.15),
                 (40, 0.3), (40, 0.5), (40, 0.7)]:
        for t in range(2):
            G = nx.gnp_random_graph(n, p, seed=rng.randint(0, 10 ** 9))
            if nx.is_connected(G):
                out.append(("gnp_%d_%s_%d" % (n, p, t), G))
    return out


CAP = 15.0                                  # per-invariant cap; the task cap is 60 s


class _Timeout(Exception):
    pass


def _alarm(signum, frame):                                          # pragma: no cover
    raise _Timeout()


def _timed(fn, *a):
    signal.signal(signal.SIGALRM, _alarm)
    signal.setitimer(signal.ITIMER_REAL, CAP)
    t0 = time.time()
    try:
        fn(*a)
        return time.time() - t0
    except _Timeout:
        return None
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def _pieces(G):
    base = I._base(G)
    adj, n = base["adj"], base["n"]
    full = (1 << n) - 1
    comp = [full & ~(adj[v] | (1 << v)) for v in range(n)]
    return [
        ("poly-part", lambda: I._poly_part(G, adj, n)),
        ("alpha", lambda: I._max_independent_bb(adj, full, n)),
        ("omega", lambda: I._max_independent_bb(comp, full, n)),
        ("chi", lambda: I._chromatic_brute(adj, n)),
        ("lam_*", lambda: [I._max_independent_bb(adj, adj[v], n) for v in range(n)]),
        ("gamma", lambda: I._min_dominating(adj, n, "gamma")),
        ("gamma_t", lambda: I._min_dominating(adj, n, "gamma_t")),
        ("gamma_2", lambda: I._min_dominating(adj, n, "gamma_2")),
        ("gamma_i", lambda: I._min_dominating(adj, n, "gamma_i")),
        ("f", lambda: I._max_induced_forest_bb(adj, n)),
        ("b", lambda: I._max_induced_bipartite_bb(adj, n)),
    ]


def runtime_budget():
    names = [p[0] for p in _pieces(nx.path_graph(3))]
    worst = {k: 0.0 for k in names}
    timeouts = {k: [] for k in names}
    rows = []
    for gname, G in stress_graphs():
        G = nx.convert_node_labels_to_integers(G)
        if not nx.is_connected(G):
            continue
        tot = 0.0
        cells = []
        for pname, fn in _pieces(G):
            el = _timed(fn)
            if el is None:
                timeouts[pname].append(gname)
                cells.append(">%d" % CAP)
                tot = float("inf")
            else:
                worst[pname] = max(worst[pname], el)
                tot += el
                cells.append("%.1f" % el if el >= 0.05 else ".")
        rows.append((gname, G.number_of_nodes(), G.number_of_edges(),
                     ("%.1f" % tot) if tot != float("inf") else "TIMEOUT", cells))
    print("\nper-invariant runtime, 'scal' backend, seconds "
          "('.' = <0.05 s).  Timings only; no inequality is evaluated here.")
    hdr = "  %-26s %4s %5s %8s  " % ("graph", "n", "m", "total") + \
          " ".join("%7s" % n for n in names)
    print(hdr)
    for gname, n, m, tot, cells in rows:
        print("  %-26s %4d %5d %8s  " % (gname, n, m, tot) +
              " ".join("%7s" % c for c in cells))
    print("\nworst per invariant:")
    for k in names:
        note = "  TIMEOUT on %s" % ", ".join(timeouts[k]) if timeouts[k] else ""
        print("  %-12s %6.2f s%s" % (k, worst[k], note))
    return worst, timeouts


def main() -> int:
    bad = cross_check()
    worst, timeouts = runtime_budget()
    slow = [k for k in worst if timeouts[k] or worst[k] >= CAP]
    if slow:
        print("\nOVER BUDGET: %s -- these must be dropped from the emission vocabulary"
              % ", ".join(slow))
    ok = bad == 0
    print("\nRESULT: correctness %s; over-budget invariants: %s"
          % ("PASS" if ok else "FAIL", slow or "none"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
