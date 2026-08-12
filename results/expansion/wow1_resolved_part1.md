# WoW I resolved-entry sweep — numeric ids below 450

## Method and progress

This lane covers every row of `corpora/graffiti_wow.json` whose id matches
`^wow-(\d+)` with numeric base id below 450 and whose normalized status does
**not** begin `open` or `unannotated`.  The frozen corpus contains **122** such
rows: 36 marked proved and 86 marked refuted.  These are a QA/retro-witness
lane, not a search that can change their historical status.

For each source-faithful and sufficiently legible row I check `C5[K_m]` for
`m in {2,3,4,5,6,8}`, `C7[K3]`, `C9[K3]`, `T(7)`, `T(8)`, `T(9)`, and
`complement(C5[K4])`, plus the named calibration graphs when the hypothesis
selects them.  A contradiction to a proved row must pass the identical-reading
connected Graph Atlas and named-graph DB-sanity gate before it can be called
anything stronger than a likely transcription/definition error.  Candidate
violations are independently recomputed; floating-point spectral comparisons
use a `1e-6` guard.  Any ILP is capped at 60 seconds.

Progress below is append-only at conjecture granularity.  Every completed row
is committed and pushed before the next row is recorded.

### wow-0 — PROVED_HOLD

> For every connected graph the radius is not more than its independence number. This conjecture was proved in [FW], [FMS1] and later in [F]. At about the same time slightly stronger result appeared in [ESS]. Radius is of course not a very good bound for the ...

Direct evaluation of the applicable arsenal using the source hypotheses and the listed alpha, distance, radius quantities gives no violation. Exact combinatorial arithmetic is used where possible and spectral values are separated from equality by the `1e-6` guard. The campaign finds no contradiction to the proved status.
