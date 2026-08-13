# WOWII 19 dense/symmetric prospective lane

Date: **2026-08-13 UTC**

Final status: **BOUNDED_HOLD — no crossing**

This was an independent lane from the odd-cycle block-tree/surgery work. It
tested only the precommitted line-graph, connected-complement,
lexicographic/nonuniform-blow-up, join, and one-edge-perturbation grammar.

## Exact result

| Gate/stratum | Profiles | Crossings | Tight |
|---|---:|---:|---:|
| Connected Atlas graphs, orders 2--7 | 995 | 0 | 599 |
| Frozen dense/symmetric family | 2,000 | 0 | 481 |

The generator stopped at exactly 8,000 unique labeled-adjacency certificates;
the first 2,000 connected profiles were evaluated exactly, matching the frozen
cap. The minimum signed residual

`R19 = b - maxLocalAlpha - floor(average eccentricity)`

was zero.

Named controls reproduced the expected values: `K5`, `C5`, and `C5[K2]` are
tight; `C6` and `K3,4` have residual one; Petersen has residual two.

## Independent tight-case recomputation

`C5[K2]` was recomputed without the primary induced-subset bipartiteness
routine. A custom BFS gave eccentricity two at all ten vertices. Direct
neighborhood bitmask search gave maximum local independence two. An exhaustive
three-state optimization (excluded/red/blue) proved the maximum induced
bipartite order is four, with witness vertices `{4,5,8,9}`. Thus

`b = 4 = 2 + floor(2)`.

## Obstruction identity

Let `v` attain maximum neighborhood independence `lambda`, and let
`A subset N(v)` be an independent set of order `lambda`.

- `G[A union {v}]` is an induced star, so `b >= lambda + 1`.
- If `v` is not universal, choose `x` outside `N[v]`. Then
  `G[A union {v,x}]` is still bipartite: `A` has no internal edges, `vx` is
  absent, and every remaining edge runs between `{v,x}` and `A`. Hence
  `b >= lambda + 2`.

Consequently every connected graph of diameter at most two satisfies #19.
Complete graphs use the first bound with average eccentricity one; every other
diameter-two graph uses the second with `floor(avgEcc) <= 2`.

This explains why joins, most connected complements, and dense blow-ups cannot
cross the wall: their density collapses eccentricity to at most two at exactly
the rate needed for the two-vertex induced-bipartite extension.

The source registry's 2005 note gives the complementary theorem shadow: when
average eccentricity is at most `diameter - 1`, #19 follows from #13. The live
search locus is therefore much narrower than the original transformation list:
graphs with `floor(avgEcc) >= 3`, especially self-centered graphs whose
lambda-maximizing vertices cannot be coupled to the diameter/geodesic witness.

## Status and novelty gate

Upstream `main` still labels #19 research/open with `sorry`. However, PR #4559
is open and claims a complete external Lean proof of the unchanged theorem;
PR #1511 separately verifies only `K3`. Any future apparent crossing must first
be reconciled against #4559's proof, so this negative run creates no novelty or
public-action path.

One preliminary implementation timed out during pairwise-isomorphism
deduplication before producing profiles; a later preliminary run was discarded
because its generator overshot the frozen generation cap by eleven. Both are
recorded in the incremental ledger. The final counted run obeyed the exact
8,000/2,000 caps. Every subprocess was capped at 60 seconds. No commit, push,
release, issue, PR, or other public action was made.
