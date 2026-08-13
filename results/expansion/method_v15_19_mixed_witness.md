# Method v0.15 proof extraction: WOWII 19 mixed witness

Date: **2026-08-13 UTC**

Status: **eccentric-geodesic mixed witness proved; covers 140/154 hard Atlas cases; exact residual 14 recorded**

## Frozen test before formalization

The remaining v0.14 class consists of connected graphs with diameter at least
three for which every peripheral vertex loses at least two units relative to
the global maximum local independence number.  There are 154 such graphs in
the connected Graph Atlas through order seven.

The natural mixed proposal was tested exactly before Lean work:

```text
some vertex c attaining localMax has ecc(c) >= diameter-1.
```

It holds on 140 of the 154 hard controls and fails on 14.  The smallest
countermodel is the six-vertex tree Graph6 `EiGO`, with edges

```text
01, 12, 13, 24, 35.
```

Its diameter is four.  Vertex 1 uniquely attains local neighborhood
independence three but has eccentricity two; both peripheral leaves have local
independence one.  Thus the maximum-local star and a geodesic from its center
cannot by themselves supply the necessary `diameter+localMax-1` count.

The bounded exact sweep completed in 1.4 seconds under the 60-second cap.

## Formal mixed witness

[`lean/GraphConjecture19MixedWitness.lean`](../../lean/GraphConjecture19MixedWitness.lean)
generalizes the canonical-tail construction away from diametral endpoints.
For arbitrary vertices `c,w` at distance at least two it proves

```lean
((G.dist c w + indepNeighborsCard G c : Nat) : Real) <= b G.
```

The proof couples:

- a maximum independent set inside `N(c)`;
- the canonical retained tail of a shortest `c`--`w` path;
- endpoint-distance parity coloring;
- exact disjoint-union cardinality and `b` insertion.

It then proves the source WOWII 13 inequality whenever a vertex attaining
`localMax` has a farthest distance at least `diameter-1`, in both explicit
long-geodesic and eccentricity-native forms.

This closes 140 of 154 previously uncovered Atlas controls structurally.  It
does not claim the remaining 14.  Their smallest member `EiGO` shows the exact
next obstruction: a successful construction must retain useful vertices from
two or more branches around a nonperipheral maximum-local vertex, rather than
selecting only one farthest geodesic.  In `EiGO`, the three independent
neighbors at the center feed two length-two arms and one leaf; a one-tail
witness discards too much of the second arm.

## Trust

Compiled with `-DwarningAsError=true`: **exit 0**.  No `native_decide`,
`sorry`, `admit`, custom axiom, upstream conjecture theorem, commit, push, or
external action was used.
