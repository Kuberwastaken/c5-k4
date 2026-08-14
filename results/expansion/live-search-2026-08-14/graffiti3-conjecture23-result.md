# Graffiti³ Conjecture 23: wall-family bounded zero; GAP arms invalid

Date: 2026-08-14 UTC

Status: **PARTIAL BOUNDED ZERO; TWO INVALID ARMS; NO COUNTEREXAMPLE; NO RELEASE**

Frozen campaign commit: `f8bd3ac25d4864fcabd0f35ed5ba5cd4ec1f8576`

GitHub Actions run:
[`31796237073`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31796237073)

Target: Graffiti³ Conjecture 23, Research Square version 1, DOI
[`10.21203/rs.3.rs-8493329/v1`](https://doi.org/10.21203/rs.3.rs-8493329/v1).
For a finite p-group, the conjecture is the integer inequality

```text
W(G) = 2|G/G'| + |G| + 2|Z(G)| - 4k(G) >= 0.
```

This is a source-listed open Graffiti³ statement. It is not a DeepMind or
Written on the Wall I target.

## Independent evidence audit

The workflow input, run head, detached checkout, preparation binding, every
worker ledger, terminal, and execution-status document all name the same exact
commit `f8bd3ac25d4864fcabd0f35ed5ba5cd4ec1f8576`. The complete assignment set is
exactly the Cartesian product of three frozen arms, shards `0..23`: 72 unique
assignments with no missing or duplicate pair. Every execution-status document
records search, terminal-validation, and certificate-verifier exit code zero.

Independent replay verified:

- the shared preparation artifact's `SHA256SUMS` and all 72 worker
  `SHA256SUMS` files (73 checksum manifests total);
- the preparation file SHA-256
  `14d7d5f4e563b708d7ce7af485423d37af939cabc0f4b74e2485d6da97d0d5d1`
  and unsigned canonical preparation hash
  `abfe2e18eabc341cd81535ce03f7a6f5c74961aebf7fe8a4951de6c4114dbba2`;
- the manifest binding
  `b8ba29601a8e4a604f8e08e7408cb761fc625a6775b3f381cc13373988c5290f`,
  source-PDF binding, exact 2,732-coordinate order, full-row hash, and all 96
  independently rebuilt chunk counts, coordinate hashes, and row hashes;
- all 4,795 canonical ledger rows, predecessor links, 72 ledger-file hashes,
  final-row hashes, final sequences, terminal counters, and execution-status
  bindings;
- every exact target profile's abelianization and integer residual; and
- every wall descriptor, shard assignment, binary-rank profile, conjugacy-class
  count, and residual from the frozen construction itself.

The shared gate exhausts the frozen source snapshot: the trivial group and all
prime-power-order SmallGroups through order 128. Its 2,732 residual rows have
zero negatives and 558 equalities, including `W(D8)=W(Q8)=0`. This is exact
finite snapshot evidence, not a proof beyond the snapshot.

## Arm dispositions

| Arm | Proposed | Exact profiles | Malformed | Timeouts | Terminals | Disposition |
|---|---:|---:|---:|---:|---|---|
| catalogue, order 256 | 2,292 | 0 | 2,271 | 21 | 24 `DEADLINE_PREFIX` | **INVALID / NO INFERENCE** |
| generic, order 512 | 2,185 | 0 | 2,163 | 22 | 24 `DEADLINE_PREFIX` | **INVALID / NO INFERENCE** |
| wall navigation | 102 | 102 | 0 | 0 | 24 `DOMAIN_EXHAUSTED` | **BOUNDED ZERO** |

The catalogue and generic coordinates replay exactly as the frozen contiguous
per-shard prefixes and deterministic hash samples. But every non-timeout GAP
proposal ended as `expected one @@PROFILE@@ marker`; none became an exact
profile. The ledger intentionally labels each such row
`mathematical_inference: NONE`. Raw per-query GAP diagnostics were not retained,
so the systematic marker failure cannot be diagnosed more narrowly from these
artifacts. Workflow success means that the fail-closed receipts were preserved
and validated; it does **not** turn these two arms into bounded holds. They
provide no evidence for or against any order-256 or order-512 group.

The wall arm is valid. Independent enumeration reproduced all 24 surjective
assignments in dimension 6 and all 78 in dimension 8, each exactly once in its
SHA-256 shard. All 102 groups have `|G'|=|Z(G)|=4`; no residual is negative:

| Dimension | Profiles | Exact residual distribution |
|---|---:|---|
| 6 (`|G|=256`) | 24 | `W=52` for 18; `W=88` for 6 |
| 8 (`|G|=1024`) | 78 | `W=244` for 24; `W=388` for 18; `W=424` for 36 |

Thus the frozen commutator-image lift family is exhausted with minimum
`W=52`, zero crossings, zero candidates, and zero certificates. This proves
only that these 102 purpose-built lifts do not refute Conjecture 23. It is not
finite p-group domain exhaustion and not evidence that the conjecture is true.

## Method implication

The prospective move from the extraspecial equality wall did change the
intended coordinate, but not in the predicted direction strongly enough: all
surjective order-four commutator-image lifts moved a positive distance to the
safe side. That is useful negative feedback. A next wall construction needs to
preserve more conjugacy classes relative to the derived-subgroup penalty, not
merely enlarge the commutator image. Separately, the GAP target evaluator must
retain bounded stdout/stderr and pass a known order-256 control before any
catalogue or generic rerun; increasing shard volume before repairing that
profile path would produce more no-inference rows.

Frozen scope and source/status details remain in
[`graffiti3-conjecture23-contract.md`](graffiti3-conjecture23-contract.md),
[`graffiti3-conjecture23-manifest.json`](graffiti3-conjecture23-manifest.json),
and
[`graffiti3-conjecture23-source-status.md`](graffiti3-conjecture23-source-status.md).
