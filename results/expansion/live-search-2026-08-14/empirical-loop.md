# Empirical live-search loop: what worked, what failed, what changes next

Date: **2026-08-14 UTC**  
Scope: live development runs against
`google-deepmind/formal-conjectures@b33d8678a28118c95d8d4f60b11faaf39ccff1e6`;
not an uncontaminated or preregistered benchmark.

## Bottom line

The run produced one new answer to an intended mathematical source question,
three separately classified formalization/source defects, and a broad set of
bounded zeroes.  The strongest methodological evidence is OEIS A113019:

```text
flat catalogue through 1,000,000       -> only known fixed points 1,32
50,000 stratified random integers      -> only known fixed points 1,32
necessary-form wall n=d^r              -> new fixed point 9^9
exact reduction                         -> complete list 1,32,9^9
```

This is a prospective arm win, not a retrospective explanation.  It supports
the claim that exact invariant coordinates can outperform flat and generic
search.  It does not yet establish a generally high-success discovery engine:
most other live wall arms produced equality, bounded zeroes, or worse residuals
than the generic baseline.

## Gate-surviving outputs

| finding | mathematical standing | decisive mechanism | public result |
|---|---|---|---|
| OEIS A109074 | merged formal declaration and as-written ratio fail at `n=1`; source/index plus local-reference defects; not a corrected-identity disproof | literal first admissible input plus authoritative A005156 terms | [release](https://github.com/Kuberwastaken/c5-k4/releases/tag/oeis-109074-formalization-v1) |
| OEIS A111291 | merged real-domain declaration fails at `x=3/2`; intended integer phenomenon passes through one million; endpoint erratum | domain-topology boundary, not integer substitution | [release](https://github.com/Kuberwastaken/c5-k4/releases/tag/oeis-111291-formalization-v1) |
| OEIS A113019 | intended question answered; literal fixed points are exactly `1,32,9^9` | necessary form `n=d^r` | [release](https://github.com/Kuberwastaken/c5-k4/releases/tag/oeis-113019-fixed-points-v1) |
| Bateman--Horn count helper | includes zero and differs at upper endpoint; asymptotically inert; not a theorem disproof | source-domain comparison at discontinuities | [release](https://github.com/Kuberwastaken/c5-k4/releases/tag/bateman-horn-count-endpoint-v1) |

The A113019 release remains marked Latest.  The Bateman--Horn validation
release was explicitly published with `--latest=false`.

## Empirical arm comparisons

### Wall navigation won decisively once

A113019 is the clean success.  The wall was not “nearby values”; it was the
defining equation itself.  Every positive fixed point must be `d^r`, where
`d` is its decimal digit count and `1<=r<=9`.  Searching those coordinates
found a witness missed by both flat arms, then yielded a complete finite
classification.

A108129 supplies a non-novel positive control for the same principle.  Flat
and random exponent screens left unresolved rows, while the mod-24 covering
wall uniquely recovered the known Riesel endpoint `509203` and its exact six-
prime certificate.  It found nothing smaller, so it is calibration rather
than discovery.

### Structural constraints improved validity without improving the objective

The second Černý run fixed the first run's premise waste.  Holding a 13-cycle
and ranging rank-12 defect maps changed the exact synchronization rate from
roughly 8% to `25,331/25,331`, but the best reset length remained the known
equality `144`.  This validates the transformation family while falsifying the
hope that premise preservation alone moves the extremal objective.

For Erdős 835, complement quotienting halved the variables and a balanced
large-set wall enforced the exact `8,398` blocks per color.  It beat the
catalogue residual by 414,031, but the unconstrained generic arm was still
14,799 better.  Known necessary equalities are therefore valuable search
coordinates, not automatically good local objectives.

### Equality walls often behaved like theorem shadows

Wave-two navigation for WOWII 40, 61, and 133 evaluated direct moves, neutral
corridors, and equality rays.  All three repeatedly stopped at exact residual
zero.  Fresh graph arms likewise recovered Petersen equality for the
Alon--Tarsi cycle-cover bound and many tight Erdős 628 splits without crossing.
These are targets for structural theorem work or stronger preserving moves,
not justification for extending the same random walk.

### Two attractive proxies failed

- Forty-eight randomized transversal attempts made Latin-square navigation
  roughly three orders of magnitude cheaper, but a proxy score of zero still
  hid at least 256 exact transversals.  Its retained exact table had 3,533
  transversals, worse than the first wave's 3,404.  Throughput without a
  certified relation to the wall is not useful progress.
- Adding a third rank-12 defect letter repaired synchronization in many Černý
  automata but introduced shortcuts; the best exact reset length was only 50.
  A transformation can preserve the premise while destroying the extremal
  geometry.

Both proxies are removed from priority use.

## Status gates saved compute and prevented false claims

The live process rejected several attractive rows before novelty counting:

- A100434 is literally false, including all three identities at `n=0`, but
  closed upstream PR #4560 already reports the underlying sign defect.
- A211417's `D=0` vacuity is already tracked by upstream issue #4923.
- Claude's Cycles was preempted by open, CI-green PR #4935 and a revised source.
- A037274 was removed from a fresh lane after prior-report subtraction found
  existing automata work.

The actual PR #4450 scope also contains 73 OEIS files, not the stale “64” in
its title.  The completed boundary audit reconciled 342 mapped primary numeric
or membership checks with authoritative b-files and found no additional fresh
prefix mismatch.

## Runtime changes justified by failures

The first replay exposed missing production executables, buffered output,
inconsistent counters, and lossy identity shortcuts.  The resulting minimal
live runtime now supplies:

- exact fail-closed `labelg` canonicalization;
- a fresh per-tree, hash-chained JSONL stream;
- immediate append, flush, and `fsync` after every evaluated candidate;
- uniform `proposed -> canonical_unique -> hypothesis_survivor ->
  exact_evaluated -> objective_scored` counters;
- a hard 60-second process-group cap;
- independent canonical replay and a scientific-output linter.

Twenty-eight focused and adjacent tests pass.  This is the runtime required
for future live arms; it does not replace the separate frozen benchmark
protocol.

## Revised live-search procedure

The next development cohort should execute these gates in order:

1. **Status/source gate before compute.** Search open, closed, and merged work,
   source revisions, and prior local reports.
2. **Resolution-shape gate.** State exactly what finite artifact would settle
   the intended question or cross the literal declaration.  Keep opaque
   `answer(sorry)` wrappers distinct from their witness-bearing RHS.
3. **Literal boundary and authoritative-reference gate.** Evaluate every
   admissible endpoint, every domain discontinuity, and the first external
   sequence terms before scheduling broad search.
4. **Wall-compression score.** Prefer targets where a necessary equation
   reduces the flat universe by orders of magnitude, as `n=d^r` did.  A small
   residual alone is insufficient.
5. **Three equal-budget arms.** Catalogue, generic, and wall navigation must
   share the same cap and emit durable exact rows through the new runtime.
6. **Independent candidate replay and classification.** Separate intended
   mathematical answers, false formal declarations, source errata, helper
   definition defects, known/preempted results, and bounded zeroes.
7. **Release only gate-surviving findings.** The title and opening paragraph
   must expose every interpretation or formal-wrapper caveat.

## Thesis update

The repository can now defend a bounded claim:

> Tightness and necessary-form structure can prospectively guide exact
> counterexample or witness discovery in machine-generated formal-conjecture
> corpora, and can outperform flat and generic search on selected targets.

It still cannot defend “general counterexample engine.”  This live cohort was
adaptive and development-facing, and one genuine wall-arm discovery does not
measure a held-out success rate.  The next strong evidentiary step remains a
fresh, frozen cohort whose targets and equal-budget arms are fixed before
semantic inspection, using the now-tested runtime and reporting every zero.

The practical search loop should continue in parallel with that benchmark:
the former finds and improves; the latter estimates whether the improvement
generalizes.
