# Method v0.28: WOWII 133 endpoint-capacity collapse

## Outcome

The strongest remaining aggregate profile,

```text
(n₁,n₂,n₃) = (3,0,8),
```

is eliminated once target index zero is correctly typed as the common
endpoint.  More strongly, the same argument eliminates all six profiles left
after v0.27 at the aggregate blocker level.

The decisive correction is:

```text
endpoint blocker capacity for genuine third choices = 0,
not 3.
```

The numerical degree calculation at target zero still gives three outside
neighbors, but those neighbors are the first choices themselves.  A genuine
third choice cannot be one of those neighbors in a C4-free realization of its
branch.

Lean certificate:

- `lean/GraphConjecture133EndpointCapacityCollapse.lean`.

This closes the finite multiplicity/capacity obstruction.  It does not by
itself splice that obstruction back into the full induced-path construction
for WOWII 133; that graph-to-accounting bridge is now the remaining theorem
engineering step.

## Endpoint exclusion

For a genuine third choice the local branch is

```text
u -- c -- p -- z,
```

with

```text
p != u,
z != c.
```

Both inequalities come directly from the two successive `Finset.erase`
choice constructions.  If `z` were adjacent to endpoint `u`, then

```text
u -- c -- p -- z -- u
```

would be a C4 on four distinct vertices.  Lean proves

```text
third_choice_not_adj_endpoint.
```

Unlike v0.27, this theorem does not first force `z=c`; it uses the genuine
third-choice freshness immediately and rules out the endpoint contact.

Therefore target zero contributes no blocker edge to an obstruction in which
every listed object is genuinely a third choice.

## Overlap control

The multiplicity cap still needs the branch geometry:

- `same_branch_parents_cannot_share_third` proves that two distinct second
  parents below one first choice cannot own the same genuine third;
- `distinct_parents_common_neighbors_le_one` proves the cross-parent C4 bound
  that two distinct parents have at most one common neighbor.

There are three branches, and within each branch a third appears below at
most one parent.  Hence a distinct third has multiplicity at most three.
For 27 parent-third incidences this yields

```text
distinct thirds >= 9.
```

The scalar version is `nine_le_distinct_thirds`.

## Degree completion

`neighborFinset_eq_four_known` and
`first_choice_neighborhood_exhausted` certify the complementary saturation
fact:

```text
N(c) = {u,p₀,p₁,p₂}
```

for a first choice `c` and its three second choices.

Thus the endpoint's three outside neighbors cannot silently accept additional
parent-third roles through unused degree.  The direct C4 lemma already gives
the sharp endpoint exclusion, while degree completion confirms that there is
no degree-level escape from the typed first-choice structure.

## Internal blocker budget

Targets one through four are internal vertices of the selected geodesic.
Each has two outside-neighbor slots.  Lean proves the aggregate bound

```text
m₁ + m₂ + m₃ + m₄ <= 8
```

as `internal_target_capacity_le_eight`.

Every distinct third in the obstruction requires at least one blocker edge.
After endpoint contacts are excluded, those blocker edges must all land in
the four internal target fibers.  The lower and upper bounds are therefore

```text
distinct thirds >= 9,
distinct thirds <= 8,
```

which are incompatible.  The profile-independent arithmetic theorem is
`no_multiplicity_profile_fits_internal_targets`.

## Strongest remaining profile

The profile `(3,0,8)` has

```text
3 + 0 + 8 = 11
```

distinct thirds.  It is the strongest remaining case because it saturates
the original eleven-slot target budget exactly.

Before endpoint exclusion, any blocker allocation for this profile must use
the complete load vector

```text
(3,2,2,2,2).
```

Lean proves this rigidity in
`profile_3_0_8_forces_full_target_capacity`.

After endpoint exclusion the first coordinate must instead be zero, leaving
capacity eight for eleven distinct blockers.  The explicit contradiction is
`profile_3_0_8_eliminated`.

## The other five profiles

The six remaining profiles and their distinct-vertex counts are:

| profile | distinct thirds |
|---|---:|
| `(0,3,7)` | 10 |
| `(0,6,5)` | 11 |
| `(1,1,8)` | 10 |
| `(1,4,6)` | 11 |
| `(2,2,7)` | 11 |
| `(3,0,8)` | 11 |

`remaining_six_profiles_exceed_internal_capacity` verifies uniformly that
each count is strictly greater than nine, hence certainly greater than the
eight internal slots.

The already treated `(0,0,9)` profile has nine distinct thirds and also fails
the same corrected eight-slot bound.  Its richer Latin analysis remains
useful because it exposed the missing endpoint identity, but the final scalar
contradiction no longer needs a classification of its ownership design.

## Exact remaining bridge

The missing formal statement is no longer a finite incidence condition.  It
is the graph-to-accounting extraction that packages, from the negation of the
desired clean handle:

1. all 27 third-choice incidences from three first choices and their three
   second choices;
2. same-branch uniqueness, hence multiplicity at most three;
3. at least one early-target contact for every distinct third;
4. endpoint exclusion by `third_choice_not_adj_endpoint`;
5. injection of one chosen blocker edge per distinct third into the union of
   the four internal outside-neighbor finsets.

The last injection does not need each third to have a unique target contact.
Choose one contact per distinct third.  Different thirds give different
outside-neighbor vertices automatically, so the chosen vertices inject into
the union whose total cardinality is at most eight.

Once this package is constructed, `no_multiplicity_profile_fits_internal_targets`
closes the obstruction without another case split.

## Verification

The module is self-contained over `FormalConjecturesUtil`.  It uses ordinary
kernel proofs and arithmetic only, with no holes, custom axioms, or native
decision shortcuts.
