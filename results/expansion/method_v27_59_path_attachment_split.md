# Method v27: WOWII #59 path-attachment split

Date: 2026-08-13

Local certificate: `lean/GraphConjecture59PathAttachmentSplit.lean`

## Result

Label the outside path `u-c-v`. The only obstruction surviving v26 was that
`q` touches the outside triple. This rung proves that one touch is harmless.

The five-set `{u,c,v,p,q}` is still a forest whenever `q` has at most one
outside neighbor. The proof is a two-step leaf extension:

```text
outside path u-c-v
  + q, with at most one neighbor on the path
  + p, whose only possible previous neighbor is q.
```

Adding one vertex to an induced forest preserves acyclicity when it has at
most one neighbor in the old forest. A reusable Lean lemma proves this by
rotating any alleged cycle to the new vertex; its successor and penultimate
would then be two distinct old neighbors. If the alleged cycle omits the new
vertex, it lifts into the old induced forest.

Apply that lemma first to `q` and the outside path. Then apply it to `p`:
compatibility makes `p` anticomplete to the path, while `p-q` is unrestricted.
This covers no hit, center-only, and either endpoint-only uniformly.

Lean therefore sharpens the path split to

```text
f(G) >= 5
or q is adjacent to at least two vertices of the outside path.
```

The remaining finite patterns are center-plus-one-endpoint,
both-endpoints-without-center, and all three path vertices. They are the exact
next obstruction family for local analysis.

## Lean audit

The complete dependency chain from `GraphConjecture40Baseline` through v26
and `GraphConjecture59PathAttachmentSplit` was rebuilt from source on a fresh
olean path. The independent v19 branch
`GraphConjecture59SynchronizedRows` → `GraphConjecture59FiveTypeAlignment`
was rebuilt against the same fresh base.

Every process completed under the 60-second cap with
`-DwarningAsError=true`. The slowest dependency was
`GraphConjecture59FiveTypeAlignment` at 26 seconds. A final timed rebuild of
the new module completed in 9.42 seconds with exit code 0 and no output.

The source contains no `sorry`, `admit`, `axiom`, or `native_decide`.
