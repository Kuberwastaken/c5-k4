# Černý C13 two-cycle surgery

**Outcome:** `HOLD_BOUNDED`  
**DeepMind base:** `7a38c469ec329d0c97c068e03c58834f61628e7e`  
**Frozen family digest:** `706fc66e813ddbc355c8246a0a38e37b9507ec84f749443b2ac0a2647f2ef107`

The exact Lean declaration is a universal finite-DFA statement. One finite
synchronizing automaton whose shortest reset word exceeds `(n-1)^2` would
literally refute its intended positive side, so this target passes Method
v1.0's finite-certificate gate.

## Status and overlap gate

The classical conjecture remains open. DeepMind issue 3905 and merged PR 3906
add the statement only; no proof, disproof, or competing upstream attempt was
found. The c5-k4 history had no prior Černý lane.

The standalone `jakubrollo/mathhandoff` repository contains an open two-cycle
Černý program with claimed structural results and finite work, but no accepted
attestations and no coverage of this exact frozen six-row family. That is
important overlap and calibration, not a duplicate resolution claim.

## Exact trial

The database gate reproduced the standard `C_n` reset thresholds for every
`n=3,...,12`:

```text
4, 9, 16, 25, 36, 49, 64, 81, 100, 121 = (n-1)^2.
```

For each `d=1,...,6`, the `n=13` cycle letter was split into cycles of lengths
`d+1` and `12-d`, while the contraction letter merged both states 1 and 12
into 0. The family left the circular/one-cluster proof domain and was frozen
before evaluation.

| d | cycle lengths | shortest reset | residual `144-L` | shortest word |
|---:|---:|---:|---:|---|
| 1 | 2, 11 | 21 | 123 | `babababababababababab` |
| 2 | 3, 10 | 19 | 125 | `bababababababababab` |
| 3 | 4, 9 | 17 | 127 | `babababababababab` |
| 4 | 5, 8 | 15 | 129 | `bababababababab` |
| 5 | 6, 7 | 13 | 131 | `babababababab` |
| 6 | 7, 6 | 11 | 133 | `bababababab` |

The primary forward BFS completed in about 0.05 seconds. An independent full
8,191-subset transition graph and reverse BFS reproduced all six minima and
directly replayed every reset word to state 0. Both stayed far below the
60-second cap.

The two implementations use different canonical row encodings, so individual
artifact hashes differ; the transition tables, lengths, residuals, words, and
targets agree exactly. The committed replay script defines the repository's
canonical family and row digests.

## Structural result

The intended wall separation has the wrong sign. Adding `b(1)=0` lowers the
rank of the contraction letter from 12 to 11. After the successor swap splits
the cycle, alternating `ba` repeatedly compresses the active state set. Across
the complete family the exact observed law is

```text
shortestResetLength(M_d) = 23 - 2d.
```

Thus the operation does not merely fail to cross the quadratic wall; it
destroys the slow-synchronization geometry that made `C13` tight.

This exact family is closed. A future Černý transformation must preserve a
rank-12 defect-one letter and the slow pair-compression mechanism while leaving
the circular/one-cluster proof domains. It may not remove the second merge from
these rows post hoc and call that the same trial.

No counterexample, Lean disproof, issue, PR, or release is authorized.
