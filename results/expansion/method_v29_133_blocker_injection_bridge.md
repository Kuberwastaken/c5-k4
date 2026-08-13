# Method v0.29: WOWII 133 blocker-injection bridge

## Outcome

The finite graph-to-accounting bridge is now kernel-checked.

Given the actual third-choice finsets for three branches and three second
parents per branch, Lean proves:

1. there are 27 parent-third incidences;
2. each fixed branch contains nine distinct thirds;
3. selecting one internal blocking target for every distinct third embeds
   those vertices into the union of four outside-neighbor finsets;
4. that target union has cardinality at most eight;
5. therefore such a blocker selection is impossible.

The important simplification is that the full multiplicity classification is
not needed for this step.  One branch already supplies nine distinct thirds,
so the contradiction is directly

```text
9 <= |third union| <= |internal blocker union| <= 8.
```

Lean certificate:

- `lean/GraphConjecture133BlockerInjectionBridge.lean`.

## The finite layer package

The module uses the finite index types

```text
Branch         = Fin 3,
ParentSlot     = Fin 3,
InternalTarget = Fin 4.
```

An actual instantiation supplies

```text
thirds : Branch -> ParentSlot -> Finset V,
outside : InternalTarget -> Finset V.
```

Here `thirds b p` is the graph finset

```text
N(parent(b,p)) \ {first(b)},
```

and `outside k` is the outside-neighbor finset of geodesic target `k+1`.

The definitions `branchThirds`, `allThirds`, and `internalOutsideUnion`
assemble these exact finite families without quotienting vertices by
incidence labels.

## The 27 incidences

Four-regularity gives

```text
|thirds(b,p)| = 3
```

for every one of the nine colored parent slots.  The theorem
`twenty_seven_actual_third_incidences` sums these cardinalities and obtains

```text
sum_b sum_p |thirds(b,p)| = 27.
```

This statement retains actual graph vertices in the finsets; only the sum
counts incidences with repetitions.

## Nine distinct vertices in one branch

C4-freeness makes the three parent-third finsets in one branch pairwise
disjoint.  Otherwise

```text
first -- parent₁ -- third -- parent₂ -- first
```

would be a C4.

`card_branchThirds_eq_nine` combines pairwise disjointness with the three
cardinality-three facts to prove

```text
|branchThirds(b)| = 9.
```

Since a branch union is contained in `allThirds`, the theorem
`nine_le_card_allThirds` yields the needed lower bound.

This bypasses the earlier `n₁,n₂,n₃` classification.  Cross-branch overlap
can collapse 27 incidences to nine vertices, but it cannot reduce even one
branch below nine.

## Selecting blockers

A third blocked at an internal target is itself an element of that target's
outside-neighbor finset.  Thus the selected blocker map on vertices is simply

```text
z |-> z.
```

It is not a map to target indices and does not need distinct target choices.
Many thirds may select the same target, but distinct thirds remain distinct
vertices inside its outside-neighbor set.

The module formalizes both directions:

- `exists_internal_target_of_mem_union` extracts a target index from union
  membership;
- `mem_union_of_exists_internal_target` turns a selected target contact into
  union membership.

`blockerEmbedding` is the subtype map from the actual third union into the
internal outside-neighbor union, and `blockerEmbedding_injective` proves it is
injective.

This makes precise the informal phrase “select one blocker for each distinct
third.”  The selected edge may vary, but its outside endpoint is always the
third vertex itself.

## Eight internal slots

Each target at original indices one through four has two outside-neighbor
slots.  Given

```text
|outside(k)| <= 2,
```

`card_internalOutsideUnion_le_eight` proves

```text
|outside(0) union ... union outside(3)| <= 8.
```

No disjointness of the target neighborhoods is assumed.  Overlap only makes
the union smaller.

## Exact bridge theorem

`no_internal_blocker_selection_of_twenty_seven_incidences` takes exactly:

1. cardinality three for every actual parent-third finset;
2. same-branch pairwise disjointness;
3. cardinality at most two for every internal outside-neighbor finset;
4. for every distinct third, one selected internal target whose outside set
   contains it.

It derives `False`.

The equivalent cover form is
`no_internal_blocker_cover_of_twenty_seven_incidences`.  The constructive
dual, `exists_third_without_internal_blocker`, produces a third lying outside
all four internal blocker sets whenever only the layer and capacity facts are
given.

## Remaining graph-specific splice

The finite selection and injection are complete.  The remaining splice into
the full WOWII proof is now narrowly syntactic:

1. instantiate `thirds b p` with `thirdHandleChoices G (first b) (parent b p)`;
2. instantiate `outside k` with `outsideTargetNeighbors G geodesic (k+1)`;
3. discharge cardinality three from four-regularity;
4. discharge same-branch disjointness from C4-freeness;
5. discharge outside cardinality two from the internal-geodesic lemma;
6. under the negation of a clean third, obtain for each `z` an early contact;
7. remove index zero using `third_choice_not_adj_endpoint`, leaving one of
   internal indices one through four.

Steps 3--5 and 7 already exist as individual graph lemmas in the #133 chain.
The only proposition that still needs to be threaded through the concrete
handle construction is step 6: translating “this third does not complete the
clean handle” into membership in one of the five early contact sets.  Once
that is available, step 7 and
`no_internal_blocker_selection_of_twenty_seven_incidences` close the branch.

## Verification

The module is self-contained over `FormalConjecturesUtil`.  It uses ordinary
finite-set cardinality proofs and kernel reduction only, with no holes,
custom axioms, or native-decision shortcuts.
