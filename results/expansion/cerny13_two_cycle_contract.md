# Černý C13 two-cycle trial contract

This file is a post-run transcription of the contract frozen in agent messages
before evaluation. It is not a Git-preregistered contract and cannot support a
held-out claim. The complete development trial remains valid because neither
implementation adapted the six-row family after seeing a result.

## Exact target

At `google-deepmind/formal-conjectures@7a38c469`, refute the intended positive
side of `CernyConjecture.cerny_conjecture` by finding one finite synchronizing
DFA whose shortest reset word is longer than `(n-1)^2`.

For `n=13`, use residual

```text
R(M) = 144 - shortestResetLength(M).
```

The conjecture holds when `R >= 0`; a candidate counterexample has `R < 0`.

## Database calibration

Compute the standard binary Černý automata `C_n` for every `n=3,...,12` and
require the exact shortest reset lengths `(n-1)^2`, with replayable reset words.

## Frozen family

States are `0,...,12`. For each `d=1,...,6`:

1. start with cycle letter `a(i)=i+1 mod 13`;
2. swap the two successor values `a(d)` and `a(12)`, producing cycles of
   lengths `d+1` and `12-d`;
3. set `b(12)=0` and `b(1)=0`, fixing every other state under `b`;
4. change no other transition.

Evaluate exactly those six rows, in that order, by full power-automaton BFS.
Do not add a row, change a transition, choose a different split, or switch
solver after the first result. Independently verify by reverse BFS over all
8,191 nonempty state subsets and directly replay every shortest word.

## Prediction and bounds

The swap deliberately leaves the circular/one-cluster proof domain. The
prospective prediction was that splitting the equality carrier could decrease
`R` while preserving synchronization. The risk was that the second merge in
`b` would create an easy contraction; this must be measured rather than hidden.

Hash the six transition tables before evaluation. Cap the complete process at
60 seconds. A negative residual stops all adaptation and starts independent
certificate and novelty review. A safe table closes this exact family as
`HOLD_BOUNDED` or a structural safe-direction law.
