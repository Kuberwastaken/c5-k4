# Frozen prospective trial: current DeepMind WOWII 314

Frozen: 2026-08-13 UTC, before evaluating any trial graph.

## Target

Only the current statement in
`FormalConjectures/WrittenOnTheWallII/GraphConjecture314.lean` is in scope:

```text
connected(G) and |V(G)| > 1 and triangle-free(G)
and largestInducedPathSize(G) <= 4
imply IsWellTotallyDominated(G).
```

Here a total dominating set contains a neighbor of every vertex, including
each selected vertex.  It is minimal under proper-subset inclusion.  A graph
is well totally dominated exactly when all its minimal total dominating sets
have the same cardinality.

The historical conjecture, earlier formalizations using another `path`
invariant, and conjectures absent from the current DeepMind repository are out
of scope.

## Predeclared crossing mechanism

Seek a connected triangle-free `P5`-free graph whose local modules admit two
inclusion-minimal total-dominating patterns of unequal sizes.  The carrier's
failure mode suggests separating a compact cross-module dominating pair from
a larger minimal pattern, while the `largestInducedPathSize <= 4` antecedent
forces every construction to remain induced-`P5`-free.

The primary wall coordinates are therefore:

```text
largest induced path order = 4,
minimum minimal-TDS size < maximum minimal-TDS size.
```

Diameter two is prioritized because an induced path of order five would then
have to arise from chord avoidance rather than metric length.

## Frozen construction lanes

The following lanes, and only these lanes, will be evaluated.

1. **Independent blowups.** Nonempty independent-set blowups of `C4`, `C5`,
   complete bipartite graphs, crowns, Petersen, Clebsch, and the small
   Andrasfai graphs.  Bag sizes are `1..6`; total order is at most 30;
   lexicographic vectors and single-heavy/double-heavy patterns are used.
2. **Bipartite nested-neighborhood families.** Connected bipartite adjacency
   matrices with at most five vertices per side, including chain graphs,
   crowns, complete bipartite graphs with one matching or one biclique
   deleted, and all lexicographic one-edge/two-edge edits of those seeds.
   Total order is at most 12.
3. **Triangle-free substitutions and surgery.** False-twin and true
   independent-module substitutions into `C4`, `C5`, Petersen, and complete
   bipartite seeds, followed by at most two deterministic edge switches.
   Retain only connected triangle-free graphs of diameter at most two and
   order at most 24.  At most 5,000 surgeries per seed are examined.
4. **Small regular and named graphs.** Every connected triangle-free Graph
   Atlas graph through order seven; named Petersen, Clebsch, Hoffman--Singleton
   (only if its order-50 exact checks finish within cap), Heawood, Moebius--
   Kantor, Pappus, Desargues, dodecahedral, cubical, and small Andrasfai
   graphs; plus deterministic regular-graph samples of orders at most 20 with
   RNG seed `31420260813`.

No graph family may be added after seeing trial outcomes.  A family rejected
by the antecedent remains a logged miss rather than being silently discarded.

## Budgets

- At most 25,000 distinct graphs across all discovery lanes.
- Every subprocess is capped at 60 seconds.
- Exact largest-induced-path computation is capped at 60 seconds per graph.
- Exact enumeration of all minimal total dominating sets is capped at 60
  seconds per graph.
- A timeout is logged as `TIMEOUT` and cannot support a crossing.
- Near-wall applicable graphs and all distinct minimal-TDS size spectra are
  retained for theorem diagnosis.

## Exact evaluators

The primary path evaluator enumerates vertex subsets of sizes five upward and
tests whether their induced graph is a path; once an induced `P5` is found,
the antecedent is rejected without needing the exact maximum.  For graphs
surviving the `P5` test it verifies the largest attainable orders `1..4`.

The primary domination evaluator enumerates all subsets, tests total
domination, and retains exactly those for which deletion of every selected
vertex destroys total domination.  Minimality-by-single-deletion is valid
because total domination is upward closed.

## Mandatory crossing protocol

For every apparent crossing, before any alert or discovery claim:

1. serialize the exact edge list and recompute connectivity, triangle
   freeness, diameter, induced-`P5` absence, and the two minimal-TDS witnesses
   with an independent implementation;
2. independently recompute all minimal total dominating sets and their size
   spectrum using a second algorithm/code path;
3. run the current reading on every connected Graph Atlas graph through order
   seven and on the sanity set `C4--C9`, `P4--P8`, Petersen, `K3,3`, stars,
   crowns, and complete bipartite graphs;
4. reject the evaluator if the Atlas/sanity results disagree between the two
   implementations;
5. append the complete evidence to the ledger before alerting the parent.

Atlas crossings are not automatically rejected: because the target concerns
all connected finite graphs, an Atlas graph can be a genuine witness.  It
must, however, survive the same independent recomputation and current-source
reading audit.

No novelty claim, issue, PR, release, commit, push, or other public action is
authorized in this lane.

## Frozen verdict rule

- `CANDIDATE`: an exact graph satisfying all antecedents with at least two
  certified minimal total dominating sets of unequal cardinalities, surviving
  the full mandatory protocol.
- `HOLD_BOUNDED`: no crossing in the frozen lanes and budgets.
- `INCONCLUSIVE`: a potentially applicable or crossing graph lacks an exact
  path or domination result within its cap.

