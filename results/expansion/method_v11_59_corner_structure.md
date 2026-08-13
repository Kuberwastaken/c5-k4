# Method v0.11: WOWII 59 corner structure

Date: 2026-08-13

## Scope

This pass pursues—but does not claim—a universal exclusion of the only
low-residue corner left by method v0.9:

```text
(residue(G), b(G), f(G)) = (3,6,4).
```

WOWII 59 is already externally disproved. This is theorem extraction and
structural diagnosis, not counterexample discovery or priority work.

## Exact obstruction on a maximum bipartite witness

Suppose `S` is a six-vertex induced bipartite witness and `f(G)=4`. For every
`v in S`, the five-set `S - {v}` remains bipartite. It cannot be acyclic,
because that would be an induced forest of order five, contradicting `f=4`.

Therefore every hypothetical corner realization contains a six-vertex
bipartite induced subgraph with the deletion-critical property

```text
for every v in S,
  G[S - {v}] is bipartite and contains a cycle.
```

This is substantially sharper than the bare invariant triple. A single
five-vertex acyclic card destroys the corner.

The implication is now formalized without any finite computation. It is the
right combinatorial interface for a future classification theorem: classify
six-vertex bipartite graphs all of whose one-vertex deletions remain cyclic.

## Dense `K3,3`-like profiles

The complete six-vertex bipartite micro-audit in method v0.10 found exactly two
isomorphism classes with induced-forest number four:

- `K3,3`, descending degree profile `[3,3,3,3,3,3]`;
- `K3,3` minus one edge, profile `[3,3,3,3,2,2]`.

This pass formalizes their Havel--Hakimi calculations directly:

```text
residueAux [3,3,3,3,3,3] = 2,
residueAux [3,3,3,3,2,2] = 2.
```

Consequently any graph whose whole descending degree sequence is one of these
two profiles has residue exactly two and cannot realize the residue-three
corner.

The qualification “whole degree sequence” matters. A larger ambient graph may
contain a `K3,3`-like maximum induced bipartite witness while outside vertices
change the ambient degrees and Havel--Hakimi process. The result therefore
closes the dense six-vertex graph class, not all possible larger ambient
extensions.

## Formal artifact

[`lean/GraphConjecture59CornerStructure.lean`](../../lean/GraphConjecture59CornerStructure.lean)
proves:

1. monotonicity of induced bipartiteness under vertex-set restriction;
2. every deletion from a six-set is non-acyclic when `f=4`;
3. the combined bipartite-and-cyclic deletion obstruction;
4. exact residue two for the cubic six-vertex profile;
5. exact residue two for the one-edge-deficient profile;
6. exclusion of residue three for their union.

The degree-profile calculations use `native_decide` only after the graph-level
hypothesis has rewritten `residue` to a concrete six-term Havel--Hakimi list.
No graph property or invariant is delegated to native computation.

## Verification

With the warning-clean v0.8-v0.10 local dependencies compiled to temporary
`.olean` files, the new module was checked by

```text
LEAN_PATH=/tmp lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture59CornerStructure.lean
```

It completed in 6.5 seconds with no warnings or errors. The file contains no
`sorry`, `admit`, custom axiom, or imported upstream conjecture proof.

## Remaining universal bridge

A universal exclusion now has a precise two-stage target:

1. classify every six-vertex bipartite graph whose five-vertex deletion cards
   are all cyclic;
2. control how vertices outside that maximum bipartite witness affect the
   ambient Havel--Hakimi residue.

Stage one is strongly suggested by the exact enumeration to collapse to the
two `K3,3`-like graphs. Stage two is the genuinely global obstruction: maximal
induced bipartiteness constrains outside attachment patterns, but no proof yet
shows those attachments preserve the residue-two conclusion.

## Outcome

`EXACT_DELETION_OBSTRUCTION_PLUS_DENSE_CLASS_EXCLUSION`.

The pass does not universally exclude `(3,6,4)`. It replaces the unexplained
corner with a deletion-critical six-vertex structure and formally eliminates
the two dense whole-graph profiles observed by complete enumeration.
