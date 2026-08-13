# Method v0.26: WOWII 133 Latin ownership survivor

## Outcome

The 3-by-3 Latin-square ownership profile **survives the ownership,
blocker-capacity, and saturation constraints assembled through v0.25**.  In
particular, it survives:

- the C4-free bound that two distinct parents share at most one third;
- the requirement that every second parent owns three thirds;
- multiplicity-three saturation at every third;
- the blocker-target capacity vector `3,2,2,2,2`;
- owning-parent/blocker-target non-incidence;
- the additional C4 check that two thirds blocked by one target cannot share
  a parent.

This is a negative result about the present proof route, not a counterexample
to WOWII 133.  The finite object certified here is an incidence model, not a
connected four-regular graph with the conjecture's metric configuration.

Lean certificate:

- `lean/GraphConjecture133LatinOwnership.lean`.

## The Latin replacement

Write the nine thirds as the points `(r,c)` of a 3-by-3 grid.  The three
branch colors use the parallel classes

1. row `r`;
2. column `c`;
3. Latin diagonal `r+c mod 3`.

Thus each branch contains three parent slots, each parent owns three points,
and each point has exactly one owner in every branch.  These are the
definitions `ownerSlot`, `parentOwns`, `parentThirds`, and `thirdOwners`.

Lean proves:

- `three_thirds_per_parent`;
- `three_owners_per_third`;
- `unique_owner_in_branch`.

Unlike the discarded repeated-slot profile, two distinct colored parents now
have at most one common third.  Parents in the same branch are disjoint, and
parents in different branches meet in exactly one point.  The relevant
certificates are

- `distinct_parents_common_thirds_le_one`;
- `cross_branch_common_thirds_eq_one`.

This exactly meets, rather than evades, the graph-derived v0.24/v0.25 bound.

## Blocker geometry

The naive cyclic blocker assignment from v0.22 is not strong enough for this
test: two thirds sent to one target can share a parent, producing the local
four-cycle

```text
parent -- third₁ -- target -- third₂ -- parent.
```

The repaired assignment uses pieces of the unused fourth parallel class of
the affine 3-by-3 grid.  Its target loads are

```text
(3, 2, 1, 2, 1),
```

which lie beneath the available capacities

```text
(3, 2, 2, 2, 2).
```

Lean proves the exact vector in `blocker_load_vector`, proves that all nine
thirds are used once in `all_nine_thirds_are_blocked_once`, and proves the
capacity inequality in `blocker_capacity_respected`.

Most importantly, `coblocked_thirds_have_no_common_parent` proves that two
distinct thirds assigned to the same target have disjoint owner sets.  The
blocker assignment therefore introduces no C4 of the displayed form.

## Saturated neighborhoods

The model has the exact local degree accounting forced by four-regularity:

- every parent has one first-layer contact and three third contacts;
- every third has three colored-parent contacts and one blocker-target
  contact.

These equalities are certified by `parent_local_degree_saturated` and
`third_local_degree_saturated`.

The abstract parent-target relation is empty.  This is compatible with, and
indeed forced locally by, saturation.  The theorem
`blocker_forbids_every_owning_parent` packages the required non-incidence for
each owned blocked third.

Finally, `latin_ownership_survives_all_local_constraints` combines all of the
following in one kernel-checked theorem:

1. three thirds per colored parent;
2. three colored owners per third;
3. at most one common third for distinct parents;
4. all blocker capacity inequalities;
5. no common parent for co-blocked thirds;
6. parent degree-four local saturation;
7. third degree-four local saturation;
8. owning-parent/blocker-target non-incidence.

## What is still missing

The exact missing condition is **metric embeddability of this saturated
incidence core into the original graph configuration**.

The finite certificate does not provide a single connected simple graph in
which all of the following hold simultaneously:

- the endpoint and its three distinct first-choice branches;
- the earlier geodesic prefixes leading to the five blocker targets;
- the target-to-endpoint distance labels used in the eccentricity argument;
- the remaining target and first-layer degree completions;
- global four-regularity, triangle-freeness, and C4-freeness after those
  completions;
- the required conclusion that one chosen tree reaches every vertex within
  the target radius.

The local incidence core itself has no remaining parent or third degree
freedom: both classes are saturated.  Any contradiction must therefore be
forced through the unsaturated target/first/endpoint side or through a global
distance requirement.  More parent-third compatibility lemmas alone cannot
eliminate this model.

## Focused next test

The next useful bounded search should treat the Latin incidence core as
fixed, then add only:

1. the five named target geodesic prefixes;
2. the three first choices and the endpoint;
3. the residual target/first degrees;
4. distance labels from the endpoint.

Reject a completion immediately on a triangle, a four-cycle, a degree above
four, or a distance-label violation.  This is much smaller and more
informative than reopening arbitrary ownership search: the ownership kernel
is now completely classified at the local level.

If no such completion exists, the first unsatisfied metric or degree clause
is the honest missing lemma for the proof.  If one does exist, the remaining
route must use a later-radius tree switch rather than local incidence
counting.

## Verification

The Lean file is intended to be checked from the fresh
`formal-conjectures` dependency chain with warnings treated as errors and a
60-second cap.  It uses ordinary kernel reduction (`decide`) only; there are
no holes, custom axioms, or native-decision shortcuts.
