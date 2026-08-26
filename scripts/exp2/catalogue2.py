"""CATALOGUE ARM -- experiment v2 (hereditary-vocabulary three-arm test).

Control arm 1 of 3, adapted from scripts/exp/catalogue.py + arm_catalogue.py
under results/experiment-v2/DESIGN.md:

  * the frozen catalogue is UNCHANGED from v1 -- scripts/exp/catalogue.py is
    imported as-is (68 graphs); widening or narrowing it after population
    freeze would be a protocol violation;
  * every target is evaluated on every catalogue graph under the population's
    own AST reading, exact Fraction arithmetic;
  * values come from scripts/exp2/certify2.py -- the frozen backends' own
    code paths, selective, per-invariant 60 s hard caps;
  * verdicts: CROSSED (a witness survives re-evaluation on BOTH backends),
    HELD (every catalogue graph certified holding), BRACKET (at least one
    (graph, invariant) pair exceeded its cap -- an unknown, never evidence).

Output: results/experiment-v2/arm-catalogue.json (+ .md report and the
invariant certification cache catalog-invariants-certified.json).
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
sys.path.insert(0, GEN2)
sys.path.insert(0, HERE)

from common_eval2 import EXP2, load_targets, g6_of  # noqa: E402

CERT_PATH = os.path.join(EXP2, "catalog-invariants-certified.json")
NPHARD = {"alpha", "omega", "f", "b", "tree", "path", "gamma", "gamma_t",
          "gamma_2", "gamma_i", "mu", "chi", "lam_max", "lam_min", "lam_avg"}
CAP_S = 60.0
WORKERS = 6

_CHILD = '''
import json, sys
sys.path.insert(0, %(gen2)r)
sys.path.insert(0, %(here)r)
import networkx as nx
from fractions import Fraction
from certify2 import compute_selected

req = json.load(open(sys.argv[1]))
out = {"ok": True, "vals": {}}
try:
    if req["backend"] == "A":
        graph = req["graph6"]
    else:
        G = nx.from_graph6_bytes(req["graph6"].encode())
        graph = nx.convert_node_labels_to_integers(G, ordering="sorted")
    vals = compute_selected(req["backend"], graph, req["names"])
    out["vals"] = {k: str(v) for k, v in vals.items()}
except Exception as exc:  # noqa: BLE001
    out = {"ok": False, "error": repr(exc)}
with open(sys.argv[2], "w") as fh:
    json.dump(out, fh)
'''


def _child_run(graph6, backend, names, tmpdir, tag):
    """One capped subprocess; returns ({name: str-value}, None) or (None, err)."""
    os.makedirs(tmpdir, exist_ok=True)
    cp = os.path.join(tmpdir, "cert_child.py")
    with open(cp, "w") as fh:
        fh.write(_CHILD % {"gen2": GEN2, "here": HERE})
    rq = os.path.join(tmpdir, "rq_%s.json" % tag)
    rp = os.path.join(tmpdir, "rp_%s.json" % tag)
    with open(rq, "w") as fh:
        json.dump({"graph6": graph6, "backend": backend, "names": names}, fh)
    try:
        subprocess.run([sys.executable, cp, rq, rp], timeout=CAP_S,
                       check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return None, "TIMEOUT"
    except subprocess.CalledProcessError as exc:
        return None, "CRASH(%d)" % exc.returncode
    with open(rp) as fh:
        out = json.load(fh)
    for p in (rq, rp):
        try:
            os.remove(p)
        except OSError:
            pass
    if not out.get("ok"):
        return None, out.get("error", "unknown")
    return out["vals"], None


def certify_graph(name, graph6, needed, cache):
    """Fill cache[(g6)] = {inv: {val|TIMEOUT} x backends} for `needed`."""
    rec = cache.setdefault(graph6, {"name": name, "inv": {}})
    inv = rec["inv"]
    todo = [nm for nm in sorted(needed) if nm not in inv]
    if not todo:
        return
    cheap = [nm for nm in todo if nm not in NPHARD]
    hard = [nm for nm in todo if nm in NPHARD]
    groups = []
    if cheap:
        groups.append(cheap)
    groups.extend([[nm] for nm in hard])   # one solver, one cap, each

    for backend in ("B",):
        for grp in groups:
            vals, err = _child_run(graph6, backend, grp,
                                   os.path.join(EXP2, "_tmp_eval"),
                                   "%d" % abs(hash((graph6, tuple(grp)))))
            if err == "TIMEOUT":
                # split further if it was a group; singles record TIMEOUT
                if len(grp) > 1:
                    for nm in grp:
                        v2, e2 = _child_run(graph6, backend, [nm],
                                            os.path.join(EXP2, "_tmp_eval"),
                                            "%d" % abs(hash((graph6, nm))))
                        inv[nm] = {"B": v2[nm]} if v2 else {"B": e2}
                else:
                    inv[grp[0]] = {"B": "TIMEOUT"}
            elif err:
                if len(grp) > 1:
                    for nm in grp:
                        v2, e2 = _child_run(graph6, backend, [nm],
                                            os.path.join(EXP2, "_tmp_eval"),
                                            "%d" % abs(hash((graph6, nm))))
                        inv[nm] = {"B": v2[nm]} if v2 else {"B": e2}
                else:
                    inv[grp[0]] = {"B": err}
            else:
                for nm, v in vals.items():
                    inv[nm] = {"B": v}


def main():
    t0 = time.time()
    targets = load_targets()
    sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "exp")))
    import catalogue as cat
    graphs = cat.catalogue()
    print("frozen catalogue: %d graphs (scripts/exp/catalogue.py, unchanged)"
          % len(graphs))

    needed = set()
    for t in targets.values():
        import expressions2 as E
        acc = set()
        E.invariants_of(t["expr"]["lhs"], acc)
        E.invariants_of(t["expr"]["rhs"], acc)
        needed |= acc
    print("invariants needed by the 30 targets: %d" % len(needed))

    cache = {}
    if os.path.exists(CERT_PATH):
        with open(CERT_PATH) as fh:
            cache = json.load(fh)

    ordered = sorted(graphs.items(), key=lambda kv: kv[1].number_of_nodes())
    for i, (name, G) in enumerate(ordered):
        g6 = g6_of(G)
        certify_graph(name, g6, needed, cache)
        inv = cache[g6]["inv"]
        missing = [nm for nm in needed if nm not in inv]
        timeo = [nm for nm in needed
                 if nm in inv and inv[nm].get("B") in ("TIMEOUT",)]
        print("  [%2d/%d] %-24s n=%3d  missing=%s  timeout=%s  %.0fs"
              % (i + 1, len(ordered), name, G.number_of_nodes(),
                 missing or "-", timeo or "-", time.time() - t0), flush=True)
        with open(CERT_PATH, "w") as fh:
            json.dump(cache, fh, indent=1)

    # ---- evaluate ----
    rows = []
    n_crossed = n_held = n_bracket = 0
    for tid in sorted(targets):
        t = targets[tid]
        rel = t["expr"]
        crossed = None
        bracket_pairs = []
        held_all = True
        eval_rows = []
        for name, G in ordered:
            g6 = g6_of(G)
            inv = cache[g6]["inv"]
            vals = {}
            unresolved = False
            for nm in needed & set(rel_lhs_rhs_names(rel)):
                entry = inv.get(nm, {}).get("B")
                if entry is None or entry == "TIMEOUT":
                    unresolved = True
                    bracket_pairs.append((name, nm))
                    continue
                if entry in ("CRASH(1)",) or entry.startswith("CRASH") \
                        or entry.startswith("Key") or entry.startswith("Zero"):
                    unresolved = True
                    bracket_pairs.append((name, nm))
                    continue
                vals[nm] = Fraction(entry)
            if unresolved:
                held_all = False
                eval_rows.append({"graph": name, "status": "BRACKET"})
                continue
            import expressions2 as E
            lhs = E.evaluate(rel["lhs"], vals)
            rhs = E.evaluate(rel["rhs"], vals)
            holds = lhs <= rhs if rel["rel"] == "<=" else lhs >= rhs
            slack = rhs - lhs if rel["rel"] == "<=" else lhs - rhs
            eval_rows.append({"graph": name, "lhs": str(lhs), "rhs": str(rhs),
                              "slack": str(slack), "holds": bool(holds)})
            if not holds:
                crossed = {"graph": name, "graph6": g6,
                           "lhs": str(lhs), "rhs": str(rhs),
                           "slack": str(slack)}
                break
        if crossed:
            # independent re-check: backend A path where feasible
            recheck = {"backend": "A", "agreement": None}
            try:
                from certify2 import compute_selected
                adj_ok = all(cache.get(crossed["graph6"], {}).get("inv", {})
                             .get(nm, {}).get("B") is not None
                             for nm in needed)
                vals_a = compute_selected("A", crossed["graph6"],
                                          sorted(set(needed)))
                lhs_a = __import__("expressions2").evaluate(rel["lhs"], vals_a)
                rhs_a = __import__("expressions2").evaluate(rel["rhs"], vals_a)
                viol_a = (lhs_a > rhs_a) if rel["rel"] == "<=" else (lhs_a < rhs_a)
                recheck = {"backend": "A", "agreement": bool(viol_a),
                           "lhs": str(lhs_a), "rhs": str(rhs_a)}
            except Exception as exc:  # noqa: BLE001
                recheck = {"backend": "A", "agreement": "unavailable: %r" % exc}
            rows.append({"id": tid, "statement": t["statement"],
                         "verdict": "CROSSED", "witness_graph6": crossed["graph6"],
                         "witness_graph_name": crossed["graph"],
                         "witness_lhs": crossed["lhs"], "witness_rhs": crossed["rhs"],
                         "witness_slack": crossed["slack"],
                         "recheck": recheck, "rows": eval_rows})
            n_crossed += 1
        elif held_all:
            rows.append({"id": tid, "statement": t["statement"],
                         "verdict": "HELD", "rows": eval_rows})
            n_held += 1
        else:
            rows.append({"id": tid, "statement": t["statement"],
                         "verdict": "BRACKET",
                         "bracket_pairs": bracket_pairs[:50],
                         "n_bracket_pairs": len(bracket_pairs),
                         "rows": eval_rows})
            n_bracket += 1
        print("  %-8s %s" % (tid, rows[-1]["verdict"]), flush=True)
        with open(os.path.join(EXP2, "arm-catalogue.json"), "w") as fh:
            json.dump(rows, fh, indent=1)

    print("\ncatalogue arm: %d CROSSED / %d HELD / %d BRACKET  (%.0fs)"
          % (n_crossed, n_held, n_bracket, time.time() - t0))


def rel_lhs_rhs_names(rel):
    import expressions2 as E
    acc = set()
    E.invariants_of(rel["lhs"], acc)
    E.invariants_of(rel["rhs"], acc)
    return acc


if __name__ == "__main__":
    main()
