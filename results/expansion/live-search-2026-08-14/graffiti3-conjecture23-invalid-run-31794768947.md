# Graffiti³ Conjecture 23: invalid first execution

**GitHub Actions run:**
[`31794768947`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31794768947)

**Frozen commit:** `5e184e2df3aef55aa3e55d6f8ccbb1a0fd65d253`

**Classification:** `INVALID_RUN` — no mathematical inference

The first execution exposed an operational defect in the mandatory database
gate before any target group was proposed or scored. Of the 72 target jobs:

- 69 reached the monolithic GAP gate and terminated `SANITY_GATE_FAILED` with
  `expected one @@GATE@@ marker`;
- three catalogue jobs (`0`, `5`, and `10`) timed out while installing GAP and
  never entered the search step.

All 69 uploaded ledgers were independently replayed. They contain exactly the
three expected rows (`start`, `database_sanity_failure`, `terminal`), their
SHA-256 hash chains and terminal bindings verify, every counter is zero, and
no certificate exists. The 69 assignments cover all generic and wall shards
and 21 catalogue shards without duplication. The remaining three assignments
have GitHub job receipts showing that the search step was skipped.

The original shell step inherited GitHub Actions' `bash -e` behavior, so the
nonzero fail-closed worker exit occurred before `assignment.json` and
`SHA256SUMS` were written. The ledger and terminal receipts themselves remain
internally bound, but this is another execution-evidence defect and is fixed
before the replacement run.

The replacement architecture prepares the complete 2,732-row source gate once
in 96 separately capped GAP chunks, content-addresses the aggregate, and makes
every target worker verify that shared attestation before admitting a proposal.
This report does not count the failed execution as a bounded zero, a target
evaluation, or evidence for or against Conjecture 23.
