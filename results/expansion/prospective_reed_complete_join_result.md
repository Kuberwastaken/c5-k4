# Prospective Reed equality-wall trial: complete joins

Date: **2026-08-13 UTC**

Verdict: **PREDICTION_CONFIRMED**.  The frozen complete-join operation did not
cross Reed's finite inequality and moved away from equality by exactly the
preregistered amount.

## Exact target

The current DeepMind finite declaration is

```text
2 chi(G) <= omega(G) + Delta(G) + 2.
```

It quantifies over all finite decidable simple graphs and adds no
connectedness or degree hypotheses.  We use slack

```text
S(G) = omega(G) + Delta(G) + 2 - 2 chi(G).
```

## Frozen operation and prediction

Before evaluation, the contract fixed

```text
J(m,t) = C5[K_m] join K_t,
m in {1,3,5,7}, 1 <= t <= 12.
```

This is a global controlled join, not a nonuniform-weight construction or an
interblob edge surgery.  Starting from the odd equality carriers, the frozen
prediction was

```text
chi':   +(t)
omega': +(t)
Delta': 3m-1 -> 5m+t-1
S':     0 -> 2m.
```

## Database and control gate

Exact clique, coloring, and degree evaluation passed all **1,253** Graph
Atlas graphs with no negative slack.  Six uniform controls reproduced the
closed-form parity pattern:

```text
C5[K_m]: S=0 for odd m, S=1 for even m, 1 <= m <= 6.
```

The generic DSATUR implementation initially exhausted its control budget on
the symmetric `C5[K5]`/`C5[K6]` searches while trying equivalent colorings.
Both aborted attempts and their completed rows remain in the append-only
ledger.  The final exact control and discovery path uses a stronger
certificate:

- `alpha(C5[K_m])=2`, so its explicit `ceil(5m/2)` coloring is optimal;
- every joined `K_t` vertex is universal and the `K_t` vertices are pairwise
  adjacent, forcing `t` new colors;
- all color classes are replayed directly against every edge.

This changed only the symmetric solver implementation, not the frozen graph
operation or predicted deltas.

## Discovery result

All **48** frozen joins matched every coordinate exactly:

```text
chi(J(m,t))   = (5m+1)/2 + t,
omega(J(m,t)) = 2m+t,
Delta(J(m,t)) = 5m+t-1,
S(J(m,t))     = 2m.
```

There were zero crossings and zero prediction failures.  Minimum slack was
two at `m=1`; the slack is independent of `t` and grows with carrier blob
size.

`scripts/verify_prospective_reed_complete_join.py` independently reconstructed
all graph6 records, identified the universal joined clique, recomputed carrier
independence/clique numbers, replayed all colorings, derived the chromatic
lower bound, and enumerated degrees.  It passed 48/48 rows.

## Structural diagnosis

The join operation cancels the `+t` changes in `chi` and `omega` only once,
while maximum degree jumps from the carrier value `3m-1` to `5m+t-1` because
each new clique vertex sees the entire carrier.  The uncancelled term is
exactly `2m`.  Complete joins are therefore structurally repelled from the
Reed wall and should be removed from the prospective crossing queue.

## Source and status gate

At local upstream commit `9a1636c4030039f70cf78b866c216d8b6c5f35b0`,
the finite declaration remains `research open`.  GitHub search found only the
merged formalization PR #1264, with no proof/disproof issue or PR.  Current
primary-literature checks still describe Reed's statement as a conjecture and
prove special classes:

- <https://arxiv.org/abs/1205.0730>
- <https://arxiv.org/abs/1205.0731>
- <https://arxiv.org/abs/1611.02063>

No crossing or novelty claim exists, and no public action follows.
