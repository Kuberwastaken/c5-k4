# OEIS A108569 DEVELOPMENT: frozen odd-support domains exhausted, no counterexample

Date: 2026-08-14 UTC

Status: **VALID FINITE DEVELOPMENT BOUNDED ZERO; NO COUNTEREXAMPLE; NO RELEASE**

Campaign commit: `833896548c702e20af98c979a7bf0f7ba8b40d86`

GitHub Actions run:
[`31830898959`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31830898959)

The two finite odd-support profile domains frozen in advance were exhausted
without finding an odd member of A108569. This is a prospective,
target-specific **DEVELOPMENT** result. It is not held out, does not exhaust
all odd integers or all support patterns, and is not a proof of the full
conjecture.

## Target and literal test

At the frozen `google-deepmind/formal-conjectures` commit
`6c0950bec7743f5098c0196c6aee7b22c1ec8005`, the declaration
`OeisA108569.conjecture` was `research open`. Let

```text
A(k) := 0 < k and phi(k) = phi(k + phi(k)).
```

The source table contains only the odd seed `1`; its other 383 entries are
even lifts. A counterexample required an odd `k>1`, complete ordered prime
factorizations of `k` and `k+phi(k)`, exact equality of their totients,
exclusion from the frozen source table, and a concrete positive enumeration
index supplied through the independently compiled `Nat.count`/`Nat.nth`
bridge. No candidate reached the final two requirements because no profile
survived the earlier algebraic gates.

## Fail-closed refresh

The first dispatch,
[`31830066668`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31830066668),
passed both immutable validators and then stopped in the source/status gate.
Upstream had advanced by one unrelated Barker-sequence file while the A108569
blob remained unchanged. All 48 target jobs were skipped and zero target
profiles were evaluated. The freeze was refreshed to the new complete tree in
commit `8338965`; no search domain or target byte changed.

## Run and independent artifact audit

- The refreshed workflow completed successfully with 51/51 jobs successful at
  the exact campaign commit.
- All 49 expected artifacts were downloaded: one gate and 48 unique worker
  assignments, comprising 391 files.
- All 49 `SHA256SUMS` manifests independently passed, covering 342
  non-manifest files.
- The committed gate verifier independently accepted the source, live-status,
  duplicate-surface, 384-row catalogue, and lift-control bundle.
- All 48 terminal/ledger pairs independently replayed with the committed
  verifier. This checked canonical bytes, hash chains, checkpoint semantics,
  exact profile order, shard ownership, terminal bindings, complete
  frozen-domain exhaustion, and candidate absence.
- Every execution receipt had zero exit codes. There were no worker errors,
  deadlines, candidate files, or certificate files.

The gate-attestation file SHA-256 is
`50517312fd4dbfa31577081a4330df562a14891aaa0a0a49695e1607b9bd9391`;
its embedded self-hash is
`3d4c8aa548db766e9d2fd77d42eb03029e0651fc7bbfbc6f3d62cb9e3d6fc02c`.
The ordered listing of all 48 ledger SHA-256 values hashes to
`2ab03d2d8ff53f56bace9fae317e12cfd9372520f954883b01afbe054fc9d93c`.

## Frozen-domain result

| Arm | Shards | Profiles visited | Per-shard visits | Outcome |
|---|---:|---:|---:|---|
| `ODD_CORE_PROFILES` | 24 | 34,066 | 1,419–1,420 | all `DOMAIN_EXHAUSTED` |
| `ODD_COLLISION_WALL` | 24 | 745,665 | 31,069–31,070 | all `DOMAIN_EXHAUSTED` |

Across 779,731 target profiles:

- 745,665 three-prime profiles had no endpoint profile with the required
  reduced totient ratio;
- 28,169 one- or two-prime profiles had no translated endpoint in the frozen
  catalogue; and
- the remaining 5,897 translated endpoints failed the required support-ratio
  identity.

Thus nothing reached the exponent-lattice or final residual gates. There were
zero source controls in the target domains, zero survivors, and zero
certificates.

This is useful negative method evidence: merely widening the same prime-rank
bands is poorly motivated. Any future A108569 iteration should change the
support/profile geometry—such as a genuinely different higher-support
construction—rather than repeat this finite catalogue at greater scale.

## Source and novelty limits

The live gate verified that the pinned and live Lean files were byte-identical,
replayed all 384 OEIS rows through `(384,997694)`, checked 383 even lifts,
6,511 divisor lifts, and five Sophie-Germain controls, scanned 279 open
upstream pull requests with complete changed-file pagination, and found no
open target-path touch or exact issue, pull-request, or release claim.

Those checks establish the exact bounded source/status/duplicate conditions
required by the frozen contract. They are not a global literature search and
cannot exclude private, unpublished, or differently described work.

Most importantly, `DOMAIN_EXHAUSTED` refers only to the immutable
one-to-three-prime odd-support catalogues and their frozen endpoint catalogue.
It does not cover every odd `k`, support cardinality at least four, unlisted
exponent patterns, or the unbounded conjecture.

No issue, pull request, Lean counterexample theorem, release, tag, or other
publication action follows from this bounded zero.
