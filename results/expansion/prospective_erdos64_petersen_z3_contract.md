# Frozen prospective trial: Erdős 64 cyclic `Z3` lifts of Petersen

Frozen: **2026-08-13 UTC**, after the source/status audit and before any lift
evaluation

Target: current
`FormalConjectures/ErdosProblems/64.lean`

No commit, push, release, issue, PR, or other public action is authorized.

## Source gate

The immutable pre-freeze audit is
`results/expansion/prospective_erdos64_petersen_z3_source_audit.md`.
Its verdict is `LIVE_OPEN_AND_DOMAIN_NOT_COVERED`.

## Frozen base and gauge

Use NetworkX's labelled Petersen graph on vertices `0,...,9`, with sorted
edges

```text
01 04 05 12 16 23 27 34 38 49 57 58 68 69 79.
```

Root at `0` and take the lexicographic BFS spanning tree

```text
01 04 05 12 16 34 49 57 58.
```

Set its oriented low-to-high edge voltages to zero.  In the exact cotree
order

```text
23 27 38 68 69 79
```

assign every tuple in `{0,1,2}^6` except `000000`, lexicographically.  This is
the complete family of **728 connected gauge-fixed cyclic `Z3` voltage
lifts**: over the prime cyclic group, a normalized assignment is connected
exactly when at least one cotree voltage is nonzero.

For a low-to-high base edge `u<v` of voltage `a`, add

```text
(u,s)--(v,(s+a) mod 3), s=0,1,2.
```

No assignment filtering, symmetry quotient, retuning, alternate tree, base
replacement, or higher-sheet family is permitted after this freeze.

## Prediction and success coordinate

A base cycle with nonzero total `Z3` voltage becomes a cycle three times as
long.  The prospective question is whether some assignment simultaneously
removes every simple cycle of lengths `4`, `8`, and `16`.  On 30 vertices
these are exactly the possible power-of-two cycle lengths allowed by the
formal statement (`32` already exceeds the order).  The lift should remain
simple, connected, cubic, and hence have minimum degree three.

The prediction does **not** assume every globally nonzero assignment makes
every base 8-cycle nonzero.

## Mandatory database gate

Before constructing any lift:

1. verify the frozen Petersen label, simplicity, connectedness, cubic degree
   sequence, and an explicit simple 8-cycle;
2. validate the primary exact-length cycle oracle against an independent
   subset/degree-two oracle on every connected Graph Atlas graph of order at
   most seven for each applicable target length among `4,8,16`;
3. require zero mismatches and zero timeouts.

Any failure is `GATE_FAIL` and locks the family.

## Candidate evaluation

For each assignment, append and flush one JSONL row before continuing.  Check
construction size `(n,m)=(30,45)`, simplicity, connectedness, degree multiset,
and minimum degree.  Enumerate simple cycles only at lengths `4`, `8`, and
`16`, stopping a length search at its first canonical witness.  A candidate
crosses only when all three exact searches return absent.

Every OS process and phase is capped at 60 seconds.  A timeout is unresolved,
never absence evidence.

## Independent crossing audit

Any apparent crossing triggers, before any novelty claim:

- reconstruction by a separately written voltage-lift routine;
- equality of canonical edge lists;
- absence checks for `4`, `8`, and `16` by an independent exact
  subset/degree-two oracle;
- fresh live source/status and literature/prior-art search.

Final classifications are `GATE_FAIL`, `HOLD_BOUNDED`,
`HOLD_WITH_TIMEOUTS`, or `CROSSING_VERIFIED`.  No public action follows from
any classification in this lane.

