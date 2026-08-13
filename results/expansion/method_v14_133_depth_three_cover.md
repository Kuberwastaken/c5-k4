# Method v0.14: WOWII 133 depth-three cover

Date: 2026-08-13

Local certificate: `lean/GraphConjecture133DepthThreeCover.lean`

## Exact incidence analysis

For one forward neighbor `a` of a valid depth-two vertex `b`, encode its
contacts with geodesic vertices `x₀,...,x₄` as a five-bit row.

Two elementary restrictions apply:

- consecutive contacts are forbidden by triangle-freeness;
- contacts two indices apart are forbidden by C4-freeness, because
  `a-x_i-x_(i+1)-x_(i+2)-a` would be a four-cycle.

Exhaustive enumeration of all 32 five-bit rows leaves exactly:

```text
∅, {4}, {3}, {2}, {1}, {1,4}, {0}, {0,4}, {0,3}.
```

Thus a candidate can meet at most two early geodesic vertices.  Restricted
to indices `1..4`, the only allowable double-contact row is `{1,4}`.

This enumeration is a transparent finite combinatorial calculation, not a
Lean oracle.  The forbidden rules themselves are proved symbolically below.

## Formal forbidden-pair table

`not_adj_both_ends_of_edge_of_triangleFree` proves the generic consecutive
contact obstruction.

`not_adj_both_distance_two_of_c4Free` proves the generic distance-two
obstruction, including all six distinctness obligations for the resulting
not-necessarily-induced C4.

Applied to geodesic indices one through four,
`depthThree_forbiddenPairTable` certifies these five impossible pairs:

```text
{1,2}, {2,3}, {3,4}, {1,3}, {2,4}.
```

`two_contacts_force_endpoints` packages the exact conclusion: if one fresh
candidate has two distinct contacts among indices `1..4`, those indices must
be exactly `1` and `4`.

## What this does and does not settle

The result sharply limits each row of the three-way cover, but it does not by
itself force an empty row.  Three forward vertices may each carry a singleton
early contact without violating the row restrictions.  Even the exceptional
row `{1,4}` is locally compatible with the five proved forbidden pairs.

Consequently the smallest remaining obstruction is now classified more
precisely:

```text
three nonempty rows, each chosen from
{4}, {3}, {2}, {1}, {1,4}, {0}, {0,4}, {0,3}.
```

To eliminate it, the next lemma must relate **different rows**.  The most
promising constraints use the fact that all three candidates share the same
parent `b`: two candidates contacting suitable nearby targets can create a
four-cycle through `b`, while some farther target combinations create a
geodesic shortcut.  The present file deliberately does not claim those
cross-row constraints before they are proved.

The exhaustive controls from v0.13 have no nonempty three-row cover at all:
all 5,616 valid `b` choices in `PG(2,3)` and all 10,080 in `Kneser(7,3)` have
a contact-free forward neighbor.

## Lean audit

The module uses no native computation, proof holes, or custom axioms.  It was
checked with local dependencies and warnings promoted to errors:

```text
LEAN_PATH=/tmp/c5k4-133-depth3:/tmp/c5k4-133-early-comb:\
/tmp/c5k4-133-handle-existence:/tmp/c5k4-133-deep-handle:\
/tmp/c5k4-133-degree-four:/tmp/c5k4-133-regular:\
/tmp/c5k4-133-specialization:/tmp/c5k4-133-v07-check \
  timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133DepthThreeCover.lean
```

Result: exit code 0 in 6.7 seconds.

This is a forbidden-contact classification, not a proof of full handle
existence and not a counterexample release candidate.
