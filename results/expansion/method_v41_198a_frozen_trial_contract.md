# Frozen prospective trial: WOWII 198a

Frozen: **2026-08-13 UTC, before candidate-family evaluation**

## Target

Current DeepMind declaration:

```lean
G.Connected -> b G <= 2 + averageEccentricity G ->
  exists a b p, p.IsHamiltonian
```

A crossing must be a finite simple connected nontraceable graph satisfying
the real-valued inequality `b(G) <= 2 + ecc_avg(G)` under the exact upstream
definitions.

## Frozen construction grammar

No family outside this list may be introduced during this trial.

1. **Block attachments:** paths of 2--5 blocks, each block `K_s` or `E_s`
   for `1 <= s <= 4`, joined through one identified cut vertex or one complete
   bipartite interface; total order at most 18.
2. **Clique/independent blowups:** blowups of `P_k`, `C_k`, claw, bowtie, and
   barbell skeletons for `3 <= k <= 7`, blob sizes `1..4`, total order at most
   18; each blob is uniformly clique or independent.
3. **Sparse cut joins:** two cliques or two odd-cycle blowups connected by
   one bridge, a length-2/3 handle, or a shared cut vertex; side sizes `2..7`,
   total order at most 18.

Isomorphic duplicates may be removed. No mutation or adaptive enlargement is
allowed after results are seen.

## Frozen ranking and budget

- Reject disconnected and traceable graphs first.
- Rank survivors by slack `2 + ecc_avg - b`, descending, then by order.
- At most 20,000 generated labeled instances and at most 2,000
  nonisomorphic/nontraceable exact evaluations.
- Every subprocess is capped at 60 seconds.

## Mandatory sanity gate

Before any crossing can count:

1. Verify exact current Lean statement and invariant definitions.
2. Check current repository metadata, WOWII source status, and existing issue,
   PR, paper, or known resolution records.
3. Validate the evaluator on named controls with independently known values:
   `P5`, `C5`, `K1,3`, `K3,3`, and `C5[K4]` where feasible.
4. Cross-check Hamiltonian-path detection against an independent algorithm on
   every proposed crossing.

A resolved/claimed target may still receive a bounded formalization audit,
but no novelty or release claim is permitted.

## Exact evaluation rules

- Connectedness: BFS/connected components.
- Traceability: subset dynamic programming for a Hamiltonian path, with a
  second independently implemented endpoint-set DP for any crossing.
- `ecc_avg`: all-pairs shortest paths, stored exactly as integer sum/order.
- `b(G)`: exact maximum induced bipartite subset by subset enumeration with
  two-colorability testing; candidate crossing independently recomputed by a
  separate deletion/odd-cycle-transversal enumeration.
- Compare without floating point:

  `b * n <= 2*n + sum(ecc(v))`.

## Crossing protocol

A candidate survives only if all are recorded:

- graph6 and explicit edge list;
- connected and nontraceable certificates/results;
- exact `b`, eccentricity sum, average, and integer cross-product inequality;
- independent recomputation agrees;
- database/source sanity status is disclosed.

No novelty, release, issue, PR, or public action is authorized in this trial.

