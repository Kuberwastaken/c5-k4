# WOWII 40 v0.19: exact feedback recursion under vertex deletion

**Date:** 2026-08-13

**Outcome:** a no-`sorry` theorem characterizes exactly when deleting a
selected vertex lowers feedback deletion by one, and combines that decrement
with the v0.18 leaf-path rank step into one complete induction move.

**Read-only upstream snapshot:** `formal-conjectures`
`9a1636c4030039f70cf78b866c216d8b6c5f35b0`

## Vertex deletion and order

The new file defines

```text
deleteVertex G v = G.induce {x | x != v}.
```

It proves directly from finite subtype cardinalities that

```text
|V(deleteVertex G v)| + 1 = |V(G)|.
```

This is the ambient-order identity needed to compare the complementary
feedback coordinate `tau=n-f` on both sides.

## Exact feedback-decrement criterion

The central equivalence is

```text
feedbackDeletion G = feedbackDeletion (G-v) + 1
  <->
largestInducedForestSize G =
  largestInducedForestSize (G-v).
```

Both directions are formalized. The proof uses only:

- the exact one-vertex order difference;
- the definition `feedbackDeletion=n-f`;
- the already-proved upper bounds `f(G)<=n(G)` on both graphs.

Conceptually, restoring `v` adds one ambient vertex. It raises `tau` exactly
when it adds no vertex to the maximum induced-forest order. Thus an
independent selected feedback step is certified by forest equality, not by a
false pointwise linear-forest gain.

## Corrected general recursion

Under the standard induced-forest comparisons

```text
f(G-v) <= f(G) <= f(G-v)+1,
```

the file proves the dichotomy

```text
tau(G)=tau(G-v) or tau(G)=tau(G-v)+1.
```

This is the strongest true one-vertex statement. Equality with the successor
cannot be asserted for every vertex.

## Minimal exact counterconfiguration to universal equality

Take two 4-cycles sharing exactly one center vertex. This connected bipartite
graph has seven vertices and feedback deletion one: deleting the shared
center destroys both cycles.

Now delete a non-center vertex from only one petal. The other 4-cycle remains,
so the vertex-deleted graph still has feedback deletion one. Therefore

```text
tau(G) = tau(G-v),
```

not `tau(G-v)+1`. In forest coordinates, `f(G)=6` and `f(G-v)=5`: restoring
that non-center vertex increases the maximum forest order by one.

Deleting the shared center behaves differently: the remainder is acyclic,
so the feedback coordinate drops from one to zero and the forest orders are
equal at six. This illustrates why shared-cut clusters must select the actual
feedback vertex rather than charge arbitrary cyclic-block vertices.

The seven-vertex two-`C4` shared-center flower is the smallest exact
configuration used here; no global minimality claim across all connected
bipartite graphs is needed for the correction.

## One complete induction step

The endpoint theorem assumes:

1. `G` is bipartite;
2. the remainder `G-v` has feedback coordinate `k`;
3. restoring `v` does not increase maximum forest order, hence `tau(G)=k+1`;
4. a path family `P` already certifies rank `2k+1`;
5. an allocated disjoint leaf path of order at least three is available.

The new feedback theorem derives `tau(G)=k+1`. The v0.18 `rank_step` inserts
the leaf path and raises the family certificate to `2(k+1)+1`. The v0.13
deficiency transfer then proves WOWII 40 in the exact upstream ceiling form.

This is the first result in the #40 ladder that couples an actual
vertex-deletion feedback recurrence to the recursive path-family mutation.

## Honest remaining boundary

The forest equality in the selected step is a mathematically exact criterion,
but this file does not prove it automatically from an arbitrary block label.
For a cactus/block-tree proof, one must choose a feedback vertex or block
cluster so that:

- the remainder feedback number is known;
- restoring the selected vertex creates one genuinely independent cycle
  obstruction;
- a leaf path disjoint from the remainder certificate is harvested.

Shared-center clusters show selection matters. The block theorem must group
all cycles paid by one cut vertex and recurse on feedback units, not on raw
cycle count.

`EQKo` remains compatible: this development reasons through forest-order
recursion and an explicit path insertion; it does not resurrect the false
claim that a feedback-number change forces a pointwise linear-forest gain.

## Verification

New file:

```text
lean/GraphConjecture40FeedbackRecursion.lean
```

After compiling the local import chain, the independent check was:

```text
timeout 60s env LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean \
  lake env lean -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture40FeedbackRecursion.lean
```

It exited `0` in 6.71 seconds with no output. The source contains no
`native_decide`, `sorry`, `admit`, or custom axiom. Every subprocess stayed
within the 60-second cap.

## Next step

The next substantive theorem should prove forest equality for a selected
independent cactus leaf or shared-cut cluster from explicit separation
hypotheses. A useful formulation would state that:

- the selected vertex is the sole interface between a cyclic cluster and the
  remainder;
- the cluster becomes acyclic after deleting it;
- every induced forest of the full graph must lose either that vertex or one
  cluster vertex;
- a maximum remainder forest extends through the trimmed cluster without
  increasing the full maximum beyond the required equality.

That would discharge the exact criterion proved here and permit true
iteration over selected feedback units.

Classification: **FORMAL FEEDBACK-DELETION RECURSION AND COMPLETE ONE-STEP
TRANSFER; no full proof, counterexample, release, or external claim.**
