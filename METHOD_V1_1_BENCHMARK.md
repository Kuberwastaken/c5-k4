# Method v1.1 prospective benchmark

**Status:** protocol design; no benchmark target has been selected or evaluated  
**Purpose:** test prospective calibration and intervention value, not maximize
the number of counterexamples

## Sampling unit and freeze

The sampling unit is a **question cluster**, not a Lean declaration. Sibling
variants and logical negations are one unit. This prevents two encodings of one
question from counting twice.

Freeze commit `C0` must contain:

1. the exact `formal-conjectures` commit and tree hash;
2. a deterministic inventory of open declarations;
3. a contamination manifest covering this repository's history and releases,
   sibling research repositories, and session-reference searches;
4. the fixed classifier, strata, transformation library, forecasts, budgets,
   scoring, and stopping rule;
5. a future public-randomness round used only after `C0` is public.

Machine-only registry and syntax scans are permitted if recorded. Any statement
whose semantics, residual, family, status, proof route, or candidate has already
been discussed is excluded. Identity or exposure ambiguity means exclusion.
WoW I and Graph Brain are categorically ineligible because they are not
DeepMind `formal-conjectures` targets.

At `C1`, the frozen future-randomness value selects exactly twelve clusters:

- three graph scalar-inequality clusters;
- three graph structural/property clusters;
- two finite algebra/equational clusters;
- two automata/game/process clusters;
- two finite combinatorial clusters.

If a stratum has too few uncontaminated units, the benchmark ends as
`NO_ELIGIBLE_BENCHMARK`. There is no backfill or relaxed exclusion. Manual
Phase-0 review occurs only after `C1`; every selected cluster remains in the
denominator even if it stops on certificate shape, source status, or prior art.

## Frozen forecasts

Each unit receives two probability vectors over:

```text
CROSS
ZERO_COMPLETE
THEOREM_STRUCTURE
PRESEARCH_STOP
TIMEOUT
PROTOCOL_INVALID
```

The `selection_forecast` is frozen at `C1` using only registry metadata and
development priors. The `intervention_forecast` is frozen after source
recovery, database controls, literal residual derivation, and wall analysis,
but before evaluating a proposed transformation. Probabilities use increments
of `0.05`, are neither zero nor one, and sum exactly to one.

## Equal-budget arms

Every runnable unit is evaluated in three isolated arms. Outcomes are not
shared until all three arms terminate.

1. `CATALOGUE`: fixed canonical arsenal and small-object catalogues.
2. `GENERIC`: deterministic seeded mutation or exhaustive finite search with
   no target-specific wall reasoning.
3. `WALL_NAVIGATION`: one target-specific transformation from the frozen
   library, chosen using exact equality, theorem subtraction, and a signed
   effect forecast.

The transformation library may include graph blow-ups, complements, line
graphs, subdivisions, block sums, lifts, and bounded edge surgery; algebraic
quotients, subalgebras, products, row-permutation reductions, and bounded table
surgery; defect-preserving automata letter surgery with explicit shortcut
risk; and state-normalization or corner/profile exchange for games/tableaux.

Only one transformation and one parameter grid are allowed in the wall arm.
No backup family can be activated after outcomes are visible.

## Budgets and evidence

Per runnable cluster:

- shared source/database/wall analysis: at most 600 CPU-seconds;
- each discovery arm: eight processes times 60 seconds, at most 480
  CPU-seconds;
- independent candidate verification: two additional 60-second processes;
- every subprocess has a hard 60-second wall cap;
- all three arms receive identical discovery CPU budgets.

Sequential checkpoints are mandatory:

1. `C0`: protocol, pool hash, contamination inventory, library, and priors;
2. `C1`: entropy-selected manifest;
3. per cluster: resolution card and source audit;
4. database/calibration ledger;
5. all arm contracts and forecasts, committed before any arm starts;
6. incremental result commits after every job or 15--20 rows;
7. independent verification and one terminal outcome.

Every ledger is append-only and hash-chained. Rows include benchmark, unit,
contract, transformation, carrier, and previous-row digests. Evaluation before
the unlock event is `PROTOCOL_INVALID`.

## Scoring and stopping

The primary metric is multiclass Brier score for both frozen forecasts. Brier
skill is measured against the frozen development-prior forecast:

```text
skill = 1 - Brier(method) / Brier(prior).
```

Arm comparisons report exact normalized residual/objective gain, paired
wall-versus-baseline wins/losses/ties, controlling-term sign accuracy,
CPU-normalized gain, and timeout/protocol-invalid rates.

Theorem yield is secondary:

- `1.0`: a proved theorem shadow/closure or warning-clean formal lemma;
- `0.5`: a preregistered theorem signal surviving its complete frozen audit
  and an independent countermodel check;
- `0`: a retrospective conjectural explanation.

Terminal precedence is:

```text
verified crossing
> theorem structure
> complete zero
> timeout
> presearch stop
> protocol invalid.
```

Novel, retro, ambiguous, and status-preempted crossings remain separate.
Multiple sibling declarations crossed by one object count once at cluster
level.

The benchmark supports `PREDICTIVE_SUPPORT` only if Brier skill is positive,
the wall arm beats both baselines in mean normalized gain with paired wins at
least losses, and controlling-term sign accuracy is at least 70%.
`DISCOVERY_SUPPORT` additionally requires an independently certified crossing
that received greater forecast probability than completed zeroes.

There is no early stop after a counterexample. All twelve clusters must reach
their frozen terminal states. Any new solver, family, target, or bound belongs
to a later benchmark version. One successful benchmark still does not license
the phrase “general discovery engine.”

## Required automation before C0

Add a benchmark schema and linter coverage for:

- upstream/tree/manifest and contamination-inventory hashes;
- future-randomness source, round, and value;
- strata quotas, cluster grouping, and no-backfill enforcement;
- exact rational probability-simplex validation;
- frozen development-prior and transformation-library hashes;
- all three arms, equal process/CPU budgets, grids, seeds, and `no_adaptation`;
- declaration paths confined to the pinned `formal-conjectures` tree;
- freeze-before-evaluation chronology and hash-chained ledgers;
- terminal-outcome/evidence consistency and ledger-derived aggregate scores.

No `C0` freeze is permitted until these checks are executable in CI.
