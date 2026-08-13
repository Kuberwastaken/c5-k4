# Catch-Up N=23,24 exact minimax contract

**Evidence split:** development  
**Upstream:** `google-deepmind/formal-conjectures@7a38c469ec329d0c97c068e03c58834f61628e7e`  
**Frozen contract digest from pre-evaluation literal JSON:** `ab99508a9f5b924088897dbaf967c8f7125ae2380c5e061e7e9721c76a999403`

This declaration has an exact finite negation: an `N` with even triangular sum
whose game-theoretic value is win or loss rather than draw. A complete minimax
strategy DAG is a replayable finite certificate.

## Source semantics

The solver reproduces `CatchUp.valueAux` exactly:

- player one takes exactly one counter on the first move;
- afterward, a player continues picking while strictly behind and passes as
  soon as their score reaches or exceeds the opponent's;
- if all remaining counters cannot close the deficit, the current player loses;
- outcomes are ordered win, draw, loss under optimal play.

After the first move, absolute scores are eliminated without changing the
game. If `delta=opponent-current >= 0`, the normalized recurrence is:

```text
post(mask, delta):
  empty: draw iff delta=0, else loss
  sum(mask)<delta: loss
  for x in mask, ascending:
    x>=delta: value = -post(mask-x, x-delta)
    x< delta: value =  post(mask-x, delta-x)
  return the best value
```

The root tries every first pick `x` and returns `-post(full-x,x)`.

## Frozen rows and controls

Calibration is exactly

```text
N = 3,4,7,8,11,12,15,16,19,20,
```

all of which must return draw. Development rows are exactly `N=23`, followed
by `N=24` only as a separately isolated workflow job; neither result changes
the other row's semantics or search order. The transition is the source's
natural `N -> N+4` continuation beyond its exact computation through 20.

Use ascending move order, deterministic SplitMix hashing, linear probing, and
a fixed maximum 0.70 load. Emit JSONL at start, each million insertions, each
rehash, result, and allocation failure. Record memo size/capacity/load, calls,
RSS, elapsed time, exit code, and `/usr/bin/time -v` output.

Every process has an external 60-second wall-clock cap. Timeout, allocation
failure, capacity exhaustion, or external termination is a resource bracket,
never a draw or hold. No alternative move order, solver, capacity-dependent
pruning, added `N`, or post-result parameter change belongs to this contract.

If either development row is non-draw, stop publication work until a second
normalized implementation reproduces it and a replayable winning-strategy DAG
passes an independent checker.

## Status and overlap

The 2015 source reports exact minimax only through `N=20`; its `N=23,24,27,28`
rows are Monte Carlo estimates. DeepMind issue 1324 and merged PR 1325 add the
statement only. Live issue 4834 proposes normalized APIs and `N -> N+4`
helpers, but explicitly reports no new exact case, reduction, or search result.
No standalone solution or counterexample repository was found.

An earlier node-heavy implementation passed every calibration but terminated
during `N=23` without a verdict. The exact cause was not captured, so its
outcome is `RESOURCE_TERMINATION_UNKNOWN`, not a claimed OOM. This normalized
flat-table replay is the separately logged semantics-preserving resource retry.
