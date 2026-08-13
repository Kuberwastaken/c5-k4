# Method v22: WOWII #59 independent-branch exit

Date: 2026-08-13

Local certificate: `lean/GraphConjecture59IndependentBranch.lean`

## Outcome

This rung connects the v20 four-way outside-triple classification to the v21
seven-vertex witness builder.

For an aligned outside triple `x,y,z`, two nonadjacent aligned cores `a,b`,
and compatible extension vertices `p,q`, Lean now proves the disjunction

```text
b(G) >= 7
or
the outside triple has type one-edge, path, or triangle.
```

The independent case is discharged constructively: v21 colors

```text
color 0: a,b,q
color 1: x,y,z,p
```

and obtains an induced bipartite seven-set. No lower bound on `b(G)` is used
as a hypothesis.

## Low-corner consequence

The complementary theorem assumes only the low-corner inequality `b(G)<7`.
Under the same local alignment, distinctness, nonedge, and compatibility data,
it proves

```text
x~y or x~z or y~z.
```

Thus the independent outside-triple branch is eliminated outright in that
corner. The remaining graph analysis can focus on the one-edge, path, and
triangle types, each of which contains a certified outside edge.

## Scope

The result is conditional on the two compatible extension vertices already
isolated in v21. It does not claim that every aligned triple supplies those
vertices, and it does not discharge the three edge-containing branches.
This is theorem extraction around WOWII #59, which is already externally
disproved, not a new counterexample.

## Lean audit

The complete local dependency chain from `GraphConjecture40Baseline` through
v21 and this module was rebuilt into a fresh temporary directory, with
warnings promoted to errors and every Lean process capped at 60 seconds. All
16 modules passed. An isolated recheck of this target completed in 6.08
seconds with exit code zero and no warnings. The file contains no proof holes,
native computation, or custom axioms.

## Next bridge

Use the forced outside edge in the low corner. For the one-edge branch, the
isolated third outside vertex is the natural candidate for a forest extension;
for the path and triangle branches, a core exchange or deletion should seek a
five-vertex induced forest instead of extending the fixed bipartite coloring.
