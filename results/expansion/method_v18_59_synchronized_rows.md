# Method v0.18: WOWII 59 synchronized dense rows

Date: 2026-08-13

## Scope

This pass synchronizes the two color-side incidence systems developed in
v0.14-v0.17. WOWII 59 is already externally disproved; this is proof
extraction, not a new disproof, release, or held-out success.

## Full row types

On either three-vertex color side, an exchange-resistant attachment row is one
of exactly four subsets:

```text
three subsets of order two,
one full subset of order three.
```

A full attachment row is the ordered pair

```text
(left side type, right side type),
```

so there are exactly

```text
4 * 4 = 16
```

possible dense full row types.

## Exact synchronization threshold

All `2^16=65,536` families of distinct full row types were enumerated. For
each family, every triple was tested for simultaneous alignment:

```text
the three left side sets have nonempty common intersection,
and the three right side sets have nonempty common intersection.
```

The largest family with no simultaneously aligned triple has size four.
Exactly nine four-element extremal families attain that maximum. Therefore:

```text
every five distinct dense full row types contain a triple aligned on both
color sides.
```

The threshold is sharp because those nine four-type families are explicit
counterexamples at size four. The exact enumeration completed in under 0.4
seconds.

This five-type theorem is currently an exact finite classification result, not
yet a Lean theorem. Formalizing the 65,536-case Boolean kernel without native
evaluation would add substantial case machinery while contributing no new
graph idea. The reusable symbolic part formalized in this pass is the exact
16-type encoding and its unconditional pigeonhole consequence below.

## Fully formal synchronized repetition threshold

The Lean development proves:

1. every dense graph attachment row belongs to the Cartesian product of the
   two large-subset families;
2. each side family has exactly four members, using
   `choose(3,2)+choose(3,3)=4`;
3. their Cartesian product has exactly sixteen members;
4. among seventeen dense outside vertices, two distinct vertices have
   identical attachment sets on **both** color sides.

The last theorem is a synchronized statement, not merely separate sidewise
repetition. It uses the finite maps-to pigeonhole theorem on the explicit
16-element target family.

## What the five-type threshold means graphically

For any five outside vertices whose full dense row types are all distinct,
the exact finite theorem supplies three vertices `x,y,z` and core vertices
`a,b` in opposite color classes such that all three outside vertices attach to
both `a` and `b`.

Thus the triple shares a complete `K_{3,2}` incidence pattern into the core.
Their mutual outside adjacency graph remains unconstrained. The v0.16 audit
shows that when a triple extension reaches residue three, it already forces
`f>=5` or `b>=7`; however, a symbolic proof connecting the synchronized
`K_{3,2}` incidence alone to one of those outcomes has not yet been obtained.

## Formal artifact

[`lean/GraphConjecture59SynchronizedRows.lean`](../../lean/GraphConjecture59SynchronizedRows.lean)
defines `fullAttachmentRow` and proves:

- membership in the product of admissible side families;
- exact cardinality four for each side-type family;
- exact cardinality sixteen for the dense full-row family;
- repeated full-row existence among seventeen dense vertices.

The proof is symbolic and uses Mathlib finite-set cardinality and maps-to
pigeonhole lemmas.

## Verification

After compiling the warning-clean v0.8-v0.17 dependencies into temporary
`.olean` files, the module was checked with

```text
LEAN_PATH=/tmp lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture59SynchronizedRows.lean
```

It completed in 6.2 seconds with no warnings or errors. The file contains no
`sorry`, `admit`, custom axiom, `native_decide`, or imported upstream
conjecture proof.

## Honest boundary

Two synchronized thresholds now coexist:

- **five distinct types:** exact finite audit forces a bi-aligned triple;
- **seventeen vertices:** formal pigeonhole proof forces a repeated full row.

Closing the gap in Lean requires a compact noncomputational proof that five
distinct pairs from the four-by-four side-type grid contain a triple aligned
in both coordinates. The nine sharp four-type configurations suggest a direct
classification via the rotating-complement exceptions from v0.16.

Even after that combinatorial theorem is formalized, one graph bridge remains:
convert either a repeated full row or a bi-aligned triple, together with the
outside adjacency pattern, into `f>=5`, `b>=7`, or an ambient Havel--Hakimi
residue bound. The finite triple audit supports this implication only after
the complete explicit core and outside graph are included; incidence alone may
need an additional adjacency split.

## Outcome

`SYNCHRONIZED_TYPE_ENCODING_AND_REPETITION_THEOREM`.

The exact lowest distinct-type threshold is five and is sharp. The fully
formal unconditional threshold currently obtained is seventeen vertices,
which forces a repeated two-sided attachment row.
