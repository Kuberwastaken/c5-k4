# Method v1.6 — yield-ordered lanes and cheap pre-flight

**Status:** `DEVELOPMENT`, supersedes nothing; layers on
[`METHOD.md`](METHOD.md) v1.0–v1.5 and
[`METHOD_V1_5_EMPIRICAL_SELECTOR.md`](METHOD_V1_5_EMPIRICAL_SELECTOR.md).

**Amendment date:** 2026-08-15 UTC

This revision is written against evidence, not taste. The
`live-search-2026-08-14` lane produced **23 strict stops and 0 crossings**.
Classifying those stops shows where the budget actually went:

| Stop family | Count | What it cost |
|---|---|---|
| `INVALID_PRE_EVALUATION_*` (source drift, gate timeout, gate integration, protected-path, deadline, semantic closure) | 6 | full setup cost, zero mathematical information |
| `STRICT_STOP_G3_*` (wrong sign, exceptional lobe) | 2 | full trial cost, negative result was symbolically predictable |
| `VERIFIED_*` / `HOLD_BOUNDED` / theorem shadow | 4 | legitimate; one produced a theorem |
| remaining audits/rotations | 11 | mostly cheap |

Two of those three families were avoidable at a fraction of the price. The
amendments below target exactly them, plus the observation that the
campaign's **published** results came overwhelmingly from a vein the
2026-08-14 lane was not working.

## A1 — Yield-ordered vein selection

Rank candidate lanes by realised historical yield per unit budget, highest
first, and require a written justification to run a lower band while a higher
band has untried inventory.

| Band | Vein | Realised yield in this campaign |
|---|---|---|
| 1 | **Formalization faithfulness** — the Lean declaration diverges from its own cited source, and the literal declaration is finitely false | 3 published releases (`oeis-109074`, `oeis-111291`, `oeis-113019`), plus the Bateman–Horn endpoint |
| 2 | **Finite refutation of an open declaration** — statement is faithful but a small artifact settles it | WOWII 172/176/181/430a, Graffiti³ 2 and 13 |
| 3 | **Retro-witness / status sync** — result already known, our artifact independently confirms or the declaration lags its source | several; no discovery claim, cheap |
| 4 | **Wall-crossing surgery** — build a separating family to cross an equality wall | 1 spawned kill (#181 via `T(n)`); 2 wrong-sign stops on 2026-08-14 |

Band 4 is the intellectually distinctive part of this programme and stays in
the portfolio, but it is the *most* expensive per result and must not crowd
out band 1 while band-1 inventory is untouched. As of this amendment the
untouched band-1 inventory is 460 open OEIS/Erdős declarations
(`results/expansion/open_targets_oeis_erdos_20260815.json`).

## A2 — Pre-flight P0, before any setup cost

Run in this order; each is seconds, and any failure is a stop *before* the
expensive apparatus is built. This exists because six 2026-08-14 stops were
infrastructure failures discovered late.

1. **Pin the blob.** Record upstream commit and the exact target file blob
   SHA. Re-check it immediately before publishing; a changed blob invalidates
   the run rather than the result.
2. **Duplicate surface.** One `gh` issue/PR search and one local
   tag/release/commit search for the target identifier. A hit is a stop.
3. **Source reachability.** Fetch the canonical source (OEIS entry/b-file,
   erdosproblems.com page, arXiv/journal PDF) and confirm the exact statement
   is readable *now*. Unreachable source is a stop, not a guess.
4. **Budget declaration.** State the per-computation cap (hard 60 s) and the
   total target budget before starting. Exceeding it is an unknown bracket,
   never evidence.

## A3 — G3-lite: symbolic sign check before any trial

The two `G3` stops on 2026-08-14 died because the proposed surgery moved the
target invariant in the wrong direction — and in both cases that was provable
by hand on two family members. Therefore:

> Before running a frozen trial, evaluate the proposed transformation
> symbolically on the smallest two members of the intended family and write
> the sign of the change in the target residual. If the sign is wrong or
> zero, stop; do not run the trial.

The Bondy exceptional-lobe coordinate is the worked example: joining two
peripheral `K_2` lobes creates the intended `P_4` but simultaneously drops the
lobe pair's path-cover cost from two to one, so a maximum packing absorbs it.
Two members would have shown that in minutes.

## A4 — Triage before depth, always

For any inventory larger than ~30 targets, a fast triage pass over *all* of it
precedes deep work on any of it, and the triage decision for every target is
recorded with a one-line reason. Depth is then spent on the ranked head. This
prevents the failure mode of exhausting the budget on the first few
alphabetically-ordered targets.

## A5 — Durability and concurrency rules

Operational, learned from losing an hour of agent work and from git contention:

- **Append after every target.** Never buffer a report to the end of a run; a
  watchdog kill or a rate limit then costs one target, not the whole lane.
- **One writer to git.** Parallel research agents write files only; a single
  process commits. Concurrent `git` from multiple agents produces
  `index.lock` races.
- **Hard caps everywhere.** Every solver, subprocess, and search gets 60 s.
  An unbounded ILP wedged a lane for 55 minutes.
- **Timeouts are brackets.** Record the interval and move on; never convert a
  timeout into a hold.

## A6 — Four-coordinate status, restated for this scope

For OEIS and Erdős targets specifically, keep these apart and never collapse
them into one label:

1. the accepted mathematical status of the underlying question;
2. whether a formal solution exists anywhere;
3. whether the *declaration in `formal-conjectures`* is faithful to its source;
4. what that declaration literally asserts.

A finite counterexample to (4) while (1) is untouched is a **formalization
counterexample**: a real, publishable artifact about the formal corpus, and
explicitly *not* a claim about the underlying mathematics. Say which one is
being claimed, in the first sentence of any release.
