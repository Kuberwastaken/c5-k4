# Overarching research plan

**Frozen scope date:** 2026-08-13 UTC  
**Status:** active development programme  
**Detailed protocol:** [`METHOD.md`](METHOD.md)  
**Publication protocol:** [`UPSTREAM_PROTOCOL.md`](UPSTREAM_PROTOCOL.md)

## Objective

Turn the `C5[K4]` campaign from a catalogue of unusually productive witnesses
into a traceable method for navigating equality walls in machine-generated
graph conjectures:

```text
source-faithful statement
  -> exact residual and database gate
  -> tight/equality family
  -> theorem-baseline subtraction
  -> explicit obstruction identity
  -> prospectively chosen separating transformation
  -> bounded complete trial
  -> exact and formal certification, or an honest zero/theorem signal
```

The immediate research claim is deliberately narrower than a general
counterexample engine:

> Equality and near-equality structure can prospectively guide the design of
> counterexamples—and the extraction of theorem lemmas—for published
> machine-generated graph conjectures.

## Scope boundary

Development targets must be existing graph statements from collections already
represented in `google-deepmind/formal-conjectures`. In this campaign the main
historical collection is **Written on the Wall II**. DeepMind's repository does
not cover Written on the Wall I; WoW I and Graph Brain results therefore do not
enter this programme's target queue or its methodological success count.

`formal-conjectures` is read-only for new discovery publication. Existing
campaign pull requests may receive CI or review maintenance, but new results
are published, when eligible, as one-problem releases in this repository. The
method does not generate new conjectures and does not introduce a new upstream
corpus.

## Standing operating rules

1. Freeze the statement, readings, family, bounds, and stop rules before
   evaluating a prospective family.
2. Run the complete database-sanity gate before any development-family row.
3. Use exact arithmetic and explicit witnesses. Every solver, scratch search,
   and child process has a hard wall-clock cap of 60 seconds.
4. Append results incrementally under `results/expansion/`; a timeout is an
   unknown bracket, never evidence for a hold or crossing.
5. Give every durable selection, implementation, ledger, correction, proof
   bridge, and publication checkpoint its own sequential git commit and push.
6. Preserve failed lemmas and smallest countermodels. Retract errors visibly;
   do not silently rewrite the research trail.
7. Count correlated formulas as one structural cluster. Separate direct
   carrier kills, spawned families, retro-witnesses, theorem results, corrupt
   statements, and interpretation-dependent results.
8. Do not publish a counterexample until source recovery, all plausible
   readings, independent recomputation, novelty review, a warning-clean
   no-`sorry` Lean certificate, and the release lock all pass.

## Active workstreams

### A. Prospective wall crossings

Run one frozen cluster at a time. The current non-metric trial is WOWII 179,
selected in `results/expansion/method_v04_nonmetric_selection.md`. Its database
gate and fixed private-neighborhood split-clique grid may be evaluated exactly
as written; its family and bounds may not be adapted after observing results.

Every completed trial ends in one durable outcome from `METHOD.md`, including
the zeroes. A negative residual starts verification; it does not itself start
publication. A bounded hold may seed a proof lane only after an exact lemma
ladder is written.

### B. Proof extraction and formalization

Maximize reusable no-`sorry` proof components, not merely top-level theorem
counts. Current theorem lanes are:

- **WOWII 133:** the corrected cubic/C4-free specialization is fully
  formalized, warning-clean and no-`sorry`. The noncubic reduction now proves
  the matching-neighborhood formula and global triangle-incidence count; its
  sole representation bridge is the neighborhood-edge/triangle bijection.
- **WOWII 183:** the `gamma_c>=3` and `gamma_c>=4` distance-three tiers are
  formalized. The false two-neighbor retention rung has been replaced by the
  universal theorem `gamma_c(G)<=b(G-N(x))` and an exact attachment conflict
  graph. The hard equality tier asks only for one clean vertex or one
  parity-compatible pair, with `H_m` and `J_m` as mandatory equality tests.
