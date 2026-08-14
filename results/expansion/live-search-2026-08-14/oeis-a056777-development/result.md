# OEIS A056777 DEVELOPMENT run result

**Verdict:** valid complete exhaustion of all three frozen finite tuple domains; no counterexample found.

This is a development-only, contamination-aware result. It does not exhaust the
full integer interval or every nonsquarefree/squarefree escape shape, and it is
not a proof of the full A056777 converse.

## Run and audit

- GitHub run: [31818792815](https://github.com/Kuberwastaken/c5-k4/actions/runs/31818792815)
- Frozen commit: `e64fc4f8dc0c09d1f670fd0f72a84cb776d90dee`
- Run conclusion: `success`, 74/74 jobs successful
- Downloaded evidence: 73 artifacts, 581 files
- All 73 artifact `SHA256SUMS` manifests passed.
- The source gate independently passed with attestation SHA-256
  `83a707f4887a2930543ae20779eeb8441f0a4f0bdc55c1484fd7d4b014d2112d`.
- All 72 terminal/ledger pairs independently replayed under separate 60-second
  caps: 72 passed, zero failures or timeouts.
- The run produced 20,411 durable ledger rows covering 2,599,809 constructed
  states. Every terminal reason was `DOMAIN_EXHAUSTED`; there were zero equation
  hits, certificates, worker errors, or nonzero execution statuses.

| Arm | Lanes | States | Per-lane visits | Outcome | Best `[abs(delta K), residual sum]` |
|---|---:|---:|---:|---|---:|
| `PURE_PRIME_POWER` | 24 | 3,970 | 165–166 | all exhausted | `[10008, 182109162712]` |
| `REPEATED_POWER_SURGERY` | 24 | 236,543 | 9,388–10,129 | all exhausted | `[162, 10009036890]` |
| `SQUAREFREE_THREE_BLOCK` | 24 | 2,359,296 | 98,304 | all exhausted | `[4, 20]` |

The exact shard visit arrays and arm-level strict minima are recorded in
`result.json`.

## Closest squarefree-three state

The strongest wall signal was the first tuple of squarefree-three shard 0:

```text
n      = 1000000000002 = 2 * 3 * 166666666667
n + 12 = 1000000000014 = 2 * 3 * 166666666669

phi(n)      = 333333333332
phi(n + 12) = 333333333336
sigma(n)      = 2000000000016
sigma(n + 12) = 2000000000040

R_phi   = phi(n+12) - phi(n) - 12       = -8
R_sigma = sigma(n+12) - sigma(n) - 12   = 12
K(n)      = 333333333344
K(n + 12) = 333333333348
delta K   = 4
```

Thus its strict metric is `[4, 20]`. Both numbers share the structural core
`2*3`; the terminal primes differ by two. This is a near miss, not an A056777
member, because neither defining translation equality holds.

The next distinct retained per-shard squarefree-three minima had first metrics
`192, 192, 200, 512, 624`. Their exact factorizations and signed residuals are
in `result.json`. They are the nearest **recorded lane minima**, not a claim that
the ledgers preserve the global top six individual states.

## Other arm minima

- `REPEATED_POWER_SURGERY`: `n=1005735322561=1549^2*419161`, with
  `n+12=179*31253*179779`, `R_phi=-5004518364`,
  `R_sigma=5004518526`, and `delta K=162`.
- `PURE_PRIME_POWER`: `n=1002702430729=10009^3`, with
  `n+12=11*91154766431`, `R_phi=-91054586360`,
  `R_sigma=91054576352`, and `delta K=-10008`.

No candidate certificate exists because no visited state satisfies both target
equalities.
