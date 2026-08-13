# Frozen prospective trial result: WOWII 198a

## Outcome

**Bounded hold: no crossing found.**

The contract and zero-evaluation ledger were written before candidate-family
evaluation.  The frozen run generated 343 nonisomorphic-by-WL-hash instances
from the fixed blowup and sparse-cut grammar.  Seventy-nine connected
nontraceable survivors received exact evaluation.  None satisfied

`b(G) <= 2 + averageEccentricity(G)`.

The closest member was the claw `K1,3`:

- `n=4`;
- `b=4`;
- eccentricity sum `7`, so `ecc_avg=7/4`;
- cleared inequality: `b*n=16` versus `2*n+sum_ecc=15`.

It misses the hypothesis by exactly `1/4`.

The closest miss was independently recomputed: explicit enumeration of all
vertex permutations found no Hamiltonian path, the whole graph is bipartite
so `b=4`, and its eccentricities are `[1,2,2,2]`.

## Mandatory sanity gate

The evaluator reproduced the expected controls:

| graph | `b` | eccentricity sum/order | traceable | hypothesis |
|---|---:|---:|---|---|
| `P5` | 5 | 16/5 | yes | 25 <= 26 |
| `C5` | 4 | 10/5 | yes | 20 = 20 |
| `K1,3` | 4 | 7/4 | no | 16 > 15 |
| `K3,3` | 6 | 12/6 | yes | 36 > 24 |
| `C5[K4]` | 4 | 40/20 | yes | 80 = 80 |

An independent small-graph database gate evaluated all 995 connected
unlabeled graphs of orders 2 through 7 in NetworkX's graph atlas.  Of these,
144 were nontraceable and none crossed.  The best cleared slack was again
`-1`.

The exact evaluator used subset Hamiltonian-path DP, all-pairs eccentricities,
and minimum-deletion enumeration for the maximum induced bipartite order.  All
inequalities used integer cross-products, not floating point.  Because no
crossing occurred, the contract's second independent recomputation trigger
was not activated.

## Current-status gate

The current DeepMind main-branch file remains tagged `research open` and
contains `sorry`.  However, the live repository also has:

- open issue `#4596`, reporting a candidate mathematical and Lean proof;
- open PR `#4597`, titled “mark Conjecture 198a solved,” linking an exact Lean
  theorem and paper;
- the local WOWII source audit records the historical page as marker `T` on
  July 22, 2026.

Therefore this trial cannot support a novelty or release claim regardless of
its mathematical outcome.  No public action was taken.

## Interpretation

Within the frozen surgery grammar, nontraceability increases `b` faster than
average eccentricity compensates.  Sparse cut joins and block blowups readily
destroy Hamiltonian paths, but they retain large induced bipartite vertex
sets.  The claw is the sharpest observed near miss, consistent with the
small-graph database gate.

This is a negative prospective trial, logged without family expansion or
post-result target changes.

## Reproduction

```text
timeout 60s python3 scripts/method_v41_198a_trial.py
```

The run completed under the cap.  No commit, push, issue, PR, release, or
novelty claim was made.
