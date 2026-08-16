"""Runtime and exactness measurement for the hereditary induced invariants.

The v2 design (``results/experiment-v2/DESIGN.md``) requires ``f``, ``b``,
``tree``, ``path`` and ``alpha`` in the emission vocabulary, and requires the
cost to be managed by **capping evaluation order** and using branch and bound
with early exit -- not by dropping the invariants, which is what v1 did.  This
script produces the data the cap is set from:

  * **exactness** -- the branch-and-bound solver is compared against exhaustive
    subset enumeration on every stress graph small enough for the exhaustive run
    to finish inside the cap, i.e. up to ``n = 20``.  (Over ``D2`` itself --
    273,192 graphs, ``n <= 9`` -- the same comparison is run on every member by
    ``crossval.py``.)
  * **runtime** -- the per-graph wall time of the branch-and-bound solver at
    ``n = 20, 30, 40`` on a fixed list of generic stress structures, so that the
    arms' budgets can be set from measurement.

CONTAMINATION CONTRACT
----------------------
The stress graphs are **not** in ``D2``.  This script therefore prints
**timings and agreement flags only**.  No invariant *value* of a non-``D2`` graph
is printed, stored, returned or compared against anything except a second
implementation of the same invariant on the same graph, and there is no code path
in this file by which a candidate inequality could be evaluated on anything.  The
stress list contains no graph named anywhere in this repository's mathematics --
no ``C5[K_m]``, no ``T(n) = L(K_n)``, no Petersen, Kneser, Paley, Moebius-Kantor
or complement thereof.  It is the generic list v1 used: paths, cycles, grids,
hypercubes, circulants, complete multipartite graphs, complete bipartite graphs,
wheels, balanced trees, complete graphs and seeded ``G(n, p)``.

This script is run **before** any candidate exists.

Usage:
    python3 scripts/gen2/bench_hereditary.py            # exactness + runtime
    python3 scripts/gen2/bench_hereditary.py --quick
"""
from __future__ import annotations

import itertools
import signal
import sys
import time
from typing import Callable, Dict, List, Tuple

import networkx as nx

import invariants2 as I

CAP_S = 60          # the project's per-computation cap
EXH_CAP_S = 150     # exhaustive reference cap (CPU s); it is not on the arms' path


class _Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise _Timeout()


def timed(fn: Callable, cap: int) -> Tuple[float, float, object]:
    """(cpu seconds, wall seconds, value); value is None if the cap was hit.

    The cap is on **CPU** time (`ITIMER_PROF`), and CPU time is what the tables
    report, because this box runs several agent sessions at once and wall clock
    under contention would understate the solvers' capability rather than
    measure it.  Wall time is reported alongside so the contention is visible.
    """
    signal.signal(signal.SIGPROF, _alarm)
    signal.setitimer(signal.ITIMER_PROF, cap)
    c0, w0 = time.process_time(), time.time()
    try:
        v = fn()
        dc, dw = time.process_time() - c0, time.time() - w0
    except _Timeout:
        return float(cap), time.time() - w0, None
    finally:
        signal.setitimer(signal.ITIMER_PROF, 0)
    return dc, dw, v


