# OEIS A231201 v2 design scout

**Scout date:** 2026-08-14 UTC
**Classification:** contaminated DEVELOPMENT design analysis
**Run inspected:** GitHub Actions `31805086511`, attempt 1
**Executed commit:** `7669f2260b2dc1f05cf4aeb389f80d3c7c37b86a`
**Disposition:** freeze a materially different v2 construction protocol before another run

This report analyzes the bounded v1 run and specifies a recommended v2 search
construction. It is not a result, a counterexample, an exhaustion claim, a
novelty claim, a release, authorization to dispatch a run, or authorization for
upstream action. No target candidate or target model was evaluated while
preparing this report.

The v2 recommendation preserves the v1 corrected `C+` semantics: coverage is
over positive exponents, each periodic class is evaluated at its least-positive
representative, and `x=0` remains excluded. It also preserves exactly the same
55-prime universe through 257. Search construction and operational accounting
may change; arithmetic semantics and the final certificate claim may not.

## Exact observations from v1

All six disjoint `(a_2,a_3)` cells reached the same protocol state: the first
CP-SAT master returned `UNKNOWN`, no assignment was emitted, the exact
adversary was never called, and no CEGAR iteration occurred.

| Cell | Active fixed values | Wall time (s) | Branches | Conflicts | Assignments | Adversary calls |
|---|---|---:|---:|---:|---:|---:|
| `A2_EQ_0/0` | `a_2=0,a_3=0` | 54.002345310 | 2,178,769 | 333,762 | 0 | 0 |
| `A2_EQ_0/1` | `a_2=0,a_3=1` | 54.003098217 | 1,333,726 | 464,974 | 0 | 0 |
| `A2_EQ_0/2` | `a_2=0,a_3=2` | 54.002757803 | 2,671,757 | 337,876 | 0 | 0 |
| `A2_EQ_1/0` | `a_2=1,a_3=0` | 54.002556911 | 1,262,322 | 292,534 | 0 | 0 |
| `A2_EQ_1/1` | `a_2=1,a_3=1` | 54.003890425 | 2,731,757 | 353,533 | 0 | 0 |
| `A2_EQ_1/2` | `a_2=1,a_3=2` | 54.003781893 | 1,946,475 | 289,739 | 0 | 0 |

The gate passed, all six search processes exited 75 with
`terminal_reason=DEADLINE_PREFIX`, and their artifact checks passed. Empty
stdout/stderr and the substantial branch/conflict counts show that this was
neither a gate failure nor process startup overhead. CP-SAT spent the entire
inner allowance searching the first seed model and did not report an incumbent.

The immediate operational cause is deterministic. The coordinator establishes
one 54-second absolute deadline and passes all remaining time to the first
`solve_once()` call. That call can consume the whole construction allowance.
V1 reserves no time for assignment serialization, the exact adversary, local
repair, or a second CEGAR iteration.

The first model is also unnecessarily broad. It creates 6,338 Boolean variables
(`sum(q)` over the 55 primes), 55 exactly-one groups, and 4,096 coverage clauses
containing one literal per prime. It has no warm hint, decision strategy,
objective, incumbent-sharing mechanism, or smaller active constraint basis.

Fixing `a_2` and `a_3` has a strong exact consequence that v1 does not apply in
its own preprocessing. The fixed literals already satisfy two thirds of the
seed. Removing satisfied rows and stripping false fixed literals leaves:

- 1,366 active rows in cells `(a_2,a_3)=(0,0)` and `(1,2)`;
- 1,365 active rows in each of the other four cells; and
- 53 unfixed prime groups.

A static audit of these six reduced seed matrices found no duplicate active row
signatures. It found only 1--7 dominated residue variables per cell, all of them
zero-incidence residues. For a fixed prime, the nonempty residue incidence sets
partition the active rows, so no nonempty one is a strict subset of another.
Cross-prime set inclusion is not, by itself, a sound elimination rule because
the one-residue-per-prime group constraints differ. V2 must emit a proof for any
stronger dominance deletion rather than treating heuristic similarity as exact
presolve.

The six `(a_2,a_3)` cells are disjoint and exhaustive, but they are not safely
interchangeable symmetry copies. Translating `x` does not preserve
`x-2^x (mod q)` uniformly across the other primes. V2 should retain all six
cells and call them partition cells, not quotient any of them away without a
separate exact equivalence proof.

Finally, construction is not the only feasibility risk. In the unchanged
ascending-prime exact adversary, the running combined modulus is 420 through
prime 7, 60,060 through 13, 2,042,040 through 17, 116,396,280 through 19, and
2,677,114,440 through 23. A purported cover that closes only at a much larger
prime can make the explicit Python frontier impractical. V2 should prefer
assignments whose basis coverage closes under a small prime prefix, while still
materializing all 55 frozen coordinates and requiring the unchanged exact
adversary and independent final checker for any claim.

## Frozen v2 construction recommendation

