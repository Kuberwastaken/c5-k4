# A109908/A109909 post-run search-arm diagnosis

**Decision:** `STOP_CURRENT_PURE_FINITE_PRIME_COVER_ARM`

**Scope:** This is a read-only post-run mathematical and search-design audit of
the completed DEVELOPMENT trial. It does not evaluate any new target value,
authorize a dispatch, change the 60-second cap, or make a conjecture-resolution
or novelty claim.

## Executive diagnosis

The completed run is strong evidence that the frozen execution, source gate,
ledger, factorization, and independent replay machinery worked. It is not
meaningful positive evidence that the counterexample search explored a broad or
promising domain.

More sharply, the bounded zero was already implied by target-free constructor
data. The constructor computed each profile's first uncovered position inside
the 262,144-position scoring prefix, and every emitted profile had such a gap.
The live evaluator then stopped at that same first position and accepted only a
profile with no uncovered position through `floor(n/2)`. Consequently none of
the 1,280 frozen profiles could have produced `FULL_COVER`, irrespective of the
particular CRT representative selected for that profile.

The correct response is therefore to stop this exact arm, add a mandatory
target-free viability gate, and test the profile-selection problem itself with
an exact SAT/CP-SAT formulation before considering another target dispatch.

## What the completed and invalid runs establish

The first workflow attempt, run `31835698077`, is strictly
`INVALID_PRE_EVALUATION_GATE_TIMEOUT`. It launched zero shards, visited zero
profiles, and evaluated zero candidate values. It teaches only that the v1 live
audit could not complete within its immutable cap; it is neither a bounded zero
nor mathematical evidence about the targets. See
[`invalid-run-31835698077.md`](invalid-run-31835698077.md), especially
"Evidence inventory" and "Disposition."

The corrected v1.1 run, `31836896948`, completed successfully. All 16 shard
terminals, all 22 ledger rows, all artifact checksum bundles, and all 16
independent replays passed. There were no search or verification deadlines and
no worker errors. That validates the evidence pipeline. The exact outcome was
15 `COMPOSITE_ESCAPE`, 7 `PRIME_ESCAPE`, zero `FULL_COVER`, and zero
`CAP_PREFIX`; see [`result.md`](result.md), "Immutable execution" and "Exact
shard outcomes," and [`result.json`](result.json), `aggregate`.

The distinction is important:

- **Execution evidence:** strong. The exact-commit lock, repaired live audit,
  canonical hash-chained ledgers, terminal accounting, exact escape
  factorizations, and independent Python 3.12 replay behaved as specified.
- **Counterexample-method evidence:** negative for this exact certificate arm.
  Its frozen profiles were known before dispatch to fail extremely early.
- **Evidence about A109908/A109909 themselves:** negligible. Exhausting this
  highly selected, pre-known-infeasible profile set is not evidence for either
  conjecture and does not approach a proof or disproof.
- **The 15/7 composite/prime split:** merely compute diagnostics. Both outcomes
  terminate the profile in the current code, so a composite first escape is not
  used to extend a counterexample certificate.

## Exact profile-domain reconstruction

The frozen constructor was reconstructed from the committed script and manifest
without invoking `coverage`, primality testing, factorization, or evaluating a
new target value. The committed file hashes match the hashes recorded in
[`freeze-files.json`](freeze-files.json).

The constructor emits a width-256 beam at each eligible depth 10 through 14:

| Depth | Selected-product modulus | Emitted profiles | Representatives in frozen interval | First-uncovered range in construction mask |
|---:|---:|---:|---:|---:|
| 10 | 6,469,693,230 | 256 | 22 | 66–96 |
| 11 | 200,560,490,130 | 256 | 0 | 90–120 |
| 12 | 7,420,738,134,810 | 256 | 0 | 104–134 |
| 13 | 304,250,263,527,210 | 256 | 0 | 126–164 |
| 14 | 13,082,761,331,670,030 | 256 | 0 | 140–174 |
| **Total** | — | **1,280** | **22** | **66–174** |

All 22 live trials were therefore the only representatives admitted by the
frozen interval, and all came from depth 10. The reported live first-gap range
of 66–96 exactly matches the target-free mask range for those admitted depth-10
profiles; see [`result.md`](result.md), "Exact shard outcomes."

The thinning is an expected arithmetic consequence of the profile constraints,
not an unlucky shard result. The interval
`1,000,000,001..1,500,000,000` has width 500,000,000, while the first eligible
modulus is 6,469,693,230. For one CRT residue class, the chance-sized fraction
of a complete residue period intersected by that interval is approximately

