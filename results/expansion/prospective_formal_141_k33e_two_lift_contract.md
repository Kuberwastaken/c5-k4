# Frozen prospective trial: WOWII #141 two-lifts of `K3,3-e`

Frozen: 2026-08-13 UTC, before development-family evaluation

Source commit: `4ea3913f552448ff46c7adaa496c9ab665964527`

Target: current
`FormalConjectures/WrittenOnTheWallII/GraphConjecture141.lean`

No commit, release, push, issue, PR, or other public action is authorized.

## Seed and prospective mechanism

The sole seed is the equality output of the preceding frozen Whitney-switch
trial:

```text
labelled graph6 EHvO, isomorphic to Atlas EhUg = K3,3 minus one edge,
edges 04 05 12 14 15 23 34 35,
(n,m,girth,lambda_max,tree,target,R141) = (6,8,4,3,4,4,0).
```

This tuple and its explicit Atlas isomorphism occur in the immutable preceding
ledger, whose SHA-256 is
`6c1395d6c1f75bdf4541c56e73f87c407790e1c0c8cc274a22e8d72abaf9056e`.

The selected mechanism is the complete finite family of connected gauge-fixed
two-sheet lifts.  A graph cover preserves every open neighborhood up to
bijection, hence preserves all local independence values and
`lambda_max = 3`.  Nonzero cycle voltage can turn a base 4-cycle into an
8-cycle, so this is a direct attempt to increase the integer girth term while
pinning the local term.  It is not an Atlas search.

## Frozen family

Use root zero and lexicographic BFS.  Set voltage zero on the five BFS-tree
edges

```text
04 05 14 34 12
```

and assign bits `(x15,x23,x35)` to the three cotree edges in this exact order.
Evaluate exactly the seven nonzero bit strings in lexicographic order:

```text
001, 010, 011, 100, 101, 110, 111.
```

For every base edge `uv` with voltage `x`, add lift edges

```text
(u,s)--(v,s xor x), s in {0,1}.
```

This produces seven labelled 12-vertex, 16-edge candidates.  No zero-voltage
disconnected lift, alternate spanning tree, switching-class representative,
higher sheet number, seed replacement, or post-result retuning is allowed.

The frozen success coordinate is

```text
girth(lift) >= 6,
lambda_max(lift) = 3,
target(lift) >= 5.
```

The trial does not predict that a crossing must occur.  It predicts that the
family can raise the target without paying in `lambda_max`; exact tree values
decide whether the move gains relative to the induced-tree coordinate.

## Mandatory gate

Before constructing a candidate, replay the same 1,057 connected Atlas and
named controls used by the preceding #141 lanes.  Compare every exact tuple
and maximum-tree witness against the frozen S4 gate ledger.  A negative
residual, mismatch, invalid witness, or timeout is `GATE_FAIL` and locks the
family.

Revalidate the seed edge list, exact tuple, and explicit isomorphism to the
frozen `atlas:EhUg` row before construction.

## Candidate verification and exact tree audit

For every voltage row, record and flush before moving to the next row:

- graph6, order, size, simplicity, connectedness, degree multiset;
- the exact covering bijection at every lifted vertex;
- every base 4-cycle and its voltage parity;
- exact girth and a replayed shortest-cycle witness;
- every local-neighborhood independence value and witness;
- target and exact maximum induced-tree order.

Run the decision-first target-tree search before maximum optimization.  Record
and replay the first target witness.  Because this trial explicitly studies
the relative motion of the tree coordinate, then compute the exact maximum by
descending subsets.  Independently audit the exact maximum with a separate
bitmask enumeration in increasing cardinality that proves every larger subset
non-tree and replays a maximum witness.  Any disagreement is `GATE_FAIL`.

Canonical isomorphism is not trusted as a verdict shortcut: pairwise
isomorphism classes are recorded only after every labelled candidate has its
own invariant and witness audit.

Every OS process and exact phase is capped at 60 seconds, with internal phase
caps at most 55 seconds.  Timeouts are unresolved, never evidence of a hold.
JSONL rows are append-only and flushed immediately.

Strict final classifications are:

- `GATE_FAIL`;
- `NO_TARGET_RAISING_CANDIDATES` if all exact girths remain four;
- `HOLD_BOUNDED` if at least one target rises and every evaluated residual is
  nonnegative with no timeout;
- `HOLD_WITH_TIMEOUTS` if no crossing is verified and any candidate times out;
- `CROSSING_VERIFIED` only after a negative exact residual and independent
  witness/value replay.

Source/status/novelty work is forbidden unless the final classification is
`CROSSING_VERIFIED`.
