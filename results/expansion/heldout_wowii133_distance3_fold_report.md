# WOWII 133 distance-three fold: prospective trial result

Date: **2026-08-13 UTC**
Primary outcome: **`GATE_FAIL`**
Candidate evaluations: **0**

## Outcome

The frozen family never unlocked. The exact semantic microfixture for `C4`
returned

```text
(path, radius, floor(l), hasC4, residual) = (3, 2, 2, true, 0),
```

while the script's preregistered calibration asserted

```text
(3, 2, 1, true, 0).
```

The incorrect coordinate is `floor(l)`: each vertex of `C4` has two
nonadjacent neighbors, so every neighborhood independence number is two and
the average (hence its floor) is two. The residual happened to remain zero
because the C4-present branch uses exponent zero, but METHOD.md treats a
wrong calibration assertion as a hard gate failure regardless of downstream
numerical coincidence.

Accordingly the distance-three-fold constructor remained locked. No Heawood
pair was folded, no candidate graph was profiled, and this trial contributes
no hold, crossing, theorem-domain row, or prediction test. Correcting the
fixture and running the family would require a separately frozen trial; it
cannot be folded into this one.

## Gates completed before failure

- Current upstream was refreshed at
  `d16e05aded22b8c467a0a27c14b2311f53185006`.
- `GraphConjecture133.lean` blob
  `9a8dca984e87efc2fb1ffd68f5d4185e4645a8e8` still contains
  `conjecture133` as `research open`.
- The literal Lean reading was frozen as `UNAMBIGUOUS`.
- Local history showed no universal proof and no prior distance-three vertex
  fold. The proposed quotient would be noncubic (one merged degree-six
  vertex), so the cubic closure did not itself reject the family.
- Exact GitHub searches found no #133 resolution issue or open PR; the only
  directly related repository PRs were the merged source-addition #3820 and
  definition-fix #4282. Exact-formula web searches found no prior
  distance-three-fold result.
- The `P4` microfixture passed exactly as `(4,2,1,false,1)`.

The full connected Graph Atlas and named-control database gate did **not** run,
because the earlier mandatory semantic microfixture failed first.

## Durable artifacts

- Frozen contract:
  `results/expansion/heldout_wowii133_distance3_fold_contract.md`
- Append-only ledger:
  `results/expansion/heldout_wowii133_distance3_fold_ledger.jsonl`
- Evaluator (constructor remains unused):
  `scripts/heldout_wowii133_distance3_fold.py`

Every invoked process was externally capped at 60 seconds. No commit, push,
issue, PR, release, or other public action was performed by this lane.
