# WOWII 40 v0.20: structural apex-forest feedback unit

**Date:** 2026-08-13

**Outcome:** cyclicity plus acyclicity after deleting a selected vertex is
formally proved to imply the forest equality required by v0.19. The selected
vertex is therefore exactly one feedback unit, with no `hforest` assumption.

**Read-only upstream snapshot:** `formal-conjectures`
`9a1636c4030039f70cf78b866c216d8b6c5f35b0`

## Structural class

For a finite graph `G` and selected vertex `v`, assume

```text
G is not acyclic,
deleteVertex G v is acyclic.
```

This is an apex-forest feedback unit. It includes a nontrivial shared-center
cactus cluster when the selected cut vertex hits every cycle, as well as any
graph whose entire cyclic obstruction is killed by one vertex.

The hypotheses are purely structural. They mention neither maximum induced
forest cardinalities nor feedback deletion.

## New finite optimization API

The file first proves that the finite `sSup` defining
`largestInducedForestSize` is attained:

```text
exists S,
  (G.induce S).IsAcyclic
  and S.card = largestInducedForestSize G.
```

This closes an API gap noted in the original #40 proof ladder. The proof uses
`Nat.sSup_mem`, the empty induced forest for nonemptiness, and ambient graph
order for boundedness.

## Cyclic graphs lose a vertex

Using the attained witness, the development proves

```text
not G.IsAcyclic
  -> largestInducedForestSize G < n.
```

If equality with `n` held, the optimizing finset would have full ambient
cardinality and therefore equal `univ`. Its acyclicity would transport across
the canonical induced-universe graph isomorphism and make `G` acyclic, a
contradiction.

## Forest equality from structure

Since `G-v` is acyclic,

```text
f(G-v) = n-1.
```

Since `G` is cyclic,

```text
f(G) <= n-1.
```

For the reverse inequality, the file takes all vertices other than `v` as an
explicit induced forest of `G`. This set has order `n-1`, because it is exactly
the vertex set of the acyclic deleted graph. Hence

```text
f(G-v) <= f(G).
```

Combining the bounds proves the v0.19 criterion directly:

```text
f(G) = f(G-v).
```

The exact feedback consequence is then derived through the already-formal
recurrence:

```text
feedbackDeletion G = 1,
feedbackDeletion (G-v) = 0.
```

## Terminal recursive #40 step

The final theorem combines these structural facts with one allocated leaf
path. Its assumptions are:

- `G` is bipartite;
- `G` is cyclic but `G-v` is acyclic;
- a remainder path family has rank at least one, the `k=0` certificate;
- a disjoint leaf-block path of order at least three is available.

The file automatically proves forest equality and zero remainder feedback,
then invokes the v0.19 complete recursion step. WOWII 40 follows in the exact
upstream ceiling form.

This is a real terminal decomposition step: neither `tau(G)=1` nor forest
equality is assumed.

## Why the theorem stops at an acyclic remainder

A tempting broader statement would replace “`G-v` is acyclic” by “the
selected cyclic cluster is separated from an arbitrary remainder.” That
requires an additivity or exchange theorem for induced-forest order across the
separator. Merely naming a separated cluster does not determine whether
maximum forests on both sides can simultaneously include the cut vertex.

The present theorem chooses the strongest clean case where both upper and
lower bounds can be proved from existing graph APIs. No universal arbitrary-
remainder claim is made, so no artificial decomposition hypothesis is hidden
inside a wrapper.

The shared-center warning remains important: deleting a non-center vertex
from two `C4` petals sharing a center does not reduce feedback deletion. The
apex-forest theorem selects the actual center; deleting it makes the remainder
acyclic and the structural proof applies.

`EQKo` is unaffected. The theorem derives feedback recursion from induced-
forest extrema and supplies rank through an explicit disjoint path; it does
not assert the false pointwise linear-forest insertion rule.

## Verification

New file:

```text
lean/GraphConjecture40CactusFeedbackUnit.lean
```

After compiling the local import chain, the independent check was:

```text
timeout 60s env LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean \
  lake env lean -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture40CactusFeedbackUnit.lean
```

It exited `0` in 6.37 seconds with no output. The source contains no
`native_decide`, `sorry`, `admit`, or custom axiom. Every subprocess stayed
within the 60-second cap.

## Next boundary

To iterate over an arbitrary cactus block tree, the next theorem must prove a
separator formula or exchange principle for `f`. A useful target is a
one-vertex sum theorem distinguishing whether a maximum induced forest on
each side includes the shared cut vertex. Such a formula would let an
apex-forest leaf cluster be removed while a cyclic remainder survives, and
would reduce forest equality to explicit inclusion-state arithmetic.

The terminal structural unit is now complete. The hard remaining content is
composition of feedback units across a cut vertex.

Classification: **FORMAL STRUCTURAL FEEDBACK UNIT AND TERMINAL RECURSION;
no full proof, counterexample, release, or external claim.**
