# Method v0.21: WOWII 133 multiplicity charging

Date: 2026-08-13

Local certificate: `lean/GraphConjecture133MultiplicityCharge.lean`

## Aggregate model

Across the three first-choice branches there are 27 third-layer incidences.
Let `n₁,n₂,n₃` count distinct third vertices occurring with multiplicity
one, two, and three.  Then

```text
n₁ + 2 n₂ + 3 n₃ = 27.
```

If every distinct third vertex is blocked, v0.17 gives one blocker edge per
vertex.  The five early targets provide at most eleven outside slots, so

```text
n₁ + n₂ + n₃ <= 11.
```

Lean proves immediately that these equations force

```text
n₃ >= 5.
```

Thus any global obstruction is dominated by vertices shared across all three
branches.  This is a genuine reduction: low-overlap configurations cannot
consume only eleven blocker slots.

## Exact compatible profiles

The two equations have exactly seven nonnegative integer profiles:

```text
(n₁,n₂,n₃) =
(0,0,9), (0,3,7), (0,6,5),
(1,1,8), (1,4,6),
(2,2,7), (3,0,8).
```

`capacity_profile_classification` proves this list in Lean.  Two useful
boundary consequences are also certified:

- eleven distinct vertices and no singletons force `(0,6,5)`;
- nine distinct vertices force `(0,0,9)`.

The second is exactly the incidence profile realized by the `PG(2,3)` control
before blocker contacts are imposed.

## Exact abstract countermodel

Aggregate charging does not force a clean candidate.  The profile

```text
(0,0,9)
```

accounts for all 27 parent incidences with nine multiplicity-three vertices
and uses only nine of the eleven blocker slots.  Lean certifies this as
`abstract_charge_countermodel`.

This is not a graph counterexample: the projective-plane control realizes the
multiplicity profile but its vertices are not all blocked.  It is an exact
integer incidence countermodel to the proposed aggregate proof.

## Degree-four saturation

Every multiplicity-three blocked vertex uses:

```text
3 parent edges + 1 blocker edge = degree 4.
```

It is saturated.  Since every abstract obstruction has at least five such
vertices, a successful graph proof may assume a large saturated core.  The
v0.20 coexistence theorem additionally says none of the three parents may
contact that vertex's blocker target.

However, saturation alone does not contradict the seven profiles.  It says
where all incident edges go, not that the resulting parent/blocker incidence
graph cannot exist.

## Missing extra constraint

The aggregate model discards which first branch owns each parent edge and
which target owns each blocker edge.  The next independent constraint must
retain that bipartite coloring:

1. every multiplicity-three vertex has exactly one parent in each of the
   three first-choice branches;
2. its blocker target is forbidden from all three parents by v0.20;
3. each target has residual capacity two or three;
4. each branch contains three disjoint second parents, each supporting three
   third incidences.

This is a small colored incidence problem, rather than another scalar count.
The natural next step is exact enumeration of the seven profiles with branch
labels and target capacities, adding the v0.20 parent-target non-incidence
rule.  If that still has models, the model itself will specify the final
missing adjacency constraint.

## Lean audit

The module uses no native computation, proof holes, or custom axioms.  It was
checked with warnings promoted to errors:

```text
timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133MultiplicityCharge.lean
```

Result: exit code 0.

This is an exact aggregate classification and integer countermodel, not
unrestricted handle existence or a graph counterexample release.
