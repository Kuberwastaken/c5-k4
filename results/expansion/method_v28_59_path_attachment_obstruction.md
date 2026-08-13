# Method v28: WOWII #59 exact path-attachment obstruction

Date: 2026-08-13

Local certificate: `lean/GraphConjecture59PathAttachmentObstruction.lean`

## Result

The three two-or-more-hit patterns left by v27 now have separate exact
algebraic residues. Label the outside path `u-c-v`.

| `q` attachment | five-forest exit | surviving extension obstruction |
|---|---|---|
| center plus exactly one endpoint | nonhit endpoint with both cores, or one core with both endpoints | `p-a`, `p-b`, and `p-q` all present |
| both endpoints, not center | center with both cores | `p-a` and `p-b` both present |
| all three path vertices | any path vertex with both cores | at least two of `p-a`, `p-b`, `p-q` present |

Most exits use the common set `{a,b,w,p,q}` in one of two orders. When `q`
misses `w` and `p` misses one core, the vertices form a successive-leaf chain.
In the all-three case, the core pair and `q` are independent; add `w`, then
add `p`, which has at most one old neighbor when no two fan edges are present.
The exceptional center-plus-endpoint case with both core edges but missing
`p-q` uses `{a,u,v,p,q}` instead.

Lean packages the three orientations of the outside path and proves

```text
f(G) >= 5
or the corresponding labeled obstruction above holds.
```

This is strictly sharper than the v27 statement that merely retained every
two-or-more-hit attachment.

## Scope

The split uses the core nonedge `a-b`, which is present in the surrounding
low-bipartite-number corner. Positive alignment edges are not needed for the
forest exits. Proving that the listed residues are impossible, or extracting
their global consequences, is the next rung.

## Lean audit

The complete dependency chain from `GraphConjecture40Baseline` through v27
and `GraphConjecture59PathAttachmentObstruction` was rebuilt from source on a
fresh olean path. The independent v19 branch
`GraphConjecture59SynchronizedRows` → `GraphConjecture59FiveTypeAlignment`
was rebuilt against the same fresh base.

Every process completed under the 60-second cap with
`-DwarningAsError=true`. The slowest dependency was
`GraphConjecture59FiveTypeAlignment` at 27 seconds. A final timed rebuild of
the new module completed in 9.50 seconds with exit code 0 and no output.

The source contains no `sorry`, `admit`, `axiom`, or `native_decide`.
