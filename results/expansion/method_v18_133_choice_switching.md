# Method v0.18: WOWII 133 choice switching

Date: 2026-08-13

Local certificate: `lean/GraphConjecture133ChoiceSwitching.lean`

## Exact bounded selection

The two independent controls were rechecked by grouping handles first by the
choice of `c` and then by the choice of `b`.

- `PG(2,3)`: every oriented radius geodesic has three first choices; across
  all 2,808 `(geodesic,c)` pairs, every valid `b` has a contact-free third
  vertex.
- `Kneser(7,3)`: the same holds across all 3,780 `(geodesic,c)` pairs.

Thus neither control realizes any of the ten v0.17 singleton obstruction
patterns, even before switching to another `c`.  The useful formal theorem was
selected from the exact geometry behind those alternative choices rather
than from an absent empirical obstruction.

## First-choice accounting

For a nontrivial radius geodesic beginning `u,x₁,...`, define

```text
C = N(u) \ {x₁}.
```

Four-regularity gives `|C|=3`.  Lean certifies this as
`card_firstHandleChoices_eq_three`.

The key pivot interpretation is exact:

```text
a contacts x₀=u and a != x₁  iff  a in C.
```

This is `mem_firstHandleChoices_iff_adj_index_zero`, with
`index_zero_contact_is_choice` as the forward form.  Therefore a singleton
row `{0}` does not merely block the current handle: its third vertex is one of
the other available first choices.  Patterns containing zero are natural
choice-switch pivots.

## Second-choice separation

For each `c in C`, define its three forward choices

```text
B(c) = N(c) \ {u}.
```

Lean proves:

- `|B(c)|=3` in a four-regular graph;
- `B(c₁)` and `B(c₂)` are disjoint for distinct first choices.

The disjointness theorem `secondHandleChoices_disjoint` is forced by
C4-freeness: a common `b` would create

```text
u -- c₁ -- b -- c₂ -- u.
```

Hence switching among the three first choices exposes three disjoint
three-element second layers--nine distinct depth-two vertices before the
early-contact validity filter is applied.

## Abstract survivor count

These choice-switching constraints do not yet eliminate a v0.17 pattern in
the abstract model.  All ten singleton triples

```text
012, 013, 014, 023, 024,
034, 123, 124, 134, 234
```

can be assigned independently to different second-layer vertices while
respecting:

1. three first choices;
2. three pairwise-disjoint second-choice sets;
3. one contact per third-layer candidate;
4. three distinct targets within each fixed `b` obstruction.

So the exact abstract survivor count remains **10**.  Choice switching
reinterprets and expands the search space, but the first two layers alone do
not force a contradiction.

## Missing independent constraint

The missing relation is at the third layer.  A forward candidate belonging to
one `b` may coincide with, or be adjacent to, a first or second choice in a
different branch.  Those cross-branch identifications are heavily constrained
by degree four and girth at least five, but they are not represented by the
ten target-index triples.

The next useful theorem should count the union of third-neighbor sets across
the disjoint `B(c)` branches, while quotienting possible repeated vertices.
Alternatively, sum residual degree capacity at `x₀,...,x₄` and prove that
the nine depth-two choices force more distinct blocker incidences than those
targets can support.  Either route genuinely couples different `(c,b)`
choices; another single-matrix filter cannot progress.

## Lean audit

The module uses no native computation, proof holes, or custom axioms.  It was
checked with local dependencies and warnings promoted to errors:

```text
LEAN_PATH=/tmp/c5k4-133-choice:/tmp/c5k4-133-pivot:\
/tmp/c5k4-133-metric:/tmp/c5k4-133-cross-row:\
/tmp/c5k4-133-depth3:/tmp/c5k4-133-early-comb:\
/tmp/c5k4-133-handle-existence:/tmp/c5k4-133-deep-handle:\
/tmp/c5k4-133-degree-four:/tmp/c5k4-133-regular:\
/tmp/c5k4-133-specialization:/tmp/c5k4-133-v07-check \
  timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133ChoiceSwitching.lean
```

Result: exit code 0 in 6.5 seconds.

This is an exact choice-layer theorem and an honest non-elimination result,
not unrestricted handle existence or a counterexample release candidate.
