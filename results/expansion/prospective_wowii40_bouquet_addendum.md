# Frozen prospective addendum: rooted biclique bouquets for WOWII 40

Frozen: 2026-08-13 UTC, before constructing or evaluating any bouquet.

## Input and learned obstruction

The only inputs are the ten equality seeds in the original frozen #40
block-surgery checkpoint. The completed line-graph trial showed why incidence
closure failed: every admissible output was Hamiltonian, so `p=1` and the
coordinate `L=n-p` became maximal. Its residual

```text
R = (n-p) + (n-b) - 2*(n-f)
```

therefore moved from the equality-wall values `1,2` to values as large as `7`.
The explicit obstruction is Hamiltonicity itself: feedback burden is harmless
when a spanning path keeps `p` at one.

## Frozen inverted transformation

For each equality seed `G`, select root `v` deterministically by maximum degree
and then minimum vertex label. Attach a rooted balanced-biclique bouquet:

- take `q` disjoint copies of `K_(r,r)`;
- in each copy identify one left-side vertex with `v`;
- introduce no other edges between petals or to `G`.

The common cut vertex means one path can enter at most two petals, explicitly
destroying Hamiltonicity as the petal count grows. At the same time, every
petal is bipartite but cyclic: it preserves/increases the feedback-deletion
burden while offering a large induced-bipartite set. This directly targets
lower `L=n-p` and lower `tau_B=n-b` without allowing induced-forest order to
track both coordinates freely.

This rooted multi-petal articulation operation is not a path-shaped biclique
block tree, block substitution, ear surgery, bounded edge mutation, line
graph, or prior frozen #40 family. No other operation may be added after
results are observed.

## Frozen finite trial

Construct, in this order:

1. three `K_(2,2)` petals (`q=3,r=2`) on every seed fitting order at most 18;
2. four `K_(2,2)` petals (`q=4,r=2`) on every seed fitting the same cap;
3. two `K_(3,3)` petals (`q=2,r=3`) on every seed fitting the same cap.

Canonically deduplicate isomorphic outputs. Evaluate at most 20 distinct
graphs, orders at most 18. Every process and exact solve is capped at 60
seconds.

## Gate and exactness

Before constructing a bouquet, repeat the exact 1,031-graph sanity set used in
the line-graph trial. Every development result requires maximum induced-forest
and induced-bipartite witnesses and an exact minimum path-cover decomposition.
A timeout is `INCONCLUSIVE`. A strict crossing must be independently
recomputed and pass current source/status/novelty audit before classification
as `CANDIDATE`.

Other outcomes are `DB_SANITY_REJECT` and `HOLD_BOUNDED`. No commit, push,
release, issue, PR, or other public action is authorized.
