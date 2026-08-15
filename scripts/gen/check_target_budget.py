"""Is every frozen target actually checkable on a 20--40 vertex graph in < 60 s?

For each stress graph, time the polynomial block once and each NP-hard invariant
separately; then, for each target in `population.json`, report the worst-case
cost of deciding *that* statement (polynomial block + the NP-hard invariants it
actually names).

CONTAMINATION NOTE.  Timings only.  No inequality is ever evaluated here, and no
invariant *value* for a graph outside `D` is printed, returned, or compared.  The
stress graphs are generic structures chosen for algorithmic difficulty.

Usage:
    python3 scripts/gen/check_target_budget.py
"""
from __future__ import annotations

import json
import os
import signal
import sys
import time

import networkx as nx

import check_invariants as CI
import invariants as I

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
POP = os.path.join(REPO, "results", "experiment", "fresh-population", "population.json")
CAP = 12.0
BUDGET = 60.0

# which measured block each vocabulary entry belongs to
BLOCK = {"alpha": "alpha", "omega": "omega", "chi": "chi",
         "lam_max": "lam", "lam_min": "lam", "lam_avg": "lam",
         "gamma": "gamma", "gamma_t": "gamma_t", "gamma_2": "gamma_2",
         "gamma_i": "gamma_i", "f": "f", "b": "b"}


class _T(Exception):
    pass


def _alarm(s, f):
    raise _T()


def _timed(fn):
    signal.signal(signal.SIGALRM, _alarm)
    signal.setitimer(signal.ITIMER_REAL, CAP)
    t0 = time.time()
    try:
        fn()
        return time.time() - t0
    except _T:
        return None
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def main() -> int:
    pop = json.load(open(POP))
    targets = pop["targets"]
    blocks = ["poly", "alpha", "omega", "chi", "lam", "gamma", "gamma_t",
              "gamma_2", "gamma_i", "f", "b"]
    worst = {b: 0.0 for b in blocks}
    timeouts = {b: [] for b in blocks}

    print("per-block runtime, 'scal' backend (seconds).  Timings only.")
    print("  %-26s %4s %5s  " % ("graph", "n", "m") + " ".join("%8s" % b for b in blocks))
    for gname, G in CI.stress_graphs():
        G = nx.convert_node_labels_to_integers(G)
        if not nx.is_connected(G):
            continue
        base = I._base(G)
        adj, n = base["adj"], base["n"]
        full = (1 << n) - 1
        comp = [full & ~(adj[v] | (1 << v)) for v in range(n)]
        jobs = [
            ("poly", lambda: I._poly_part(G, adj, n)),
            ("alpha", lambda: I._max_independent_bb(adj, full, n)),
            ("omega", lambda: I._max_independent_bb(comp, full, n)),
            ("chi", lambda: I._chromatic_brute(adj, n)),
            ("lam", lambda: [I._max_independent_bb(adj, adj[v], n) for v in range(n)]),
            ("gamma", lambda: I._min_dominating(adj, n, "gamma")),
            ("gamma_t", lambda: I._min_dominating(adj, n, "gamma_t")),
            ("gamma_2", lambda: I._min_dominating(adj, n, "gamma_2")),
            ("gamma_i", lambda: I._min_dominating(adj, n, "gamma_i")),
            ("f", lambda: I._max_induced_forest_bb(adj, n)),
            ("b", lambda: I._max_induced_bipartite_bb(adj, n)),
        ]
        cells = []
        for name, fn in jobs:
            el = _timed(fn)
            if el is None:
                timeouts[name].append(gname)
                cells.append(">%d" % CAP)
            else:
                worst[name] = max(worst[name], el)
                cells.append("%.2f" % el if el >= 0.005 else ".")
        print("  %-26s %4d %5d  " % (gname, G.number_of_nodes(), G.number_of_edges())
              + " ".join("%8s" % c for c in cells), flush=True)

    print("\nworst observed per block:")
    for b in blocks:
        note = ("   TIMEOUT (>%ds) on: %s" % (CAP, ", ".join(timeouts[b]))) if timeouts[b] else ""
        print("  %-9s %7.2f s%s" % (b, worst[b], note))

    print("\nworst-case cost per frozen target (polynomial block + the NP-hard "
          "invariants it names):")
    over = []
    for t in targets:
        need = {BLOCK[i] for i in t["invariants_used"] if i in BLOCK}
        if any(timeouts[b] for b in need) or timeouts["poly"]:
            cost, mark = float("inf"), "TIMEOUT"
        else:
            cost = worst["poly"] + sum(worst[b] for b in need)
            mark = "%.2f s" % cost
        if cost >= BUDGET:
            over.append(t["id"])
        print("  %-8s %-46s %-10s  blocks=%s"
              % (t["id"], t["relation"][:46], mark, ",".join(sorted(need)) or "-"))
    print("\nover the %.0f s budget: %s" % (BUDGET, over or "none"))
    return 1 if over else 0


if __name__ == "__main__":
    sys.exit(main())
