# Solvability from cyclic-subgroup count: bounded development zero

Date: 2026-08-14 UTC

Status: **BOUNDED ZERO; NO COUNTEREXAMPLE; NO RELEASE**

Frozen campaign commit: `61f49a75974657304a8f2210171941bd1c8bdedf`

GitHub Actions run:
[`31793242351`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31793242351)

Target pin: `google-deepmind/formal-conjectures` commit
`942fb149e782a56c2719c543ab58e093f733acb4`, blob
`cb099f09a40eab0149b3332979d92e190ef44def`, declaration
`Arxiv.«2604.08040».solvable_of_cyc_lt`.

The pinned blob and its current-main copy both retain
`@[category research open, AMS 20]`. Its Git blob hash and independent file
SHA-256 (`26669f9461c5c65d8bd69469825057a2210eebee05f2e3a0ff3fedcfb57fc28a`)
match the frozen source/status attestation. Issue `#4844` was closed by the
statement-formalization merge, not by a mathematical resolution.

All three jobs reproduced the mandatory `S3`, `A4`, and `A5` sanity profiles
before target evaluation. Independent artifact audit then reproduced all three
`SHA256SUMS` manifests, all 82 canonical JSONL row hashes and predecessor
links, all three terminal final-row bindings, and all counters and cursors.
Full integer replay of every recorded element-order histogram checked

```text
cyc(G) = sum_d count(elements of order d) / phi(d),
R(G)   = cyc(G) - 2^(pi(G)+2).
```

Each histogram population summed to the recorded group order, every summand
was integral, and every recorded threshold, residual, and crossing Boolean
recomputed exactly. This covered 65 scored nonsolvable target rows and the
nine separately recorded sanity-control profiles. No local GAP installation
was available for a second subgroup-conjugacy-class enumeration, so this audit
uses the contract's independent exact-histogram route rather than claiming a
second GAP algorithm.

| Arm | Preserved scope | Proposed | Exactly scored | Excluded | Terminal | Crossings |
|---|---|---:|---:|---:|---|---:|
| catalogue | complete order-index prefix `60..137`; order `138` index timed out | 4 | 4 | 1 order-index timeout | `DEADLINE_PREFIX` | 0 |
| generic | complete deterministic order-index prefix `256..335`; order `336` index timed out | 1 | 1 | 1 order-index timeout | `DEADLINE_PREFIX` | 0 |
| wall navigation | all 63 frozen descriptors attempted in exact frozen order | 63 | 60 | 2 descriptor errors, 1 evaluation timeout | `SEARCH_EXHAUSTED` | 0 |
| **total** | two prefixes plus one exhausted descriptor schedule | **68** | **65** | **5 non-scoring events** | **3 receipts** | **0** |

The total proposed column counts target group descriptors, so the two
order-index timeouts are listed as exclusions but are not proposals. Every one
of the 65 successfully parsed target profiles was nonsolvable. The catalogue
residuals were `0,17,35,32`; the generic residual was `50`; and the wall
residuals ranged from `0` to `348692`. Exact equality occurred only at `A5`,
`A5 x C7`, and `A5 x C11` in the wall arm (and at the catalogue copy of `A5`).
No residual was negative, so no primary candidate or certificate file exists.

The wall terminal means that the frozen *descriptor schedule* was consumed,
not that all 63 descriptors produced mathematical values. `Aut_A7` and
`Aut_A8` returned no complete profile because the pinned GAP installation
lacked the required `TransitiveGroupsAvailable` path; their durable rows say
`mathematical_inference: NONE`. `A5 x C13` hit its per-query/deadline allowance.
Those three records incremented neither exact evaluations nor objective scores
and are not holds. Likewise, the order-index timeouts at `138` and `336` are
not statements about any group at those orders.

Method implication: the simple-socle and automorphism-endpoint replacements
that evaluated successfully mostly move decisively to the safe side of the
wall, while the coprime `A5` products preserve equality in the two completed
cases. More undirected volume in the same schedule is therefore
low-information. A useful next iteration should (1) repair the two
representation/package gaps and replay the three non-scoring descriptors,
and (2) derive a structural operation that can lower
`cyc(G) / 2^pi(G)` below the `A5` equality wall before spending further search
budget. The catalogue and generic arms also need sharded/restartable order
indexes if broader finite coverage is desired.

The frozen contract, manifest, and source/status attestation remain in
[`solvable-cyclic-subgroups-contract.md`](solvable-cyclic-subgroups-contract.md),
[`solvable-cyclic-subgroups-manifest.json`](solvable-cyclic-subgroups-manifest.json),
and
[`solvable-cyclic-subgroups-source-status.json`](solvable-cyclic-subgroups-source-status.json).
