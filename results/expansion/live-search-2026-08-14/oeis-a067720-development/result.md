# OEIS A067720 DEVELOPMENT: frozen profile domains exhausted, no counterexample

Date: 2026-08-14 UTC

Status: **VALID FINITE DEVELOPMENT BOUNDED ZERO; NO COUNTEREXAMPLE; NO RELEASE**

Campaign commit: `ec0ea9cc070072979a08d4da80ffd8cc901311ef`

GitHub Actions run:
[`31825942865`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31825942865)

The two finite composite-successor profile domains frozen in advance were
exhausted without finding a new exact equality. This is a prospective,
target-specific **DEVELOPMENT** result. It is not held out, does not exhaust
all integers or all composite-successor shapes, and is not a proof of the full
conjecture.

## Target and literal test

At the frozen `google-deepmind/formal-conjectures` commit
`05ea0345d09375efac830fac93bf083b654e317e`, the declaration
`OeisA67720.prime_add_one_of_a` was `research open`. With `s=k+1` and
`m=k^2+1`, the search tested the exact residual

```text
R(k) = phi(m) - k*phi(s).
```

A counterexample certificate required `k != 8`, composite `s`, complete
ordered prime factorizations of `s` and `m`, `R(k)=0`, and exclusion from the
frozen 10,000-row OEIS source table. No such certificate was produced.

## Run and independent artifact audit

- The workflow-dispatch run completed successfully with 50/50 jobs successful
  at the exact campaign commit.
- All 49 expected artifacts were downloaded: one gate and 48 unique worker
  assignments, comprising 391 files.
- All 49 `SHA256SUMS` manifests independently passed, covering 342
  non-manifest files.
- The committed gate verifier independently accepted the source, live-status,
  duplicate-surface, and 10,000-row catalogue bundle.
- All 48 terminal/ledger pairs independently replayed with the committed
  verifier. This checked canonical bytes, hash chains, exact profile order,
  shard ownership, terminal bindings, complete frozen-domain exhaustion, and
  candidate absence.
- Every execution receipt had zero exit codes. There were no worker errors,
  candidate files, or certificate files.

The gate-attestation file SHA-256 is
`e671a5687e30c449234637b391d762d6bb8bd6cebd754f8c469250147f705622`;
its embedded self-hash is
`c67abba8a39c2e4b0e1d6cc434f02c4847d5a891943608449d7baede05d924a4`.
The ordered listing of all 48 ledger SHA-256 values hashes to
`c4d56024cbf96d53c9e1857c1d635ea507795a9fce5f7b15d56e30394e6f87a6`.

## Frozen-domain result

| Arm | Shards | Profiles visited | Per-shard visits | Translated profile matches | Outcome |
|---|---:|---:|---:|---:|---|
| `SUCCESSOR_PROFILE_SURGERY` | 24 | 824 | 34–35 | 10 | all `DOMAIN_EXHAUSTED` |
| `TOTIENT_RATIO_WALL` | 24 | 269,943 | 11,247–11,248 | 124 | all `DOMAIN_EXHAUSTED` |

Across 270,767 profiles, 270,633 had no translated endpoint in the frozen
factor catalogue. The remaining 134 translated profile matches comprised one
known-exception control (`k=8`, `R=0`) and 133 nonzero residuals. There were
zero source-catalogue controls and zero survivors. Among the nonzero residuals,
7 were negative and 126 positive.

The three closest non-control residuals were:

- `k=3`: `s=4=2^2`, `m=10=2*5`, `R=-2`;
- `k=5`: `s=6=2*3`, `m=26=2*13`, `R=+2`; and
- `k=9`: `s=10=2*5`, `m=82=2*41`, `R=+4`.

These are diagnostics inside the already frozen domains, not an adaptive
extension and not candidate evidence.

## Source and novelty limits

The gate verified that the pinned and live Lean files were byte-identical at
the run, replayed all 10,000 OEIS b-file rows through `(10000,1548870)`, and
confirmed the single composite-successor table control `(5,8)`. Its fresh
authenticated repository audit scanned 282 open upstream pull requests,
accepted only the two frozen non-resolving target-path maintenance cases
(`#4198` and `#4688`), and found no local exact-search or release match.

Those checks establish the exact bounded source/status/duplicate conditions
required by the frozen contract. They are not a global literature search, do
not establish universal novelty, and cannot exclude unpublished or differently
described prior work.

Most importantly, `DOMAIN_EXHAUSTED` refers only to the two immutable
successor-profile catalogues and their frozen endpoint-factor catalogue. It
does not cover every `k <= 2,000,000,000`, every composite `k+1`, every
factorization of `k^2+1`, or the unbounded conjecture.

No issue, pull request, Lean certificate, release, tag, README claim, or other
publication action follows from this bounded zero.
