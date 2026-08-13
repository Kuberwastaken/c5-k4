# Method v0.9: WOWII 59 residue-three frontier

Date: 2026-08-13

## Scope

This continues proof extraction for an already-disproved
`formal-conjectures` statement. It is neither a new counterexample nor a
held-out discovery claim. The known counterexamples remain the 123-vertex
witness in upstream PR #4574 and the fully Lean-certified 18-vertex witness in
upstream PR #4583.

Method v0.8 proved the complete `residue <= 2` slice of WOWII 59. This pass
asks exactly how far the same source inequality can be pushed at residue three.

## Two graph constraints beyond raw arithmetic

The first ingredient remains the WOWII 40 source baseline

```text
b(G) + 2 <= 2 f(G).
```

The second is now proved directly for connected nontrivial finite graphs:

```text
alpha(G) + 1 <= f(G).
```

Choose a maximum independent set `I`. Connectedness and nontriviality give a
vertex `v` outside `I`; the graph induced by `I union {v}` is a star plus
isolates, hence a forest.

The classical Griggs--Kleitman/Favaron--Mahéo--Saclé residue inequality

```text
residue(G) <= alpha(G)
```

is not reproved in this lane. Wherever it is used, it appears as an explicit
hypothesis rather than being smuggled in through an upstream theorem with
`sorry`.

## Unconditional extension

For `residue <= 3` and `f >= 5`, the source baseline gives

```text
residue * b <= 3b <= 6f - 6 <= f^2.
```

The last step is valid exactly because

```text
f^2 - 6f + 6 >= 0
```

for integral `f >= 5`. Therefore the exact upstream ceiling-square-root bound
holds unconditionally throughout

```text
residue(G) <= 3 and f(G) >= 5.
```

This strictly extends v0.8.

## Exact conditional frontier

Assume the standard residue inequality `residue <= alpha`. If residue is
three, the newly formalized independent-set augmentation forces `f >= 4`.

- If `f >= 5`, the unconditional extension applies.
- If `f = 4`, the source baseline forces `b <= 6`.
- If additionally `b != 6`, integrality gives `b <= 5`, so
  `residue*b <= 15 < 16 = f^2`.

Consequently, subject only to the explicit classical residue inequality,
every possible failure with `residue <= 3` is forced into the exact invariant
corner

```text
(residue(G), b(G), f(G)) = (3, 6, 4).
```

Equivalently, the full conjectured inequality is proved for every such graph
with `b != 6`. This is stronger and more informative than adding the blunt
condition `f >= 5`: it classifies the only unresolved low-residue coordinate.

The theorem does **not** assert that the corner is realizable. Closing or
excluding that one graph-realizability corner is the next honest mathematical
question.

## Formal artifact

[`lean/GraphConjecture59Extension.lean`](../../lean/GraphConjecture59Extension.lean)
contains:

1. `indepNum_add_one_le_largestInducedForestSize`, an unconditional graph
   theorem;
2. the unconditional residue-three product certificate for `f >= 5`;
3. its exact upstream-shaped ceiling corollary;
4. the product certificate for `residue <= 3`, `residue <= alpha`, and
   `b != 6`;
5. its exact upstream-shaped ceiling corollary;
6. a converse frontier theorem showing any low-residue product failure must
   have exactly `(residue,b,f)=(3,6,4)`.

No upstream conjecture theorem is invoked.

## Verification

The warning-clean `.olean` files for the two earlier local dependencies were
placed in `/tmp`, then the new module was checked with

```text
LEAN_PATH=/tmp lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture59Extension.lean
```

The final command completed in 6.8 seconds with no warnings or errors. The
module contains no `sorry`, `admit`, custom axiom, native decision procedure,
or imported open-conjecture proof.

## Outcome

`THEOREM_SLICE_AND_EXACT_FRONTIER`.

This pass expands the unconditional theorem from residue at most two to the
entire residue-three region with `f >= 5`, and reduces the remaining
low-residue problem to one exact invariant triple under the standard residue
inequality. It makes no novelty claim about the already-known falsity of the
general conjecture.
