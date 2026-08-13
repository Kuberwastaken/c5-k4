# Method v0.13: WOWII 133 early-escape combinatorics

Date: 2026-08-13

Local certificate: `lean/GraphConjecture133EarlyEscapeCombinatorics.lean`

## Exact bounded controls

The v0.12 controls were re-evaluated at the finer early-contact level.  The
enumeration covered every oriented radius geodesic, every clean first vertex
`c`, every depth-two choice `b` avoiding geodesic indices `1..3`, and every
depth-three choice `a` avoiding indices `0..4`.

| graph | radius geodesics | clean `c` | valid `b` | valid `a` | valid `b` with no `a` |
|---|---:|---:|---:|---:|---:|
| incidence graph of `PG(2,3)` | 936 | 2,808 | 5,616 | 11,232 | 0 |
| `Kneser(7,3)` | 1,260 | 3,780 | 10,080 | 22,680 | 0 |

Thus every valid depth-two continuation in both independent controls extends
to at least one valid depth-three handle.  No early-contact obstruction was
found.  These exhaustive counts are graph-specific and are not imported into
Lean.

## The depth-two existence theorem

The first finite existence layer is now closed in full generality.

Fix a vertex `c`, remove one distinguished neighbor `u`, and call the three
remaining neighbors the forward set.  For any vertex `x != c`, at most one
member of that set can be adjacent to `x`: two such members `a,b` would form

```text
c -- a -- x -- b -- c.
```

This is a not-necessarily-induced four-cycle.  Lean proves the exact cardinal
bound as `card_common_forward_neighbors_le_one`.

For a four-regular graph the forward set has cardinality three.  Two target
vertices can therefore forbid at most two forward vertices.  The theorem
`exists_forward_neighbor_avoiding_two_targets` proves that some forward
neighbor avoids both targets, using explicit finite-set cardinal arithmetic.

## Geodesic consequence

At a clean first handle vertex `c`, choose the two targets to be geodesic
vertices `x₂` and `x₃`.  The counting theorem supplies a neighbor `b`
avoiding both.  Its possible contact with `x₁` is automatically impossible:

```text
u -- c -- b -- x₁ -- u
```

would be a C4.  Hence `exists_depthTwo_avoiding_first_three` proves that a
valid `b` always exists whenever the radius geodesic has length at least
three.

Combined with v0.12's shortcut lemma, this means the entire depth-two stage is
settled: indices `1..3` are avoided by counting and C4-freeness, while indices
`>=4` are excluded by geodesic shortestness.

## Smallest remaining obstruction

Only the depth-three choice `a` remains.  Once `b` is fixed, it has three
forward neighbors other than `c`.  The potentially blocking geodesic targets
are indices `0..4`.  C4-freeness again says each individual target can block
at most one forward neighbor, but five singleton blocking sets can cover a
three-element forward set.  The depth-two pigeonhole argument therefore does
not iterate unchanged.

The smallest possible obstruction is consequently a three-way covering:
each forward neighbor of every admissible `b` is assigned at least one early
contact among `x₀,...,x₄`.  The bounded controls contain no such covering,
but local cardinality alone does not rule it out.  The next proof must exploit
relations among those contacts--for example, pairs of nearby geodesic targets
that cannot block different forward neighbors without creating a C4 or a
shorter path.

## Lean audit

The module uses no native computation, proof holes, or custom axioms.  It was
checked with local dependencies and warnings promoted to errors:

```text
LEAN_PATH=/tmp/c5k4-133-early-comb:/tmp/c5k4-133-handle-existence:\
/tmp/c5k4-133-deep-handle:/tmp/c5k4-133-degree-four:\
/tmp/c5k4-133-regular:/tmp/c5k4-133-specialization:/tmp/c5k4-133-v07-check \
  timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133EarlyEscapeCombinatorics.lean
```

Result: exit code 0 in 7.1 seconds.

This is a general counting theorem and structural reduction, not a proof of
the unrestricted degree-four case and not a counterexample release.
