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

### wow-147 — SKIP_ORDER_DEPENDENT

> The average distance < the number of vertices whose coordinates of Max- ane ts 0. With a right (or really wrong) ordering of vertices in barbell graphs, [FA] , Maxine may select every third vertex in the central path, so the strongest version of the observa...

The source explicitly makes the Maxine output ordering-dependent and explains how a bad ordering refutes the strongest version. No canonical ordering is frozen for the arsenal, so no extra witness is claimed.

### wow-146 — PROVED_HOLD

> The sum of positive eigenvalues < size. The equality holds true iff the maximum degree is 1. James B. Shearer, July 88.

Direct evaluation of the applicable arsenal using the source hypotheses and the listed degree, spectrum quantities gives no violation. Exact combinatorial arithmetic is used where possible and spectral values are separated from equality by the `1e-6` guard. The campaign finds no contradiction to the proved status.

### wow-145 — HOLD / NO ADDITIONAL WITNESS

> minimum of derivative of positive eigenvalues < n/average distance. [FMS'2], December 89.

The applicable arsenal satisfies the source-faithful inequality using the listed average_distance, distance, spectrum quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-141 — HOLD / NO ADDITIONAL WITNESS

> range of positive eigenvalues < the matching number. [FMS2]. December 88.

The applicable arsenal satisfies the source-faithful inequality using the listed matching, spectrum quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-140 — HOLD / NO ADDITIONAL WITNESS

> deviation of eigenvalues < harmonic. FMS. 10.89.

The applicable arsenal satisfies the source-faithful inequality using the listed spectrum quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-139 — HOLD / NO ADDITIONAL WITNESS

> - (2-nd smallest eigenvalue) < harmonic. James B. Shearer. October 8&8.

The applicable arsenal satisfies the source-faithful inequality using the listed spectrum quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-138 — PROVED_HOLD

> 2-nd largest eigenvalue < size / clique. [FMS2] proved that this conjec- ture is true for all graphs but Ky .December 89.

Direct evaluation of the applicable arsenal using the source hypotheses and the listed clique_number, spectrum quantities gives no violation. Exact combinatorial arithmetic is used where possible and spectral values are separated from equality by the `1e-6` guard. The campaign finds no contradiction to the proved status.

### wow-137 — HOLD / NO ADDITIONAL WITNESS

> 2nd largest eigenvalue < harmonic. James B. Shearer October 88. [/FMS2]. November 88.

The applicable arsenal satisfies the source-faithful inequality using the listed spectrum quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-128 — PROVED_HOLD

> The second smallest eigenvalues of Laplacian < n/averagedistance. Vance Faber, Los Alamos National Laboratory, deduced from the results of [CF] that for every fixed d = maximum degree there are at most finitely many countereramples to this conjecture and ev...

Direct evaluation of the applicable arsenal using the source hypotheses and the listed degree, diameter, distance, laplacian, spectrum quantities gives no violation. Exact combinatorial arithmetic is used where possible and spectral values are separated from equality by the `1e-6` guard. The campaign finds no contradiction to the proved status.

### wow-127 — HOLD / NO ADDITIONAL WITNESS

> minimum degree < n / average distance. (comp. 62) Mekkia Kouider, L. R. I. University de Paris-Sud and Peter Winkler, Bellcore proved that the average distance < 3+ n/(1+ mindeg).

The applicable arsenal satisfies the source-faithful inequality using the listed average_distance, degree, distance quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-124 — RETRO-VIOLATION — dense arsenal

> size/2 < the rank of Laplacian. Disproved by s.f.

The primary scan states `size/2 <= rank(L)`, with size meaning `|E|`. `C5[K4]` gives `55 > 19`; indeed `C5[K_m]` violates from `m=2` onward. `K5` already fails the identical reading (`5>4`), so the DB-sanity gate confirms a genuinely false historical statement rather than an OCR artifact. This is only a new carrier witness to a row already marked refuted.

### wow-116 — PROVED_HOLD

> largest eigenvalue < Randic. Proved in [FMS2] . November 88. As it was the case with 63 this conjecture again is a generalization of Turan’s theorem in the triangle-free case. Indeed: Randic is always at most n/2, and for triangle-free graphs, the size s at...

Direct evaluation of the applicable arsenal using the source hypotheses and the listed randic_index, spectrum quantities gives no violation. Exact combinatorial arithmetic is used where possible and spectral values are separated from equality by the `1e-6` guard. The campaign finds no contradiction to the proved status.

### wow-112 — HOLD / NO ADDITIONAL WITNESS

> Radius < maximal frequency of the degree sequence. Disproved by Shui- Tain Chen. April 88. James B. Shearer found a bipartite counterexample. May 88. Shui-Tain Chen proved the conjecture for trees, October 88.

The applicable arsenal satisfies the source-faithful inequality using the listed bipartite, degree, radius, tree quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-110 — HOLD / NO ADDITIONAL WITNESS

> Even(v) is the number of vertices at even distance from v. Conjecture: If G is triangle-free then range of Even < Range of Degree. Disproved by William Staton. March 88.

The applicable arsenal satisfies the source-faithful inequality using the listed degree, distance quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-107 — HOLD / NO ADDITIONAL WITNESS

> A graph G is even-regular if the vector E defined in conjecture 96 is constant. If G is even-regular then the mode of the distance matrix < radius. Vance Faber, Los Alamos National Laboratory used LANL Cray com- puter and Reed’s program listing all at most ...

The row depends on the even-regular/modal convention. Under the source-faithful convention used in the existing campaign profiles, every applicable arsenal graph holds; no alternate convention is introduced and no additional historical witness is claimed.

### wow-101 — HOLD / NO ADDITIONAL WITNESS

> The variance of the degree sequence is < than the independence number. Disproved independently by James B. Shearer and William Staton. Febru- ary 88.

The applicable arsenal satisfies the source-faithful inequality using the listed alpha, degree quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-95 — HOLD / NO ADDITIONAL WITNESS

> The mode of the distance < the residue. Cy is a counterexample with the interpretation of the mode as the largest of modes. Odile Favaron , Maryvonne Maheo and Jean-Francois Sacle, July 88.

The row depends on the modal tie plus residue convention. Under the source-faithful convention used in the existing campaign profiles, every applicable arsenal graph holds; no alternate convention is introduced and no additional historical witness is claimed.

### wow-81 — SKIP_ORDER_DEPENDENT

> variance of coordinates of a maximal independent set < maximal frequency of Even. Disproved by William Staton. March 88.

The coordinate vector depends on the selected maximal independent set and ordering conventions not frozen in the corpus. The row is already refuted; guessing an ordering would not yield a defensible additional witness.

### wow-79 — HOLD — HISTORICALLY PROVED

> mean of coordinates of a maximal independent set < matching. Proved by William Staton for all independent sets. The equality holds true iff the graph has no edges, but there are graphs like stars in which the two invariants can be arbitrarily close. January...

The row records Staton's proof for all independent sets. The arsenal has positive matching number and no source-faithful contradiction; ordering-dependent coordinate variants are not substituted for the proved statement.

### wow-69 — HOLD / NO ADDITIONAL WITNESS

> Residue 1s not more than the independence number. This is really a joint conjecture of Graffiti and myself, because I began to an- ticipate this conjecture writing the code for residue.

The row depends on the residue algorithm already covered by its proof. Under the source-faithful convention used in the existing campaign profiles, every applicable arsenal graph holds; no alternate convention is introduced and no additional historical witness is claimed.

### wow-68 — HOLD / NO ADDITIONAL WITNESS

> If G is triangle-free then the matching number < then the maximal fre- quency of the degree sequence. Disproved by Thomas Spencer, Rensselaer Poly- technic Institute February 87. November 26. 87.

The applicable arsenal satisfies the source-faithful inequality using the listed degree, matching quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-67 — HOLD / NO ADDITIONAL WITNESS

> chromatic number of a triangle-free graph is not more than the maximum frequency of its degree sequence (mfd.). Disproved by William Staton, U. of Mississippi, July 87. Staton skillfully modified Myctelski’s construction of triangle-free graphs with high ch...

The applicable arsenal satisfies the source-faithful inequality using the listed chromatic_number, degree quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-66 — HOLD / NO ADDITIONAL WITNESS

> If G is triangle-free then radius < the sum of reciprocal of degrees. Disproved by Thomas Spencer, Rensselaer Polytechnic Institute Febru- ary 87. I wrote in [FA2] that it was the first counterexample with over 100 vertices but that was incorrect. The first...

The applicable arsenal satisfies the source-faithful inequality using the listed average_distance, degree, distance, radius quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-65 — HOLD / NO ADDITIONAL WITNESS

> If G is triangle-free then the mode of Degree < the matching number. Disproved by Thomas Spencer, Rensselaer Polytechnic Institute February 8&7.

The applicable arsenal satisfies the source-faithful inequality using the listed degree, matching quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-64 — HOLD / NO ADDITIONAL WITNESS

> If G is triangle-free then the mode of Degree < then the Randic Index. Disproved by James B. Shearer. July 87.

The applicable arsenal satisfies the source-faithful inequality using the listed degree, randic_index quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-62 — HOLD / NO ADDITIONAL WITNESS

> If G is a regular graph of degree d then the average distance is not more than n/d, comp 127. Peter Puget proved the conjecture for graphs of diameter < 3 and constructed an infinite family of graphs of diameter 4 and even F such that average distance = 2+ ...

The applicable arsenal satisfies the source-faithful inequality using the listed average_distance, degree, diameter, distance, path, tree quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-61 — HOLD / NO ADDITIONAL WITNESS

> mode of distance is not more than the matching number. Disproved by Alon, Saks, Seymour and Winkler,who also proved that the conjecture is true for regular graphs of high degree, > 10 is enough.

The applicable arsenal satisfies the source-faithful inequality using the listed degree, distance, matching quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-60 — HOLD / NO ADDITIONAL WITNESS

> mode of distance is not more than the independence number. Disproved by Alon, Saks, Seymour and Winkler.

The applicable arsenal satisfies the source-faithful inequality using the listed alpha, distance quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-59 — HOLD / NO ADDITIONAL WITNESS

> Diameter is not more than the sum of positive eigenvalues. Disproved by Peter Puget

The applicable arsenal satisfies the source-faithful inequality using the listed diameter, spectrum quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-58 — HOLD / NO ADDITIONAL WITNESS

> - largest negative eigenvalue is not more than the number of centers. Disproved by Peter Puget

The applicable arsenal satisfies the source-faithful inequality using the listed spectrum quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-56 — HOLD / NO ADDITIONAL WITNESS

> The second largest eigenvalue is not more than the number of centers. Disproved by Halina Bielak, U. of Marie Curie-Skladowska, Lublin, Poland. It seems that I lost 57. Perhaps someone has an original version.

The applicable arsenal satisfies the source-faithful inequality using the listed spectrum quantities. This does not rehabilitate the conjecture: the row is already historically refuted, and the campaign simply found no additional witness among its carrier, triangular, complement, and named graphs.

### wow-55 — RETRO-VIOLATION — dense arsenal

> The second largest eigenvalue is not more than the minimode of distance. Disproved by Peter Puget 11. 88, and later independently by Favaron, Maheo and Sacle. 1.91

On the source-faithful minimode-as-smallest-modal-distance reading, `C5[K4]` has `lambda_2=(sqrt(5)-1)4/2-1=5.472135... > 1`, its unique modal distance. `T(7)` likewise gives `3>2`. Both are additional witnesses to the already-refuted statement; values are beyond the `1e-6` guard and independently recomputed.

### wow-53 — HOLD / NO ADDITIONAL WITNESS

> average temperature < minimal frequency of the distance matrix. Proved by Shui-Tain Chen, U. of Houston. April 87.

The row depends on the minimum-frequency convention. Under the source-faithful convention used in the existing campaign profiles, every applicable arsenal graph holds; no alternate convention is introduced and no additional historical witness is claimed.

### wow-52 — HOLD / NO ADDITIONAL WITNESS

> The number of zero eigenvalues < the number of vertices in the boundary of the graph. s.f.

The row depends on the boundary/periphery terminology. Under the source-faithful convention used in the existing campaign profiles, every applicable arsenal graph holds; no alternate convention is introduced and no additional historical witness is claimed.

### wow-51 — PROVED_HOLD

> The number of zero eigenvalues < the number of vertices in the center of the graph. s.f. April 87.

Direct evaluation of the applicable arsenal using the source hypotheses and the listed spectrum quantities gives no violation. Exact combinatorial arithmetic is used where possible and spectral values are separated from equality by the `1e-6` guard. The campaign finds no contradiction to the proved status.

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
