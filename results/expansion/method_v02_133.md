# Method v0.2 Trial H2: WOWII 133

Status: **HOLD_BOUNDED / THEOREM_SIGNAL**

Started: 2026-08-12 UTC

## Frozen statement and reading

Upstream baseline `547f309edcc2069c1f61c2465729031c10385540`, file
`FormalConjectures/WrittenOnTheWallII/GraphConjecture133.lean`, declares for a
finite nontrivial connected simple graph

```text
path(G) >= radius(G) + floor(l(G))^cC4(G),
```

where `path` is the number of vertices in a largest induced path, `l(G)` is
the average independence number of open vertex neighborhoods, and `cC4=1`
exactly when there is no (not necessarily induced) four-cycle.  The source
record `data/wowii-conjectures.json` gives the same formula and marks it open
since 12 July 2005.  The floor reading is the upstream file's explicit
Graffiti.pc bracket convention.  Classification: **UNAMBIGUOUS**.

Use signed residual

```text
R133 = path - radius - floor(l)^cC4.
```

The C4-present branch is structurally safe: a diameter geodesic is induced,
so `path >= diameter+1 >= radius+1`, while the exponent-zero term is one.
Only C4-free graphs can cross.

## Frozen prediction and coordinate effects

This report executes frozen Trial H2 from
`method_v02_upstream_selection.md`.  A connected 2-lift preserves vertex
degree; a lift of a girth-at-least-five base also preserves C4-freeness.
The intended effects are therefore:

| coordinate | predicted effect |
|---|---|
| degree and, for triangle-free regular graphs, `floor(l)` | pinned |
| C4-free hypothesis | pinned |
| radius | may increase |
| longest induced-path order | unknown; hoped to increase more slowly |

The prospective crossing is `path < radius + degree` on a triangle-free
regular lift.

## Generator availability and exactness boundary

The host has nauty `geng` at a pinned local executable.  It supports connected,
C4-free, degree-exact generation with `-cf -d3D3 n 3n/2:3n/2`.  The script
records every completed order and generator timeout.  Complete generation of
an order subsumes every connected C4-free result of one or two
degree-preserving 2-switches at that order, so switch descendants need not be
re-enumerated separately inside completed cubic strata.

Every induced-path solve has an independent 60-second deadline.  Timeouts are
logged as bounds and never treated as holds.

## Incremental results

### Database-sanity gate

All 1,014 applicable gate rows passed: the 995 connected Graph Atlas graphs
on two through seven vertices, cycles `C5`--`C9`, `P7`, Petersen, `K3,3`,
`K7`, stars, and complete-bipartite controls.  There were no optimization
timeouts and no negative residuals.  Fifty-three rows attain equality.  The
reading therefore survives the required gate.

### Exact 2-lifts

Spanning-tree gauge fixing reduces sign assignments to the cycle-space
coordinates; graph isomorphism then removes automorphic duplicates.  This
produced exactly:

- one connected lift class of `C5`, namely `C10`, with residual `2`;
- five nonisomorphic connected lift classes of Petersen, with residuals
  `3, 5, 5, 4, 3`.

Thus the frozen covering transformation moves every equality control tested
strictly to the safe side.  There were no solve timeouts.

### Cubic C4-free controls

Nauty generated connected C4-free cubic graphs.  Completed orders are exact
unlabeled strata.  A complete stratum already contains every connected
C4-free output of one or two degree-preserving switches from its members, so
the frozen switch requirement adds no graph outside it.

| order | graphs | complete | minimum `R133` | solve timeouts |
|---:|---:|:---:|---:|---:|
| 10 | 3 | yes | 0 | 0 |
| 12 | 8 | yes | 2 | 0 |
| 14 | 36 | yes | 1 | 0 |
| 16 | 269 | yes | 3 | 0 |
| 18 | 2,761 | yes | 4 | 0 |
| 20 | 36,101 | yes | 3 | 0 |
| 22 | 2,966 | no, generator stopped at 60 s | 6 observed | 0 |
| 24 | 1,757 | no, generator stopped at 60 s | 7 observed | 0 |

There is no violation among the **39,178 graphs in completed strata**.  The
order-22 and order-24 values are observations only, not exhaustive minima.
An earlier partial order-20 run is retained in the JSONL ledger before the
completed run; it is not double-counted here.

### Named calibration graphs

McGee, Pappus, Desargues, Dodecahedron, and Kneser `(7,3)` have exact positive
residuals `10, 4, 3, 4, 13`.  The exact longest-induced-path search on the
50-vertex Hoffman--Singleton graph hit its 60-second cap.  The ledger records
that timeout and makes no verdict from the incomplete optimization.

### Independent recomputation

`scripts/method_v02_133_verify.py` uses descending vertex-subset enumeration,
not the endpoint-extension DFS used for discovery.  It independently checks
connectivity, C4-freeness by common-neighbor pairs, radius by BFS, every local
neighborhood independence number, longest induced-path order, and the signed
residual.  It passes all six lift representatives and one exact minimum
representative from every completed cubic order (12 durable rows total).

## Outcome

**HOLD_BOUNDED / THEOREM_SIGNAL.**  Frozen Trial H2 found no counterexample.
More importantly, its directional prediction failed consistently: connected
2-lifts of both equality controls increased maximum induced-path order enough
to create positive, not negative, slack.  Equality persists elsewhere at
order ten, but the complete cubic strata through order 20 never cross.

The appropriate next action is mathematical, not a wider unstructured graph
search: investigate whether every connected cubic C4-free graph satisfies

```text
path(G) >= radius(G) + 3.
```

That is exactly the live regular specialization exposed by the trial.  This
report does not claim the specialization, or Conjecture 133, is proved.
