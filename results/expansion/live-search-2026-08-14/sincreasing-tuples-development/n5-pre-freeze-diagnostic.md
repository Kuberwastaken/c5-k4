# Strong 2-increasing-tuples bound: observed-before-freeze n=5 diagnostic

**Audit date:** 2026-08-14 UTC

**Protocol classification:** `PROTOCOL_DEVIATION / DEVELOPMENT`

**Disposition:** `N5_ARM_THEOREM_BLOCKED`

**Scoring status:** `NOT_SCOREABLE`

This file records computations that were run while designing the proposed
order-five arm, before a constructor, evaluation order, implementation, and
independent verifier had been frozen. They therefore are not a frozen bounded
result, not a prospective trial, and not evidence for the benchmark success
rate. They produced no counterexample and authorize no release, issue, pull
request, workflow dispatch, or other public action.

## Literal target and integer crossing threshold

The target is
`Arxiv.«1609.08688».maximalLength_le_strong`:

```lean
theorem maximalLength_le_strong (n : ℕ) : F n ≤ Real.sqrt n ^ 3 := by
  sorry
```

Here `F n` is the supremum of the lengths of lists of triples in `[1,n]^3`
for which every earlier triple is strictly smaller than every later triple in
at least two of the three labelled coordinates. `List.Pairwise` requires all
earlier/later pairs, not only adjacent pairs.

At `n=5`, the real right side is

```text
(sqrt 5)^3 = 5*sqrt 5.
```

The exact squared comparisons are

```text
11 < 5*sqrt 5    because 121 < 125,
5*sqrt 5 < 12    because 125 < 144.
```

Consequently the declared inequality at five is equivalent, for the
natural-valued `F 5`, to `F 5 ≤ 11`. A counterexample must have length at
least 12. A length-10 or length-11 list cannot refute this declaration.

## Authoritative order-four equality wall

The Gowers--Long paper and the prior exact order-four certificate both give
the following eight-term extremizer:

```text
(1,1,1)
(1,2,2)
(2,1,3)
(2,2,4)
(3,3,1)
(3,4,2)
(4,3,3)
(4,4,4)
```

Direct replay checks all 28 earlier/later pairs. An exact bit-mask Bellman
recurrence over the 64 triples in `[1,4]^3` gives

```text
F(4) = 8
reachable recurrence states = 527
observed end-to-end Python time = 0.005244 seconds
```

The same recurrence has exactly 12 labelled optimal ordered sequences of
length eight. No coordinate quotient was used when counting them.

For a candidate mask `M`, with `out(v)` the mask of triples `w` satisfying
`v <₂ w`, the recurrence was

```text
D(0) = 0
D(M) = max { 1 + D(M ∩ out(v)) : v ∈ M }.
```

Every child has smaller cardinality because `v ∉ out(v)`. The recurrence
therefore terminates and represents the full pairwise list condition: each
successive intersection retains only triples compatible with every earlier
choice.

## Complete observed equality-wall insertion diagnostic

The diagnostic enumerated the following finite family without symmetry
quotients:

1. all 12 labelled order-four extremizers, in lexicographic recurrence order;
2. all `5^3 = 125` coordinatewise order-preserving injections
   `[4] → [5]`, encoded by the omitted value in each labelled coordinate;
3. the 61 triples outside the resulting embedded `4 × 4 × 4` box; and
4. every cut `0,...,8` compatible with the complete embedded base prefix and
   suffix.

A triple has at most one compatible cut: compatibility at two distinct cuts
would require it to be both directions of `<₂` with an intervening base
triple. For each embedded base, an exact DFS intersected the remaining node
mask with the current triple's `out` mask and required nondecreasing cut
indices. This allowed either tuple order within a shared cut whenever the
literal directed relation allowed it; lexicographic tuple order was not
silently imposed as a mathematical constraint.

All `12 × 125 = 1,500` cases were exhausted. Their maximum insertion-depth
distribution was:

