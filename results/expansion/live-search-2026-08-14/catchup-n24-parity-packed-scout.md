# Catch-Up N=24 parity-packed exact-search scout

**Disposition:** `NOT_SELECTED_NOT_EVALUATED`  
**Evidence split:** development design only  
**Target:** `CatchUp.value_of_even_mul_succ_self_div_two` at `N=24`

This note records a read-only design audit for a possible successor to the
completed flat-hash Catch-Up trial. It does not select the lane, authorize a
target run, or report an `N=24` evaluation.

## Current source and prior-art gate

The audit resolved `google-deepmind/formal-conjectures` `main` to commit
`6c0950bec7743f5098c0196c6aee7b22c1ec8005`, tree
`5af0d2a3a319ee2458f8cd061db7c49aeba1b35e`. The current file is
`FormalConjectures/Paper/CatchUpConjecture.lean`, blob
`ce8251a228ea79a6b2f8414e9eb6b5291a640677`. Its theorem
`CatchUp.value_of_even_mul_succ_self_div_two` remains tagged
`category research open` and has its intentional `sorry`.

The current public-status check found:

- merged PR #1325, which introduced the statement;
- open issue #4834, which proposes normalized APIs but explicitly claims no
  new exact case, reduction theorem, exact search, or certificate;
- no Catch-Up resolution PR in the upstream repository;
- no public exact `N=24` result in exact-name GitHub issue, PR, and code
  searches. The other exact-identifier code hits were formalization mirrors or
  benchmark copies.

That last item is a negative search, not proof of novelty. The source commit,
the theorem tag, upstream issues and PRs, and exact-result searches must all be
rerun immediately before any contract is authorized. A source change, closed
target, public exact result, or duplicate effort is a strict stop.

## Observed wall

The completed solver implements the exact normalized recurrence with a flat
open-addressed memo table. It established `N=23` as a draw with
95,451,689 memo states and 826,741,149 recursive calls in 50.786115 seconds.
At `N=24` it reached at least 112,000,000 memo states and 985,908,066 calls
before the external 60-second cap, with no result. Its final table capacity was
268,435,456 slots and its last solver RSS was 2,395,756 KiB; transient rehash
RSS was higher.

The next arm should therefore remove hashing and rehashing without changing
the game recurrence or using the previous timeout as a mathematical result.
A complete bottom-up layer table is less attractive: it evaluates many states
that the exact short-circuiting DFS never needs and can require billions of
move transitions.

## Reachable-state invariants

Write a post-opening state as `(M,d)`, where `M` is the remaining set and
`d = opponent_score - current_score >= 0`. For `N=24`, the initial total is
`T=300`, hence even.

After opening with `x`, the normalized state has

```text
M = full ∖ {x},  d = x,
sum(M) = T - x.
```

Thus `d ≡ sum(M) (mod 2)` and `d ≤ 24`. Both invariants are preserved by
every recurrence edge:

- if `x < d`, the player continues at `(M ∖ {x}, d-x)`, and both the
  deficit and remaining sum lose `x`;
- if `x ≥ d`, the turn swaps at `(M ∖ {x}, x-d)`, and
  `(x-d) - (sum(M)-x) = 2x - (d+sum(M))` is even;
- in both cases the new deficit is at most `24`.

Consequently a fixed mask can reach only one parity of deficit and has at
most 13 admissible deficit slots, represented by `slot = d >> 1`.

## Proposed compact exact arm

Allocate one `uint32_t` per 24-bit remaining mask. Pack each state's memo code
into two bits at `shift = 2 * (d >> 1)`, using four distinct codes for
`unknown`, `loss`, `draw`, and `win`.

The complete memo allocation is

```text
2^24 masks * 4 bytes = 64 MiB.
```

Pass the remaining sum as a recursion argument and update it by `sum' = sum-x`.
This avoids the existing 32-MiB subset-sum array. Enumerate present moves in
ascending order using set-bit extraction, preserving the old solver's actual
move order while avoiding tests of absent bits.

This representation removes SplitMix hashing, stored keys, linear probing,
load-factor checks, and all rehashes. The evaluator otherwise retains the
source recurrence exactly:

