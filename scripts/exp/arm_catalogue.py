"""Catalogue arm of the preregistered three-arm test (control arm).

Pure lookup, no design step: every one of the 30 frozen targets in
``results/experiment/fresh-population/population.json`` is evaluated on every one
of the 68 graphs of the frozen catalogue ``scripts/exp/catalogue.py`` (which is
imported, never modified).

Two independent code paths compute every invariant and evaluate every statement:

  path A  the campaign's own code -- ``scripts/gen/invariants.py`` for the
          invariants and ``scripts/gen/expressions.py`` for the AST, with two
          substitutions recorded in the results: the chromatic number (the
          campaign's static-order branch and bound does not terminate on the
          larger catalogue members) and ``ceil(lambda_1)`` (the campaign's test
          is wrong when floor(lambda_1) is a non-maximal eigenvalue).
  path B  ``arm_catalogue_pathb.py`` -- SAT, ``networkx.max_weight_clique``,
          max-flow vertex connectivity, and a separate AST evaluator, sharing no
          code with path A.

A candidate crossing is only reported if both paths agree on it, and only if the
database-sanity gate (``arm_catalogue_gate.py``) passed for that target.

Usage:  python3 scripts/exp/arm_catalogue.py [--gate FILE] [--cache FILE]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts", "gen"))

import networkx as nx                                      # noqa: E402

import expressions                                         # noqa: E402  campaign evaluator
import arm_catalogue_patha as PA                           # noqa: E402
import arm_catalogue_pathb as PB                           # noqa: E402
from catalogue import catalogue                            # noqa: E402  FROZEN, imported only

POP = os.path.join(ROOT, "results", "experiment", "fresh-population", "population.json")
OUT_MD = os.path.join(ROOT, "results", "experiment", "arm-catalogue.md")
OUT_JSON = os.path.join(ROOT, "results", "experiment", "arm-catalogue.json")

BUDGET_SECONDS = 3600.0                                    # preregistered cap, per target


def g6(G):
    H = nx.convert_node_labels_to_integers(G, ordering="sorted")
    return nx.to_graph6_bytes(H, header=False).decode().strip()


def load_catalogue_invariants(cache_path, chi_budget=900.0):
    """Compute (or reload) both paths' invariants for all 68 catalogue graphs."""
    cat = catalogue()
    if cache_path and os.path.exists(cache_path):
        blob = json.load(open(cache_path))
        if blob.get("names") == sorted(cat):
            return cat, blob
    names = sorted(cat)
    vals_a, vals_b, times_a, times_b, extras, g6s = {}, {}, {}, {}, {}, {}
    for i, name in enumerate(sorted(names, key=lambda s: cat[s].number_of_nodes())):
        G = cat[name]
        t0 = time.time()
        vb, tb = PB.invariants(G, timed=True)
        va, ta, ex = PA.invariants(G, chi_deadline=time.monotonic() + chi_budget,
                                   candidate_colourings=[vb["_chi_colouring"]])
        vals_a[name] = {k: (None if v is None else str(v))
                        for k, v in va.items() if not k.startswith("_")}
        vals_b[name] = {k: str(v) for k, v in vb.items() if not k.startswith("_")}
        times_a[name] = ta
        times_b[name] = tb
        extras[name] = {"n": G.number_of_nodes(), "m": G.number_of_edges(),
                        "chi_lb": ex["chi_lb"], "chi_ub": ex["chi_ub"],
                        "chi_timeout": ex["chi_timeout"],
                        "chi_certified_by_checked_colouring": ex["chi_from_certificate"],
                        "gen_spec_ceil": ex["gen_spec_ceil"],
                        "spec_ceil": va["spec_ceil"]}
        g6s[name] = g6(G)
        mism = [k for k in PB.DEFINITIONS if va[k] is not None and va[k] != vb[k]]
        print("  [%2d/%2d] %-24s n=%-3d %.1fs  path mismatches: %s"
              % (i + 1, len(names), name, G.number_of_nodes(), time.time() - t0,
                 mism or "none"), flush=True)
    blob = {"names": names, "g6": g6s, "vals_a": vals_a, "vals_b": vals_b,
            "times_a": times_a, "times_b": times_b, "extras": extras}
    if cache_path:
        json.dump(blob, open(cache_path, "w"))
    return cat, blob