# --------------------------------------------------------------------------
# exhaustive reference: subsets in decreasing size, first hit wins
# --------------------------------------------------------------------------
def exhaustive(adj: List[int], n: int, which: str) -> int:
    """Largest k with a valid induced subgraph of order k, by enumerating every
    subset in decreasing size and stopping at the first hit.

    A subset is rejected on its internal edge count before the component /
    bipartiteness scan runs: an induced forest, tree or path on k vertices has at
    most k-1 edges and an induced bipartite subgraph at most k^2/4, so on dense
    graphs almost every subset dies on one pop-count pass.  This is a speed-up of
    the reference implementation only -- it decides exactly the same predicate.
    """
    pc = I._pc
    if which == "alpha":
        for k in range(n, 0, -1):
            for combo in itertools.combinations(range(n), k):
                S = 0
                for v in combo:
                    S |= 1 << v
                if all(not (adj[v] & S) for v in combo):
                    return k
        return 0
    for k in range(n, 0, -1):
        lim_e = (k - 1) if which in ("f", "tree", "path") else (k * k) // 4
        for combo in itertools.combinations(range(n), k):
            S = 0
            for v in combo:
                S |= 1 << v
            e2 = 0
            md = 0
            for v in combo:
                d = pc(adj[v] & S)
                e2 += d
                if d > md:
                    md = d
            if (e2 >> 1) > lim_e:
                continue
            if which == "path" and md > 2:
                continue
            e, nc, bp, _ = I._scan_A(adj, S, n)
            if which == "b":
                if bp:
                    return k
            elif which == "f":
                if e == k - nc:
                    return k
            elif which == "tree":
                if nc == 1 and e == k - 1:
                    return k
            elif which == "path":
                if nc == 1 and e == k - 1:
                    return k
            else:
                raise ValueError(which)
    return 0


SOLVER = {
    "alpha": lambda adj, n: I.max_independent_bb(adj, (1 << n) - 1, n),
    "f": I.max_induced_forest_bb,
    "b": I.max_induced_bipartite_bb,
    "tree": I.max_induced_tree_bb,
    "path": I.max_induced_path_bb,
}
ORDER = ["alpha", "f", "b", "tree", "path"]


# --------------------------------------------------------------------------
# stress structures (generic; none of them appears in this repo's mathematics)
# --------------------------------------------------------------------------
def _connected_gnp(n: int, p: float, seed: int) -> nx.Graph:
    s = seed
    while True:
        G = nx.gnp_random_graph(n, p, seed=s)
        if nx.is_connected(G):
            return G
        s += 1000003


