# Reed complete-join Lean extraction

Date: **2026-08-13 UTC**

Status: **COMPLETE — no-sorry reusable coordinate theorem**

Source: `lean/ReedCompleteJoinCoordinates.lean`

## What is formalized

The module introduces `ExactCoordinates`, containing natural-number
`chi`, `omega`, and `maxDegree` fields, and defines exact Reed slack by

```text
omega + maxDegree + 2 = 2 chi + slack.
```

It proves the generic complete-join coordinate transform:

```text
base slack = s
base order = base Delta + 1 + q
joined chi = base chi + t
joined omega = base omega + t
joined Delta + 1 = base order + t
------------------------------------------------
joined slack = s + q.
```

The formulation deliberately avoids natural-number subtraction.  The
uncancelled order/degree gap appears directly as `q`.

## Odd-carrier specialization

Writing the odd carrier parameter as `m=2k+1`, the exact coordinates are

```text
chi   = 5k+3,
omega = 4k+2,
Delta = 6k+2,
order = 10k+5.
```

Lean proves:

1. these coordinates have zero Reed slack;
2. `order = Delta+1+(4k+2)`;
3. any certified complete-clique join has exact slack `4k+2 = 2m`,
   independently of the joined clique order;
4. a finite graph carrying the three predicted invariant equalities satisfies
   both the exact extended equality

   ```text
   2 chi + (4k+2) = omega + Delta + 2
   ```

   and the finite Reed inequality.

`GraphCertificate.reed_bound` separately packages the general fact that any
finite graph with certified exact natural slack satisfies Reed's bound.

## Honest API boundary

The current pinned Mathlib tree has disjoint graph sum but no complete-join
constructor accompanied by finite formulae for chromatic number, clique
number, and maximum degree.  The module therefore does **not** claim to have
formalized `C5[K_m] join K_t` as a graph object.  It formalizes the strongest
reusable theorem supported by the available API: exact invariant equalities
are explicit certificate premises, and the resulting slack transformation is
kernel checked.

This cleanly separates two future tasks:

- graph-library work proving the generic join invariant formulae;
- family-specific work proving the odd carrier invariant certificates.

Either can plug directly into the completed arithmetic theorem.

## Verification

The module was compiled in a fresh output directory with the repository's
pinned Lean 4.27.0 toolchain:

```text
lean -DwarningAsError=true -o <fresh>/ReedCompleteJoinCoordinates.olean \
  lean/ReedCompleteJoinCoordinates.lean
```

Every compiler process was capped at 60 seconds.  The final warning-as-error
build completed successfully.  The source contains no `sorry`, `admit`,
`native_decide`, custom axiom, or diagnostic print command.

No commit or public action was performed.
