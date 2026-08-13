# WOWII 40 v0.21: corrected cut-vertex include/exclude states

**Date:** 2026-08-13

**Outcome:** the unconditional additive cut formula is replaced by a formally
proved max-of-states identity. Both include-cut and exclude-cut optima are
attained, and statewise exchange bounds imply equality of maximum induced-
forest orders.

**Read-only upstream snapshot:** `formal-conjectures`
`9a1636c4030039f70cf78b866c216d8b6c5f35b0`

## Why raw additivity is false

Even the smallest one-vertex sum rejects the formula

```text
f(G1 ∨c G2) = f(G1) + f(G2).
```

Take two edges and identify one endpoint. Each side is an edge with forest
order two, while the union is the three-vertex path with forest order three,
not four. The shared cut was counted twice.

Subtracting one is still not a universal state-free derivation method for
arbitrary cyclic sides: an optimizing forest on one side may need the cut
while the optimum on the other side may exclude it. Composition must record
which state is used before combining the two optima.

The corrected universal formula therefore distinguishes include and exclude
states rather than asserting an unqualified side sum.

## Stateful optimizations

For a graph `G` and selected cut vertex `c`, the new file defines

```text
forestOrderIncluding G c =
  max {|S| : G[S] is acyclic and c in S},

forestOrderExcluding G c =
  max {|S| : G[S] is acyclic and c notin S}.
```

Both are encoded as finite natural-number `sSup` values. The development
proves attainment for each state:

- `{c}` supplies a nonempty including family;
- the empty set supplies a nonempty excluding family;
- ambient graph order bounds both families;
- `Nat.sSup_mem` supplies optimizing finsets.

It also proves comparison lemmas saying every explicit induced forest is
bounded by the corresponding state.

## Correct universal max-of-states formula

The central theorem is

```text
largestInducedForestSize G =
  max (forestOrderIncluding G c)
      (forestOrderExcluding G c).
```

For the upper bound, take the attained global maximum and split on whether it
contains `c`. For the lower bound, take the attained witness in each state and
compare it with the global induced-forest invariant.

This identity is valid for every finite graph and every selected vertex; it
does not need a cut-vertex or separation hypothesis.

## One composition/exchange theorem

The file proves the corrected stateful composition interface:

```text
includeState(G,c) = includeState(H,c)
and excludeState(G,c) = excludeState(H,c)
  -> f(G)=f(H).
```

A second form accepts four directional bounds—extension and restriction for
each state—and derives equality by antisymmetry before applying the
max-of-states formula.

This is the exchange theorem needed for an apex-forest leaf cluster attached
to an arbitrary cyclic remainder. A future separator proof may handle the
two states independently:

- **include-cut:** glue forests containing the cut and subtract its duplicated
  contribution;
- **exclude-cut:** glue forests avoiding the cut, where the sides are vertex-
  disjoint after removal.

Once both extension/restriction pairs are proved for the concrete separator,
the formal theorem here converts them immediately into the forest equality
required by v0.19.

## What remains unproved

This file does not yet formalize a graph gluing constructor or prove a closed
arithmetic formula for a particular one-vertex sum. Mathlib's induced graph
API does not expose a ready-made finite one-sum decomposition, and proving
that every cycle in the union lies within one side requires substantial walk
or cycle localization machinery.

Accordingly, the result is the strongest unconditional and fully verified
state formula, plus the exact statewise comparison theorem consuming future
separator arguments. It does not label a conditional side-additivity premise
as a proved graph theorem.

The terminal apex-forest result from v0.20 is recovered conceptually when the
remainder is acyclic: both states can be bounded directly by ambient order.
For an arbitrary cyclic remainder, the state split identifies precisely the
new work rather than hiding it inside an assumed equality.

## Verification

New file:

```text
lean/GraphConjecture40CutVertexSum.lean
```

After compiling the local import chain, the independent check was:

```text
timeout 60s env LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean \
  lake env lean -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture40CutVertexSum.lean
```

It exited `0` in 6.90 seconds with no output. The source contains no
`native_decide`, `sorry`, `admit`, or custom axiom. Every subprocess stayed
within the 60-second cap.

## Next step

Define an explicit one-vertex-separation predicate using vertex subsets
`L,R` with:

```text
L union R = univ,
L intersection R = {c},
no edges between L-{c} and R-{c}.
```

Then prove cycle localization and the two state formulas. The expected
arithmetic has the shape

```text
include = includeLeft + includeRight - 1,
exclude = excludeLeft + excludeRight,
global = max include exclude.
```

The present file certifies the last equality and the exchange endpoint. The
remaining hard lemma is cycle localization across the separator.

Classification: **FORMAL CUT-STATE OPTIMIZATION AND EXCHANGE INTERFACE;
no full one-sum localization theorem, counterexample, release, or external
claim.**
