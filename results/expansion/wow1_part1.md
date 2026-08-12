# WoW I expansion sweep — numeric ids below 450

## Method and progress

This lane covers every row of `corpora/graffiti_wow.json` whose id matches
`^wow-(\d+)` with numeric base id below 450 and whose normalized status begins
with `open` or `unannotated`.  The frozen corpus contains **201** such rows:
154 unannotated, 45 open per Aouchiche–Hansen (2010), and 2 open per the WoW
annotation.  Suffixes such as `(2)` retain their numeric base id and are separate
rows.  Eligibility was counted independently with Python and `jq`.

For each row I test every legible, plausible reading against the required
arsenal: `C5[K_m]` for `m in {2,3,4,5,6,8}`, `C7[K3]`, `C9[K3]`, triangular
graphs `T(7),T(8),T(9)`, and the complement of `C5[K4]`.  A hypothesis that
none of these graphs satisfies is reported `N/A_ARSENAL`; a statement whose
mathematics cannot be recovered without guessing is reported `SKIP_OCR` with
the damaged text quoted.  Historical prose inside an otherwise unannotated row
is respected: an explicit proof or counterexample in that prose is not promoted
to a new open target.

Every apparent violation must first pass the DB-sanity gate under the identical
reading: all connected Graph Atlas graphs through order 7, cycles `C5`–`C9`,
`P7`, Petersen, `K3,3`, `K7`, stars, and complete bipartite calibration graphs.
A failure there is classified as corrupt OCR/misreading, not a kill.  A
gate-surviving violation is recomputed by an independent code path and checked
for novelty on the web before it can be called a counterexample.  Distance and
degree arithmetic is exact; spectral comparisons use a `1e-6` guard band.  Any
CBC/ILP invocation in this lane uses `timeLimit=60`.

Progress below is append-only at conjecture granularity.  Each completed row is
committed and pushed before the next row is recorded.

### wow-5 — HOLD

> average distance is not more than mode of distance + sum of reciprocals of degrees.

Reading `mode of distance` as the modal value among unordered-pair distances
(including diagonal zeroes is the only plausible alternative, and only increases
the right side when zero wins), every arsenal graph satisfies the bound.  The
regular diameter-two members have pair-distance mode 1 or 2 and
`sum_v 1/deg(v)=n/d`; for the carrier this gives
`27/19 <= 1 + 20/11` (and also `<= 2 + 20/11` under the other modal tie rule).
The other required blow-ups and triangular graphs have still larger margins.
All distance averages and reciprocal sums were evaluated exactly as rational
numbers.  No candidate violation arose, so the DB-sanity and novelty gates were
not triggered.

### wow-7 — HOLD

> mode of distance is not more than radius + Randic index.

Under both pair-distance conventions (unordered off-diagonal, or all
distance-matrix coordinates), direct evaluation gives the claimed bound
throughout the arsenal.  For `C5[K4]`, the pair mode is 1 (or 0/1 under matrix
counting), while `rad+R=2+10=12`.  No candidate violation arose.
