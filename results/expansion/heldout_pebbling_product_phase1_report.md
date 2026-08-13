# Graph pebbling product Phase 1 — threshold-shell result

Date: **2026-08-13 UTC**
Outcome: **`PREDICTION_CONFIRMED`**

## Result

All **4,032** preregistered support-63 configurations on the labelled Lemke
square `L □ L` are exactly root-solvable. There were no timeouts, oracle
mismatches, or candidate lower bounds.

For each root `r` and extra-pebble location `x != r`, the evaluator selected
the lexicographically first shortest path from `x` to `r`. The extra pebble at
`x` pairs with its existing singleton; each move deposits one pebble onto the
next vertex's singleton, so the pair relays along the path and the final move
places one pebble on `r`.

Every evaluated row matched the frozen exact prediction:

```text
move count = dist(x,r)
final root count = 1
final total = 64 - dist(x,r)
```

The distance distribution was:

| distance | states |
|---:|---:|
| 1 | 416 |
| 2 | 1,124 |
| 3 | 1,488 |
| 4 | 888 |
| 5 | 112 |
| 6 | 4 |

This is a complete bounded hold only for the frozen single-extra shell. It
does not determine `pi(L □ L)` and is not evidence that every 64-pebble
distribution is solvable.

## Gates and independent checks

Before product construction, a second exact oracle performed full BFS over
the finite configuration transition graph for all corresponding states of
`K2`, `P3`, `K3`, and `C4`. It agreed with the primary shortest-path replay on
every threshold-shell state and rejected every immobile `n-1`-pebble lower
state: **38 calibration checks** passed.

The first activation attempt stopped with zero states when concurrent commit
integration normalized trailing whitespace in the Phase 0 contract and
changed its byte digest. That stop and the semantic-no-change refresh are
preserved in the ledger before the unlock.

Finalization freshly replayed all **4,032** literal move sequences from their
stored initial distributions and 208-edge labelled graphs. Every row stores
the complete edge list, 64-entry factor role map, initial/final distributions,
intermediate states, path, moves, and labelled digests.

Eight frozen batches of 504 states completed. The maximum recorded batch time
was 0.148 seconds; every process was externally capped at 60 seconds and used
a 55-second internal deadline.

## Artifacts

- Phase 1 addendum:
  `results/expansion/heldout_pebbling_product_phase1_addendum.md`
- Append-only ledger:
  `results/expansion/heldout_pebbling_product_phase1_ledger.jsonl`
- Exact evaluator:
  `scripts/heldout_pebbling_product_phase1.py`

Final ledger audit: 4,050 valid JSON rows, 4,032 consecutive state rows,
208 labelled edges and 64 roles in every state row, zero timeout rows, zero
candidate rows. Final ledger SHA-256 before this report was
`0f1c836f0fabaef495de57cfd5ecd6e5a14467445cfe7d124d858fabe0bee238`.

No commit, push, issue, PR, release, or other public action was performed by
this lane.
