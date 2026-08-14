# OEIS A056777 mixed square/triple v2 DEVELOPMENT result

**Verdict:** valid complete exhaustion of both frozen finite tuple domains; no
counterexample found.

This is a development-only, contamination-aware negative result. It exhausts
only the two algebraically indexed mixed square/triple domains specified by the
frozen contract. It does **not** exhaust the integer interval, prove the full
A056777 converse, or create a discovery/release candidate.

## Run and independent audit

- GitHub run: [31822383549](https://github.com/Kuberwastaken/c5-k4/actions/runs/31822383549)
- Frozen commit: `7446588ddfce5b65993f34fbfc53e243a2179427`
- Run conclusion: `success`, 50/50 jobs successful
- Downloaded evidence: 49 artifacts, 389 files
- All 49 artifact `SHA256SUMS` manifests passed.
- The exact-source gate independently passed with gate-file SHA-256
  `41ae3a315824aaa11f877905c6661b92bb81461c4a3eff827c0d4aa639055134`.
- All 48 terminal/ledger pairs independently replayed from the frozen commit,
  each under a separate 60-second cap: 48 passed, zero failures or timeouts.
- Every execution-status code was zero, every terminal reason was
  `DOMAIN_EXHAUSTED`, and there were zero certificates, survivors, worker
  errors, or deadlines.

| Arm | Shards | States | Per-shard visits | Dominant stops | Result |
|---|---:|---:|---:|---|---|
| `REPEATED_LOWER` | 24 | 773,673 | 25,290–39,652 | 508,972 `K_SIGN`; 264,700 `K_NONINTEGRAL` | exhausted |
| `REPEATED_UPPER` | 24 | 773,658 | 25,290–39,651 | 508,959 `K_SIGN`; 264,697 `K_NONINTEGRAL` | exhausted |

The run evaluated 1,547,331 constructed states and wrote 12,160 durable ledger
rows. Only three states passed the sign and integrality gates. None approached
the defining `C_IDENTITY` wall.

## Rare-stop diagnostics

These three states are useful method diagnostics, not candidates:

| Arm/shard | `(r,t,u)` | Derived `(p,q,n)` | Stop | Oriented C-identity gap |
|---|---|---|---|---:|
| lower/14 | `(2731,3217,4637)` | `(301433947,150711851,2248203194380867)` | `BAND` | `-360331510392` |
| upper/0 | `(2659,3529,4007)` | `(489052841,978115435,6915550975887223)` | `BAND` | `1084211280816` |
| upper/6 | `(2857,3863,4231)` | `(4394003,8798479,71817136115059)` | `NONPRIME` | `10431588444` |

For the lower arm the gap is
`r*p+r*(r-1)-((t+u-1)*q+(t*u-t-u+1))`; for the upper arm it is the same
identity oriented as
`(t+u-1)*p+(t*u-t-u+1)-(r*q+r*(r-1))`.

The two out-of-band states also have composite derived partners:

- lower/14: `p=2339*128873`, `q=17*8865403`;
- upper/0: `p=23*21263167`, `q=5*11*17783917`.

The in-band upper/6 state has `p=97^2*467` and `q=421*20899`. Thus merely
widening the value band would not recover a candidate from the two `BAND`
states, and the sole in-band integrality hit fails primality before missing the
C identity by more than ten billion.

The exact per-shard visit arrays, stop counts, source hashes, and diagnostic
records are preserved in `result.json`.
