# WOWII 40 v0.13: disjoint path families as linear-forest certificates

**Date:** 2026-08-13

**Outcome:** the single-path sufficient condition is generalized to arbitrary
finite families of pairwise vertex-disjoint paths, giving the exact formal
certificate interface for spanning-linear-forest rank.

**Read-only upstream snapshot:** `formal-conjectures`
`9a1636c4030039f70cf78b866c216d8b6c5f35b0`

## Formal path families

The new file defines `IsPathSupportFamily G P` to mean:

1. distinct members of `P` are vertex-disjoint;
2. every member is the support finset of an actual path in `G`.

Let `U` be the union of all supports. The spanning completion of `P` adds one
singleton path for every vertex outside `U`. The file proves directly that
this completion is a repository `IsPathCover`.

The completion cardinality is exact:

```text
completion.card + U.card = n + P.card.
```

Equivalently, its linear-forest rank is

```text
n - completion.card = U.card - P.card.
```

This is precisely the edge count of the disjoint path family: a path on `q`
vertices contributes `q-1`, and summing over components gives total covered
vertices minus the number of components.

## Generic witness-to-deficiency theorem

To avoid truncated subtraction, the public comparison is stated as:

```text
P.card + r <= U.card
  -> pathCoverNumber G + r <= n.
```

For a bipartite graph with feedback-deletion coordinate `k`, instantiate
`r=2k+1`. The principal theorem is therefore:

```text
G.IsBipartite
and feedbackDeletion G = k
and IsPathSupportFamily G P
and P.card + (2k+1) <= U.card
  -> WOWII 40.
```

The conclusion is the exact upstream real/ceiling statement. This strictly
contains the single-path v0.12 theorem: a single path on `2k+2` vertices has
one component and rank `2k+1`.

## What remains graph-theoretic

The formal “spanning linear forest of rank at least `2k+1` is sufficient”
transfer is now complete. The unresolved connected bipartite base is exactly
the existence assertion

```text
feedbackDeletion G = k
  -> exists a disjoint path family P,
       P.card + (2k+1) <= coveredVertices(P).card.
```

No counterexample to this existence statement was introduced by the known
`EQKo` control: it has `tau=1` and `ell=4`, so it has more than the required
rank three. What `EQKo` refutes is only the stronger pointwise induction rule
that every feedback-number drop must create a new rank unit. The v0.13
certificate is global and therefore preserves that warning.

The hoped generic witness-to-deficiency statement itself is true; no smaller
obstruction arises because the Lean proof constructs the spanning path cover
explicitly and establishes its exact cardinality. The remaining existence
claim is the substantive theorem boundary and is not asserted here.

## Verification

New file:

```text
lean/GraphConjecture40PathFamily.lean
```

After compiling its local import chain, the independent check was:

```text
timeout 60s env LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean \
  lake env lean -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture40PathFamily.lean
```

It exited `0` in 6.18 seconds with no output. The source contains no
`sorry`, `admit`, or custom axiom. All subprocesses remained below the
60-second cap.

## Next rung

The best next step is no longer more optimization plumbing. It is a
block-level construction in a connected bipartite graph from a minimum
feedback vertex set to a disjoint path family of rank at least `2tau+1`.
Because `EQKo` blocks vertex-by-vertex charging, the natural units are blocks,
ears, or a globally maximal linear forest with an exchange argument.

Classification: **FORMAL GENERAL LINEAR-FOREST CERTIFICATE; no full proof,
counterexample, release, or external claim.**