| Maximum compatible insertions | Embedded bases |
|---:|---:|
| 0 | 72 |
| 1 | 840 |
| 2 | 588 |
| 3 or more | 0 |

The observed end-to-end enumeration time, including reconstruction of the 12
bases, was 1.794265 seconds. Thus this entire insertion grammar reaches length
at most ten, two terms below the required crossing length.

One best case starts from the displayed order-four extremizer, uses omitted
values `(1,1,2)`, and embeds its base as

```text
(2,2,1)
(2,3,3)
(3,2,4)
(3,3,5)
(4,4,1)
(4,5,3)
(5,4,4)
(5,5,5)
```

Inserting `(1,1,1)` at cut zero and `(1,3,2)` at cut one gives the valid
length-10 list

```text
(1,1,1)
(2,2,1)
(1,3,2)
(2,3,3)
(3,2,4)
(3,3,5)
(4,4,1)
(4,5,3)
(5,4,4)
(5,5,5)
```

All 45 earlier/later pairs in this list satisfy the literal `<₂` relation.

## Exact unrestricted order-five diagnostic

Two separately encoded models were also evaluated before freeze.

### Model A: complete bit-mask Bellman recurrence

The order-four recurrence above was rebuilt over all 125 lexicographically
ordered triples in `[1,5]^3`, without requiring an embedded order-four
subsequence. It returned

```text
F(5) = 10
reachable recurrence states = 6,552
observed end-to-end Python time = 0.082120 seconds
```

Hence the failed insertion crossing is not merely a limitation of the chosen
wall grammar: no order-five list of length 11 or 12 exists under the literal
formal relation.

### Model B: independent one-hot SAT encoding

The second model did not reuse the Bellman adjacency table. For each list
position, labelled coordinate, and value in `1..5`, it used exactly-one
Boolean variables. For every earlier/later position pair and coordinate, a
separate Boolean was constrained against all 25 ordered value pairs and the
three coordinate Booleans were required to contain at least two strict
increases.

The observed Glucose4 results were:

| Requested length | Result | Variables | Retained clauses | Solve time |
|---:|:---:|---:|---:|---:|
| 10 | SAT | 285 | 3,840 | 0.000906 s |
| 11 | UNSAT | 330 | 4,426 | 0.034486 s |
| 12 | UNSAT | 378 | 5,254 | 0.031771 s |

The SAT length-10 result independently agrees with the Bellman optimum. The
UNSAT solver observations are corroboration, not durable proof certificates;
the recurrence-closed Bellman table is the appropriate independently
replayable exact certificate shape.

## Required interpretation and protocol consequence

The observed equality is `F(5)=10`, so

```text
F(5) = 10 < 5*sqrt 5.
```

The order-five arm is therefore theorem-blocked from producing the required
length-12 witness. Continuing to tune its base order, cuts, solver, branch
order, or runtime cannot change that mathematical fact.

Because all target rows above were observed before freeze, this document must
not be relabelled `HOLD_BOUNDED`, `DOMAIN_EXHAUSTED`, or a prospective negative
result. The only valid classification is an observed-before-freeze
`PROTOCOL_DEVIATION / DEVELOPMENT` diagnostic. There is no candidate and no
release.

## Methodological choices after the stop

Without evaluating another value of `n`, the method now has three clean
choices:

1. **Retire this target from the immediate prospective queue.** Preserve the
   exact order-five obstruction as development knowledge and choose a
   different current formal target with a still-live integer crossing.
2. **Turn the negative observation into tooling calibration.** Freeze a
   target-free replay format for recurrence-closed finite certificates,
   independent relation reconstruction, full pair tables, exact threshold
   arithmetic, and solver-disagreement stops.
3. **Design a new, separately frozen larger-order experiment.** Any new order,
   product construction, unequal-box construction, or relaxed wall grammar
   must receive a new preflight, source/status gate, database-sanity gate,
   fixed evaluation order, and 54/60-second stop before its first target row
   is observed. This file supplies no authorization or prediction for such an
   experiment.
