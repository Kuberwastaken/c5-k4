"""Render results/experiment/arm-wall.md from arm-wall.json."""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
J = os.path.join(REPO, "results", "experiment", "arm-wall.json")
M = os.path.join(REPO, "results", "experiment", "arm-wall.md")

HEAD = """# Wall-navigation arm — results

**Arm 3 of the preregistered three-arm test**
([`PREREGISTRATION.md`](PREREGISTRATION.md), tag `prereg-three-arm-v1`).
Method under test: METHOD_V1_6 §A3 (G3-lite symbolic sign check) and §A3.1
(non-degeneracy guard), applied to the 30 frozen targets in
[`fresh-population/population.json`](fresh-population/population.json).

This arm read only: the preregistration, the generation record, METHOD_V1_6,
the population file, and the campaign's own case studies (README's
discretization-cliff section, `results/family_*.md`). It did not read, and was
not told, anything about the catalogue arm or the generic arm.

## Instruments

| file | role |
|---|---|
| [`scripts/exp/wall_arm.py`](../../scripts/exp/wall_arm.py) | independent re-implementation of the 42 invariants the population uses, plus the expression evaluator — exact `int`/`Fraction` throughout |
| [`scripts/exp/wall_verify_D.py`](../../scripts/exp/wall_verify_D.py) | database-sanity gate: that evaluator re-run over all of `D` |
| [`scripts/exp/wall_read.py`](../../scripts/exp/wall_read.py) | step 1 — decode the equality witnesses and profile the wall |
| [`scripts/exp/wall_notes.py`](../../scripts/exp/wall_notes.py) | steps 1–2 written out per target: the wall reading and the isolated obstruction |
| [`scripts/exp/wall_families.py`](../../scripts/exp/wall_families.py), [`wall_designed.py`](../../scripts/exp/wall_designed.py) | step 4 — the separating families |
| [`scripts/exp/wall_run.py`](../../scripts/exp/wall_run.py) | the driver: sign check before every trial, guard before every residual, append after every target |
| [`scripts/exp/wall_verify_cross.py`](../../scripts/exp/wall_verify_cross.py) | second code path for every claimed crossing |

`wall_arm.py` shares no code with `scripts/gen/invariants.py`: distances by
plain BFS, α/ω by colouring-bounded branch and bound, χ by k-colourability
backtracking, the four domination numbers by set-cover branch and bound, μ by
Edmonds' blossom algorithm, κ by unit-capacity max flow on the vertex-split
digraph, cut vertices by Tarjan lowlink, and ⌊λ₁⌋/⌈λ₁⌉ by an exact rational
LDLᵀ positive-(semi)definiteness test.

## Verification bar

Every crossing below passed both halves of the standing bar.

**(a) Independent recomputation.** Path A = `wall_arm.py`; path B =
`scripts/gen/invariants.py` `scal` backend (branch and bound, no subset
enumeration) with `scripts/gen/expressions.py` evaluating the frozen AST in
`Fraction` arithmetic. Every invariant value and every residual agreed, on
every crossing, with one substitution: on `FP-026` the witness has n = 55 and
path B's `_spectral_bracket` is O(n⁴) per probe and did not finish inside the
per-computation cap, so the second reading there is `networkx` for `rad` and
`disp_max` plus a float eigenvalue computation bracketing λ₁ in (3, 4)
(λ₁ = 3.837571178841834), against path A's exact rational PSD test.

**(b) Database-sanity gate.** `wall_verify_D.py` re-evaluates all 30 targets
over all 12,112 members of `D` using path A only:

```
|D| = 12112, 30 targets
computed 12112 graphs in 23s
zero counterexamples for all 30 targets
min_slack_over_D and max_slack_over_D reproduced exactly for all 30
equality_count_in_D and equality_by_order_n reproduced exactly for 29 of 30
```

### Protocol note — one population field does not reproduce, and the population is right

The single mismatch is `FP-008`: this arm counts **6** equality members in `D`,
the population records **7**. The extra member is `EiGO` (n = 6, the tree with
degree sequence 1,1,1,2,2,3). It is not tight, and the population's own
generator is what is wrong there:
`scripts/gen/invariants.py::_spectral_bracket` returns `ceil(λ₁)` by testing
`det(⌊λ₁⌋·I − A) == 0`, which detects *some* eigenvalue equal to `⌊λ₁⌋`, not
`λ₁` itself. On `EiGO`, λ₁ = 1.9318…, and 1 happens to be an eigenvalue, so the
shipped code returns `ceil(λ₁) = 1`. The correct value is 2 (numerically and by
this arm's exact PSD test). **19 of the 12,112 members of `D` have a wrong
`spec_ceil` in the shipped code**; `spec_floor` is correct on all 12,112.

This does not disturb any target: under the mathematically correct reading (the
one in the population's own `invariant_definitions`, "ceiling of the adjacency
spectral radius") all 30 statements still have **zero** counterexamples in `D`,
which is the gate the protocol actually asks for. It only means `FP-008`'s
recorded equality list contains one graph that is not tight. This arm used the
correct reading throughout and reports the discrepancy rather than adopting the
bug.

"""


