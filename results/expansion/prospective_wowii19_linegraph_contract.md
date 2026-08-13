# Frozen prospective WOWII 19 trial: line graphs of equality seeds

Frozen: **2026-08-13 UTC**, before evaluating any transformed graph.

## Current DeepMind target

Only the current declaration in
`FormalConjectures/WrittenOnTheWallII/GraphConjecture19.lean` is tested:

```text
b(G) >= floor(average_v eccentricity(v)
              + max_v alpha(G[N(v)])).
```

The signed residual is

```text
R19(G) = b(G) - floor(averageEccentricity(G) + localMax(G)).
```

A negative residual is a crossing.  This is Written on the Wall II in the
current DeepMind corpus, not Written on the Wall I.

## Equality input lock

The only inputs are the 56 exact equality rows already serialized as `SEEDS`
in `scripts/prospective_wowii19_square_trial.py`.  No later #19 equality,
near-equality, or safe-side graph may be substituted.  Isomorphic transformed
outputs may be deduplicated.  A transformed graph is evaluated only when its
order is at most 60; larger outputs receive an explicit `OUT_OF_SCOPE` row.

## Single frozen transformation

For every locked seed `G`, form its line graph `L(G)`.  No edge edit, graph
power, subdivision, product, lift, or adaptive second transformation is
authorized.

This operation is selected from an explicit residual separation:

- every open neighborhood in a line graph is the union of the two endpoint
  cliques of the represented edge, so `localMax(L(G)) <= 2`;
- `b(L(G))` is the largest edge set of `G` whose selected-edge subgraph has
  maximum degree at most two and no odd cycle (a disjoint union of paths and
  even cycles);
- distances in `L(G)` are edge-incidence distances in `G`, so the average
  eccentricity remains a nonzero metric coordinate and is not definitionally
  tied to either of the preceding two quantities.

The prospective prediction is that incidence closure can make the
even-linear edge rank grow more slowly than
`floor(averageEccentricity + localMax)`.  In predicted coordinate language:

```text
localMax: pinned above by 2;
average eccentricity: retained as an independently moving positive coordinate;
b: replaced by the maximum even-linear selected-edge rank.
```

This is a prospective transformation prediction, not a claim that a crossing
has already been observed.

## Frozen protocol and bounds

1. Before any line graph is evaluated, rerun the source-faithful database
   gate on all 995 connected Graph Atlas graphs of orders two through seven
   and the same 28 named controls used by the completed #19 trial.
2. Require zero unexplained gate crossings and zero unresolved gate rows.
3. Evaluate every distinct in-scope line graph.  Every process and every exact
   solve has a hard 60-second wall-clock cap.
4. Append records incrementally to
   `prospective_wowii19_linegraph_ledger.jsonl`.
5. For every apparent crossing, independently recompute `b(L(G))` in the
   original seed's edge domain, separately verify the line-graph metric and
   neighborhood coordinates, and store graph6, edge list, witnesses, and
   checks before classification.

Strict outcomes are `DB_SANITY_REJECT`, `CANDIDATE`, `HOLD_BOUNDED`, or
`INCONCLUSIVE`.  A timeout cannot support a hold.  No commit, push, release,
issue, PR, novelty claim, or other public action is authorized.
