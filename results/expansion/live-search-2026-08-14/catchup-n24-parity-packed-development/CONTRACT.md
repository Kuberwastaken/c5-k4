# Catch-Up N=24 parity-packed DEVELOPMENT freeze

**State:** prepared and target-unevaluated  
**Evidence split:** development only  
**Literal target:** `CatchUp.value_of_even_mul_succ_self_div_two` at `N=24`

This is a versioned successor to the completed flat-hash Catch-Up trial. It
freezes a representation change before the target is evaluated. It does not
change the source recurrence, claim an `N=24` value, authorize a release, or
prove the universal conjecture.

## Source, status, and resolution boundary

The exact current source frozen by the committed status audit is:

- formal-conjectures commit
  `6c0950bec7743f5098c0196c6aee7b22c1ec8005`;
- tree `5af0d2a3a319ee2458f8cd061db7c49aeba1b35e`;
- path `FormalConjectures/Paper/CatchUpConjecture.lean`;
- blob `ce8251a228ea79a6b2f8414e9eb6b5291a640677`;
- raw SHA-256
  `7e940f2e37a1794e98fc21454096429da13243669a432b9239743aaf46f1d3c0`;
- declaration `CatchUp.value_of_even_mul_succ_self_div_two`, still
  `@[category research open]` with `sorry` at the audit time.

The theorem is universal in `N`. Since `24*25/2=300` is even, an exact
non-draw at `N=24` would be a finite counterexample candidate. An exact draw
is only `HOLD_BOUNDED`; it does not prove the universal statement. Timeout,
OOM, abnormal termination, or heuristic evidence is only a resource bracket.

The primary 2015 paper reports exact values only through `N=20`; its
`N=23,24,27,28` observations are Monte Carlo evidence. The committed
`catchup-n24-current-status-audit.md` found no exact public `N=24` value or
strategy certificate. The frozen known upstream surface is source issue #1324,
merged source PR #1325, and open API-only proposal #4834. A same-run live
source/status/duplicate gate is mandatory before an
authorized target execution. Any drift or plausible new exact claim is a
strict stop.

The pre-freeze local history coordinate is
`c5-k4@d9ae09fe54af131790e72d12ad8b438a4b1fd9f6`. Execution is not tied to a
movable branch: workflow dispatch requires the exact 40-hex campaign commit,
checks out that commit, and verifies `HEAD` plus every frozen-file digest.

## Exact recurrence and packed representation

After the opening move, use `(M,d,s)`, where `M` is the remaining mask,
`d=opponent-current`, and `s=sum(M)`. The recurrence is exactly:

```text
empty:  draw iff d=0, otherwise loss
s<d:    loss
x<d:    P(M-x,d-x,s-x)
x>=d:  -P(M-x,x-d,s-x)
state:  maximum over legal x in ascending order
root:   maximum over -P(full-x,x,T-x)
```

Every edge removes one counter. On every reachable state, `0<=d<=N` and
`d+s` has the parity of the fixed triangular total `T`. Consequently each
mask reaches only one parity of deficit. Store `unknown/loss/draw/win` as
four two-bit codes at `shift=2*(d>>1)` in one `uint32_t` per mask. The full
`N=24` memo is therefore exactly:

```text
2^24 * 4 bytes = 67,108,864 bytes = 64 MiB.
```

The remaining sum is passed through recursion; there is no subset-sum array.
Moves use ascending set-bit extraction. The solver retains win-only
short-circuiting and evaluates every required move before returning draw or
loss. No hash, rehash, probabilistic cache, replacement, symmetry quotient,
changed move order, or target-informed parameter is allowed.

## Gates before N=24

The target remains mechanically disabled unless all of the following pass at
the exact campaign commit:

1. warning-clean C++20 compilation at `-O3 -Wall -Wextra -Werror`;
2. the freeze verifier and full frozen-file registry;
3. independent absolute-score comparison for every `N=1..12`;
4. actual solver-emitted strategy DAG replay for a target-free win (`N=1`) and
   loss (`N=9`), covering both existential-win and exhaustive-loss branches;
