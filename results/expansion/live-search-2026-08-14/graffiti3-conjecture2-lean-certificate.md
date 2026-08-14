# Graffiti³ Conjecture 2: arithmetic Lean certificate

Date: **2026-08-14 UTC**

Scope: **arithmetic extraction only; not a full graph-invariant formalization**

## Candidate reduction

Let the two centers of a double star be adjacent, with eleven leaves incident
to the left center and twelve leaves incident to the right center.  Under the
source's closed distance-two convention, the exact values are:

- both centers: `d₂ = 25`;
- each of the eleven left leaves: `d₂ = 13`;
- each of the twelve right leaves: `d₂ = 14`.

The 23 leaves form an independent set.  Splitting the RGA2 sum into its center
edge and two spoke classes therefore gives

```text
RGA2
  = 2 sqrt(25*25)/(25+25)
      + 11 * 2 sqrt(13*25)/(13+25)
      + 12 * 2 sqrt(14*25)/(14+25)
  = 1 + 55 sqrt(13)/19 + 40 sqrt(14)/13
  < 23.
```

The strict inequality uses the rational upper bounds
`sqrt(13) < 361/100` and `sqrt(14) < 15/4`; squaring reduces both obligations
to exact rational arithmetic.

## Formal scope

[`lean/Graffiti3Conjecture2Arithmetic.lean`](../../../lean/Graffiti3Conjecture2Arithmetic.lean)
contains no `sorry`.  It proves:

1. the two radical simplifications and the three-edge-class decomposition;
2. the exact simplified expression is strictly less than 23;
3. an abstract wrapper: any graph data with `alpha >= 23` and this exact RGA2
   formula violates `alpha <= RGA2`.

The current `formal-conjectures` snapshot has no Graffiti³ Conjecture 2 or
RGA2 declaration.  Accordingly, this file does **not** claim to verify the
double-star adjacency relation, the 23-leaf independent set, the closed
distance-two counts, or a graph-level RGA2 edge sum in Lean.  Those finite
graph equalities remain explicit hypotheses of the wrapper rather than being
hidden behind axioms.

## Cleaner balanced companion

The same arithmetic file also records the balanced double star with twelve
leaves on each center.  It has 26 vertices, 24 independent leaves, center
values `d₂ = 26`, and leaf values `d₂ = 14`.  Its one center edge and 24
spokes reduce to

```text
RGA2 = 1 + 12 sqrt(91)/5 < 24.
```

Here `sqrt(91) < 191/20`, again by exact squaring.  This is a cleaner companion
witness; the `(11, 12)` double star above remains the original frozen-search
hit.  No infinite-family statement is asserted.
