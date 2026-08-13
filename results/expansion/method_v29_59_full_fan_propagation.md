# Method v29: WOWII #59 full-fan propagation

Date: 2026-08-13

Local certificate: `lean/GraphConjecture59FullFanPropagation.lean`

## Result

The highest-priority v28 residue was the center-plus-one-endpoint pattern with
the complete fan `p-a`, `p-b`, `p-q`. Let `w` be the path endpoint missed by
`q`. Positive alignment and compatibility give the induced four-vertex path

```text
q -- p -- a -- w
```

because `q-a`, `q-w`, and `p-w` are absent.

Now let `d` be a third core-side vertex, so `a-d` is absent. If `d` has at
most one neighbor among `{q,p,w}`, adding it to this path gives an induced
forest of order five. Therefore the global corner hypothesis `f(G)=4` forces

```text
d hits at least two of q, p, w.
```

Lean proves this cover directly and specializes it to either orientation of
the center-plus-exactly-one-endpoint attachment.

## The other two v28 residues

The same frame argument also attacks the other exact residues.

For the endpoints-only attachment, take `w=c`, the missed center. Then
`q-c` and `p-c` are absent, so the four-vertex frame is automatically a
forest regardless of `p-q`. Thus `f(G)=4` forces every third same-side core
vertex to hit at least two of `{q,p,c}`. This matches the v28 observation that
`p-q` is irrelevant in that residue.

For the all-three attachment, the frame has the potential rectangle

```text
q -- p
|    |
w -- a
```

with opposite nonedges `q-a` and `p-w`. If either `p-q` or `p-a` is missing,
the rectangle is broken and the same two-neighbor cover is forced. Therefore
every all-three obstruction with exactly two fan edges propagates by choosing
a core incident with the missing fan edge. Only the all-three/full-fan case,
where the rectangle is already saturated, survives this rung unchanged.

## Interpretation

The residues are not discharged yet, but—with the single saturated-rectangle
exception—they no longer remain self-contained seven-vertex obstructions.
They propagate a sharp two-neighbor requirement onto every fresh same-side
core vertex. This is the requested bridge from the local path obstruction to
the dense-core/global-`f=4` constraints.

The next step is to combine the forced cover with the deletion-critical
`3+3` core profile. Since every core card contains a rectangle and the core
has eight or nine cross-edges, the third core vertex has very little freedom
left for simultaneously covering `q,p,w` without creating another explicit
five-forest.

## Lean audit

The complete dependency chain from `GraphConjecture40Baseline` through v28
and `GraphConjecture59FullFanPropagation` was rebuilt from source on a fresh
olean path. The independent v19 branch
`GraphConjecture59SynchronizedRows` → `GraphConjecture59FiveTypeAlignment`
was rebuilt against the same fresh base.

Every process completed under the 60-second cap with
`-DwarningAsError=true`. The slowest dependency was
`GraphConjecture59FiveTypeAlignment` at 27 seconds. A final timed rebuild of
the new module completed in 8.06 seconds with exit code 0 and no output.

The source contains no `sorry`, `admit`, `axiom`, or `native_decide`.
