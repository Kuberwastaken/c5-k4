# Method v27: WOWII #59 cyclic-card rectangle bridge

Date: 2026-08-13

Local certificate: `lean/GraphConjecture59CyclicCardRectangle.lean`

## Outcome

The v26 exact profile classifier used the coordinate statement that every
five-vertex deletion of a `3+3` core retains a `K2,2` rectangle.  The earlier
`CornerStructure` theorem supplied Mathlib's abstract statement that every
such deletion is cyclic.  This checkpoint closes the graph-theoretic gap
between those formulations.

Lean now proves:

```text
bipartite + order five + cyclic
  ==> an explicit four-cycle
  ==> two vertices with two distinct common neighbors in the opposite side.
```

The first implication is not an exhaustive graph computation.  For a
Mathlib cycle `p`:

- the tail is a path, so `length(p) <= 5`;
- every cycle has length at least three;
- every closed walk in a two-colorable graph has even length; therefore
- `length(p)=4`.

Four consecutive `getVert` values then give a pairwise-distinct four-cycle.
The fixed `IsBipartiteWith I X` partition forces these vertices to alternate,
yielding the required rectangle.

## Composition with the `f=4` corner

`corner_deletion_contains_rectangle` consumes the existing theorem
`every_single_deletion_bipartite_and_cyclic` directly.  For every vertex `z`
of a bipartite six-core `S`, if the global induced-forest number is four, Lean
produces four distinct vertices of `S.erase z` with all four cross-edges:

```text
a-c, a-d, b-c, b-d.
```

Thus the v26 deletion-critical matrix premise is no longer justified by an
informal claim about cycles: it has an end-to-end Mathlib graph certificate
from the actual `f(G)=4` hypothesis.

After labeling the two three-vertex core color classes by `Fin 3`, these six
deletion rectangles are exactly `DeletionCritical m`.  The already certified
v26 theorem then gives

```text
edgeCount = 8 or 9,
internal degree profile = [3,3,3,3,2,2] or [3,3,3,3,3,3].
```

The generic finite-set theorem and the coordinate classifier are both Lean
certified.  Their final composition still requires routine relabeling data
(bijections from the two color classes to `Fin 3`); this module does not hide
that transport behind an unstated identification.

## Next use

The remaining mathematical step is no longer cycle classification.  It is to
combine the four-or-six saturated internal core degrees with the dense outside
rows already established in v14--v20.  That should force a multi-entry prefix
of the global descending degree sequence, the kind of residue input that the
v25 scalar countermodels cannot imitate.

## Lean audit

The new module was rebuilt against a fresh local copy of the v26 dependency
using the repository-pinned Lean 4.27 toolchain, a 60-second cap, and warnings
as errors:

```text
ELAN_TOOLCHAIN=leanprover/lean4:v4.27.0 \
LEAN_PATH=/tmp/c5k4-59-v27-audit.Q5a01Z:/tmp/c5k4-59-v26-fast.FgYBev:/tmp \
timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  -o /tmp/c5k4-59-v27-audit.Q5a01Z/GraphConjecture59CyclicCardRectangle.olean \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture59CyclicCardRectangle.lean
```

Result: exit code 0 in 7.0 seconds.  The certificate uses no native
computation, proof holes, or custom axioms.

WOWII #59 is already externally disproved; this is theorem extraction, not a
new counterexample or release candidate.
