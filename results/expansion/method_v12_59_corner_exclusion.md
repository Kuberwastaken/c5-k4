# Method v0.12: WOWII 59 ambient corner obstruction

Date: 2026-08-13

## Scope

This pass continues theorem extraction around the only low-residue corner left
by methods v0.9-v0.11:

```text
(residue(G), b(G), f(G)) = (3,6,4).
```

WOWII 59 is already externally disproved. No counterexample, novelty, or
held-out-success claim is made here.

## The ambient-extension problem

The v0.10 exact census found that a six-vertex bipartite graph with `f=4` is
isomorphic to `K3,3` or `K3,3` minus one edge, and both have residue two. That
does not settle a larger ambient graph: it may contain such a maximum induced
bipartite six-set while outside vertices change the ambient degree sequence and
Havel--Hakimi residue.

This pass proves the first universal constraint on those outside vertices.

Let `S` be an induced bipartite six-set with `b(G)=6`, and let `x` lie outside
`S`. Fix any valid two-coloring of `G[S]`.

If `x` has no neighbor in one color class, assign `x` that missing color. This
extends the coloring to `S union {x}`, producing an induced bipartite graph on
seven vertices. That contradicts `b(G)=6`.

Therefore:

```text
every outside vertex has a neighbor in each color class of every
valid two-coloring of G[S].
```

In particular, every outside vertex has at least two attachments into `S`.

This is stronger than a raw degree lower bound. It is a parity obstruction:
outside vertices must simultaneously see both sides of the bipartition, which
is exactly why they cannot be added to the bipartite witness.

## Combined corner structure

Together with v0.11, a hypothetical `(b,f)=(6,4)` witness now satisfies both:

1. every one-vertex deletion from `S` is cyclic;
2. every outside vertex attaches to both colors of `S`.

Thus a universal exclusion can now focus on ambient extensions of the two
deletion-critical `K3,3`-like cores whose outside vertices are forced to have
mixed-parity attachment patterns. Attachments of size zero or one, or confined
to one color class, are formally impossible.

## Formal artifact

[`lean/GraphConjecture59CornerExclusion.lean`](../../lean/GraphConjecture59CornerExclusion.lean)
proves:

1. an explicit coloring-extension theorem for a compatible new color;
2. existence of such a color when an outside vertex has at most one
   attachment;
3. preservation of induced bipartiteness after inserting that vertex;
4. the universal lower bound of two attachments for every outside vertex of a
   maximum bipartite six-set;
5. the stronger theorem that both colors occur among those attachments;
6. a combined interface joining this ambient constraint with the v0.11
   deletion-cyclic obstruction.

These are graph-level theorems. No search result or finite computation is used
inside their proofs.

## Verification

After compiling the warning-clean v0.8-v0.11 dependencies into temporary
`.olean` files, the new module was checked with

```text
LEAN_PATH=/tmp lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture59CornerExclusion.lean
```

It completed in 6.2 seconds with no warnings or errors. The file contains no
`sorry`, `admit`, custom axiom, native decision procedure, or imported upstream
conjecture proof.

## Remaining bridge

Universal exclusion is not yet proved. The remaining task is sharply reduced:

- classify the six-vertex deletion-critical bipartite core internally; then
- show that every mixed-parity ambient attachment pattern either creates a
  seven-vertex induced bipartite graph after a compensating deletion, creates
  a five-vertex induced forest, or forces ambient Havel--Hakimi residue at most
  two.

The natural next move is one-for-one exchange: add an outside vertex and delete
one carefully chosen core vertex. Maximality says every such seven-to-six swap
must still encounter an odd cycle; `f=4` says every five-vertex retained set
must still encounter a cycle. Their simultaneous parity constraints should be
much tighter than either condition alone.

## Outcome

`UNIVERSAL_AMBIENT_ATTACHMENT_OBSTRUCTION`.

This does not close the exact corner universally. It eliminates all sparse and
single-color ambient extensions and leaves only mixed-parity attachments to a
deletion-critical `K3,3`-like core.
