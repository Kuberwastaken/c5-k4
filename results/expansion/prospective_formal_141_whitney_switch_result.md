# WOWII #141 unique-triangle Whitney-switch result

Date: **2026-08-13 UTC**

Verdict: **HOLD_BOUNDED — the frozen move reaches equality, not a crossing**

No public action was taken.

## Frozen selection

The seed was selected strictly from the pre-existing 1,057-control #141
ledger, not from a generated family.  The immutable rule chose the first
unit-residual, unique-triangle Atlas graph with `lambda_max = Delta`:

```text
atlas:EhdW
graph6 = EhdW
(n,m,girth,lambda_max,tree,target,R141) = (6,8,3,3,4,3,1).
```

This is a different seed from `complement(C5[K3])`.  The frozen transformation
was a single local, degree-preserving Whitney switch, not a cover:

```text
delete 01 and 45; add 05 and 14.
```

The prediction was that the move would destroy the seed's unique triangle,
raise girth from three to four, pin `lambda_max` and `tree`, and consume the
one unit of residual.

## Gate and exact result

The full database-sanity gate replayed all 1,057 controls in **3.206 s**:

```text
completed = 1057 / 1057
baseline mismatches = 0
negative controls = 0
witness failures = 0
timeouts = 0
gate = PASS.
```

The labelled output has graph6 `EHvO` and exact tuple

```text
(n,m,girth,lambda_max,tree,target,R141) = (6,8,4,3,4,4,0).
```

The girth witness is `0-5-1-4-0`.  All open-neighborhood independence values
and witnesses replay, and the degree multiset remains
`(2,2,3,3,3,3)`.  The decision-first target-tree search found
`[0,1,2,4]` after four states.

The exact upper certificate for `tree = 4` requires no forbidden post-witness
optimization: the output is explicitly isomorphic to the already gated Atlas
control `atlas:EhUg` (`K3,3` minus one edge).  The candidate-to-control map is

```text
0->0, 1->2, 2->3, 3->4, 4->1, 5->5.
```

It transports the frozen maximum-tree witness back to `[0,4,1,2]`.
Three append-only candidate replays were made while adding the isomorphism and
final-classification rows; all deterministic candidate fields agreed exactly.

## Interpretation

The local invariant-navigation prediction was exact: one degree-preserving
switch moved a unit-residual graph onto the #141 wall while holding both
`lambda_max` and the maximum induced-tree order fixed.  It did **not** disprove
#141, so source/status/novelty work was correctly not triggered.

This is useful negative evidence.  The move terminates at the familiar
`K3,3-e` equality geometry, and no second switch is authorized by this frozen
trial.  In particular, it suggests that triangle elimination can spend the
available residual exactly, but does not by itself create the missing deficit.

Artifacts:

- `results/expansion/prospective_formal_141_whitney_switch_contract.md`;
- `results/expansion/prospective_formal_141_whitney_switch_ledger.jsonl`;
- `scripts/prospective_formal_141_whitney_switch.py`.
