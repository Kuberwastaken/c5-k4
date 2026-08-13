# Frozen prospective Reed equality-wall trial: complete joins

Frozen: **2026-08-13 UTC**, before evaluating any output graph.

## Exact target

Only the current finite declaration in
`FormalConjectures/Paper/ReedOmegaDeltaChi.lean` is evaluated:

```text
2 chi(G) <= omega(G) + Delta(G) + 2
```

for every finite decidable simple graph.  There are no connectedness,
nontriviality, or minimum-degree hypotheses.

Use signed slack

```text
S(G) = omega(G) + Delta(G) + 2 - 2 chi(G).
```

A negative exact slack is a crossing.

## Frozen operation and prospective prediction

Start only from the odd equality carriers `C5[K_m]`, for
`m in {1,3,5,7}`, and take the complete join with `K_t`, for
`1 <= t <= 12`:

```text
J(m,t) = C5[K_m] join K_t.
```

This is neither a nonuniform blow-up nor an interblob edge surgery.  It is a
global controlled join that preserves finiteness and decidability.

Before evaluation, the predicted coordinate changes are frozen as follows.
For odd `m` the carrier has

```text
chi = (5m+1)/2, omega = 2m, Delta = 3m-1, S = 0.
```

Under join with `K_t`, chromatic and clique numbers should each increase by
`t`.  The new clique vertices should control maximum degree:

```text
chi'   = (5m+1)/2 + t,
omega' = 2m + t,
Delta' = 5m + t - 1,
S'     = 2m.
```

Thus the prospective prediction is deliberately falsifiable but negative:
the operation should leave the equality wall and move exactly `2m` units to
the safe side, independently of `t`.  A different exact delta or a negative
slack falsifies the prediction.

## Database sanity and exactness

Before evaluating joins:

1. compute `chi`, `omega`, and `Delta` exactly on every Graph Atlas graph;
2. cross-check all connected nontrivial Atlas graphs against the finite Reed
   inequality;
3. reproduce equality on odd `C5[K_m]` controls and slack one on even controls
   for `1 <= m <= 6`;
4. evaluate every frozen join by exact DSATUR coloring, exact maximum-clique
   search, and direct degree enumeration;
5. independently replay a coloring certificate and verify the structural
   join formulas for every row.

Every process is capped at 60 seconds.  A timeout is unresolved and cannot be
called a hold.  Every row is appended immediately to
`results/expansion/prospective_reed_complete_join_ledger.jsonl`.

## Status gate

After computation, re-check the current DeepMind declaration and current
research status of Reed's conjecture.  Any crossing requires a separate
source/novelty search before being reported.  No commit, push, issue, PR,
release, or other public action is authorized.

## Verdicts

- `CROSSING_VERIFIED`: an exact negative slack survives all gates.
- `PREDICTION_CONFIRMED`: all 48 joins have exact slack `2m`.
- `HOLD_BOUNDED`: no crossing, but at least one predicted delta differs.
- `INCONCLUSIVE`: an exact computation times out.
- `GATE_FAIL`: the Atlas/control sanity phase fails.
