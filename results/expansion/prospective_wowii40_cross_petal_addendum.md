# Frozen prospective addendum: cross-petal incompatibility for WOWII #40

Frozen: 2026-08-13 UTC, before evaluating any development graph.

## Mechanism learned from the bouquet failure

The rooted balanced-biclique bouquets raised exact path-cover number to as
much as six, but their petals remained mutually compatible inside a large
induced forest.  Their residuals consequently moved from the equality wall
`R in {1,2}` to `R=6..11`.

This trial preserves separate exact-equality petals rather than identifying a
root.  It then adds a predeclared system of cross-petal edges.  The edges all
respect a common bipartition, so the entire transformed graph is itself an
explicit induced-bipartite witness.  At the same time, alternating cross
connections create cycles that use vertices in different petals, making the
petal forest witnesses mutually incompatible.

## Frozen exact-equality inputs

Only these canonical `R=1`, bipartite equality seeds are allowed:

| seed graph6 | `(n,f,b,p)` |
|---|---|
| `C]` | `(4,3,4,1)` |
| `Gs\\r_[` | `(8,5,8,1)` |
| `G]r@xw` | `(8,5,8,1)` |
| `GS\\r_[` | `(8,5,8,1)` |
| `GsLr_[` | `(8,5,8,1)` |

The exact evaluator must reverify these coordinates before constructing the
trial graphs.

## Frozen cross-petal constructions

Give every connected bipartite seed the deterministic coloring returned from
the component containing vertex zero, swapping colors if necessary so vertex
zero lies on the left.  Within each side, order terminals by decreasing seed
degree and then vertex label; call the first two `x0,x1` and `y0,y1`.

Use exactly these petal multisets:

- three and four disjoint copies of `C]`;
- every unordered pair with replacement of the four order-eight seeds.

For petals indexed cyclically, add one of three global edge systems:

1. `parallel_ring`: `x0_i--y0_(i+1)` and `x1_i--y1_(i+1)`;
2. `crossed_ring`: `x0_i--y1_(i+1)` and `x1_i--y0_(i+1)`;
3. `primary_incompatibility`: for every `i<j`, add both
   `x0_i--y0_j` and `x0_j--y0_i`.

Existing edges are harmlessly deduplicated.  Retain only connected outputs,
orders 12--16, and canonically deduplicate isomorphic graphs.  This operation
uses vertex-disjoint equality seeds plus at least four cross-component edges;
it is not a bouquet, block tree, ear/substitution, line graph, neighborhood
closure, false-twin ray, or prior one/two-edge mutation.

## Frozen prediction, gate, and budget

Because every output remains bipartite, `b=n` exactly and no odd-cycle penalty
can mask the experiment.  Relative to the disjoint petals, cross edges can
only decrease path-cover number, but they can also raise feedback-vertex
burden by making maximum petal forests incompatible.  A crossing is accepted
only from the exact inequality `f < ceil((p+n+1)/2)`.

- Rerun the standard exact 1,031-graph #40 sanity gate before development.
- Evaluate at most 36 distinct graphs, with exact witnesses and graph6 logged
  incrementally.
- Cap every exact solve and process below 60 seconds; a timeout is
  `INCONCLUSIVE`.
- Stop on the first strict crossing, then independently recompute all three
  invariants and rerun source/status/novelty checks before any release claim.

No commit, push, release, issue, PR, or other public action is authorized in
this lane.

## Exact outcome

The database gate passed all 1,031 controls.  The 36 predeclared constructions
deduplicated to 24 exact graphs: two of order 12 and 22 of order 16.  Every
solve completed within its cap.

| quantity | exact result |
|---|---:|
| strict crossings | 0 |
| bipartite outputs (`b=n`) | 24 |
| Hamiltonian outputs (`p=1`) | 24 |
| slack 1 | 21 |
| slack 2 | 2 |
| slack 3 | 1 |

The corresponding residual distribution is `{3: 21, 5: 2, 7: 1}`.  Thus the
cross edges did suppress simultaneous forest growth substantially: most
outputs ended only one unit above the conjectured bound.  But the same edges
made every composition Hamiltonian, erasing the bouquet's useful path-cover
fragmentation.

There is also a sharp obstruction to extending this exact direction.  In a
bipartite graph with color classes `A,B`, all of the larger color class plus
any single vertex of the other class induce a star, so
`f >= max(|A|,|B|)+1`.  For a balanced order-16 output with `b=16,p=1`, this
already gives `f>=9`, exactly the right side.  More bipartite cross edges can
at best reach equality; they cannot cross while Hamiltonicity persists.

The frozen classification is `HOLD_BOUNDED`.  A genuinely separating successor
would have to retain `p>=2` while approaching the bipartite forest lower bound,
or accept a small odd-cycle penalty in exchange for more than twice as much
additional feedback burden.  No novelty or release gate was triggered.
