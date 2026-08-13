# WOWII 40 v0.12: a parametric path witness for arbitrary feedback deletion

**Date:** 2026-08-13

**Outcome:** the positive-feedback class is extended from `tau=1` to
arbitrary `tau=k` whenever the bipartite graph contains one path on at least
`2k+2` vertices. A concrete `tau=2` endpoint requires a six-vertex path.

**Read-only upstream snapshot:** `formal-conjectures`
`9a1636c4030039f70cf78b866c216d8b6c5f35b0`

## Generic witness-to-rank theorem

The path-support cover constructed in v0.11 is now packaged without fixing
its size. If `p` is a path with support order `q>=2`, the new Lean theorem
proves

```text
pathCoverNumber G + (q-1) <= n.
```

Thus the complement coordinate

```text
ell = n - pathCoverNumber G
```

satisfies `ell>=q-1`. This is the exact path-instance of the more general
spanning-linear-forest intuition: a path with `q` vertices supplies `q-1`
edges of rank, while every outside vertex remains a singleton component.

## Arbitrary feedback-deletion coordinate

For a bipartite graph, `o=0`. If

```text
feedbackDeletion G = k
```

and a path has at least `2k+2` vertices, then the generic witness theorem
gives

```text
ell >= (2k+2)-1 = 2k+1 = 2*tau+1.
```

The file transports this deficiency inequality to the exact upstream
real/ceiling statement of WOWII 40. The result is uniform in `k`; v0.11 is
recovered at `k=1`.

The concrete theorem for `k=2` states:

```text
G.IsBipartite
and feedbackDeletion G = 2
and G has a path supported on at least 6 vertices
  -> WOWII 40.
```

## Scope and relation to linear forests

This theorem uses one path, not an arbitrary family of disjoint paths. It is
therefore a clean sufficient condition, not the full connected bipartite
base. Mathematically, the same counting argument extends to a spanning
linear forest with at least `2k+1` edges: use its nontrivial path components
together with singleton components. The repository currently represents
path covers but has no spanning-linear-forest structure or equivalence API,
so the single-path theorem is the strongest compact formal witness bridge
available without introducing a second bespoke optimization layer.

The theorem is substantive even when no single path spans the graph: it only
requires a path long enough to pay the feedback coordinate; every vertex
outside that path is handled automatically by the formal cover construction.

## EQKo check

The `EQKo` obstruction has `tau=1` and `ell=4`, and its relevant path witness
pays at least the required three units. The present theorem never asserts
that deleting one vertex increases `ell`; it constructs all required rank
from a fixed path in the original graph. Therefore it is compatible with the
known countermodel to pointwise insertion.

## Verification

New file:

```text
lean/GraphConjecture40LinearForest.lean
```

After compiling its local import chain, the independent warning-as-error
check exited `0` with no output. Every individual subprocess remained under
the 60-second cap. The final Lean invocation was:

```text
timeout 60s env LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean \
  lake env lean -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture40LinearForest.lean
```

The source contains no `sorry`, `admit`, or custom axiom.

## Remaining boundary

The complete connected bipartite base still requires an existence theorem:

```text
tau=k -> some spanning linear forest has at least 2k+1 edges.
```

The current file proves the downstream transfer once that forest is a single
sufficiently long path. The next proof work should broaden the explicit cover
from one path support to a finite family of pairwise disjoint path supports,
then isolate the actual graph-theoretic construction of such a family from a
minimum feedback set. That construction must be global or block-level;
`EQKo` continues to forbid naive pointwise induction.

Classification: **FORMAL PARAMETRIC POSITIVE-DEFICIENCY CLASS; no
counterexample, release, or external claim.**
