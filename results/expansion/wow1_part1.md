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

