# Results — fresh-generation three-arm test

**Run completed 2026-08-16.** Protocol frozen at
[`PREREGISTRATION.md`](PREREGISTRATION.md) (tag `prereg-three-arm-v1`), before
the population existed; population frozen at tag `population-frozen-v1`;
adjudicator committed before any arm reported.

## Verdict: INCONCLUSIVE by the letter — and close to null in substance

| arm | CROSSED | HELD | BRACKET |
|---|---|---|---|
| catalogue | 8 | 22 | 0 |
| generic | 14 | 14 | 2 |
| wall | 15 | 15 | 0 |

**Amended 2026-08-16.** The generic arm was still running when this file was
first written; it had 14 CROSSED / 0 HELD / 16 BRACKET at that moment. It then
ran a further ~16 hours and resolved 14 of its 16 brackets — **into HELDs, not
CROSSEDs**. Its crossing set is unchanged, so the endpoint below is unchanged.
The table above is the completed run.

Scored targets: **30**.

| endpoint | value |
|---|---|
| **wall-unique crossings** | **1** (`FP-026`) |
| catalogue-unique | 0 |
| generic-unique | 0 |
| crossed by all three | 8 |

Applying the preregistered rule mechanically:

- **Supported** requires wall-unique ≥ 3 **and** ≥ catalogue total (8). Wall-unique
  is 1. **Not met.**
- **Falsified** requires wall-unique ≤ catalogue-unique (0). Wall-unique is 1.
  **Not met** — by a single target.
- Therefore: **INCONCLUSIVE**.

## What actually happened, stated plainly

The three arms nest almost perfectly:

```
catalogue (8)  ⊆  generic (14)  ⊆  wall (15)
```

The wall arm found **everything** the other two found, and exactly **one**
target more. That is the whole measured marginal value of tightness navigation
on this population: one conjecture out of thirty, over a control that is random
graphs plus annealing.

The verdict is "inconclusive" only because the falsification threshold was set
at wall-unique ≤ catalogue-unique, and catalogue-unique came out at 0 rather
than 1. Nobody should read the label as encouraging. The honest summary is that
**the method did not distinguish itself from generic search** on a population
built to suit it, and it cleared the falsification bar by the narrowest
possible margin.

## Caveats that cut both ways

**Against the method** — the population was *favourable to it by construction*.
Every target had `min_slack_over_D = 0`, so the wall arm was handed usable
tightness data on all 30; `GENERATION.md` recorded this in advance as "the most
favourable fair setting for the hypothesis".

**~~In its favour, weakly~~ — RETRACTED 2026-08-16.** The first version of this
section argued that the generic arm's 14 crossings were a lower bound, because
it had bracketed 16/30 and returned no HELDs, so more compute might have found
`FP-026` and taken wall-unique to 0. That speculation has now been settled by
the arm itself: given roughly 16 further hours it converted 14 of those 16
brackets, and **every one became a HELD, not a CROSSED**. Generic search found
no additional crossing with an order of magnitude more time.

The correction cuts both ways and both should be stated. It **removes** the
"budget-starved control" caveat — the control did reach a verdict on 28 of 30
targets, so the comparison was fairer than it looked. And it **strengthens**
the one positive datum: `FP-026` survived a control arm that had far more
compute than the wall arm spent (the wall arm's entire run was 724 s).

**Contamination (event E2)** — arms ran concurrently on a shared box and
cross-arm process-table visibility could not be excluded. As recorded *before*
the wall arm reported, any such leak inflates catalogue/generic and deflates
wall-unique. It cannot manufacture the observed result: even granting maximum
benefit of the doubt, the wall arm's own crossings are only 15 of 30, and 14 of
those were independently reached by annealing.

**The prespecified worthlessness condition was partly met.** "Targets so easy
that all three arms refute everything" — generic search alone refuted 14/30
with no structural insight at all. The population was not trivial (half of it
held), but it was easy enough that the discriminating power of the test was
low. The database edge at `n = 8` is the likely cause, and that too was
recorded pre-freeze.

## Findings worth keeping regardless of the verdict

1. **G3-lite does heavy work.** 756 sign checks were run and **691 (91%)
   stopped a trial before it was executed**. Whatever the navigation method's
   discovery value, the sign check is an effective filter against wasted
   trials — which is what it was added for after the 2026-08-14 wrong-sign
   stops.
2. **The sign check has a known failure mode: floor/ceiling step functions.**
   On `FP-008`, `FP-020`, `FP-026`, `FP-007`, `FP-023` the residual is a step
   function, so consecutive members of the obvious parametrisation give
   `dR = 0` and the literal §A3 test stops a family that in fact crosses. All
   five needed re-indexing (or subdivision instead of path-stretch). Any future
   version of §A3 must test across a *step*, not across adjacent members.
3. **The wall arm found a defect in the population's own generator.**
   `_spectral_bracket` computes `⌈λ₁⌉` by testing `det(⌊λ₁⌋·I − A) == 0`, which
   fires whenever *any* eigenvalue equals `⌊λ₁⌋`; **19 of 12,112** members of
   `D` get a wrong `spec_ceil`. Consequence: `FP-008`'s recorded
   `equality_count_in_D` is 7 where the truth is 6, and its witness list
   contains a non-tight member. Under the corrected reading all 30 targets
   still have zero counterexamples in `D`, so no target loses validity — but
   the tightness data one arm was handed was wrong on one target.
4. **Database gate passed cleanly**: the wall arm's independent evaluator
   reproduced min/max slack for all 30 targets over all 12,112 members, and
   equality counts for 29 of 30 (the exception being the `FP-008` defect
   above).

## What this does and does not license

It does **not** license the claim that tightness navigation prospectively finds
counterexamples generic search misses. On the only preregistered test ever run,
the margin was one target out of thirty, and the control arm was budget-starved
in a way that likely understates it.

It does **not** falsify the mechanism either. `n = 8` is a weak database edge,
`f`/`b`/`tree` — the invariants that carried the original C₅[K_m] case study —
were excluded from emission on runtime grounds, and one run on one population
is one data point.

The correct next step is **not** a seventh method version and **not** a rerun
of this design with tweaks. If the claim is to be tested again it needs a
harder population (larger database edge, hereditary induced invariants in the
vocabulary), an equal-and-sufficient budget for the control, and arms in
isolated environments. Absent that, the honest position is the one the
independent review already reached: the corpus-audit work is what this project
demonstrably does well, and the navigation claim remains unproven.

## Reproducibility

`scripts/exp/adjudicate.py` (committed before results), `scripts/exp/wall_*.py`,
`scripts/gen/`, raw arm outputs `arm-catalogue.{md,json}`,
`arm-generic.{md,json}`, `arm-wall.{md,json}`, gate log `arm-wall-dbgate.txt`.
Verdict recomputable from the three JSONs by set difference on `CROSSED`.
