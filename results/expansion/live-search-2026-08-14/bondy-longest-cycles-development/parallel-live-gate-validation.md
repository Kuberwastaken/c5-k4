# Parallel live-gate validation

This is target-free execution evidence, not mathematical evidence.

- Gate implementation: current uncommitted repair atop
  `ee46d10fefcdfa6e4f6d58d614e86f96e16b97bb`
- External cap: 60 seconds (`TERM`, then `KILL` after 6 seconds)
- Authentication: current GitHub CLI credential, passed only through `GH_TOKEN`
- Primary paper: `/tmp/2606.03696.pdf`, frozen SHA-256 verified
- Target evaluations: `0`

The initial 12-worker validation passed all 14 checks with equal snapshots of
275 open PRs in 56.18 seconds. It was treated as insufficient scheduling
margin; the final recorded validation below uses the frozen 24-worker pool.

## Prior double-scan validation

- Classification: `TARGET_FREE_LIVE_GATE_PASS`
- Exit status: `0`
- Exact elapsed wall time: `55.02` seconds
- Gate status: `PASS`
- Checks: `14/14` true
- Open PR identities with fully paginated changed paths: `275`
- Before/after snapshots equal: yes
- Attestation bytes: `714912`
- `/tmp` attestation SHA-256:
  `2f269735b7023500bbfe6ef1ebfb26bd6cd8100b21b5bc167c828ae772cbfc9e`

## Final bracketed single-scan validation

The current schema was then validated with `GH_TOKEN` exported in the shell
environment (never placed in process arguments, output, or artifacts).

- Schema: `bondy_source_status_duplicate_gate_bracketed_single_scan_v1`
- Classification: `TARGET_FREE_LIVE_GATE_FAIL_CLOSED_UPSTREAM_MAIN_DRIFT`
- Exit status: `1` (expected fail-closed result)
- Exact elapsed wall time: `36.11` seconds
- Gate status: `GATE_FAIL`
- Checks: `15/16` true; only `main_commit` is false
- Frozen main: `5a5af706fa5bef3f09606554d393c9170d2b27e8`
- Observed stable main: `b5acb0ff13e38084105b7fe020ba0d59c1925bc5`
- Open PR identities: `274`
- Fully paginated single-scan file bindings: `274`
- Before/after bracket snapshots equal: yes
- Attestation bytes: `570150`
- `/tmp` attestation SHA-256:
  `1624afaeae286f7e6ad88624dd4efbaa56fda16c2f1f905885491c40499cd0b7`
- Target evaluations: `0`

This validates comfortable runtime margin and fail-closed behavior. It is not
a passing source gate, does not authorize activation, and does not repin the
frozen upstream source.
