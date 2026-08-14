# OEIS A231201 v2.2 contaminated DEVELOPMENT freeze

This is the smallest operational supersession of the immutable v2.1 freeze.
GitHub Actions run
[`31811239530`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31811239530)
confirmed that the v2.1 Python correction worked: six round-zero
`SMALL_BASIS_CEGAR` assignments were durably emitted.  Every one of their six
exact adversaries nevertheless reached the outer 60-second timeout before it
could write a terminal.  The observed prefix reached prime `q=17` with a
368,640-state frontier; while beginning `q=19`, the deadline branch recomputed
the hash of its already-large partial queue.  The process was killed with
stage exit 124, the artifact verifier returned 1 because no terminal existed,
and every downstream stage failed closed.  The run produced zero candidates
and no mathematical result.

## Frozen operational correction

V2.2 changes only exact-adversary execution and verification:

- exact exploration receives 48 seconds, reserving six of the inherited 54
  internal seconds for in-process ledger closure, terminal serialization, and
  fsync before the unchanged 60-second outer cap.  The separate artifact
  verifier runs only after the bounded adversary process has returned;
- each appended CRT state updates a SHA-256 stream using the historical
  `r,modulus\n` encoding, making a deadline digest O(1) rather than a fresh
  traversal of the partial queue;
- completed and partial levels now preserve deterministic insertion order.
  The old completed-level digest was computed after sorting, whereas the old
  partial deadline digest used insertion order.  V2.2 therefore declares an
  explicit insertion-order digest scheme and does not claim byte compatibility
  with the old completed-level digest.  Sorting was not part of the exact set
  semantics: all generated states are retained, no deduplication is performed,
  and every retained state is visited exactly once at the next level;
- the least positive final state is maintained as states are appended, so a
  completed search also requires no unbounded post-deadline sort, hash, or
  minimum pass;
- the v2.2 artifact wrapper first performs every inherited v2 structural,
  source-gate, assignment, candidate, and final check, then additionally binds
  a deadline receipt to its v2.2 ledger row, cursor, count, digest scheme,
  budget, and exit status;
- a synthetic Python-3.9-compatible test forces a 200,000-state partial
  frontier, obtains a deadline terminal, and verifies the hash-chained artifact
  without loading the frozen target order table, periodic value function,
  source gate, target assignment, candidate, or final verifier.

The v2 and v2.1 trees remain byte-for-byte frozen.  V2.2 reuses the v2.1
constructor, the exact source/database gate, all three arms, six cells, three
rounds, predecessor validation, candidate format, and independent final
verifier.  It remains nonresumable.  A deadline is only an exact explored
prefix and may never be upgraded to exhaustion, infeasibility, a cover, or a
counterexample.

## Execution rule

Only an exact 40-hex commit containing this complete freeze may be supplied to
`.github/workflows/oeis-a231201-v22-development.yml`.  All artifact names are
v2.2-specific.  Every gate, constructor, adversary, and final execution remains
under `timeout --signal=TERM --kill-after=6s 60s`; the adversary alone stops
search at 48 seconds to reserve bounded finalization time inside the inherited
54-second internal budget.

This lane remains `CONTAMINATED_DEVELOPMENT`.  Constructor or adversary output
must not be published.  Only exact adversary completion plus the independent
final verifier can promote a candidate, followed by source/status/novelty
review under the repository protocol.
