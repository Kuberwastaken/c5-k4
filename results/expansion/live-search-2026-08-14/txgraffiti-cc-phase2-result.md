# TxGraffiti C-C phase two: extremal-reservoir result

Date: **2026-08-14 UTC**

Evidence split: **DEVELOPMENT**

Final status: **ZERO_BOUNDED_WITH_ALLOCATION_DEFECT**

Phase two tested the theorem-backed construction frozen in
[`txgraffiti-cc-phase2.md`](txgraffiti-cc-phase2.md).  All three workers
completed within the hard 60-second cap.  Every stream passes the strict
Method v1.5 hash-chain and nauty-canonicalization linter.

## Exact denominator

| Frozen arm | Proposed | Exact | Residual zero | Residual one | Residual two | Crossing |
|---|---:|---:|---:|---:|---:|---:|
| `CATALOGUE` | 10 | 10 | 3 | 7 | 0 | 0 |
| `GENERIC` | 40 | 40 | 0 | 20 | 20 | 0 |
| `WALL_NAVIGATION` | 48 | 48 | 0 | 46 | 2 | 0 |
| **Total** | **98** | **98** | **3** | **73** | **22** | **0** |

For every row, the displayed subdivision matching and the cubic counting
bound certify `mu*(G)=3t`.  The only optimized invariant was the child's exact
independent domination number.  No row crossed `3t-i(G)<0`, so there is no
candidate, formal-certificate task, release, or novelty claim.

The fresh generic coordinates moved strictly to the safe side:

```text
t=5: 15 rows with (i,mu*)=(14,15), 3 with (13,15)
t=6:  5 rows with (17,18),       17 with (16,18)
```

The fixed catalogue retained equality only at the smallest coordinates.  The
larger named examples were safe by one.

## Allocation defect discovered live

The wall worker began with two seeds at each of `t=3,4,5`.  All six were safe,
so the beam's frozen tie-break `i(G)` descending favored the largest order.
It then spent 42 of its 48 exact evaluations on `t=5` children before the
internal deadline:

```text
t=3:  2 exact rows, both residual 1
t=4:  2 exact rows, both residual 1
t=5: 42 residual-1 rows and 2 residual-2 rows
```

Raw `i(G)` is not comparable across orders.  Using it as a global tie-break
therefore created an order bias and prevented the arm from testing its own
smaller-coordinate neighborhoods.  The ledger remains valid, but the wall
arm is not evidence that all three frozen coordinates received meaningful
navigation depth.

## Revision forced by the result

The structural family remains useful: it solves replacement-set collapse by
fixing `mu*` exactly.  The next trial should retain that theorem but change the
allocation rule:

1. stratify the beam and wall-time budget by `t`;
2. compare residual first only within a coordinate;
3. concentrate exhaustive or near-exhaustive pairing search at the smallest
   equality-bearing coordinate before scaling order; and
4. do not resample the now-strict objective-blind `t=5,6` generic arm.

This is a method correction, not a reinterpretation of phase two.  Any such
run requires a new freeze and fresh ledgers.

## Artifacts

- [`txgraffiti-cc-phase2-manifest.json`](txgraffiti-cc-phase2-manifest.json)
- [`../../../scripts/search_txgraffiti_cc_phase2.py`](../../../scripts/search_txgraffiti_cc_phase2.py)
- [`txgraffiti-cc-phase2-ledgers/`](txgraffiti-cc-phase2-ledgers/)

Across all three phases, 395 exact graphs have now been retained with zero
crossings.  This remains a bounded search result, not a proof of the
conjecture.
