# Private-leaf cone v2: theorem-safe

Date: **2026-08-13 UTC**

Final status: **`THEOREM_SAFE_CONE`**

## Outcome

This fresh v2 trial passed its semantic source/status/prior-art gate before
freezing or evaluating any arithmetic coordinates. The bounded domain then
evaluated all **246,854** frozen quotient rows:

| result | count |
|---|---:|
| even-degree rows | 123,280 |
| odd-degree rows | 123,574 |
| negative residuals | 0 |
| equality rows | 82 |
| minimum residual | 0 |

The deterministic row digest is
`0f7c13e9ffb5763ef4cc01503e29b58a805e9667a188861aa39f24ca0ce48acd`.
An independent nested-loop verifier reproduced every aggregate and the digest.

The first completed evaluator run had a runner-only exit-status bug: it
returned code 2 because a gate-specific check did not recognize the intended
`HOLD_BOUNDED_EXTRACT_THEOREM` status. That run is preserved as nonfinal in
the append-only ledger. After changing only that exit condition, the identical
frozen evaluation exited zero with the same counts and digest.

## Exact analytic explanation

For `q>=2` positive private-leaf counts, write

```text
a=q-1, M=max p_j, T=sum p_j-M.
D=a+M, i=1+T, n=a+1+M+T, T<=aM.
```

The formal right-minus-left residual reduces exactly to

```text
even D: D(D^2-4T),
odd D:  D(D^2-1-4T).
```

The square identity `(a-M)^2>=0` gives `4aM<=(a+M)^2`. In the odd case,
`a+M` odd forces `a!=M`, so the integer square gap is at least one. Since
`T<=aM`, both residuals are nonnegative throughout the entire cone, not only
inside the frozen bounds.

## Lean theorem extraction

[`lean/IndependentDominationPrivateLeafCone.lean`](../../lean/IndependentDominationPrivateLeafCone.lean)
proves the two unbounded arithmetic adapters:

- `independentDominationEven_privateLeafCone`;
- `independentDominationOdd_privateLeafCone`.

They consume the coordinates supplied by the already-proved private-leaf
independent-domination formula. They do not silently claim that an arbitrary
graph has that structure.

The final warning-as-error build was:

```text
timeout 60s lake env lean -DwarningAsError=true \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/IndependentDominationPrivateLeafCone.lean
```

It exited zero. The axiom audit reports only standard Lean/Mathlib foundations;
there is no `sorry`, `admit`, `native_decide`, or custom axiom.

No commit, push, release, issue, pull request, or public action was performed.
