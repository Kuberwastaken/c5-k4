# OEIS A105720 DEVELOPMENT: all frozen finite domains exhausted, no extra square

Date: 2026-08-14 UTC

Status: **FINITE DEVELOPMENT BOUNDED ZERO; NO CANDIDATE; NO RELEASE**

Campaign commit: `9946c3a1707d72991a0e74dd286586919a8a47ff`

GitHub Actions run:
[`31799206901`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31799206901)

This is a target-specific **DEVELOPMENT finite-search comparator**. It is not
wall-navigation method evidence. The operational arm name `WALL_NAVIGATION`
denotes an ordered interval plus a lossless square-residue screen, not an
invariant-separating family.

## Target and frozen meaning

At the frozen `google-deepmind/formal-conjectures` commit
`942fb149e782a56c2719c543ab58e093f733acb4`, the research-open declaration
`OeisA105720.conjecture` states that, for positive `n`, the sum of the one-based
primes `p_n` through `p_(2n)` is square exactly at `n = 3`, `6`, or `4072`.
A crossing requires a square at a positive index outside that known set.

The run found no such index. It recovered the in-domain published control

```text
n = 4072,  a(n) = 247590225 = 15735^2,
```

and emitted no candidate certificate.

## Independent evidence audit

Independent replay verified:

- the successful run head and all 73 artifact identities at the exact campaign
  commit, with no missing, duplicate, expired, or foreign-run artifact;
- all 73 `SHA256SUMS` manifests, covering 510 artifact files;
- both committed gate verifiers, followed by an independent reconstruction of
  all 500,040 primes through the last prime `7,369,291`;
- the immutable Lean source SHA-256
  `2ee734da9e2c90fefaa889b5d3eedd4c48bff96cffe24f5b478c593466bcbdf8`
  and Git blob `c5f760ccfa563547224b6140ea8aa64eed03977e`;
- the OEIS b-file SHA-256
  `b89ca17a684da7b6200d0e862409269ef51d5d7e0ac9a2da2958eee64cfe7e4d`,
  its exact 1,000-row extent, and every frozen source/prime control;
- the gate-attestation SHA-256
  `915e7cbd74e4b2c2d065d5770ece44e506933c0837d480396d2ccf27d85aedee`,
  prime-table SHA-256
  `27c9dc8386a16dee3ef365bd281c2864929c518582292d5dc2e261e2b702b3bd`,
  manifest SHA-256
  `22d935a9bf4c0ebc8082dd64879dcdf2ef002e62363b72d7a824cacf33127976`,
  source/status attestation, file set, and campaign binding;
- exactly three arms by 24 shards, all 72 assignments complete and unique;
- all 216,000 ledger rows, canonical row hashes and predecessor links, exact
  arm/shard/campaign/source/gate bindings, domain order, and arithmetic;
- all 72 terminal-to-ledger hashes, final rows, row counts, screening counters,
  `DOMAIN_EXHAUSTED` claims, and execution-status receipts with every gate,
  search, terminal, and certificate-verifier exit code zero; and
- absence of worker-error rows and candidate files.

For every ledger row the audit independently reconstructed `a(n)` from the
prime prefix sums, the frozen residue-screen decision, the exact-square bit,
and the nearest-square distance. The affine generic domain was independently
regenerated and shown to contain 96,000 distinct points. All three arm domains
are pairwise disjoint.

## Authoritative arm totals

| Arm | Frozen domain | Screened | Passed screen / exact-tested | Screen-rejected | Extra squares | Terminals | Disposition |
|---|---:|---:|---:|---:|---:|---|---|
| `CATALOGUE` | every `n` in `[21,20020]` | 20,000 | 20,000 | 0 | 0 | 24 `DOMAIN_EXHAUSTED` | domain exhausted |
| `WALL_NAVIGATION` | every `n` in `[20021,120020]` | 100,000 | 793 | 99,207 | 0 | 24 `DOMAIN_EXHAUSTED` | domain exhausted |
| `GENERIC` | 96,000 frozen affine-permutation points in `[120021,250020]` | 96,000 | 96,000 | 0 | 0 | 24 `DOMAIN_EXHAUSTED` | selected domain exhausted |

Totals: 216,000 screened rows, 116,793 screen-compatible exact-square tests,
99,207 lossless residue-screen rejections, one known exact-square control,
zero extra squares, zero crossings, and zero certificates.

The residue filter uses squares modulo `64`, `63`, `65`, and `11`. Independent
constructor tests establish that an integer square cannot fail this screen;
therefore the 99,207 rejected rows are exact nonsquare certificates for this
finite computation, not heuristic omissions. The 793 compatible rows were
checked by integer square root and none was square.

## Scope

The bounded zero applies exactly to the three frozen finite domains above. The
generic arm does not cover every index in its enclosing interval, and the run
does not prove the OEIS conjecture for all positive integers. No issue, pull
request, Lean certificate, release, or README claim follows from this zero.

The frozen source, status, domains, caps, and execution discipline are recorded
in [`CONTRACT.md`](CONTRACT.md), [`manifest.json`](manifest.json), and
[`source-status-attestation.json`](source-status-attestation.json).