Run three complementary construction arms over all six exact partition cells.
They may share deterministic hints and assignment hashes, but an arm's ledger
must identify the source of every hint. No construction arm may certify a
cover.

### Arm 1: `COMPRESSED_SET_COVER_CP`

1. Evaluate the fixed `q=2,3` literals before model creation. Remove satisfied
   rows and remove the two false fixed literals from every remaining row.
2. Create a Boolean variable only for a `(q,a)` residue that occurs in the
   current active basis. Record zero-incidence alternatives rather than adding
   them to the master.
3. Use `sum_a z[q,a] <= 1` for each unfixed prime, not exactly one. This is
   feasibility-equivalent for a finite basis: a prime left unselected can later
   be assigned any residue, and adding that residue cannot uncover an already
   covered row.
4. Before adversary submission, materialize exactly one residue for every one
   of the 55 primes. Use the selected active residue when present; otherwise use
   the previous hinted residue, then the least residue as the final deterministic
   fallback.
5. Seed the first model with the best deterministic greedy assignment from Arm
   2. After each adversary counterexample, hint the full previous assignment.
6. Branch on smaller primes first and, within a prime, on residues in descending
   uncovered-row gain with the residue value as the final tie-break.
7. Keep the complete, explicitly reduced `x=1,...,4096` seed in this arm, but
   solve it through bounded calls rather than one call that owns the global
   deadline.

This is still a grouped set-cover master, but it avoids forcing CP-SAT to make
irrelevant choices among residues that cover no active row and makes the
already-fixed coverage reduction explicit and auditable.

### Arm 2: `DETERMINISTIC_GREEDY_REPAIR`

1. Store active-row incidence as bitsets.
2. Initialize each unfixed prime with the residue that covers the most currently
   uncovered rows. Break ties by smaller prime and then smaller residue.
3. Apply deterministic coordinate descent. At each move, change one prime's
   residue to minimize the lexicographic score
   `(uncovered rows, singly covered rows, full assignment tuple)`.
4. When no improving move exists, perturb around the lexicographically first
   uncovered row using a frozen prime/residue rotation schedule. Do not use
   ambient randomness or an undeclared seed.
5. Whenever all current basis rows are covered, serialize the complete frozen
   55-coordinate assignment before invoking the exact adversary.
6. If the adversary returns `UNCOVERED_CLASS`, append its exact positive `x`,
   update the affected bitsets, and resume local repair from the prior
   assignment.

This arm is intended to produce early assignments and adversary observations
even when proof-oriented CP search cannot finish a seed model. Its local scores
are construction heuristics only.

### Arm 3: `SMALL_BASIS_CEGAR`

1. Start from 192 active rows in each cell, selected by a manifest-frozen
   low-discrepancy permutation of `1,...,4096`. Freeze both the permutation
   algorithm and its salt; do not use a runtime-random sample or a consecutive
   prefix.
2. Use the compressed grouped-set-cover formulation from Arm 1.
3. Submit every complete assignment to the exact adversary. Append an returned
   `UNCOVERED_CLASS` immediately.
4. Every fourth master round, append the next 64 active seed rows from the
   frozen permutation until the entire corrected 4,096-row seed has entered the
   basis.
5. Warm-start every master from its previous complete assignment. If the arm
   receives a better assignment from another arm, record its hash and source
   before using it as a hint.

This arm directly tests whether v1 stalled because it demanded a difficult,
possibly nearly infeasible 4,096-row basis before obtaining any adversary
information. Exactness is unchanged: a small-basis assignment is merely a
proposal, and only exact adversary exhaustion can establish coverage.

## Cross-arm and verifier rules

- Every complete assignment from every arm goes to the existing exact
  construction adversary. No heuristic coverage score may create a pending
  candidate.
- Only an adversary receipt with `COMPLETE_COVER` may create
  `candidate-pending.json`.
- Every pending candidate goes to the existing independent final checker. Only
  its `VERIFIED_COUNTEREXAMPLE` status is a result.
- Deduplicate exact adversary submissions by full assignment SHA-256 within a
  job. A duplicate still receives a `DUPLICATE_ASSIGNMENT_SKIPPED` ledger row
  that binds the original submission and receipt.
- Rank construction assignments first by uncovered-basis count, then by the
  least prime prefix covering the basis, then lexicographically. Favoring early
  closure is a search preference, not a semantic restriction.
- Do not delete a nonempty cross-prime signature as "dominated" unless a
  group-aware exact implication certificate is stored and independently
  checked.
- Preserve all six `(a_2,a_3)` cells. Sharing hints or learned counterexample
  exponents does not merge their assignment spaces.

## Exact cap proposal

The scout initially considered a multi-minute allowance, but the standing
project protocol requires a 60-second ILP/process cap. The executable v2 must
therefore stage construction and exact replay as separate fixed jobs rather
than lengthening one process:

