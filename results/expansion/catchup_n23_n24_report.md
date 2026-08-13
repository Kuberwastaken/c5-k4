# Catch-Up exact N=23,24 workflow result

**Primary outcomes:** `N=23 HOLD_BOUNDED`; `N=24 TIMEOUT_BRACKET`  
**Successful workflow:** [run 31721869656](https://github.com/Kuberwastaken/c5-k4/actions/runs/31721869656)  
**Frozen source:** `google-deepmind/formal-conjectures@7a38c469ec329d0c97c068e03c58834f61628e7e`

The exact source range through `N=20` first replayed successfully. The two
development rows then ran in isolated GitHub-hosted jobs with identical pinned
source, contract, card, compiler flags, solver semantics, and 60-second caps.

## Exact outcomes

| N | result | memo states | calls | wall time | last/final solver RSS |
|---:|---|---:|---:|---:|---:|
| 23 | exact draw | 95,451,689 | 826,741,149 | 50.786 s | 2,379,368 KiB |
| 24 | unresolved timeout | at least 112,000,000 | at least 985,908,066 | 60.000 s cap | 2,395,756 KiB |

The external resource recorder observed a peak RSS of 3,558,716 KiB for
`N=23` and 3,575,100 KiB for `N=24`; the higher figures include transient
flat-table rehash allocation. `N=23` exited zero with value draw. `N=24`
exited 124 under the external timeout and emitted no result row, so it remains
unknown.

The raw incremental JSONL and `/usr/bin/time -v` records are committed without
normalization:

- `catchup_n23_workflow_raw.jsonl`, SHA-256
  `d4169059292c8798db81f236d23f20b81370123d6dc2dce4a2c60ef7a74a5b7f`;
- `catchup_n24_workflow_raw.jsonl`, SHA-256
  `19ddce33e5b3b99e7cb80206a7fa33b8ab0e484ae6d9c20731d365d7218b0db0`;
- `catchup_n23_resources.txt`, SHA-256
  `fdef10d94656d537bb043559fff4205123f942b5a3d5743723b430b2658addb1`;
- `catchup_n24_resources.txt`, SHA-256
  `02b8fcac006367170deeb2c807d7cd344a5b8b01e695f8f36ace6a9f26020644`.

Both jobs built the same solver binary, SHA-256
`2e6771dc7fb338a1ffb8da2df58707c9651c09bcafde9a566ae41adda691b2e0`.

## Protocol accounting

An earlier workflow run, 31721776964, failed in the calibration harness because
YAML folding passed a command named ` python3` to `timeout`. It evaluated no
development row and carries no mathematical outcome. Commit `157134a` fixed
only that invocation; source, contract, solver, controls, rows, and caps were
unchanged.

The normalized flat-table retry converted the earlier unknown `N=23` resource
termination into an exact draw without changing the recurrence. It does not
authorize another `N=24` solver, move order, memory layout, or longer cap inside
this trial. `N=24` is a durable timeout bracket.

No counterexample, strategy certificate, Lean disproof, issue, PR, or release
is authorized. The useful method outcome is operational: semantics-preserving
state normalization can turn a resource bracket into a scoreable exact row,
while the unchanged cap still produces an honest unknown at the next order.