```text
500,000,000 / 6,469,693,230 = 0.07728.
```

Across 256 depth-10 profiles this gives a neutral occupancy scale of about
19.8 representatives; the observed count 22 is ordinary. At depth 11 the same
scale is only about 0.64 representatives across the whole beam, and it becomes
negligible thereafter. Thus the frozen interval and width-256 beam made the
profile domain highly selective in `n`.

This sparsity follows from a valid mathematical constraint. If `Q_profile` is
the lcm/product of the selected prime moduli and `Q_profile <= n/2`, then
`k=Q_profile` is uncovered because `f_n(k) = -1 (mod q)` for every selected
`q`. A complete cover therefore requires `Q_profile > n/2`. The contract states
this obstruction explicitly in "Frozen finite-prefix construction," and the
theory audit proves it in "Modular-cover lemma and mandatory caveats."

## Why selectivity is not the main failure

Making more profiles intersect the interval would increase the number of live
trials, but it would not repair the certificate method. The decisive defect is
that every emitted profile was already known to fail the necessary prefix-cover
condition.

The constructor forms a bit mask for positions `1..262144`, ranks states first
by the least uncovered position, and retains the best 256 states. See
[`scripts/prospective_oeis_a109908_a109909.py`](../../../../scripts/prospective_oeis_a109908_a109909.py)
functions `residue_masks`, `first_uncovered`, and `frozen_profiles` (currently
lines 346–385), together with [`manifest.json`](manifest.json), `construction`.
The evaluator recreates the same residue-class coverage from `k=1` and returns
immediately at the first zero label; only reaching `floor(n/2)` without a zero
can produce `FULL_COVER`. See the same script's `coverage` and `run_search`
functions (currently lines 394–445).

Exact mask counts show that the arm was not close to covering even its scoring
prefix:

| Depth | Uncovered positions among 262,144 | Median uncovered count |
|---:|---:|---:|
| 10 | 17,372–27,822 | 17,400 |
| 11 | 16,239–18,070 | 16,280 |
| 12 | 15,361–16,321 | 15,397 |
| 13 | 14,606–15,523 | 14,640 |
| 14 | 13,921–14,338 | 13,948 |

For the 22 interval-admissible depth-10 profiles specifically, 17,385–18,439
prefix positions remained uncovered. Adding four more primes moved the first
gap only from the 66–96 range to the 140–174 range and left roughly 5.3% of the
construction prefix uncovered at depth 14. Extrapolating that percentage is not
a proof about longer intervals, but the exact early gaps already prove that no
frozen profile was eligible for a pure cover certificate.

Changing only the candidate interval cannot remove these gaps: for all `n` in a
profile's CRT class, the selected root classes in `k` are identical. A larger
beam, extra shards, a longer run cap, or a flat enumeration of more CRT
representatives would therefore multiply known early escapes. Those changes
would be brute-force theater rather than a principled response to the result.

Adding composite moduli or prime powers without another idea also does not
broaden the basic divisibility cover: if a composite `q` divides `f_n(k)`, each
prime factor of `q` divides it, so the composite root set is contained in the
corresponding prime-factor root sets. More small primes may improve a prefix,
but the observed marginal scale and the finite-lcm obstruction give no present
mathematical justification for assuming they can bridge from `O(10^2)` first
gaps to a literal half-range of at least 500 million positions.

## Mandatory no-dispatch viability gate

Every future version of this search family must fail closed before target
evaluation unless all of the following are demonstrated using target-free
profile data:

1. At least one frozen profile is CRT-admissible under the predeclared novelty
   range or canonical-representative rule.
2. At least one such profile covers the **entire predeclared construction
   prefix**, i.e. `first_uncovered = construction_prefix_k + 1`. Merely ranking
   profiles by a larger but still finite first gap is insufficient because full
   literal coverage necessarily implies construction-prefix coverage.
3. The design gives an auditable bound on the remaining certificate burden,
   rather than assuming that prefix success extrapolates to `floor(n/2)`.
4. A worst-case independent replay fixture for the proposed certificate shape,
   including any residual factor records, completes below 60 seconds with a
   declared safety margin.

Had item 2 existed in v1.1, it would have rejected the campaign before all 22
target evaluations.

## Cheapest principled next step: exact target-free optimization

Before another dispatch, formulate the profile problem as SAT or CP-SAT.

For every permitted modulus `q`, introduce exactly-one variables for its
attainable residues `r = k + k^(-1) (mod q)`. For each prefix position `k`, add
a coverage clause requiring at least one selected residue equal to its
prescribed residue for a modulus where `k` is invertible. Then use incremental
prefix lengths or binary search to determine the maximum satisfiable initial
interval. The result should be either:

