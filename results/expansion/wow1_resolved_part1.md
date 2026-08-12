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

### wow-50 — HOLD / NO ADDITIONAL WITNESS

> The number of zero eigenvalues < smallest mode of the distance matriz. s.f. April 87.

The row depends on the distance minimode convention. Under the source-faithful convention used in the existing campaign profiles, every applicable arsenal graph holds; no alternate convention is introduced and no additional historical witness is claimed.

### wow-48 — PROVED_HOLD

> The sum of positive eigenvalues < largest eigenvalue of the distance matrix. Peter Puget, The University of Puget Sound. September 88. A9. -largest negative eigenvalue < minimal frequency of the distance matrix.

Direct evaluation of the applicable arsenal using the source hypotheses and the listed distance, spectrum quantities gives no violation. Exact combinatorial arithmetic is used where possible and spectral values are separated from equality by the `1e-6` guard. The campaign finds no contradiction to the proved status.

### wow-46 — HOLD / BUNDLED SOURCE

> The smallest positive eigenvalue < number of vertices of the center of a graph. Disproved by James B. Shearer. May 88. See also 58. AT. The smallest positive eigenvalue < number of vertices on the boundary. Disproved by Peter Puget, The University of Puget ...

The row bundles #46 and #47. On every arsenal graph, the smallest positive adjacency eigenvalue is at most both the center size and periphery size (both equal `n` for the regular vertex-transitive members). No additional witness arises, but the two historical refutations remain external.

### wow-45 — PROVED_HOLD

> The second largest eigenvalue is not more than the matching number. Proved by Noga Alon, 5.88.

Direct evaluation of the applicable arsenal using the source hypotheses and the listed matching, spectrum quantities gives no violation. Exact combinatorial arithmetic is used where possible and spectral values are separated from equality by the `1e-6` guard. The campaign finds no contradiction to the proved status.

### wow-43 — PROVED_HOLD

> Let s be the smallest eigenvalue of G, and m its matching number. Then - s 1s smaller or equal to m. Proved by Favaron, Maheo and Sacle, University of Paris-Sud, /FMS2/. 4A, The second largest eigenvalue is not more than the independence number. Noga Alon f...

Direct evaluation of the applicable arsenal using the source hypotheses and the listed alpha, connectivity, matching, spectrum quantities gives no violation. Exact combinatorial arithmetic is used where possible and spectral values are separated from equality by the `1e-6` guard. The campaign finds no contradiction to the proved status.

### wow-39 — SKIP_BUNDLED_OCR

> The deviation of the distance matrix is not more than the number of positive eigenvalues. AO. The deviation of the distance matrix is not more than the number of negative eigenvalues. Al. chromatic number + radius 1s not more than the maximum degree + the f...

This row merges at least four numbered statements (`39`, `40`, `41`, `42`) and truncates the last one. Assigning its single status to a particular inequality would be unsafe; no verdict is inferred from the bundled OCR.

### wow-38 — HOLD / NO ADDITIONAL WITNESS

> The variance of the distance matrix is not more than the negative of the smallest eigenvalue.

The row depends on the distance-matrix variance convention. Under the source-faithful convention used in the existing campaign profiles, every applicable arsenal graph holds; no alternate convention is introduced and no additional historical witness is claimed.

### wow-37 — PROVED_HOLD

> Radius is not more than the sum of positive eigenvalues. Proved in [FA2]. Also partially proved by Zang Shu, Beijing Institute of Technology.

Direct evaluation of the applicable arsenal using the source hypotheses and the listed radius, spectrum quantities gives no violation. Exact combinatorial arithmetic is used where possible and spectral values are separated from equality by the `1e-6` guard. The campaign finds no contradiction to the proved status.

### wow-36 — PROVED_HOLD

> The diameter of a graph is not more than the number of negative eigen- values of the distance matrix. James B. Shearer, see 35.

Direct evaluation of the applicable arsenal using the source hypotheses and the listed diameter, distance quantities gives no violation. Exact combinatorial arithmetic is used where possible and spectral values are separated from equality by the `1e-6` guard. The campaign finds no contradiction to the proved status.

### wow-35 — PROVED_HOLD

> The diameter of a graph is not more than the negative of the largest negative distance eigenvalue. This and the next conjecture follows from interlacing theorem. James B. Shearer, 7.88

Direct evaluation of the applicable arsenal using the source hypotheses and the listed diameter, distance, spectrum quantities gives no violation. Exact combinatorial arithmetic is used where possible and spectral values are separated from equality by the `1e-6` guard. The campaign finds no contradiction to the proved status.

### wow-34 — HOLD / NO ADDITIONAL WITNESS

> n - rank of the distance matrix is not more than the maximum frequency of the distance. Disproved by James B. Shearer, comp 23.

The applicable arsenal satisfies the source-faithful inequality using the listed distance, rank quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-33 — HOLD / NO ADDITIONAL WITNESS

