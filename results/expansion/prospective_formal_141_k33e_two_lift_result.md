# WOWII #141 `K3,3-e` two-lift result

Date: **2026-08-13 UTC**

Verdict: **NO_TARGET_RAISING_CANDIDATES**

No public action was taken.

## Frozen mechanism

Starting from the newly reached equality graph

```text
EHvO ~= EhUg = K3,3-e,
(girth,lambda_max,tree,target,R141) = (4,3,4,4,0),
```

the trial froze the complete seven-member family of connected, gauge-fixed
two-sheet lifts.  The mechanism was chosen because covering maps preserve each
open neighborhood while nonzero cycle voltage can lengthen a base 4-cycle.
Thus it attempted to raise the girth contribution to the #141 target while
pinning `lambda_max = 3`.

The three cotree voltages were `(x15,x23,x35)`, evaluated without retuning as

```text
001, 010, 011, 100, 101, 110, 111.
```

## Gate

The full database gate passed before family evaluation:

```text
controls = 1057 / 1057
baseline mismatches = 0
negative residuals = 0
witness failures = 0
timeouts = 0
gate time = 2.929 s.
```

The seed audit independently recovered its exact tuple and explicit
isomorphism to the frozen `atlas:EhUg` row.

## Exact result

Every one of the seven labelled lifts is simple, connected, and a valid local
two-cover.  All covering bijections, girth witnesses, local-independence
witnesses, target-tree witnesses, and exact maximum-tree witnesses replayed.
The primary descending-subset optimizer and independent all-subset bitmask
audit agreed on every row.

All seven candidates have the same exact invariant tuple:

```text
(n,m,girth,lambda_max,tree,target,R141) = (12,16,4,3,9,4,5).
```

They form three isomorphism classes:

```text
{001,011,100,110}, {010,101}, {111}.
```

The exact family phase took 0.128 seconds with no timeout or failed audit.

## Structural closure

The failure to raise girth has a complete parity explanation.  The five base
4-cycles have voltage forms

```text
0415: x15
0435: x35
1234: x23
1235: x15 xor x23 xor x35
1435: x15 xor x35.
```

Making the first three cycles odd forces
`x15 = x23 = x35 = 1`.  The last cycle then has parity
`x15 xor x35 = 0`, so it lifts to 4-cycles.  Consequently **every** two-sheet
lift of `K3,3-e`, not merely the seven representatives as an empirical matter,
retains girth four.

This closes the selected mechanism before the induced-tree tradeoff can become
relevant.  The covers actually increase the exact tree coordinate from four to
nine while leaving the target at four.

## Logged implementation incident

The first family invocation stopped before emitting any candidate because the
host Python lacks `int.bit_count`.  The frozen family and contract were not
changed; the popcount primitive was replaced with the exact compatible
expression `bin(x).count("1")`, the incident was appended to the ledger, and
the same seven rows were executed.

Artifacts:

- `results/expansion/prospective_formal_141_k33e_two_lift_contract.md`;
- `results/expansion/prospective_formal_141_k33e_two_lift_ledger.jsonl`;
- `scripts/prospective_formal_141_k33e_two_lift.py`.
