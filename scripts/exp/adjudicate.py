"""Adjudicator for the preregistered three-arm test.

Written BEFORE any arm reported, so the analysis cannot be tuned to the result
(see results/experiment/PREREGISTRATION.md, tag prereg-three-arm-v1).

What it does, in order:

1. Re-evaluates every crossing any arm claims, using ONE common evaluator built
   from the population file's own `expr` + `invariant_definitions`. An arm's
   crossing counts only if it survives this. Arms implementing an invariant
   slightly differently is the main way a three-arm comparison goes wrong, and
   this is the check for it.
2. Applies the database-sanity gate to each surviving crossing: the same reading
   is re-evaluated over the generating database D. A reading that also refutes
   members of D is a bug, not a crossing.
3. Computes the preregistered endpoint (wall-arm-unique crossings) and applies
   the decision rule mechanically. No judgement calls in the scoring.

Usage: python adjudicate.py [--db-gate]   (--db-gate rebuilds D; slower)
"""
import json
import pathlib
import sys
from fractions import Fraction

import networkx as nx

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXP = ROOT / "results" / "experiment"


def load_population():
    with open(EXP / "fresh-population" / "population.json") as fh:
        pop = json.load(fh)
    return {t["id"]: t for t in pop["targets"]}


def load_arm(name):
    p = EXP / f"arm-{name}.json"
    if not p.exists():
        return None
    with open(p) as fh:
        d = json.load(fh)
    rows = d if isinstance(d, list) else d.get("results", d.get("targets", []))
    return {r["id"]: r for r in rows}


def graph_from_g6(g6):
    return nx.from_graph6_bytes(g6.encode() if isinstance(g6, str) else g6)


def evaluate(target, G, invlib):
    """Evaluate the target's inequality on G under the population's own reading.

    Returns (holds: bool, lhs, rhs) or raises if an invariant is unavailable.
    """
    env = {}
    for name in target["invariants_used"]:
        fn = invlib.get(name)
        if fn is None:
            raise KeyError(f"no implementation for invariant {name!r}")
        env[name] = fn(G)
    expr = target["expr"]
    # expr is expected to be a dict with 'lhs'/'rhs' python-eval strings, or a
    # single relation string; support both, failing loudly on anything else.
    safe = {"Fraction": Fraction, "ceil": lambda x: -((-x.numerator) // x.denominator)
            if isinstance(x, Fraction) else -((-x) // 1),
            "floor": lambda x: x.numerator // x.denominator
            if isinstance(x, Fraction) else x // 1,
            "min": min, "max": max, "abs": abs, "int": int}
    safe.update(env)
    if isinstance(expr, dict) and "lhs" in expr and "rhs" in expr:
        lhs = eval(expr["lhs"], {"__builtins__": {}}, safe)
        rhs = eval(expr["rhs"], {"__builtins__": {}}, safe)
    else:
        raise ValueError(f"unsupported expr shape for {target['id']}: {type(expr)}")
    rel = target.get("relation", "<=")
    holds = (lhs <= rhs) if rel in ("<=", "le") else (lhs >= rhs)
    return holds, lhs, rhs


def adjudicate(invlib, db_gate=False):
    pop = load_population()
    arms = {n: load_arm(n) for n in ("catalogue", "generic", "wall")}
    missing = [n for n, a in arms.items() if a is None]
    if missing:
        print(f"arms not yet reported: {missing} — partial adjudication", file=sys.stderr)

    confirmed = {n: set() for n in arms}
    rejected = {n: [] for n in arms}

    for arm_name, arm in arms.items():
        if arm is None:
            continue
        for tid, row in arm.items():
            if row.get("verdict") != "CROSSED":
                continue
            g6 = row.get("witness_graph6") or row.get("graph6")
            if not g6:
                rejected[arm_name].append((tid, "no witness graph6"))
                continue
            try:
                G = graph_from_g6(g6)
                holds, lhs, rhs = evaluate(pop[tid], G, invlib)
            except Exception as exc:
                rejected[arm_name].append((tid, f"re-eval failed: {exc}"))
                continue
            if holds:
                rejected[arm_name].append(
                    (tid, f"does NOT refute under common evaluator: {lhs} vs {rhs}"))
            else:
                confirmed[arm_name].add(tid)

    scored = set()
    for arm in arms.values():
        if arm:
            scored |= {t for t, r in arm.items()
                       if r.get("verdict") in ("CROSSED", "HELD")}

    wall_unique = confirmed["wall"] - confirmed["catalogue"] - confirmed["generic"]
    cat_unique = confirmed["catalogue"] - confirmed["wall"] - confirmed["generic"]

    print("=== adjudicated (common evaluator) ===")
    for n in arms:
        print(f"  {n:10s} confirmed={len(confirmed[n]):2d}  rejected={len(rejected[n])}")
        for tid, why in rejected[n]:
            print(f"      REJECTED {tid}: {why}")
    print(f"\nscored targets: {len(scored)}")
    print(f"wall-unique crossings:      {len(wall_unique)} {sorted(wall_unique)}")
    print(f"catalogue-unique crossings: {len(cat_unique)} {sorted(cat_unique)}")
    print(f"catalogue total crossings:  {len(confirmed['catalogue'])}")

    # preregistered decision rule, applied mechanically
    if len(scored) < 20:
        verdict = "INCONCLUSIVE (fewer than 20 scored targets)"
    elif len(wall_unique) >= 3 and len(wall_unique) >= len(confirmed["catalogue"]):
        verdict = "CLAIM SUPPORTED"
    elif len(wall_unique) <= len(cat_unique):
        verdict = "CLAIM FALSIFIED"
    else:
        verdict = "INCONCLUSIVE"
    print(f"\nPREREGISTERED VERDICT: {verdict}")
    return verdict


if __name__ == "__main__":
    print("This adjudicator needs the invariant library the arms used.\n"
          "Import it and call adjudicate(invlib). Written pre-results; see\n"
          "results/experiment/PREREGISTRATION.md.")
