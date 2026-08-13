# Method v0.30: WOWII 133 final local splice

## Outcome

The blocker-counting argument is now spliced into actual graph neighborhoods.

Lean proves the following end-to-end local statement:

> Let `c` be a first choice at the head `u` of a length-at-least-five
> geodesic.  If all three second parents below `c` are distinct and clean
> against the geodesic, then among their nine actual third choices there is a
> vertex with no contact at geodesic indices `0..4`.

Shortestness already removes contacts at indices five and later.  Therefore,
when combined with the previously established first- and second-layer
freshness data, this is exactly the third-layer escape needed by the clean
three-handle construction.

The proof identifies one remaining structural hypothesis:

```text
one first-choice branch has all three second parents geodesically clean.
```

The current earlier theorem guarantees at least one clean second parent for
each first choice.  It does not yet guarantee three clean second parents below
one first choice.  Thus the local blocker splice is complete, but that
three-parent strengthening is still needed before claiming the full WOWII 133
theorem.

Lean certificate:

- `lean/GraphConjecture133FinalLocalSplice.lean`.

## Failed cleanliness gives a contact

For a candidate third `z`, early cleanliness is

```text
forall k < 5, k <= geodesic.length ->
  not Adj z (geodesic.getVert k).
```

`contact_of_not_early_clean` proves the exact classical negation:

```text
not early-clean(z)
  -> exists k < 5, k <= length and Adj z x_k.
```

No finite search or row classification is used here.  This is the direct
logical bridge from failure of the desired condition to a blocking edge.

## Index zero is removed

For an actual third choice the branch chain is

```text
u -- c -- parent -- z,
```

with

```text
parent != u,
z != c.
```

The latter two facts come from the two neighbor-set erasures defining second
and third choices.  If `z` contacted `x₀=u`, these four distinct vertices
would make a C4.  `genuine_third_not_contact_zero` formalizes this exclusion.

Therefore the contact extracted from failed cleanliness has index one, two,
three, or four.

## Contacts become outside-neighbor membership

`internalOutside G p k` is the neighborhood of original geodesic target
`x_(k+1)` after erasing its two path neighbors:

```text
N(x_(k+1)) \ {x_k,x_(k+2)}.
```

Freshness of `z` from the geodesic supplies both erasure inequalities.
`mem_internalOutside_of_contact` then turns adjacency to `x_(k+1)` into
membership in this exact finset.

`internal_blocker_of_not_early_clean` combines:

1. the negated-cleanliness contact;
2. index-zero C4 exclusion;
3. the four finite index cases;
4. freshness from the geodesic;

to prove

```text
z in internalOutside(0) union ... union internalOutside(3).
```

This is the concrete graph-level hypothesis required by v0.29's blocker
injection.

## Exact internal capacities

`card_internalOutside_eq_two` proves directly that every one of the four
internal target finsets has cardinality two in a four-regular graph.  The
proof erases the two distinct path neighbors from a degree-four neighborhood.

The geodesic length assumption `5 <= length` is used only to make all four
targets genuinely internal and to supply the required path vertices through
index five.

## Actual third choices

The file defines

```text
thirdChoices G c parent = N(parent) \ {c}.
```

It proves:

- `card_thirdChoices_eq_three`: four-regularity gives three choices;
- `thirdChoices_disjoint`: two distinct parents below the same `c` cannot
  share a third in a C4-free graph.

Thus three distinct parents yield nine actual third vertices, with no
abstract incidence encoding.

## End-to-end local contradiction

`exists_early_clean_third_of_branch_capacity` is the generic finite-set form.
Assuming all nine thirds fail cleanliness:

1. every third lies in the four internal outside-neighbor sets;
2. the disjoint triples give a nine-element source union;
3. the four degree-two target sets give an at-most-eight-element target
   union;
4. inclusion forces `9 <= 8`.

`exists_early_clean_third_of_three_clean_parents` specializes everything to
the actual neighbor-erasure sets.  Its inputs are:

- a four-regular C4-free graph;
- a path of length at least five;
- one first choice adjacent to the path head;
- three distinct second parents adjacent to that first choice;
- second-parent freshness from the head;
- all three parents clean against the full geodesic.

It returns a concrete parent slot and one of its actual third choices that is
clean at every early index.

## Exact remaining hypothesis

The earlier depth-two theorem
`exists_depthTwo_avoiding_first_three` finds **one** second parent below a
chosen first choice which avoids the unresolved early contacts.  Together
with shortestness and triangle/C4 arguments, that parent is clean against the
geodesic.

The new theorem needs **three** such clean parents below one common first
choice in order to expose nine pairwise-disjoint thirds.  Four-regularity
does provide three second choices, but they need not all be clean under the
currently proved lemmas.

This is the precise remaining fork:

1. prove that one first choice has all three second choices clean; or
2. replace the one-branch nine-point argument with a cross-branch bound using
   one clean parent from each of the three first choices.

The second route starts with only three triples.  Cross-branch parents may
share one third, so their union need not have cardinality nine.  It therefore
requires an additional overlap/target argument and cannot be substituted
silently into the present proof.

The result should consequently be described as a completed local splice with
one exact three-clean-parents hypothesis, not yet as an unconditional proof
of WOWII 133.

## Verification

The file is self-contained over `FormalConjecturesUtil`.  It uses ordinary
kernel proofs, finite-set cardinality, and arithmetic only.  There are no
proof holes, custom axioms, or native-decision shortcuts.
