# Method v24: WOWII #59 path-branch core exchange

Date: 2026-08-13

Local certificate: `lean/GraphConjecture59PathBranch.lean`

## Construction

For a path on the outside triple, delete its center and delete aligned core
`b`. Keep aligned core `a`, the two nonadjacent path endpoints, and both v21
extension vertices `p,q`.

The resulting five-set has the bipartition

```text
left:  path endpoint, path endpoint, p
right: a, q.
```

The left side is independent from the path endpoint nonedge and v21
compatibility. The right side is independent because `q!~a`.

## Missing condition and forest exit

To make this bipartite incidence graph a forest, the proof asks that every
left vertex have at most one neighbor on the right. Since both endpoints see
aligned core `a`, it is enough to require

```text
q avoids all three outside vertices,
p avoids a or p avoids q.
```

Under these additional nonedges, Lean constructs the induced forest directly
and proves

```text
f(G) >= 5.
```

The theorem covers all three labeled realizations of the path type.

## Smallest explicit obstruction

The v21 data alone do not control edges from `q` to the path endpoints. If
`q` sees both retained endpoints, then

```text
a - endpoint1 - q - endpoint2 - a
```

is a four-cycle inside the proposed five-set. Lean constructs this walk and
proves that the exchanged candidate is not acyclic. This is the first exact
adjacency counterconfiguration to the forest construction.

The sufficient condition above also prevents a second possible double
neighbor: `p` seeing both `a` and `q`.

## Scope

The local v21 hypotheses alone are insufficient for this forest exit; the
new nonedges are stated explicitly rather than inferred. WOWII #59 is already
externally disproved. This is theorem extraction, not a new counterexample.

## Lean audit

The complete dependency chain from `GraphConjecture40Baseline` through the
v23 one-edge branch was rebuilt into a fresh temporary directory with warnings
promoted to errors and every process capped at 60 seconds. The separate v19
synchronization branch was rebuilt as well. Every module passed. The final
target check completed in 10.78 seconds with exit code zero and no warnings.
The file contains no proof holes, native computation, or custom axioms.

## Next bridge

Use exchange resistance to force one of the new compatibility conditions, or
show that repeated failure—two endpoint neighbors of `q`, or simultaneous
`p-a` and `p-q` edges—creates a different induced forest after exchanging the
remaining aligned core.
