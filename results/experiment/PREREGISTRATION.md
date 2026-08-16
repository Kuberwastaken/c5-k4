# Preregistration — fresh-generation three-arm test

**Written 2026-08-15, BEFORE the conjecture population exists.** The generator
was running when this file was committed and had produced no output; the git
history of this repository is the evidence for that ordering. If the population
file predates this commit, this preregistration is void.

**Tag:** `prereg-three-arm-v1`

## Why

The campaign's central claim — that exact tightness structure *prospectively*
guides counterexample design — has never been tested against a control. The
independent review of 2026-08-15
([`../review/INDEPENDENT_REVIEW_2026-08-15.md`](../review/INDEPENDENT_REVIEW_2026-08-15.md))
counted **n≈4** developmental crossings, **n≈1** under frozen protocol, and
**n=0** held-out, against roughly 80 frozen decisions — and noted that the one
frozen crossing was found independently by its own catalogue arm, giving the
navigation method a measured marginal value of zero on that instance. This
experiment exists to settle that with one clean measurement.

## Hypotheses

- **H1 (the claim):** an arm that uses equality/tightness structure to design
  separating families finds counterexamples that neither a fixed catalogue of
  known extremal graphs nor generic search finds, at equal compute.
- **H0 (null):** it does not. Any crossing the wall arm finds is also found by
  the catalogue arm or by generic search.

## Population

Generated **after** this file is committed, by
[`../../scripts/gen/`](../../scripts/gen/), and frozen at
`results/experiment/fresh-population/population.json`.

- Database `D`: all connected graphs on `n ≤ 8` (boundary to be recorded exactly
  by the generator; if `n = 8` proves infeasible the generator must say so).
- Emitted statements: Graffiti-style inequalities over a fixed invariant
  vocabulary, retained only if they have **zero counterexamples in `D`**.
