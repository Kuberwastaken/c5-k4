# Frozen second prospective trial: square closure from #19 equality seeds

Frozen: 2026-08-13 UTC, before evaluating any transformed development graph.

This addendum is a new trial. It does not extend the family menu of
`prospective_wowii19_new_contract.md` after observing that trial's outcome.

## Learned equality identity

All 56 retained equality rows in the completed trial satisfy the explicit
integer wall identity

```text
b(G) - max_v alpha(G[N(v)]) = floor(average_v eccentricity(v)).
```

The observed left/right values cover 1 through 5. This is stronger guidance
than merely knowing that total slack is zero: it identifies the two-coordinate
difference that must fail to track the eccentricity floor.

## Frozen separating move

For every equality seed `G` from the completed base and deterministic
one-surgery sets, construct its graph square `G^2`: distinct vertices are
adjacent exactly when their distance in `G` is at most two.

This is a global distance-closure transformation, not an odd-cycle block,
vertex substitution, edge/endpoint surgery, or member of the existing #19
proof ladder. It is therefore genuinely outside the completed development
families.

The prospective prediction is that distance closure can destroy induced
bipartite capacity faster than it destroys local neighborhood independence
plus the eccentricity floor. In coordinates, the desired separation is

```text
b(G^2) - max_v alpha(G^2[N(v)])
  < floor(average_v eccentricity_G^2(v)).
```

No other transformation may be added after results are observed.

## Frozen inputs, limits, and order

1. Repeat the exact database-sanity gate on all connected Graph Atlas graphs
   of orders two through seven, before evaluating a square.
2. Reconstruct exactly the 56 equality seeds already selected by the frozen
   first-trial generators (`74` base graphs and `195` seed-3 surgeries).
3. Square every seed, canonically deduplicate equal/isomorphic fingerprints,
   and evaluate every distinct square of order at most 22.
4. Maximum 56 inputs and 56 transformed evaluations. Fixed surgery RNG seed
   remains `1920260813`.
5. Every process is capped at 60 seconds; every fallback exact solve is capped
   at 10 seconds.

Exact eccentricity, local independence, and maximum induced-bipartite order
use the same witness-producing implementations as the completed trial. A
strict crossing must be recomputed independently and pass source/status and
novelty checks before it can be classified `CANDIDATE`.

## Outcomes

- `DB_SANITY_REJECT`: the reading fails the repeated database gate.
- `CANDIDATE`: a squared equality seed crosses and survives all mandatory
  exact and novelty gates.
- `HOLD_BOUNDED`: every distinct squared seed is exact and nonnegative.
- `INCONCLUSIVE`: any potentially crossing transformed input lacks an exact
  result within its cap.

No commit, push, release, PR, issue, or public action is authorized.
