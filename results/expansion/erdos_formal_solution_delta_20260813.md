# Erdős formal-solution status delta audit

**Verdict:** no unclaimed DeepMind proof-transfer candidate after excluding
previously audited Problems 92 and 617  
**DeepMind snapshot:** `7a38c469ec329d0c97c068e03c58834f61628e7e`  
**Erdős data snapshot:** `66dfe4860f73d94ecb1b09b99990a67272b6d16a`

The audit compared four distinct coordinates: canonical informal status,
canonical formal-solution status, canonical statement-formalization status,
and the exact DeepMind declaration. It also inspected the linked external proof
artifacts and all visible open, closed, and merged DeepMind attempts.

The strongest clean deltas run in the opposite direction from a missing proof:
DeepMind already links merged, sorry-free formal solutions, while the canonical
Erdős metadata still reports `open / unformalized / formalized yes`.

| Problem | DeepMind standing | exact correspondence | correct action |
|---:|---|---|---|
| 489 | `research solved`, `answer(True)` | linked `erdos489_statement` matches the quantified limit statement | canonical metadata sync only |
| 796 | `research solved`, `answer(True)` | linked `erdos796_statement` is definitionally the same existential limit | canonical metadata sync only |
| 1188 | `research solved` | linked theorem states the exact `log(log F(x))/log x -> 1` limit | canonical metadata sync only |

All three were merged by DeepMind PR 4578 on 2026-08-07, using the pinned
external proof commit `4f915a323443bfb1709a6805a013812016dca88a`. The
downloaded proof files contain neither `sorry` nor `axiom`. No current
`teorth/erdosproblems` issue or PR was found for synchronizing these three
canonical records.

Problems 254 and 267 are additional likely full-solution status lags from the
same merged PR, but their exact correspondence needs an explicit bridge, so
they are not promoted to the clean list. Problems 130 and 769 are partial; 655
is statement-ambiguity dependent; 1097 refutes a displayed asymptotic guess
without resolving the optimal-exponent problem. Problems 692, 1112, and 321
already have live DeepMind claims and were excluded.

These rows are valuable four-axis status-gate controls. They do not authorize a
new Lean proof, discovery claim, release, issue, or PR from this repository.
