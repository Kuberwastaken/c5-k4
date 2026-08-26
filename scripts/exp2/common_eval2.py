"""Shared exact evaluator for experiment v2's arms and adjudicator.

ONE evaluation path, built on the generator's own machinery:

  * invariants come from ``scripts/gen2/invariants2.compute`` (backend A takes a
    graph6 string, backend B takes a networkx graph or graph6 string); both
    return all 51 vocabulary invariants as exact int/Fraction;
  * relations are the population file's own ASTs, evaluated by
    ``scripts/gen2/expressions2.check`` / ``slack`` in Fraction arithmetic.

The adjudicator uses backend B as its independent recomputation path precisely
because backend A is what the generator swept with at freeze time; see METHOD
v1.7 R4 for why sharing no code matters.

Every solver-backed value is computed inside a subprocess with a hard wall
cap (METHOD standing rule 3: 60 s).  A pair that exceeds the cap raises
`SolverTimeout`; callers must turn that into a BRACKET, never a guess.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
GEN2 = os.path.abspath(os.path.join(HERE, "..", "gen2"))
if GEN2 not in sys.path:
    sys.path.insert(0, GEN2)

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
POP_PATH = os.path.join(ROOT, "results", "experiment-v2",
                        "population", "population.json")
EXP2 = os.path.join(ROOT, "results", "experiment-v2")

DEFAULT_CAP_S = 60.0
PY = sys.executable


class SolverTimeout(Exception):
    """A solver-backed invariant exceeded its hard cap."""


# --------------------------------------------------------------------------
# population
# --------------------------------------------------------------------------

def load_population():
    with open(POP_PATH) as fh:
        return json.load(fh)


def load_targets():
    return {t["id"]: t for t in load_population()["targets"]}


# --------------------------------------------------------------------------
# in-process exact evaluation (small graphs only: no solver blowup risk)
# --------------------------------------------------------------------------

def values_for(code_or_graph, backend, names):
    import invariants2 as I
    vals = I.compute(code_or_graph, backend)
    return {k: vals[k] for k in names}


def eval_relation(target, vals):
    """Returns (holds, lhs, rhs) as exact Fractions for the target's AST."""
    import expressions2 as E
    lhs = E.evaluate(target["expr"]["lhs"], vals)
    rhs = E.evaluate(target["expr"]["rhs"], vals)
    holds = lhs <= rhs if target["expr"]["rel"] == "<=" else lhs >= rhs
    return holds, lhs, rhs


def slack_of(target, vals):
    import expressions2 as E
    return E.slack(target["expr"], vals)


def evaluate_target_on_graph(target, code_or_graph, backend="B"):
    """Exact evaluation of one target on one graph. Raises SolverTimeout if a
    hereditary/domination solver would exceed the cap -- call sites decide
    between a subprocess retry and a BRACKET."""
    names = sorted(target_invariants(target))
    # cheap invariants first: n gates everything else
    vals = values_for(code_or_graph, backend, names)
    return eval_relation(target, vals)


def target_invariants(target):
    import expressions2 as E
    acc = set()
    E.invariants_of(target["expr"]["lhs"], acc)
    E.invariants_of(target["expr"]["rhs"], acc)
    return acc


# --------------------------------------------------------------------------
# subprocess evaluation with a hard wall cap (solver safety)
# --------------------------------------------------------------------------

_CHILD_TEMPLATE = '''\
import json, sys
from fractions import Fraction
sys.path.insert(0, %(gen2)r)
import invariants2 as I
import expressions2 as E

req = json.load(open(sys.argv[1]))
out = {"ok": True}
try:
    if req["backend"] == "A":
        vals = dict(I.compute(req["graph6"], "A"))
    else:
        import networkx as nx
        G = nx.from_graph6_bytes(req["graph6"].encode())
        G = nx.convert_node_labels_to_integers(G, ordering="sorted")
        vals = dict(I.compute(G, "B"))
    rel = req["relation"]
    lhs = E.evaluate(rel["lhs"], vals)
    rhs = E.evaluate(rel["rhs"], vals)
    holds = lhs <= rhs if rel["rel"] == "<=" else lhs >= rhs
    sl = rhs - lhs if rel["rel"] == "<=" else lhs - rhs
    out.update(holds=bool(holds), lhs=str(lhs), rhs=str(rhs), slack=str(sl),
               vals={k: str(v) for k, v in vals.items() if k in req["names"]})
except Exception as exc:  # noqa: BLE001 - reported, never fatal here
    out = {"ok": False, "error": repr(exc)}
with open(sys.argv[2], "w") as fh:
    json.dump(out, fh)
'''


def _run_child(graph6, relation, names, backend, cap_s, tmpdir):
    os.makedirs(tmpdir, exist_ok=True)
    tag = "%d" % os.getpid()
    req = os.path.join(tmpdir, "req_%s.json" % tag)
    rep = os.path.join(tmpdir, "rep_%s.json" % tag)
    if os.path.exists(rep):
        os.remove(rep)
    child_src = _CHILD_TEMPLATE % {"gen2": GEN2}
    child_path = os.path.join(tmpdir, "eval_child.py")
    with open(child_path, "w") as fh:
        fh.write(child_src)
    with open(req, "w") as fh:
        json.dump({"graph6": graph6, "relation": relation,
                   "names": sorted(names), "backend": backend}, fh)
    cmd = [PY, child_path, req, rep]
    t0 = time.time()
    try:
        subprocess.run(cmd, timeout=cap_s, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise SolverTimeout("cap %.0fs exceeded (%s)" % (cap_s, graph6))
    with open(rep) as fh:
        out = json.load(fh)
    for p in (req, rep):
        try:
            os.remove(p)
        except OSError:
            pass
    if not out.get("ok"):
        raise RuntimeError(out.get("error"))
    out["cpu_wall_s"] = round(time.time() - t0, 3)
    out["lhs"] = Fraction(out["lhs"])
    out["rhs"] = Fraction(out["rhs"])
    out["slack"] = Fraction(out["slack"])
    return out


def evaluate_capped(target, graph6, backend="B", cap_s=DEFAULT_CAP_S,
                    tmpdir=None):
    """Evaluate one target on one graph6 inside a capped subprocess.

    Returns the child dict {holds, lhs, rhs, slack, vals,...}. Raises
    SolverTimeout on cap exceedance."""
    tmpdir = tmpdir or os.path.join(EXP2, "_tmp_eval")
    return _run_child(graph6, target["expr"], target_invariants(target),
                      backend, cap_s, tmpdir)


def g6_of(G):
    import networkx as nx
    if not nx.is_connected(G):
        raise ValueError("unconnected graph")
    return "".join(nx.to_graph6_bytes(G, header=False).decode().split())