- every construction arm/cell process has a 54-second internal deadline inside
  a 60-second external process-group cap, with `TERM` at 60 seconds and `KILL`
  six seconds later;
- every CP-SAT call is sliced to at most 12 seconds, with at most three slices
  in one construction job and time reserved for assignment serialization and
  the terminal receipt;
- greedy/repair and small-basis rounds share the same 54/60 envelope and stop
  before their finalization reserve;
- construction jobs persist a frozen maximum number of complete assignments;
  separate fixed-matrix adversary jobs replay those slots, each under its own
  54/60 envelope;
- a pending complete cover enters a separately capped independent final replay,
  again 54 seconds internal and 60 seconds external; and
- absent assignment slots are explicit `NOT_RUN` records, never successful
  verifier exit codes.

A CP-SAT slice returning `UNKNOWN` records `SLICE_UNKNOWN` and yields control
to the remaining permitted slices or construction logic. It does not terminate
another arm. All limits are per fresh, non-resumable stage; no later job may
continue an omitted exact frontier unless a separate freeze adds a replayable
cursor and independent checker. This staging preserves the standing cap while
still guaranteeing that construction cannot consume the adversary's allowance.

## Terminal vocabulary

Each construction terminal must use exactly one of these meanings:

- `COVER_FOUND_PENDING_VERIFY`: the exact construction adversary returned
  `COMPLETE_COVER` and a pending candidate was durably written.
- `BASIS_INFEASIBLE_UNVERIFIED`: an exact solver proved only the current finite
  basis infeasible in this cell. It is not exhaustion of the 55-prime universe
  under the unbounded exact coverage condition.
- `CAP_EXHAUSTED_AFTER_ASSIGNMENTS`: the attempt ended after at least one
  complete assignment and adversary submission but without a verified cover.
- `CAP_EXHAUSTED_NO_ASSIGNMENT`: the attempt ended without producing a complete
  assignment.
- `ADVERSARY_DEADLINE`: a submitted assignment's exact adversary exhausted its
  own reserved allowance without a complete classification.
- `WORKER_ERROR`: an exception or invariant failure occurred; include the
  fail-closed traceback artifact.

`SLICE_UNKNOWN` is iteration-local, not a terminal mathematical status.
`NO_COMPLETE_COVER` remains forbidden without a separately frozen,
independently replayable exhaustive certificate. `DOMAIN_EXHAUSTED` remains
level-local to exact refinement. An adversary uncovered class is a construction
counterexample and must not be relabelled as a deadline.

## Artifact rules

1. Write `basis-0000.json` before construction and append immutable
   `basis-delta-NNNN.json` files. Every ledger row binds the ordered basis count
   and SHA-256.
2. Persist every complete assignment atomically before starting its adversary
   process. Bind the construction arm, cell, round, basis hash, and hint source.
3. Record each round's solver branches, conflicts, status, and wall time, or the
   greedy move and score counts; also record remaining internal time.
4. Store every adversary ledger and receipt, including deadline-prefix receipts,
   and bind them from the master hash chain.
5. A terminal receipt records construction rounds, complete assignments,
   distinct adversary submissions, duplicate skips, basis size, cap state, all
   artifact hashes, and whether a pending candidate exists.
6. When there is no candidate, record
   `final_verifier_status="NOT_RUN"` and `final_verifier_exit_code=null`. V1's
   `final_verifier_exit_code=0` in this situation is operationally misleading.
7. Artifact-verifier success means only that the bounded evidence is complete
   and internally consistent. It cannot promote `UNKNOWN`, basis infeasibility,
   a deadline, or an uncovered class to a mathematical conclusion.
8. Retain atomic writes, fsync, canonical JSON, source/manifest/gate bindings,
   ledger hash chains, and independent final replay from v1.

## Expected feasibility and stop interpretation

There is high operational confidence that v2 will produce complete assignments
and exact adversary calls. The greedy arm and the deliberately small initial
basis remove v1's all-or-nothing dependency on a single 54-second CP-SAT solve.
There is moderate confidence that hinted compressed CP-SAT can solve at least
some reduced 1,365/1,366-row cell masters within repeated 15-second slices.

There is low-to-unknown confidence that this will yield a verified
counterexample. Prior exact controls already establish infeasibility through
prime 13, and the explicit exact frontier grows sharply after primes 17 and 19.
A scientifically useful v2 attempt may therefore consist of reproducible
assignments, adversary receipts, and a calibrated earliest-closure boundary,
without a complete cover.

If all three arms repeatedly cover their finite bases but the exact adversary
reliably reaches its cap beyond the 17/19 frontier, stop and freeze a separate
verifier-engineering addendum. Do not silently change the prime universe,
positive-representative rule, final checker, time limits, or meaning of a
terminal status during the frozen v2 run.

No target candidate or target solver model was evaluated for this design
scout. No search was dispatched. This report records no result and authorizes
no commit, push, release, publication, or upstream action.
