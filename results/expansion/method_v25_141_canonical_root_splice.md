# Method v0.25: WOWII #141 canonical root-path splice

Date: 2026-08-13
Status: supplied last-common-vertex premise removed

## Result

[`lean/GraphConjecture141CanonicalRootSplice.lean`](../../lean/GraphConjecture141CanonicalRootSplice.lean)
constructs the last-common root-path splice directly from any two finite
simple paths beginning at the same root.  Callers no longer supply a vertex
`w` or prove `IsLastCommonVertex p q w`.

The new bounded-cycle constructor therefore removes one of the two premises
left open in v0.24.  Only closing-edge exclusion remains.

## Canonical selection

For paths

```text
p : r -> x
q : r -> y,
```

the construction applies mathlib's finite first-hit lemma to:

```text
p.reverse
q.support.toFinset.
```

The filtered set is nonempty because the common root `r` belongs to both
supports.  The selected vertex `w` is the first vertex of `q.support`
encountered while walking from `x` backward along `p`.  Equivalently, it is a
last common vertex when viewed from the root.

This orientation fits the splice API particularly cleanly.  Define:

```text
pxr := p.reverse.takeUntil w  -- x -> w
qy  := q.dropUntil w          -- w -> y.
```

The first-hit property says every vertex common to `pxr.support` and
`q.support` equals `w`.  Path nodupness excludes `w` from `qy.support.tail`,
so `pxr.support` and `qy.support.tail` are disjoint.  Their append is therefore
a simple path from `x` to `y`.

Lean also proves the exact and bounded lengths:

```text
(pxr.append qy).length = pxr.length + qy.length
(pxr.append qy).length <= p.length + q.length.
```

## Improved bounded-cycle interface

`bounded_cycle_of_root_paths_and_endpoint_edge` performs the canonical
selection internally.  Given an endpoint edge and its exclusion from the
selected simple splice, it constructs a simple cycle of length at most

```text
p.length + q.length + 1.
```

Thus the v0.24 `IsLastCommonVertex` premise is eliminated.  The exact next
obligation is the metric closing-edge exclusion for distinct equal-layer
shortest-path endpoints.

## Verification

The complete recursive #141 chain was compiled from source into the fresh
directory `/tmp/c5k4_141_last_audit.FEpB19`.  Each module used:

```bash
LEAN_PATH=/tmp/c5k4_141_last_audit.FEpB19 timeout 60s lake env lean \
  -DwarningAsError=true \
  -o /tmp/c5k4_141_last_audit.FEpB19/<MODULE>.olean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/<MODULE>.lean
```

The chain from `GraphConjecture141Extraction` through
`GraphConjecture141RootPathSplice` passed, followed by the new
`GraphConjecture141CanonicalRootSplice` module.  Every invocation exited `0`,
emitted no Lean diagnostics, used warnings-as-errors, and was individually
capped at 60 seconds.  The new file contains no `sorry`, `admit`,
`native_decide`, `#print`, or custom axiom declaration.
