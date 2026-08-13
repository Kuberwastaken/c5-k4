# Method v0.10: WOWII 59 exact-corner audit

Date: 2026-08-13

## Question

Method v0.9 proved, conditional only on the standard
`residue(G) <= alpha(G)` theorem, that every possible WOWII 59 product failure
with `residue(G) <= 3` must have the exact invariant triple

```text
(residue(G), b(G), f(G)) = (3, 6, 4).
```

This pass tests whether that corner is graph-realizable and formalizes one
structural class that excludes it. WOWII 59 is already externally disproved;
none of this is a counterexample or novelty claim.

## Exact bounded audit: all connected graphs through order seven

The primary search enumerated every connected graph of orders 2 through 7 in
`networkx.graph_atlas_g()`: 995 nonisomorphic graphs total. For every graph it
computed:

- Havel--Hakimi residue from the sorted degree sequence;
- `b` by descending subset enumeration with NetworkX bipartiteness tests;
- `f` by descending subset enumeration with NetworkX forest tests.

The process completed in 1.48 seconds, below the fixed 60-second cap. Exactly
447 graphs had residue three. Their complete `(residue,b,f)` distribution was:

| triple | count |
|---|---:|
| `(3,4,4)` | 34 |
| `(3,5,4)` | 4 |
| `(3,5,5)` | 171 |
| `(3,6,5)` | 93 |
| `(3,6,6)` | 119 |
| `(3,7,5)` | 4 |
| `(3,7,6)` | 18 |
| `(3,7,7)` | 4 |

There were **zero** graphs with `(3,6,4)`.

An independent implementation then repeated only the 447 residue-three rows.
It represented subsets by bit masks, tested bipartiteness by a custom
two-colour depth-first traversal, and tested acyclicity by a custom union-find
cycle detector. It reproduced the table exactly in 0.15 seconds, again finding
zero corner realizations.

These two computations use different invariant code paths. The graph source is
shared because the scope is explicitly the canonical Atlas census.

## Fixed random extension

A preregistered reproducible random sample used

```text
generator: networkx.gnp_random_graph
seed: 59010
orders: 8,9,10,11,12
p: 0.20,0.35,0.50,0.65,0.80
connected graphs per (n,p) cell: 50
```

This gives 1,250 connected graphs. The exact subset optimizers completed in
12.06 seconds. There were 423 residue-three graphs and again **zero** exact
corner realizations. In particular, the sample did contain nearby values:

- one `(3,4,4)` graph;
- nine `(3,6,5)` graphs;
- 81 `(3,6,6)` graphs.

The zero is therefore not caused by residue-three or `b=6` being absent from
the sample. This random extension is evidence only, not an exhaustive result.

## Complete six-vertex bipartite micro-audit

Because `b=6` means that a six-vertex graph is itself bipartite, a separate
enumeration generated every labelled bipartite graph on fixed parts of sizes
`1+5`, `2+4`, and `3+3`, then quotiented the `f=4` survivors by graph
isomorphism.

Exactly two isomorphism classes survive:

1. `K_{3,3}`;
2. `K_{3,3}` with one edge deleted.

Both have Havel--Hakimi residue two, not three. This completely excludes the
corner at graph order six. It does not by itself exclude a larger graph whose
maximum induced bipartite subgraph has order six.

## Formal structural exclusion

[`lean/GraphConjecture59Corner.lean`](../../lean/GraphConjecture59Corner.lean)
formalizes three reusable rungs:

1. if the whole finite graph is bipartite, then
   `largestInducedBipartiteSubgraphSize = Fintype.card V`;
2. if five vertices split into two independent parts and every vertex of the
   first part has at most one neighbor in the second, those vertices induce a
   forest, hence `f >= 5`;
3. any graph carrying that deletion certificate cannot realize
   `(residue,b,f)=(3,6,4)`.

The second theorem is a meaningful local exclusion class: it recognizes a
forest without globally enumerating paths or cycles and applies to arbitrary
ambient graphs. It uses the already formalized acyclicity criterion from the
WOWII 40 source-baseline lane.

The current Lean result deliberately does not claim a universal exclusion of
the corner. The exact census supports that conjecture, but bridging from an
arbitrary maximum six-vertex bipartite witness to an appropriate deletion
certificate remains unproved. Dense witnesses such as `K_{3,3}` do not satisfy
the one-neighbor certificate, although their residue is already two.

## Verification

After compiling the warning-clean v0.8 and v0.9 local dependencies into
temporary `.olean` files, the new module was checked with

```text
LEAN_PATH=/tmp lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture59Corner.lean
```

It completed in 6.5 seconds with no warnings or errors. The module contains no
`sorry`, `admit`, custom axiom, native decision procedure, or imported upstream
conjecture proof.

## Outcome

`BOUNDED_NONREALIZATION_PLUS_CLASS_EXCLUSION`.

The exact corner is absent from all 995 connected graphs through order seven,
absent from an independently recomputed residue-three census, absent from the
fixed 1,250-graph random extension through order twelve, and impossible at
order six by a complete bipartite enumeration. A useful Lean deletion class is
also closed. Universal nonrealizability remains a theorem candidate, not a
claim.