- **WOWII 438b:** maintain the completed stronger arbitrary-subset proof and
  existing upstream review lane; do not recast it as a counterexample.

Proof work is independently useful even if no new counterexample appears: it
tests whether repeated equality walls are shadows of genuine invariant
relations.

### C. Verification and releases

The release backlog is audited before selecting new public work. As of
`results/expansion/release_backlog_audit_2026-08-13.md`, it is empty: completed
unreleased disproofs are already claimed, already released, retro, corrupt,
ambiguous, or incomplete.

For a genuinely new candidate, proceed in separate commits:

1. source/status audit and exact verifier;
2. independent recomputation and saved witness;
3. no-`sorry` Lean certificate and `#print axioms` audit;
4. novelty and immutable-artifact preflight;
5. annotated locked tag and one-problem GitHub release;
6. release/tag/link readback.

No public issue or pull request is opened for a new result under the current
policy.

### D. Method iteration

After each cluster, update `METHOD.md` only with lessons supported by the
completed ledger. Record whether each lesson was known prospectively or learned
after the result. In particular, update:

- the transformation-effect catalogue;
- theorem-shadow and theorem-signal criteria;
- quotient/family pruning rules;
- formalization cost and recurring API bridges;
- failure modes in source parsing, process supervision, or novelty checks.

The README should explain the method through a few strong case studies and its
published zeroes, not optimize for a raw kill count.

## Evidence already established

The development set currently contains four qualitatively useful outcomes:

1. `C5[K_m]` exposed the rounding cliff behind WOWII 63/64/85 and a correlated
   historical failure cluster.
2. Separating `alpha=lambda_max` with triangular graphs crossed the formalized
   square-degree reading of WOWII 181.
3. Leaving the diameter-two theorem wall with barbell graphs crossed WOWII 176
   and adjacent 172.
4. Nonuniform `P7` clique blow-ups separated center geometry from the
   Caro--Wei correction and crossed WOWII 430a in another invariant cluster.

The zeroes and theorem lanes are part of the evidence: 422b was pruned at the
quotient level, 184/185 held on their frozen grid, 438b became a stronger
theorem, and 133/183 have produced successively narrower formal or structural
obligations.

## Near-term execution order

1. Preserve the strict `TIMEOUT_BRACKET` stop on WOWII 179; do not reopen its
   unevaluated grid without a newly frozen protocol.
2. Close WOWII 133's explicit neighborhood-edge/triangle bijection, then use
   the triangle-corrected local-average identity in the noncubic path bound.
3. Attack WOWII 183's final conflict-graph existence condition in the hard
   equality and near-equality tiers; retain all parity countermodels.
4. Continue WOWII 61 only through graphical, realization-aware recursive
   invariants; the unrestricted and naive equal-sum variants are formally
   false.
5. Keep Method v0.6's prospective queue empty until a genuinely new open
   WOWII module enters `formal-conjectures`; all 14 current modules were
   already evaluated and cannot be retrospectively relabeled held out.

Long computation and narrow proof experiments should be delegated to bounded
agents. The primary lane validates artifacts, catches scope or trust errors,
and integrates one logical checkpoint at a time.

## Maturity milestone

The development method becomes ready for a genuinely held-out experiment only
after it has:

- a stable target-ranking rule and transformation library;
- multiple prospective successes in distinct invariant clusters;
- complete ledgers for failures, ambiguities, theorem shadows, and compute;
- repeatable exact-verification and Lean-certificate templates; and
- no unresolved publication or provenance ambiguity in its case studies.

Only then may a new untouched manifest and equal baseline budgets be frozen.
Nothing already discussed, ranked, or searched in this repository can be
retrospectively labelled held out.

## Completion condition

This programme is not complete when a headline counterexample is found. It is
complete only when the method, full developmental evidence, formal artifacts,
negative results, and a prospectively frozen held-out evaluation can be audited
from the git history without relying on private context.