```text
empty: draw iff d=0, otherwise loss
sum(M)<d: loss
x<d:      P(M-x,d-x)
x>=d:    -P(M-x,x-d)
state:    maximum over legal x
root:     maximum over -P(full-x,x)
```

Memoization is exact because every edge removes one element. Short-circuiting
is permitted only after a state reaches `win`, the maximum outcome. A draw or
loss is returned only after all required legal moves have been checked.

The completeness boundary is exactly optimal Catch-Up on `{1,...,24}` under
the current DeepMind semantics. A completed draw proves this one instance; a
completed non-draw is a finite counterexample candidate. Neither outcome says
anything by itself about later admissible orders.

## Frozen controls and performance gate

Before `N=24` can be authorized, a versioned successor contract must freeze
the source pins, compact representation, outcome codes, ascending move order,
compiler and flags, internal 54-second cap, external 60-second cap, and output
schema. The old trial must remain immutable.

Required pre-target controls are:

1. independently prove or mechanically audit the deficit-bound and parity
   invariants;
2. exhaustively compare compact states with an absolute-score reference on
   small admitted orders;
3. reproduce all existing exact source controls;
4. replay the known `N=23` row.

Because the compact DFS preserves the normalized recurrence and included-move
order, the `N=23` replay must reproduce exactly:

```text
value       = draw
memo states = 95,451,689
calls       = 826,741,149
```

Any mismatch is a correctness failure. Freeze a pre-target performance gate
of at most 38 seconds for this `N=23` replay. If it misses that gate, do not
run `N=24`: the known `N=24` lower-bound workload leaves insufficient honest
headroom under 54 seconds.

The target process, if later authorized, must be single-threaded and check its
internal steady clock periodically. At 54 seconds it must emit a controlled
timeout record and stop; an external 60-second limit remains the fail-safe.
No target-informed change of move order, packing, compiler flags, or limits is
allowed after the frozen run starts.

## Incremental artifacts and candidate certificate

The frozen run should preserve:

- upstream commit, tree, blob, and declaration digest;
- the captured status and duplicate-search coordinates;
- contract, source, compiler, binary, and test-suite SHA-256 digests;
- JSONL at run start, every million memo insertions, controlled timeout, and
  exact result, with calls, memo states, elapsed time, and RSS;
- raw stdout/stderr and `/usr/bin/time -v` output;
- an append-only resolution ledger and independent replay report.

If the exact result is non-draw, publication remains blocked until a second
independently implemented normalized evaluator reproduces it and an
independent checker accepts a replayable strategy DAG. In that DAG:

- a winning state supplies one legal child that proves the win;
- a losing state supplies every legal child, proving every move loses;
- terminal values and sign changes at turn swaps are explicit;
- each node records `(mask, deficit, remaining_sum, value)` and the checker
  independently verifies the mask sum, parity, bounds, legal transitions,
  terminal conditions, and strict mask-cardinality decrease.

Canonical certificate bytes, checker source, checker output, and all their
digests must be retained. A table digest alone is not a mathematical
certificate.

## Stop and disposition rules

- Source/status/duplicate gate fails: `PRIOR_ART_OR_STATUS_STRICT_STOP`.
- Invariant proof, state comparison, source calibration, or exact `N=23`
  counts fail: `INVALID_ARM`; do not evaluate the target.
- `N=23` exceeds 38 seconds: `PERFORMANCE_GATE_STOP`; do not evaluate the
  target.
- Internal/external timeout, allocation failure, or abnormal termination:
  `TIMEOUT_BRACKET`; never infer draw or hold.
- Exact `N=24` draw: `HOLD_BOUNDED`; commit the result, but no candidate,
  release, issue, or PR.
- Exact non-draw with evaluator disagreement or failed certificate:
  quarantine as `UNVERIFIED_CANDIDATE`.
- Verified non-draw that is already public: record it as a duplicate, with no
  novelty claim or release.
- Only a source-mapped, independently reproduced, certificate-checked, and
  novelty-cleared non-draw may enter the repository's release pipeline.
- Do not advance to `N=25`, whose triangular sum is odd. Orders `27` or `28`
  require their own separately frozen contracts.

No target evaluation, candidate, release, or public action is represented by
this scout.
