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

### wow-54 — HOLD — historically proved

Regular-graph bound `n/d <= rank(A)` holds throughout: `C5[K4]` gives `20/11 <= 20`, and its rank-5 complement gives `5/2 <= 5`. The row explicitly records independent proofs.

### wow-63 — HOLD where applicable

The inherited triangle-free hypothesis selects only `complement(C5[K4])`; its average degree is 8 and its Randić index is 10. All other arsenal members contain triangles.

### wow-70 — RETRO-VIOLATION — already refuted

On the natural clique-coordinate reading, `C5[K4]` has `chi=10 > 8=max frequency`; the cycle blow-ups similarly fail. The same row explicitly records Staton's counterexample and Rödl's arbitrarily large gaps, so this is only a retro-witness.

### wow-71 — HOLD — historically proved

Every arsenal graph is bridgeless, so the cut-edge count is zero. The row explicitly records proofs by Shearer and Staton.

### wow-72 — HOLD — historically proved

All arsenal graphs are regular; direct temperature/depth evaluation holds (carrier `11/9 <= 18`). The row records independent proofs.

### wow-73 — HOLD

Every arsenal graph has no cut vertices, so the cut-vertex coordinate vector is empty/zero and its maximum is 0, at most `alpha`.

### wow-74 — HOLD

Every arsenal graph has no cut vertices, hence the relevant maximum coordinate is 0, at most the positive matching number.

### wow-75 — HOLD

Every arsenal graph has no cut vertices, hence the cut-vertex-coordinate variance is 0, at most `alpha`.

### wow-76 — HOLD

Every arsenal graph has no cut vertices; under the zero-vector convention its mode is 0, at most the matching number.

### wow-77 — HOLD

For all maximal/maximum-independent-set coordinate readings, the modal coordinate is at most the diameter (at most 4), whereas `n-residue` is at least 8 in the arsenal.

### wow-78 — HOLD

The maximal-independent-set coordinate mode is at most 4, while the smallest arsenal Randić index is 5.

### wow-80 — HOLD — historically proved

The coordinate mean is at most the diameter (at most 4), while `n-residue>=8`; the row also cites its proof from #79 and #98.

### wow-82 — HOLD — historically validated

Coordinate range for any maximal clique is at most `diameter+1<=5`, and `max Even>=5`; the row itself says the conjecture is valid for all maximal cliques.

### wow-83 — HOLD under surviving reading

The row says the unrestricted strongest version was refuted and retains dominating cliques. For a dominating clique its coordinate scope is at most 4, while `max Even>=5`.

### wow-84 — HOLD

A distance-to-clique coordinate vector supported in `[0,diam]` has variance at most `diam^2/4<=4`; every arsenal graph has `n-residue>=8`.

### wow-85 — HOLD

The same variance is at most 4, while the smallest adjacency rank in the arsenal is 5.

### wow-86 — SKIP_OCR

Garble: `variance of coordinates of a maximal clique maximum of Even.` The comparison operator is absent. Supplying one would be guessing; if intended `<=`, the arsenal holds.

### wow-87 — HOLD

Direct ordered distance-matrix variance is at most `1070/729` on the arsenal, while the smallest sum of reciprocal temperatures is 10.

### wow-88 — HOLD

Every plausible distance-matrix mode lies between 0 and 4; the smallest inverse-temperature sum is 10.

### wow-89 — HOLD

Exact average distance is at most `31/13`, while the smallest inverse-temperature sum is 10.

### wow-90 — HOLD on settled reading

For maximum independent sets the row invokes Chung's theorem; direct arsenal checks hold. The source distinguishes an all-maximal-set question and notes star failures of a stronger size reading.

### wow-91 — HOLD

Ordered distance-matrix variance is at most `1070/729`, below the smallest arsenal matching number 5.

### wow-92 — HOLD; strongest reading historically refuted

All plausible arsenal evaluations hold. The row itself reports that odd cycles above order 10 refute the strongest maximum-mode/maximum-set interpretation.

### wow-93 — HOLD

Exact average distances are at most their residues: `C9[K3]` gives `31/13 <= 3`, and `C5[K4]` gives `27/19 <= 2`.

### wow-94 — HOLD

Distance-matrix variance is at most `1070/729`, while every arsenal graph has independence number at least 2.

### wow-96 — HOLD — historically proved

The even-distance vector is constant on every vertex-transitive arsenal graph, so it has one distinct component value, at most residue 2 or 3. The row cites `[FMS1]`.

### wow-96(2) — SKIP_OCR

Garble: `William Staton. April 88.` This parser row is orphan commentary with no mathematical statement.

### wow-98 — HOLD — historically proved

All arsenal graphs satisfy `mu <= n-residue`; the closest small member gives `5 <= 8`. The row explicitly says the result is true for all graphs.

### wow-99 — HOLD

Distance-matrix variance is below 1.5, while `n-residue>=8` throughout the arsenal.

### wow-100 — HOLD

The even-distance vector is constant on every arsenal graph, so the maximum frequency is `n`, trivially at least `chi`.

### wow-102 — HOLD

For visible #102, degree variance is zero on every regular arsenal graph, below mean Even. OCR-appended #103/#104 also hold because these graphs have no cut vertices.

### wow-105 — N/A_ARSENAL

The tree hypothesis excludes every mandated arsenal graph.

### wow-106 — N/A_ARSENAL — historically proved

The tree hypothesis excludes every arsenal graph; the row cites `[FMS]` and characterizes equality.

### wow-109 — HOLD / historically refuted elsewhere

The even-distance-vector range is 0 on all vertex-transitive arsenal graphs. The row explicitly reports Puget's counterexample to the general statement.

<!-- NEXT -->
