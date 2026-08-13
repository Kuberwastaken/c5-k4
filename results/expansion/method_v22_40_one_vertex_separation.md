# WOWII 40 v0.22: explicit one-vertex separation, restriction half

**Date:** 2026-08-13

**Outcome:** an explicit one-vertex separator is formalized, together with
stateful side optimizations and the complete restriction inequality for the
exclude-cut state. The reverse union/cycle-localization half is isolated
precisely rather than assumed.

**Read-only upstream snapshot:** `formal-conjectures`
`9a1636c4030039f70cf78b866c216d8b6c5f35b0`

## Separation data

The new `OneVertexSeparation G` contains finite vertex sides `L,R` and a cut
vertex `c`, with proofs that

```text
L union R = univ,
L intersection R = {c},
no edge joins L-{c} to R-{c}.
```

The final no-cross-edge field is not needed for restriction; it is included
because it is exactly the hypothesis required by the remaining union
localization direction.

The file proves immediately that `c` lies in both sides.

## Side optimization

For any finite side `A`, define

```text
forestOrderWithin G A =
  max {|S| : S subset A and G[S] is acyclic}.
```

This is a finite natural `sSup`. The development proves:

- the state is nonempty via the empty forest;
- it is bounded by `|A|`;
- its maximum is attained;
- every explicit forest inside `A` is bounded by the state.

These lemmas are independent of ambient `Fintype` enumeration because the
finite side itself supplies the bound.

## Exact cardinal splitting outside the cut

If `S` excludes `c`, the file proves

```text
|(S intersection L)| + |(S intersection R)| = |S|.
```

Coverage shows the two restrictions exhaust `S`. Their intersection is
empty: any common vertex lies in `L intersection R={c}`, contradicting
`c notin S`.

## Complete restriction inequality

Take the attained optimum `S` for the global exclude-cut state. Its two
restrictions satisfy:

- `S intersection L` lies inside `L.erase c`;
- `S intersection R` lies inside `R.erase c`;
- both induce acyclic graphs, by embedding each restriction into the global
  induced forest;
- their orders sum exactly to `|S|`.

Therefore Lean proves

```text
forestOrderExcluding G c
  <= forestOrderWithin G (L.erase c)
     + forestOrderWithin G (R.erase c).
```

This is the full restriction/upper half of the desired exclude-state formula.
It is a genuine separator theorem: the optimizing global forest is split,
localized to both sides, and compared with independently attained side
states.

## Why the reverse half remains

For equality, take optimizing forests on `L.erase c` and `R.erase c`, union
them, and prove their union is acyclic. Set-theoretic disjointness and
cardinality are straightforward. The missing graph lemma is:

```text
if A and B induce acyclic graphs
and no edge joins A to B,
then A union B induces an acyclic graph.
```

Mathematically this follows because a cycle is connected and must lie wholly
in one side. In the present Mathlib API, proving it requires walk-support or
cycle localization across an induced-subgraph embedding; no ready-made
acyclic disjoint-union theorem was found. Implementing that machinery safely
exceeded this lane's bounded scope.

The include-cut formula is harder still: the two side forests share `c`, the
union cardinality subtracts one, and cycle localization must show a simple
cycle cannot pass through the separator twice. It remains downstream of the
same walk-localization API.

Thus the exact formulas are not claimed prematurely. What is now proved is
the complete side-restriction direction and all finite optimization plumbing.

## Relation to v0.21 and feedback recursion

The v0.21 identity

```text
f(G)=max(includeState,excludeState)
```

remains the final exchange interface. This file supplies one of the four
directional state bounds needed by its statewise comparison theorem.

Once the separated-union acyclicity lemma is available, the exclude formula
will close immediately. The same cycle localization adapted to a shared
vertex will then provide the include formula. Together they permit composing
the v0.20 apex-forest unit with an arbitrary cyclic remainder.

## Verification

New file:

```text
lean/GraphConjecture40OneVertexSeparation.lean
```

After compiling the local import chain, the independent check was:

```text
timeout 60s env LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean \
  lake env lean -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture40OneVertexSeparation.lean
```

It exited `0` in 8.61 seconds with no output. The source contains no
`native_decide`, `sorry`, `admit`, or custom axiom. Every subprocess stayed
within the 60-second cap.

## Next step

Prove the standalone separated-union forest lemma using walks:

1. assume a cycle in the induced union;
2. map it to an ambient walk;
3. choose the side containing its base vertex;
4. show leaving that side creates a boundary dart crossing to the other side;
5. contradict the no-cross-edge hypothesis;
6. localize the cycle to one side and contradict that side's acyclicity.

That one lemma closes the reverse exclude inequality. A variant allowing the
shared cut vertex then closes the include state and the full one-sum formula.

Classification: **FORMAL ONE-VERTEX-SEPARATOR RESTRICTION THEOREM; no full
state equality, counterexample, release, or external claim.**