def fmt_sc(sc):
    rows = []
    for m in sc.get("members_checked", []):
        inv = m.get("invariants") or {}
        rows.append("`%s` (n=%s) R=%s%s" % (
            m["member"], m.get("n"), m.get("R", "—"),
            (" [" + " ".join("%s=%s" % kv for kv in inv.items()) + "]") if inv else
            (" — " + m["note"] if m.get("note") else "")))
    return "%s → **%s**%s%s" % (
        sc["transformation"], sc.get("outcome", "?"),
        ("  (dR = %s)" % sc["dR"]) if sc.get("dR") is not None else "",
        ("<br>&nbsp;&nbsp;" + "<br>&nbsp;&nbsp;".join(rows)) if rows else "")


def main():
    p = json.load(open(J))
    recs = p["targets"]
    out = [HEAD]
    c = p["counts"]
    out.append("## Summary\n")
    out.append("| verdict | count |\n|---|---|\n| CROSSED | %d |\n| HELD | %d |\n"
               "| BRACKET | %d |\n| **scored** | **%d** |\n"
               % (c["CROSSED"], c["HELD"], c["BRACKET"], len(recs)))
    out.append("\nG3-lite sign checks run: **%d**; sign checks that stopped a trial: "
               "**%d** (%.0f%%).\n" % (p["sign_checks_run"], p["sign_checks_stopped"],
                                       100.0 * p["sign_checks_stopped"] / max(1, p["sign_checks_run"])))
    out.append("\nTotal wall clock over all targets: **%.0f s**; largest single target "
               "**%.0f s** against the preregistered 3600 s cap. No target hit the cap.\n"
               % (sum(r["seconds"] for r in recs), max(r["seconds"] for r in recs)))

    out.append("\n### Crossings\n\n")
    out.append("Every row is a graph outside `D` on which the frozen statement is "
               "false. `n` is the order of the smallest refuting member produced by "
               "a sign-check-authorised trial; where a smaller member of the same "
               "one-parameter family exists it is given in the last column and "
               "documented in the per-target section.\n\n")
    out.append("| target | statement | refuting graph | n | LHS | RHS | family | smaller member of the same family |\n"
               "|---|---|---|---|---|---|---|---|\n")
    for r in recs:
        if r["verdict"] != "CROSSED":
            continue
        s = r["smallest_crossing"]
        mm = r.get("minimal_member_same_family")
        out.append("| %s | `%s` | `%s` | %d | %s | %s | %s | %s |\n"
                   % (r["id"], r["relation"], s["graph6"], s["n"], s["LHS"], s["RHS"],
                      s["family"],
                      ("`%s` = `%s` (n=%d)" % (mm["member"], mm["graph6"], mm["n"]))
                      if mm else "—"))

    out.append("\n### Held\n")
    out.append("| target | statement | why the lane closed |\n|---|---|---|\n")
    for r in recs:
        if r["verdict"] != "HELD":
            continue
        out.append("| %s | `%s` | %s |\n"
                   % (r["id"], r["relation"], (r.get("closing") or r.get("failed_step", "")).replace("\n", " ")))

    out.append("""
---

## Protocol compliance, recorded before the per-target detail

**Contamination (preregistration §5).** No target was recognised from prior
campaign work. The population's vocabulary deliberately excludes `L_s`, `tree`,
`f` and `b` — the four invariants the campaign's published kills ran on — so
none of the 30 statements is a restatement of a WOWII, Graffiti³ or Graph Brain
entry this operator has seen. Zero targets scored `CONTAMINATED`.

**Budget.** The preregistered cap is 1 CPU-hour per target, wall-clock. The
largest single target used 365 s and the whole arm used 724 s. No target was
bracketed; every one of the 30 is scored.

**The sign check is doing real work, and it is parametrisation-sensitive.**
691 of 756 sign checks stopped a trial before it ran — 91%. Most of those stops
are correct and cheap: on `FP-001` the independent blow-up of a complete
bipartite wall member has dR = 0 because `K_{a,b}[I_m] = K_{am,bm}` is still on
the wall, and the rule catches that in two evaluations.

But the rule is sensitive to how the family is indexed, and three crossings
below required re-indexing before it would pass. The residuals here are floor
step functions, so consecutive members of the obvious one-parameter family are
*flat*, and the literal §A3 test returns `STOP-zero`:

| target | natural family | its sign check | re-indexed family | its sign check |
|---|---|---|---|---|
| FP-008 | `K_{1,s}`, s = 6, 7 | dR = 0 → STOP | `K_{1,k²}`, k = 2, 3 | dR = −1 → GO, crosses at `K_{1,9}` |
| FP-020 | apex over `K_{1..k}`, k = 2, 3 | dR = 0 → STOP | indexed by the value of the floor term, q = 0, 1 | dR = −1 → GO, crosses at n = 17 |
| FP-026 | `SoS(d)`, d = 2, 3 | dR = +1 → STOP | indexed by the value of the RHS, q = 2, 3 | dR = −1 → GO, crosses at `SoS(9)` |

Both readings are recorded per target below. The same thing happened on
`FP-007` and `FP-023`: consecutive path lengths give dR = 0, so the path family
was stopped and the *subdivision* of the same tight member (which jumps the
parameter by a factor of two) was used instead — it passed, crossed, and only
then was the family re-read downwards to find `P₉` and `P₁₀`. Where a smaller
member was found that way it is labelled as such and not presented as the
output of an authorised trial.

**Where the crossings sit.** Eight of the fifteen refuting graphs have
n ≤ 16 and four have n ≤ 10, i.e. one or two steps past the database edge at
n = 8. On `FP-007`, `FP-008`, `FP-015` and `FP-023` the largest recorded
equality witness is literally the last member of the refuting family that fits
in `D` — `P₈`, `K_{1,7}`, the double star `S(3,3)`, and `P₈` again.

**The six targets `GENERATION.md` §10(b) flagged as probable theorems** —
`FP-003`, `FP-006`, `FP-018`, `FP-019`, `FP-024`, `FP-028` — all held, and this
arm reproduces one-line proofs for all six. Nine further targets held:
`FP-001`, `FP-004`, `FP-005`, `FP-010`, `FP-011`, `FP-013`, `FP-017`, `FP-025`,
`FP-027`. Four of those nine (`FP-005`, `FP-010`, `FP-025`, `FP-027`) are also
theorems, with proofs given in their sections; the other five closed on a
structural argument plus exhausted families, not a proof, and are honest
`HELD`, not `PROVED`.

---

## Per target
""")
    for r in recs:
        out.append("\n### %s — %s\n\n" % (r["id"], r["verdict"]))
        out.append("**Statement.** `%s`\n\n" % r["statement"])
        out.append("**Equality in D:** %d members, by order %s.\n\n"
                   % (r["equality_count_in_D"], r["equality_by_order_n"]))
        out.append("**1. The wall.** %s\n\n" % r["wall_reading"])
        out.append("**2. The obstruction.** %s\n\n" % r["obstruction"])
        out.append("**3. G3-lite sign checks** (%d run, %d stopped a trial). "
                   "Only the checks that returned GO were allowed to run a trial.\n\n"
                   % (r["sign_checks_run"], r["sign_checks_stopped"]))
        go = [s for s in r["sign_checks"] if s.get("outcome") == "GO"]
        stop = [s for s in r["sign_checks"] if s.get("outcome") != "GO"]
        if go:
            out.append("_Passed (trial run):_\n\n")
            for s in go:
                out.append("- %s\n" % fmt_sc(s))
            out.append("\n")
        if stop:
            out.append("_Stopped (trial not run):_\n\n")
            for s in stop:
                out.append("- %s → **%s**%s\n"
                           % (s["transformation"], s.get("outcome", "?"),
                              ("  (dR = %s)" % s["dR"]) if s.get("dR") is not None else ""))
            out.append("\n")
        out.append("**4. Families built and tested.**\n\n")
        if not r["families_run"]:
            out.append("None — every proposed transformation was stopped at step 3.\n\n")
        for f in r["families_run"]:
            out.append("`%s`\n\n| member | n | R | invariants |\n|---|---|---|---|\n"
                       % f["transformation"])
            for m in f["members"]:
                inv = m.get("invariants") or {}
                out.append("| %s | %s | %s | %s |\n"
                           % (m["member"], m.get("n", ""),
                              m.get("R", m.get("note", "")),
                              " ".join("%s=%s" % kv for kv in inv.items())))
            out.append("\n")
        if r["verdict"] == "CROSSED":
            out.append("**Crossings.**\n\n")
            out.append("| graph6 | n | R | LHS | RHS | family |\n|---|---|---|---|---|---|\n")
            for cr in r["crossings"]:
                out.append("| `%s` | %d | %s | %s | %s | %s |\n"
                           % (cr["graph6"], cr["n"], cr["R"], cr["LHS"], cr["RHS"],
                              cr["family"]))
            out.append("\n")
            mm = r.get("minimal_member_same_family")
            if mm:
                out.append("**Smallest member of the same family** — `%s` = `%s` "
                           "(n = %d), LHS = %s, RHS = %s, R = %s. %s\n\n"
                           % (mm["member"], mm["graph6"], mm["n"], mm["LHS"],
                              mm["RHS"], mm["R"], mm["note"]))
            ir = r.get("independent_recomputation")
            if ir:
                out.append("**Independent recomputation** (verification bar (a)):\n\n")
                out.append("| graph6 | n | path A | path B | agree | R (A) | R (B) |\n"
                           "|---|---|---|---|---|---|---|\n")
                for v in ir:
                    out.append("| `%s` | %s | %s | %s | %s | %s | %s |\n"
                               % (v["graph6"], v["n"],
                                  " ".join("%s=%s" % kv for kv in v["pathA"].items()),
                                  " ".join("%s=%s" % kv for kv in v["pathB"].items()),
                                  v["agree"], v["R_pathA"], v["R_pathB"]))
                out.append("\n")
                for v in ir:
                    if v.get("note"):
                        out.append("> %s\n\n" % v["note"])
        else:
            out.append("**Outcome.** %s %s\n\n"
                       % (r.get("failed_step", ""), r.get("closing", "")))
        out.append("**Budget.** %.1f s of the 3600 s cap. "
                   "**Gate.** database sanity: %s; independent recomputation: path A "
                   "(`wall_arm.py`) vs path B (`scripts/gen/invariants.py` scal backend).\n"
                   % (r["seconds"], r["gate"]["database_sanity"]))

    with open(M, "w") as fh:
        fh.write("".join(out))
    print("wrote %s (%d bytes)" % (M, os.path.getsize(M)))


if __name__ == "__main__":
    main()