5. exact source controls `N=3,4,7,8,11,12,15,16,19,20`, all draws;
6. exact `N=23` replay with value `draw`, `95,451,689` memo states, and
   `826,741,149` calls;
7. the `N=23` solver-reported time is at most 38 seconds;
8. the same-run source/status/duplicate gate passes.

A target-free pre-freeze replay on this VPS reproduced the exact `N=23`
counts in 10.08 seconds with about 35.5 MiB peak RSS. That measurement freezes
the plausibility of the 38-second gate; the workflow must rerun the gate and
may not rely on this prose record.

The solver has no generic `--n 24` route. Target execution requires all three:

- workflow input `authorize_n24=true`;
- activation token `AUTHORIZE_FROZEN_CATCHUP_N24_V1`;
- an exact 40-hex campaign commit checked out as `HEAD`.

The default workflow dispatch therefore validates and replays `N=23` without
evaluating `N=24`.

## Caps and incremental evidence

The `N=24` solver has an internal steady-clock deadline of 54 seconds and an
external `timeout` cap of 60 seconds with a three-second kill-after failsafe.
The `N=23` performance gate has a 38-second internal deadline and a 43-second
external failsafe. Every auxiliary verifier is externally capped at 60
seconds. GitHub job limits are only outer containment and do not replace these
process caps.

The solver flushes canonical JSONL at run start, each million memo insertions,
controlled timeout, and exact result. Every row records calls, memo states,
the exact allocation, elapsed time, and RSS where applicable. The workflow
retains raw stdout/stderr, `/usr/bin/time -v`, source-gate receipts, execution
status, independent-verifier output, binary/source/freeze digests, and a
complete `SHA256SUMS`, uploading artifacts even on failure.

`SIGTERM` and `SIGINT` request a controlled stop; the recursive evaluator checks
that request at the same fixed cadence as the steady-clock deadline and emits a
single flushed `controlled_signal` terminal when it can do so before the outer
kill-after failsafe. Strategy certificates are written to a `.partial` path and
renamed only after the complete DAG is flushed, so a deadline or signal cannot
present truncated bytes as a finished certificate. The independent checker
requires one start, exact million-state progress steps, and exactly one final
result/resource terminal; unknown, reordered, early-timeout, and post-terminal
rows fail closed.

## Non-draw strategy DAG

Any exact non-draw is quarantined unless the solver emits and the independent
Python checker accepts a complete strategy DAG. Each node records
`(mask,deficit,remaining_sum,value)`. A winning node supplies one legal child
with move value `win`; a losing node supplies every legal child and proves all
move values are `loss`. The checker independently recomputes mask sums,
parity, deficit bounds, legal transitions, turn-swap sign changes, terminal
and `sum<deficit` rules, strict mask-cardinality decrease, reachability, and
root completeness. A table digest or one principal variation is insufficient.

Even a checked non-draw remains only a candidate until a fresh duplicate
audit, source mapping, independent mathematical review, and the repository's
normal Lean/release preflight pass. This freeze authorizes no issue, PR, tag,
release, README edit, or other public claim.

## Frozen dispositions

| Event | Disposition |
|---|---|
| source/status/duplicate drift | `PRIOR_ART_OR_STATUS_STRICT_STOP` |
| invariant, small-reference, source-control, exact-count, or digest failure | `INVALID_ARM` |
| N=23 over 38 seconds | `PERFORMANCE_GATE_STOP` |
| N=24 controlled/external timeout, OOM, or abnormal termination | `TIMEOUT_BRACKET` |
| exact N=24 draw | `HOLD_BOUNDED` |
| non-draw without accepted complete DAG | `UNVERIFIED_CANDIDATE` |
| accepted, source-mapped, novelty-cleared non-draw | candidate for later formal/release preflight only |

No result permits an automatic extension to another `N`, compiler, move
order, packing scheme, deadline, or certificate format.