- a profile whose exact prefix coverage exceeds the new no-dispatch threshold;
  or
- a solver-checkable unsatisfiability/upper-bound certificate showing that the
  divisor universe cannot cover beyond a stated `k`.

First solve the unconstrained coverage problem. If it already has only a
microscopic maximum prefix, the interval cannot rescue it. Only after that test
passes should the model incorporate CRT representative feasibility in the
predeclared `n` domain. This separates the mathematical viability question from
the interval-occupancy question and avoids spending target evaluations on a
known-infeasible profile set.

If exact optimization justifies another beam-based implementation, make the
beam interval-aware: retain states that have an actual representative or a
provably feasible lift at the first eligible depth. That would address the fact
that 234 of the 256 depth-10 profiles and all later profiles produced no live
trial. It is an efficiency correction, not by itself an iterate criterion.

## Hybrid residual certificates

The theory audit permits a compact residue cover plus individually certified
residual positions: every uncovered representative may carry an exact proper
factor. See [`theory-and-prior-claim-audit.md`](theory-and-prior-claim-audit.md),
"What a complete counterexample certificate must contain."

This is mathematically legitimate but not presently operationally justified.
The current best profiles leave about fourteen thousand residual positions in
only 262,144 entries. A naive continuation to a half-range above 500 million
would suggest tens of millions of residual records, which is incompatible with
the compact-certificate goal and 60-second replay discipline. No such
extrapolation should be treated as a theorem, but it is sufficient to reject a
naive "continue after composite escape" patch.

A hybrid arm may iterate only if a target-free construction reduces the exact
residual set to a small, predeclared maximum and the worst-case independent
factor-and-coverage replay passes under the existing cap. The allowed residual
budget must be frozen before target evaluation.

## Ranked recommendation and decision criteria

1. **STOP** retries of v1.1 and variants that change only shards, runtime,
   interval width, representative count, or modest beam width.
2. **ADD** the mandatory no-dispatch prefix viability gate above.
3. **RUN TARGET-FREE ONLY** an exact SAT/CP-SAT maximum-prefix analysis of the
   allowed modulus universe.
4. **ITERATE CONDITIONALLY** with interval-aware profile retention only after
   exact profile viability is demonstrated.
5. **CONSIDER A HYBRID** only after exact residual counts and worst-case replay
   benchmarks establish compactness under 60 seconds.
6. **RETIRE** this modular-cover family if the exact optimizer bounds the best
   first gap far below the construction prefix, or if every viable profile's
   residual certificate exceeds the frozen storage/replay budget.

A further target run is mathematically justified only when a new versioned
design changes the scale of the method, not merely its amount of compute.
Acceptable iterate evidence would include at least one of:

- exact full coverage of a substantial predeclared construction prefix by a
  CRT-admissible profile;
- a solver-certified improvement by orders of magnitude as the divisor
  universe grows;
- a new compact divisor-family or interval decomposition with a proved coverage
  property; or
- a sparse hybrid residual bound whose independent worst-case replay fits the
  60-second cap with margin.

Absent such evidence, the correct classification remains
`METHOD_ARM_RETIRED_AFTER_PREDETERMINED_BOUNDED_ZERO`.

## Current source status and prior claim

As checked on 2026-08-14, the maintained public sources still describe both
statements as open:

- [OEIS A109908](https://oeis.org/A109908) and
  [OEIS A109909](https://oeis.org/A109909) record the positivity assertion as a
  conjecture and its historical verification through `10^9`.
- The current Formal Conjectures sources for
  [A109908](https://raw.githubusercontent.com/google-deepmind/formal-conjectures/main/FormalConjectures/OEIS/109908.lean)
  and
  [A109909](https://raw.githubusercontent.com/google-deepmind/formal-conjectures/main/FormalConjectures/OEIS/109909.lean)
  remain tagged `@[category research open]` with `sorry`.

The directly relevant 2024 Niu--Zhang preprint is a prior public proof claim and
must continue to be disclosed. It does not resolve the targets: its `mu=0`
stationary branch is feasible with objective `-l/4`, so it cannot be the claimed
global maximum, and the asserted positive minimum does not follow. The exact
defect and an explicit feasible point are recorded in
[`theory-and-prior-claim-audit.md`](theory-and-prior-claim-audit.md), "Decisive
failure in the preprint's proof," and
[`murthy-preprint-source-recovery.md`](murthy-preprint-source-recovery.md),
"Fatal proof defect."

The conjectures' continuing open status makes a genuinely new method eligible;
it does not supply positive justification for repeating this search arm.
