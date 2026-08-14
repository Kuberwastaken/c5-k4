# Graffiti³ Conjecture 23: exact bounded zero on all three frozen arms

Date: 2026-08-14 UTC

Status: **BOUNDED ZERO; NO COUNTEREXAMPLE; NO RELEASE**

Authoritative campaign commit: `3c60bc6f438127782c43e2cbf64dbed927235ed4`

Authoritative GitHub Actions run:
[`31797089374`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31797089374)

Target: Graffiti³ Conjecture 23, Research Square version 1, DOI
[`10.21203/rs.3.rs-8493329/v1`](https://doi.org/10.21203/rs.3.rs-8493329/v1).
For a finite p-group, the conjecture is the integer inequality

```text
W(G) = 2|G/G'| + |G| + 2|Z(G)| - 4k(G) >= 0.
```

This is a source-listed open Graffiti³ statement. It is not a DeepMind or
Written on the Wall I target.

## Independent evidence audit

The run completed successfully at the exact detached commit above. Independent
replay verified the complete set of 73 artifacts: one shared database-gate
preparation and the Cartesian product of three frozen arms with shards `0..23`,
72 unique worker assignments with no missing or duplicate pair.

The replay verified:

- all 73 `SHA256SUMS` manifests, covering 433 artifact files;
- the gate file SHA-256
  `51cbc755618817a15afaa8db06e2094284b93107391747ef53ce66bc6f7246d0`;
- the unsigned canonical preparation hash
  `0174a162d18f1473f4f51c8bc80f4ed38daa42d542bc97409ed31dd9d235ce35`;
- the frozen-manifest binding
  `b2bab5054fdeb0861027fdc2079183b64cd59ead68530889e5e94144425d091a`,
  source-PDF binding, exact campaign binding, all 96 chunk bindings, and the
  ordered 2,732-coordinate and residual hashes;
- all 4,574 canonical ledger rows, predecessor links, row hashes, 72 ledger
  file hashes, terminal final-row/final-sequence/counter bindings, and 72
  execution-status documents with all postprocessing exit codes zero;
- the exact frozen contiguous catalogue prefixes, deterministic generic hash
  prefixes, and complete wall-descriptor assignment and sharding;
- all 4,315 exact profiles by recomputing abelianization order and the integer
  residual from `|G|`, `|G'|`, `|Z(G)|`, and `k(G)`; and
- every wall profile independently from its descriptor, binary ranks,
  conjugacy-class count, and residual.

The shared gate exhausts the frozen source snapshot: the trivial group and all
prime-power-order SmallGroups through order 128. Its 2,732 exact residuals have
zero negatives and 558 equalities, including `W(D8)=W(Q8)=0`. This is finite
snapshot evidence, not a proof beyond that snapshot.

## Authoritative arm dispositions

| Arm | Proposed | Exact | Timeouts | Malformed | Minimum | Equalities | Terminals | Disposition |
|---|---:|---:|---:|---:|---:|---:|---|---|
| catalogue, order 256 | 2,092 | 2,070 | 22 | 0 | `W=0` | 12 | 24 `DEADLINE_PREFIX` | exact bounded prefix zero |
| generic, order 512 | 2,164 | 2,143 | 21 | 0 | `W=32` | 0 | 24 `DEADLINE_PREFIX` | exact bounded hash-prefix zero |
| wall navigation | 102 | 102 | 0 | 0 | `W=52` | 0 | 24 `DOMAIN_EXHAUSTED` | frozen family exhausted zero |

Totals: 4,358 proposals, 4,315 exact profiles, 43 separately capped query
timeouts, zero malformed rows, zero negative residuals, zero crossings, zero
candidates, and zero certificates. A timed-out proposal is unevaluated and
carries no inference; the bounded-zero claim covers only the 4,315 exact rows.

The catalogue assignments replay as the first frozen contiguous prefix in each
of the 24 disjoint `SmallGroup(256,id)` intervals. The generic assignments
replay as the first unique deterministic SHA-256 sample prefix in each shard.
Neither arm exhausts its full order layer. Their exact residual ranges are:

- catalogue: `0 <= W <= 256`, with 12 equality rows;
- generic: `32 <= W <= 400`, with no equality row.

The wall arm does exhaust its specified descriptor domain. Independent
enumeration reproduced all 24 surjective assignments in dimension 6 and all 78
in dimension 8, each exactly once in its SHA-256 shard:

| Dimension | Profiles | Exact residual distribution |
|---|---:|---|
| 6 (`|G|=256`) | 24 | `W=52` for 18; `W=88` for 6 |
| 8 (`|G|=1024`) | 78 | `W=244` for 24; `W=388` for 18; `W=424` for 36 |

Thus none of the exact frozen rows refutes Conjecture 23. This is not finite
p-group domain exhaustion and is not evidence that the conjecture is true.

## Correction history

Run
[`31796237073`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31796237073)
validated the shared source gate and the 102 wall descriptors, but its
catalogue and generic GAP queries used top-level global variables and produced
no profile markers. Those two arms were correctly recorded as
`INVALID_NO_INFERENCE`. The evaluator was changed to function-local GAP
framing, bounded output-tail diagnostics were added, and all three arms were
rerun from their frozen beginnings. Run `31797089374` is the sole authoritative
result; no counts are aggregated across the correction run.

Frozen scope and source/status details remain in
[`graffiti3-conjecture23-contract.md`](graffiti3-conjecture23-contract.md),
[`graffiti3-conjecture23-manifest.json`](graffiti3-conjecture23-manifest.json),
and
[`graffiti3-conjecture23-source-status.md`](graffiti3-conjecture23-source-status.md).
