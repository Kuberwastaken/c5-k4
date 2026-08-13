# Frozen prospective trial: WOWII 19, dense/symmetric transformations

Frozen: **2026-08-13 UTC, before database or development-family evaluation**

This lane is independent of the active odd-cycle block-tree/surgery lane.

## Exact current reading

For a finite nontrivial connected simple graph `G`, current DeepMind
`GraphConjecture19.lean` asserts

`floor(average eccentricity + maximum neighborhood independence) <= b(G)`,

where eccentricity is converted from `ENat` to `Nat`, neighborhood
independence is `indepNeighbors`, and `b(G)` is the largest order of an induced
bipartite subgraph. Because the maximum neighborhood independence is integral,
the exact crossing rule is

`b(G) < maxLocalAlpha(G) + floor(sum_v ecc(v) / |V|)`.

## Mandatory database and status gates

Before any development-family row:

1. exhaust all connected unlabeled Atlas graphs of orders 2--7 using exact
   integer/rational invariants;
2. replay named controls (`K_n`, `C_n`, complete bipartite graphs, Petersen,
   and `C5[K_m]` where within the exact cap);
3. audit the live source, issue, PR, and local novelty/status records.

Any apparent database crossing stops family evaluation until independently
recomputed. Existing proof activity is recorded but does not retroactively
alter the frozen search.

## Frozen development-family grammar

1. **Line graphs:** line graphs of paths/cycles, complete graphs,
   complete-bipartite graphs, wheels, Petersen, and connected Atlas bases,
   retaining connected outputs of order at most 14.
2. **Connected complements:** complements of the named bases and line-graph
   outputs, only when connected and of order at most 14.
3. **Lexicographic/nonuniform blow-ups:** `H[K_m]` and `H[empty_m]` for
   `H` in `{P3,P4,P5,C3,C4,C5,C6,K1,3,diamond}`, `m=2..4`; plus bag-size
   vectors in `{1,2,3}` on `P3..P5` and `C3..C6`, total order at most 14.
4. **Joins:** joins of two graphs selected from paths/cycles/cliques/empty
   graphs of orders 1--5, total order at most 12.
5. **Bounded perturbations:** every canonical single-edge addition or deletion
   of the named outputs above, retaining connected graphs of order at most 14.

Deduplicate by graph6 after canonical relabeling where available, otherwise by
WL hash plus exact adjacency certificate. Caps: 8,000 generated outputs and
2,000 connected exact profiles. Stop at the first independently verified
crossing or cap exhaustion. No adaptive family expansion is allowed.

## Exact evaluation and witnesses

- eccentricities: all-pairs shortest paths, retaining every value;
- local independence: exact descending subset enumeration in every open
  neighborhood, retaining a maximizing vertex and independent-set witness;
- `b(G)`: exact descending subset enumeration, retaining a largest induced
  bipartite vertex set and a two-coloring; exhaustion of every larger subset
  is the upper certificate;
- arithmetic: exact integers/Fractions only, never floating point.

Any crossing receives graph6, explicit edges, independent recomputation of
all invariants, and a separately formulated bipartite-subset optimization.
Every subprocess has a hard 60-second cap.

No commit, push, release, issue, PR, or other public action is authorized.

