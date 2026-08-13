# Independent-domination private-leaf cone: gate failure

Date: **2026-08-13 UTC**

Strict status: **`GATE_FAIL / STOP_LITERAL_MISMATCH`**

The mandatory executable live source/prior-art gate stopped before any
arithmetic or graph evaluation. It correctly found the current upstream
declarations `independentDominationEven` and `independentDominationOdd`, both
still tagged `research open`, and preserved the source-paper facts that the
result is proved through `D=4` and reported checked without included proofs
for `D=5,6,7,8`.

The stop was caused by a brittle paper-source literal. The gate required the
rendered phrase `Conjecture 1.6`, while the primary arXiv TeX encodes the same
statement as a conjecture environment labeled `con:idset-general`.

Issue #227 and merged PR #1373 are only the history that added the open
declarations; the exact upstream search found no resolution. These source and
prior-art observations survive the stop, but they do not authorize development.

Due to a coordination race, a repaired replay and proposed bounded-domain
freeze were appended before the terminal instruction arrived. Append-only
discipline forbids deleting those ledger rows. The final ledger event marks
both as non-operative and superseded: repairing the failed mandatory gate
inside this trial is not allowed. Consequently:

- candidate evaluations: **0**;
- no arithmetic domain was validly frozen;
- no arithmetic vector or graph was evaluated;
- no theorem-safe or counterexample conclusion is claimed.

No commit, push, release, issue, pull request, or public action was performed.
