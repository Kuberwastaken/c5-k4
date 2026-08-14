# Solvable cyclic-subgroups DEVELOPMENT run 31792455211: INVALID_RUN

- Workflow: `Solvability from cyclic-subgroup count DEVELOPMENT search`
- GitHub Actions run: <https://github.com/Kuberwastaken/c5-k4/actions/runs/31792455211>
- Event: manual `workflow_dispatch`
- Campaign commit: `1be238c1e6de413b2fd5dce7f9fcbb607ca0cc25`
- Classification: **`INVALID_RUN`**
- Mathematical inference: **none beyond the mandatory S3/A4/A5 sanity gate**

The first framing correction worked for long successful rows: the wall arm
parsed A5, Aut(A5), A6, Aut(A6), and A7. The next frozen descriptor,
`AutomorphismGroup(SimpleGroup("A7"))`, returned process code zero but emitted
no `@@PROFILE@@` marker. The worker converted that one descriptor failure into
whole-arm `WORKER_ERROR`. Its arm-level stdout contained only the Python error,
while the raw GAP stdout/stderr had already been discarded. The preserved
artifact therefore cannot distinguish an unavailable constructor from a GAP
evaluation error. No group-theoretic conclusion follows.

| Arm | Preserved terminal at audit | Receipt-only counters | Admitted mathematics |
|---|---|---|---|
| `WALL_NAVIGATION` | `WORKER_ERROR` at proposed 6, exact-evaluated 5 | A5 through A7 appear as parsed rows | sanity gate only |
| `GENERIC` | `DEADLINE_PREFIX` at next order 355 | proposed/evaluated 4; one order-index timeout | sanity gate only |
| `CATALOGUE` | job exceeded its ten-minute limit during dependency installation; no artifact | none | none |

The table transcribes execution state solely to diagnose the harness. The
successful-looking target rows and terminal prefix are excluded from holds,
crossings, coverage, and method-efficacy denominators because the run is
globally invalid for this DEVELOPMENT decision.

Final artifact attestations available from the GitHub Actions API:

| Artifact id | Artifact name | Archive SHA-256 |
|---:|---|---|
| `9216045346` | `solvable-cyclic-subgroups-31792455211-1-WALL_NAVIGATION` | `386a3c8a00dd358b305b1dd5215b79d40eab57625613247506939c1ae4c6f3db` |
| `9216069156` | `solvable-cyclic-subgroups-31792455211-1-GENERIC` | `a1ab7c17ecf68b3fc3f1c5b18dc5836e01c3874247247183ea0da9943be9db3f` |

The corrected protocol now captures bounded raw stdout and stderr plus return
code for every descriptor. A nonzero exit or missing, duplicate, or malformed
profile becomes a durable `descriptor_error` skip with
`mathematical_inference: NONE`; it increments neither exact evaluations nor
holds/crossings and cannot kill the rest of the frozen arm. Constructor-only
tests exercise missing-marker diagnostics, byte-bounded truncation, durable
ledger emission, and zero scoring without invoking GAP.