def stress(n: int) -> List[Tuple[str, nx.Graph]]:
    out: List[Tuple[str, nx.Graph]] = []
    out.append(("path_%d" % n, nx.path_graph(n)))
    out.append(("cycle_%d" % n, nx.cycle_graph(n)))
    out.append(("star_%d" % n, nx.star_graph(n - 1)))
    out.append(("wheel_%d" % n, nx.wheel_graph(n)))
    out.append(("complete_%d" % n, nx.complete_graph(n)))
    out.append(("bintree_%d" % n, nx.balanced_tree(2, {20: 3, 30: 4, 40: 4}[n])))
    a, b = {20: (4, 5), 30: (5, 6), 40: (5, 8)}[n]
    out.append(("grid_%dx%d" % (a, b), nx.convert_node_labels_to_integers(
        nx.grid_2d_graph(a, b))))
    out.append(("circulant_%d_12" % n, nx.circulant_graph(n, [1, 2])))
    out.append(("circulant_%d_1k" % n, nx.circulant_graph(n, [1, n // 4])))
    out.append(("K_%d_%d" % (n // 2, n // 2), nx.complete_bipartite_graph(n // 2, n // 2)))
    out.append(("multipartite_%d" % n, nx.complete_multipartite_graph(*([5] * (n // 5)))))
    if n == 40:
        out.append(("hypercube_Q5", nx.convert_node_labels_to_integers(
            nx.hypercube_graph(5))))
    for j, p in enumerate((0.15, 0.3, 0.5, 0.7)):
        out.append(("gnp_%d_%.2f" % (n, p), _connected_gnp(n, p, 20260816 + 97 * n + j)))
    return [(nm, nx.convert_node_labels_to_integers(G, ordering="sorted"))
            for nm, G in out]


def adj_of(G: nx.Graph) -> Tuple[List[int], int]:
    n = G.number_of_nodes()
    adj = [0] * n
    for u, v in G.edges():
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj, n


# --------------------------------------------------------------------------
def exactness_pass(max_n: int = 20) -> int:
    """Branch-and-bound vs exhaustive enumeration, on stress graphs up to n=20.

    Prints agreement only; no invariant value of a non-D2 graph is emitted.
    """
    print("== exactness: branch-and-bound vs exhaustive 2^n enumeration ==")
    print("   (over D2 itself the same comparison runs on all 273,192 members;")
    print("    see crossval.py.  Values are never printed for non-D2 graphs.)")
    agree = disagree = skipped = 0
    for n in (10, 12, 14, 16, 18, 20):
        gs = [("path_%d" % n, nx.path_graph(n)),
              ("cycle_%d" % n, nx.cycle_graph(n)),
              ("grid", nx.convert_node_labels_to_integers(
                  nx.grid_2d_graph(2, n // 2))),
              ("complete_%d" % n, nx.complete_graph(n)),
              ("bipartite", nx.complete_bipartite_graph(n // 2, n // 2)),
              ("multipartite", nx.complete_multipartite_graph(*([n // 5] * 5))),
              ("circulant", nx.circulant_graph(n, [1, 3])),
              ("wheel", nx.wheel_graph(n)),
              ("gnp_0.15", _connected_gnp(n, 0.15, 424242 + n)),
              ("gnp_0.30", _connected_gnp(n, 0.30, 525252 + n)),
              ("gnp_0.50", _connected_gnp(n, 0.50, 626262 + n)),
              ("gnp_0.70", _connected_gnp(n, 0.70, 727272 + n))]
        line = []
        for name, G in gs:
            G = nx.convert_node_labels_to_integers(G, ordering="sorted")
            if G.number_of_nodes() != n or not nx.is_connected(G):
                continue
            adj, nn = adj_of(G)
            for inv in ORDER:
                _, _, ve = timed(lambda: exhaustive(adj, nn, inv), EXH_CAP_S)
                if ve is None:
                    skipped += 1
                    continue
                _, _, vb = timed(lambda: SOLVER[inv](adj, nn), CAP_S)
                if vb is None:
                    skipped += 1
                    continue
                if ve == vb:
                    agree += 1
                else:
                    disagree += 1
                    line.append("MISMATCH %s on %s (n=%d)" % (inv, name, n))
        print("   n=%2d  agree so far %d, disagree %d, skipped %d %s"
              % (n, agree, disagree, skipped, "; ".join(line)), flush=True)
    print("   RESULT: %d agreements, %d disagreements, %d not finished inside the cap"
          % (agree, disagree, skipped))
    return 0 if disagree == 0 else 1


def runtime_pass(orders=(20, 30, 40)) -> Dict[int, Dict[str, float]]:
    print("== per-graph CPU time of the branch-and-bound solvers (cap %d s CPU) ==" % CAP_S)
    print("   columns: median / 90th percentile / worst, CPU seconds; "
          "'over-cap' counts graphs the solver did not finish inside %d s CPU."
          % CAP_S)
    worst: Dict[int, Dict[str, float]] = {}
    for n in orders:
        gs = stress(n)
        worst[n] = {}
        print("   n=%d  (%d stress graphs)" % (n, len(gs)), flush=True)
        for inv in ORDER:
            times = []
            timeouts = 0
            for name, G in gs:
                adj, nn = adj_of(G)
                dc, dw, v = timed(lambda: SOLVER[inv](adj, nn), CAP_S)
                if v is None:
                    timeouts += 1
                times.append(dc)
            times.sort()
            med = times[len(times) // 2]
            p90 = times[min(len(times) - 1, int(0.9 * len(times)))]
            worst[n][inv] = times[-1]
            print("      %-6s median %8.3f   p90 %8.3f   worst %8.3f   over-cap %d/%d"
                  % (inv, med, p90, times[-1], timeouts, len(times)), flush=True)
    return worst


def main() -> int:
    rc = 0
    if "--runtime-only" not in sys.argv:
        rc |= exactness_pass()
    if "--exactness-only" not in sys.argv:
        runtime_pass((20,) if "--quick" in sys.argv else (20, 30, 40))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
