# Method v0.20: WOWII 133 shared-third blockers

Date: 2026-08-13

Local certificate: `lean/GraphConjecture133SharedThirdBlockers.lean`

## Control-guided selection

The projective-plane control realizes the sharp cross-branch overlap from
v0.19: every one of its nine distinct third vertices belongs to three
different `(c,b)` parent pairs.  For a representative radius geodesic, for
example, one shared vertex has parent pairs

```text
(17,1), (20,12), (23,9).
```

Most shared vertices have no early contact.  A representative shared vertex
that does contact the radius geodesic meets only index two; it is still a
clean candidate for other parent pairs because the relevant early-cleanliness
conditions depend on the chosen branch.  This confirms that multiplicity
three and an early contact can coexist.  A theorem excluding all shared
blockers would therefore be false.

The Lean results below capture the sharp coexistence restrictions that hold
without overclaiming an elimination.

## Cross-parent/first non-incidence

Suppose one third vertex `a` is shared by parent pairs

```text
c₁ -- b₁ -- a -- b₂ -- c₂.
```

C4-freeness forces

```text
b₁ not adjacent c₂,
b₂ not adjacent c₁.
```

Otherwise either side closes a four-cycle through `a`.  The theorem
`sharedThird_forbids_cross_parent_first` proves both exclusions with all six
distinctness obligations explicit.

## Blocker/parent non-incidence

If the same shared vertex `a` blocks early target `x`, triangle-freeness
forces

```text
b₁ not adjacent x,
b₂ not adjacent x.
```

This is `sharedThird_blocker_forbids_parent_target`.  Thus a blocker edge
owned by a multiply represented third vertex excludes that target from every
one of its second parents.

For the special target `x₀=u`,
`sharedThird_endpoint_blocker_signature` packages the full signature:

```text
b₁ !~ u,  b₂ !~ u,
b₁ !~ c₂,  b₂ !~ c₁.
```

## Exact remaining configurations

These restrictions do not eliminate one of the ten singleton target triples
at the level of a fixed parent `b`.  They instead constrain how that pattern
can be repeated across branches:

1. a third vertex may occur in multiple branches;
2. it may have one early target contact, as the control demonstrates;
3. none of its multiple second parents may contact that target;
4. no second parent may contact an opposite first choice;
5. the shared vertex itself has only four incident edges, so multiplicity
   three plus one blocker contact exhausts its degree.

The last point is the key next constraint.  In a four-regular graph, a
multiplicity-three shared blocker has exactly the three parent edges and its
single blocker edge--no residual adjacency.  Conversely, multiplicity two
leaves one residual edge after blocking.  A global capacity proof should
partition third vertices by multiplicity `1,2,3`, charge blocker edges once
rather than once per parent-pair incidence, and use these saturated
multiplicity-three vertices to control overlap.

The current exact survivor statement is therefore: all ten target triples
remain locally possible, but any cross-branch realization must satisfy the
parent/target and parent/opposite-first non-incidence signature above.

## Lean audit

The module is self-contained over `FormalConjecturesUtil`; it uses no native
computation, proof holes, or custom axioms.  It was checked with warnings
promoted to errors:

```text
timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133SharedThirdBlockers.lean
```

Result: exit code 0 in 8.1 seconds.

This is a sharp coexistence theorem and calibrated non-elimination result,
not unrestricted handle existence or a counterexample release candidate.
