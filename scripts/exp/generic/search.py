"""GENERIC ARM -- mechanical counterexample search for the three-arm experiment.

Method (no structural insight, by design):

  * FAM    -- standard random families over a wide order and density range:
              G(n,p), random d-regular, random bipartite, random trees (Pruefer),
              Barabasi-Albert preferential attachment, random geometric.
  * SWEEP  -- near-exhaustive small-graph sweep beyond `D`: every connected graph
              on 9 vertices is a one-vertex extension of a connected graph on 8
              vertices (delete a non-cut vertex), so extending every member of
              `D` at n=8 by one vertex over all 255 non-empty neighbourhoods
              covers n=9 exhaustively up to isomorphism (with multiplicity).
              Base graphs are visited in increasing order of their slack, which
              is a purely mechanical use of the objective.
  * GROW   -- beam search: keep the lowest-slack graphs found at each order and
              extend them by one vertex over sampled neighbourhoods.
  * ANNEAL -- simulated annealing on edge flips and degree-preserving double-edge
              swaps, minimising the target's slack, restarted from many seeds
              over a range of orders.

The work is a deterministic sequence of *units*; a run consumes units until its
CPU budget is spent, and records the index of the next unit, so a later run
resumes the identical trajectory.  Every seed is derived from the target id.

Usage:
    python3 scripts/exp/generic/search.py --target FP-001 --cpu 300 \
        --start-unit 0 --out /path/result.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts", "gen"))

import ginv                                        # noqa: E402

POP = os.path.join(ROOT, "results", "experiment", "fresh-population", "population.json")
DBF = os.path.join(ROOT, "scripts", "gen", "data", "connected_n2_n8.g6")

BASE_SEED = 20260815


# --------------------------------------------------------------------------
# random graph families (all mechanical, no structural design)
# --------------------------------------------------------------------------
def _mk(n):
    return [0] * n


def _add(adj, u, v):
    if u != v:
        adj[u] |= 1 << v
        adj[v] |= 1 << u


def _connect(adj, n, rng):
    """Make connected by adding random edges between components."""
    while True:
        seen = 1
        frontier = 1
        while frontier:
            nxt = 0
            for v in ginv.bits(frontier):
                nxt |= adj[v]
            nxt &= ~seen
            seen |= nxt
            frontier = nxt
        if seen == (1 << n) - 1:
            return adj
        out = [v for v in range(n) if not (seen >> v & 1)]
        ins = [v for v in range(n) if seen >> v & 1]
        _add(adj, rng.choice(ins), rng.choice(out))


def gnp(n, p, rng):
    adj = _mk(n)
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                _add(adj, u, v)
    return _connect(adj, n, rng)


def rand_regular(n, d, rng):
    if (n * d) % 2 or d >= n:
        d = max(1, d - 1)
        if (n * d) % 2:
            d = max(1, d - 1)
    for _ in range(60):
        stubs = []
        for v in range(n):
            stubs += [v] * d
        rng.shuffle(stubs)
        adj = _mk(n)
        ok = True
        for i in range(0, len(stubs) - 1, 2):
            u, v = stubs[i], stubs[i + 1]
            if u == v or (adj[u] >> v & 1):
                ok = False
                break
            _add(adj, u, v)
        if ok:
            return _connect(adj, n, rng)
    return gnp(n, float(d) / max(1, n - 1), rng)


def rand_bipartite(n, p, rng):
    a = rng.randint(1, n - 1)
    adj = _mk(n)
    for u in range(a):
        for v in range(a, n):
            if rng.random() < p:
                _add(adj, u, v)
    # reconnect only inside the bipartition to stay bipartite
    while True:
        seen = 1
        frontier = 1
        while frontier:
            nxt = 0
            for v in ginv.bits(frontier):
                nxt |= adj[v]
            nxt &= ~seen
            seen |= nxt
            frontier = nxt
        if seen == (1 << n) - 1:
            return adj
        out = [v for v in range(n) if not (seen >> v & 1)]
        w = rng.choice(out)
        side = range(a, n) if w < a else range(0, a)
        cand = [v for v in side if seen >> v & 1]
        if not cand:
            cand = [v for v in side]
        _add(adj, w, rng.choice(cand))


def rand_tree(n, rng):
    """Uniform random labelled tree via a Pruefer sequence (heap-free decode)."""
    adj = _mk(n)
    if n <= 2:
        if n == 2:
            _add(adj, 0, 1)
        return adj
    pruefer = [rng.randrange(n) for _ in range(n - 2)]
    deg = [1] * n
    for x in pruefer:
        deg[x] += 1
    leaves = sorted(v for v in range(n) if deg[v] == 1)
    import heapq
    heapq.heapify(leaves)
    for x in pruefer:
        leaf = heapq.heappop(leaves)
        _add(adj, leaf, x)
        deg[x] -= 1
        if deg[x] == 1:
            heapq.heappush(leaves, x)
    a = heapq.heappop(leaves)
    b = heapq.heappop(leaves)
    _add(adj, a, b)
    return adj


def rand_ba(n, mm, rng):
    mm = max(1, min(mm, n - 1))
    adj = _mk(n)
    targets = list(range(mm))
    for i in range(1, mm):
        _add(adj, i, i - 1)
    repeated = list(range(mm))
    for v in range(mm, n):
        chosen = set()
        while len(chosen) < mm:
            chosen.add(rng.choice(repeated) if repeated else rng.randrange(v))
        for t in chosen:
            _add(adj, v, t)
            repeated.append(t)
        repeated += [v] * mm
    return _connect(adj, n, rng)


def rand_geometric(n, r, rng):
    pts = [(rng.random(), rng.random()) for _ in range(n)]
    adj = _mk(n)
    r2 = r * r
    for u in range(n):
        for v in range(u + 1, n):
            dx = pts[u][0] - pts[v][0]
            dy = pts[u][1] - pts[v][1]
            if dx * dx + dy * dy <= r2:
                _add(adj, u, v)
    return _connect(adj, n, rng)


def family_sample(k, rng, n_max):
    """One mechanical random graph; `k` selects the family deterministically."""
    lo = 9
    hi = max(10, n_max)
    n = rng.randint(lo, hi)
    fam = k % 6
    if fam == 0:
        p = rng.choice([0.08, 0.12, 0.18, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.92])
        return gnp(n, p, rng), "G(n,p) p=%.2f n=%d" % (p, n)
    if fam == 1:
        d = rng.randint(2, max(2, min(n - 1, 8)))
        return rand_regular(n, d, rng), "random %d-regular n=%d" % (d, n)
    if fam == 2:
        p = rng.choice([0.2, 0.35, 0.5, 0.7, 0.9])
        return rand_bipartite(n, p, rng), "random bipartite p=%.2f n=%d" % (p, n)
    if fam == 3:
        return rand_tree(n, rng), "random tree n=%d" % n
    if fam == 4:
        mm = rng.randint(1, max(1, min(5, n - 1)))
        return rand_ba(n, mm, rng), "preferential attachment m=%d n=%d" % (mm, n)
    r = rng.choice([0.25, 0.35, 0.45, 0.6])
    return rand_geometric(n, r, rng), "random geometric r=%.2f n=%d" % (r, n)


# --------------------------------------------------------------------------
# annealing
# --------------------------------------------------------------------------
def _connected(n, adj):
    return ginv.is_connected(n, adj)


def anneal(expr, n, seed, steps, deadline, record):
    """Simulated annealing on edge flips + double-edge swaps.  Returns best."""
    rng = random.Random(seed)
    p0 = rng.choice([0.1, 0.2, 0.3, 0.45, 0.6, 0.8])
    adj = gnp(n, p0, rng)
    cur = ginv.slack(expr, ginv.Inv(n, adj))
    record(n, adj, cur)
    if cur < 0:
        return adj, cur
    best_adj, best = list(adj), cur
    T0, T1 = 2.5, 0.03
    for step in range(steps):
        if (step & 31) == 0 and time.process_time() > deadline:
            break
        T = T0 * (T1 / T0) ** (step / max(1, steps - 1))
        mode = rng.random()
        undo = None
        if mode < 0.72:
            u = rng.randrange(n)
            v = rng.randrange(n)
            if u == v:
                continue
            if adj[u] >> v & 1:
                adj[u] &= ~(1 << v)
                adj[v] &= ~(1 << u)
                if not _connected(n, adj):
                    adj[u] |= 1 << v
                    adj[v] |= 1 << u
                    continue
                undo = ("add", u, v)
            else:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
                undo = ("del", u, v)
        else:
            edges = [(u, v) for u in range(n) for v in ginv.bits(adj[u]) if v > u]
            if len(edges) < 2:
                continue
            (a, b), (c, d) = rng.sample(edges, 2)
            if len({a, b, c, d}) < 4:
                continue
            if (adj[a] >> c & 1) or (adj[b] >> d & 1):
                continue
            adj[a] &= ~(1 << b); adj[b] &= ~(1 << a)
            adj[c] &= ~(1 << d); adj[d] &= ~(1 << c)
            adj[a] |= 1 << c; adj[c] |= 1 << a
            adj[b] |= 1 << d; adj[d] |= 1 << b
            if not _connected(n, adj):
                adj[a] &= ~(1 << c); adj[c] &= ~(1 << a)
                adj[b] &= ~(1 << d); adj[d] &= ~(1 << b)
                adj[a] |= 1 << b; adj[b] |= 1 << a
                adj[c] |= 1 << d; adj[d] |= 1 << c
                continue
            undo = ("swap", (a, b, c, d))
        new = ginv.slack(expr, ginv.Inv(n, adj))
        record(n, adj, new)
        if new < 0:
            return adj, new
        delta = new - cur
        if delta <= 0 or rng.random() < math.exp(-float(delta) / T):
            cur = new
            if new < best:
                best, best_adj = new, list(adj)
        else:
            if undo[0] == "add":
                _, u, v = undo
                adj[u] |= 1 << v
                adj[v] |= 1 << u
            elif undo[0] == "del":
                _, u, v = undo
                adj[u] &= ~(1 << v)
                adj[v] &= ~(1 << u)
            else:
                a, b, c, d = undo[1]
                adj[a] &= ~(1 << c); adj[c] &= ~(1 << a)
                adj[b] &= ~(1 << d); adj[d] &= ~(1 << b)
                adj[a] |= 1 << b; adj[b] |= 1 << a
                adj[c] |= 1 << d; adj[d] |= 1 << c
    return best_adj, best


# --------------------------------------------------------------------------
# the search driver
# --------------------------------------------------------------------------
class Search:
    def __init__(self, target, cpu_budget, start_unit=0, prior_cpu=0.0,
                 prior_units=0, verbose=False):
        self.t = target
        self.expr = target["expr"]
        self.budget = cpu_budget
        self.start_unit = start_unit
        self.prior_cpu = prior_cpu
        self.prior_units = prior_units
        self.verbose = verbose
        self.seed = BASE_SEED + int(target["id"].split("-")[1]) * 7919
        self.hit = None
        self.hit_method = None
        self.best = None
        self.best_g6 = None
        self.best_desc = None
        self.beam = {}          # n -> list of (slack, adj)
        self.evals = 0
        self.n_max = 12
        self.d8 = None
        self.method_counts = {}
        self.sweep_bases = 0

    # -- bookkeeping -------------------------------------------------------
    def record(self, n, adj, s, desc=None, method=None):
        self.evals += 1
        if self.best is None or s < self.best:
            self.best = s
            self.best_g6 = ginv.to_graph6(n, adj)
            self.best_desc = desc
        if s < 0 and self.hit is None:
            self.hit = (n, list(adj), s)
            self.hit_method = method or desc
        b = self.beam.setdefault(n, [])
        b.append((s, list(adj)))
        if len(b) > 24:
            b.sort(key=lambda z: z[0])
            del b[12:]

    def ev(self, n, adj, desc=None, method=None):
        s = ginv.slack(self.expr, ginv.Inv(n, adj))
        self.record(n, adj, s, desc, method)
        return s

    # -- probe -------------------------------------------------------------
    def probe(self):
        """Largest order at which one evaluation costs <= 80 ms."""
        rng = random.Random(self.seed ^ 0x5EED)
        # warm-up: the very first evaluation in a fresh process pays for
        # importing numpy (used only to *guess* the spectral bracket), which
        # would otherwise be charged to n = 10 and collapse the order range.
        for _ in range(2):
            try:
                ginv.slack(self.expr, ginv.Inv(9, gnp(9, 0.4, rng)))
            except Exception:
                pass
        best_n = 9
        for n in (10, 12, 14, 16, 20, 24, 28, 32, 36, 40):
            adj = gnp(n, 0.4, rng)
            t0 = time.process_time()
            try:
                ginv.slack(self.expr, ginv.Inv(n, adj))
            except Exception:
                break
            dt = time.process_time() - t0
            adj2 = gnp(n, 0.12, rng)
            t0 = time.process_time()
            ginv.slack(self.expr, ginv.Inv(n, adj2))
            dt = max(dt, time.process_time() - t0)
            if dt > 0.08:
                break
            best_n = n
        self.n_max = best_n
        return best_n

    # -- the D(n=8) base list, ordered by slack (mechanical use of objective)
    def d8_bases(self):
        if self.d8 is not None:
            return self.d8
        codes = [ln.strip() for ln in open(DBF) if ln.strip()]
        out = []
        for c in codes:
            n, adj = ginv.from_graph6(c)
            if n != 8:
                continue
            s = ginv.slack(self.expr, ginv.Inv(n, adj))
            out.append((s, c, adj))
        out.sort(key=lambda z: (z[0], z[1]))
        self.d8 = out
        return out

    # -- units -------------------------------------------------------------
    def unit(self, k, deadline):
        """Run work unit `k`.  Returns True iff the unit ran to completion."""
        kind, arg = self.unit_kind(k)
        self.method_counts[kind] = self.method_counts.get(kind, 0) + 1
        if kind == "FAM":
            rng = random.Random(self.seed + 1000 + arg)
            for j in range(180):
                if (j & 7) == 0 and time.process_time() > deadline:
                    return False
                adj, desc = family_sample(arg * 180 + j, rng, self.n_max)
                n = len(adj)
                self.ev(n, adj, desc, "FAM")
                if self.hit:
                    return True
        elif kind == "ANNEAL":
            ns = [n for n in (9, 10, 11, 12, 13, 14, 16, 18, 20, 24, 28, 32, 36, 40)
                  if n <= self.n_max]
            n = ns[arg % len(ns)]
            anneal(self.expr, n, self.seed + 500000 + arg, 6000, deadline,
                   lambda nn, aa, ss: self.record(nn, aa, ss,
                                                  "anneal n=%d unit=%d" % (n, arg),
                                                  "ANNEAL"))
        elif kind == "SWEEP":
            bases = self.d8_bases()
            B = 20
            lo = arg * B
            if lo >= len(bases):
                return True
            for _, c, adj8 in bases[lo:lo + B]:
                if time.process_time() > deadline:
                    return False
                for mask in range(1, 1 << 8):
                    adj = list(adj8) + [mask]
                    for i in ginv.bits(mask):
                        adj[i] |= 1 << 8
                    self.ev(9, adj, "n=9 exhaustive extension of %s" % c, "SWEEP")
                    if self.hit:
                        return True
                self.sweep_bases += 1
        elif kind == "GROW":
            rng = random.Random(self.seed + 900000 + arg)
            pool = []
            for n, lst in self.beam.items():
                if n >= self.n_max:
                    continue
                for s, adj in sorted(lst, key=lambda z: z[0])[:4]:
                    pool.append((s, n, adj))
            pool.sort(key=lambda z: z[0])
            for s, n, adj0 in pool[:10]:
                if time.process_time() > deadline:
                    return False
                masks = set()
                full = (1 << n) - 1
                if full <= 2047:
                    masks = set(range(1, full + 1))
                else:
                    for v in range(n):
                        masks.add(1 << v)
                    for _ in range(1500):
                        masks.add(rng.randrange(1, full + 1))
                for mask in sorted(masks):
                    adj = list(adj0) + [mask]
                    for i in ginv.bits(mask):
                        adj[i] |= 1 << n
                    self.ev(n + 1, adj, "beam extension of order %d" % n, "GROW")
                    if self.hit:
                        return True
                    if time.process_time() > deadline:
                        return False
        return True

    @staticmethod
    def unit_kind(k):
        """Deterministic unit schedule."""
        if k < 30:
            return "FAM", k
        k -= 30
        cyc = k % 6
        blk = k // 6
        if cyc in (0, 1, 2):
            return "ANNEAL", blk * 3 + cyc
        if cyc == 3:
            return "SWEEP", blk
        if cyc == 4:
            return "GROW", blk
        return "ANNEAL", 100000 + blk

    # -- run ---------------------------------------------------------------
    def run(self):
        t_wall0 = time.time()
        t_cpu0 = time.process_time()
        deadline = t_cpu0 + self.budget
        self.probe()
        k = self.start_unit
        while time.process_time() < deadline and self.hit is None:
            done = True
            try:
                done = self.unit(k, deadline)
            except RecursionError:
                pass
            if done:
                k += 1
            else:
                break
            if k > 400000:
                break
        cpu = time.process_time() - t_cpu0
        return {
            "next_unit": k,
            "sweep_bases_n8_completed": self.sweep_bases,
            "cpu_this_run": cpu,
            "cpu_total": self.prior_cpu + cpu,
            "wall_this_run": time.time() - t_wall0,
            "units_this_run": k - self.start_unit,
            "units_total": self.prior_units + (k - self.start_unit),
            "evals_this_run": self.evals,
            "n_max": self.n_max,
            "method_counts": self.method_counts,
        }


# --------------------------------------------------------------------------
# witness reduction (mechanical: greedy vertex deletion, keep slack < 0)
# --------------------------------------------------------------------------
def shrink(expr, n, adj, budget=60.0):
    """Delete vertices greedily while the graph stays connected and slack < 0.

    Purely mechanical; it only makes the witness cheaper to re-verify (a witness
    with n <= 20 can be re-checked by the exhaustive 2^n backend as well).
    """
    t0 = time.process_time()
    changed = True
    while changed and n > 2 and time.process_time() - t0 < budget:
        changed = False
        for v in range(n):
            sub = [u for u in range(n) if u != v]
            idx = {u: i for i, u in enumerate(sub)}
            a2 = [0] * (n - 1)
            for u in sub:
                for w in ginv.bits(adj[u]):
                    if w != v:
                        a2[idx[u]] |= 1 << idx[w]
            if not ginv.is_connected(n - 1, a2):
                continue
            try:
                s = ginv.slack(expr, ginv.Inv(n - 1, a2))
            except (ZeroDivisionError, KeyError):
                continue
            if s < 0:
                n, adj = n - 1, a2
                changed = True
                break
    return n, adj


# --------------------------------------------------------------------------
# verification of a candidate crossing
# --------------------------------------------------------------------------
def verify(target, n, adj):
    """(a) second code path.  Returns a dict.

    The witness is recomputed by `scripts/gen/invariants.py` (the exhaustive
    `2^n` backend as well, when `n <= 20`) and re-evaluated by
    `scripts/gen/expressions.py`.  Because the shipped `ceil(lambda_1)` follows
    the generator's own convention (see `check_against_gen.py --json`), the arm
    reports its reading under *both* conventions and requires the slack to be
    negative under both, with the generator-convention values matching
    `scripts/gen` exactly.
    """
    import networkx as nx
    import invariants as GEN
    import expressions as EXPR

    out = {}
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for u in range(n):
        for v in ginv.bits(adj[u]):
            if v > u:
                G.add_edge(u, v)

    keep = ginv.SPEC_CONVENTION
    readings = {}
    for conv in ("true", "generator"):
        ginv.SPEC_CONVENTION = conv
        inv = ginv.Inv(n, adj)
        l, r = ginv.lhs_rhs(target["expr"], inv)
        readings[conv] = (l, r, ginv.slack(target["expr"], inv))
    ginv.SPEC_CONVENTION = keep

    out["arm_lhs"] = str(readings[keep][0])
    out["arm_rhs"] = str(readings[keep][1])
    out["arm_slack"] = str(readings[keep][2])
    out["arm_convention"] = keep
    out["arm_lhs_generator_convention"] = str(readings["generator"][0])
    out["arm_rhs_generator_convention"] = str(readings["generator"][1])
    out["arm_slack_generator_convention"] = str(readings["generator"][2])
    out["arm_slack_true_convention"] = str(readings["true"][2])

    backends = ["scal"] + (["brute"] if n <= 20 else [])
    ok = readings["true"][2] < 0 and readings["generator"][2] < 0
    for b in backends:
        vals = GEN.compute(G, backend=b)
        l = EXPR.evaluate(target["expr"]["lhs"], vals)
        r = EXPR.evaluate(target["expr"]["rhs"], vals)
        s = EXPR.slack(target["expr"], vals)
        out["gen_%s_lhs" % b] = str(l)
        out["gen_%s_rhs" % b] = str(r)
        out["gen_%s_slack" % b] = str(s)
        if (l, r) != (readings["generator"][0], readings["generator"][1]) or s >= 0:
            ok = False
    out["second_code_path"] = "PASS" if ok else "FAIL"
    out["connected"] = bool(ginv.is_connected(n, adj))
    out["n"] = n
    out["graph6"] = ginv.to_graph6(n, adj)
    return out


def database_gate(target, sample_gen=1500, seed=20260815):
    """(b) database-sanity gate.

    Re-evaluate the arm's reading of `target` over the whole of `D`.  A reading
    that refutes members of `D` is a bug in the evaluator, not a crossing.  Also
    re-checks a deterministic sample of `D` through the shipped `scripts/gen`
    code path, and reports whether the recorded equality count reproduces.
    """
    import networkx as nx
    import invariants as GEN
    import expressions as EXPR

    codes = [ln.strip() for ln in open(DBF) if ln.strip()]
    viol = []
    eq = 0
    for c in codes:
        n, adj = ginv.from_graph6(c)
        s = ginv.slack(target["expr"], ginv.Inv(n, adj))
        if s < 0:
            viol.append(c)
        elif s == 0:
            eq += 1
    rng = random.Random(seed)
    idx = sorted(rng.sample(range(len(codes)), min(sample_gen, len(codes))))
    viol_gen = []
    for i in idx:
        G = nx.from_graph6_bytes(codes[i].encode())
        vals = GEN.compute(G, backend="brute")
        if EXPR.slack(target["expr"], vals) < 0:
            viol_gen.append(codes[i])
    return {
        "convention": ginv.SPEC_CONVENTION,
        "arm_counterexamples_in_D": len(viol),
        "arm_equality_count_in_D": eq,
        "population_equality_count_in_D": target["equality_count_in_D"],
        "equality_count_reproduces": eq == target["equality_count_in_D"],
        "gen_path_sample": len(idx),
        "gen_path_counterexamples": len(viol_gen),
        "status": "PASS" if (not viol and not viol_gen) else "FAIL",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    ap.add_argument("--cpu", type=float, default=300.0)
    ap.add_argument("--start-unit", type=int, default=0)
    ap.add_argument("--prior-cpu", type=float, default=0.0)
    ap.add_argument("--prior-units", type=int, default=0)
    ap.add_argument("--prior-wall", type=float, default=0.0)
    ap.add_argument("--cap", type=float, default=3600.0)
    ap.add_argument("--out", required=True)
    ap.add_argument("--spec", default="true", choices=("true", "generator"),
                    help="convention for ceil(lambda_1); see ginv.SPEC_CONVENTION")
    args = ap.parse_args()
    ginv.SPEC_CONVENTION = args.spec

    pop = json.load(open(POP))
    target = next(t for t in pop["targets"] if t["id"] == args.target)

    budget = min(args.cpu, max(0.0, args.cap - args.prior_cpu))
    S = Search(target, budget, args.start_unit, args.prior_cpu, args.prior_units)
    stats = S.run()

    res = {
        "id": target["id"],
        "statement": target["statement"],
        "seeds": {
            "base_seed": S.seed,
            "formula": "BASE_SEED(20260815) + 7919 * int(id suffix); "
                       "FAM unit k -> base+1000+k, ANNEAL unit k -> base+500000+k, "
                       "GROW unit k -> base+900000+k, probe -> base XOR 0x5EED",
        },
        "n_max_probed": stats["n_max"],
        "evals_this_run": stats["evals_this_run"],
        "units_total": stats["units_total"],
        "next_unit": stats["next_unit"],
        "method_counts": stats["method_counts"],
        "cpu_seconds": stats["cpu_total"],
        "wall_seconds": args.prior_wall + stats["wall_this_run"],
        "sweep_bases_n8_completed": stats["sweep_bases_n8_completed"],
        "best_slack_found": str(S.best) if S.best is not None else None,
        "best_slack_graph6": S.best_g6,
        "best_slack_desc": S.best_desc,
        "cap_cpu_seconds": args.cap,
        "spec_convention": args.spec,
    }

    if S.hit is not None:
        tv0 = time.process_time()
        n0, adj0, s0 = S.hit
        res["witness_raw_graph6"] = ginv.to_graph6(n0, adj0)
        res["witness_raw_n"] = n0
        n, adj = shrink(target["expr"], n0, adj0)
        v = verify(target, n, adj)
        g = database_gate(target)
        res["verify_cpu_seconds"] = time.process_time() - tv0
        res["verdict"] = "CROSSED" if (v["second_code_path"] == "PASS"
                                       and g["status"] == "PASS"
                                       and v["connected"]) else "GATE-FAIL"
        res["witness_graph6"] = v["graph6"]
        res["witness_n"] = n
        res["witness_lhs"] = v["arm_lhs"]
        res["witness_rhs"] = v["arm_rhs"]
        res["witness_slack"] = v["arm_slack"]
        res["method_found"] = S.hit_method
        res["gate_second_code_path"] = v
        res["gate_database_sanity"] = g
    else:
        res["verdict"] = "HELD" if stats["cpu_total"] >= args.cap - 1 else "BRACKET"
        res["method_found"] = None

    with open(args.out, "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True)
    print(json.dumps({k: res[k] for k in
                      ("id", "verdict", "cpu_seconds", "best_slack_found",
                       "next_unit", "n_max_probed")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
