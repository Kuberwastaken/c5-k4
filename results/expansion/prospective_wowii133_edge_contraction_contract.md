# Frozen prospective addendum: Heawood edge contraction for WOWII #133

Frozen: 2026-08-13 UTC, before evaluating any contracted graph.

## Closest new-family wall and exact obstruction

The closest noncontrol graph in the completed covers-and-switches lane was
the Heawood graph, equivalently the Levi graph of `PG(2,2)`.  Its exact
coordinates are

```text
n = 14, m = 21,
maximum induced-path order = 7,
radius = 3,
alpha(G[N(v)]) = 3 for every vertex v,
floor(average_v alpha(G[N(v)])) = 3,
R133 = 7 - 3 - 3 = 1.
```

The graph is cubic, bipartite, and has girth six.  Triangle-freeness makes
every open neighborhood independent, so the local-average coordinate is
exactly average degree.  The obstruction is therefore one unit of induced-
path slack above the target wall `radius + floor(local average) = 6`.

## Frozen local transformation

For every edge `uv` of each of the two independently constructed but
isomorphic inputs (NetworkX Heawood and the `PG(2,2)` Levi construction),
contract `uv` to one vertex, discard the contracted loop, relabel densely,
and canonically deduplicate isomorphic outputs.  No second transformation or
post-result mutation may be added.

This is an edge-minor operation, not a cover, switch, subdivision, pendant
attachment, polarity deletion, or cycle-chord addition.  It was selected to
compress a path-supporting adjacency without introducing a low-degree
vertex.  For the Heawood input the contraction has `n=13,m=20`; because it
remains triangle-free, its average local independence is `40/13`, whose floor
is still three.  Thus the floor correction survives the compression.

The girth-six input also makes the move C4-free.  A triangle through the
contracted vertex would lift to a 4-cycle in the input.  A 4-cycle through it
would lift to a 4- or 5-cycle, and a 4-cycle avoiding it would already have
existed.  All are excluded by girth six.  The implementation nevertheless
checks C4-freeness exactly before evaluation.

Contraction cannot increase distances.  The intended separator is the case
where the radius remains three while the local compression destroys every
induced path on six vertices.  That would put the maximum induced path one
below `radius + floor(local average)` and strictly refute the formalized
C4-free branch.  A target path on six vertices instead rejects the candidate
immediately, without exact maximization.

## Frozen decision-first protocol

1. Before any contracted graph is evaluated, rerun the existing #133
   database gate: every connected Graph Atlas graph of orders two through
   seven and all named controls from `method_v02_133_search.py`.  The
   decision oracle and exact evaluator must agree that every control holds.
2. Independently reconstruct and verify the two input profiles above.
3. Generate all one-edge contractions, reject any disconnected or C4-present
   result, and isomorphically deduplicate.  The frozen cap is 42 raw inputs
   and at most 42 distinct retained candidates of order 13.
4. Compute radius and the exact local-independence average, then search only
   for an induced path on
   `radius + floor(average_v alpha(G[N(v)]))` vertices.
5. If such a path is found, log its vertex order and stop on that candidate;
   do not optimize its maximum induced-path order.  Only if exhaustive target
   search finds no witness may exact maximization run.
6. A strict crossing requires exact maximization, an independent descending-
   subset no-target check, and a fresh source/status/novelty audit.

Every operating-system process, decision search, and exact fallback is capped
at 60 seconds.  Results are appended immediately to
`prospective_wowii133_edge_contraction_ledger.jsonl`; a timeout is unresolved,
never a crossing.

Verdicts are `DB_SANITY_REJECT`, `CANDIDATE`, `HOLD_BOUNDED`, or
`INCONCLUSIVE`.  No commit, push, release, issue, PR, or other public action is
authorized.
