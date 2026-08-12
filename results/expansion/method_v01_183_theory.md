# Method v0.1 lane: WOWII 183 after theorem subtraction

Date: **2026-08-12**. Status: **blocked structural subcase / strengthened
theorem signal**. This note does not claim a proof or a counterexample.

## Fixed statement and residual

For a finite simple connected graph `G` of order at least two, WOWII 183 asks

```text
L_s(G) + b(G) >= Delta(G^2) + 2 rad(G^2).
```

Write `H=G^2`, `r=rad(H)`, and

```text
q = n - 1 - Delta(H).
```

The proved WOWII 173 baseline of DeLaViña--Waller is

```text
L_s(G) + b(G) >= n + 1,
```

equivalently `b(G)>=gamma_c(G)+1`.  Thus the residual correction demanded by
183 over the theorem is

```text
2(r-1)-q.
```

The original source was re-read rather than inferred from the WOWII summary:
Theorem 4 and its full greedy connected-bipartite construction appear in
DeLaViña and Waller, *Spanning Trees with Many Leaves and Average Distance*,
EJC 15 (2008), #R33.  Their closing section explicitly leaves equality in
Theorem 4 as an open characterization problem.

Primary source:
<https://www.combinatorics.org/ojs/index.php/eljc/article/download/v15i1r33/pdf>

## New exact structural reduction

For a vertex `x`, let `S_i(x)` be its distance-`i` layer in `G`.  Distances in
the square satisfy

```text
dist_H(x,y) = ceil(dist_G(x,y)/2),
ecc_H(x) = ceil(ecc_G(x)/2),
rad(H) = ceil(rad(G)/2).
```

Choose `x` of maximum degree in `H`.  Its nonneighbors in `H` are exactly the
vertices at `G`-distance at least three, so

```text
q = sum_{i>=3} |S_i(x)|.
```

Since `rad(G)>=2r-1` and `ecc_G(x)>=rad(G)`, every layer through
`S_{2r-1}(x)` is nonempty.  Consequently

```text
q >= 2r-3.
```

More importantly, equality is rigid.  If `q=2r-3`, then

```text
ecc_G(x) = 2r-1,
|S_i(x)| = 1 for every 3 <= i <= 2r-1,
and there are no later layers.
```

Thus the extremal square profile consists of an arbitrary radius-two core
followed by a unique distance tail.

### Safe tail pruning

When `2r-1>=4`, the unique last-layer vertex is a leaf: its only possible
neighbor is the unique vertex in the preceding layer.  If `z` is any leaf of
a connected graph and `G'=G-z`, then

```text
b(G) = b(G') + 1,
gamma_c(G) <= gamma_c(G') + 1.
```

The first equality holds because a leaf can be added to every induced
bipartite subgraph without creating a cycle.  For the second inequality, a
minimum connected dominating set of `G'` either already contains the support
of `z`, or that support can be added while preserving connectivity.
Therefore

```text
b(G)-gamma_c(G) >= b(G')-gamma_c(G').
```

Deleting the forced tail one leaf at a time preserves connectedness and
nonbipartiteness.  It follows that the entire unresolved lemma reduces to the
following radius-three core proposition:

> **Core proposition.** If a connected nonbipartite graph has a vertex `x`
> with exactly one vertex at distance three and no vertex farther away, then
> `b(G)>=gamma_c(G)+2`.

A proof of this proposition would prove WOWII 183.  A counterexample would
refute 183 after reattaching any desired forced tail.

## Interaction with the stronger published baseline

The same 2008 paper proves its Theorem 5, equivalent to

```text
b(G) >= gamma_c(G) + floor(mu(G)/2),
```

where `mu(G)` is maximum local independence.  Hence the desired `+2` already
follows when `mu(G)>=4`.  The unresolved core can therefore be narrowed again
to

```text
unique distance-3 vertex, nonbipartite, and mu(G) <= 3.
```

The tight examples through order eight all in fact have `mu(G)=2`; this is
the claw-free boundary (`mu<=2`) rather than a high-local-independence case.
The tempting step "nonbipartite implies another unit of theorem slack" is
false in general: odd cycles and several dense diameter-two graphs attain the
173 equality wall.  The unique-far-vertex hypothesis is essential.

## Exact bounded audit

[`scripts/verify_wowii_183_extremal.py`](../../scripts/verify_wowii_183_extremal.py)
independently computes the square, `r`, `q`, `b`, and `gamma_c`; it also asserts
the layer rigidity above at every maximum-degree vertex of the square.  All
optimization is exhaustive subset enumeration, with no ILP, floating point,
or heuristic invariant values.

Results:

| catalogue | connected graphs | `q=2r-3` | nonbipartite critical | minimum `b-gamma_c-1` |
|---|---:|---:|---:|---:|
| NetworkX Graph Atlas, orders 2--7 | 995 | 15 | 7 | 1 |
| McKay connected order-8 catalogue | 11,117 | 187 | 140 | 1 |

There are 7 order-at-most-7 and 45 order-8 examples attaining the proposed
bound `b=gamma_c+2`; none attains the forbidden `b=gamma_c+1` value.  The
order-8 source is Brendan McKay's CC-BY-4.0 graph6 catalogue:
<https://users.cecs.anu.edu.au/~bdm/data/graph8c.g6>.

Reproduction (each command is externally capped at 60 seconds):

```bash
timeout 60s .venv/bin/python scripts/verify_wowii_183_extremal.py --summary-only
curl -fsSL https://users.cecs.anu.edu.au/~bdm/data/graph8c.g6 \
  | timeout 60s .venv/bin/python scripts/verify_wowii_183_extremal.py \
      --graph6 - --summary-only
```

The local project virtual environment had been intentionally pruned for disk
space, so this run used an already-installed NetworkX 3.6.1 environment from
another project.  This does not affect the pure NetworkX algorithm, but the
commands above describe the intended project-local reproduction once its
environment is recreated.

An attempted streaming order-9 extension did not return a completed summary
inside this work stretch and is **not counted**.  No conclusion is inferred
from that incomplete run.

## Formal-library check

The current `formal-conjectures` support library defines
`SimpleGraph.IsConnectedDominating` and `connectedDominationNumber` in
`FormalConjecturesForMathlib/Combinatorics/SimpleGraph/Domination.lean`, and
defines `largestInducedBipartiteSubgraphSize` in the adjacent induced-subgraph
support file.  It explicitly says connected variants are support-library
extensions rather than mature mathlib theory.  No existing theorem relating
these two invariants, graph powers, or the required equality case was found.
Consequently a Lean proof would presently require formalizing substantial new
graph theory; there is no honest short formal certificate until the core
proposition is settled on paper.

## Method v0.1 outcome and stop decision

- **Prediction:** the residual-one profile may be a theorem shadow.
- **Theorem subtraction:** reduced 183 to `q=2r-3` and one extra unit over 173.
- **New obstruction identity:** equality forces a singleton distance tail.
- **Transformation/reduction:** safe leaf pruning reduces all radii to one
  radius-three core proposition.
- **Bounded evidence:** exhaustive through order eight, with zero violations.
- **Failed assumption:** source Theorem 5 does not finish the low-local-
  independence (`mu<=3`) core.
- **Classification:** strengthened theorem signal, blocked at a precise
  structural subcase; neither a disproof nor a proof.
- **Hard stop:** do not spend further unguided random-search budget on 183.
  Resume only with a proof idea for the core proposition, an equality-case
  theorem for DeLaViña--Waller, or a complete exact catalogue extension.
