# Frozen prospective trial: current DeepMind WOWII 34

Frozen: 2026-08-13 UTC, before evaluating any trial graph.

## Exact target

Only the current declaration in
`FormalConjectures/WrittenOnTheWallII/GraphConjecture34.lean` is in scope:

```text
ceil(distavg(G, center(G)) + distavg(G, maxDegreeVertices(G)))
  <= largestInducedPathOrder(G).
```

The module comment incorrectly calls `path` “the floor of the average
distance”; the imported implementation defines it as the number of vertices
in a largest induced path, and that implementation controls this trial.

The user-suggested “periphery” direction is interpreted only as construction
guidance.  The formal right-hand distance set `M` is the set of maximum-degree
vertices, not the periphery.  No alternative reading will be mixed into the
frozen verdict.

Although the declaration is tagged `research solved`, its Boolean answer is
still `answer(sorry)` and the resolution direction is not recorded.  This is a
prospective witness search against the quantified inequality, not an open-
status or novelty claim.

## Frozen mechanism

Increase the average distances to both the center and maximum-degree set while
keeping every induced path short through dense substitutions and abundant
chords/shortcuts.

## Frozen construction lanes

1. **Nonuniform blowups.** Lexicographic clique blowups of paths, cycles,
   theta graphs, and complete-bipartite bases. Blob sizes 1--5, total order at
   most 24; monotone, alternating, center-heavy, endpoint-heavy, and one-large-
   blob patterns.
2. **Substituted diameter layers.** Layer chains of cliques or independent
   sets with complete joins between consecutive layers, optionally adding
   complete joins at distance two on alternating layers. Layer counts 3--8,
   layer sizes 1--4, total order at most 24.
3. **Block joins.** Paths and cycles of clique blocks joined by portal edges,
   complete bipartite portal joins, or shared cut vertices. Two through seven
   blocks, block orders 3--6, total order at most 24.
4. **Strong-product-like cages.** Strong and lexicographic products of paths,
   cycles, cliques, and small cubic cages where total order is at most 24;
   plus deterministic edge additions preserving diameter at least three.

No new family may be introduced after observing results.  Enumeration is
deterministic; any subsampling uses fixed seed `3420260813`.

## Computation budget

- At most 2,000 constructed graphs.
- Every process and every exact induced-path solve: at most 60 seconds.
- Exact induced path is computed by chord-aware path DFS with memoized/canonical
  endpoint states, and every retained crossing is recomputed independently by
  exhaustive vertex-subset/path-order testing when order permits, otherwise a
  separately implemented branch-and-bound search.
- Distances are exact integers and averages are exact `Fraction`s.  Ceiling is
  applied only after adding the two exact fractions.
- Timeouts are logged as `INCONCLUSIVE`, never crossings.
- Retain exact slack `path - ceil(distance sum)` in `[-2,2]`.

## Mandatory crossing gates

Before reporting any strict crossing:

1. recompute center, maximum-degree set, all set distances, both exact averages,
   and the ceiling by a second code path;
2. recompute largest induced path independently and emit an explicit maximum
   witness plus an exhaustive upper-bound certificate/search count;
3. test the same current reading on all connected Atlas graphs through order
   seven and the standard sanity graphs;
4. reject a reading contradicted by a generator-database sanity graph;
5. append evidence to the ledger before alerting the parent.

No commit, push, issue, PR, release, novelty claim, or other public action is
authorized.

## Frozen verdicts

- `CANDIDATE`: strict crossing surviving every mandatory gate.
- `HOLD_BOUNDED`: no crossing within the frozen families and budgets.
- `INCONCLUSIVE`: a promising graph reaches an exact induced-path timeout.

