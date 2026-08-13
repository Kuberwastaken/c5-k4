# Method v0.27: WOWII 133 endpoint metric failure

## Outcome

The v0.26 Latin ownership kernel does **not** embed into even the first
geodesic-prefix layer of the graph.  The first failed clause is the identity
of target index zero:

```text
x₀ = u,
```

where `u` is the common endpoint of the three first-choice branches.

The earlier capacity abstraction treated the three outside slots at `x₀` as
anonymous.  They are not anonymous.  After the geodesic successor `x₁` is
removed, the outside neighbors of `u` are exactly the three first handle
choices.  Restoring that identity makes every cross-branch third blocked at
index zero impossible in a C4-free graph.

This eliminates not only the explicit v0.26 blocker assignment but every
capacity-respecting reassignment of the nine Latin thirds.

Lean certificate:

- `lean/GraphConjecture133EndpointMetricFailure.lean`.

## The four-cycle

Fix one first branch and write its local chain as

```text
u -- c -- p -- z.
```

Here:

- `c` is a first choice adjacent to endpoint `u`;
- `p` is one of its second choices, with `p != u` because `u` was erased;
- `z` is a third owned by `p`.

If `z` blocks target index zero, then `z -- u`.  Unless `z=c`, the four
distinct vertices form

```text
u -- c -- p -- z -- u.
```

Therefore C4-freeness forces `z=c`.  This is the theorem
`endpoint_blocker_forces_first_eq`.

Now use two distinct first branches.  A Latin third has an owner below every
branch.  The same argument forces simultaneously

```text
z = c₀
z = c₁,
```

contradicting distinctness of the first choices.  The generic graph theorem
`cross_branch_endpoint_blocker_impossible` packages this contradiction.

No triangle-free or degree-four hypothesis is needed for this step.  The
only graph obstruction is C4-freeness, together with the genuine
second-parent freshness `p != u`.

## Why changing blocker colors cannot help

The fixed v0.26 assignment places three thirds at target zero; Lean verifies

```text
|blockedThirds(0)| = 3
```

in `three_thirds_block_index_zero`.

More generally, there are nine distinct Latin thirds requiring blockers.
The four internal prefixes have capacity two each, for total capacity eight.
Hence every capacity-respecting assignment must use index zero at least once:

```text
9 > 2 + 2 + 2 + 2.
```

The arithmetic form is `endpoint_blocker_is_capacity_forced`.  The stronger
function-level theorem `exists_index_zero_blocker_of_capacities` proves this
directly for an arbitrary map

```text
ThirdVertex -> Target.
```

It uses finite fiber counting, not enumeration of all `5^9` assignments.

## Exact noncompletion certificate

`EndpointPrefixRealizationFor` records only the smallest layer needed:

1. the geodesic prefix edge `u--x₁`;
2. three distinct first choices adjacent to `u` and different from `x₁`;
3. each colored parent adjacent to its branch's first choice;
4. every parent fresh from `u`;
5. all Latin parent-third incidences;
6. every target-zero blocker adjacent to `u`.

The theorem
`no_endpointPrefixRealizationFor_of_latin_kernel` states that no C4-free
simple graph realizes this data for **any** blocker assignment satisfying the
target capacities.

`no_endpointPrefixRealization_of_latin_kernel` specializes the result to the
explicit v0.26 blocker map.

Thus this is an exact noncompletion certificate, not merely a failed search.
The contradiction already occurs before completing target degrees, enforcing
global four-regularity, or checking longer distance labels.

## What this corrects

The local capacity equation

```text
3 + 2 + 2 + 2 + 2 = 11
```

is numerically correct but loses vertex identity at index zero.  The first
three slots are the endpoint's existing off-geodesic neighbors.  A blocker
using one of them must participate in the first-choice structure rather than
being introduced as a fresh third vertex.

The v0.26 Latin incidence model passed all tests that deliberately omitted
this identification.  Its failure here is therefore the requested first
missing metric/embedding clause, not an inconsistency in the earlier Lean
theorems.

## Consequence for the `(0,0,9)` survivor

The maximally collapsed Latin realization of the aggregate `(0,0,9)` profile
is eliminated:

- all nine thirds have multiplicity three across the branches;
- an endpoint blocker is impossible for every such third;
- internal targets can block at most eight distinct thirds.

This does not yet prove WOWII 133.  Less symmetric ownership profiles from
the earlier multiplicity partition may contain multiplicity-one or
multiplicity-two thirds that can coincide with a first choice without the
same cross-branch contradiction.  Those profiles must now be revisited with
the target-zero slots typed as first choices.

## Next focused step

Return to the seven aggregate multiplicity profiles from v0.21 and split
blockers by target type:

- target zero: the blocker must equal a first choice and its branch ownership
  pattern is sharply restricted;
- targets one through four: at most eight distinct blockers in total.

The next useful inequality should count how many distinct thirds are eligible
to be identified with one of the three first choices.  If the non-endpoint
blocker demand remains above eight after those eligible vertices are removed,
the corresponding aggregate profile is eliminated immediately.

## Verification

The certificate is self-contained over `FormalConjecturesUtil` so it can be
checked against the fresh upstream dependency chain.  It uses ordinary
kernel reduction only and contains no proof holes, custom axioms, or native
decision shortcuts.
