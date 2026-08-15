# Method v1.5 empirical selector

**Status:** `DEVELOPMENT`

**Scope:** adaptive target/family selection for the repository's live research
loop. This document is not a preregistration, held-out result, or confirmatory
success-rate claim.

This selector is deliberately separate from
[`METHOD_V1_5_BENCHMARK.md`](METHOD_V1_5_BENCHMARK.md). The benchmark admits
only future clusters introduced after its public P1/U1 chronology and fixes
its own target-blind sampling rule. Nothing in this document changes that
population, its contamination rules, its quotas, or its three equal-budget
arms. A target discussed here is `DEVELOPMENT` evidence and cannot be moved
into the future-cohort denominator.

## Decision rule

Apply `G0` through `G4` before evaluating any target instance. Failure of any
gate is a strict stop for the proposed target/family pair. Passing a gate says
only that the pair is eligible for a frozen trial; it is not evidence that the
conjecture is false.

### G0 — claimable finite resolution

All of the following must hold:

- the exact current statement has a finite artifact that can settle the
  intended question or cross the literal declaration;
- its source status, interpretation, theorem range, public issue/PR surface,
  and local duplicate surface are pinned;
- the proposed parameter domain is outside every accepted proof or completed
  computation that already settles it; and
- the proposed mechanism is not already present in a source, paper, public
  claim, or prior local campaign.

An `answer(sorry)` wrapper is not automatically disqualifying, but the
resolution card must say whether the artifact resolves the intended
right-hand proposition, the literal biconditional, or only a variant.

### G1 — compressive, nondegenerate wall

Require at least one of these two certificates:

1. a source-faithful parametric carrier has exact residual zero or integer
   slack at most one; or
2. a lossless necessary-form reduction shrinks the flat candidate universe by
   at least a factor of `1000`.

Degenerate empty/zero hosts, a small numerical residual without a family
identity, and a heuristic proxy do not pass. The wall coordinate and its
orientation must be written before target evaluation.

### G2 — target-free constructor reachability

Count every exact existence condition between the proposed parameters and a
legal target instance: integrality, square-discriminant, primality, S-unit,
simultaneous block, graph-premise, or analogous conditions. Call the number
of unresolved conditions `B`.

Require `B=0`. An otherwise positive `B` is cleared only by one of:

- a symbolic constructive parametrization proving infinitely many legal
  instances; or
- a frozen target-free pilot over at most `1,000,000` constructor descriptors
  that produces at least `32` canonical applicable instances at density at
  least `10^-4`.

The pilot may test syntax, constructor equations, target hypotheses, theorem-
domain exclusions, and canonical identity. It may not call the target
residual, objective, membership predicate, or candidate classifier. Zero
reachable rows is stronger than a bounded target hold and terminates the arm.

### G3 — signed invariant separation

Before evaluation, provide a decomposition

```text
R(theta) = R0 + A(theta) + E(theta),
```

where `R` is the oriented residual, `A` is the deliberately changed invariant
coordinate, and `E` contains every coupled side effect. The proposed move must
improve the residual by at least one integer unit or cross one exact rounding
shelf. A proof-bound on `E` must preserve that direction. At least one
obstruction invariant must be certified on the children; counting destroyed
parent witnesses or using a throughput proxy is insufficient.

### G4 — exact bounded replay

The first apparent crossing must admit an independent exact replay within one
60-second process tree. The replay must not import the discovery evaluator's
objective helper. If the required certificate cannot plausibly fit that cap,
the pair is deferred before search rather than allowed to emit an unverifiable
candidate.

Workflow source locks, attestations, and activation controls are a separate
dispatch-readiness layer. A failed workflow with zero target rows does not
change the mathematical score, but it blocks execution until a fresh disabled
run passes.

## Score after the gates

Only pairs passing `G0`--`G4` receive a priority score:

| Feature fixed before evaluation | Points |
|---|---:|
| symbolic/infinite reachability, or the full `G2` finite threshold | `+3` |
| exact equality or gap-one parametric wall | `+2` |
| lossless compression by at least `1000` | `+2` |
| certified signed one-coordinate separation | `+2` |
| independent exact replay comfortably inside 60 seconds | `+1` |
| the same family can test an adjacent untouched conjecture without changing its grammar | `+1` |
| material source-reading ambiguity | `-1` |

- `score >= 8`: run after an immutable freeze and dispatch gate;
- `score 6..7`: reserve; improve the certificate before evaluation;
- `score <= 5`: retire the proposed pair.

The score ranks already eligible pairs. It cannot compensate for a failed
hard gate.

## Saturation stop

Retire a frozen family after at least `1,000` exact applicable rows if at least
`80%` are equality rows and none crosses. Reopening requires a newly proved
child-invariant coordinate, not a larger order, longer timeout, new random
seed, or another copy of the same constructor.

This rule would have stopped further unchanged pairing work after the
TxGraffiti phase-three prefix: `2,575` exact rows, `2,235` equalities
(`86.8%`), and zero crossings
([evidence](results/expansion/live-search-2026-08-14/txgraffiti-cc-phase3-result.md)).

## Retrospective calibration

This table calibrates the rule; it is not a prospective success-rate result.

