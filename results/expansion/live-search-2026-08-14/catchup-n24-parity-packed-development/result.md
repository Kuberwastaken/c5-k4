# Catch-Up N24 parity-packed DEVELOPMENT result

## Disposition

- Research classification: `HOLD_BOUNDED`
- Computational classification: `EXACT_VERIFIED_DRAW`
- Resolution status: `NON_RESOLUTION`
- Release status: `NO_RELEASE`

GitHub Actions run
[`31838019833`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31838019833),
attempt 1, completed successfully. It establishes the exact game value at
`N = 24` as a draw for the frozen Catch-Up encoding. This bounded computation
does not prove or disprove the general upstream conjecture, and it is not a
release result.

## Immutable run identity

- Event and branch: `workflow_dispatch` on `main`
- Head SHA and campaign commit:
  `0c35c4220d6b0ba62b84769ef6658c28de0cb890`
- Created/started: `2026-08-14T20:27:56Z`
- Completed metadata update: `2026-08-14T20:29:11Z`
- Run conclusion: `success`
- Jobs: source/status gate `12s`; frozen-arm validation `13s`; N23 gate
  `20s`; N24 target `31s`; all concluded `success`
- Frozen upstream commit:
  `6c0950bec7743f5098c0196c6aee7b22c1ec8005`
- Frozen upstream tree: `5af0d2a3a319ee2458f8cd061db7c49aeba1b35e`
- Frozen source blob: `ce8251a228ea79a6b2f8414e9eb6b5291a640677`
- Frozen source SHA-256:
  `7e940f2e37a1794e98fc21454096429da13243669a432b9239743aaf46f1d3c0`

## Exact replay

The committed verifier was replayed independently with Python 3.12.13 against
the downloaded ledgers at the exact campaign commit.

| Metric | N23 gate | N24 target |
| --- | ---: | ---: |
| Terminal event | `result` | `result` |
| Exact value | `0` (`draw`) | `0` (`draw`) |
| Verifier classification | `PASS_N23_GATE` | `PASS_EXACT_DRAW` |
| Execution classification | solve `0`, verify `0` | `EXACT_VERIFIED_RESULT`; solve `0`, verify `0` |
| Memo states | 95,451,689 | 199,721,295 |
| Calls | 826,741,149 | 1,845,920,291 |
| Memo bytes | 33,554,432 | 67,108,864 |
| Ledger rows | 97 (1 start, 95 progress, 1 result) | 201 (1 start, 199 progress, 1 result) |
| Ledger time | 8.95436057s | 21.003911s |
| Ledger terminal RSS | 36,412 KiB | 69,208 KiB |
| `/usr/bin/time` user/system | 8.95s / 0.00s | 20.98s / 0.02s |
| `/usr/bin/time` wall | 8.95s | 21.01s |
| `/usr/bin/time` maximum RSS | 36,296 KiB | 69,092 KiB |
| Frozen internal deadline | 38s | 54s |
| External cap | 43s | 60s |
| Stderr bytes | 0 | 0 |

Both terminal rows set `matches_frozen_gate=true` and
`certificate_emitted=false`. No `strategy-dag.jsonl` exists in either
artifact. A complete strategy DAG is required only for a non-draw result; for
an exact draw the committed verifier requires that no DAG bytes be emitted.
Accordingly, there is no DAG to verify, and the absent N24 certificate path
passes `PASS_EXACT_DRAW`.

## Artifact integrity

Every internal `SHA256SUMS` entry verified, and every manifest was exhaustive.

| Artifact | ID | GitHub archive SHA-256 | Size | Checksummed payloads |
| --- | ---: | --- | ---: | ---: |
| `catchup-n24-source-gate-31838019833-1` | 9233211622 | `8ee3b6ac5f7c9d714bef325564a620c3358fcf05079a4703effb042bf0b7cc21` | 18,907 bytes | 11 |
| `catchup-n23-parity-gate-31838019833-1` | 9233222732 | `ba5fbf84e6fe085fe17f87fc77674c37ce6f2bffd02c767e837c17b42988a030` | 25,891 bytes | 7 |
| `catchup-n24-parity-packed-31838019833-1` | 9233237579 | `66e02d500e08f835f1b9b523e6eee72bdee505ed1e1da8a18a223abb96b863b5` | 27,785 bytes | 7 |

The N23 and N24 solver binaries are byte-identical.

## Source and status gate

- `pinned.lean` and `live.lean` are byte-identical, both with SHA-256
  `7e940f2e37a1794e98fc21454096429da13243669a432b9239743aaf46f1d3c0`.
- The required open-research category, theorem name, and one `sorry` occurrence
  are present.
- The eight GitHub search receipts report total counts
  `[1, 4, 3, 0, 0, 0, 0, 0]`.
- Four unique IDs were returned: `{1324, 1325, 4834, 4862}`.
- The frozen semantic filter accepted exactly `{1324, 1325, 4834}`, matching
  `duplicate-ids.txt` and the allowed surface.
- `#4862`, titled `ErdosProblems/973: the answer is no`, was returned by search
  but rejected as irrelevant by the frozen Catch-Up/theorem-name predicate.

The offline reconstruction of the source/status gate passed.

## Provenance hashes

- Committed verifier Git blob:
  `df7fdeb70a0d7fbd962c378b98e3eab3007f2988`
- Committed verifier file SHA-256:
  `af30c4f9c06eb6e10bb765ef54818c4a9e106b8ce64c2b426d8e6ec171543cae`
- Committed solver source SHA-256:
  `19648cd806fcbe5f42ab7ccb1ffbf2690406c0a58fd178b21bfd0336480e6bc3`
- N23 and N24 solver binary SHA-256:
  `8ac6b633d11bf23d1d8024214cbb15cf849be51379c94ce4f73ff746b6db503e`

Final classification: retain this result as `HOLD_BOUNDED` with an
`EXACT_VERIFIED_DRAW` at `N = 24`; it is a `NON_RESOLUTION` and carries
`NO_RELEASE` authorization.
