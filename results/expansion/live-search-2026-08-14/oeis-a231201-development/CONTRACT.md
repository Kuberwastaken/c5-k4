# OEIS A231201 contaminated DEVELOPMENT freeze

This is a target-specific, contaminated DEVELOPMENT continuation. It is not
held-out evidence, a result, a novelty claim, a release, or authorization for
upstream action. The prior A231201 least-witness experiment and the prior
covering-congruence runs are mandatory controls, not discoveries by this lane.

## Exact target and finite certificate

The immutable target is `OeisA231201.conjecture` at Formal Conjectures commit
`4010c1f1...`. A counterexample is an `n>1` for which every `1<=x<n` makes
`2^x+n-x` composite. A verified certificate consists of `n`, one selected
residue `a_q` per frozen prime, an exact generalized-CRT positive-exponent
cover, the reconstructed CRT congruences `n=a_q (mod q)`, and proper-divisor
inequalities. The exact source and database hashes are in `manifest.json`.

## Source/database-sanity stop gate

Before construction, the gate verifies the Lean commit/path/blob/module,
declaration and category; the immutable OEIS record, offset `1,5`, formula,
examples, and `10^7` boundary; parses and content-locks all 10,000 b-file
rows; and exactly recomputes the complete prefix `n=1,...,72` by enumerating
`x=1,...,n-1`. Every tested integer is below the frozen 12-base deterministic
Miller--Rabin bound `318665857834031151167461`; an out-of-range value fails the
gate rather than becoming a probable-prime decision. Eight contiguous chunks
each have a 54-second internal deadline inside a 60-second process-group cap.
It also replays the Lean controls `2,3,4,5,8,53`, OEIS examples `53,64`, the
prior private vendored `L(327)=72` control, and the public bounds `7,11,13`
covering receipts. Any drift, mismatch, incomplete classification, missing control, or
deadline yields `SANITY_GATE_INCOMPLETE`; no search job depends on a failed
gate.

## Frozen finite universe and correction

`P` is exactly the 55 primes at most 257 in `manifest.json`. For odd `q`,
`o_q=ord_q(2)`; `o_2=1`; and `m_q=q*o_q`. There is exactly one variable
`a_q in Z/qZ` per prime. Positive periodic classes use the least-positive
representative rule frozen in `PRE_FREEZE_CORRECTION.md`. The combined period
is the exact manifest integer.

The six `(a_2,a_3)` shards are disjoint and exhaust every assignment in the
documented universe. They are operational partitioning only: no prime,
residue, or assignment is added or removed. The exact superseding corrections
to the infeasible gate and invalid `x=0` seed are in `PRE_FREEZE_CORRECTION.md`.

## CEGAR, exact adversary, and terminal meanings

The CP-SAT master uses `ortools==9.15.6755`, one worker, seed zero, ascending
`(q,a)` creation order, no objective, exactly-one constraints, and direct seed
constraints for `x=1,...,4096`. Each feasible assignment is passed to a
separate exact generalized-CRT adversary. The adversary refines uncovered
congruence states in ascending-prime order, logs and fsyncs every completed
level, and returns the least positive surviving class as the next constraint.
Empty final state means `COVER_FOUND_PENDING_VERIFY`, never a result.

An independent final process, using a separately implemented depth-first
coverage routine rather than the adversary's refinement function, rebuilds
primes, orders, period, assignment, coverage, CRT, the least `n>10^7`, and the
generic proper-divisor inequalities. Only it may emit
`VERIFIED_COUNTEREXAMPLE`.

`DEADLINE_PREFIX` means only that one non-resumable bounded attempt stopped.
Its cursor, queue hash, and iteration snapshots are diagnostics; no omitted
queue is recoverable from them and no later run may continue from them.
`SOLVER_INFEASIBLE_UNVERIFIED`
is not exhaustion. `NO_COMPLETE_COVER` is forbidden unless an independently
replayable exact exhaustive certificate exists; this harness does not create
that status. `DOMAIN_EXHAUSTED` is reserved for a verifier-refinement level
whose complete input queue was consumed and is never promoted to a search
conclusion. Gate chunks use the separate `GATE_CHUNK_EXHAUSTED` status. If
final replay finds a surviving class it records
`VERIFICATION_FAILED_UNCOVERED_CLASS`, distinct from `DEADLINE_PREFIX`. All
JSONL rows are canonical SHA-256 hash chains and are fsynced;
iteration snapshots and terminal receipts bind queue hashes, solver responses,
source hashes, counters, ledger hashes, elapsed time, and exit status as audit
evidence only. This freeze has no resume interface.
