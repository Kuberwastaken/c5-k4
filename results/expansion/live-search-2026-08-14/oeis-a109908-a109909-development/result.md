# OEIS A109908/A109909 finite-prefix result

**Classification:** `BOUNDED_ZERO / DOMAIN_EXHAUSTED`

This completed DEVELOPMENT trial found no shared A109908/A109909
counterexample in its frozen finite-prefix profile domain. This is a bounded
zero for the exact committed search, not a resolution of either conjecture.

## Immutable execution

- Run: <https://github.com/Kuberwastaken/c5-k4/actions/runs/31836896948>
- Run / attempt: `31836896948 / 1`
- Head SHA: `8237b76485e4578a9dbd9a65c4e1e73d8200cfe1`
- `campaign_commit`: `8237b76485e4578a9dbd9a65c4e1e73d8200cfe1`
- Workflow conclusion: `success`
- Gate: `VERIFIED`
- Artifacts: 17 downloaded—one gate and 16 shard bundles; every recorded
  `SHA256SUMS` check passed.

The workflow pinned Python 3.12.9. The unchanged verifier committed at the
campaign SHA was replayed independently against all 16 downloaded shard
bundles under Python 3.12.13. Every replay returned exit code zero in
8.254–8.511 seconds, within the 60-second verification cap. The VPS default
Python 3.9 is not a supported replay environment for this artifact version
because the committed verifier uses `int.bit_count`; that interpreter
compatibility fact does not affect the Python 3.12 workflow or replay result.

## Exact shard outcomes

| Shard | Ledger rows | Terminal | Candidate | Gate/search/verifier |
|---:|---:|---|---|---|
| 0 | 2 | `DOMAIN_EXHAUSTED` | no | `0/0/0` |
| 1 | 2 | `DOMAIN_EXHAUSTED` | no | `0/0/0` |
| 2 | 1 | `DOMAIN_EXHAUSTED` | no | `0/0/0` |
| 3 | 1 | `DOMAIN_EXHAUSTED` | no | `0/0/0` |
| 4 | 2 | `DOMAIN_EXHAUSTED` | no | `0/0/0` |
| 5 | 1 | `DOMAIN_EXHAUSTED` | no | `0/0/0` |
| 6 | 1 | `DOMAIN_EXHAUSTED` | no | `0/0/0` |
| 7 | 2 | `DOMAIN_EXHAUSTED` | no | `0/0/0` |
| 8 | 1 | `DOMAIN_EXHAUSTED` | no | `0/0/0` |
| 9 | 1 | `DOMAIN_EXHAUSTED` | no | `0/0/0` |
| 10 | 2 | `DOMAIN_EXHAUSTED` | no | `0/0/0` |
| 11 | 1 | `DOMAIN_EXHAUSTED` | no | `0/0/0` |
| 12 | 1 | `DOMAIN_EXHAUSTED` | no | `0/0/0` |
| 13 | 0 | `DOMAIN_EXHAUSTED` | no | `0/0/0` |
| 14 | 2 | `DOMAIN_EXHAUSTED` | no | `0/0/0` |
| 15 | 2 | `DOMAIN_EXHAUSTED` | no | `0/0/0` |

All 16 terminals and all 22 ledger rows replayed successfully. The ledger
contains 15 `COMPOSITE_ESCAPE` and 7 `PRIME_ESCAPE` outcomes. It contains zero
`CAP_PREFIX`, `FULL_COVER`, or `WORKER_ERROR` outcomes. There are zero
candidates, worker errors, and reached search or verification deadlines.

The 22 visited values range from `n=1,014,990,500` through
`n=1,461,176,240`. Their first uncovered representatives range from `k=66`
through `k=96`. These diagnostics explain the bounded zero: every visited
profile escaped before completing the required half-interval cover.

## Standing

The frozen 16-shard profile domain is exhausted. No counterexample certificate
was emitted, so neither A109908 nor A109909 is disproved or proved by this run.
The result authorizes no release or novelty claim.
