# Experiment v2 — design and preregistration

**Written 2026-08-16, before any v2 population exists.**

## The v1 result stands. This is not a rerun.

[`../experiment/RESULTS.md`](../experiment/RESULTS.md) is final: wall-unique
crossings = 1/30, INCONCLUSIVE, substance close to null, and it is not being
reinterpreted, reweighted, or quietly superseded. Anyone reading this repo
should read that first.

## The flaw v2 addresses — and the trap in addressing it

v1's vocabulary **excluded `f`, `b`, `tree`, `path`** — the largest induced
forest / bipartite subgraph / tree / path — dropped from emission on measured
runtime (>20 s on G(40,0.3)). Those are precisely the invariants the mechanism
is about: the claim is that *hereditary induced invariants stay pinned while
metric and degree terms grow*, and the C₅[K_m] case study is built on exactly
`f = b = tree = 4`. So v1 tested the navigation method on a population in which
the claimed mechanism was **not representable**.

**The trap:** the v1 generator pre-committed, in `GENERATION.md`, that "a null
result cannot be blamed on that vein." That was the right thing to write, and
it binds. So v2 does **not** get to say "v1 doesn't count."

**The resolution:** v2 tests a *different and narrower hypothesis*, and is
labelled as such. v1 answered "does tightness navigation beat generic search on
a general Graffiti-style population?" — answer: barely, one target in thirty.
v2 asks a strictly narrower question that v1 could not ask:

> **H1-v2:** on conjectures whose statements involve hereditary induced
> invariants (`f`, `b`, `tree`, `path`, `α`), does tightness navigation find
> crossings that generic search misses?

A positive v2 result would **not** rehabilitate H1 as stated in v1. It would
establish a bounded claim: the method works where its mechanism applies. That
is a smaller claim than the project has been making, and it is the largest one
the evidence could support.

## Repairs carried in from METHOD v1.7

- **R1 step-aware sign check.** Residuals are evaluated across a run long enough
  to contain a discontinuity of every rounding operator. v1 lost five families
  to `dR = 0` readings over adjacent members.
- **R2 isolation covers process tables.** Arms run **sequentially**, each after
  the previous session has exited. No concurrent arms.
- **R3 control gets a sufficient budget.** The generic arm must return
  HELD or CROSSED — not BRACKET — on ≥ 75% of targets, or the run is reported
  as having no valid control. v1's control bracketed 16/30 and never returned a
  single HELD.
- **R4 invariants cross-validated pre-freeze** against a second independent
  implementation over the whole database. v1 shipped a `⌈λ₁⌉` bug that corrupted
  one target's tightness data.

## Population

- **Database `D₂`:** all connected graphs on `n ≤ 9` where feasible; if `n = 9`
  (261,080 graphs) proves infeasible for the expensive invariants, `D₂` is
  `n ≤ 8` **plus** a recorded, exhaustively-enumerated `n = 9` subset, and the
  boundary is stated exactly. A harder edge than v1's `n = 8` is the point:
  v1's targets fell to annealing 14 times out of 30.
- **Vocabulary:** must include `f`, `b`, `tree`, `path`, `α` alongside the
  metric/degree/spectral terms. Runtime is managed by capping evaluation order
  (these are `2ⁿ` subset problems; exact to `n ≈ 20`, branch-and-bound beyond),
  not by dropping the invariants.
- **Every target must involve at least one hereditary induced invariant.** That
  is the population's defining restriction and the reason it is a different
  experiment.
- Same filters as v1: zero counterexamples in `D₂`, finite-universal form,
  structural dedup, ≤ 30 targets, tightness data recorded per target.
- The generator may not test any candidate outside `D₂`.

## Arms, endpoint, decision rule

Unchanged from v1 — they produced a usable answer and changing them now would
be exactly the post-hoc adjustment v1's protocol forbade. Catalogue (frozen
68-graph list, unchanged file), generic (search without structural insight),
wall (read the wall → isolate the obstruction → step-aware sign check → build
the separating family). Primary endpoint: **wall-unique crossings**.

- **H1-v2 supported** iff wall-unique ≥ 3 over ≥ 20 scored targets AND
  wall-unique ≥ catalogue total.
- **H1-v2 falsified** iff wall-unique ≤ catalogue-unique.
- **Inconclusive** otherwise, reported as such.
- **No valid control** iff the generic arm brackets > 25% of targets — reported
  as a failed run, not as a result in either direction.

## Commitments

Identical to v1: published in this repository whatever it shows; no criterion
changes after any arm reports; no arm re-run to improve its score; deviations
recorded as protocol violations. If v2 also returns null, the honest conclusion
is that the navigation claim is not supported even where its mechanism applies,
and the project should stop testing it and keep doing corpus work.