| Target/family | Pre-evaluation features under this rule | Selector verdict | Recorded outcome |
|---|---|---|---|
| WOWII 181 / triangular graphs `T(n)` | exact carrier wall, explicit one-parameter legal family, `alpha` separated from `lambda_max`, cheap exact replay, adjacent-cluster leverage; one reading caveat | retain, score `8` | `T(7)` crosses the formalized square-degree reading ([audit](results/expansion/wowii_181_formalized_reading_audit.md)) |
| WOWII 176 then 172 / two triangles joined by a path | exact diameter-two wall, legal `D_L` family, closed-form metric separation, one grammar tests the adjacent statement | retain, score `9` | infinite crossings for 176 and 172 ([176](results/expansion/wowii_176_disproof.md), [172](results/expansion/wowii_172_disproof.md)) |
| WOWII 430a / nonuniform `P7` clique blow-ups | quotient-coordinate compression, legal positive integer family, center geometry separated from the Caro--Wei floor, exact replay | retain, score `10` | order-53 witness and infinite scaling family ([evidence](results/expansion/wowii_430a_disproof.md)) |
| Graffiti3 Conjecture 2 / double stars | exact star wall, explicit double-star family, hub split crosses one radical shelf, exact replay | retain, score `8` | `DS(k,k)` crosses for every `k>=12` ([evidence](results/expansion/live-search-2026-08-14/graffiti3-conjecture2-result.md)) |
| OEIS A113019 / `n=d^r` | lossless necessary form, more than `1000`-fold compression, complete finite coordinate set, exact replay | retain, score `8` | recovered `9^9` and the complete fixed-point set ([evidence](results/expansion/live-search-2026-08-14/oeis-113019.md)) |
| OEIS A056777 v3 / triple--triple surgery | multiple Diophantine reconstruction conditions and no reachable second block | reject at `G2` | `27,528,192` constructor rows, `749` integral intermediates, zero reconstructed prime blocks ([evidence](results/expansion/live-search-2026-08-14/oeis-a056777-v3-reachability/preflight.md)) |
| OEIS A056777 v4 / power--triple surgery | square-discriminant bottleneck without a parametrization | reject at `G2` | `10,967,040` profiles and zero square discriminants ([evidence](results/expansion/live-search-2026-08-14/oeis-a056777-v4-reachability/preflight.md)) |
| Erdos 373 / factorial-product band `17..256` | the entire proposed band is already theorem-covered and exact-path races are open | reject at `G0` | strict source-bound stop; no target rows ([evidence](results/expansion/live-search-2026-08-14/erdos373-maximal-solution-development/source-bound-gate.md)) |
| Erdos 375 / smooth-number Hall construction | published same-wall transfer plus unresolved S-unit and all-composite-block existence | reject at `G0` and `G2` | duplicate/reachability strict stop; no target rows ([evidence](results/expansion/live-search-2026-08-14/erdos375-grimm-development/preflight.md)) |
| next held-out rotations | no chronology-qualified graph or arithmetic cluster existed | reject at `G0`; do not fabricate a ranking | both qualified sets were empty ([graph](results/expansion/live-search-2026-08-14/next-heldout-graph-rotation-strict-stop.md), [arithmetic](results/expansion/live-search-2026-08-14/next-heldout-arithmetic-rotation-strict-stop.md)) |

## Frozen next-ten evaluation

The next empirical test consists of the first ten new `DEVELOPMENT` target/
family pairs that pass `G0`--`G4` and score at least `8` after this rule is
frozen. For every pair:

1. record `G0`--`G4`, `B`, every score feature, and the family grammar before
   target evaluation;
2. retain every intervening rejected pair in a gate ledger with zero target
   calls, but do not substitute it into the ten-pair denominator;
3. give every admitted pair the same frozen catalogue, generic, and wall-arm
   budgets and the repository's 60-second process cap;
4. count every pair in its original score bucket, including bounded zeroes,
   infrastructure-invalid runs, ambiguities, and theorem shadows; and
5. permit no post-result score, threshold, family, or bucket change.

The selector earns the description **counterexample selector** only if these
ten pairs produce at least one independently verified crossing. As a secondary
arm-level test, wall navigation must beat both equal-budget catalogue and
generic arms in exact crossing count or exact near-wall incidence on at least
three of the ten pairs. If ten score-qualified pairs produce zero crossings,
the counterexample-selection claim is falsified. The rule may still be
reported as a wall-finding or theorem-shadow heuristic.

This adaptive next-ten experiment remains `DEVELOPMENT`; it does not replace
or contribute observations to the future-cohort benchmark.

## Current ranking

There is exactly one current preflight candidate. It was frozen before this
selector and remains a legacy `DEVELOPMENT` arm under its own audited contract;
it cannot enter the prospective next-ten denominator or derive execution
authority from this document:

1. **Bondy longest cycles / `K4 join H`, where `H` is a balanced delete/add
   rewire of `5K4`.** The source family is exactly one degree below the rounded
   premise, the proposed surgery raises that premise by one, and the separator/
   path-cover coordinate identifies the obstruction
   ([preflight](results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/preflight.md),
   [mathematical audit](results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/math-audit.md)).
   Its existing target-free calibration completes all 96 frozen constructor
   rows and certifies the degree wall, theorem-range subtraction, induced-claw
   condition, and non-monotone grammar. A post hoc score still remains
   provisional because the new `G3` leakage-bound form was not preregistered
   before this arm was frozen. Its own contract—not this selector—controls
   whether a target process may run. Any later Bondy-family arm must satisfy
   `G0`--`G4` prospectively from scratch.

There is no rank two. A056777 v5, Erdos 375, Sidorenko, A103151, and another
unchanged TxGraffiti pairing do not currently pass the hard gates. They must
not be promoted merely to keep a worker busy. The graph and arithmetic
held-out queues are independently recorded as empty at the current pins.

The Bondy workflow's earlier v3.2 run is operational evidence only: it emitted
a canonical gate failure and skipped the target
([record](results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/invalid-run-31852437717.md)).
It neither supplies a mathematical row nor lowers the pair's scientific
priority; a passing fresh disabled gate remains mandatory before any later
activation.
