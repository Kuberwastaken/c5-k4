# Method v0.26: WOWII #141 equal-layer cycle closure

Date: 2026-08-13
Status: closing-edge premise eliminated; radius-three cycle bound verified

## Result

[`lean/GraphConjecture141EqualLayerClosure.lean`](../../lean/GraphConjecture141EqualLayerClosure.lean)
closes the final premise left by the v0.25 canonical root-path splice.

For two equal-length root geodesics ending at distinct adjacent vertices, Lean
now selects the last common vertex internally and constructs a simple cycle.
The caller supplies neither:

- a last-common vertex or intersection certificate; nor
- a proof that the endpoint edge is absent from the spliced path.

The resulting general bound is

```text
cycle length <= p.length + q.length + 1.
```

When both endpoints lie at distance at most three from the root, the cycle has
length at most seven.

## Metric endpoint exclusion

If `p : r -> x` and `q : r -> y` are shortest paths with equal lengths and
`x != y`, then

```text
x ∉ q.support
y ∉ p.support.
```

For example, if `x` occurred on `q`, the prefix `q.takeUntil x` would be a
subwalk of a geodesic and hence itself shortest.  Its length would equal
`dist r x = p.length = q.length`; the endpoint-at-prefix-index lemma would
then force `x = y`.

## Why the closing edge cannot occur

For any simple path `t : x -> y`, if the endpoint edge `{x,y}` occurs in
`t.edges`, mathlib's first-edge property for simple paths shows that `y` is
the second vertex of `t`.  The remaining tail is then a simple walk from `y`
to itself, hence nil.  Therefore `t.length = 1`.

Apply this to the canonical splice

```text
t = pxr.append qy.
```

If `t.length = 1`, then `pxr.length + qy.length = 1`, so one side has length
zero:

- `pxr.length = 0` forces `x = w`, putting `x` on `q`; or
- `qy.length = 0` forces `w = y`, putting `y` on `p`.

Both contradict the metric endpoint-exclusion lemma.  Thus the closing edge
is absent automatically.

## Certificate constructors

The module proves:

- `equal_geodesic_endpoints_not_mem`;
- `simple_path_length_one_of_endpoint_edge_mem`;
- `equal_geodesic_splice_closing_edge_not_mem`;
- a membership-enriched canonical splice constructor;
- `bounded_cycle_of_equal_geodesic_endpoint_edge`; and
- `cycle_length_le_seven_of_equal_layer_three`.

The last theorem is the exact equal-layer radius-three cycle certificate:
distinct adjacent same-layer vertices produce a simple cycle of order at most
seven.  A girth lower bound of eight or more therefore excludes such an edge.

## Verification

The entire recursive #141 chain was compiled from source into the fresh
directory `/tmp/c5k4_141_equal_audit.ql4rbJ`.  Every module used:

```bash
LEAN_PATH=/tmp/c5k4_141_equal_audit.ql4rbJ timeout 60s lake env lean \
  -DwarningAsError=true \
  -o /tmp/c5k4_141_equal_audit.ql4rbJ/<MODULE>.olean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/<MODULE>.lean
```

All dependencies from `GraphConjecture141Extraction` through
`GraphConjecture141CanonicalRootSplice` passed, followed by the new
`GraphConjecture141EqualLayerClosure`.  Every process exited `0`, emitted no
Lean diagnostics, used warnings-as-errors, and was individually capped at 60
seconds.  The new module contains no `sorry`, `admit`, `native_decide`,
`#print`, or custom axiom declaration.
