# TxGraffiti C-C phase three: stratified pairing-prefix result

Date: **2026-08-14 UTC**

Evidence split: **DEVELOPMENT**

Final status: **ZERO_BOUNDED_PREFIX**

Phase three applied the order-stratification correction frozen in
[`txgraffiti-cc-phase3.md`](txgraffiti-cc-phase3.md).  The three disjoint
canonical-hash shards evaluated only the equality-bearing coordinate `t=2`,
where every constructed graph is connected cubic on 20 vertices and carries
the structural certificate `mu*(G)=6`.

All three workers stopped cleanly at the 54-second internal deadline.  Their
streams pass the strict Method v1.5 hash-chain and nauty-canonicalization
linter.

## Exact retained denominator

| Shard | Assigned proposals | Canonical exact | `i=6`, residual 0 | `i=5`, residual 1 | Crossing |
|---|---:|---:|---:|---:|---:|
| `CATALOGUE` | 876 | 852 | 734 | 118 | 0 |
| `GENERIC` | 864 | 832 | 726 | 106 | 0 |
| `WALL_NAVIGATION` | 924 | 891 | 775 | 116 | 0 |
| **Total** | **2,664** | **2,575** | **2,235** | **340** | **0** |

No exact row had any other residual.  Equality occupied `86.8%` of the
retained canonical graphs, a substantial concentration improvement over the
larger-coordinate phase-two arms.  No row is a counterexample candidate,
certificate task, release, or novelty claim.

## Conservative coverage classification

The contract contained 5,320 pairing-orbit construction states before final-
graph isomorphism deduplication.  Each worker scanned the common deterministic
state list, canonicalized every visited graph, and admitted only its own hash
shard.  All three summaries were appended at approximately 54.0 seconds.

The current runtime's `COMPLETED` summary means that a worker exited normally;
it does **not** record whether `run_shard` exhausted its finite iterator or
returned at the internal deadline.  Nor does the phase-three recorder count
states assigned to another shard.  Consequently, these ledgers do not prove
that all 5,320 construction states were scanned, even though every retained
row is exact and the three retained class sets are disjoint.

This result is therefore a bounded prefix, not an exhaustive order-20 result.

## Revision forced by the run

The mathematical coordinate is now behaving as intended: the certified
family concentrates overwhelmingly on the target wall.  The next correction
is operational and must be frozen before more target evaluation:

1. precompute a target-blind manifest mapping every construction state to its
   canonical graph identity;
2. deduplicate and partition that manifest once, rather than making all three
   workers canonicalize the same common list;
3. record both `states_scanned` and an explicit `DOMAIN_EXHAUSTED` or
   `DEADLINE_PREFIX` terminal reason; and
4. run exact `i(G)` only on the remaining unscored canonical identities.

This would turn the next pass into an auditable completion attempt without
changing the graph family or mining these residuals for a new proposal rule.

## Artifacts

- [`txgraffiti-cc-phase3-manifest.json`](txgraffiti-cc-phase3-manifest.json)
- [`../../../scripts/search_txgraffiti_cc_phase3.py`](../../../scripts/search_txgraffiti_cc_phase3.py)
- [`txgraffiti-cc-phase3-ledgers/`](txgraffiti-cc-phase3-ledgers/)

Across phases zero through three, the project has retained 2,970 exact graphs
for this target and found no crossing.  This remains finite negative evidence,
not a proof of the conjecture.
