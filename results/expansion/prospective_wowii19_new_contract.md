# Frozen prospective discovery trial: current DeepMind WOWII 19

Frozen: 2026-08-13 UTC, before database-gate or development-graph evaluation.

## Exact current target

Only `FormalConjectures/WrittenOnTheWallII/GraphConjecture19.lean` is in scope:

```text
floor(average_v eccentricity(v) + max_v alpha(G[N(v)])) <= b(G),
```

where `b(G)` is the largest order of an induced bipartite subgraph and
`alpha(G[N(v)])` is the local independence number `indepNeighbors G v`.
The declaration is currently tagged `research open`.

## Separation from the existing proof ladder

This is a new prospective discovery lane, not an extension or evaluation of
the repository's maximum-star, geodesic, canonical-tail, cubic, unicyclic,
center-attachment, or theorem-extraction control families.  Those graphs and
their parameterized variants are excluded from development evaluation.

## Frozen mechanism

Raise average eccentricity and maximum local neighborhood independence while
forcing many vertex deletions to destroy all odd cycles.  The intended
separation is between a global odd-cycle packing/block structure and a locally
large independent neighborhood.

## Frozen development families

1. **Odd-cycle block trees.** Trees of `C3`, `C5`, and `C7` blocks joined at
   cut vertices or by single bridge edges. Block-tree shapes: path, star,
   binary fork, and broom. Two through six blocks, total order at most 22.
   Exactly one block may receive a chord or pendant-free clique ear.
2. **Nonuniform clique/cycle blowups.** Vertex substitutions of odd-cycle and
   odd-cycle-block bases by cliques or independent twins of sizes 1--4, with
   complete joins along base edges. Total order at most 22. Frozen patterns:
   alternating, one-large, monotone, and center-heavy.
3. **Bounded edge and endpoint surgeries.** At most two edge additions,
   deletions, or endpoint reattachments on graphs from lanes 1--2 of order at
   most 20, retaining connectivity. At most 5,000 deterministic surgeries.
   These operations are intended to change local independence/eccentricity
   while preserving much of the odd-cycle transversal burden.

Enumeration is deterministic. Any surgery subsampling uses fixed seed
`1920260813`. No new family may be introduced after results are observed.

## Gate order and budgets

1. Run database sanity **before** development families: all connected Atlas
   graphs through order seven and the standard named graphs.
2. If the reading survives, evaluate at most 1,000 base graphs and 5,000
   surgeries.
3. Every process and exact invariant solve is capped at 60 seconds.

Exact invariant requirements:

- eccentricities and their average use integer distances and exact `Fraction`;
- local independence is exact exhaustive/branch-and-bound independence on
  every open neighborhood, with a vertex witness;
- `b(G)` is exact exhaustive odd-cycle-transversal/induced-subset search, with
  a bipartite vertex-set witness and exhaustive upper-bound count;
- a timeout is `INCONCLUSIVE`, never a crossing.

Retain exact slack

```text
b(G) - floor(average eccentricity + max local independence)
```

in `[-2,2]`.

## Mandatory crossing protocol

For any strict negative slack:

1. independently recompute all invariants by a separate implementation;
2. verify the bipartite witness and independently prove no larger induced
   bipartite subset exists;
3. rerun the database sanity reading and reject any reading contradicted there;
4. audit current source status, GitHub issues/PRs, and literature/web novelty;
5. append all evidence to the JSONL ledger before alerting the parent.

No commit, push, release, PR, issue, or other public action is authorized.

## Gate-classified outcomes

- `DB_SANITY_REJECT`: current reading fails on a generator-database graph.
- `CANDIDATE`: strict crossing survives exact recomputation and novelty audit.
- `HOLD_BOUNDED`: gate passes but frozen development families do not cross.
- `INCONCLUSIVE`: an exact solve times out on a potentially crossing graph.

