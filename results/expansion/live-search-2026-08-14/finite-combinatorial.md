# Live finite-combinatorial search — 2026-08-14

**Lane:** currently open finite-combinatorial declarations in
`google-deepmind/formal-conjectures` that were not already resolved by the
expansion campaign.  **Terminal result:** `ZERO_BOUNDED` on three clusters;
zero candidate crossings.  This is development evidence, not a proof of any
universal statement and not a release candidate.

## Live source and status audit

The audit used GitHub's live API and raw `main`, not only the older local
registry.  At `2026-08-14` the upstream head was
`b33d8678a28118c95d8d4f60b11faaf39ccff1e6` (committer timestamp
`2026-08-13T23:56:30Z`).  All declarations below remain literally tagged
`@[category research open]` at that head.

| cluster | live path/blob | exact declarations searched | merged/open audit |
|---|---|---|---|
| arithmetic theta sum | `FormalConjectures/Arxiv/2501.03234/ArithmeticSumS.lean`, blob `d9d5fe56ab73d2d72a6926f89f0321332f509e01` | `conjecture_1_1`, `conjecture_4_1`, `conjecture_4_2`, `conjecture_4_3`; `conjecture_4_4` only receives bounded evidence | PR #616, which added 4.1--4.4, merged `2025-08-28`; an exact repository issue/PR search found no current resolving PR for `ArithmeticSumS` |
| tight union-closed family | `FormalConjectures/Wikipedia/UnionClosed.lean`, blob `b693d7d96203e976c145d6fc957c84d898ebc0dc` | `union_closed.variants.cardinality_even_of_union_closed_tight` | statement-introduction PR #684 merged `2025-09-25`; the base conjecture's PR #123 merged `2025-08-04`; exact search found only open docstring issue #3596 and no resolving PR; closed PRs #2599/#3123 concern already-tagged solved variants, not this declaration |
| semi-magic square of cubes | `FormalConjectures/Wikipedia/MagicSquares.lean`, blob `e23096fef51be05110f9a02493826c0fcf088bd8` | `exists_semi_magic_square_cubes` | source PR #3578 merged `2026-03-21`; exact repository search found no current resolving PR for `MagicSquares` |

The merged PRs above establish that the statements are present upstream; they
do not mark them solved.  No open or merged resolution artifact preempted these
three searches.

## Literal readings and calibration gate

### Arithmetic theta sum

The evaluator used the literal definitions

```text
S'(h,k) = sum_{j=1}^{k-1} (-1)^(j+1+floor(hj/k))
S(k)    = sum_{h=1}^{k-1} S'(h,k).
```

For positive prime `k`, Lean's `floor ((h*j : Q)/k)` is exactly integer
division `(h*j)//k`; all arithmetic was integral.  The four falsifiable signed
residuals were `S(k)`, `S(k)-k`, `S(k)-2k`, and `S(k)-3k`, with the exact
threshold premises applied separately.  The eventual `conjecture_4_4` cannot
be refuted by a finite run unless an explicit `n` has infinitely many bad
primes, so this run makes no resolution claim about it.

Database sanity reproduced the upstream table exactly:

```text
[S(0),...,S(9)] = [0,0,1,2,5,4,7,10,11,8].
```

An independent scalar double loop rechecked all 124 catalogue primes and
matched the vectorized path's extrema.

### Tight union-closed family

The literal object is a finite family `A` of subsets of a nonempty labelled
ground type.  The premises require `A` to be neither empty nor `{empty}`, to be
closed under pairwise union, and to have every ground element in exactly half
the members.  A crossing is therefore a tight family with `#A` not a power of
two.  Unused ground elements are not silently deleted: they fail the literal
all-elements half-frequency premise.

The database gate used two independent encodings (integer subset masks and
tuples).  Both obtained the same `(union-closed, tight)` counts for ground-set
orders 1--4:

```text
n=1: (2,1), n=2: (12,2), n=3: (120,5), n=4: (4958,15).
```

Every tight control had power-of-two family size.  Full powersets calibrate
the equality wall and the explicit exclusions remove the two degenerate
families exactly as in the declaration.

### Semi-magic square of positive distinct cubes

The literal witness is a `3 x 3` natural matrix with nine pairwise distinct
entries, each equal to `r^3` for a positive natural root, and one common sum
for all three rows and all three columns.  Diagonal equality is not required.
The gate verified that the Lo Shu array passes the semi-magic row/column test
but fails the cube predicate, while the all-ones cube array passes the sum and
cube predicates but fails distinctness.  This catches the two easiest
statement weakenings.

## Equal-arm searches

Every row below was a separate subprocess launched under GNU `timeout 60s`.
Each arm had one process and hence a nominal budget of `1 x 60 = 60`
CPU/wall-seconds.  All completed normally before the cap; no timeout was
reclassified as a hold.

### Cluster A — arithmetic theta sum

