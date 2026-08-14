# OEIS A231201 v2 contaminated DEVELOPMENT freeze

This is a bounded, contaminated DEVELOPMENT construction protocol. It is not
held-out evidence, a result, an exhaustion claim, a novelty claim, a release,
or authorization to dispatch or publish. It inherits the immutable source,
database-sanity gate, corrected positive-exponent `C+` semantics, exact 55-prime
universe, combined period, and six disjoint `(a_2,a_3)` cells from v1.

V2 changes only proposal construction and stage accounting. Three arms run in
every cell: `COMPRESSED_SET_COVER_CP`, `DETERMINISTIC_GREEDY_REPAIR`, and
`SMALL_BASIS_CEGAR`. The full arm/cell/round matrix is static. Every construction,
exact-adversary, and independent-final process has 54 internal seconds inside
`timeout --signal=TERM --kill-after=6s 60s`. CP-SAT uses at most three 12-second
slices per construction process. There are exactly three non-resumable rounds
and one assignment slot per arm/cell/round.

Construction may only propose a complete 55-coordinate assignment. It cannot
certify the target. Every emitted assignment is durably stored and sent to a
separate exact generalized-CRT adversary job. Only `COMPLETE_COVER` from that
adversary creates a pending candidate, which always enters a separately capped,
independently implemented final verifier. Only `VERIFIED_COUNTEREXAMPLE` is a
mathematical result. Basis infeasibility, a cap, an uncovered class, and artifact
verification never upgrade to exhaustion or a result.

The compressed arm removes rows already satisfied by fixed `q=2,3`, removes
false fixed literals, creates only occurring residue variables, uses at-most-one
groups, greedy warm hints, small-prime decision order, and deterministic full
completion. The greedy arm uses integer bitsets, deterministic max-gain
initialization, coordinate repair, and a frozen perturbation schedule. The
small-basis arm begins with 192 rows from the manifest-frozen bit-reversal
permutation, consumes prior exact uncovered exponents immediately, and adds the
next 64 frozen rows on each fourth logical master round. Small-prime closure is
only a proposal-ranking preference.

All JSONL ledgers are canonical SHA-256 chains and fsynced per row. Assignments,
bases, deltas, receipts, and terminals are atomic and fsynced. Artifacts upload
under `always()`. No cursor is resumable. `NO_COMPLETE_COVER` is forbidden.
Every fixed matrix cell is initialized before prerequisite acquisition. Missing
or corrupt prerequisites therefore produce a durable `PREREQUISITE_NOT_RUN`
terminal (or `NOT_RUN` for an absent assignment/candidate), never an absent
terminal. Execution status records stage and artifact-verifier exit codes
separately and gives verifier failure fail-closed precedence.
If checkout, Python setup, or the frozen recorder itself is unavailable, an
environment-independent `stage-diagnostic-terminal.json` is finalized as
`STAGE_TERMINAL_UNAVAILABLE` and checksummed before unconditional upload. This
bootstrap diagnostic is evidence of infrastructure failure, not a stage result.
Every downstream edge verifies both the predecessor checksum manifest and its
`execution-status.json` and stage terminal. A predecessor is usable only when
its prerequisite and artifact-verifier codes are zero, its job code faithfully
equals its bounded-stage code, and both records have exact stage/arm/cell/round
identity. Honest bounded nonzero terminals such as no-assignment caps,
adversary deadlines, and `NOT_RUN` remain usable control flow; prerequisite and
worker failures do not. Thus a checksum-valid but unverified predecessor never
authorizes the next target-processing stage.
