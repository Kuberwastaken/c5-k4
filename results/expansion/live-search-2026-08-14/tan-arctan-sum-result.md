# Tan-arctan-sum development search: bounded zero

Date: 2026-08-14 UTC

Status: **BOUNDED ZERO; NO COUNTEREXAMPLE; NO RELEASE**

Frozen campaign commit: `5496aa36a17feebf3377406db1a2f2aeadbc91cb`

GitHub Actions run:
[`31790686819`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31790686819)

Target pin: `google-deepmind/formal-conjectures` commit
`942fb149e782a56c2719c543ab58e093f733acb4`, declaration
`Arxiv.«2607.05739».tan_arctan_sum_not_integer`.

All three frozen jobs passed the pre-target sanity gate and finished with
valid terminal receipts. Independent audit reproduced every artifact checksum,
every JSONL row hash and link, every terminal final-row binding, and every
recorded exact recurrence, norm, wall-membership, sample-membership, reduced
denominator, counter, and cursor claim.

| Arm | Preserved range/domain | Exact divisibility tests | Terminal | Integral values |
|---|---|---:|---|---:|
| catalogue | all 12 paper exceptional indices through `44088` | 12 | `DOMAIN_EXHAUSTED` | 0 |
| generic | complete selected non-wall sample through `n=60980` | 73 | `DEADLINE_PREFIX` | 0 |
| wall navigation | every index `60001 <= n <= 155802` | 0 | `DEADLINE_PREFIX` | 0 |
| **total** | two prefixes plus one exhausted catalogue | **85** | **3 receipts** | **0** |

The wall worker's zero tests are substantive bookkeeping rather than missing
evaluation: independent recurrence found no index satisfying its exact wall
predicate anywhere in its preserved range. The generic worker evaluated all
73 deterministically selected non-wall indices in its prefix (from `60039` to
`60980`). Every one had reduced denominator greater than one. The catalogue
worker independently reproduced the twelve frozen indices
`15,17,80,82,395,397,1904,1906,9163,9165,44086,44088`; all were nonintegral.

This is not domain exhaustion for the conjecture. Both post-paper arms stopped
at their 54-second deadlines, far below the frozen maximum `250000`, so the
result certifies only the recorded finite prefixes.

Method implication: replaying the exact Gaussian product from the origin makes
large-integer state growth the dominant cost, while the exceptional-wall arm
found no proposals in a long prefix. Another volume-only replay is therefore
low-information. A next version should first derive exact modular or norm
filters and use independently certified restart states to shard later ranges;
full integer reconstruction should be reserved for surviving divisibility
candidates.

The frozen inputs and certificate contract remain in
[`tan-arctan-sum-contract.md`](tan-arctan-sum-contract.md) and
[`tan-arctan-sum-manifest.json`](tan-arctan-sum-manifest.json).
