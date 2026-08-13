# WOWII 40 v0.11: the first positive-feedback bipartite slice

**Date:** 2026-08-13

**Outcome:** a no-`sorry` proof of WOWII 40 for bipartite graphs with
feedback-deletion coordinate one and an explicit path on at least four
vertices.

**Read-only upstream snapshot:** `formal-conjectures`
`9a1636c4030039f70cf78b866c216d8b6c5f35b0`

## The path-support cover

The v0.10 edge cover paid one unit of linear-forest rank. This lane
generalizes that construction. Given a path `p`, define a path cover whose
members are:

```text
p.support.toFinset
and one singleton {x} for every x outside p.support.
```

The Lean file proves directly from `IsPathCover` that these members are
pairwise disjoint, cover the vertex set, and are supports of paths. If the
support has at least two vertices, its cover cardinality satisfies

```text
pathSupportCover.card + p.support.card = n + 1.
```

Consequently a path on at least four vertices gives

```text
pathCoverNumber G + 3 <= n,
```

which is exactly `ell >= 3` in the v0.9 deficiency coordinates.

## Positive-feedback theorem

The principal theorem assumes:

```text
G.IsBipartite,
feedbackDeletion G = 1,
and G contains a path whose support has at least four vertices.
```

Bipartiteness proves `B=n`, hence `o=0`. The feedback hypothesis is exactly
`tau=1`, and the path-support cover gives `ell>=3`. Therefore

```text
ell + o >= 3 = 2*tau + 1.
```

The file transports this through the already-formalized deficiency bridge
and proves the exact upstream ceiling statement for WOWII 40.

This is the first formally closed `tau>0` class. It covers the intended
four-vertex-cycle and longer-cycle examples once their evident path witness
and `tau=1` value are supplied. The generic theorem itself does not assume
connectedness or unicyclicity; it states only the invariant and witness data
actually used.

## EQKo remains a warning, not an obstruction

The known six-vertex `EQKo` graph has

```text
tau=1, o=0, ell=4.
```

It contains paths on at least four vertices, so the new theorem is consistent
with it and proves only the weaker required `ell>=3`. The false pointwise
insertion statement is still false: deleting vertex `4` or `5` lowers `tau`
without increasing `ell`. Nothing in this lane charges a feedback change to
a newly inserted edge; the proof instead obtains all three required units at
once from one long path.

## Verification

New file:

```text
lean/GraphConjecture40PositiveFeedback.lean
```

After compiling its local import chain, the independent check was:

```text
timeout 60s env LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean \
  lake env lean -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture40PositiveFeedback.lean
```

It exited `0` in 6.69 seconds with no output. The source contains no
`sorry`, `admit`, or custom axiom.

## Remaining boundary

For the complete connected bipartite base one must prove

```text
ell >= 2*tau + 1
```

for arbitrary positive `tau`. The present construction pays for `tau=1`
with one four-vertex path. A plausible next structural rung would find a
spanning linear forest with at least `2*tau+1` edges from a minimum feedback
set, globally rather than one deletion at a time. The `EQKo` warning rules out
the naive pointwise induction but not a block-level or amortized construction.

Classification: **FORMAL POSITIVE-DEFICIENCY SPECIAL CASE; no counterexample,
release, or external claim.**