| arm | frozen search | actual outcome |
|---|---|---|
| `CATALOGUE` | all 124 odd primes `3 <= k <= 700`; exact vectorized parity table | 0 violations in 0.167 s. Minimum applicable residuals were `(S,k)=(2,3)`, `(S-k,k,S)=(3,7,10)`, and `(S-2k,k,S)=(10,293,596)`; no `k>3119` was in this arm |
| `GENERIC` | seed `677255`; 80 shuffled primes from `[701,5000]` | 0 violations in 2.205 s. Minimum residuals for coefficients 0,1,2,3 were respectively `(2736,761,2736)`, `(1943,857,2800)`, `(1086,857,2800)`, `(937,4703,15046)` |
| `WALL_NAVIGATION` | exact `h`-row parity profiles for the first eight primes immediately above each hard threshold 5, 233, and 3119 | 24/24 held in 0.335 s. Closest relevant walls were `S(7)-7=3`, `S(263)-2*263=100`, and `S(3137)-3*3137=2869`; every row profile summed back to `S(k)` |

Independent verification used a separate scalar implementation, took 2.075 s,
reproduced the upstream ten-value table, all 124 catalogue values, and the same
minimum residuals.  Outcome: `ZERO_BOUNDED`; no candidate.

### Cluster B — tight union-closed family size

| arm | frozen search | actual outcome |
|---|---|---|
| `CATALOGUE` | exhaustive enumeration of every family over labelled ground sets of orders 1--4 (`2`, `14`, `254`, and `65,534` nondegenerate family codes) | exact census above; 0 non-power-of-two tight families in 0.949 s |
| `GENERIC` | seed `20260814`; take random seed families on 5, 6, and 7 elements and close them under union | 60,000 closures in 4.743 s; 18 tight hits, with size profile `2,4,8,16` only; 0 candidates |
| `WALL_NAVIGATION` | enforce the equality-frequency profile by taking unions of complete cyclic subset-orbits, then test union closure; exhaust orbit selections for `n=5,6` | `n=5`: 256 orbit unions, 22 union-closed, 2 tight; `n=6`: 16,384 orbit unions, 198 union-closed, 4 tight; 0 candidates in 0.091 s |

An independent tuple/set implementation repeated the complete order-1--4
census in 0.480 s and found no discrepancy.  Outcome: `ZERO_BOUNDED`; no
candidate.

### Cluster C — semi-magic square of cubes

| arm | frozen search | actual outcome |
|---|---|---|
| `CATALOGUE` | exact cube roots `1..35`; group every unordered triple of distinct cubes by its sum and test three disjoint triples for column completion | 0 candidates in 0.017 s |
| `GENERIC` | seed `314159`; roots `1..180`; 500,000 random choices of the four free entries and a first-row-induced target sum in the standard `3 x 3` semi-magic parametrization | 0 candidates in 6.532 s |
| `WALL_NAVIGATION` | roots `1..200`; exact equal-row-sum collision catalogue, fix the first row up to column symmetry, permute the second row, and force the third-row column complements | 1,151,496 sum groups, 20,264 groups with at least three triples, and 22,825 disjoint three-row sets checked; 0 candidates in 5.023 s |

The wall arm is exhaustive for matrices whose nine positive cube roots are at
most 200: row order and first-row column order are symmetries, all unordered
distinct cube triples were catalogued, and the final row was forced exactly by
the columns.  A second ordered-row-pair implementation independently exhausted
roots `1..100` (16,674 disjoint row pairs) in 0.244 s and also found no witness.
Outcome: `ZERO_BOUNDED`; no candidate.

## Method-improvement observations

1. **Filter by certificate shape before calling a finite zero progress.**  The
   first four arithmetic statements admit a one-prime disproof; the eventual
   fifth statement does not.  They belong to one source module but not one
   finite resolution shape.
2. **Profiles can collapse an enormous catalogue.**  For the Union-Closed
   tight variant, cyclic orbit closure enforces equal element frequencies by
   construction, so the wall arm spends its budget on union closure and the
   power-of-two conclusion instead of rediscovering balance accidentally.
3. **Solve forced coordinates rather than sample whole objects.**  A `3 x 3`
   semi-magic array has only a few free coordinates.  Grouping cube triples by
   row sum and forcing the third row from column complements turned the
   target-specific arm into a complete root-200 census, substantially stronger
   than the generic 500,000-sample arm at comparable cost.
4. **Catalogue boundaries should be semantic, not uniform.**  Ground-order 4
   is already a complete 65,536-code family universe, whereas root 200 still
   yields a manageable cube-triple collision table.  Equal nominal process
   budgets need not imply equal parameter ceilings.
5. **A no-candidate lane still needs two calibration classes.**  Positive
   controls show the structural predicate is recognized (upstream `S` values,
   balanced powersets, ordinary semi-magic arrays); near-miss controls show no
   premise was dropped (unused elements, noncubes, repeated cubes).

No candidate notification, independent two-process candidate verification,
issue, PR, release, or claim is warranted from this lane.