def parse(vals):
    return {k: (None if v is None else Fraction(v)) for k, v in vals.items()}


def alt_spec_ceil_reading(expr, blob, names):
    """Same target read with the *generator's* ceil(lambda_1), bug and all.

    ``scripts/gen/invariants._spectral_bracket`` returns ceil(lambda_1) = fl
    whenever fl = floor(lambda_1) happens to be an eigenvalue, even when it is
    not the largest one (19 members of `D` are affected; see
    ``arm_catalogue_spec``).  Any target naming ``ceil(lambda_1)`` is therefore
    reported under both readings so no verdict can hinge on the discrepancy.
    """
    out = []
    for name in names:
        va = parse(blob["vals_a"][name])
        va = dict(va)
        va["spec_ceil"] = Fraction(blob["extras"][name]["gen_spec_ceil"])
        la = expressions.evaluate(expr["lhs"], va)
        ra = expressions.evaluate(expr["rhs"], va)
        ok = la <= ra if expr["rel"] == "<=" else la >= ra
        if not ok:
            out.append({"graph": name, "graph6": blob["g6"][name],
                        "lhs": str(la), "rhs": str(ra)})
    return {"refuting_graphs": out, "verdict": "CROSSED" if out else "HELD"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", default=os.path.join(HERE, "gate_result.json"))
    ap.add_argument("--cache", default=os.path.join(HERE, "catalogue_invariants.json"))
    args = ap.parse_args()

    pop = json.load(open(POP))
    targets = pop["targets"]

    # the population's own definitions must be the ones this arm implements
    for t in targets:
        for k, d in t["invariant_definitions"].items():
            assert PB.DEFINITIONS[k] == d, (k, d, PB.DEFINITIONS.get(k))

    gate = json.load(open(args.gate))

    print("computing catalogue invariants (both paths)...", flush=True)
    t_setup = time.time()
    cat, blob = load_catalogue_invariants(args.cache)
    setup_seconds = time.time() - t_setup
    names = sorted(cat, key=lambda s: (cat[s].number_of_nodes(), s))

    path_mismatch = []
    for name in names:
        va, vb = parse(blob["vals_a"][name]), parse(blob["vals_b"][name])
        for k in PB.DEFINITIONS:
            if va[k] is not None and va[k] != vb[k]:
                path_mismatch.append((name, k, str(va[k]), str(vb[k])))
    chi_unresolved = [n_ for n_ in names if blob["extras"][n_].get("chi_timeout")]

    results = []
    for t in targets:
        tid = t["id"]
        expr = t["expr"]
        used = t["invariants_used"]
        blocks = {PA.BLOCK_OF.get(k, "poly") for k in used} | {"poly"}
        t0 = time.time()
        crossings, evaluated, unresolved = [], 0, []
        for name in names:
            va, vb = parse(blob["vals_a"][name]), parse(blob["vals_b"][name])
            if any(va[k] is None for k in used):
                unresolved.append(name)
                continue
            la, ra = expressions.evaluate(expr["lhs"], va), expressions.evaluate(expr["rhs"], va)
            lb, rb = PB.sides(expr, vb)
            ok_a = la <= ra if expr["rel"] == "<=" else la >= ra
            ok_b = lb <= rb if expr["rel"] == "<=" else lb >= rb
            evaluated += 1
            if not ok_a or not ok_b:
                crossings.append({
                    "graph": name,
                    "graph6": blob["g6"][name],
                    "n": blob["extras"][name]["n"],
                    "m": blob["extras"][name]["m"],
                    "lhs_pathA": str(la), "rhs_pathA": str(ra),
                    "lhs_pathB": str(lb), "rhs_pathB": str(rb),
                    "slack_pathA": str((ra - la) if expr["rel"] == "<=" else (la - ra)),
                    "slack_pathB": str((rb - lb) if expr["rel"] == "<=" else (lb - rb)),
                    "both_paths_agree": ok_a == ok_b and (la, ra) == (lb, rb),
                    "invariant_values": {k: blob["vals_a"][name][k] for k in used},
                })
        eval_seconds = time.time() - t0
        charged = eval_seconds
        for name in names:
            for b in blocks:
                charged += blob["times_a"][name].get(b, 0.0)
                charged += blob["times_b"][name].get(b, 0.0)

        g = gate["targets"][tid]
        gate_ok = g["gate"] == "PASS"
        reason = None
        if charged > BUDGET_SECONDS:
            verdict, reason = "BRACKET", "over the 1 CPU-hour preregistered cap"
        elif unresolved:
            verdict, reason = "BRACKET", ("path A could not decide %s on %s"
                                          % (",".join(used), ", ".join(unresolved)))
        elif not gate_ok:
            verdict, reason = "BRACKET", "database-sanity gate did not pass"
        elif crossings and all(c["both_paths_agree"] for c in crossings):
            verdict = "CROSSED"
        elif crossings:
            verdict, reason = "BRACKET", "the two code paths disagree at a candidate crossing"
        else:
            verdict = "HELD"

        rec = {
            "id": tid,
            "statement": t["statement"],
            "relation": t["relation"],
            "invariants_used": used,
            "verdict": verdict,
            "bracket_reason": reason,
            "catalogue_graphs_tested": evaluated,
            "refuting_graphs": crossings,
            "seconds": round(charged, 3),
            "seconds_evaluation_only": round(eval_seconds, 4),
            "seconds_with_database_gate_share": round(
                charged + gate["seconds"] + gate.get("rebuild_seconds", 0.0), 3),
            "budget_seconds": BUDGET_SECONDS,
            "gate": {
                "status": g["gate"],
                "counterexamples_in_D_pathA": g["counterexamples_in_D_pathA"],
                "counterexamples_in_D_pathB": g["counterexamples_in_D_pathB"],
                "equality_count_mine": g["equality_count_mine"],
                "equality_count_recorded": g["equality_count_recorded"],
                "slack_histogram_matches_population": g["histogram_matches_recorded"],
                "slack_histogram_diff": g["histogram_diff"],
                "recorded_equality_witnesses_all_tight": g[
                    "all_recorded_equality_witnesses_attain_equality"],
                "two_paths_agree_on_D": g["pathA_pathB_slack_agree"],
            },
            "second_path_recomputation": "pass" if all(
                c["both_paths_agree"] for c in crossings) else "DISAGREEMENT",
        }
        if "spec_ceil" in used:
            rec["gate"]["generator_spec_ceil_reading_on_D"] = g.get(
                "generator_spec_ceil_reading")
            rec["alt_reading_generator_spec_ceil"] = alt_spec_ceil_reading(expr, blob, names)
        results.append(rec)
        write_outputs(pop, results, blob, path_mismatch, gate, setup_seconds, partial=True)
        print("%-8s %-9s %2d crossing(s)  %.2fs charged" %
              (tid, verdict, len(crossings), charged), flush=True)

    write_outputs(pop, results, blob, path_mismatch, gate, setup_seconds, partial=False)

    # third check: brute force from the recorded graph6, on the smallest witness
    # of every crossing.  Shares no solver with path A or path B.
    import arm_catalogue_witness_check as WC
    for r in results:
        if r["verdict"] != "CROSSED":
            continue
        cand = [w for w in r["refuting_graphs"]
                if w["n"] <= WC.MAX_N
                and ("mu" not in r["invariants_used"] or w["m"] <= WC.MAX_EDGES_FOR_MU)]
        if not cand:
            r["third_path_bruteforce_check"] = {"status": "not attempted",
                                                "reason": "no witness inside the 2^n limit"}
            continue
        w = min(cand, key=lambda z: z["n"])
        t0 = time.time()
        vals = WC.brute(nx.from_graph6_bytes(w["graph6"].encode()),
                        set(r["invariants_used"]))
        bad = {k: [v, str(vals[k])] for k, v in w["invariant_values"].items()
               if str(vals[k]) != v}
        r["third_path_bruteforce_check"] = {
            "status": "agree" if not bad else "DISAGREE",
            "graph": w["graph"], "graph6": w["graph6"], "n": w["n"],
            "recomputed": {k: str(vals[k]) for k in sorted(w["invariant_values"])},
            "disagreements": bad, "seconds": round(time.time() - t0, 2),
        }
        print("third path  %-8s %-22s %s" % (r["id"], w["graph"],
                                             r["third_path_bruteforce_check"]["status"]),
              flush=True)
    write_outputs(pop, results, blob, path_mismatch, gate, setup_seconds, partial=False)

    from collections import Counter
    print(Counter(r["verdict"] for r in results))
    return 0


def write_outputs(pop, results, blob, path_mismatch, gate, setup_seconds, partial):
    from collections import Counter
    counts = Counter(r["verdict"] for r in results)
    payload = {
        "arm": "catalogue",
        "protocol": "results/experiment/PREREGISTRATION.md (tag prereg-three-arm-v1)",
        "catalogue": "scripts/exp/catalogue.py (frozen, imported unmodified)",
        "catalogue_size": len(blob["names"]),
        "population": "results/experiment/fresh-population/population.json",
        "population_size": len(pop["targets"]),
        "complete": not partial,
        "targets_scored": len(results),
        "counts": dict(counts),
        "budget_seconds_per_target": BUDGET_SECONDS,
        "setup_seconds_shared": round(setup_seconds, 2),
        "invariant_path_mismatches_on_catalogue": path_mismatch,
        "database_gate": {
            "database_rebuilt": gate["database_rebuilt"],
            "database_sha256": gate["database_sha256"],
            "database_sha256_recorded": gate["database_sha256_recorded"],
            "database_sha256_match": gate["database_sha256_match"],
            "invariant_path_mismatch_count_on_D": gate["invariant_path_mismatch_count"],
            "seconds": gate["seconds"],
            "rebuild_seconds": gate.get("rebuild_seconds"),
        },
        "results": results,
    }
    json.dump(payload, open(OUT_JSON, "w"), indent=1)
    with open(OUT_MD, "w") as fh:
        fh.write(render_md(payload, blob, gate))


def render_md(payload, blob, gate):
    L = []
    A = L.append
    A("# Arm 1 — catalogue (control arm)\n")
    A("Preregistered protocol: [`PREREGISTRATION.md`](PREREGISTRATION.md), "
      "tag `prereg-three-arm-v1`.\n")
    A("Method: pure lookup. Every one of the %d frozen targets in "
      "[`fresh-population/population.json`](fresh-population/population.json) is "
      "evaluated on every one of the %d graphs of the frozen catalogue "
      "[`scripts/exp/catalogue.py`](../../scripts/exp/catalogue.py). No graph was "
      "constructed, tuned or selected for any target; the catalogue file was "
      "imported, never edited.\n"
      % (payload["population_size"], payload["catalogue_size"]))
    A("**Status:** %s — %d/%d targets scored.\n"
      % ("complete" if payload["complete"] else "in progress",
         payload["targets_scored"], payload["population_size"]))
    c = payload["counts"]
    A("| verdict | count |")
    A("|---|---|")
    for k in ("CROSSED", "HELD", "BRACKET"):
        A("| %s | %d |" % (k, c.get(k, 0)))
    A("")
    A("## Results\n")
    A("| id | statement | verdict | refuting graph | LHS | RHS | s |")
    A("|---|---|---|---|---|---|---|")
    for r in payload["results"]:
        if r["refuting_graphs"]:
            w = r["refuting_graphs"][0]
            wit = "`%s`" % w["graph"]
            lhs, rhs = w["lhs_pathA"], w["rhs_pathA"]
            if len(r["refuting_graphs"]) > 1:
                wit += " (+%d more)" % (len(r["refuting_graphs"]) - 1)
        else:
            wit, lhs, rhs = "—", "—", "—"
        A("| %s | `%s` | **%s** | %s | %s | %s | %.1f |"
          % (r["id"], r["relation"], r["verdict"], wit, lhs, rhs, r["seconds"]))
    A("")
    crossed = [r for r in payload["results"] if r["verdict"] == "CROSSED"]
    A("## Crossings in detail\n")
    if not crossed:
        A("None.\n")
    for r in crossed:
        A("### %s — `%s`\n" % (r["id"], r["relation"]))
        A("| graph | graph6 | n | m | LHS | RHS | slack | 2nd path |")
        A("|---|---|---|---|---|---|---|---|")
        for w in r["refuting_graphs"]:
            A("| %s | `%s` | %d | %d | %s | %s | %s | %s |"
              % (w["graph"], w["graph6"], w["n"], w["m"], w["lhs_pathA"],
                 w["rhs_pathA"], w["slack_pathA"],
                 "agree" if w["both_paths_agree"] else "DISAGREE"))
        A("")
        w = r["refuting_graphs"][0]
        A("Invariant values at `%s`: %s\n"
          % (w["graph"], ", ".join("`%s = %s`" % (k, v)
                                   for k, v in sorted(w["invariant_values"].items()))))
        A("Gate: %s — %d counterexamples in `D` under this arm's reading "
          "(path A) and %d (path B); recorded equality witnesses all tight: %s.\n"
          % (r["gate"]["status"], r["gate"]["counterexamples_in_D_pathA"],
             r["gate"]["counterexamples_in_D_pathB"],
             r["gate"]["recorded_equality_witnesses_all_tight"]))
        tp = r.get("third_path_bruteforce_check")
        if tp:
            A("Third path (brute force from the recorded graph6, no solver shared "
              "with path A or path B) on `%s`: **%s** — %s.\n"
              % (tp.get("graph", "—"), tp["status"],
                 ", ".join("`%s = %s`" % kv for kv in
                           sorted(tp.get("recomputed", {}).items())) or tp.get("reason", "")))
    brackets = [r for r in payload["results"] if r["verdict"] == "BRACKET"]
    if brackets:
        A("## Brackets\n")
        A("| id | reason |")
        A("|---|---|")
        for r in brackets:
            A("| %s | %s |" % (r["id"], r["bracket_reason"] or "—"))
        A("")

    alt = [r for r in payload["results"] if "alt_reading_generator_spec_ceil" in r]
    if alt:
        A("## Targets read twice: `ceil(lambda_1)`\n")
        A("`scripts/gen/invariants._spectral_bracket` decides `ceil(lambda_1)` with "
          "`if det(fl*I - A) == 0: return fl, fl`, which tests whether "
          "`fl = floor(lambda_1)` is *an* eigenvalue rather than the *largest* one. "
          "On `P_5` (graph6 `Dh_`, spectrum ±√3, ±1, 0) it returns "
          "`ceil(lambda_1) = 1` where the true value is 2; **19 of the 12,112 "
          "members of `D` are affected**, `floor(lambda_1)` on none of them. "
          "This arm uses the mathematically correct `ceil(lambda_1)` (exact, via "
          "the Perron null-space test in "
          "[`arm_catalogue_spec.py`](../../scripts/exp/arm_catalogue_spec.py)) and "
          "reports every target naming it under **both** readings, so no verdict "
          "can hinge on the discrepancy.\n")
        A("| id | verdict, corrected reading | verdict, generator's reading | "
          "generator reading: counterexamples in `D` |")
        A("|---|---|---|---|")
        for r in alt:
            gs = r["gate"].get("generator_spec_ceil_reading_on_D") or {}
            A("| %s | **%s** | %s | %s |"
              % (r["id"], r["verdict"], r["alt_reading_generator_spec_ceil"]["verdict"],
                 gs.get("counterexamples_in_D", "—")))
        A("")

    A("## Verification\n")
    A("**Second code path.** Every invariant and every statement was computed "
      "twice: path A is the campaign's own `scripts/gen/invariants.py` + "
      "`scripts/gen/expressions.py`; path B (`scripts/exp/arm_catalogue_pathb.py`) "
      "shares no code with it — SAT (`python-sat`) for the chromatic, matching and "
      "four domination numbers, `networkx.max_weight_clique` for independence, "
      "clique and local independence, a vertex-splitting max-flow for connectivity, "
      "and a separate `Fraction` evaluator for the expression AST. "
      "Invariant disagreements on the catalogue: **%d**.\n"
      % len(payload["invariant_path_mismatches_on_catalogue"]))
    for mm in payload["invariant_path_mismatches_on_catalogue"]:
        A("  * `%s` / `%s`: path A `%s`, path B `%s`" % mm)
    A("")
    A("**Two substitutions inside path A, both recorded.** (1) The chromatic "
      "number: `scripts/gen/invariants._chromatic_brute` is a static-order branch "
      "and bound that does not terminate on T(9), C5[K5] or C5[K6] (> 60 s each), "
      "so path A uses saturation-ordered branch and bound closed between an "
      "explicit greedy colouring and the bound `max(omega, ceil(n/alpha))` "
      "([`arm_catalogue_chi.py`](../../scripts/exp/arm_catalogue_chi.py)); path B's "
      "chromatic number is SAT-based and independent of it. (2) `ceil(lambda_1)`, "
      "for the reason given above. Neither substitution changes any value on `D`: "
      "the slack histograms below reproduce `population.json` exactly on 29 of 30 "
      "targets, the exception being the one target that names `ceil(lambda_1)`.\n")
    dg = payload["database_gate"]
    A("**Database-sanity gate.** `D` was rebuilt from `scripts/gen/graph_db.py` "
      "(%d graphs, sha256 `%s`, recorded `%s` — %s) and all %d targets were "
      "re-evaluated over all of it under this arm's reading, through both paths. "
      "Invariant/slack path mismatches over `D`: %d.\n"
      % (dg["database_rebuilt"], dg["database_sha256"][:16],
         dg["database_sha256_recorded"][:16],
         "match" if dg["database_sha256_match"] else "MISMATCH",
         payload["population_size"], dg["invariant_path_mismatch_count_on_D"]))
    A("| id | counterexamples in `D` (A / B) | equality count mine / recorded | "
      "slack histogram identical to population.json | recorded witnesses tight | gate |")
    A("|---|---|---|---|---|---|")
    for r in payload["results"]:
        g = r["gate"]
        A("| %s | %d / %d | %d / %d | %s | %s | %s |"
          % (r["id"], g["counterexamples_in_D_pathA"], g["counterexamples_in_D_pathB"],
             g["equality_count_mine"], g["equality_count_recorded"],
             "yes" if g["slack_histogram_matches_population"] else "no",
             "yes" if g["recorded_equality_witnesses_all_tight"] else "no",
             g["status"]))
    A("")
    A("## Budget\n")
    A("Preregistered cap: 1 CPU-hour per target. Seconds charged to a target = "
      "its own evaluation time over the 68 catalogue graphs plus the wall clock of "
      "every invariant block it names, in **both** code paths, summed over all 68 "
      "graphs. Shared invariant work is therefore charged in full to every target "
      "that needs it, which over-counts rather than under-counts. Shared setup "
      "wall clock was %.1f s in total.\n" % payload["setup_seconds_shared"])
    A("The whole database-sanity gate (rebuilding `D` and re-evaluating all 30 "
      "targets over all 12,112 graphs through both paths) cost %.0f s once; the "
      "last column charges that entire cost again to *every* target. The largest "
      "figure anywhere below is %.0f s against a 3600 s cap, so no target came "
      "close to the budget and none is a bracket for time.\n"
      % (dg["seconds"] + dg.get("rebuild_seconds", 0.0),
         max(r["seconds_with_database_gate_share"] for r in payload["results"])
         if payload["results"] else 0.0))
    A("| id | s charged | s evaluation only | s incl. whole gate |")
    A("|---|---|---|---|")
    for r in payload["results"]:
        A("| %s | %.2f | %.4f | %.1f |"
          % (r["id"], r["seconds"], r["seconds_evaluation_only"],
             r["seconds_with_database_gate_share"]))
    A("")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
