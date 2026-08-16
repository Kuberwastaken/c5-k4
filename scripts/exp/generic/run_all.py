"""GENERIC ARM -- driver: run every frozen target, staged, and write the report.

Each target is searched by `search.py` in its own process, with the budget
measured as that process's own CPU time (`time.process_time`), so the
preregistered "1 CPU-hour per target" cap is exact even when several targets run
concurrently on a shared box.

The search is a deterministic sequence of work units, so a target's budget can be
spent in stages: stage 2 resumes at the unit stage 1 stopped on and follows the
identical trajectory a single long run would have followed.

    python3 scripts/exp/generic/run_all.py --stage 240 --workers 6
    python3 scripts/exp/generic/run_all.py --stage 900 --workers 6
    python3 scripts/exp/generic/run_all.py --stage 3600 --workers 6
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
EXPDIR = os.path.join(ROOT, "results", "experiment")
RUNDIR = os.path.join(EXPDIR, "arm-generic-runs")
POP = os.path.join(EXPDIR, "fresh-population", "population.json")
CAP = 3600.0

sys.path.insert(0, HERE)


def load_pop():
    return json.load(open(POP))["targets"]


def result_path(tid):
    return os.path.join(RUNDIR, "%s.json" % tid)


def read_result(tid):
    p = result_path(tid)
    if os.path.exists(p):
        try:
            return json.load(open(p))
        except Exception:
            return None
    return None


# --------------------------------------------------------------------------
# report writers (called after every completed target)
# --------------------------------------------------------------------------

def mono(s):
    """Inline-code span that survives graph6 strings containing backticks."""
    if s is None:
        return "—"
    s = str(s)
    longest = 0
    run = 0
    for ch in s:
        run = run + 1 if ch == "`" else 0
        longest = max(longest, run)
    fence = "`" * (longest + 1)
    pad = " " if (s.startswith("`") or s.endswith("`")) else ""
    return "%s%s%s%s%s" % (fence, pad, s, pad, fence)


def write_report(targets, gate0):
    a3p = os.path.join(RUNDIR, "_audit3.json")
    audit3 = {}
    if os.path.exists(a3p):
        try:
            for e in json.load(open(a3p))["crossings"]:
                audit3[e["id"]] = e
        except Exception:
            audit3 = {}
    rows = []
    for t in targets:
        r = read_result(t["id"])
        if r is None:
            rows.append({"id": t["id"], "statement": t["statement"],
                         "verdict": "PENDING"})
            continue
        row = {
            "id": t["id"],
            "statement": t["statement"],
            "verdict": r["verdict"],
            "refuting_graph6": r.get("witness_graph6"),
            "witness_n": r.get("witness_n"),
            "lhs_at_witness": r.get("witness_lhs"),
            "rhs_at_witness": r.get("witness_rhs"),
            "slack_at_witness": r.get("witness_slack"),
            "cpu_seconds": round(r.get("cpu_seconds", 0.0), 2),
            "wall_seconds": round(r.get("wall_seconds", 0.0), 2),
            "verify_cpu_seconds": round(r.get("verify_cpu_seconds", 0.0), 2),
            "cap_cpu_seconds": r.get("cap_cpu_seconds", CAP),
            "seeds": r.get("seeds"),
            "method_found": r.get("method_found"),
            "method_unit_counts": r.get("method_counts"),
            "search_evaluations": r.get("evals_this_run"),
            "max_order_searched": r.get("n_max_probed"),
            "n9_exhaustive_bases_completed": r.get("sweep_bases_n8_completed"),
            "best_slack_found": r.get("best_slack_found"),
            "best_slack_graph6": r.get("best_slack_graph6"),
            "best_slack_source": r.get("best_slack_desc"),
            "gate_second_code_path": (r.get("gate_second_code_path") or {}).get(
                "second_code_path", "n/a (no candidate)"),
            "gate_database_sanity": (r.get("gate_database_sanity") or {}).get(
                "status", "n/a (no candidate)"),
            "gate_detail": {
                "second_code_path": r.get("gate_second_code_path"),
                "database_sanity": r.get("gate_database_sanity"),
            } if r.get("gate_second_code_path") else None,
            "witness_before_reduction_graph6": r.get("witness_raw_graph6"),
            "witness_before_reduction_n": r.get("witness_raw_n"),
            "spec_convention": r.get("spec_convention"),
            "gate_third_code_path": (audit3.get(t["id"]) or {}).get(
                "status", "n/a (no candidate)"),
            "gate_third_code_path_detail": audit3.get(t["id"]),
        }
        rows.append(row)

    counts = {}
    for r in rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1

    out = {
        "arm": "generic",
        "experiment": "fresh-generation three-arm test (prereg-three-arm-v1)",
        "method": "brute force plus heuristics: random families over a wide "
                  "order/density range, near-exhaustive n=9 sweep beyond D, beam "
                  "extension, and simulated annealing on edge flips minimising "
                  "the target's slack. No structural analysis of tightness.",
        "code": ["scripts/exp/generic/ginv.py",
                 "scripts/exp/generic/search.py",
                 "scripts/exp/generic/run_all.py",
                 "scripts/exp/generic/check_against_gen.py"],
        "budget_cap_cpu_seconds_per_target": CAP,
        "protocol_notes": [
            "A first pass of this arm was run and DISCARDED before any verdict "
            "was recorded, because profiling showed the arm's exact spectral "
            "test was slow enough to cap the searchable order at n=9 for the two "
            "targets that use floor(lambda_1) (FP-019, FP-026). The evaluator "
            "was rewritten (fraction-free integer Sylvester test) and the whole "
            "arm restarted from unit 0 with the final code, so every target was "
            "searched by one and the same instrument. No verdict from the "
            "discarded pass was carried over.",
            "While fixing that, the arm found that "
            "scripts/gen/invariants._spectral_bracket returns ceil(lambda_1) = "
            "floor(lambda_1) whenever floor(lambda_1) is an eigenvalue, even "
            "when it is not the largest one; that is wrong on 19 of the 12,112 "
            "members of D. It affects exactly one target, FP-008, whose "
            "right-hand side is floor(A / ceil(lambda_1)). The arm searches "
            "under the definition-faithful convention, which is the harder one "
            "for this target (a larger ceil makes the right-hand side smaller "
            "and the '>=' easier to satisfy), and every crossing is required to "
            "be a crossing under BOTH conventions.",
        ],
        "spec_convention_searched": "true (definition-faithful)",
        "written": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "counts_by_verdict": counts,
        "evaluator_gate": gate0,
        "targets": rows,
    }
    with open(os.path.join(EXPDIR, "arm-generic.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)

    # ---- markdown
    L = []
    L.append("# Generic arm — results")
    L.append("")
    L.append("Arm 2 of the preregistered three-arm test "
             "([`PREREGISTRATION.md`](PREREGISTRATION.md), tag "
             "`prereg-three-arm-v1`), run blind to the other two arms.")
    L.append("")
    L.append("**Written incrementally; last update %s.**" % out["written"])
    L.append("")
    L.append("## Method")
    L.append("")
    L.append("Search without structural insight. Four mechanical generators, run "
             "as a fixed deterministic sequence of work units so that a staged "
             "run reproduces a single long run exactly:")
    L.append("")
    L.append("| unit | what it does |")
    L.append("|---|---|")
    L.append("| `FAM` | standard random families over a wide order and density "
             "range: `G(n,p)` for `p = 0.08..0.92`, random `d`-regular, random "
             "bipartite, uniform random trees (Prüfer), Barabási–Albert "
             "preferential attachment, random geometric. Orders `9..n_max`. |")
    L.append("| `SWEEP` | near-exhaustive sweep beyond `D`: every connected graph "
             "on 9 vertices has a non-cut vertex, so extending every `n = 8` "
             "member of `D` by one vertex over all 255 non-empty neighbourhoods "
             "covers `n = 9` exhaustively up to isomorphism. Bases are visited in "
             "increasing order of their slack. |")
    L.append("| `GROW` | beam search: keep the lowest-slack graphs found at each "
             "order and extend them by one vertex over sampled neighbourhoods. |")
    L.append("| `ANNEAL` | simulated annealing minimising the target's slack, "
             "moves = single edge flips plus degree-preserving double-edge swaps, "
             "restarted from many seeds across the order range. |")
    L.append("")
    L.append("`n_max` per target is set by a probe: the largest order in "
             "`10..40` at which one exact evaluation of that target costs "
             "≤ 80 ms. Tightness/slack data from `population.json` is used only "
             "as a numeric objective and as a seed ordering; no equality member "
             "is analysed structurally and no purpose-built family is "
             "constructed.")
    L.append("")
    L.append("**Budget.** 1 CPU-hour per target (`time.process_time` of that "
             "target's own process), the preregistered cap. `HELD` means the cap "
             "was spent without a crossing; `BRACKET` means the run stopped "
             "before the cap.")
    L.append("")
    L.append("## Evaluator and gates")
    L.append("")
    L.append("`scripts/exp/generic/ginv.py` is an independent implementation of "
             "the 42 invariants the 30 targets use, written from the "
             "`invariant_definitions` shipped in `population.json`; it shares no "
             "code with `scripts/gen/invariants.py`. Exact `int`/`Fraction` "
             "arithmetic throughout.")
    L.append("")
    for line in gate0.get("lines", []):
        L.append("* " + line)
    L.append("")
    L.append("Every candidate crossing must pass both of the required gates, "
             "and this arm adds a third check of its own:")
    L.append("")
    L.append("* **(a) second code path** — the witness is recomputed by "
             "`scripts/gen/invariants.py` (backend `scal`, plus the exhaustive "
             "`2^n` backend `brute` when `n ≤ 20`) and re-evaluated by "
             "`scripts/gen/expressions.py`; LHS, RHS and slack must agree "
             "exactly and the slack must be negative;")
    L.append("* **(b) database-sanity gate** — the same reading is re-evaluated "
             "over all 12,112 members of `D` (rebuilt from `scripts/gen/`); it "
             "must produce zero counterexamples there and reproduce the recorded "
             "equality count. A reading that also refutes members of `D` is a bug "
             "and is discarded.")
    L.append("")
    L.append("* **(c) third code path** (not required by the protocol; added "
             "here) — every crossing is recomputed a third time from different "
             "algorithms again: `networkx` primitives for the polynomial "
             "invariants and the matching number, `networkx.max_weight_clique` "
             "for `alpha`/`omega`/`lambda(v)`, the chromatic number as an exact "
             "minimum cover of `V` by independent sets, and the four domination "
             "numbers by naive `itertools` enumeration over all vertex subsets "
             "in increasing size (`scripts/exp/generic/audit_crossings.py`).")
    L.append("")
    L.append("Two protocol notes, recorded because they affect how this arm "
             "should be read:")
    L.append("")
    for note in out["protocol_notes"]:
        L.append("* " + note)
    L.append("")
    L.append("Witnesses are then reduced mechanically (greedy vertex deletion "
             "while connected and slack < 0), which is why several are much "
             "smaller than the graph the search first hit.")
    L.append("")
    L.append("## Counts")
    L.append("")
    L.append("| verdict | targets |")
    L.append("|---|---|")
    for k in ("CROSSED", "HELD", "BRACKET", "GATE-FAIL", "PENDING"):
        if k in counts:
            L.append("| %s | %d |" % (k, counts[k]))
    L.append("| **total** | **%d** |" % len(rows))
    L.append("")
    L.append("## Per-target results")
    L.append("")
    L.append("| id | statement | verdict | witness (graph6) | n | LHS | RHS | "
             "found by | CPU s | gate (a) | gate (b) | gate (c) |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        if r["verdict"] == "PENDING":
            L.append("| %s | `%s` | PENDING | | | | | | | | | |"
                     % (r["id"], r["statement"].split(":  ")[-1]))
            continue
        L.append("| %s | `%s` | **%s** | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["id"], r["statement"].split(":  ")[-1], r["verdict"],
            mono(r["refuting_graph6"]) if r["refuting_graph6"] else "—",
            r["witness_n"] if r["witness_n"] else "—",
            r["lhs_at_witness"] or "—", r["rhs_at_witness"] or "—",
            r["method_found"] or "—", r["cpu_seconds"],
            r["gate_second_code_path"], r["gate_database_sanity"],
            r["gate_third_code_path"]))
    L.append("")
    L.append("## Crossings in detail")
    L.append("")
    ncr = 0
    for r in rows:
        if r["verdict"] != "CROSSED":
            continue
        ncr += 1
        L.append("### %s — `%s`" % (r["id"], r["statement"].split(":  ")[-1]))
        L.append("")
        L.append("* refuting graph (graph6, `n = %s`): %s"
                 % (r["witness_n"], mono(r["refuting_graph6"])))
        L.append("* at the witness: **LHS = %s**, **RHS = %s**, slack = %s"
                 % (r["lhs_at_witness"], r["rhs_at_witness"],
                    r["slack_at_witness"]))
        L.append("* found by: `%s`; first hit at `n = %s` "
                 "(%s), then reduced to `n = %s`"
                 % (r["method_found"], r["witness_before_reduction_n"],
                    mono(r["witness_before_reduction_graph6"]), r["witness_n"]))
        L.append("* search cost: %.2f CPU s (cap %.0f s); verification %.2f CPU s"
                 % (r["cpu_seconds"], r["cap_cpu_seconds"],
                    r["verify_cpu_seconds"]))
        gd = r.get("gate_detail") or {}
        sc = gd.get("second_code_path") or {}
        db = gd.get("database_sanity") or {}
        L.append("* gate (a) second code path: **%s** — "
                 "`scripts/gen` %s" % (
                     r["gate_second_code_path"],
                     ", ".join("%s: LHS %s / RHS %s"
                               % (b, sc.get("gen_%s_lhs" % b),
                                  sc.get("gen_%s_rhs" % b))
                               for b in ("brute", "scal")
                               if sc.get("gen_%s_lhs" % b) is not None)))
        L.append("* gate (b) database sanity: **%s** — %s counterexamples over "
                 "all 12,112 members of `D` through this arm's evaluator, %s "
                 "through the `scripts/gen` path on a %s-graph sample; equality "
                 "count %s vs %s recorded"
                 % (r["gate_database_sanity"],
                    db.get("arm_counterexamples_in_D"),
                    db.get("gen_path_counterexamples"),
                    db.get("gen_path_sample"),
                    db.get("arm_equality_count_in_D"),
                    db.get("population_equality_count_in_D")))
        t3 = r.get("gate_third_code_path_detail") or {}
        L.append("* gate (c) third code path: **%s** — LHS %s, RHS %s, slack %s"
                 % (r["gate_third_code_path"], t3.get("third_path_lhs"),
                    t3.get("third_path_rhs"), t3.get("third_path_slack")))
        if t3.get("invariants"):
            L.append("* invariants at the witness (third path): %s"
                     % ", ".join("`%s = %s`" % (k, v)
                                 for k, v in sorted(t3["invariants"].items())))
        L.append("* seeds: base `%s`; %s"
                 % ((r["seeds"] or {}).get("base_seed"),
                    (r["seeds"] or {}).get("formula")))
        L.append("")
    if ncr == 0:
        L.append("_none yet._")
        L.append("")
    L.append("## Non-crossings — how close the search got")
    L.append("")
    L.append("| id | verdict | best slack found | at (graph6) | source | "
             "evaluations | max order | n=9 bases swept | CPU s |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        if r["verdict"] in ("CROSSED", "PENDING"):
            continue
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["id"], r["verdict"], r["best_slack_found"],
            mono(r["best_slack_graph6"]), r["best_slack_source"],
            r["search_evaluations"], r["max_order_searched"],
            r["n9_exhaustive_bases_completed"], r["cpu_seconds"]))
    L.append("")
    L.append("Machine-readable copy: [`arm-generic.json`](arm-generic.json). "
             "Per-target raw run records: `arm-generic-runs/`.")
    L.append("")
    with open(os.path.join(EXPDIR, "arm-generic.md"), "w") as fh:
        fh.write("\n".join(L))
    return counts


# --------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=float, default=240.0,
                    help="cumulative CPU-second budget each target should reach")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--only", default=None)
    ap.add_argument("--report-only", action="store_true")
    args = ap.parse_args()

    os.makedirs(RUNDIR, exist_ok=True)
    targets = load_pop()
    gate0 = json.load(open(os.path.join(RUNDIR, "_gate0.json")))
    if args.report_only:
        print("counts:", write_report(targets, gate0))
        return 0

    todo = []
    for t in targets:
        if args.only and t["id"] not in args.only.split(","):
            continue
        r = read_result(t["id"])
        if r is not None and r["verdict"] in ("CROSSED", "GATE-FAIL"):
            continue
        prior = r["cpu_seconds"] if r else 0.0
        if prior >= min(args.stage, CAP) - 1:
            continue
        todo.append((t["id"],
                     r["next_unit"] if r else 0,
                     prior,
                     r["units_total"] if r else 0,
                     r["wall_seconds"] if r else 0.0))

    print("stage %.0f CPU s; %d targets to run" % (args.stage, len(todo)),
          flush=True)
    running = {}
    queue = list(todo)
    while queue or running:
        while queue and len(running) < args.workers:
            tid, unit, prior, punits, pwall = queue.pop(0)
            budget = min(args.stage, CAP) - prior
            cmd = [sys.executable, os.path.join(HERE, "search.py"),
                   "--target", tid, "--cpu", "%.1f" % budget,
                   "--start-unit", str(unit), "--prior-cpu", "%.4f" % prior,
                   "--prior-units", str(punits), "--prior-wall", "%.4f" % pwall,
                   "--cap", "%.1f" % CAP,
                   "--out", result_path(tid)]
            running[tid] = subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                                            stderr=subprocess.PIPE)
            print("  start %s  budget %.0f s (prior %.0f s, unit %d)"
                  % (tid, budget, prior, unit), flush=True)
        time.sleep(2.0)
        for tid in list(running):
            p = running[tid]
            if p.poll() is None:
                continue
            err = p.stderr.read().decode()[-2000:]
            if p.returncode != 0:
                print("  !! %s exited %d: %s" % (tid, p.returncode, err),
                      flush=True)
            del running[tid]
            r = read_result(tid)
            print("  done  %s -> %s (%.0f CPU s)"
                  % (tid, r["verdict"] if r else "NO RESULT",
                     r["cpu_seconds"] if r else 0), flush=True)
            write_report(targets, gate0)
    counts = write_report(targets, gate0)
    print("counts:", counts, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