> The negative of the largest negative distance eigenvalue is not more than the chromatic number. Disproved by Alon, Saks, Seymour, Shearer and Winkler. comp 28.

The applicable arsenal satisfies the source-faithful inequality using the listed chromatic_number, distance, spectrum quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-31 — HOLD / NO ADDITIONAL WITNESS

> The negative of the largest negative distance eigenvalue is not more than the independence number. A counterexample is D2(B4). James B. Shearer, 7.88.

The applicable arsenal satisfies the source-faithful inequality using the listed alpha, distance, spectrum quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-30 — HOLD / NO ADDITIONAL WITNESS

> The number of positive distance eigenvalues is not more than sum of temperatures of vertices. A counterexample is D6(B6). James. B. Shearer, July 88.

The applicable arsenal satisfies the source-faithful inequality using the listed distance, spectrum, temperature quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-29 — RETRO-VIOLATION — T(q), q≥7

> The Randic index is not more than the number of negative distance eigen- values. Disproved by Alon, Saks, Seymour, Shearer and Winkler. July 88.

For `T(q)`, regularity gives `R=n/2=q(q-1)/4`, while the distance spectrum has exactly `q-1` negative eigenvalues. Thus `T(7)` gives `10.5 > 6`, and every `q>=7` violates. This supplements the row's historical refutation; it is not a new conjecture kill. Exact spectral multiplicities and a separate eigensolver agree.

### wow-28 — HOLD / NO ADDITIONAL WITNESS

> Randic index is not more than the sum of positive eigenvalues. This conjecture is false, but working on a counterexample I formed a conjecture that for trees the value of Randic index is close, and seem to be correlated with the sum of the positive eigenval...

The applicable arsenal satisfies the source-faithful inequality using the listed randic_index, spectrum, tree quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-26 — HOLD / NO ADDITIONAL WITNESS

> Sum of reciprocals of degrees is not more than the rank of the distance matriz. (1.) This was disproved by Alon, Saks, Seymour, Shearer and Winkler.

The applicable arsenal satisfies the source-faithful inequality using the listed degree, distance, rank quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-25 — PROVED_HOLD

> average temperature is not more than the number of negative eigenvalues of the distance matrix. (-1.) see 24.

Direct evaluation of the applicable arsenal using the source hypotheses and the listed distance, spectrum, temperature quantities gives no violation. Exact combinatorial arithmetic is used where possible and spectral values are separated from equality by the `1e-6` guard. The campaign finds no contradiction to the proved status.

### wow-24 — PROVED_HOLD

> average temperature is not more than the number of negative eigenvalues. This and the next conjecture were proved by Shearer.

Direct evaluation of the applicable arsenal using the source hypotheses and the listed spectrum, temperature quantities gives no violation. Exact combinatorial arithmetic is used where possible and spectral values are separated from equality by the `1e-6` guard. The campaign finds no contradiction to the proved status.

### wow-23 — RETRO-VIOLATION — T(q), q≥7

> rank of the adjacency matrix is not more than the rank of the distance Matrie. Even cycles Cy, n > 6 or more are counterecamples. James B. Shearer, Thomas J. Watson Research Center, Yorktown Heights, May 88. The counterexample is Ce (and all bigger even cyc...

`T(7)=L(K7)` has adjacency rank 21 but distance-matrix rank 7, so it violates `rank(A) <= rank(D)`; generally `T(q)` has full adjacency rank `q(q-1)/2` while its distance matrix has rank `q`. This is a new witness to an already-refuted conjecture, not new mathematics. The closed-form spectra and an independent numerical rank computation agree.

### wow-22 — HOLD / NO ADDITIONAL WITNESS

> Let e be the largest negative eigenvalue of a graph. Then -e is smaller or equal to the independence number. The Paley graph with 101 vertices 1s a counter-example. Noga Alon, Tel Aviv University and Bellcore. June 88. Alon and myself noticed that the conje...

The applicable arsenal satisfies the source-faithful inequality using the listed alpha, degree, spectrum quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-19 — PROVED_HOLD

> Let a be the smallest eigenvalue of a graph G. Then - a is < Randic index of G. (3.) This conjecture was proved by Favaron, Maheo and Sacle, University of Paris-Sud. comp also conj’s 20, 21, 27 and 28. [FMS2] O. Favaron, M. Maheo and J-P. Sacle, Some Result...

Direct evaluation of the applicable arsenal using the source hypotheses and the listed randic_index, spectrum quantities gives no violation. Exact combinatorial arithmetic is used where possible and spectral values are separated from equality by the `1e-6` guard. The campaign finds no contradiction to the proved status.

### wow-18 — HOLD / NO ADDITIONAL WITNESS

> radius is not more than the number of vertices of maximum degree + the maximum frequency of the degree sequence. Disproved by Shui-Tain Chen, University of Houston, March 88. February 19. 87.

The applicable arsenal satisfies the source-faithful inequality using the listed degree, radius quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.
