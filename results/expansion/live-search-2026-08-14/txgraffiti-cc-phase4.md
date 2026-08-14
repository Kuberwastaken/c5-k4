# TxGraffiti C-C phase four: canonical-domain completion

Date: **2026-08-14 UTC**

Evidence split: **DEVELOPMENT**. This is not held-out Method v1.5 evidence.

Phase four is the operational correction required by
[`txgraffiti-cc-phase3-result.md`](txgraffiti-cc-phase3-result.md). It does not
change the graph family, objective, source reading, exact solver, structural
`mu*(G)=6` certificate, candidate replay, or database-sanity gate. It changes
only how the finite order-20 domain is identified, assigned, resumed, and
declared complete.

The original phase-four contract was frozen before its first target execution.
Constructor counts, source parsing, exact canonicalization, manifest audits,
workflow parsing, and unit tests were its only pre-execution checks.

## Post-failure infrastructure chronology

The first frozen dispatch, GitHub Actions run
[`31788725249`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31788725249),
is **`INVALID_RUN`** and supplies no mathematical evidence. The preparation
runner built nauty with its automatically selected `-march=native` flag and
then uploaded that CPU-specific binary to unrelated runners. Eighteen of the
24 workers passed the database gate but stopped with an illegal-instruction
failure at their first canonicalization. Six workers happened to run on
compatible CPUs, but the independent aggregate runner was incompatible and
could not replay even those ledgers. The aggregate therefore correctly
admitted zero new identities and reported 24 audit errors.

This revision is solely a post-failure infrastructure replay. It does not use
any residual, objective, witness, or apparent zero from run `31788725249` to
alter the target, construction family, identity partition, prior-score set,
or proposal order. No theorem, counterexample, bounded-zero result, or other
mathematical inference may be drawn from that run.

The replay builds nauty with
`--enable-generic --disable-popcnt --disable-clz`, preventing host-specific
instructions from entering the transported binary. Preparation, every exact
worker, and aggregation must each canonicalize the fixed graph6 input `Dhc`
to `DqK` before trusting `labelg`. A failed smoke gate invalidates the run
before mathematical evidence can be admitted.

## Target-blind domain authority

The five frozen order-eight cubic bases and their pairing-orbit representatives
still give exactly 5,320 construction states. A single preparation job:

1. enumerates every state in the frozen SHA-256 order;
2. constructs its connected cubic order-20 graph without evaluating `i(G)`;
3. canonicalizes it with pinned nauty 2.8.9 `labelg`;
4. records the complete state-to-identity map;
5. deduplicates exact canonical identities once; and
6. partitions those identities by `int(canonical_sha256,16) mod 24`.

The domain schema forbids `objective`, `crossing`, `independent_domination`,
and `minimum_maximal_matching`. Its manifest may say `DOMAIN_EXHAUSTED` only
when all 5,320 unique construction keys were scanned, identity multiplicities
sum to 5,320, and the 24 disjoint files exactly cover the canonical identity
set.

## Prior-score subtraction

A separate selector reads only `canonical_sha256` from the three phase-three
scientific ledgers. It never branches on an objective, witness, or residual.
For every identity partition it writes a strictly sorted worklist containing
only identities absent from the prior scored set. The selection audit proves
that prior-scored and unscored identities partition the complete canonical
domain.

Each identity carries one representative construction state. The exact worker
rebuilds that state and independently replays its nauty identity before target
evaluation, preserving the phase-two structural certificate that would be
lost by decoding canonical graph6 alone.

## Exact workers and terminal semantics

There are 24 workers, mapped bijectively onto the existing Method v1.5
`(arm, tree_index)` identities. Every worker:

- reruns the full database-sanity gate before its first target evaluation;
- consumes only its precomputed unscored worklist;
- uses a four-second cap on each exact independent-domination MILP;
- stops internally at 54 seconds;
- runs inside the Method v1.5 60-second process-group cap; and
- durably binds a terminal receipt into its hash-chained ledger.

The receipt distinguishes:

- `DOMAIN_EXHAUSTED`: every worklist identity was evaluated;
- `DEADLINE_PREFIX`: the internal deadline left an explicit next index;
- `SOLVER_INCOMPLETE`: a capped MILP did not prove optimality; and
- `CROSSING_VERIFIED`: a negative residual passed the existing independent
  SAT and structural matching replay.

Normal exit and the old generic `COMPLETED` ledger summary are not evidence of
domain exhaustion. An aggregate may report `DOMAIN_EXHAUSTED_ZERO` only if all
24 receipts say `DOMAIN_EXHAUSTED` and the newly evaluated identities exactly
equal the frozen unscored set. Otherwise a valid zero run is
`BOUNDED_PREFIX_ZERO`; any crossing is `VERIFIED_CROSSING`; missing, overlapping,
or unauthenticated evidence is `INVALID_RUN`.

## GitHub Actions execution

[`txgraffiti-cc-phase4.yml`](../../../.github/workflows/txgraffiti-cc-phase4.yml)
is a manual, read-only workflow pinned to an exact 40-hex campaign commit. It
builds generic-portable nauty 2.8.9 from a SHA-256-pinned source archive,
smoke-tests it at every execution boundary, uploads one immutable
domain artifact, runs the 24 exact partitions with at most eight concurrent
runners, and always attempts a content-addressed aggregate. It has no write
token, release step, AWS dependency, scheduled trigger, or public mutation.

Frozen implementation paths:

- [`txgraffiti-cc-phase4-manifest.json`](txgraffiti-cc-phase4-manifest.json)
- [`../../../scripts/txgraffiti_cc_phase4_domain.py`](../../../scripts/txgraffiti_cc_phase4_domain.py)
- [`../../../scripts/search_txgraffiti_cc_phase4.py`](../../../scripts/search_txgraffiti_cc_phase4.py)
- [`../../../scripts/aggregate_txgraffiti_cc_phase4.py`](../../../scripts/aggregate_txgraffiti_cc_phase4.py)
- [`../../../scripts/test_txgraffiti_cc_phase4.py`](../../../scripts/test_txgraffiti_cc_phase4.py)
- [`../../../scripts/test_txgraffiti_cc_phase4_workflow.py`](../../../scripts/test_txgraffiti_cc_phase4_workflow.py)
