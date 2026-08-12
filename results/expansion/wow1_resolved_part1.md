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

### wow-1 — HOLD / NO ADDITIONAL WITNESS

> Chromatic number of a graph is not more than its rank +1. The rank of a graph is the rank of its adjacency matrix. Francois Jeager told me (about a year) later that a somewhat stronger conjecture was made earlier by Cyriel Van Neufallen, [CDS].

The applicable arsenal satisfies the source-faithful inequality using the listed chromatic_number, rank quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-2 — PROVED_HOLD

> In every connected graph the average distance is not more than the indepen- dence number. W. Waller, UH and myself proved that the average distance is not more than 1 + the independence number, [FW]. The conjecture was proved by Fan Chung, Bell Communicatio...

Direct evaluation of the applicable arsenal using the source hypotheses and the listed alpha, average_distance, distance quantities gives no violation. Exact combinatorial arithmetic is used where possible and spectral values are separated from equality by the `1e-6` guard. The campaign finds no contradiction to the proved status.

### wow-3 — HOLD / NO ADDITIONAL WITNESS

> The weight of an edge with endpoints of degree x and y is the reciprocal of the square root of xy. The Randic index of a graph is the sum of weights of its edges. Conjecture: If G is a connected graph then the average distance between its distinct vertices ...

The applicable arsenal satisfies the source-faithful inequality using the listed average_distance, degree, distance, randic_index, tree quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-6 — HOLD / NO ADDITIONAL WITNESS

> average distance is not more than the variance of the degree sequence + maximal frequency of the degree sequence, (4.) The conjecture was refuted by James B. Shearer, IBM Research Center at Yorktown Heights. 10.89.

The applicable arsenal satisfies the source-faithful inequality using the listed average_distance, degree, distance quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-9 — HOLD / NO ADDITIONAL WITNESS

> Let m be the mode of distance of connected graph, 1.e the distance which occurs most often. Conjecture: m is not more than the average distance + the matching number. This conjecture was refuted by Hi Dong Qi, Dept. of Applied Mathemat- ics, Beijing Institu...

The applicable arsenal satisfies the source-faithful inequality using the listed average_distance, distance, matching quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-11 — HOLD / NO ADDITIONAL WITNESS

> average temperature is not more than the variance of the degree sequence + maximum frequency of the degree sequence. (-1, 4.) Disproved by William Staton, OleMiss 6. 88.

The applicable arsenal satisfies the source-faithful inequality using the listed degree, temperature quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-13 — HOLD / NO ADDITIONAL WITNESS

> radius is not more than the average distance + sum of reciprocals of degrees. (3.) Disproved by James B. Shearer, IBM, Yorktown Heights, 10. 89.

The applicable arsenal satisfies the source-faithful inequality using the listed average_distance, degree, distance, radius quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-15 — HOLD / NO ADDITIONAL WITNESS

> radius is not more than the variance of the degree sequence + Randic Index. (8, 4.) Gilles Caporossi and Pierre Hansen, University of Montreal noticed that even paths with > 22 vertices are counterexamples to this conjecture and for n > 26 even paths are co...

The applicable arsenal satisfies the source-faithful inequality using the listed degree, path, radius, randic_index quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-16 — HOLD / NO ADDITIONAL WITNESS

> radius is not more than the average temperature + Randic index. (-1, 3.) Disproved by Gilles Caporossi and Pierre Hansen, University of Mon- treal. See conj. 3 and 15.

The applicable arsenal satisfies the source-faithful inequality using the listed radius, randic_index, temperature quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-17 — HOLD / NO ADDITIONAL WITNESS

> radius is not more than the variance of the degree sequence + maximal frequency of the degree sequence. (4.) Disproved by James B. Shearer, IBM, Yorktown Heights, 10. 89.

The applicable arsenal satisfies the source-faithful inequality using the listed degree, radius quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.
