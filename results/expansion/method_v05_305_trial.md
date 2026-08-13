# Method v0.5 WOWII 305 trial audit

Date: **2026-08-13 UTC**

Frozen selection commit: `925d56dea3aaa6246560f42890e1d6fc6ee5c3a8`

Disposition: **STOPPED — FROZEN CALIBRATION DISAGREEMENT**

This run does **not** have a Method outcome such as `HOLD_BOUNDED` or a
counterexample. The mandatory database gate fails an explicit calibration in
the selection contract, so the subsequently evaluated family rows are
procedurally inadmissible and excluded from the evidence ledger.

## Exact gate result

The primary bitset/subset-enumeration implementation evaluated all 1,079
explicit gate rows in fresh processes. The independent NetworkX/set plus CBC
implementation replayed all 1,079. Both recorded explicit total-dominating
witnesses, proved their minimality independently, and agreed on every exact
complement edge-neighborhood multiset and extremizing edge.

The frozen contract requires the calibration

```text
C5[K2]: gamma_t = 3, M = 6, R305 = 1.
```

Both implementations instead obtain

```text
complement edge-neighborhood multiset = [8, 8, 8, 8, 8,
                                         8, 8, 8, 8, 8,
                                         8, 8, 8, 8, 8,
                                         8, 8, 8, 8, 8]
m = M = 8
gamma_t = 3
T306 = 2 floor(8/2) - 3 = 5
R305 = ceil(2*8/3) - 3 = 3.
```

This follows directly from the frozen reading. In the complement of
`C5[K2]`, each edge joins two consecutive two-vertex fibres; the union of the
endpoints' open neighborhoods contains four complete fibres, hence eight
vertices. The endpoints are included because they are adjacent to each other.
The printed expected value `M=6` is exactly what results if those two endpoints
are excluded from the edge neighborhood, contrary to the contract's explicit
endpoint-including sentence. This reading mismatch is the exact cause of the
failed calibration.

No applicable control crossed WOWII 305 and all applicable controls had
`T306 >= 0`, but exact reproduction of the printed unit residual is itself a
mandatory gate condition. Its failure requires a strict stop before the grid.

## Procedurally excluded grid data

The coordinator lacked the calibration assertion during execution and
therefore incorrectly unlocked the grid after the two computational ledgers
agreed. It constructed and evaluated all 28 frozen labelled rows. All 28 were
distinct under isomorphism, and the independent implementation reproduced
every row exactly. These data are retained for auditability but are marked
`EXCLUDED_PROTOCOL_VIOLATION`; they do not support `HOLD_BOUNDED`.

The excluded rows uniformly gave

```text
gamma_t(G(s,d)) = 2
m(G(s,d)) = M(G(s,d)) = 4d
T306 = 4d - 2
R305 = ceil(8d/3) - 2.
```

Their observed minimum residual was `1`, attained exactly at

```text
(s,d) = (2,1), (3,1), (4,1), (5,1), (6,1), (7,1), (8,1).
```

Again, that is an excluded observation, not a valid bounded-hold outcome.

## Supervision and artifacts

- Internal worker/optimizer deadline: 55 seconds.
- External fresh-process cap: 60 seconds per graph.
- Every JSONL row was appended, flushed, and `fsync`ed independently.
- No mathematical timeout, negative `T306`, implementation disagreement, or
  unexpected control crossing occurred.
- Two implementation bookkeeping failures occurred before producing affected
  invariants (Python 3.9 population-count compatibility and explicit `K1,1`
  hypothesis handling); both stops and corrections are preserved in JSONL.
- The final audit exposed the missing frozen-calibration assertion. The script
  now hard-checks the tuple before gate completion and again before grid
  unlock, so a clean rerun would stop at `C5[K2]` and keep the prospective grid
  locked. Audit chronology permits only the 28 already-preserved excluded rows
  preceding this incident marker; any later grid append without a valid gate
  and replay fails the audit.
- No adaptive family, bound extension, browsing, upstream operation, release,
  README edit, commit, or push occurred.

Primary ledger: `results/expansion/method_v05_305_trial.jsonl`

Independent ledger: `results/expansion/method_v05_305_trial.verify.jsonl`
