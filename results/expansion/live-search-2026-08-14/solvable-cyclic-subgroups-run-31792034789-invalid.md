# Solvable cyclic-subgroups DEVELOPMENT run 31792034789: INVALID_RUN

- Workflow: `Solvability from cyclic-subgroup count DEVELOPMENT search`
- GitHub Actions run: <https://github.com/Kuberwastaken/c5-k4/actions/runs/31792034789>
- Event: manual `workflow_dispatch`
- Campaign commit: `2619631aea514dcb19e36463dff8a67573b2f2bc`
- Classification: **`INVALID_RUN`**
- Mathematical inference: **none beyond the mandatory S3/A4/A5 sanity gate**

All three jobs reproduced the pinned GAP environment and the exact serialized
sanity values for S3, A4, and the source-documented A5 equality control. Each
job then encountered a longer profile whose permutation-generator field was
wrapped by GAP's formatted stdout. The parser found the marker prefix but
correctly rejected its truncated physical line as `malformed GAP profile
marker`. This is an output-framing defect, not a property of any group.

| Arm | Terminal | Proposed | Exact evaluated | Last admissible statement |
|---|---|---:|---:|---|
| `CATALOGUE` | `WORKER_ERROR` | 2 | 1 | sanity gate passed; no target inference admitted |
| `GENERIC` | `WORKER_ERROR` | 1 | 0 | sanity gate passed; no target inference admitted |
| `WALL_NAVIGATION` | `WORKER_ERROR` | 2 | 1 | sanity A5 row passed; no target inference admitted |

The counter columns above are receipt transcription only. Because output
framing failed, they are not denominators for holds, crossings, coverage, or
search efficacy. In particular, the target-looking A5/SmallGroup row in the
catalogue ledger is not counted separately from the source sanity control.

Artifact attestations returned by the GitHub Actions API:

| Artifact id | Artifact name | Archive SHA-256 |
|---:|---|---|
| `9215883148` | `solvable-cyclic-subgroups-31792034789-1-CATALOGUE` | `fa573fafbcc42e97694e0330187dd1859c6e6d00a8ca7bfbfcc68a1f96d9c37f` |
| `9215878445` | `solvable-cyclic-subgroups-31792034789-1-GENERIC` | `c2d781208d6cdff2c1723cbd335219ebf0ce657fe0b98eb9e0527c8121f3875b` |
| `9215864374` | `solvable-cyclic-subgroups-31792034789-1-WALL_NAVIGATION` | `30a04c2f25930e1661279c96b23016cafad30befaa1e895e1bec28f1da0ad34a` |

The correction disables GAP print formatting before profile emission while
retaining strict one-marker, one-line parsing. A constructor-only regression
test locks the formatting command and independently confirms that a synthetic
wrapped marker remains fail-closed. No target GAP query is needed to validate
the correction locally.
