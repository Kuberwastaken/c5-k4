# WOWII 40 v0.9: exact deficiency coordinates and the zero-feedback base

**Date:** 2026-08-13

**Outcome:** no-`sorry` Lean normalization of WOWII 40 to its exact
deficiency inequality, plus a formal zero-feedback-deletion base case.

**Read-only upstream snapshot:** `formal-conjectures`
`9a1636c4030039f70cf78b866c216d8b6c5f35b0`

## Formal coordinates

The new file defines, locally,

```text
feedbackDeletion G = n - largestInducedForestSize G
oddDeletion G      = n - largestInducedBipartiteSubgraphSize G
linearForestRank G = n - pathCoverNumber G.
```

These are the exact natural-number coordinates denoted `tau`, `o`, and `ell`
in the proof ladder. The last name is intentionally conservative: this file
defines the complement of the repository path-cover number, but does not yet
claim the missing graph-theoretic bijection with maximum spanning linear
forests.

The Lean theorem `integer_bound_iff_deficiency_bound` proves

```text
p + B + 1 <= 2f  <->  2*tau + 1 <= ell + o.
```

It assumes the elementary API bound `p <= n`; the file independently proves
`f <= n` and `B <= n` directly from the two finite `sSup` definitions. The
path-cover assumption is explicit because the repository currently offers
neither an attainment lemma nor the singleton-cover upper bound for its
`sInf` definition.

The theorem `conjecture40_of_deficiency_bound` transports the right-hand
inequality all the way to the exact upstream real/ceiling statement.

## Zero-feedback-deletion rung

The file also proves:

- an acyclic graph has `f = n`;
- an acyclic graph has `B = n`;
- if it additionally has `pathCoverNumber G < n`, then WOWII 40 holds in the
  exact upstream shape.

In deficiency coordinates this is

```text
tau = 0, o = 0, ell >= 1  ->  ell + o >= 2*tau + 1.
```

Thus the complete `tau = 0` base is formal once the elementary “a connected
nontrivial graph has a path cover with fewer than `n` paths” API lemma is
supplied. Constructively, that missing lemma is obtained by putting the two
ends of any edge in one two-vertex path and every other vertex in a singleton
path. Formalizing this path-cover witness is now an isolated repository-API
task rather than part of the conjectural inequality.

## EQKo obstruction check

No pointwise insertion claim is used. The known obstruction remains the
six-vertex graph `EQKo`, with edges

```text
02, 13, 24, 25, 34, 35.
```

For this graph the frozen exact computation is

```text
n=6, tau=1, o=0, ell=4,
```

so the newly formalized deficiency inequality reads `3 <= 4` and holds.
However, deleting vertex `4` (or `5`) changes `tau` from `1` to `0` without
increasing `ell`, which refutes the tempting pointwise lemma

```text
tau(J)=tau(J-v)+1 -> ell(J)>=ell(J-v)+1.
```

The v0.9 proof is purely an exact change of coordinates and zero-deficiency
base, so it is compatible with this countermodel. Any later transfer proof
must still amortize globally rather than charge each feedback-number change
to one new linear-forest edge.

## Verification

New file:

```text
lean/GraphConjecture40Deficiency.lean
```

Independent check:

```text
timeout 60s env LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean \
  lake env lean -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture40Deficiency.lean
```

It exited `0` in 6.06 seconds with no output. The source contains no
`sorry`, `admit`, or custom axiom.

## Remaining boundary

This is not a full proof of WOWII 40. The next formal rung is one of:

1. construct the universal singleton path cover and the edge-improved cover,
   eliminating the explicit `p <= n` and `p < n` API assumptions;
2. prove the positive-feedback bipartite inequality `ell >= 2*tau + 1`;
3. prove a slack-aware transfer from a maximum induced bipartite core.

The second and third are the actual graph-theoretic boundary. The false
pointwise insertion route above must not be reused.

Classification: **FORMAL PARTIAL THEOREM; no counterexample, release, or
external claim.**
