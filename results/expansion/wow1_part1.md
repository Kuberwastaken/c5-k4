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

### wow-8 — HOLD

> mode of distance is not more than average distance + Randic index.

Both plausible modal-distance conventions hold throughout the arsenal.  On
`C5[K4]`, the left side is 1 (with a possible zero/one tie if diagonal entries
are included) and the exact right side is `27/19+10=217/19`.  No candidate
violation arose.

### wow-10 — HOLD — source says proved

> average temperature is not more than rank. … This conjecture is correct.

With `temp(v)=deg(v)/(n-deg(v))` and adjacency-matrix rank, every arsenal graph
holds.  The low-rank complement of `C5[K4]` gives `2/3 <= 5`; the carrier gives
`11/9 <= 20`.  The historical row itself says the result is correct.

### wow-12 — HOLD

> radius is not more than 1 + Randic index.

Using `R=sum_{uv in E}1/sqrt(deg(u)deg(v))`, all arsenal graphs hold.  The
carrier gives `2 <= 11`; `C9[K3]`, the largest-radius arsenal member, gives
`4 <= 29/2`.  No candidate violation arose.

### wow-14 — HOLD

> radius is not more than average distance + Randic Index.

All arsenal graphs satisfy the standard reading.  For `C5[K4]`,
`2 <= 27/19+10`; for `C9[K3]`, `4 <= 31/13+27/2`.  Distance terms were
computed as exact rationals.

### wow-20 — HOLD

> The number of positive eigenvalues of a graph is not more than their sum.

Adjacency eigenvalues were counted with the `1e-6` zero guard.  Every arsenal
graph holds.  The carrier has 3 positive eigenvalues and positive-eigenvalue sum
approximately `21.944272`; no comparison lies within the guard band.

### wow-21 — HOLD

> The number of negative eigenvalues of a graph is not more than the sum of its positive eigenvalues.

Adjacency inertia uses the `1e-6` zero guard.  All arsenal graphs hold.  The
carrier gives `17 <= 21.944272…`; its complement has only 2 genuinely negative
eigenvalues (15 numerical zeroes are excluded), against positive sum
`12.944272…`.  No near-boundary case arose.

### wow-27 — HOLD — historical support recorded

> The standard deviation of the degree sequence < Randic.

Every arsenal member is regular, so its degree standard deviation is exactly
zero and the bound holds.  The row's truncated commentary records supporting
proof results; it is not treated as a new open claim.

### wow-32 — HOLD; alternate reading rejected

> The negative of the largest negative distance eigenvalue is not more than the matching number.

The Aouchiche–Hansen spectral-order reading, `-max{lambda<0} <= mu`, holds on
all arsenal graphs (left side 1 on the cycle blow-ups). Reading “largest” as
largest magnitude instead fails on `C7[K3]` and `C9[K3]`, but contradicts the
survey's explicit formula and is not a faithful reading.

<!-- NEXT -->
