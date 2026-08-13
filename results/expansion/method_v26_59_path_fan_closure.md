# Method v26: WOWII #59 complete-fan closure

Date: 2026-08-13

Local certificate: `lean/GraphConjecture59PathFanClosure.lean`

## Main result

The complete core-extension fan from v25 is not a genuine obstruction. The
right exchange is simpler: discard both aligned cores and retain the full
outside path together with `p,q`.

When `q` avoids the outside triple, the five-set has bipartition

```text
left:  the two path endpoints, p
right: the path center, q.
```

Both sides are independent. Each left vertex has at most one neighbor on the
right: the endpoints can only see the path center, while `p` can only see
`q`. Thus the induced graph is a forest. The edge `p-q` is unrestricted and
may be present, exactly as forced by the complete fan.

Equivalently, the witness is the disjoint union of the outside path and the
optional edge `p-q`.

## Improved path split

For every path outside triple under the v21 distinctness and compatibility
data, Lean now proves

```text
f(G) >= 5
or q has a neighbor in the outside triple.
```

Thus the complete core-extension fan from v25 is eliminated completely. Its
forced edges to the aligned cores become irrelevant because the witness omits
both cores.

## Scope and next step

No claim is made yet about the surviving outside-neighbor cases. WOWII #59 is
already externally disproved; this is theorem extraction, not a new
counterexample.

Split the remaining cases by whether `q` hits the path center, one endpoint,
or both endpoints. A center-only hit suggests retaining the endpoint exchange;
endpoint hits require changing the retained pair or exploiting the resulting
four-cycle through an aligned core.

## Lean audit

The certificate was checked on a fresh olean path by rebuilding, in order,
the complete dependency chain from `GraphConjecture40Baseline` through
`GraphConjecture59PathObstructionSplit`, followed by
`GraphConjecture59PathFanClosure`. The independent v19 branch
`GraphConjecture59SynchronizedRows` → `GraphConjecture59FiveTypeAlignment`
was also rebuilt against the same fresh base.

Every individual process completed below the 60-second cap with
`-DwarningAsError=true`. The slowest dependency was
`GraphConjecture59FiveTypeAlignment` at 27 seconds. A final timed rebuild of
the new module completed in 8.44 seconds with exit code 0 and no output.

The source contains no `sorry`, `admit`, `axiom`, or `native_decide`.
