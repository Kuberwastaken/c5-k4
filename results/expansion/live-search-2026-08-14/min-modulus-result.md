# Minimum-modulus development search: bounded zero

Date: 2026-08-14 UTC

Status: **BOUNDED ZERO; NO COUNTEREXAMPLE; NO RELEASE**

Frozen campaign commit: `200de6f3c7bd136db2c3fa4c6c42f124218c2d03`

GitHub Actions run:
[`31788882575`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31788882575)

Target pin: `google-deepmind/formal-conjectures` commit
`942fb149e782a56c2719c543ab58e093f733acb4`, declaration
`Arxiv.2607.08366.min_modulus`.

The frozen exact search completed all 24 isolated jobs successfully. Every job
passed the database-sanity gate and wrote a terminal receipt bound to its
hash-chained ledger. All 24 artifact checksum manifests, all ledger chains,
and all terminal final-row bindings replay independently.

| Arm | Proposed | Canonical unique | Exact scored | Terminal receipts | Crossings |
|---|---:|---:|---:|---|---:|
| catalogue | 258,953 | 4,686 | 4,686 | 8 `DEADLINE_PREFIX` | 0 |
| generic | 18,998 | 18,949 | 18,949 | 8 `DEADLINE_PREFIX` | 0 |
| wall navigation | 30,916 | 30,916 | 30,042 | 3 `SEARCH_EXHAUSTED`, 5 `DEADLINE_PREFIX` | 0 |
| **total** | **308,867** | **54,551** | **53,677** | **24** | **0** |

The 874 wall states not scored by the target were boundary or otherwise failed
the literal sub-threshold hypotheses; they are not candidate evaluations. The
three exhausted wall shards cover their assigned frozen `n` coordinates only.
No catalogue shard exhausted its full finite range, and no generic shard
reached its proposal ceiling, so this result is a bounded zero rather than a
proof of the universal conjecture.

Method implication: the current one/two-residue substitutions around the
proved super-increasing construction did not cross the optimality wall. A
future version should alter several residues coherently or use a constraint
solver over collision classes; merely extending these deadline prefixes would
measure volume, not introduce a new structural degree of freedom.

The frozen inputs and certificate contract remain in
[`min-modulus-contract.md`](min-modulus-contract.md) and
[`min-modulus-manifest.json`](min-modulus-manifest.json).