- Filtered to finite-universal form ("for all connected graphs, <finite
  inequality>"), deduplicated to structural clusters, capped at **30 targets**.
- The generator is forbidden from testing any candidate against any graph
  outside `D`. Any candidate it accidentally learns is false outside `D` is
  discarded and recorded.

**Population freeze:** once `population.json` is committed, no target may be
added, removed, edited, or reordered. A target that later proves malformed is
scored as `INVALID` and reported, not silently dropped.

## Arms

Three arms, run **independently and blind to each other's results**, each on a
disjoint agent with no access to the others' output files.

1. **Catalogue arm.** Test each target against a fixed, pre-declared list of
   known extremal/pathological graphs: C₅[K_m] for m = 2..6, T(n) = L(Kₙ) for
   n = 7..9, Petersen, Kneser K(n,2) for n = 5..7, Paley(13/17/29), complete
   multipartite, cocktail-party, prisms/Möbius–Kantor, complete bipartite,
   stars, brooms, double stars, the complement of each of the above. No design
   step; pure lookup.
2. **Generic arm.** Search without tightness information: random graphs across a
   range of densities, plus local search / simulated annealing minimising the
   target's slack, plus exhaustive small-graph sweeps beyond `D`.
3. **Wall arm.** The campaign's method (METHOD_V1_6 §A3, frozen): read the
   equality members recorded with each target, identify the invariant that
   prevents crossing, apply the G3-lite symbolic sign check on the two smallest
   members, then construct and test a purpose-built separating family.

**Budget:** 1 CPU-hour per arm per target, hard cap, wall-clock enforced. An arm
that exceeds it on a target records a bracket, not a result.

## Primary endpoint

**Wall-arm-unique crossings**: targets refuted by the wall arm and by neither
the catalogue arm nor the generic arm, where every crossing must pass the
standing verification bar — independent recomputation by a second code path,
and the database-sanity gate (a "refutation" that also refutes members of `D`
is a bug in the reading, not a crossing).

## Decision rule, fixed in advance

- **Claim supported** if the wall arm produces **≥ 3 unique crossings** over
  **≥ 20 scored targets** AND its unique count is **≥** the catalogue arm's
  total crossings.
- **Claim falsified** if wall-unique crossings **≤** catalogue-unique crossings.
- **Inconclusive** otherwise (including fewer than 20 scored targets), reported
  as inconclusive with no reinterpretation of the endpoint.

## Commitments

1. The result is published in this repository **whatever it shows**, including
   a null or falsifying result, within one week of the run completing.
2. The endpoint, criterion, arms, and budget above will not be changed after
   seeing any arm's output. Any deviation is recorded as a protocol violation in
   the results file, with the reason.
3. Arms do not communicate. Cross-contamination invalidates the affected target.
4. No arm may be re-run to improve its score. A failed or crashed arm run is
   reported as such.
5. If the wall arm's operator (agent or human) recognises a target from prior
   campaign work, that target is scored `CONTAMINATED` and excluded from the
   denominator — reported, not hidden.

## What would make this test worthless

Recorded now so it cannot be rationalised later: a population small enough that
3 uniques is noise; targets so easy that all three arms refute everything; a
wall arm that is really doing generic search with extra steps; or any
post-hoc adjustment of the criterion. If the run hits one of these, the honest
report is "the experiment failed to test the hypothesis", not a claim in either
direction.

---

## Run log (appended during execution, no criterion changes)

**2026-08-15, arms launched.** Catalogue, generic and wall arms started
concurrently and blind: each was instructed not to read the others' output
files, and the generic and wall arms were additionally forbidden from reading
`scripts/exp/catalogue.py` (the control arm's instrument).

**Interim, generic arm partial (12 CROSSED / 8 BRACKET / 10 PENDING of 30).**
Recorded as it stands. This is in the direction of the pre-specified
worthlessness condition "targets so easy that all three arms refute
everything": if generic search alone refutes most of the population, the
experiment loses power to discriminate between arms regardless of what the wall
arm does. The criterion is **not** being changed in response — that is exactly
the post-hoc adjustment this document forbids. If the final numbers land there,
the honest report is "the experiment failed to test the hypothesis", per the
closing section above.

Contributing factor already documented pre-freeze in `GENERATION.md`: the
database edge is `n = 8`, well inside Graffiti.pc's, so these targets were
expected to be easier to refute than the WOWII conjectures the method was
developed on. Only the between-arm comparison was ever meaningful.

## Integrity events (disclosed, no criterion changes)

### E1 — process-table leak, downstream → upstream

The generator agent, checking for dangling processes with `pgrep -af`, saw the
command line of the **wall arm's** verifier: `<target-id>:<graph6>` pairs for
**15 of the 30 targets**, on graphs well outside `D`. It saw target IDs paired
with candidate witnesses; it did **not** see any outcome, did not open the
verifier's inputs or outputs, and stopped investigating on recognising what the
process was.

It correctly did **nothing** to the population. Discarding those 15 targets
would have (a) edited a population this document freezes, (b) on a guess about
results it had not seen, and (c) removed precisely the targets an arm was
working on — biasing the primary endpoint in the direction the experiment
exists to test. `population.json` was generated, deduplicated, selected and
verified *before* those process arguments existed, and `sha256sum` confirms it
unchanged.

**The structural gap is real and is not covered by this document.** The
arm-isolation clause isolates *files*; it says nothing about *process tables*,
which are world-readable on a shared box. Here the leak ran downstream→upstream
into already-frozen output, which is harmless. It would not be harmless
arm→arm.

### E2 — arms ran concurrently; cross-arm leakage cannot be excluded

By my design all three arms ran **concurrently on one machine**. Post-hoc
checks of the arm transcripts:

- **Wall arm**: zero reads of any other arm's files, zero process-listing calls.
- **Catalogue arm**: its only `Read` of an `arm-*` file was of **its own**
  `arm-catalogue.md`. Ran ~7 process-listing commands.
- **Generic arm**: ran ~7 process-listing commands; one bash invocation matched
  an `arm-*` filename pattern. **This check is incomplete** — the grep over the
  transcript timed out and I did not establish whether that invocation touched
  its own file or another's.

So: no arm is shown to have read another's results file, but **I cannot exclude
that the catalogue or generic arm saw wall-arm process arguments.**

**Direction of the residual risk matters.** Any leak from the wall arm into
catalogue/generic would let those arms find crossings they would not otherwise
have found, which *raises* their counts and *lowers* wall-unique crossings —
the primary endpoint. That biases **against** the hypothesis, not for it. A
positive result would survive this contamination; a null or falsifying result
is the one that would be suspect. Recorded now, before the wall arm has
reported.

### E3 — catalogue arm crashed after completing its scored run

The catalogue arm completed all 30 targets (22 HELD, 8 CROSSED) and then
stalled during a supplementary third-path witness check, killed by the
watchdog. Its scored output is complete and is used as-is. Per the commitments
above this is reported, not re-run: re-running is disallowed as score-fishing,
and in any case the catalogue arm is deterministic lookup, so a re-run could
only reproduce it.

### Corrective for any future run

Run arms in separate containers or namespaces, or sequentially after the
previous session has exited — never concurrently on a shared box with readable
process tables. This document's isolation clause should be amended to cover
process visibility, not just file access. That amendment applies to the *next*
experiment; changing it now would be a post-hoc protocol change.
