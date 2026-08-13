# Method v0.24: WOWII #141 last-common root-path splice

Date: 2026-08-13
Status: supplied-last-common splice and bounded cycle closure verified

## Scope

This rung continues the exact upstream WOWII #141 proof extraction after the
v0.23 simple-cycle decomposition.  It formalizes the root-path surgery in a
small reusable certificate API.  It does not yet claim the full radius-three
cycle-peak theorem.

## Last-common certificate

[`lean/GraphConjecture141RootPathSplice.lean`](../../lean/GraphConjecture141RootPathSplice.lean)
defines `IsLastCommonVertex p q w` for two paths beginning at the same root.

The certificate says:

- `w` lies on both path supports; and
- after both paths are split at `w`, any vertex in both suffix supports is
  equal to `w`.

This is the exact finite-path meaning of “`w` is their last common vertex.”
The current API accepts the witness and this property explicitly, separating
selection from the graph-theoretic splice.

## Verified suffix splice

The theorem `splice_at_last_common_vertex` starts with simple root paths

```text
p : root -> x
q : root -> y
```

and a last-common certificate at `w`.  It takes the `dropUntil w` suffixes

```text
px : w -> x
qy : w -> y
```

and proves:

- both suffixes are simple paths;
- `px.reverse.support` is disjoint from `qy.support.tail`;
- `px.reverse.append qy` is a simple path from `x` to `y`;
- its length is exactly `px.length + qy.length`; and
- its length is at most `p.length + q.length`.

The disjointness proof is the key root-path step.  Any common support vertex is
`w` by the last-common hypothesis, while nodupness of `qy.support` excludes
its starting vertex `w` from the tail.  The append is then a path by the
standard nodup-append criterion.

## Bounded cycle closure

`close_spliced_path_with_edge` proves the standard endpoint closure: a simple
path from `x` to `y`, together with the edge `y-x`, is a simple cycle whenever
that closing edge is absent from the path's edge list.

`bounded_cycle_of_last_common_and_endpoint_edge` combines both results.  Given
the closing-edge exclusion, it constructs a simple cycle `c` satisfying

```text
c.length <= p.length + q.length + 1.
```

This is exactly the numerical form needed for equal-layer adjacency.  Two
shortest root paths of length `k` would produce a cycle of length at most
`2k+1`; at radius three this is at most seven, contradicting girth at least
ten.

## Exact remaining obstruction

Two finite/metric obligations remain before the radius-three certificate can
be instantiated directly:

1. **Canonical selection.** From two shortest root paths, select a common
   support vertex maximal along the paths and prove it satisfies
   `IsLastCommonVertex`.  The common-support set is finite and contains the
   root, but its maximum-index construction has not yet been connected to the
   dependent `dropUntil` API.

2. **Closing-edge exclusion.** Prove that the equal-layer endpoint edge is not
   already an edge of the spliced connector.  For shortest paths to distinct
   vertices at the same layer, the only dangerous degenerate branch would put
   one endpoint on the other's shortest path immediately before the other;
   that would force their root distances to differ by one, contradicting
   equal layers.  This metric argument remains to be formalized.

After these two obligations, the verified bounded-cycle theorem yields the
same-layer-edge contradiction.  The analogous two-parent case uses two root
paths ending at the parents and closes through their common child, yielding
the required `2k` bound.  Those two contradictions supply `uniqueParent` and
the cycle-peak field of the v0.22 radius-three certificate.

## Verification

From the `formal-conjectures` checkout:

```bash
LEAN_PATH=/tmp/c5k4-141-splice:/tmp/c5k4-141-cycle \
timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture141RootPathSplice.lean
```

Result: exit code 0, no diagnostics, approximately seven seconds.  The file
contains no `sorry`, `admit`, `native_decide`, or custom axiom.
