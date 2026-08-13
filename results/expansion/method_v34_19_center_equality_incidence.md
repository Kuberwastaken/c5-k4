# Method v34: WOWII #19/#13 center equality incidence

## Scope

This rung converts the sole numerical obstruction left by the v33 center
charge into exact neighborhood-incidence data and combines it with the
saturated path/neighborhood cover.

Lean source:
`lean/GraphConjecture19CenterEqualityIncidence.lean`

## Full local independence means an independent neighborhood

The first theorem proves the representation bridge

```text
indepNeighborsCard(G,v) = degree(v)
  -> G.neighborSet(v) is independent.
```

It extracts a maximum independent set from the induced neighborhood graph.
That set is contained in `neighborFinset v`; equality of its cardinality with
the degree, which is the cardinality of the whole neighborhood finset, forces
the two finite sets to be equal.  Independence then transfers back to the
entire ambient neighbor set.

Thus the v33 equality obstruction is not merely a number: it supplies a
maximum-degree vertex whose whole open neighborhood is independent.

## Saturated center incidence

Assume the on-path saturation identity

`P union N(c) = V`.

If `N(c)` is independent, every vertex outside `P` is forced by saturation
into `N(c)`.  Hence the complete off-path set

`V \ P`

is independent.  This is certified directly as an ambient
`SimpleGraph.IsIndepSet` statement.

## Exact three-way theorem

For the center-endpoint geometry, the final theorem proves:

1. WOWII 13 already holds; or
2. `N(c)` is independent and every vertex outside `P` is independent as one
   set; or
3. there is a distinct vertex `v != c` of maximum degree whose entire open
   neighborhood is independent.

This distinction is necessary.  The equation
`localMax = maxDegree` does not imply that the maximum is attained at `c`;
the file explicitly separates the center-attained and distinct-witness cases.

## Exact residual

The center equality obstruction now has two concrete incidence branches:

- **center-attained:** the saturated graph consists of the geodesic plus an
  independent off-path set contained in the independent neighborhood `N(c)`;
- **distinct witness:** another maximum-degree vertex has a fully independent
  neighborhood.

The next useful step in the center-attained branch is to exploit the
tree-plus-one-edge restriction on how the independent off-path vertices can
attach to the geodesic; any two attachments producing a second route should
force a short fundamental cycle.  The distinct-witness branch needs the
position of `v` under `P union N(c) = V` split into `v in P` or `v in N(c)`.

The consecutive-added-edge-on-geodesic geometry remains separate, as
requested.

## Verification

The local dependency chain and new target were compiled using the pinned
`formal-conjectures` environment with `-DwarningAsError=true`.  The fresh
target check exited 0 in 8.2 seconds, under the 60-second cap, with no warnings.
No `sorry`, `admit`, `native_decide`, or custom axioms are used.
